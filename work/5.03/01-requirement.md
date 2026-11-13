---
task: 5.03
title: Backend API tiếp nhận yêu cầu xóa tài khoản
type: feature
stage: requirement
size: L
contract_change: yes
affected: [backend, api_contract]
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-11 10:03 +0700
content_hash: sha256:27fa780328dcbe8e
---

# 5.03 · Backend API tiếp nhận yêu cầu xóa tài khoản

## 1. Mục tiêu

Khi người dùng yêu cầu xóa tài khoản của mình, backend xác nhận đã tiếp nhận sau khi lưu bền vững yêu cầu và đưa tài khoản vào trạng thái chờ xóa 30 ngày. Trong thời gian chờ, dữ liệu vẫn được giữ để người dùng có thể quay lại, còn quyền truy cập của người thân bị tạm chặn.

## 2. Phạm vi

### Trong phạm vi

- API cho tài khoản cá nhân đã xác thực để gửi yêu cầu cho chính mình. Xác thực lại bằng OTP gửi tới email đã gắn với tài khoản. OTP dùng một lần, có thời hạn, gắn với tài khoản và mục đích xóa, có giới hạn số lần thử. Phản hồi tối thiểu đủ để client xác nhận tiếp nhận và hiển thị thời hạn.
- Lưu một yêu cầu đang mở cho mỗi tài khoản. Tính hạn từ thời điểm backend tiếp nhận lần đầu, theo đồng hồ máy chủ. Lần gửi lại khi còn yêu cầu mở không làm thay đổi thời hạn.
- Từ khi yêu cầu được lưu, backend chặn việc người thân xem thông tin của tài khoản đang chờ xóa, gồm cả thông tin hiển thị trong danh sách liên kết và gợi ý món. Giữ liên kết, cài đặt chia sẻ và lịch sử consent. Áp dụng trạng thái chờ xóa làm điều kiện chặn tạo gợi ý món mới khi luồng gợi ý được tích hợp.
- Chốt điểm bàn giao cho luồng đăng nhập và worker. Đăng nhập thành công trước hạn tự hủy yêu cầu và khôi phục quyền truy cập dựa trên liên kết, cài đặt chia sẻ và consent còn hiệu lực. Từ lúc hết hạn, đăng nhập không còn được dùng để hủy yêu cầu. Sau khi xóa hoàn tất, người dùng thiết lập như tài khoản mới và không thấy dữ liệu cũ.

### Ngoài phạm vi

- Màn hình Mobile, giao diện Admin và luồng Admin xử lý ngoại lệ.
- Xác thực lại qua số điện thoại được để cho giai đoạn sau.
- Triển khai hủy yêu cầu trong luồng đăng nhập và thực thi xóa sau hạn. Đây là các phần phụ thuộc cần hoàn tất trước khi bật tính năng cho người dùng.
- Xây tính năng gợi ý món, sửa OCR và quyết định chi tiết cách xóa dữ liệu, xử lý backup, audit và tài khoản đăng nhập sau hạn.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn | Điều rút ra |
|---|---|
| `work/5.03/brainstorm.md` | Lưu các quyết định 30 ngày, hủy khi đăng nhập lại, tạm chặn chia sẻ và gợi ý món, khôi phục quyền theo trạng thái hiện tại. |
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx` | Sprint 5 Backlog gắn 5.03 với API PB34. Replan Log ghi 5.13 nhưng `work/5.13/01-requirement.md` đang thuộc task liệt kê bệnh nhân liên kết. Dùng mã 5.03 theo trao đổi. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 8–11 | QD-35 cũ ghi 7 ngày, ngừng chia sẻ và AI. QD-28 quy định quyền chia sẻ. QD-41 tắt gửi dữ liệu sức khỏe sang LLM ngoài ở giai đoạn 1. |
| `api_contract/openapi.json`, `backend/README.md`, `backend/src/drugtime/modules/consent/adapters/inbound/http.py` | OpenAPI chưa có route tạo yêu cầu xóa. README đánh dấu `done` nhưng router consent còn TODO. API rút consent đã là luồng riêng. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql`, `backend/src/drugtime/modules/consent/application/execute_erasure.py` | Schema có bản ghi yêu cầu và ràng buộc một yêu cầu mở. Worker hiện xử lý yêu cầu đã duyệt, chưa thể hiện chính sách chờ 30 ngày. |
| `backend/src/drugtime/modules/access/application/authorize.py`, `backend/src/drugtime/modules/ai_meal/adapters/inbound/http.py` | Có PEP dùng chung và nhánh chọn người thân nhận cảnh báo. Endpoint gợi ý món còn TODO. |

### Quyết định nghiệp vụ áp dụng

| Nguồn và trạng thái | Quy tắc trong phạm vi | Tiêu chí |
|---|---|---|
| QD-35, mục 10, baseline `QD-2026-10-03-v1`, nhóm đã chốt, chưa có chữ ký Mentor | Xác thực lại khi gửi, ngừng chia sẻ và xử lý AI ngay khi tiếp nhận. Mốc 7 ngày trong tài liệu được thay bằng 30 ngày theo trao đổi với người dùng. | AC1, AC2, AC4, AC5 |
| `brainstorm.md`, người dùng đã xác nhận | Giữ dữ liệu trong thời gian chờ, chặn người thân dù còn liên kết, dừng tạo gợi ý món mới, đăng nhập lại trước hạn tự hủy. Khi hủy, quyền chia sẻ được tính theo liên kết, consent và cài đặt hiện tại. | AC1, AC4–AC8 |
| QD-28 và QD-33, mục 8–9, cùng baseline | Đọc quyền từ DB ở mỗi yêu cầu và trước khi gửi dữ liệu. Ghi audit theo cơ chế dự án, giữ metadata tối thiểu. | AC4, AC6, AC7 |
| QD-41, mục 11, cùng baseline | Quy tắc chặn tạo món theo tài khoản áp dụng cả khi gợi ý dựa trên mẫu và quy tắc. Giai đoạn 1 không gửi dữ liệu sức khỏe cho LLM ngoài. | AC5 |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | API, trạng thái yêu cầu và kiểm soát truy cập khi chờ xóa. Test API và quyền với DB thật trong `backend/tests/integration`. |
| `api_contract` | Có | Đặc tả route, xác thực, thời hạn, phản hồi và lỗi. |
| `frontend`, `tests`, `docs`, `.agents` | Không | Mobile, E2E xuyên service và cập nhật tài liệu nguồn là các đầu việc riêng. |

## 5. Thay đổi API contract

- `contract_change: yes`. Thêm API tiếp nhận yêu cầu xóa cho chính chủ và đặc tả cách client nhận trạng thái, thời hạn, kết quả gửi lại và lỗi xác thực.
- Đường dẫn tham chiếu từ README là `POST /api/v1/data-deletion-requests`. Chốt đường dẫn, mã lỗi và cách biểu diễn trạng thái tại giai đoạn contract. Rà soát tác động lên các API đang trả thông tin cho người thân.

## 6. Vùng rủi ro và bất biến bị chạm

- Phân quyền người thân và dữ liệu sức khỏe. Kiểm trạng thái chờ xóa từ DB qua PEP hiện có, trả 403 và ghi `denied` ở transaction riêng khi truy cập dữ liệu sức khỏe bị từ chối. Các danh sách không trả thông tin của tài khoản đang chờ xóa. Tác vụ gửi không chia sẻ dữ liệu sau khi trạng thái đã có hiệu lực.
- Schema. Schema hiện theo luồng duyệt Admin và chưa thể hiện đầy đủ vòng đời chờ và hủy của quy tắc mới. Nếu cần đổi schema, dùng migration mới và kiểm trên DB sạch.
- Gửi trùng và ranh giới thời hạn. Giữ một yêu cầu mở khi request chạy đồng thời. Luồng hủy và worker cần thống nhất cùng mốc hết hạn để tránh hủy sau hạn hoặc xóa yêu cầu đã hủy.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Tài khoản cá nhân đã xác thực lại và chưa có yêu cầu mở gửi yêu cầu. Backend lưu thành công yêu cầu chờ xóa, trả xác nhận và hạn sau 30 ngày kể từ lúc tiếp nhận, giữ nguyên dữ liệu và liên kết. Nếu lưu lỗi, backend không trả xác nhận tiếp nhận. | integration |
| AC2 | Người gọi chưa đăng nhập, OTP sai, hết hạn, đã dùng, vượt giới hạn thử, thuộc tài khoản hoặc mục đích khác, hoặc cố yêu cầu xóa cho người khác. Backend từ chối và không tạo yêu cầu. OTP hợp lệ được gửi tới email gắn với chính tài khoản. | integration |
| AC3 | Hai request hợp lệ của cùng tài khoản được gửi lặp hoặc đồng thời. Chỉ tồn tại một yêu cầu mở và hạn vẫn tính theo lần tiếp nhận đầu tiên. | integration |
| AC4 | Người thân đã có quyền truy cập trước đó. Ngay sau khi API tiếp nhận, request mới tới API dữ liệu sức khỏe của tài khoản chờ xóa trả 403, có dòng `denied` bền vững và không trả dữ liệu. Danh sách liên kết không trả thông tin của tài khoản này và tác vụ gửi mới không gửi nội dung của tài khoản cho người thân. Tài khoản khác vẫn theo quyền hiện có. | integration |
| AC5 | Tài khoản đang chờ xóa. Kiểm tra quyền gợi ý món từ chối tạo gợi ý mới dựa trên dữ liệu tài khoản và từ chối người thân xem gợi ý cũ. Kiểm thử điều kiện quyền khi endpoint còn TODO, bổ sung test xuyên API khi endpoint được triển khai. | unit / integration phụ thuộc |
| AC6 | Luồng đăng nhập đã hủy yêu cầu trước hạn. Request kế tiếp của người thân thành công nếu liên kết, cài đặt chia sẻ và consent đúng mục đích vẫn hợp lệ. Nếu một điều kiện không còn, request vẫn bị từ chối và ghi `denied`. | integration |
| AC7 | Chính chủ đăng nhập thành công trước hạn. Luồng đăng nhập tự hủy yêu cầu và mở lại dữ liệu cũ. Làm mới token hoặc đăng nhập thất bại không hủy yêu cầu. | integration, phụ thuộc luồng đăng nhập |
| AC8 | Đã đến hạn mà yêu cầu còn hiệu lực. Đăng nhập không hủy yêu cầu, worker có thể xử lý xóa theo chính sách được chốt. Sau khi xóa hoàn tất, thiết lập tài khoản mới không khôi phục dữ liệu cũ. | integration, phụ thuộc worker và đăng nhập |

## 8. Câu hỏi mở

- **Q3 [không chặn 5.03] Xóa cứng và xử lý thông tin đăng nhập sau hạn theo chính sách nào?** Ảnh hưởng: phạm vi worker, sao lưu và tái sử dụng email. Giả định mặc định: xóa dữ liệu cá nhân và tài khoản đăng nhập, giữ audit tối thiểu theo chính sách được duyệt và cho đăng ký mới khi xóa hoàn tất. Việc xử lý dữ liệu chưa đồng bộ cần được chốt trước khi bật worker.

## 9. Giả định

- Người dùng xác nhận sau 30 ngày hệ thống tự động xóa, không chờ Admin duyệt.
- Người dùng chốt xác thực lại bằng OTP qua email đã gắn với tài khoản. Số điện thoại để giai đoạn sau. API OTP đăng nhập hiện có không mặc nhiên là OTP xác thực lại.
- Theo người dùng, luồng vào app dùng email đã xác minh. OTP xóa gửi tới email gắn với chính tài khoản, không nhận địa chỉ tùy ý từ request. Code hiện có hỗ trợ định danh điện thoại; trường hợp tài khoản không có email cần được xử lý fail-closed khi triển khai, không mở thêm luồng xác thực điện thoại trong task này.
- Đề xuất tính 30 ngày theo 30 × 24 giờ kể từ mốc backend tiếp nhận. Đăng nhập trước mốc hết hạn mới được hủy, từ đúng mốc trở đi đã hết hạn. Mốc lưu và trả về phải xác định được chính xác.
- Quy tắc tạm chặn không ghi đè consent hay cài đặt chia sẻ. Khi hủy yêu cầu, backend tính lại quyền dựa trên trạng thái hiện tại.

## 10. Phát sinh

- Cập nhật QD-35 và backlog sau khi duyệt quy trình 30 ngày. Cần chốt đầu việc đăng nhập, worker và UI để nghiệm thu cả luồng trước khi bật tính năng.
- Schema khai báo ID yêu cầu `bigint`, trong khi model/worker hiện dùng UUID. Cần đối chiếu ở giai đoạn contract và plan trước khi chọn kiểu ID công khai và cách bàn giao cho worker.

## 11. Size

- `size: L`. Có API contract mới, thay đổi kiểm soát quyền và dự kiến migration cho vòng đời yêu cầu xóa.

Kiểm tra phạm vi bằng `python .agents/scripts/scope.py 5.03 --stage requirement`. Kết quả đạt, log tại `work/5.03/evidence/requirement-scope.log`.

## Bước tiếp theo

- Đang chờ: người duyệt xem bản yêu cầu.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve 5.03 requirement`. Giai đoạn tiếp theo là contract.
- Cập nhật lần cuối: 2026-11-11 09:55 +0700, Codex.
