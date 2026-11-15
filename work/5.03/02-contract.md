---
task: 5.03
stage: contract
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-11 11:00 +0700
content_hash: sha256:43a6bbd0c729803a
inputs:
  01-requirement.md: sha256:27fa780328dcbe8e
---

# 5.03 · API contract

## 1. File đã sửa trong submodule contract

- `api_contract/openapi.json` trên nhánh `feat/deletion-request-record-creation`, tách từ `origin/main` (`75fc702`).

## 2. Thay đổi

| Endpoint | Thêm / sửa / xóa | Tương thích | Tóm tắt |
|---|---|---|---|
| `POST /data-deletion-requests/otp` | Thêm | Không phá vỡ | Gửi OTP đến email đăng nhập đã xác minh của tài khoản. |
| `POST /data-deletion-requests` | Thêm | Không phá vỡ | Xác thực OTP và ghi nhận yêu cầu xóa của chính chủ. |
| API dữ liệu sức khỏe và danh sách liên kết dành cho người thân | Sửa điều kiện quyền | Đổi hành vi có chủ đích | Từ chối quyền xem tài khoản chờ xóa và loại thông tin tài khoản đó khỏi danh sách. Giữ cấu trúc phản hồi. |
| `POST /me/email-change/otp` | Thêm | Không phá vỡ | Xin OTP xác thực qua email hiện tại trước khi đổi email. |
| `POST /me/email-change/verify-current` | Thêm | Không phá vỡ | Xác nhận OTP cũ và gửi OTP tới email mới. |
| `POST /me/email-change/confirm` | Thêm | Không phá vỡ | Xác nhận OTP mới và hoàn tất đổi email. |
| `PUT /profile` | Sửa | **Phá vỡ** | Email khác email hiện tại trả `409 email_change_verification_required`; không cập nhật các trường khác trong cùng request. |

## 3. Chi tiết từng endpoint

- Cả hai thao tác dùng app session bearer của tài khoản cá nhân trên Mobile. URL trên môi trường backend có tiền tố `/api/v1` theo cấu hình ứng dụng. Phản hồi của hai route dùng `Cache-Control: no-store`. Client không gửi email hay ID tài khoản.
- Gửi OTP không có body. `201` trả `challenge_id` và `expires_at`. `409 verified_email_required` xử lý an toàn trường hợp ngoại lệ thiếu email đã xác minh. Tài khoản dùng luồng email bình thường đã có email phù hợp. Gửi lại thành công thay challenge cũ.
- Tạo yêu cầu nhận `challenge_id` và `otp` (chuỗi 6 chữ số). `201` trả `status: cho_xoa`, `requested_at` và `scheduled_deletion_at`. `200` trả cùng trạng thái và thời hạn cũ khi xác nhận bằng mã mới lúc còn yêu cầu đang chờ. Mã cũ đã dùng bị từ chối với `422 deletion_otp_invalid`. Nếu mất phản hồi, client xin mã mới rồi xác nhận lại. Khi yêu cầu đã đến hạn mà chưa hoàn tất, trả `409 deletion_request_due` và giữ nguyên thời hạn.
- OTP gắn với tài khoản và mục đích xóa, có thời hạn, chỉ tiêu thụ một lần và chịu giới hạn thử. Không ghi OTP hoặc payload chứa OTP vào log. Khi backend gặp lỗi tạm thời, trả `503`. Xử lý ghi yêu cầu và tiêu thụ bằng chứng xác thực nhất quán khi retry hoặc chạy đồng thời.
- Thời gian theo RFC 3339 có offset. `scheduled_deletion_at` bằng `requested_at` cộng 30 × 24 giờ, là mốc bắt đầu đủ điều kiện xử lý xóa. Sau mốc này hệ thống tự động xử lý, không qua Admin duyệt. ID nội bộ của yêu cầu không nằm trong phản hồi nên client không phụ thuộc kiểu khóa DB.
- Đổi email gồm ba request theo thứ tự trong OpenAPI. Challenge gắn tài khoản, hai email và giai đoạn, mỗi mã chỉ dùng một lần. Sau khi email mới xác minh và việc đổi hoàn tất, challenge xóa cấp theo email cũ bị vô hiệu. Nếu mất phản hồi khi xác minh email cũ, bắt đầu lại từ đầu; nếu mất phản hồi cuối, đọc lại `GET /profile`. Cả ba endpoint yêu cầu bearer Mobile, không nhận query, trả no-store, và định nghĩa các lỗi 401/403/409/422/429/503 trong OpenAPI.
- Trong bước xác nhận email mới, Auth và hồ sơ phải nhất quán trước khi trả `204`. Khi chỉ hoàn thành được một bên, trả `503`, thực hiện bù hoặc đối soát và không cho địa chỉ chưa xác minh trở thành kênh nhận OTP xóa.

## 4. Thay đổi phá vỡ và client bị ảnh hưởng

- Mobile dùng lịch uống, lịch sử, kiểm tra tương tác và danh sách liên kết cho người thân. Khi tài khoản đích chờ xóa, các màn hình cần xử lý 403 theo hợp đồng hiện có và danh sách có thể không còn tài khoản đó. Không thêm trường, đổi mã trạng thái đã khai báo hoặc thay cấu trúc dữ liệu ở các endpoint hiện có.
- API `GET /family/patients` ở nhánh task liệt kê bệnh nhân chưa nằm trong `origin/main` dùng làm gốc cho contract này. Khi hai đầu việc được tích hợp, endpoint đó phải áp dụng cùng quy tắc loại tài khoản chờ xóa.
- Mobile hiện có `frontend/mobile/lib/features/profile/data/repositories/remote_profile_repository.dart` gọi `PUT /profile`, và `personal_profile_screen.dart` cho người dùng nhập email. Bản app cũ sẽ không đổi được email khi backend áp dụng `409`; nếu gửi đồng thời các thay đổi hồ sơ khác thì toàn bộ request bị từ chối. Cần cập nhật client để lưu các trường khác riêng, chạy ba bước xác thực và xử lý lỗi trước khi bật luồng xóa. Chưa có phiên bản client tương thích trong task này.

## 5. Đối chiếu tiêu chí chấp nhận

| AC | Endpoint phục vụ |
|---|---|
| AC1–AC3 | Hai endpoint mới. Schema và ví dụ mô tả OTP, phiên Mobile, từ chối, xác nhận sau ghi và giữ nguyên hạn khi gửi lại. |
| AC4 | Điều kiện chung trong `info.description` áp dụng cho các API dữ liệu sức khỏe và danh sách liên kết. Không gửi cảnh báo mới chứa thông tin của tài khoản trong thời gian chờ. |
| AC5 | Mô tả trạng thái chờ xóa quy định chặn tạo gợi ý mới. Quy tắc truy cập chung chặn người thân xem. Chưa có endpoint gợi ý món để chỉnh schema. |
| AC6–AC8 | Mô tả điều kiện trước và sau hạn. Đăng nhập tự hủy và worker tự xóa thuộc đầu việc phụ thuộc, cần hoàn tất trước khi bật tính năng. |
| AC2 / review R1 | `PUT /profile` và ba endpoint đổi email ngăn phiên đang mở tự thay email rồi nhận OTP xóa. Các endpoint cần test lặp mã, cạnh tranh, thay email giữa hai giai đoạn và lỗi Auth/DB. |

## 6. Kiểm tra đã chạy

| Lệnh | Kết quả | Log |
|---|---|---|
| `python work/5.03/scratch/validate_contract.py` | Đạt. Kiểm tra JSON, ref nội bộ, operation ID, ví dụ theo schema và hai mốc thời gian. | `evidence/contract-validate.log` |
| `python .agents/scripts/scope.py 5.03 --stage contract` | Chặn do ba file Mobile ngoài phạm vi. `api_contract/openapi.json` nằm trong phạm vi. | `evidence/contract-scope.log` |
| Kiểm ví dụ JSON/schema của ba endpoint mới và chạy lại validator contract xóa | Đạt. | `evidence/contract-email-validate.log` |
| `python .agents/scripts/scope.py 5.03 --stage contract` sau reopen | OpenAPI `[OK]`. Các file backend và workbook từ các giai đoạn trước còn trong workspace, cùng ba file Mobile ngoài task, được báo ngoài phạm vi contract. | `evidence/contract-email-scope.log` |

## 7. Câu hỏi mở

- **Q1 [chặn về chuyển đổi client]:** App Mobile cũ sẽ nhận `409` khi đổi email và chưa có màn hình xác thực hai hộp thư. Đề xuất phát hành client mới hỗ trợ ba endpoint trước khi bật chức năng xóa, đồng thời xử lý `409` an toàn ở client cũ nếu có thể. Vì `PUT /profile` đang được app dùng, người duyệt cần xác nhận chấp nhận thay đổi này và đầu việc client phụ thuộc.
- Thời gian sống cụ thể, giới hạn gửi và số lần thử OTP sẽ được xác định ở plan. Client dựa vào `expires_at` và phản hồi `429`.

## 8. Phát sinh

- Plan cần xác định các điểm kiểm tra quyền, lọc danh sách và chặn cảnh báo tại thời điểm gửi. Luồng hủy khi đăng nhập cần làm mất hiệu lực challenge xóa cũ để không thể tạo lại yêu cầu bằng mã phát trước khi khôi phục.
- Cần đồng bộ schema, đăng nhập, worker và tài liệu QD-35 theo quy trình 30 ngày. Cập nhật con trỏ submodule sau khi thay đổi contract được merge theo `wf-git`.
- `scope.py` phát hiện ba file Firebase của Mobile ngoài task. Theo chỉ dẫn của người dùng, các thay đổi này nằm ngoài phạm vi xử lý và không cản việc bàn giao contract 5.03.
- Cần task Mobile bổ sung luồng đổi email trước khi bật tính năng, và phương án hỗ trợ khi người dùng không truy cập được email cũ. Client hiện tại không thuộc phạm vi code 5.03.

## Bước tiếp theo

- Đang chờ: người duyệt xem thay đổi phá vỡ `PUT /profile` và cách chuyển đổi client ở Q1.
- Việc cần làm: sau khi xác nhận Q1, người duyệt chạy `python .agents/scripts/gate.py approve 5.03 contract`. Giai đoạn tiếp theo là plan.
- Cập nhật lần cuối: 2026-11-11, Codex.
