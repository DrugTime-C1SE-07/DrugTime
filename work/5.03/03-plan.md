---
task: 5.03
stage: plan
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-11 11:03 +0700
content_hash: sha256:9aa8b9ed860a97cf
inputs:
  01-requirement.md: sha256:27fa780328dcbe8e
  02-contract.md: sha256:43a6bbd0c729803a
---

# 5.03 · Kế hoạch triển khai yêu cầu xóa tài khoản

## 1. Giải pháp

Module `consent` sở hữu OTP và yêu cầu xóa. Hai route trong OpenAPI chỉ chấp nhận phiên Mobile của chính chủ. Backend lấy email đã xác minh từ bản ghi Supabase Auth theo ID phiên qua `identity.api`, kiểm tra lại email khi xác nhận để mã phát trước khi đổi email không còn dùng được. Gửi OTP bằng adapter SMTP có TLS, timeout và cấu hình riêng. Backend hiện chưa có dịch vụ gửi email theo mục đích xóa. Dùng SMTP để tận dụng hạ tầng email mà không dùng lại OTP đăng nhập, vốn có thể cấp phiên và tạo tài khoản.

Đề xuất mặc định OTP sống 5 phút, cách hai lần gửi ít nhất 60 giây, tối đa 5 lần gửi mỗi giờ và 5 lần thử sai trong 15 phút trên mỗi tài khoản. Gửi lại không đặt lại bộ đếm thử. Sinh mã bằng nguồn ngẫu nhiên bảo mật, lưu HMAC với khóa bí mật riêng và gắn với user, challenge, email và mục đích xóa. Không lưu mã gốc. Tuần tự hóa phát, thử và tiêu thụ OTP theo tài khoản. Lưu bộ đếm thất bại bền vững dù trả lỗi. Khi gửi email, chỉ công bố challenge mới sau khi SMTP chấp nhận và DB commit. Nếu lỗi, trả 503, giữ challenge trước đó nếu còn hạn và vẫn tính lần gọi vào giới hạn gửi.

Xác nhận OTP và ghi yêu cầu trong cùng transaction. Khi có yêu cầu chờ hợp lệ, mã mới trả `200` với hạn gốc. Khi chưa có thì tạo và trả `201`. Mã đã dùng trả `422`. Khi đã đến hạn, trả `409 deletion_request_due` và giữ trạng thái chờ xử lý. Thời hạn lấy từ đồng hồ máy chủ và cộng đúng 30 × 24 giờ. `cho_xoa` là trạng thái công khai. Hàng mới dùng `cho_duyet` nội bộ kèm thời hạn, do đó worker cũ chỉ quét `da_duyet` sẽ không xóa hàng mới. Luồng đăng nhập và worker mới sẽ nhận bàn giao từ hai mốc `scheduled_deletion_at` và `cancelled_at`; hai luồng này cần hoàn tất trước khi bật tính năng cho người dùng.

PEP đọc cờ chờ xóa từ `consent.api` trong mỗi lần kiểm quyền. Từ chối người thân trên mọi scope và từ chối tạo gợi ý món mới cho tài khoản chờ xóa. `GET /family/patients` và hộp thư người thân lọc qua điều kiện đó trước khi trả dữ liệu. Worker kiểm quyền khi chọn người nhận và kiểm lại trong transaction mới ngay trước khi gọi gateway. Các quyết định được ghi audit qua cơ chế hiện hành, trong đó denied ghi riêng và lỗi ghi audit không trả dữ liệu. Khi hủy yêu cầu, các điều kiện liên kết và consent hiện tại tiếp tục quyết định quyền xem.

### Bổ sung sau review R1–R3

- **R1, bảo vệ kênh email:** Đề xuất chỉ đổi email đăng nhập sau khi chính chủ xác nhận OTP gửi đến email hiện tại đã được xác minh. Email mới tiếp tục phải được xác minh quyền sở hữu trước khi trở thành kênh đăng nhập và nhận OTP xóa. Khi thay đổi hoàn tất, challenge xóa đã phát cho email cũ hết hiệu lực. Dùng một mục đích OTP riêng cho thay email, không chấp nhận challenge xóa hay OTP đăng nhập. Không ghi OTP, email đầy đủ hoặc thông tin sức khỏe vào log. Nếu email cũ không truy cập được, luồng khôi phục cần đặc tả riêng, không tự thay email dựa trên phiên đang mở.
- **R1 contract đã duyệt lại:** `PUT /profile` trả `409 email_change_verification_required` và không cập nhật bất kỳ trường nào nếu email chuẩn hóa khác email hiện tại. Ba route `POST /me/email-change/otp`, `/verify-current` và `/confirm` thực hiện hai lần OTP. Mỗi challenge gắn tài khoản, email cũ, email mới và trạng thái, mã dùng một lần. `expires_at` trả theo UTC, mỗi giai đoạn hiệu lực 5 phút. Tối đa 5 lần gửi mỗi giờ, 5 lần thử sai mỗi 15 phút và cách lần gửi trước 60 giây theo tài khoản, không reset bộ đếm khi phát lại. Client mất phản hồi ở bước xác minh email cũ phải bắt đầu lại, mất phản hồi cuối thì đọc lại `GET /profile`. Client cũ gửi email mới sẽ nhận 409. App mới là phụ thuộc trước khi bật tính năng xóa.
- **R1 dữ liệu và tính nhất quán Auth/DB:** Migration mới tạo bảng `email_change_challenges` với `user_id` duy nhất, `challenge_id` UUID, email cũ/mới đã chuẩn hóa, giai đoạn, digest HMAC, mốc phát/hết hạn, lần thử và giới hạn. Bảng chỉ cho `api_role` qua RLS, không cho role client và worker. Khóa HMAC có cấu hình riêng, có domain tách biệt giữa OTP cũ/mới và OTP xóa. Các bước chuyển trạng thái và thử sai được ghi bền vững. Email cũ được lấy trực tiếp từ Auth theo user đã đăng nhập; không nhận email cũ từ client. Auth và DB phải so sánh cùng địa chỉ hiện tại dưới khóa theo user trước khi chuyển bước.
- **R1 lỗi giữa Auth và DB:** Trước khi cập nhật email trên Auth, ghi bền vững marker `applying` chứa email cũ/mới và challenge đã xác minh, rồi commit marker. Giữ khóa advisory cấp session `hashtextextended('account-deletion:' || user_id, 0)` trên một connection riêng trong suốt quá trình commit marker, gọi Auth và cập nhật DB/OTP xóa. Mọi thao tác tạo OTP/xác nhận xóa hoặc đổi email dùng cùng khóa tương ứng. Phải giải phóng khóa trong `finally`; nếu không chắc đã mở khóa, đóng hẳn connection thay vì trả connection còn khóa về pool. Thành công chỉ trả 204 sau khi Auth và DB trùng email mới đã xác minh, challenge xóa cũ đã vô hiệu và marker hoàn tất. Khi Auth thất bại hoặc kết quả không chắc chắn, giữ marker; các route đổi email và OTP xóa trả 503 fail-closed cho tài khoản đó. Không tự gửi OTP xóa tới địa chỉ đang trong trạng thái chưa đối soát. Bước đối soát/khôi phục vận hành phải được đặc tả trong code và test: đọc Auth và DB, đối chiếu marker, chỉ hoàn tất nếu đã chứng minh đúng email mới hoặc khôi phục email cũ; nếu chưa chắc thì giữ chặn. Không log email hay OTP. Marker cho phép tiến trình sau nhận biết cả trường hợp crash sau khi Auth thành công.
- **R2, thứ tự gửi:** Với từng cảnh báo, mở transaction ngắn, lấy khóa advisory dùng cùng khóa `account-deletion:<patient_id>` như luồng tạo yêu cầu, đọc lại trạng thái chờ xóa, link và consent từ DB. Nếu đủ quyền, thực hiện một lần gửi FCM trong khi giữ khóa, với timeout kết nối/đọc/ghi/pool hữu hạn, rồi kết thúc transaction trước khi xử lý cảnh báo khác. Nếu tạo yêu cầu đã commit trước khi khóa được lấy, không gửi; nếu FCM đã bắt đầu dưới khóa, commit yêu cầu đợi tới khi lần gửi đó kết thúc. Khóa, kiểm quyền và gửi thất bại đều fail-closed; không giữ khóa cho cả lô. Không hứa thu hồi push mà FCM đã chấp nhận trước commit.
- **R3, pool kết nối:** Dependency xác thực cho hai endpoint xóa và ba endpoint đổi email lấy và đóng transaction đọc user trước khi use case giữ connection riêng; không mở thêm DB connection trong lúc đang giữ khóa theo tài khoản. Tạo giới hạn đồng thời cho SMTP bằng semaphore theo process và dùng timeout Auth/SMTP hữu hạn; kiểm thêm pool size 2 và nhiều request. Giữ nguyên các điều kiện 201, thay challenge, gửi lỗi và giới hạn thử của contract. Marker `applying` ở trên cho phép nhận biết kết quả không chắc chắn, không suy thành công từ lỗi mạng.

Các phương án trên là dự thảo kỹ thuật để xử lý phát hiện review. Thời gian giữ khóa khi gọi FCM có thể ảnh hưởng độ trễ tạo yêu cầu xóa và SLO cảnh báo, cần đo bằng test với FCM giả lập chậm, timeout và nhiều bệnh nhân độc lập.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/5.03/01-requirement.md`, `02-contract.md`, `api_contract/openapi.json` | AC1–AC8, hai endpoint, mã lỗi và ranh giới với đăng nhập/worker đã duyệt. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 6, 8–11, baseline `QD-2026-10-03-v1` | Dấu ✅ là nhóm chốt trong baseline, chưa có chữ ký Mentor. Mốc 7 ngày ở nguồn được thay bằng 30 ngày trong yêu cầu đã duyệt. |
| `backend/.../consent/adapters/outbound/sql_consent.py`, `application/execute_erasure.py`, migration `20260927082912_rebuild_schema_v11.sql` | Cột ID thực tế là `bigint`, model worker hiện dùng UUID. Luồng 5.03 giữ ID nội bộ và chuyển kiểu worker ở đầu việc phụ thuộc. |
| `backend/.../identity/api.py`, `adapters/inbound/dependencies.py`, `adapters/outbound/supabase_auth.py`, `adapters/outbound/sql_users.py` | Có app session và adapter Auth. Email trong hồ sơ có thể được cập nhật qua luồng khác, nên kiểm email đã xác minh tại Auth. |
| `backend/.../access/domain/rules.py`, `adapters/outbound/facts.py`, `application/authorize.py`, `application/list_linked_patients.py` | Điểm quyết định quyền, audit và danh sách bệnh nhân dùng chung. |
| `backend/.../adherence/application/manage_notifications.py`, `application/scan_missed_doses.py`, `domain/alert.py`, `adapters/outbound/other_modules.py`, `runtime/job_runner.py` | Hộp thư đã kiểm PEP. Push hiện tạo trong lượt quét rồi gửi sau commit, cần kiểm lại trước dispatch. |
| `backend/.../family/application/send_link_request.py`, `adapters/inbound/http.py`, `backend/tests/architecture/test_module_dependencies.py` | Có mẫu giữ bộ đếm thử thất bại và API liên kết. Quan hệ `consent → identity`, `access → consent`, `adherence → access` đã được phép. |
| `backend/.../identity/application/profile.py`, `identity/adapters/outbound/supabase_auth.py`, `medication/adapters/inbound/profile_http.py`, `api_contract/openapi.json` (`ProfileUpdateRequest.email`) | `PUT /profile` hiện đổi email ngay qua Auth Admin. Contract đã duyệt lại yêu cầu 409 cho đổi trực tiếp và xác minh cả hai hộp thư. |
| `backend/.../adherence/application/scan_missed_doses.py`, `notification_gateway/fcm.py`, `notification_gateway/__init__.py`, `shared/db.py` | Hiện kiểm quyền cho cả lô trước khi FCM gửi tuần tự; dependency identity giữ UoW request và use case mở UoW riêng. |

### Quyết định nghiệp vụ áp dụng

| Quyết định và trạng thái | AC | Bước | Test |
|---|---|---|---|
| QD-35 mục 10, baseline. Xác thực lại, ngừng chia sẻ và xử lý AI ngay. Yêu cầu đã duyệt chốt email OTP và 30 ngày. | AC1–AC5 | P1–P7 | U1–U5, I1–I5 |
| QD-28 mục 6 và 8, baseline. Kiểm quyền từng request và trước gửi cảnh báo. QD-33 mục 9, baseline. Audit tối thiểu, fail-closed. | AC4, AC6 | P5–P7 | U4–U5, I3–I5 |
| QD-41 mục 11, baseline. Gợi ý từ mẫu và quy tắc ở giai đoạn 1, dừng tạo mới khi chờ xóa theo yêu cầu đã duyệt. | AC5 | P5 | U4, I3 |
| Yêu cầu đã duyệt. Đăng nhập trước hạn hủy, từ đúng hạn trở đi chuyển xử lý tự động. | AC6–AC8 | P1, P4, P8 | U3, I5–I6 |

## 3. File sẽ thay đổi

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| backend | `supabase/migrations/*_deletion_request_creation.sql` | Thêm | Hạn xóa, trạng thái hủy, challenge OTP và ràng buộc đã triển khai; không sửa migration đã chạy. |
| backend | `supabase/migrations/*_email_change_verification.sql` | Thêm | Challenge đổi email, giới hạn và marker đối soát. |
| backend | `src/drugtime/shared/config.py` | Sửa | Cấu hình gửi email, khóa HMAC và giới hạn. |
| backend | `src/drugtime/modules/identity/api.py` | Sửa | Cổng email Auth đã xác minh và xác thực phiên Mobile. |
| backend | `src/drugtime/modules/identity/adapters/inbound/dependencies.py` | Sửa | Tái sử dụng xác thực phiên và kiểm loại phiên. |
| backend | `src/drugtime/modules/identity/adapters/outbound/supabase_auth.py` | Sửa | Đọc email đã xác minh theo ID tài khoản. |
| backend | `src/drugtime/modules/consent/domain/deletion_creation.py` | Thêm | Chính sách OTP, giới hạn, vòng đời tiếp nhận. |
| backend | `src/drugtime/modules/consent/application/create_deletion_request.py` | Thêm | Luồng phát OTP và ghi yêu cầu. |
| backend | `src/drugtime/modules/consent/application/ports.py` | Sửa | Cổng lưu trạng thái, xác minh email và gửi OTP. |
| backend | `src/drugtime/modules/consent/adapters/outbound/sql_deletion_creation.py` | Thêm | Giao dịch OTP, yêu cầu đang mở và truy vấn cờ chờ xóa. |
| backend | `src/drugtime/modules/consent/adapters/outbound/email_otp.py` | Thêm | SMTP TLS và dịch lỗi không lộ bí mật. |
| backend | `src/drugtime/modules/consent/adapters/inbound/deletion_http.py` | Thêm | Hai endpoint và schema. |
| backend | `src/drugtime/modules/consent/api.py` | Sửa | Gắn router và công bố truy vấn trạng thái. |
| backend | `src/drugtime/main.py` | Sửa | No-store, bảo vệ lỗi validation và lỗi hạ tầng trên hai route. |
| backend | `src/drugtime/modules/access/domain/rules.py` | Sửa | Chặn truy cập trong trạng thái chờ xóa. |
| backend | `src/drugtime/modules/access/adapters/outbound/facts.py` | Sửa | Đọc cờ chờ xóa từ consent. |
| backend | `src/drugtime/modules/access/application/ports.py` | Sửa | Cổng đọc cờ chờ xóa cho worker. |
| backend | `src/drugtime/modules/access/application/authorize.py` | Sửa | Lọc người nhận cảnh báo. |
| backend | `src/drugtime/modules/adherence/domain/alert.py` | Sửa | Giữ patient ID nội bộ để kiểm trước gửi. |
| backend | `src/drugtime/modules/adherence/application/scan_missed_doses.py` | Sửa | Kiểm quyền lại trước gateway. |
| backend | `src/drugtime/modules/adherence/api.py` | Sửa | Truyền transaction factory và cổng kiểm quyền vào dispatch. |
| backend | `tests/unit/test_deletion_creation*.py` | Thêm | OTP, API, provider, thời hạn và tương thích contract. |
| backend | `tests/unit/test_access_authorize.py` | Sửa | Kiểm quyền worker. |
| backend | `tests/unit/test_access_rules.py` | Sửa | Kiểm người thân và scope gợi ý món. |
| backend | `tests/unit/test_alert_dispatch.py` | Sửa | Chặn gửi cảnh báo đã chọn trước lúc yêu cầu được tạo. |
| backend | `tests/architecture/test_health_route_enforcement.py` | Sửa | Kiểm hai route chính chủ và các route đọc tiếp tục đi qua PEP. |
| backend | `tests/integration/test_deletion_creation*.py` | Thêm | Migration, OTP, cạnh tranh, quyền và kiểm điểm bàn giao. |
| backend | `src/drugtime/notification_gateway/fcm.py` | Sửa dự kiến | Gửi và xử lý kết quả theo từng cảnh báo dưới điều phối quyền. |
| backend | `src/drugtime/notification_gateway/__init__.py` | Sửa dự kiến | Timeout FCM hữu hạn theo từng loại thao tác. |
| backend | `src/drugtime/modules/identity/application/profile.py` | Sửa | Ngăn thay email trực tiếp qua profile. |
| backend | `src/drugtime/modules/identity/application/ports.py` | Sửa | Cổng xác minh và cập nhật email. |
| backend | `src/drugtime/modules/identity/application/email_change.py` | Thêm | Use case OTP hai giai đoạn và đối soát marker. |
| backend | `src/drugtime/modules/identity/domain/email_change.py` | Thêm | Chính sách, trạng thái, HMAC và giới hạn OTP. |
| backend | `src/drugtime/modules/identity/adapters/outbound/sql_email_change.py` | Thêm | Challenge, marker, khóa session và transaction. |
| backend | `src/drugtime/modules/identity/adapters/outbound/email_change_otp.py` | Thêm | Gửi OTP an toàn qua SMTP TLS. |
| backend | `src/drugtime/modules/identity/adapters/inbound/email_change_http.py` | Thêm | Ba endpoint đổi email theo contract. |
| backend | `src/drugtime/modules/identity/adapters/inbound/http.py` | Sửa | Đăng ký router đổi email. |
| backend | `src/drugtime/modules/identity/adapters/outbound/sql_users.py` | Sửa | So sánh và cập nhật email hồ sơ dưới giao dịch theo user. |
| backend | `src/drugtime/modules/medication/adapters/inbound/profile_http.py` | Sửa | Giữ PEP, trả 409 và không ghi hồ sơ khi yêu cầu đổi email trực tiếp. |
| backend | `src/drugtime/modules/medication/adapters/inbound/profile_schemas.py` | Sửa | Mô tả field theo contract mới. |
| backend | `src/drugtime/modules/medication/application/manage_profile.py` | Sửa | Xử lý trường email và đảm bảo rollback request. |
| backend | `src/drugtime/modules/medication/adapters/outbound/other_modules.py` | Sửa | Nối xử lý identity theo interface mới nếu cần. |
| backend | `tests/unit/test_deletion_creation_email.py` | Sửa dự kiến | Ca đổi email và thay kênh xác thực. |
| backend | `tests/unit/test_email_change*.py` | Thêm | OTP hai giai đoạn, lỗi và contract route. |
| backend | `tests/unit/test_profile*.py` | Sửa | Điều chỉnh và kiểm hành vi 409 đúng contract đã thay đổi. |
| backend | `tests/unit/test_identity_profile.py` | Sửa | Kiểm lớp identity không đổi email trực tiếp. |
| backend | `tests/unit/test_contract_profile.py` | Sửa | Đối chiếu contract hồ sơ đã thay đổi. |
| backend | `tests/unit/test_fcm_gateway.py` | Sửa | Kiểm timeout và gửi từng cảnh báo. |
| backend | `tests/unit/test_identity_auth.py` | Sửa | Kiểm transaction của dependency và giữ hành vi đăng nhập. |
| backend | `tests/unit/test_alert_dispatch.py` | Sửa dự kiến | Ca đồng bộ gửi theo từng patient. |
| backend | `tests/integration/test_deletion_creation_flow.py` | Sửa giai đoạn test | Ca tranh chấp và đổi email xuyên route. |
| backend | `tests/integration/test_email_change*.py` | Thêm giai đoạn test | Chứng minh hành vi hợp đồng, đối soát và cạnh tranh. |
| backend | `tests/integration/test_profile_api.py` | Sửa giai đoạn test | Cập nhật test contract 409 và rollback hồ sơ. |

## 4. Checklist

- [ ] P1 [backend] Tạo migration mới cho thời hạn, thời điểm hủy và challenge OTP, giữ tương thích dữ liệu cũ — file: `supabase/migrations/*_deletion_request_creation.sql` — AC: AC1–AC3, AC6–AC8 — xong khi: reset DB sạch, kiểm quyền DB và thử khóa trùng đều đạt.
- [ ] P2 [backend] Xây cổng xác thực phiên Mobile, lấy email Auth theo chủ tài khoản, và adapter SMTP — file: `identity/api.py`, `identity/adapters/**`, `consent/adapters/outbound/email_otp.py`, `shared/config.py` trong bảng — AC: AC2 — xong khi: từ chối phiên sai loại, email thiếu xác minh và lỗi nhà cung cấp đúng contract.
- [ ] P3 [backend] Lưu challenge, bộ đếm và HMAC. Thử sai cập nhật bền vững, phát lại giữ giới hạn cấp tài khoản — file: `deletion_creation.py`, `ports.py`, `sql_deletion_creation.py`, `create_deletion_request.py` — AC: AC2–AC3 — xong khi: mã khác tài khoản, hết hạn, bị thay, đã dùng và vượt giới hạn đều bị chặn.
- [ ] P4 [backend] Gắn hai route, ghi yêu cầu và tiêu thụ OTP cùng transaction. Chuẩn hóa lỗi và loại dữ liệu nhập OTP khỏi lỗi validation, giữ schema `detail` — file: `deletion_http.py`, `consent/api.py`, `create_deletion_request.py`, `sql_deletion_creation.py`, `main.py` — AC: AC1–AC3, AC8 — xong khi: kiểm schema, no-store, `201`/`200` giữ nguyên hạn và `409` tại đúng hạn.
- [ ] P5 [backend] Bổ sung cờ chờ xóa vào PEP, dùng cùng điều kiện cho liên kết, hộp thư và scope món ăn. Kiểm trực tiếp 403, audit denied riêng và fail-closed — file: bốn file `access` trong bảng — AC: AC4–AC6 — xong khi: request ngay sau commit không thấy dữ liệu và tài khoản khác vẫn kiểm theo quyền hiện tại.
- [ ] P6 [backend] Kiểm lại quyền ngay trước dispatch trong transaction mới. Khi mất quyền hoặc không kiểm được, bỏ push tương ứng — file: `alert.py`, `scan_missed_doses.py`, `adherence/api.py` — AC: AC4 — xong khi: notification tạo trước commit yêu cầu không phát cho người thân sau khi quyền đã bị chặn.
- [ ] P7 [backend] Chạy unit, architecture, kiểm hợp đồng và ca tích hợp được liệt kê. Rà soát các route gia đình có thể trả thông tin tài khoản đích — file: các file test trong bảng — AC: AC1–AC6 — xong khi: có log và mỗi route có bằng chứng được bảo vệ hoặc ghi phát sinh nếu cần thay đổi ngoài bảng.
- [ ] P8 [backend] Kiểm điều kiện bàn giao trước/sau hạn và khôi phục PEP bằng dữ liệu test, ghi phụ thuộc bật tính năng — file: `tests/integration/test_deletion_creation*.py` — AC: AC6–AC8 — xong khi: có ca kiểm biên và ghi rõ các ca đăng nhập/worker phải được chạy khi hai đầu việc đó tích hợp.
- [ ] P9 [backend] Tạo migration OTP/marker mới, RLS, index và cấp quyền; kiểm reset DB sạch — file: `supabase/migrations/*_email_change_verification.sql` — AC: AC2 — xong khi: không có role client/worker đọc hoặc ghi challenge và ràng buộc từ chối dữ liệu không hợp lệ.
- [ ] P10 [backend] Tạo ba route đổi email, trạng thái hai OTP, giới hạn, chống gửi lặp và marker đối soát. Dùng khóa theo user để phối hợp với OTP xóa — file: `identity/**` đã liệt kê, `consent/application/create_deletion_request.py`, `consent/adapters/outbound/sql_deletion_creation.py`, `shared/config.py`, `main.py` — AC: AC2 — xong khi: OTP email cũ/mới đều phải hợp lệ, email chưa xác minh không trở thành kênh xóa, lỗi từng bước trả đúng contract, và marker còn dang dở chặn xóa an toàn.
- [ ] P11 [backend] Chặn `PUT /profile` đổi email trực tiếp, giữ PEP và rollback toàn bộ trường nếu khác email hiện tại — file: `identity/application/profile.py`, `medication/.../profile_http.py`, `profile_schemas.py`, `manage_profile.py`, `other_modules.py` trong bảng — AC: AC2 — xong khi: trả 409 như contract, update không đổi email vẫn thành công, không ảnh hưởng consent/audit.
- [ ] P12 [backend] Phối hợp khóa tạo yêu cầu với kiểm quyền và gửi từng cảnh báo — file: các file adherence, access, notification gateway trong bảng — AC: AC4 — xong khi: test cạnh tranh dùng barrier xác minh cả hai thứ tự commit/gửi và gateway lỗi không làm gửi trái quyền.
- [ ] P13 [backend] Tách transaction xác thực khỏi use case và kiểm giới hạn kết nối — file: identity dependency, consent HTTP/use case và test trong bảng — AC: AC1–AC3 — xong khi: nhiều request với pool nhỏ kết thúc hoặc nhận lỗi có hạn, OTP và giới hạn vẫn đúng.

## 5. Test

### Unit

| Test dự kiến | AC | Nơi chứa |
|---|---|---|
| U1 `test_deletion_otp_policy` kiểm TTL, dùng một lần, thay mã, khác email/đối tượng, giới hạn gửi và thử | AC2 | `tests/unit/test_deletion_creation_otp.py` |
| U2 `test_mobile_session_and_verified_auth_email` kiểm phiên, email xác minh, lỗi Auth/SMTP và dữ liệu phản hồi không chứa OTP thật | AC2 | `tests/unit/test_deletion_creation_http.py`, `test_deletion_creation_email.py` |
| U3 `test_contract_and_deadline_boundary` kiểm schema, no-store, trước và tại hạn, lỗi không báo thành công | AC1–AC3, AC8 | `tests/unit/test_deletion_creation_http.py` |
| U4 `test_pending_deletion_denies_family_and_new_meal` kiểm vai trò và scope, ca log lỗi không trả dữ liệu | AC4–AC6 | `tests/unit/test_access_rules.py`, `test_access_authorize.py` |
| U5 `test_recheck_before_dispatch` kiểm đã chờ xóa, mất consent, lỗi kiểm quyền và người nhận hợp lệ | AC4 | `tests/unit/test_alert_dispatch.py` |
| U6 `test_email_change_two_proofs_and_recovery` kiểm OTP hai mục đích, sai/hết hạn/lặp, resend, email thay giữa các bước, marker đang xử lý và lỗi Auth/DB. Kiểm update profile trả 409 và không ghi trường khác | AC2, R1 | `tests/unit/test_email_change*.py`, `tests/unit/test_profile*.py` |
| U7 `test_dispatch_lock_and_pool_pressure` kiểm khóa theo từng patient, timeout, lỗi FCM và pool nhỏ không giữ hai connection mỗi request | AC1–AC4, R2/R3 | `tests/unit/test_alert_dispatch.py`, `tests/unit/test_deletion_creation*.py` |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Nơi chứa |
|---|---|---|
| I1 `test_create_and_reject_deletion_request` qua HTTP và DB, fake email/Auth. Kiểm chính chủ, phiên sai, lỗi giao dịch, thử sai và mã đã dùng | AC1–AC2 | `tests/integration/test_deletion_creation_api.py` |
| I2 `test_concurrent_otp_and_open_request_uniqueness` kiểm dùng trùng mã, hạn không dời, OTP và yêu cầu rollback nhất quán | AC1–AC3 | `tests/integration/test_deletion_creation_concurrency.py` |
| I3 `test_pending_blocks_related_reads` kiểm lịch uống/lịch sử, danh sách và hộp thư ngay sau commit. Kiểm 403 và audit, chính chủ, tài khoản khác, thiếu link/consent, đổi patient ID, tắt chia sẻ, rút quyền tức thời và lỗi audit | AC4–AC6 | `tests/integration/test_deletion_creation_access.py` |
| I4 `test_pending_blocks_alert_dispatch` kiểm chặn thông báo mới và đã chọn trước đó | AC4 | `tests/integration/test_deletion_creation_access.py` |
| I5 `test_access_after_cancelled_request` cập nhật bản ghi hủy trong fixture rồi kiểm quyền với liên kết, consent và cài đặt hiện tại | AC6 | `tests/integration/test_deletion_creation_access.py` |
| I6 `test_deadline_handoff` kiểm `now <`, `now =`, `now >` hạn, yêu cầu đã hủy và worker cũ không nhận bản ghi mới. Ca đăng nhập tự hủy trước hạn, không hủy khi refresh/đăng nhập lỗi, và worker xóa khi hết hạn phải chạy ở đầu việc phụ thuộc | AC7–AC8 | `tests/integration/test_deletion_creation_lifecycle.py` |
| I7 `test_deletion_schema_grants` kiểm migration, RLS, role và constraint trên DB thật | AC1–AC3 | `tests/integration/test_deletion_creation_migration.py` |
| I8 `test_change_email_with_both_proofs` kiểm route thật, OTP sai/đúng, resend, cạnh tranh, `PUT /profile` không cập nhật khi đổi email, challenge xóa cũ vô hiệu | AC2, R1 | `tests/integration/test_email_change*.py` |
| I9 `test_email_change_recovery_and_lock` giả lập lỗi và crash ở trước/sau cập nhật Auth, DB commit lỗi, nhiều request đổi email/xóa cạnh tranh. Đối soát thành công và lỗi đều không gửi OTP xóa tới email chưa được xác nhận | AC2, R1 | `tests/integration/test_email_change*.py` |
| I10 `test_deletion_commit_races_fcm_send` dùng barrier, transaction và lock DB thật cho cả hai thứ tự, thêm timeout và hai patient độc lập | AC4, R2 | `tests/integration/test_deletion_creation_flow.py` |

## 6. Migration

- Dùng `supabase migration new deletion_request_creation`. Bổ sung `scheduled_deletion_at` và `cancelled_at` kiểu `timestamptz`, nullable để giữ bản ghi cũ. Hàng mới có hạn đúng 720 giờ kể từ `requested_at`. Ràng buộc thời điểm hủy trong khoảng từ lúc tiếp nhận đến trước hạn. Không sửa migration đã áp dụng và không backfill 30 ngày cho yêu cầu theo chính sách cũ.
- Cập nhật partial unique index theo `user_id` để giữ quy tắc một yêu cầu mở, ngoại trừ hàng đã hủy. Thêm partial index `(scheduled_deletion_at, id)` cho hàng mới còn hiệu lực để worker sau này tìm yêu cầu đến hạn. Cờ PEP dùng index mở theo `user_id`, tiếp tục chặn khi đã qua hạn nhưng chưa hoàn tất. Nếu gặp yêu cầu legacy đang mở không có hạn, fail-closed và trả 503 ở thao tác tạo yêu cầu, đối soát dữ liệu legacy trước khi bật.
- Bảng OTP một hàng mỗi `user_id` (PK/FK, `ON DELETE CASCADE`), lưu UUID challenge, HMAC, thời gian phát/hết hạn/tiêu thụ và cửa sổ giới hạn. Dùng `CHECK` cho thứ tự thời gian, bộ đếm không âm và kích thước digest. RLS bật, chỉ policy và quyền SELECT/INSERT/UPDATE cho `api_role`; kiểm và thu hồi quyền mặc định không cần thiết. `worker_role` chỉ cần quyền đọc trạng thái yêu cầu đã có, không được đọc OTP. Access log giữ cơ chế append-only hiện tại.
- Migration mới `email_change_verification` tạo bảng challenge và marker như mục giải pháp. Dùng FK `users(id)`, PK theo user, unique challenge, `CHECK` trạng thái/giai đoạn, mốc thời gian và bộ đếm, index theo hạn để dọn các challenge không còn dùng. Bật RLS, cấp SELECT/INSERT/UPDATE tối thiểu cho `api_role`, không cấp cho anon/authenticated/worker/service_role. Marker `applying` không được xóa tự động khi quá hạn vì cần đối soát Auth trước.
- Chạy `supabase db reset` trên DB local đã xác nhận, test migration và các test tích hợp. Ghi log dưới `work/5.03/evidence/`. Kế hoạch chưa chạy reset hay test runtime.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| `backend` | `feat/deletion-request-record-creation` |
| `api_contract` | `feat/deletion-request-record-creation`, hợp đồng đã duyệt |

## 8. Rủi ro

- Lỗi gửi email hoặc thời gian chờ DB. Dùng timeout SMTP và giới hạn phát theo tài khoản. Không báo gửi thành công khi chưa lưu challenge. Cần cấu hình SMTP ở môi trường chạy trước khi bật.
- Tái dùng OTP hoặc ghi nhiều yêu cầu khi gọi song song. Khóa theo tài khoản, kiểm ràng buộc DB và rollback hai thao tác tiêu thụ/ghi yêu cầu cùng nhau.
- Dữ liệu đã gửi trước khi yêu cầu commit không thể thu hồi từ thiết bị. Kiểm lại quyền trước dispatch và kiểm PEP trên mọi request lấy nội dung.
- Worker cũ dùng trạng thái và kiểu ID khác. Giữ hàng 5.03 ngoài tập quét của worker cũ. Trước khi bật tính năng, kiểm riêng giao dịch tranh chấp giữa hủy lúc đăng nhập và worker nhận xử lý từ đúng hạn.

## 9. Câu hỏi mở

- Contract đổi email đã được duyệt, bao gồm thay đổi phá vỡ `PUT /profile`. Client Mobile cần đầu việc riêng để hỗ trợ luồng xác minh hai email trước khi bật tính năng xóa.
- Giới hạn OTP là mặc định kỹ thuật đề xuất để người duyệt xem. Tài khoản SMTP thực tế là đầu vào vận hành và không đưa bí mật vào repo.

## 10. Phát sinh

- Cập nhật tài liệu QD-35, chính sách dữ liệu chưa đồng bộ, tài khoản đăng nhập sau xóa và chi tiết khôi phục thuộc các đầu việc đã nêu trong requirement.
- Kiểm tra phạm vi của plan sau reopen tại `evidence/plan-reopen-scope.log`. Contract, code backend và workbook là diff từ các giai đoạn trước. Các file Firebase của Mobile nằm ngoài task theo chỉ dẫn người dùng.

## Bước tiếp theo

- Đang chờ: người duyệt xem plan cập nhật, gồm lưu trạng thái đối soát Auth/DB và thay đổi phạm vi backend.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve 5.03 plan`, sau đó thực hiện lại implement.
- Cập nhật lần cuối: 2026-11-11, Codex.
