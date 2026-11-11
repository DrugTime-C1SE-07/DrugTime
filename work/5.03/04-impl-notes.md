---
task: 5.03
stage: implement
owner: Bao Nguyen
started_at: 2026-11-11 10:14
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-11 20:40 +0700
content_hash: sha256:27a7c7ea69fad2b1
inputs:
  01-requirement.md: sha256:27fa780328dcbe8e
  02-contract.md: sha256:43a6bbd0c729803a
  03-plan.md: sha256:9aa8b9ed860a97cf
---

# 5.03 · Triển khai

## 1. Tiến độ

| Bước | Trạng thái | Kiểm tra và bằng chứng |
|---|---|---|
| P1 | Xong | Áp dụng toàn bộ migration trên PostgreSQL 18 sạch bằng `psql`, kiểm RLS và grant OTP trong smoke test. `evidence/implement-db-reset.log`, `evidence/implement-db-smoke.log`. |
| P2 | Xong | Adapter Auth đọc email xác minh của chính chủ, route kiểm phiên Mobile, SMTP TLS và lỗi được kiểm bằng mock. `evidence/implement-focused.log`. |
| P3 | Xong | OTP dùng một lần, có hạn, gắn với tài khoản/email/mục đích, thử sai giữ bộ đếm, gửi lại giữ giới hạn. Ca đồng thời chạy qua HTTP và PostgreSQL. `evidence/implement-focused.log`, `evidence/implement-db-smoke.log`. |
| P4 | Xong | Hai route khớp operation ID, bearer và mã trạng thái theo contract. `201` và `200` cùng hạn, `409` tại hạn, OTP không lộ qua lỗi validation. `evidence/implement-focused.log`, `evidence/implement-db-smoke.log`. |
| P5 | Xong | PEP đọc trạng thái DB. Smoke test kiểm lịch uống trả 403, audit `denied` bền vững, danh sách người thân bỏ tài khoản chờ xóa, và quyền trở lại sau khi fixture hủy. Unit test kiểm scope gợi ý món. `evidence/implement-focused.log`, `evidence/implement-db-smoke.log`. |
| P6 | Xong | Lượt quét lọc người nhận và composition root kiểm lại trong transaction mới trước khi gửi push. Kiểm giao dịch quét phải commit trước push và chỉ gửi người còn quyền. `evidence/implement-focused.log`. |
| P7 | Xong phần implement | 113 test tập trung và architecture đạt. Ruff các file thay đổi đạt. Ca tích hợp chính thức được viết ở giai đoạn test theo workflow. `evidence/implement-focused.log`, `evidence/implement-lint-task.log`. |
| P8 | Xong phần bàn giao | Kiểm hạn và cờ PEP trước/sau khi fixture hủy. Bản ghi mới nằm ngoài danh sách quét của worker cũ. Luồng đăng nhập tự hủy và worker xóa sau hạn thuộc đầu việc phụ thuộc. `evidence/implement-focused.log`, `evidence/implement-db-smoke.log`. |
| P9 | Xong | Migration đổi email chạy cùng chuỗi migration từ DB PostgreSQL 18 sạch. Kiểm RLS và quyền của năm role. `evidence/implement-reopen-db-reset.log`, `evidence/implement-reopen-db-grants.log`. |
| P10 | Xong phần implement | Ba route xác minh hai địa chỉ, dùng OTP riêng và có giới hạn. Thử lỗi Auth sau khi email đã đổi trên PostgreSQL thật với provider giả lập, kiểm marker còn lưu, chặn OTP xóa trong thời gian đối soát và vô hiệu OTP xóa cũ khi phục hồi. `evidence/implement-reopen-focused.log`, `evidence/implement-reopen-profile-db.log`. |
| P11 | Xong | `PUT /profile` trả 409 khi đổi email trực tiếp và giữ nguyên các trường trong request bị từ chối. Các lần lưu hồ sơ hợp lệ không ghi cột email, tránh ghi đè nếu đổi email đồng thời. Kiểm qua HTTP/DB và unit. `evidence/implement-reopen-profile-db.log`, `evidence/implement-reopen-final-profile.log`. |
| P12 | Xong phần implement | Mỗi cảnh báo dùng chung khóa theo tài khoản với thao tác tạo yêu cầu. Kiểm với transaction PostgreSQL và gateway giả lập: nếu đang gửi, yêu cầu đợi lần gửi kết thúc trước khi commit; sau commit, lượt gửi tiếp theo bị chặn. `evidence/implement-reopen-fcm-race.log`. |
| P13 | Xong | Đóng transaction đọc danh tính trước use case, giới hạn số lượt SMTP đồng thời. Smoke test pool hai kết nối cho kết quả 201, 429 và 503 khi quá tải có kiểm soát. `evidence/implement-reopen-pool.log`. |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| `backend` | `feat/deletion-request-record-creation` | Migration và các file nguồn/test trong `evidence/implement-scope.log`. Tất cả file backend thay đổi được `scope.py` đánh `[OK]`. |

`scope.py` trả mã khác 0 vì diff `api_contract/openapi.json` đã duyệt từ giai đoạn contract và ba file Firebase của Mobile ngoài task. Các file đó không được sửa trong giai đoạn implement. Người dùng đã yêu cầu bỏ qua thay đổi ngoài task.

Vòng sửa dùng cùng nhánh. Tất cả file nguồn, migration và unit test của vòng sửa được đánh `[OK]`. File test tích hợp hiện có từ giai đoạn test trước cũng được liệt kê ngoài phạm vi implement. Xem `evidence/implement-reopen-scope.log`.

## 3. Kết quả test cuối

| Lệnh | Kết quả | Log |
|---|---|---|
| `python -m pytest -p no:cacheprovider tests/unit tests/architecture -q` | 2.036 đạt, 14 lỗi contract tái hiện trên backend HEAD trước task. | `evidence/implement-final-backend.log`, `evidence/implement-baseline-contract.log` |
| `python -m ruff check <các file Python thay đổi>` | Đạt. Ruff toàn backend báo 63 lỗi ngoài file task. Chạy lại trên bản sao backend HEAD cho cùng số lỗi. | `evidence/implement-lint-task.log`, `evidence/implement-lint-backend.log`, `evidence/implement-baseline-lint.log` |
| `python work/5.03/scratch/verify_db.py` | Đạt trên DB cô lập. Email/Auth giả lập, DB và route thật, gồm gọi song song, RLS, PEP và phục hồi quyền theo fixture. | `evidence/implement-db-smoke.log` |
| `python -m pytest -p no:cacheprovider tests/unit tests/architecture -q` sau vòng sửa | 2.042 đạt, 14 lỗi contract trùng với baseline trước task. | `evidence/implement-reopen-final-profile.log` |
| `python -m pytest -p no:cacheprovider -q tests/integration/test_deletion_creation_flow.py` | 18 ca tích hợp hiện có đạt sau migration mới. | `evidence/implement-reopen-old-integration.log` |
| Ruff trên các file Python thay đổi | Đạt. | `evidence/implement-reopen-lint.log` |

## 3b. Bộ test case Excel

Làm ở giai đoạn test.

## Sửa các phát hiện R4–R6

| Mục | Thay đổi | Bằng chứng |
|---|---|---|
| R4 | Đổi tên model lỗi thành `EmailChangeValidationError` để FastAPI không ghi đè component. Kiểm cả ba route, giải tham chiếu 422 và xác nhận `detail` có hai dạng mảng và chuỗi. | `evidence/implement-r4-r6-unit.log` |
| R5 | Đặt `lock_timeout` cục bộ 5 giây trước khi lấy khóa tạo OTP hoặc xác nhận xóa. PostgreSQL báo hết hạn đợi khóa được đổi thành 503. | Unit test và PostgreSQL thật. Hết hạn sau 5,04 giây. Tài khoản khác lấy được khóa và tài khoản đang đợi thử lại được sau khi khóa được nhả. Xem `evidence/implement-r4-r6-db-timeout.log`. |
| R6 | Bỏ nhánh gọi bù Auth và hàm `restore_profile_email` cũ. Route hồ sơ trả 204 sau khi commit; lỗi commit vẫn trả 500 chung. Giữ kiểu trả về của cổng hồ sơ nội bộ theo phạm vi file đã duyệt. | Unit test và hồi quy HTTP/DB trong `evidence/implement-r4-r6-focused.log`. |

- `python -m pytest -p no:cacheprovider -q tests/unit tests/architecture` có 2.042 ca đạt và 14 lỗi trùng ID với baseline trước 5.03. Xem `evidence/implement-r4-r6-unit.log` và `evidence/implement-r4-r6-baseline.log`.
- 44/44 ca hồi quy trên ba file integration của 5.03 đạt trên PostgreSQL cục bộ. Xem `evidence/implement-r4-r6-focused.log`.
- Ruff đạt cho bảy file đã sửa. `scope.py` đánh OK cả bảy file. Mã thoát 1 đến từ các diff đã có của contract, integration test và ba file Firebase ngoài task. Xem `evidence/implement-r4-r6-lint.log` và `evidence/implement-r4-r6-scope.log`.

## 4. Migration

Migration `20261111031400_deletion_request_creation.sql` đã chạy cùng toàn bộ chuỗi migration trên PostgreSQL 18 sạch với các role Supabase được tạo trước. Docker chưa chạy và Supabase CLI không có trên PATH, nên chưa chạy `supabase db reset`. Dùng DB local riêng, không kết nối môi trường dùng chung. Kiểm quyền `api_role`, `worker_role`, `anon`, `authenticated`, `service_role` trên bảng OTP.

## 5. Ghi chú cho người review

- AC1–AC3, QD-35: bước OTP, một yêu cầu mở, mốc 720 giờ và lưu nhất quán đã được kiểm bằng unit và smoke test.
- AC4–AC6, QD-28/33/35/41: quyền đọc kiểm lại từ DB qua PEP, audit từ chối lưu riêng, worker kiểm ngay trước gửi. Gợi ý món được chặn qua scope `MEAL`; endpoint gợi ý thực tế chưa có. Ca khôi phục dùng bản ghi hủy trong fixture.
- AC7–AC8: các ca đăng nhập tự hủy và worker tự xóa cần chạy khi tích hợp đầu việc phụ thuộc. Hủy/nhận việc xóa cần dùng cùng khóa giao dịch theo tài khoản và hủy hiệu lực OTP cũ.

## 6. Phát sinh

- Không bật luồng cho người dùng trước khi có đăng nhập hủy yêu cầu và worker xóa sau hạn. Môi trường chạy cần cấu hình `DELETION_OTP_HMAC_KEY`, các biến `DELETION_SMTP_*` và quyền Auth server. Kiểm email thực tế cần SMTP của môi trường chạy.
- 14 ca contract cũ lỗi trên cả bản sao backend HEAD chưa có code task khi chạy với OpenAPI hiện tại. Xem `evidence/implement-baseline-contract.log`.
- Vòng sửa thêm `EMAIL_CHANGE_OTP_HMAC_KEY`. `identity.reconcile_email_change` là điểm gọi nội bộ tin cậy để đối soát thao tác đổi email đang dang dở. Kiểm với Supabase Auth/SMTP thật và hoàn thiện test tích hợp của contract mới ở giai đoạn test. Mobile cần hỗ trợ contract đổi email trước khi bật tính năng.

## Bước tiếp theo

- Đang chờ người duyệt xem bản sửa R4–R6 và log.
- Người duyệt chạy `python .agents/scripts/gate.py approve 5.03 implement` và `python .agents/scripts/gate.py reopen 5.03 test` để cập nhật kiểm thử sau vòng sửa.
- Cập nhật lần cuối: 2026-11-11, Codex.
