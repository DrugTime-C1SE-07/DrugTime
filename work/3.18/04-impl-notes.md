---
task: 3.18
stage: implement
status: ready_for_review
owner: om-cx
---

# 3.18 · Ghi chú thực thi (Implementation Notes)

## 1. File test mới và cấu trúc triển khai

- **File test mới**: `backend/tests/integration/test_family_consent_on_link__3_18.py`
  - Độc lập hoàn toàn, không chỉnh sửa file test có sẵn.
  - Đặt hậu tố `__3_18` cho toàn bộ 7 hàm test.
  - Sử dụng API thật (FastAPI TestClient qua fixture `client`) tương tác với cơ sở dữ liệu PostgreSQL Supabase local qua SQLAlchemy.

## 2. Chi tiết các kịch bản kiểm thử (T1 – T5)

| Mã test | Hàm test | Nội dung kiểm chứng | Tiêu chí (AC) & Quyết định | Kết quả chạy |
|---|---|---|---|---|
| **T1** | `test_consent_on_link_lifecycle_with_audit_logs__T1__3_18` | Luồng tuần tự với cùng JWT token người thân: gửi yêu cầu $\rightarrow$ pending (403 `khong_co_quyen`) $\rightarrow$ patient approve (vẫn 403 do `sharing_enabled=False` mặc định) $\rightarrow$ patient bật chia sẻ qua `PATCH /family/links/{id}/sharing` $\rightarrow$ 200 OK. Kiểm tra tăng chính xác đúng 1 log ở mỗi bước; kiểm tra đầy đủ timestamps và DB row. | AC1, AC3, AC4, AC11<br>(QD-04, QD-28, QD-33) | **PASSED** |
| **T2** | `test_patient_rejects_link__family_denied_with_audit_log__T2__3_18` | Bệnh nhân từ chối link qua API thật `POST /family/links/{id}/reject` $\rightarrow$ link chuyển `rejected`, `rejected_at` NOT NULL, `revoked_at` IS NULL $\rightarrow$ người thân đọc thuốc $\rightarrow$ 403 `khong_co_quyen` + ghi nhận đúng 1 dòng log `result='denied'`, `actor_role='khong_co_quyen'`. | AC2, AC11<br>(QD-04, QD-33) | **PASSED** |
| **T3a** | `test_withdraw_family_sharing_consent_takes_effect_immediately__T3_family_sharing__3_18` | Đang truy cập 200 OK, bệnh nhân rút consent `family_sharing` qua `POST /consents/family_sharing/withdraw` $\rightarrow$ người thân gửi lại request kế tiếp với cùng token $\rightarrow$ 403 `khong_co_quyen` ngay lập tức (không cache) + denied log. | AC8, AC11<br>(QD-28, QD-29, QD-33) | **PASSED** |
| **T3b** | `test_withdraw_health_data_consent_takes_effect_immediately__T3_health_data__3_18` | Đang truy cập 200 OK, bệnh nhân rút consent `health_data` qua `POST /consents/health_data/withdraw` $\rightarrow$ người thân gửi lại request kế tiếp với cùng token $\rightarrow$ 403 `khong_co_quyen` ngay lập tức do vi phạm PEP purpose guard + denied log. | AC8, AC11<br>(PEP, QD-29, QD-33) | **PASSED** |
| **T4** | `test_revoke_link_via_post_endpoint_takes_effect_immediately__T4__3_18` | Đang truy cập 200 OK, bệnh nhân thu hồi link qua `POST /family/links/{id}/revoke` $\rightarrow$ link chuyển `revoked`, `revoked_at` NOT NULL $\rightarrow$ người thân bị từ chối 403 `khong_co_quyen` ngay request kế tiếp (cùng token) + denied log. | AC9, AC11<br>(QD-28, QD-29, QD-33) | **PASSED** |
| **T4_delete** | `test_revoke_link_via_delete_endpoint_pending_baseline_update__T4_delete__3_18` | Bệnh nhân có link chia sẻ hợp lệ (family 200 OK) $\rightarrow$ bệnh nhân thu hồi link qua API thật `DELETE /links/{id}` (PR #39 / commit `5bb4e457`) $\rightarrow$ trả về 204 No Content $\rightarrow$ database row chuyển `revoked`, `revoked_at` NOT NULL, `rejected_at` IS NULL, `sharing_enabled=False` $\rightarrow$ request kế tiếp của family nhận 403 `khong_co_quyen` $\rightarrow$ ghi nhận đúng 1 dòng log `result='denied'`, `actor_role='khong_co_quyen'`, `data_scope='danh_sach_thuoc'`. | AC9 (Route DELETE)<br>PR #39 | **PASSED** (trên commit 5bb4e457) |
| **T5** | `test_relink_after_revoke_does_not_restore_sharing__T5__3_18` | Thu hồi link 1 qua `DELETE` $\rightarrow$ family nhận 403 ngay $\rightarrow$ người thân gửi link request mới $\rightarrow$ bệnh nhân approve link 2 $\rightarrow$ link 2 active nhưng `sharing_enabled=False` (không tự khôi phục quyền chia sẻ cũ của link 1) $\rightarrow$ người thân vẫn 403 cho tới khi bệnh nhân chủ động bật chia sẻ lại cho link 2 $\rightarrow$ sau khi bật chia sẻ, rút consent `family_sharing` khiến family bị chặn 403 ngay. | AC10, AC11<br>(QD-30, QD-28) | **PASSED** |

---

## 3. Phân tích Ngữ nghĩa hai loại Consent (QD-28 vs PEP)

Hệ thống DrugTime áp dụng mô hình phân quyền hai lớp độc lập (conjunction `AND`), được định nghĩa tại `backend/src/drugtime/modules/access/domain/rules.py`:

```python
def _role(f: AccessFacts) -> ActorRole:
    if f.active_sharing_link and f.family_sharing_consent and f.purpose_consent:
        return ActorRole.FAMILY
    return ActorRole.NO_ACCESS
```

1. **Consent `family_sharing` (QD-28)**:
   - Cho phép người bệnh bật tính năng chia sẻ với người thân nói chung.
   - Được kiểm tra trong quy trình cấp mã (`get_link_code`), gửi yêu cầu (`send_link_request`), phê duyệt (`approve`), và tại PEP (`f.family_sharing_consent`).
   - Rút consent này qua API `POST /consents/family_sharing/withdraw` sẽ khiến `f.family_sharing_consent = False`, tước bỏ vai trò `FAMILY` ở request kế tiếp (kiểm thử tại **T3a** và **T5**).
2. **Consent `health_data` (PEP Purpose Guard)**:
   - Là purpose consent bắt buộc cho việc xử lý dữ liệu y tế của bệnh nhân đối với `Scope.MEDICATIONS` (`"danh_sach_thuoc"`), `Scope.HEALTH_PROFILE`, `Scope.ADHERENCE`, `Scope.INTERACTIONS` theo từ điển `SCOPE_PURPOSE`.
   - Rút consent này qua API `POST /consents/health_data/withdraw` sẽ khiến `f.purpose_consent = False`, tước bỏ vai trò `FAMILY` ở request kế tiếp dù link vẫn `active` và `family_sharing` vẫn còn (kiểm thử tại **T3b**).
3. **Kết luận**: Người thân chỉ có thể đọc dữ liệu khi **ĐỒNG THỜI** thỏa mãn 3 điều kiện:
   - Link ở trạng thái `active` và `sharing_enabled=True`.
   - Bệnh nhân có consent `family_sharing` còn hiệu lực.
   - Bệnh nhân có consent `health_data` còn hiệu lực.

---

## 4. Quy ước và Lược đồ Access Logs (QD-33, CD2, CD3)

Theo schema database (`20260927082912_rebuild_schema_v11.sql`) và module access (`backend/src/drugtime/modules/access/`):

- **Lược đồ cột**:
  - `actor_user_id`: UUID người thực hiện gọi API.
  - `actor_role`: Enum `access_actor_role` (`'patient'`, `'family'`, `'admin'`, `'khong_co_quyen'`).
  - `patient_user_id`: UUID của bệnh nhân có dữ liệu được truy cập.
  - `data_scope`: Enum `access_data_scope` (`'danh_sach_thuoc'`, `'ho_so_suc_khoe'`, `'lich_su_tuan_thu'`, `'canh_bao_tuong_tac'`, `'goi_y_bua_an'`).
  - `result`: Enum `access_result` (`'allowed'`, `'denied'`).
  - `rejection_reason`: Chuỗi mô tả lý do (text, nullable).
  - `accessed_at`: Timestamptz (`DEFAULT now()`).

- **Quy ước giá trị khi kiểm thử**:
  - Khi được phép (**Allowed**):
    - `result = 'allowed'`
    - `actor_role = 'family'`
    - `data_scope = 'danh_sach_thuoc'`
    - `rejection_reason = None`
  - Khi bị từ chối (**Denied** - dù người gọi là người thân nhưng link pending/reject/revoke/sharing_off/thiếu consent):
    - `result = 'denied'`
    - `actor_role = 'khong_co_quyen'` (Lưu ý: Không lưu `'family'` vì tại thời điểm kiểm tra, caller không có quyền hợp lệ).
    - `data_scope = 'danh_sach_thuoc'`
    - `rejection_reason = 'khong_co_quyen'`

---

## 5. Xác minh Route Thu hồi: POST vs DELETE

- **Baseline commit hiện tại của superproject backend**: `33867bf` (detached HEAD).
- **Worktree kiểm thử độc lập**: `E:\DrugTIme_main.worktrees\backend-3.18-delete-verify` (commit `5bb4e457ef84617695dce3a32415e9fad8a573de` - merge PR #39).
- **Phát hiện quan trọng về Route Registration**:
  - Trong PR #39 (`http.py` dòng 419-450), endpoint được khai báo là:
    ```python
    @router.delete(
        "/links/{id}",
        status_code=status.HTTP_204_NO_CONTENT,
        operation_id="revokeLink",
    )
    def delete_link(id: int, ...):
    ```
  - Do `router = APIRouter(tags=["family"])` không có prefix `/family`, đường dẫn thực tế của endpoint là **`/links/{id}`** (chứ không phải `/family/links/{id}`). Test unit có sẵn `test_family_delete_link.py` dòng 276 cũng xác nhận rõ `client.delete("/family/links/1")` trả về 404, trong khi `client.delete("/links/1")` xử lý thành công.
  - Test `T4_delete` và `T5` đã hỗ trợ route chuẩn `/links/{id}` (kèm fallback `/family/links/{id}` nếu có prefix trong tương lai).
  - Kết quả trên commit `5bb4e457`: `DELETE /links/{id}` trả về **204 No Content**, chuyển link sang `revoked`, tước quyền ngay lập tức, và ghi đúng access log.

---

## 6. Lược đồ bảng `caregiver_links` và xác minh cơ sở dữ liệu

- Bảng `caregiver_links` trong database có chính xác 9 cột:
  - `id` (bigint, PK)
  - `patient_user_id` (uuid, FK)
  - `family_user_id` (uuid, FK)
  - `status` (link_status: `'pending'`, `'active'`, `'revoked'`, `'rejected'`)
  - `sharing_enabled` (boolean, default false)
  - `linked_at` (timestamptz, default now())
  - `revoked_at` (timestamptz, nullable)
  - `rejected_at` (timestamptz, nullable)
  - `client_uuid` (uuid, nullable)
- Bằng chứng phê duyệt liên kết (confirmation) được lưu tại bảng riêng `family_link_consent_confirmations` (gồm `document_version`, `confirmed_at`).
- Toàn bộ test T1, T2, T4, T4_delete, T5 đều assert trực tiếp vào database để xác nhận đúng trạng thái cột, các mốc thời gian không NULL và tính toàn vẹn của ràng buộc CHECK `(status='revoked') = (revoked_at IS NOT NULL)` và `(status='rejected') = (rejected_at IS NOT NULL)`.
