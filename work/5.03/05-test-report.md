---
task: 5.03
stage: test
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-11 20:45 +0700
content_hash: sha256:abd8997c3aad312d
inputs:
  01-requirement.md: sha256:27fa780328dcbe8e
  02-contract.md: sha256:43a6bbd0c729803a
  03-plan.md: sha256:9aa8b9ed860a97cf
  04-impl-notes.md: sha256:27a7c7ea69fad2b1
---

# 5.03 · Test tích hợp

## 1. Môi trường

- Backend và tài liệu kiểm thử trên nhánh `feat/deletion-request-record-creation`.
- PostgreSQL 18 cô lập trên `127.0.0.1:55403`. Tạo database `task_503_retest` từ `template0`, tạo schema `extensions` và chạy toàn bộ migration theo thứ tự bằng `psql -v ON_ERROR_STOP=1 -1 -f <file>`. Xem `evidence/test-reopen-migrations.log`.
- Các ca 5.03 dùng route thật, bearer phiên Mobile do backend phát, `api_role` và DB thật. Giả lập Supabase Auth, gửi OTP và giao tiếp FCM. Đồng hồ nghiệp vụ được cố định trong các ca OTP. Môi trường không có Supabase Auth và SMTP thử nghiệm nên chưa xác nhận gửi email thật.
- Lệnh test dùng `TEST_ADMIN_DATABASE_URL=postgresql+psycopg://postgres@127.0.0.1:55403/task_503_retest` và dependency Python ở `work/5.03/scratch/deps`.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test trong `backend/tests/integration/test_deletion_creation_flow.py` | Kết quả |
|---|---|---|
| AC1 | `test_confirm_creates_one_request_with_server_deadline`, `test_insert_failure_leaves_otp_usable_and_never_acknowledges`, `test_delivery_failure_does_not_create_request` | Đạt. `201` sau khi ghi và đúng hạn 30 ngày. Lỗi ghi trả `503`; không tiêu thụ OTP hoặc xác nhận thành công. |
| AC2 | `test_invalid_identity_and_unverified_email_never_create_request`, `test_invalid_otp_cannot_create_request`, `test_rate_limit_persists_after_wrong_otp_and_resend` | Đạt với Auth/email giả lập. Từ chối 401/403/409 theo phiên và email, 422 khi sai cấu trúc, sai/hết hạn/đã thay mã, và 429 khi vượt giới hạn. Không ghi yêu cầu trái phép. Gửi email thật còn Pending. |
| AC3 | `test_concurrent_confirm_with_same_otp_only_commits_once`, `test_confirm_creates_one_request_with_server_deadline`, `test_migration_limits_roles_and_enforces_open_request_uniqueness` | Đạt. Hai xác nhận song song trả một `201`, một `422`. OTP mới trả `200` với hạn gốc. DB chặn yêu cầu mở trùng. |
| AC4 | `test_deletion_revokes_family_reads_immediately_and_keeps_other_patient_visible`, `test_pending_deletion_blocks_meal_creation_and_family_alert_dispatch` | Đạt. Request kế tiếp trả `403` và `denied`, danh sách/hộp thư bỏ thông tin bị chặn, push đã chọn bị giữ lại. Quyền của chính chủ và tài khoản khác vẫn được áp dụng. |
| AC5 | `test_pending_deletion_blocks_meal_creation_and_family_alert_dispatch` | PEP scope `MEAL` chặn tạo gợi ý mới trên DB thật. Ca xem/tạo qua API gợi ý món còn Pending do chưa có endpoint. |
| AC6 | `test_deletion_revokes_family_reads_immediately_and_keeps_other_patient_visible` | Đạt với bản ghi hủy tạo bởi fixture. Người thân được xem lại khi còn quyền, và nhận `403` kèm `denied` ngay sau khi rút consent. |
| AC7 | `TC-DELREQ-23` | Pending. Cần tích hợp đăng nhập tự hủy, kiểm đăng nhập lỗi và OTP xóa cũ. |
| AC8 | `test_deadline_handoff_keeps_request_out_of_legacy_worker`, `TC-DELREQ-24` | Đạt phần 5.03 tại hạn −1 giây, đúng hạn và +1 giây. `200` trước hạn, `409` từ đúng hạn. Worker cũ không chọn hàng mới. Tự động xóa và thiết lập mới còn Pending. |

### Kiểm thử bổ sung sau khi mở lại

| Plan | Ca kiểm thử | Kết quả |
|---|---|---|
| I8 · AC2 | `test_profile_rejects_unverified_email_change_and_preserves_fields`, `test_change_email_with_both_proofs_and_invalidate_deletion_otp`, `test_email_resend_cooldown_and_replaced_expired_otp` | `PUT /profile` trả 409 và giữ nguyên toàn bộ hồ sơ khi gửi email khác. Gửi lại với email hiện hành lưu được các trường khác. OTP sai, đã thay, hết hạn và sai bước trả 422. Gửi lại sớm trả 429. Hai xác nhận email mới song song chỉ cập nhật một lần. OTP xóa cũ trả 422 và mã mới đến email mới. |
| I9 · AC2 | `test_email_change_recovery_blocks_deletion_until_addresses_agree`, `test_email_change_holds_deletion_confirmation_until_old_otp_invalidated` | Lỗi trước và sau khi Auth ghi email, cùng lỗi rollback ở PostgreSQL, đều giữ trạng thái `applying`. Khi đang dang dở, hai API xóa trả 503 và không gửi OTP. Đối soát lỗi tiếp tục chặn. Sau đối soát thành công, OTP xóa cũ chỉ dùng được nếu email vẫn là địa chỉ cũ. Xác nhận xóa đang đợi khóa trả 422 khi đổi email hoàn tất trước. |
| I10 · AC4 | `test_deletion_commit_races_fcm_send`, `test_fcm_lock_timeout_skips_only_the_locked_patient` | Kiểm cả hai thứ tự khóa. Nếu lượt gửi giữ khóa trước thì hoàn tất trước khi yêu cầu xóa commit. Nếu giao dịch xóa giữ khóa trước thì lượt gửi bị chặn sau commit. Tài khoản khác vẫn gửi được khi A giữ khóa hoặc hết thời gian đợi khóa. |

Lệnh `python -m pytest -p no:cacheprovider -v -r fEsX tests/integration/test_deletion_creation_flow.py tests/integration/test_email_change_flow.py tests/integration/test_profile_api.py` đạt **44/44** trong 12,88 giây. Gồm 28 ca trực tiếp cho 5.03 và 16 ca hồi quy hồ sơ. Xem `evidence/test-reopen-focused.log`. Ruff trên ba file test đạt, xem `evidence/test-reopen-lint.log`.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Bằng chứng | Kết quả |
|---|---|---|
| Truy cập chéo tài khoản chờ xóa, kể cả người thân đã có quyền hoặc người không có liên kết | Ca AC4/AC6 kiểm lịch uống, `403`, dòng `denied`, danh sách liên kết, hộp thư và tài khoản khác | Đạt |
| Rút consent và gọi lại ngay | Ca AC4/AC6 kiểm sau hủy bằng fixture, rồi rút `family_sharing` và đọc lại | Đạt |
| Gửi trùng, cạnh tranh đồng thời, lỗi transaction | Ca AC1/AC3 kiểm số bản ghi, mã trạng thái, hạn gốc và rollback | Đạt |
| Ngừng chia sẻ qua tác vụ gửi và kiểm quyền gợi ý món | Ca AC4/AC5 qua PEP thật, giả lập kết quả lượt quét để kiểm chặn khi dispatch | Đạt phần backend hiện có |
| Migration sạch, RLS và quyền tối thiểu | Log migration và ca quyền DB kiểm bốn role không có quyền bảng OTP, hạn sai và hàng mở trùng bị từ chối | Đạt |

### Hồi quy sau khi sửa R4–R6

Lượt này dùng database cục bộ `task_503_review` đã áp dụng toàn bộ migration từ database sạch ở vòng review. Chạy ba file integration của 5.03, `tests/unit/test_email_change_http.py` và `test_profile_put_returns_safe_500_if_database_commit_fails`. Kết quả **49/49 đạt** trong 23,11 giây, gồm 46 ca tích hợp và ba ca unit. Ruff file tích hợp cập nhật đạt. Xem `evidence/test-r4-r6-focused.log` và `evidence/test-r4-r6-lint.log`.

| Mục | Kết quả |
|---|---|
| R4 · AC2 | Cả ba route đổi email công bố hai dạng `detail` của 422. Gửi OTP sai định dạng bị từ chối và OTP không xuất hiện trong phản hồi. |
| R5 · AC1/AC3 | Hai ca integration giữ khóa bằng phiên PostgreSQL riêng. Cấp OTP và xác nhận xóa đều trả 503, không gửi mail hay ghi yêu cầu. Tài khoản khác tạo yêu cầu được trong khi khóa còn giữ. Sau khi nhả khóa, cả hai thao tác thử lại được, kể cả xác nhận với cùng OTP. |
| R6 · AC2 | Lỗi commit hồ sơ trả 500 chung. Hồi quy HTTP/DB vẫn trả 409 và giữ nguyên hồ sơ khi gửi email khác, trả 204 khi lưu với email hiện hành. |

## 4. Toàn bộ bộ test tích hợp

- `python -m pytest -p no:cacheprovider -q -r fEsX tests/integration` chạy trong 151,66 giây. Kết quả **1.280 đạt, 8 lỗi, 167 skip, 1 xpass**. Xem `evidence/test-r4-r6-integration.log`.
- Đối chiếu ID test cho thấy tám ca đỏ trùng với lần chạy trên bản sao backend `HEAD` trước khi có code 5.03. Các lỗi liên quan fixture xác thực cảnh báo, thời điểm ghi liều, so khớp tên món theo locale và schema notification. Xem `evidence/test-integration-baseline.log` và `evidence/test-r4-r6-baseline.log`.
- `scope.py 5.03 --stage test` đánh `[OK]` cho cả ba file test tích hợp và workbook tổng. Lệnh trả mã 1 vì kiểm toàn bộ workspace và liệt kê 45 file từ diff contract, implement đã duyệt và ba file cấu hình Firebase có sẵn. Xem `evidence/test-r4-r6-scope.log`.

## 5. Bộ test case Excel

- Spec `testcases.json`, file riêng `testcases.xlsx`. Đã gộp chức năng `DELREQ` và cập nhật `Report` trong `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- `validate`, `build`, `merge` đạt. Kiểm đọc lại hai workbook có đúng 37 ID và giá trị ô của 36 sheet chức năng cũ giữ nguyên. Xem `evidence/test-r4-r6-workbook.log`, `evidence/test-r4-r6-workbook-verify.log`.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---:|---:|---:|---:|
| Yêu cầu xóa tài khoản (DELREQ) | 37 | 32 | 0 | 5 |

- `TC-DELREQ-22`: gửi OTP qua SMTP thật đến hộp thư test.
- `TC-DELREQ-23`: đăng nhập lại trước hạn tự hủy yêu cầu.
- `TC-DELREQ-24`: worker tự xóa sau hạn và thiết lập tài khoản mới.
- `TC-DELREQ-25`: tạo/xem gợi ý món qua API thực khi tài khoản chờ xóa.
- `TC-DELREQ-34`: đổi email qua hai hộp thư thực với Supabase Auth và SMTP, sau đó nhận OTP xóa tại email mới.
- Bug Report của 5.03 không có dòng mới.

## 5b. Lỗi sản phẩm tìm thấy

Chưa phát hiện lỗi sản phẩm thuộc phạm vi 5.03. Tám ca đỏ của toàn suite đều tái hiện trên baseline và không được tính là Fail của bộ test case 5.03.

## 6. Test không ổn định hoặc bị skip

- 49 ca kiểm thử tập trung chạy đầy đủ. Các skip sẵn có của suite được ghi lý do trong log, chủ yếu do môi trường thiếu Supabase Auth/Mailpit local.
- Chưa có bằng chứng kiểm thử xuyên suốt đăng nhập, worker xóa hoặc API gợi ý món. Theo requirement đã duyệt, hoàn thành các đầu việc phụ thuộc trước khi bật tính năng.

## 7. Phát sinh

Lượt R4–R6 bổ sung hai biến thể timeout trong file test tích hợp yêu cầu xóa và cập nhật bộ test case. Việc đối chiếu lỗi suite và trạng thái workspace được ghi trong mục 4.

## Bước tiếp theo

- Đang chờ người duyệt xem báo cáo test.
- Người duyệt chạy `python .agents/scripts/gate.py approve 5.03 test`. Giai đoạn tiếp theo là review.
- Cập nhật lần cuối ngày 2026-11-11, Codex.
