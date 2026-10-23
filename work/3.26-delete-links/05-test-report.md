---
task: 3.26-delete-links
stage: test
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 14:34 +0700
content_hash: sha256:a6678a32b2a61b61
inputs:
  01-requirement.md: sha256:e9780e264d8de972
  03-plan.md: sha256:6cc904b55d5e24ed
  04-impl-notes.md: sha256:502e1520beba53c6
---

# 3.26-delete-links · Test tích hợp

## 1. Môi trường

- Lệnh chuẩn bị: Docker Desktop, Supabase local PostgreSQL (`npx supabase db reset`)
- Nhánh của vùng test tích hợp: `feat-3.26` trên repository `DrugTime-backend` (commit `d03dac4`)

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test | Kết quả |
|---|---|---|
| AC1: Bệnh nhân thu hồi link active | `test_revoke_active_link_sets_revoked_and_clears_sharing` | pass |
| AC2: Người thân tự rời link active | `test_family_member_self_leave_db` | pass |
| AC3: Kẻ lạ hoặc link không tồn tại nhận 403 `khong_co_quyen` | `test_stranger_revoke_active_link_gets_403_and_db_unchanged`, `test_stranger_revoke_nonexistent_link_gets_403`, `test_stranger_revoke_rejected_link_gets_403` | pass |
| AC4: Thu hồi link pending | `test_revoke_pending_link_db` | pass |
| AC5: Idempotency trên link đã revoked (giữ nguyên revoked_at, tắt sharing) | `test_sql_revoke_idempotent_preserves_revoked_at`, `test_revoke_idempotent_via_use_case`, `test_revoke_already_revoked_with_sharing_enabled_true_clears_sharing_db` | pass |
| AC6: Thu hồi có hiệu lực tức thì, PEP từ chối và worker không alert | `test_http_revoke_e2e_flow_and_health_access_denied_under_5s`, `test_worker_scan_missed_doses_does_not_alert_revoked_family_member` | pass |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| QA.02: Rút quyền có hiệu lực ngay $\le 5$s; PEP ghi nhật ký `access_logs` denied | `test_http_revoke_e2e_flow_and_health_access_denied_under_5s` | pass |
| Idempotency: Gỡ lặp lại giữ nguyên `revoked_at` ban đầu qua `COALESCE` | `test_sql_revoke_idempotent_preserves_revoked_at` | pass |
| Data consistency: Ép `sharing_enabled=false` nếu dữ liệu cũ còn true | `test_revoke_already_revoked_with_sharing_enabled_true_clears_sharing_db` | pass |
| Bảo vệ trạng thái: Thành viên nhận 422 trên link rejected, kẻ lạ luôn 403 | `test_owner_revoke_rejected_link_gets_422`, `test_stranger_revoke_rejected_link_gets_403` | pass |
| Worker Job Isolation: Không gửi cảnh báo liều bỏ lỡ cho người thân đã gỡ | `test_worker_scan_missed_doses_does_not_alert_revoked_family_member` | pass |

## 4. Toàn bộ bộ test tích hợp

- Lệnh: `python -m pytest tests/integration/test_sql_family_links.py tests/integration/test_medication_access.py -v`
- Kết quả: 29 passed in 5.57s
- Log: `evidence/implement-integration-tests.log`
- `scope.py --stage test`: Đạt chuẩn cho file test tích hợp `backend/tests/integration/test_sql_family_links.py`.

## 5. Bộ test case Excel

Theo skill `wf-testcase`:

- Spec: `work/3.26-delete-links/testcases.json`
- File task: `work/3.26-delete-links/testcases.xlsx`
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`
- Log: `work/3.26-delete-links/evidence/testcase-xlsx.log`

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Gỡ hoặc tự rời liên kết người thân (`LINKREVOKE`) | 12 | 12 | 0 | 0 |

- Test case `Pending` cần người chạy: Không có (12/12 ca đã được tự động hóa và chạy thực tế trong phiên).
- Bug đã ghi vào Bug Report: Không có.

## 5b. Lỗi sản phẩm tìm thấy

Không có. Mọi trường hợp biên và kịch bản nghiệp vụ đều phản hồi chính xác theo đặc tả.

## 6. Test không ổn định hoặc bị skip

Không có. Cả 29 test tích hợp đều chạy ổn định với 100% pass.

## 7. Phát sinh

- Các file untracked trong thư mục `docs/` và `step3.diff` tồn tại sẵn từ các phiên làm việc trước không thuộc phạm vi task 3.26.

## Bước tiếp theo

- Đang chờ: Người duyệt (Approver / Developer).
- Việc cần làm:
  1. Chuyển lại branch tại worktree backend `C:\Users\Admin\orca\workspaces\DrugTime-backend\feat-3.26`:
     `git checkout feat-3.26` và xóa branch tạm `feat/3.26-contract` tại đó.
  2. Cập nhật `openapi.json` trong submodule `api_contract` và tạo PR cho `DrugTime-api_contract`.
  3. Người duyệt chạy lệnh duyệt các giai đoạn trong terminal:
     ```powershell
     python .agents/scripts/gate.py approve 3.26-delete-links requirement
     python .agents/scripts/gate.py approve 3.26-delete-links plan
     python .agents/scripts/gate.py approve 3.26-delete-links implement
     python .agents/scripts/gate.py approve 3.26-delete-links test
     ```
  4. Tiến hành giai đoạn 6: `review` (`wf-review`).
- Cập nhật lần cuối: 2026-10-23 13:48, Antigravity
