---
task: 3.26-delete-links
title: Ghi chú triển khai DELETE /links/{id} trong module family
stage: implement
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 14:34 +0700
content_hash: sha256:502e1520beba53c6
inputs:
  01-requirement.md: sha256:e9780e264d8de972
  03-plan.md: sha256:6cc904b55d5e24ed
---

# Báo cáo chi tiết triển khai task SCRUM-134 (Backlog 3.26)

- **Mã task:** SCRUM-134 (Sprint Backlog 3.26, PB17)
- **Tiêu đề:** Chuyển `DELETE /links/{id}` từ prototype sang module `family` trên kiến trúc Hexagonal Modular Monolith
- **Trạng thái:** Đã hoàn thành triển khai code, lint ruff 0 lỗi, unit test và integration test DB thật (29/29 passed)
- **Commit:** `d03dac4` trên nhánh `feat-3.26` (repo backend)
- **Ngày thực hiện:** 23/10/2026

---

## 1. Mục tiêu và bối cảnh

Trong giai đoạn prototype ban đầu (nhánh `feat/api-contract`), endpoint `DELETE /api/v1/links/{id}` được đặt tại `backend/app/routers/links.py` và chạy trên bộ nhớ tạm `mock_db.py`.

Nhiệm vụ của task 3.26 là chuyển toàn bộ nghiệp vụ thu hồi liên kết này sang module `family` chuẩn của hệ thống Backend API (`src/drugtime/modules/family/`) theo mô hình Hexagonal Architecture:
- Xóa bỏ TODO comment trong [`http.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/adapters/inbound/http.py).
- Kết nối router chính thức `@router.delete("/links/{id}")` (prefix `/family`).
- Tuân thủ nghiêm ngặt các bất biến kiến trúc: PEP / Access control, bảo mật phân quyền (chỉ bệnh nhân hoặc người thân thuộc link mới được gỡ), Idempotency, không thay đổi schema CSDL v11.

---

## 2. Chi tiết các thay đổi mã nguồn đã thực hiện

### 2.1. Tầng Domain: [`src/drugtime/modules/family/domain/link.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/domain/link.py)
- **Cập nhật hàm `transition_link`**:
  - Hỗ trợ chuyển đổi từ `LinkStatus.ACTIVE` hoặc `LinkStatus.PENDING` sang `LinkStatus.REVOKED`:
    - Đặt trạng thái `status = LinkStatus.REVOKED`.
    - Tắt chia sẻ dữ liệu sức khỏe `sharing_enabled = False`.
    - Ghi nhận thời điểm thu hồi `revoked_at = now`.
    - Xóa `rejected_at = None`.
  - **Bảo đảm Idempotent**: Nếu link đã ở trạng thái `LinkStatus.REVOKED` và tiếp tục yêu cầu chuyển sang `REVOKED`, giữ nguyên đối tượng link hiện tại (không ghi đè `revoked_at`).
  - **Xử lý link `REJECTED`**: Nếu link đang ở trạng thái `REJECTED` mà bị gọi thu hồi, hàm ném ra `FamilyLinkError("invalid_link_transition", "cannot transition family link from rejected to revoked")` (kế thừa từ `DomainError`).

### 2.2. Tầng Application: Ports & Use-cases
- **Port [`ports.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/application/ports.py)**:
  - Khai báo thêm phương thức `revoke` trong Protocol `Links`:
    ```python
    def revoke(
        self,
        uow: UnitOfWork,
        *,
        link_id: int,
        caller_id: UUID,
        now: datetime,
    ) -> FamilyLink | None: ...
    ```
- **Use-case [`manage_links.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/application/manage_links.py)**:
  - Cập nhật hàm `revoke_link(uow, *, link_id: int, caller_id: UUID | None = None, now: datetime, links: Links) -> FamilyLink`:
    1. **Kiểm tra tồn tại**: Tìm link qua `links.get(uow, link_id)`. Nếu không tồn tại $\rightarrow$ raise `Forbidden("khong_co_quyen")` (HTTP 403, không làm lộ sự tồn tại của link cho người ngoài).
    2. **Kiểm tra quyền sở hữu**: Nếu `caller_id` khác cả `patient_user_id` lẫn `family_user_id` $\rightarrow$ raise `Forbidden("khong_co_quyen")`.
    3. **Xử lý Idempotency**: Nếu `link.status is LinkStatus.REVOKED`, trả về link ngay mà không gọi lệnh ghi đè mốc thời gian xuống DB.
    4. **Thực thi cập nhật**: Gọi `transition_link` để kiểm tra domain invariants, sau đó gọi phương thức chuyên biệt `links.revoke(...)` của adapter SQL.

### 2.3. Tầng Outbound SQL: [`src/drugtime/modules/family/adapters/outbound/sql_links.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/adapters/outbound/sql_links.py)
- **Định nghĩa câu truy vấn `_REVOKE_LINK`**:
  ```sql
  UPDATE caregiver_links
  SET status = 'revoked',
      revoked_at = COALESCE(revoked_at, :revoked_at),
      sharing_enabled = false
  WHERE id = :id
    AND (patient_user_id = :caller_id OR family_user_id = :caller_id)
  RETURNING id, patient_user_id, family_user_id, status, sharing_enabled,
            linked_at, revoked_at, rejected_at
  ```
- **Các điểm kỹ thuật quan trọng**:
  - **Nguyên tử (Atomicity)**: Cập nhật đồng thời `status='revoked'`, `revoked_at`, `sharing_enabled=false` trong CÙNG MỘT câu UPDATE, bảo đảm luôn thỏa mãn ràng buộc schema PostgreSQL:
    `CHECK ((status = 'revoked') = (revoked_at IS NOT NULL))`.
  - **Bảo toàn thời gian gỡ**: `revoked_at = COALESCE(revoked_at, :revoked_at)` ngăn việc gọi nhiều lần làm trôi mốc thời gian đã gỡ ban đầu.
  - **Cô lập quyền sở hữu**: Điều kiện `AND (patient_user_id = :caller_id OR family_user_id = :caller_id)` đảm bảo nếu kẻ lạ gọi lệnh SQL, câu UPDATE khớp 0 bản ghi và trả về `None`.
- **Cài đặt hàm `SqlLinks.revoke(...)`**: Nhận `caller_id` và `now`, thực thi truy vấn và trả về `FamilyLink` hoặc `None`.

### 2.4. Tầng Inbound HTTP: [`src/drugtime/modules/family/adapters/inbound/http.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/adapters/inbound/http.py)
- Xóa bỏ dòng ghi chú `TODO: DELETE /family/links/{id}`.
- Nối endpoint chính thức:
  ```python
  @router.delete(
      "/links/{id}",
      status_code=status.HTTP_204_NO_CONTENT,
      responses={
          204: {"description": "Thu hồi hoặc tự rời liên kết thành công, hoặc đã thu hồi từ trước"},
          401: {"model": ErrorDetail, "description": "Chưa xác thực hoặc token không hợp lệ"},
          403: {"model": ErrorDetail, "description": "khong_co_quyen: link không tồn tại hoặc không thuộc người gọi"},
      },
      operation_id="revokeLink",
  )
  def delete_link(
      id: int,
      uow: SqlUnitOfWork = Depends(get_uow),
      user: identity.CurrentUser = Depends(identity.current_user),
  ) -> Response:
      manage_links.revoke_link(
          uow,
          link_id=id,
          caller_id=user.id,
          now=datetime.now(UTC),
          links=SqlLinks(),
      )
      return Response(status_code=status.HTTP_204_NO_CONTENT)
  ```
- **Export public API [`src/drugtime/modules/family/api.py`](file:///e:/DrugTIme_main/backend/src/drugtime/modules/family/api.py)**: Xuất hàm `revoke_link` để các module khác có thể gọi khi cần.

---

## 3. Chi tiết các bộ test đã xây dựng và kết quả

### 3.1. Unit Tests Domain: [`tests/unit/test_family_link_rules.py`](file:///e:/DrugTIme_main/backend/tests/unit/test_family_link_rules.py)
- `test_transition_active_to_revoked_disables_sharing`: Chuyển link ACTIVE sang REVOKED $\rightarrow$ sharing_enabled tắt, revoked_at được gán.
- `test_transition_pending_to_revoked`: Chuyển link PENDING sang REVOKED $\rightarrow$ thành công.
- `test_transition_already_revoked_is_idempotent`: Link đã REVOKED chuyển tiếp sang REVOKED $\rightarrow$ giữ nguyên đối tượng cũ.
- `test_transition_rejected_to_revoked_raises_error`: Link REJECTED chuyển sang REVOKED $\rightarrow$ ném `FamilyLinkError`.
- **Kết quả:** 10/10 test pass (100%).

### 3.2. Unit Tests Use-case: [`tests/unit/test_family_manage_links.py`](file:///e:/DrugTIme_main/backend/tests/unit/test_family_manage_links.py)
- `test_patient_can_revoke_active_link`: Bệnh nhân gỡ link active của mình thành công.
- `test_family_member_can_self_leave`: Người thân tự rời khỏi link thành công.
- `test_stranger_cannot_revoke_link_returns_forbidden`: Người lạ gọi gỡ link $\rightarrow$ raise `Forbidden("khong_co_quyen")`.
- `test_revoke_non_existent_link_returns_forbidden`: Link không tồn tại $\rightarrow$ raise `Forbidden("khong_co_quyen")`.
- `test_revoke_idempotent_preserves_first_timestamp`: Gỡ lần hai giữ nguyên mốc thời gian `revoked_at` ban đầu.
- `test_pending_link_can_be_revoked`: Link pending thu hồi thành công.
- `test_after_revoke_access_control_denies_and_logs`: Xác minh Policy Enforcement Point (PEP) ngay lập tức từ chối 403 và ghi nhật ký truy cập `denied` khi người thân cố truy cập dữ liệu sức khỏe sau khi đã gỡ liên kết.
- **Kết quả:** 17/17 test pass (100%).

### 3.3. Unit Tests HTTP Router: [`tests/unit/test_family_delete_link.py`](file:///e:/DrugTIme_main/backend/tests/unit/test_family_delete_link.py)
- `test_http_patient_revokes_active_link_204`: Gọi `DELETE /family/links/1` bằng token bệnh nhân $\rightarrow$ HTTP 204 No Content.
- `test_http_family_member_self_leave_204`: Gọi bằng token người thân $\rightarrow$ HTTP 204 No Content.
- `test_http_stranger_cannot_revoke_returns_403`: Gọi bằng token người lạ $\rightarrow$ HTTP 403 `{"detail": "khong_co_quyen"}`.
- `test_http_non_existent_link_returns_403`: Link không tồn tại $\rightarrow$ HTTP 403 `{"detail": "khong_co_quyen"}`.
- `test_http_pending_link_revoked_204`: Link pending thu hồi $\rightarrow$ HTTP 204.
- `test_http_already_revoked_is_idempotent_204`: Thu hồi link đã revoked $\rightarrow$ HTTP 204, `revoked_at` giữ nguyên.
- `test_http_missing_token_returns_401`: Không truyền Bearer token $\rightarrow$ HTTP 401 Unauthorized.
- `test_http_rejected_link_returns_422`: Link `rejected` bị gọi DELETE $\rightarrow$ HTTP 422 Unprocessable Entity kèm `{"detail": "cannot transition family link from rejected to revoked"}`.
- **Kết quả:** 8/8 test pass (100%).

### 3.4. Unit Tests SQL Outbound: [`tests/unit/test_sql_family_links.py`](file:///e:/DrugTIme_main/backend/tests/unit/test_sql_family_links.py)
- `test_sql_revoke_executes_coalesce_and_ownership`: Kiểm tra câu lệnh SQL thực thi chứa đúng `COALESCE(revoked_at, :revoked_at)` và `WHERE id = :id AND (patient_user_id = :caller_id OR family_user_id = :caller_id)`.
- `test_sql_revoke_returns_none_when_no_match`: Kiểm tra trả về `None` khi caller_id không khớp hoặc link không tồn tại.
- **Kết quả:** 8/8 test pass (100%).

### 3.5. Integration Tests: [`tests/integration/test_sql_family_links.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/tests/integration/test_sql_family_links.py)
Đã chạy toàn bộ bộ kiểm thử cơ sở dữ liệu thật với Supabase/PostgreSQL trên worktree `DrugTime-backend/feat-3.26`:
- `test_sql_revoke_idempotent_preserves_revoked_at`: Tạo link `active`, gọi `SqlLinks().revoke` lần 1 với thời điểm $t_1$, sau đó gọi lại với thời điểm $t_2 > t_1$. Xác minh `revoked_at` trong CSDL vẫn giữ nguyên mốc $t_1$.
- `test_sql_revoke_stranger_cannot_modify`: Người lạ gọi `revoke` $\rightarrow$ trả về `None`, xác minh CSDL vẫn giữ nguyên `status='active'`, `sharing_enabled=true`, `revoked_at=null`.
- `test_sql_revoke_rejected_link_returns_none`: Link `rejected` gọi qua `SqlLinks().revoke` trả về `None`.
- `test_revoke_active_link_sets_revoked_and_clears_sharing`: Thu hồi link active chuyển `revoked` và `sharing_enabled=false`.
- `test_revoke_idempotent_via_use_case`: Gọi use-case lần 2 trả về 204 và không đổi mốc thời gian.
- `test_stranger_revoke_rejected_link_gets_403`: Người lạ gọi trên link rejected nhận 403 `khong_co_quyen`.
- `test_stranger_revoke_nonexistent_link_gets_403`: Người lạ gọi trên link không tồn tại nhận 403 `khong_co_quyen`.
- `test_owner_revoke_rejected_link_gets_422`: Thành viên thuộc link gọi trên link rejected nhận 422 `invalid_link_transition`.
- `test_revoke_already_revoked_with_sharing_enabled_true_clears_sharing_db`: Link đã revoked nhưng dữ liệu cũ còn `sharing_enabled=true` được ép về `false`.
- `test_family_member_self_leave_db`: Người thân tự rời khỏi link thành công trong DB.
- `test_revoke_pending_link_db`: Thu hồi link `pending` thành công.
- `test_stranger_revoke_active_link_gets_403_and_db_unchanged`: Kẻ lạ gỡ link active bị 403 và DB không bị thay đổi.
- `test_http_revoke_e2e_flow_and_health_access_denied_under_5s`: Đo lường E2E luồng gỡ và kiểm tra PEP từ chối dữ liệu sức khỏe trong vòng $\le 5$ giây (QA.02), ghi log `access_logs` denied.
- `test_worker_scan_missed_doses_does_not_alert_revoked_family_member`: Worker quét bỏ lỡ không gửi cảnh báo cho người thân đã bị revoke.
- Cùng với 15 test tích hợp trong `test_medication_access.py` kiểm chứng PEP và audit trail.

**Kết quả:** 29/29 tests PASSED in 5.57s.
**Bằng chứng:** [`work/3.26-delete-links/evidence/implement-integration-tests.log`](file:///e:/DrugTIme_main/work/3.26-delete-links/evidence/implement-integration-tests.log)

---

## 4. Tóm tắt kết quả kiểm tra chất lượng

1. **Ruff Lint:**
   - Lệnh: `python -m ruff check src/drugtime/modules/family/`
   - Kết quả: `All checks passed!` (Exit code: 0).
   - Đã xử lý triệt để lint F841 (biến `updated` không dùng) và E501 (độ dài dòng).

2. **Unit Tests:**
   - 47/47 test liên quan đến module `family` (rules, manage_links, delete_link, link_code, sql_links) đều PASS 100%.

3. **Integration Tests (Postgres/Supabase thật):**
   - 29/29 test trong `tests/integration/test_sql_family_links.py` và `tests/integration/test_medication_access.py` đều PASS 100%.

---

## 5. Trạng thái mã nguồn & Bước tiếp theo

1. **Backend Worktree (`DrugTime-backend/feat-3.26`):**
   - Đã commit sạch: `d03dac4 fix(family): make link revocation idempotent` (7 files, +386/-6).
   - Đã push lên remote `origin/feat-3.26`.
   - Cần chuyển nhánh tại worktree này trở lại `feat-3.26` (nếu đang ở `feat/3.26-contract` do gõ nhầm):
     ```powershell
     git checkout feat-3.26
     git branch -D feat/3.26-contract
     ```

2. **Submodule Contract (`api_contract`):**
   - Cần cập nhật `openapi.json` thêm route `DELETE /links/{id}` (các mã phản hồi 204, 401, 403, 422).
   - Đẩy nhánh `feat/SCRUM-134-delete-link-contract` lên remote và tạo PR cho `DrugTime-api_contract`.

3. **Dựng Bộ Test Case Excel (`wf-testcase`):**
   - Xây dựng spec `work/3.26-delete-links/testcases.json`.
   - Sinh file `work/3.26-delete-links/testcases.xlsx` và gộp vào file tổng `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.

4. **Duyệt cổng giai đoạn (`gate.py`):**
   - Người duyệt chạy các lệnh duyệt trong terminal:
     ```powershell
     python .agents/scripts/gate.py approve 3.26-delete-links requirement
     python .agents/scripts/gate.py approve 3.26-delete-links plan
     python .agents/scripts/gate.py approve 3.26-delete-links implement
     ```
