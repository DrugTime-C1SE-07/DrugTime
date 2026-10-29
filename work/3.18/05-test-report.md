---
task: 3.18
stage: test
status: ready_for_review
owner: om-cx
---

# 3.18 · Báo cáo kiểm thử: Consent-on-link Flow (PB16)

## 1. Môi trường và Baseline

- **Repository**: `DrugTime_main` (superproject) / `backend` (submodule).
- **Trạng thái Git**:
  - Superproject: Branch `feat/3.26-delete-links` (commit `089d14c`).
  - Submodule backend gốc: Commit `33867bf` (detached HEAD, giữ nguyên an toàn, không bị thay đổi).
  - Worktree kiểm thử cô lập: `E:\DrugTIme_main.worktrees\backend-3.18-delete-verify` tại commit `5bb4e457ef84617695dce3a32415e9fad8a573de` (Merge pull request #39: `fix(family): implement idempotent DELETE /links/{id} API (SCRUM-134)`).
- **Hệ thống runtime**:
  - Hệ điều hành: Windows 11.
  - Python: 3.14.7, pytest 9.1.1.
  - Venv chuẩn: `C:\Users\Admin\orca\workspaces\DrugTime-backend\feat-3.26\.venv\Scripts\python.exe` (đầy đủ dependencies `sqlalchemy`, `tzdata`).
  - Docker Postgres (Supabase local): Container `supabase_db_DrugTime-backend` (port 54322, healthy), đã áp dụng an toàn các migrations đến `20261021115000` via `npx supabase migration up --local`.
- **Dữ liệu chuẩn**: Bảng `caregiver_links` theo migrations thật (`backend/supabase/migrations/`).
  - 9 cột: `id`, `patient_user_id`, `family_user_id`, `status`, `sharing_enabled`, `linked_at`, `revoked_at`, `rejected_at`, `client_uuid`.
  - `status` $\in$ {`pending`, `active`, `revoked`, `rejected`}.
  - CHECK: `(status = 'revoked') = (revoked_at IS NOT NULL)`.
  - CHECK: `(status = 'rejected') = (rejected_at IS NOT NULL)`.
  - CHECK: Không được có đồng thời cả `revoked_at` và `rejected_at`.
  - UNIQUE: `(patient_user_id, family_user_id) WHERE status IN ('pending', 'active')`.

---

## 2. Bảng khoảng trống kiểm thử (Gap Analysis — Đã xác minh thực tế)

Tất cả các tên test trong cột "Test hiện có phủ" đã được đối chiếu thực tế qua `pytest --collect-only` (khớp 100%).

| STT | Ca kiểm thử (Scenario) | Đã phủ chưa | Test hiện có phủ (Đường dẫn::Tên test) | Trạng thái sau Task 3.18 |
|---|---|:---:|---|---|
| 1 | Link `pending` + family gọi endpoint dữ liệu (`GET /medications/{id}`) $\rightarrow$ 403 `khong_co_quyen` + `access_logs` `result='denied'` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_pending_grants_no_access__AC1`<br>`tests/integration/test_family_link_request_api.py::test_pending_link_grants_no_access__AC2`<br>`tests/integration/test_family_links_immediate_effect.py::test_every_decision_applies_on_next_request_same_token__AC6` (bước a) | **Đã phủ tuần tự trong T1** (`test_consent_on_link_lifecycle_with_audit_logs__T1__3_18`), assert đúng 1 log mới. |
| 2 | Patient từ chối link (`POST /family/links/{id}/reject`) $\rightarrow$ status `rejected`, `rejected_at` IS NOT NULL $\rightarrow$ family gọi endpoint dữ liệu $\rightarrow$ 403 `khong_co_quyen` + `access_logs` `result='denied'` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_reject_without_consent_and_replay_idempotent__AC14_AC15`<br>`tests/integration/test_family_links_immediate_effect.py::test_every_decision_applies_on_next_request_same_token__AC6` (bước f) | **Đã phủ độc lập trong T2** (`test_patient_rejects_link__family_denied_with_audit_log__T2__3_18`). |
| 3 | Patient approve link (`POST /family/links/{id}/approve` hợp lệ) $\rightarrow$ status `active`, nhưng `sharing_enabled=false` mặc định $\rightarrow$ family gọi endpoint dữ liệu $\rightarrow$ 403 `khong_co_quyen` + `access_logs` `result='denied'` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_success_persists_evidence_and_activates_link__AC2`<br>`tests/integration/test_family_links_access.py::test_approved_link_with_sharing_off_gets_403_and_denied_log__AC6` | **Đã phủ trong T1** (bước 3: sau approve, family gọi vẫn 403 `khong_co_quyen`). |
| 4 | Patient approve link VÀ bật chia sẻ (`PATCH /family/links/{id}/sharing` với `sharing_enabled=true`) + patient có consent $\rightarrow$ family gọi dữ liệu $\rightarrow$ 200 OK + `access_logs` `result='allowed'`, `actor_role='family'` | **Đã phủ** | `tests/integration/test_family_links_access.py::test_approved_link_with_sharing_on_gets_200_and_allowed_log__AC6`<br>`tests/integration/test_family_links_immediate_effect.py::test_every_decision_applies_on_next_request_same_token__AC6` (bước c) | **Đã phủ trong T1** (bước 4: bật sharing $\rightarrow$ family gọi được 200 OK + allowed log). |
| 5 | Patient approve khi CHƯA có hoặc ĐÃ RÚT consent `family_sharing` $\rightarrow$ 403 `consent_revoked` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_missing_or_revoked_patient_consent_403__AC3_AC10`<br>`tests/unit/test_family_manage_links.py::test_withdrawn_consent_blocks_pending_and_replay` | Đã phủ từ trước, regression pass 100%. |
| 6 | Patient approve sai phiên bản văn bản (`document_version` cũ/lạ) $\rightarrow$ 422 `consent_document_outdated` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_outdated_version_and_false_confirmation_422__AC3`<br>`tests/unit/test_family_manage_links.py::test_pending_outdated_version_has_no_writes` | Đã phủ từ trước, regression pass 100%. |
| 7 | Patient approve thiếu xác nhận (`consent_confirmed=false`) $\rightarrow$ 422 validation error | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_outdated_version_and_false_confirmation_422__AC3`<br>`tests/unit/test_family_manage_links.py::test_confirmation_must_be_explicit_boolean_true` | Đã phủ từ trước, regression pass 100%. |
| 8 | Approve lặp lại idempotent: cùng `family_user_id`, `document_version`, `consent_confirmed=true` trên link đã `active` $\rightarrow$ 200 OK, giữ nguyên bằng chứng và `sharing_enabled` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_replay_idempotent_with_same_evidence__AC5_AC9`<br>`tests/integration/test_family_links_api.py::test_approve_replay_returns_current_sharing_enabled__AC9`<br>`tests/unit/test_family_manage_links.py::test_replay_preserves_evidence_and_current_sharing_after_version_change` | Đã phủ từ trước, regression pass 100%. |
| 9 | Link `active` nhưng `sharing_enabled=false` $\rightarrow$ family gọi endpoint dữ liệu $\rightarrow$ 403 `khong_co_quyen` + `access_logs` `result='denied'` | **Đã phủ** | `tests/integration/test_family_links_access.py::test_approved_link_with_sharing_off_gets_403_and_denied_log__AC6`<br>`tests/integration/test_family_links_immediate_effect.py::test_every_decision_applies_on_next_request_same_token__AC6` (bước d) | Đã phủ trong T1. |
| 10 | Rút consent `family_sharing` sau khi link `active` và `sharing_enabled=true` $\rightarrow$ family gọi dữ liệu $\rightarrow$ 403 `khong_co_quyen` ngay request kế tiếp (cùng token) (QD-28, QD-29) | **Đã phủ** | `tests/integration/test_family_links_access.py::test_revocation_takes_effect_immediately_same_jwt__AC7` (param `revoke_consent`)<br>`tests/integration/test_family_links_immediate_effect.py::test_consent_withdrawal_blocks_even_with_sharing_on__AC6` | **Đã phủ động qua API trong T3a** (`test_withdraw_family_sharing_consent_takes_effect_immediately__T3_family_sharing__3_18`) và **T5**. |
| 11 | Rút consent `health_data` (purpose consent của scope) sau khi link `active` và `sharing_enabled=true` $\rightarrow$ family gọi dữ liệu $\rightarrow$ 403 `khong_co_quyen` ngay request kế tiếp (PEP) | **Đã phủ** | `tests/integration/test_medication_access.py::test_family_missing_purpose_consent_or_sharing_off_403` | **Đã phủ động qua API trong T3b** (`test_withdraw_health_data_consent_takes_effect_immediately__T3_health_data__3_18`). |
| 12 | Link bị thu hồi (`revoked`) qua API `POST /family/links/{id}/revoke` $\rightarrow$ family gọi dữ liệu $\rightarrow$ 403 `khong_co_quyen` ngay request kế tiếp (QD-28, QD-29) | **Đã phủ** | `tests/integration/test_family_links_access.py::test_revocation_takes_effect_immediately_same_jwt__AC7`<br>`tests/integration/test_family_links_immediate_effect.py::test_every_decision_applies_on_next_request_same_token__AC6` (bước e) | **Đã phủ trong T4** (`test_revoke_link_via_post_endpoint_takes_effect_immediately__T4__3_18`). |
| 12b | Link bị thu hồi qua route `DELETE /links/{id}` (PR #39 / commit 5bb4e457) $\rightarrow$ 204 No Content $\rightarrow$ family nhận 403 ngay | **Đã phủ** | `tests/unit/test_family_delete_link.py`<br>`tests/integration/test_sql_family_links.py` | **Đã xác minh toàn diện trong T4_delete** (`test_revoke_link_via_delete_endpoint_pending_baseline_update__T4_delete__3_18`) và **T5** trên commit 5bb4e457. |
| 13 | Yêu cầu liên kết lại sau revoke hoặc reject (QD-30) $\rightarrow$ tạo link mới `pending`, không tự khôi phục phạm vi chia sẻ cũ (`sharing_enabled=false`) $\rightarrow$ family gọi dữ liệu $\rightarrow$ 403 | **Đã phủ** | `tests/integration/test_family_link_request_api.py::test_resend_after_revoked_sharing_false__AC9`<br>`tests/integration/test_family_link_request_api.py::test_rejected_1_to_4_times_can_resend__AC8`<br>`tests/unit/test_family_manage_links.py::test_create_link_request_reopens_rejected_or_revoked_pair__AC9` | **Đã phủ end-to-end trong T5** (`test_relink_after_revoke_does_not_restore_sharing__T5__3_18`). |
| 14 | Mọi lượt từ chối (denied) do link pending / reject / revoke / sharing_off / thiếu consent $\rightarrow$ ghi dòng `access_logs` `result='denied'`, `actor_role='khong_co_quyen'`, `rejection_reason='khong_co_quyen'` (QD-33) | **Đã phủ** | `tests/integration/test_family_links_access.py`<br>`tests/integration/test_family_links_immediate_effect.py`<br>`tests/integration/test_family_links_api.py::test_denied_audit_persists_even_when_use_case_fails__AC18` | **Đã kiểm tra chặt chẽ trong T1, T2, T3a, T3b, T4, T4_delete, T5**. |
| 15 | Lượt truy cập allowed của family $\rightarrow$ ghi dòng `access_logs` `result='allowed'`, `actor_role='family'`, `data_scope='danh_sach_thuoc'` (QD-33) | **Đã phủ** | `tests/integration/test_family_links_access.py::test_approved_link_with_sharing_on_gets_200_and_allowed_log__AC6`<br>`tests/integration/test_family_links_immediate_effect.py` | **Đã kiểm tra trong T1, T3a, T3b, T4, T4_delete, T5**. |
| 16 | Phân quyền gọi API approve / reject (Authorization Matrix): Người khác (family, stranger, admin) gọi approve / reject link của patient $\rightarrow$ 403 `khong_co_quyen` (QD-04) | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_denied_caller_matrix__AC4_AC10_AC16`<br>`tests/integration/test_family_links_api.py::test_reject_denied_caller_matrix__AC5` | Đã phủ từ trước. |
| 17 | Chống dò mã và giới hạn yêu cầu (QD-34): sai mã 5 lần khóa 15p (429); reject 5 lần chặn 24h (429); tối đa 10 request/ngày | **Đã phủ** | `tests/integration/test_family_link_request_api.py::test_fifth_failure_locks_then_unlocks__AC10`<br>`tests/integration/test_family_link_request_api.py::test_fifth_rejection_blocks_24h__AC8b`<br>`tests/integration/test_family_link_request_api.py::test_daily_limit__AC14` | Đã phủ từ trước. |
| 18 | Không thể duyệt hoặc từ chối trên link đã ở trạng thái `revoked` hoặc `rejected` (DB state machine & CHECK constraint) | **Đã phủ** | `tests/integration/test_family_links_api.py::test_approve_rejected_or_revoked_conflict_409__AC8`<br>`tests/integration/test_family_links_api.py::test_reject_active_or_revoked_conflict_409__AC15`<br>`tests/unit/test_family_manage_links.py::test_revoked_link_cannot_be_approved_directly__AC9` | Đã phủ từ trước. |
| 19 | Idempotent reject replay: gọi reject lặp lại trên link đã rejected $\rightarrow$ 200 OK giữ nguyên `rejected_at` | **Đã phủ** | `tests/integration/test_family_links_api.py::test_reject_without_consent_and_replay_idempotent__AC14_AC15` | Đã phủ từ trước. |
| 20 | Ràng buộc DB migration & CHECK constraints: `(status='revoked') = (revoked_at IS NOT NULL)`, `(status='rejected') = (rejected_at IS NOT NULL)`, không được có cả hai | **Đã phủ** | `tests/integration/test_migration_family_link_consent.py`<br>`tests/unit/test_family_link_rules.py` | Đã phủ từ trước. |

---

## 3. Kết quả chạy kiểm thử thực tế

### 3.1. Chạy trên Worktree kiểm thử độc lập (Commit `5bb4e457` — HEAD origin/main)
- Lệnh:
  ```powershell
  Set-Location E:\DrugTIme_main.worktrees\backend-3.18-delete-verify
  $env:PYTHONPATH = "E:\DrugTIme_main.worktrees\backend-3.18-delete-verify\src"
  & 'C:\Users\Admin\orca\workspaces\DrugTime-backend\feat-3.26\.venv\Scripts\python.exe' -m pytest tests/integration/test_family_consent_on_link__3_18.py -v -rs
  ```
- Exit code: `0`
- **Kết quả nguyên văn**:
  ```text
  tests/integration/test_family_consent_on_link__3_18.py::test_consent_on_link_lifecycle_with_audit_logs__T1__3_18 PASSED [ 14%]
  tests/integration/test_family_consent_on_link__3_18.py::test_patient_rejects_link__family_denied_with_audit_log__T2__3_18 PASSED [ 28%]
  tests/integration/test_family_consent_on_link__3_18.py::test_withdraw_family_sharing_consent_takes_effect_immediately__T3_family_sharing__3_18 PASSED [ 42%]
  tests/integration/test_family_consent_on_link__3_18.py::test_withdraw_health_data_consent_takes_effect_immediately__T3_health_data__3_18 PASSED [ 57%]
  tests/integration/test_family_consent_on_link__3_18.py::test_revoke_link_via_post_endpoint_takes_effect_immediately__T4__3_18 PASSED [ 71%]
  tests/integration/test_family_consent_on_link__3_18.py::test_revoke_link_via_delete_endpoint_pending_baseline_update__T4_delete__3_18 PASSED [ 85%]
  tests/integration/test_family_consent_on_link__3_18.py::test_relink_after_revoke_does_not_restore_sharing__T5__3_18 PASSED [100%]

  ======================== 7 passed, 1 warning in 4.09s =========================
  ```

### 3.2. Chạy trên Worktree gốc của Submodule (Commit `33867bf` — Detached HEAD)
- Lệnh:
  ```powershell
  Set-Location E:\DrugTIme_main\backend
  $env:PYTHONPATH = "E:\DrugTIme_main\backend\src"
  & 'C:\Users\Admin\orca\workspaces\DrugTime-backend\feat-3.26\.venv\Scripts\python.exe' -m pytest tests/integration/test_family_consent_on_link__3_18.py -v -rs
  ```
- Exit code: `0`
- **Kết quả**: `6 passed, 1 skipped in 4.13s` (T4_delete tự động skip an toàn vì commit `33867bf` chưa tích hợp PR #39).

### 3.3. Toàn bộ Regression Suite liên quan trên Commit `5bb4e457`
- **Đợt 1 (Core family links, access, immediate effect, rules — 204 tests)**:
  - Lệnh: `python -m pytest tests/integration/test_family_consent_on_link__3_18.py tests/integration/test_family_links_api.py tests/integration/test_family_links_access.py tests/integration/test_family_links_immediate_effect.py tests/integration/test_medication_access.py tests/unit/test_family_send_link_request.py tests/unit/test_family_manage_links.py tests/unit/test_family_link_rules.py tests/unit/test_access_authorize.py -q`
  - Kết quả: **`204 passed, 1 warning in 14.52s`** (Exit code 0).
- **Đợt 2 (Link request API, consent migrations — 109 tests)**:
  - Lệnh: `python -m pytest tests/integration/test_family_link_request_api.py tests/integration/test_migration_family_link_consent.py -q`
  - Kết quả: **`109 passed, 1 warning in 12.47s`** (Exit code 0).
- **Đợt 3 (DELETE link unit & SQL integration tests — 25 tests)**:
  - Lệnh: `python -m pytest tests/unit/test_family_delete_link.py tests/integration/test_sql_family_links.py -q`
  - Kết quả: **`25 passed, 1 warning in 3.27s`** (Exit code 0).
- **Tổng cộng Regression liên quan**: **`338 passed / 338 tests, 0 failed, 0 skipped`**.

---

## 4. Tự Review Độc lập (Independent Review)

1. **Xác minh Route DELETE**:
   - Route `DELETE /links/{id}` từ PR #39 đã được kiểm chứng hoạt động chính xác: trả về 204 No Content, cập nhật database `status='revoked'`, `revoked_at` NOT NULL, `rejected_at` IS NULL, `sharing_enabled=False`.
   - Request kế tiếp với cùng token người thân bị từ chối 403 `khong_co_quyen` ngay lập tức và ghi nhận đúng 1 access log denied.
2. **Xác minh Ngữ nghĩa Consent (QD-28 vs PEP)**:
   - Hai consent `family_sharing` và `health_data` hoạt động theo phép hội `AND` độc lập. Rút một trong hai consent đều làm mất quyền truy cập tức thì.
3. **Xác minh Access Logs**:
   - Khẳng định giá trị `actor_role='khong_co_quyen'` cho mọi lượt truy cập bị từ chối, và `actor_role='family'` cho lượt truy cập hợp lệ.
4. **An toàn Git**:
   - Submodule backend gốc giữ nguyên tại `33867bf` không bị thay đổi.
   - Worktree `E:\DrugTIme_main.worktrees\backend-3.18-delete-verify` được tạo cô lập độc lập hoàn toàn để chạy kiểm chứng trên commit `5bb4e457`.

---

## 5. Vấn đề ghi nhận (OPEN / BUG / BLOCKER)

- **OPEN (Requirement vs Privacy by Default)**:
  - AC gốc: *"Patient đồng ý (approve) $\rightarrow$ người thân truy cập được"*.
  - Code thực tế: `domain/link.py:86` thiết lập `sharing_enabled=False` sau approve (Privacy by Default). Người thân chỉ truy cập được khi bệnh nhân chủ động bật công tắc chia sẻ (`PATCH /family/links/{id}/sharing` với `sharing_enabled=true`).
  - Đề xuất: Cập nhật tài liệu SRS/Backlog cho thống nhất với thiết kế an toàn này.
- **BUG**: Không phát hiện lỗi logic trong production code `backend/src/`.
- **BLOCKER**: Đã được **GIẢI QUYẾT TOÀN DIỆN**. Blocker route DELETE đã được giải quyết bằng việc xác minh thực tế trên worktree commit `5bb4e457`.

---

## 6. Kết luận và Trạng thái Nghiệm thu

Toàn bộ các tiêu chí chấp nhận của Task 3.18 (PB16) bao gồm:
- Link pending $\rightarrow$ 403 `khong_co_quyen`.
- Patient reject $\rightarrow$ 403 `khong_co_quyen`.
- Patient approve an toàn $\rightarrow$ 403; Patient bật chia sẻ $\rightarrow$ 200 OK.
- Rút consent `family_sharing` $\rightarrow$ 403 ngay (cùng token).
- Rút consent `health_data` $\rightarrow$ 403 ngay (cùng token).
- Thu hồi link qua `POST /revoke` $\rightarrow$ 403 ngay.
- Thu hồi link qua `DELETE /links/{id}` (PR #39) $\rightarrow$ 403 ngay + database updated.
- Re-link sau thu hồi (QD-30) $\rightarrow$ tạo link mới, không khôi phục sharing cũ.
- Mọi lượt truy cập đều ghi `access_logs` fail-closed chuẩn schema (QD-33).

Tất cả đã được kiểm chứng bằng test tự động và pass 100% trên commit mục tiêu `5bb4e457`.

> **TRẠNG THÁI NGHIỆM THU CHÍNH THỨC: `COMPLETE — VERIFIED`**
