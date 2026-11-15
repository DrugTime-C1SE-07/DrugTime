---
task: 5.03
stage: review
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-11 20:48 +0700
content_hash: sha256:f1bc76d974c8fd93
inputs:
  01-requirement.md: sha256:27fa780328dcbe8e
  02-contract.md: sha256:43a6bbd0c729803a
  03-plan.md: sha256:9aa8b9ed860a97cf
  04-impl-notes.md: sha256:27a7c7ea69fad2b1
  05-test-report.md: sha256:abd8997c3aad312d
---

# 5.03 · Review

## 1. Kết luận

**Đạt trong phạm vi 5.03.** Đã xác nhận các bản sửa R4–R6. Không còn phát hiện mở trong phạm vi review. Năm ca nghiệm thu tích hợp vẫn Pending.

## 2. Phạm vi đã review

| Submodule | Phạm vi |
|---|---|
| Backend | Đối chiếu `git -C backend diff origin/main...HEAD`, diff đang làm việc và các file mới trong `git ls-files --others --exclude-standard`. Rà soát source, hai migration, unit, architecture và integration test. |
| API contract | Đối chiếu OpenAPI với HEAD theo từng path và schema. Diff gồm năm route mới, `PUT /profile`, schema liên quan và mô tả chính sách chung. So mã trạng thái và schema với `create_app().openapi()`. |
| Docs | Đối chiếu workbook tổng với spec 5.03 và log kiểm giá trị ô của 36 sheet chức năng cũ. |

`scope.py 5.03 --stage implement` đánh OK các file nguồn, migration, unit test và workbook. Lệnh trả mã 1 vì cùng workspace còn OpenAPI và ba file integration thuộc giai đoạn đã duyệt, cùng ba file Firebase ngoài task. Xem `evidence/review-r4-r6-scope.log`.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC3 có bằng chứng API chỉ xác nhận sau commit, hạn đúng 30 × 24 giờ, mã một lần, giới hạn thử, tài khoản chính chủ và không dời hạn khi retry. AC4 kiểm 403, audit từ chối, lọc danh sách và hộp thư, cùng hai thứ tự commit/gửi cảnh báo. AC5 được kiểm qua scope MEAL và AC6 qua bản ghi hủy từ fixture. AC7 và phần thực thi xóa của AC8 phụ thuộc đăng nhập và worker. Test bàn giao AC8 đã kiểm ngay trước, đúng và sau hạn, cùng việc worker cũ bỏ qua hàng mới. |
| Phạm vi | Source và test đều thuộc bảng file đã duyệt theo giai đoạn. Workbook tổng chỉ cập nhật bộ DELREQ và Report theo log kiểm thử. |
| Contract | Mã trạng thái và header của năm route mới và PUT /profile khớp về danh sách. Phản hồi thực tế của các luồng chính có test. Cả ba route đổi email công bố đúng hai dạng lỗi 422 sau khi tách tên schema riêng. |
| Bất biến kiến trúc | Quyết định quyền đọc DB qua PEP ở request mới, đối chiếu liên kết và consent. Audit từ chối ghi riêng, truy cập được phép vẫn dùng audit fail-closed. Thay đổi không đụng bảng access_logs hoặc các cơ chế ghi nhận liều và tương tác thuốc. Hai migration mới có RLS, revoke cho role client, grant API tối thiểu và index phục vụ truy vấn. Đã chạy toàn bộ chuỗi migration trong review trên PostgreSQL 18 từ database sạch, log `evidence/review-reopen-migrations.log`. |
| Bảo mật | OTP gắn tài khoản, email, challenge, bước và mục đích, lưu HMAC. Lỗi validation không trả lại giá trị OTP. Route dùng bearer Mobile. Việc thay email yêu cầu chứng minh cả hai hộp thư, có marker bền vững và khóa chung với API xóa. |
| Xử lý lỗi | Lỗi ghi tạo yêu cầu rollback cùng tiêu thụ OTP. Nếu Auth và hồ sơ chưa đồng bộ sau đổi email, marker chặn các API xóa đến lúc đối soát. Không trả dữ liệu cho người thân khi lần kiểm quyền chặn. |
| Hiệu năng | Có index cho trạng thái chờ và email. Gửi FCM giữ khóa mỗi cảnh báo riêng. API xóa giới hạn chờ khóa theo tài khoản ở 5 giây, trả 503 khi hết thời gian chờ và có thể thử lại. |
| Chất lượng test | Có ca sai/hết hạn/dùng lại, Auth lỗi trước/sau thay email, rollback PostgreSQL, cạnh tranh và timeout. Auth, SMTP và FCM được giả lập ở các ca tích hợp 5.03. |
| Dễ đọc và nhất quán | Luồng OTP chia domain, use case và adapter. Đã bỏ nhánh bù Auth khỏi PUT /profile và giữ giao diện nội bộ của lớp hồ sơ. |
| Đối chiếu bằng chứng | Log implement cuối ghi 2.042 ca đạt, 14 lỗi trùng baseline. Log kiểm thử ghi 49/49 ca tập trung đạt. Toàn bộ tích hợp có 1.280 ca đạt, 8 lỗi trùng ID với baseline, 167 skip và 1 xpass. Spec Excel hợp lệ, hai workbook có 37 ca gồm 32 Pass, 0 Fail và 5 Pending. |

## 4. Phát hiện

| ID | Trạng thái | Xác nhận |
|---|---|---|
| R4 | Đã xử lý | `email_change_http.py:54` dùng model `EmailChangeValidationError` riêng. Test giải tham chiếu schema 422 của cả ba route và xác nhận `detail` dạng chuỗi hoặc mảng. |
| R5 | Đã xử lý | `sql_deletion_creation.py:20` đặt giới hạn chờ khóa 5 giây và ánh xạ SQLSTATE 55P03 thành 503. Hai ca HTTP/PostgreSQL xác nhận yêu cầu chưa được ghi, tài khoản khác hoạt động và có thể thử lại sau khi nhả khóa. |
| R6 | Đã xử lý | `profile_http.py:96` lưu hồ sơ trong transaction, trả 204 sau commit. Đã bỏ nhánh bù Auth và hàm `restore_profile_email`. Test xác nhận lỗi commit trả 500 chung, email khác trả 409 và hồ sơ giữ nguyên. |

Bằng chứng tại `evidence/test-r4-r6-focused.log`, `evidence/implement-r4-r6-db-timeout.log`, `evidence/test-r4-r6-baseline.log` và `evidence/review-r4-r6-focused.log`.

Lượt review chạy lại 90 ca unit và kiểm tra kiến trúc, tất cả đạt. `git diff HEAD --check` đạt cho các file backend đã được Git theo dõi.

### Đối chiếu phát hiện vòng trước

- **R1 đã xử lý.** Sửa hồ sơ chỉ có thể giữ email. Hai hộp thư phải được xác minh trước khi cập nhật kênh đăng nhập. Test trên PostgreSQL kiểm rollback, chặn xóa trong lúc đối soát và vô hiệu OTP cũ sau đổi email.
- **R2 đã xử lý.** Tác vụ gửi và xác nhận xóa dùng chung khóa theo tài khoản. Test điều khiển cả hai thứ tự, hết thời gian đợi khóa và kiểm tài khoản khác vẫn gửi được. Cảnh báo đã được gateway chấp nhận trước commit có thể được FCM giao sau đó.
- **R3 đã xử lý phần giữ hai connection.** Dependency đóng transaction đọc danh tính trước khi use case mở transaction riêng. R5 bổ sung giới hạn chờ khóa ở API xóa.

## 5. Mô tả PR dự thảo

### API contract · `feat(consent): define account deletion and email verification APIs`

5.03 thêm hai endpoint cấp OTP và tiếp nhận yêu cầu xóa sau 30 ngày, ba endpoint đổi email bằng hai OTP, và lỗi 409 của PUT /profile khi gửi email khác. Client Mobile cần luồng xác thực hai hộp thư để đổi email sau khi áp dụng contract. PR liên quan là Backend 5.03 và PR cập nhật con trỏ của superproject.

### Backend · `feat(consent): accept verified account deletion requests`

5.03 lưu yêu cầu xóa đã xác thực, bảo toàn hạn khi retry, giữ dữ liệu và liên kết, tạm chặn quyền người thân và gửi cảnh báo sau commit, chặn tạo gợi ý món qua PEP. Bổ sung luồng đổi email hai bước OTP và đối soát Auth/DB. Kiểm bằng ba file integration của 5.03, unit/architecture và migration DB sạch. Môi trường test có Auth/SMTP thật cần chạy TC-DELREQ-22 và TC-DELREQ-34. Các ca đăng nhập tự hủy, worker xóa và API gợi ý món cần chạy sau khi tích hợp đầu việc phụ thuộc. PR này theo API contract 5.03 và được superproject tham chiếu sau merge.

### Docs · `test(docs): add account deletion test cases`

Cập nhật sheet DELREQ và Report với 37 ca kiểm thử, gồm 32 Pass và 5 Pending. Đối chiếu ID và trạng thái với spec 5.03, và đối chiếu giá trị ô của các sheet chức năng cũ. Tham chiếu PR Backend 5.03 và báo cáo test.

### Superproject · `chore: update submodule pointers for task 5.03`

Cập nhật con trỏ đã merge của API contract, Backend và Docs, kèm artifact và bằng chứng 5.03. Thứ tự merge là API contract → Backend → Docs → superproject. Điền link các PR khi tạo. Nếu squash hoặc rebase merge, dùng SHA đã merge trước khi cập nhật con trỏ.

## 6. Ghi chú cho quy trình

So schema OpenAPI đã resolve tham chiếu với response thực tế, bên cạnh kiểm operation ID, status code và bảo mật. Kiểm này phát hiện xung đột tên component mà ca HTTP độc lập không thấy.

## Bước tiếp theo

- Người duyệt chạy `python .agents/scripts/gate.py approve 5.03 review` nếu chấp nhận kết luận.
- Năm ca Pending là TC-DELREQ-22, 23, 24, 25 và 34. Cần hoàn tất các đầu việc phụ thuộc và nghiệm thu Auth/SMTP trước khi bật luồng cho người dùng.
- Cập nhật lần cuối ngày 2026-11-11, Codex.
