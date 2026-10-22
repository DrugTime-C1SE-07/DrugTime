---
task: 3.24-adherence-family-view
title: Mobile - người thân xem lịch sử tuân thủ
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-22 16:22 +0700
content_hash: sha256:78a2784681c4911b
---

# 3.24-adherence-family-view · Mobile - người thân xem lịch sử tuân thủ

## 1. Mục tiêu

Người thân đã được bệnh nhân cho phép có thể xem lịch sử tuân thủ dùng thuốc cơ bản của đúng bệnh nhân được chọn trên ứng dụng Mobile. Màn hình thể hiện tiến độ và trạng thái từng liều dễ hiểu, đồng thời xóa dữ liệu sức khỏe đang hiển thị ngay khi quyền xem không còn hiệu lực.

## 2. Phạm vi

### Trong phạm vi

- Màn Mobile chỉ đọc, nhận `patient_id` của một bệnh nhân từ nơi gọi; lấy lịch sử qua `GET /adherence?patient_id=...` với khoảng ngày hợp lệ.
- Hiển thị khoảng ngày/ngày đang xem, tổng quan tuân thủ, nhóm liều theo ngày và trạng thái từng liều. Cho phép xem ngày khác trong khoảng dữ liệu API hỗ trợ; có trạng thái tải, không có dữ liệu, lỗi mạng và mất quyền.
- Giao diện theo Figma `Prototype_DrugTime`: lấy màn lịch sử ngày `S09a`, lịch tháng `S09b`, thẻ tiến độ và token từ `00 · Design Foundation` làm chuẩn; bổ sung ngữ cảnh bệnh nhân/người thân ở phần đầu. Màn này chỉ đọc, không có nút xác nhận hoặc sửa liều.
- Không giữ lịch sử bệnh nhân trên màn khi API trả 403, khi chuyển sang `patient_id` khác, hoặc khi người dùng rời rồi quay lại màn sau thay đổi quyền; lần xem mới phải kiểm lại qua API.
- Hỗ trợ màn hình nhỏ, vùng an toàn hệ điều hành, cỡ chữ hệ thống lớn và nhãn đọc màn hình cho ngày, tỷ lệ, trạng thái liều.

### Ngoài phạm vi

- Liệt kê/chuyển giữa nhiều bệnh nhân, API danh sách bệnh nhân và tích hợp nơi chọn bệnh nhân (PB22, task 5.13). Theo xác nhận của người dùng, màn 3.24 nhận `patient_id` từ nơi gọi.
- Cấp/thu hồi consent, tạo/hủy liên kết người thân, sửa lịch thuốc, ghi nhận liều, thông báo và hồ sơ y tế.
- Đổi cách tính tuân thủ, đổi response hoặc phân quyền của backend; bộ test riêng toàn luồng người thân của task 3.25.
- Sao chép nguyên mẫu lịch của bệnh nhân với hành động xác nhận liều sang ngữ cảnh người thân.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx`, Product Backlog PB21/PB22 và Sprint 3 Backlog 3.23–3.25 | PB21 yêu cầu người thân xem lịch sử cơ bản của bệnh nhân đã liên kết và bị chặn sau khi rút consent. PB22 mới có bộ chọn nhiều bệnh nhân; 3.25 là task test riêng. |
| [Figma `Prototype_DrugTime`](https://www.figma.com/design/aBPUpNPZIXqE44D1Gx8gaJ/Prototype_DrugTime?node-id=0-1&p=f), Page 1, node `75:7848` (S09a), `75:8120` (S09b), `51:5751` (S08-3), đọc bằng Reqwise Figma | Bản vẽ có màn lịch sử ngày/tháng kích thước tham chiếu 375 × 812, thẻ tiến độ, nhóm liều, ký hiệu trạng thái và ngôn ngữ người thân. Chưa có frame riêng cho người thân xem lịch sử; cần ghép đúng ngữ cảnh mà không thêm hành động ghi liều. |
| Figma `Prototype_DrugTime`, `00 · Design Foundation`, đọc bằng Reqwise Figma | Token gốc: canvas `#fcfcfc`, surface `#ffffff`, ink `#211d1d`, muted `#5b6169`, primary `#01554f`, tint `#e7f3f1`, safe `#16a34a`, danger `#dc2626`; khoảng cách theo bội số 4/8 và bán kính 8/12/16/24. |
| Skill `ui-ux-pro-max:ui-ux-pro-max`, truy vấn design system và Flutter, `references/pro-rules.md` | Hướng dẫn phù hợp là giao diện chăm sóc sức khỏe dễ đọc, vùng chạm tối thiểu theo nền tảng, thông báo trạng thái bằng chữ và màu, Semantics, bố cục thích ứng, safe area. Gợi ý bảng màu/font tự sinh của skill không thay token Figma và theme đang có. |
| `api_contract/openapi.json`, `GET /adherence` và `Adherence*` schemas | API sẵn có nhận `patient_id`, `from`, `to`, `group_by`; trả `summary`, `groups`, `as_of`, timezone `Asia/Ho_Chi_Minh`. `adherence_rate` gồm cả uống trễ và là `null` nếu `counted=0`; trả 403 khi thiếu quyền, 401 khi hết phiên. Khoảng ngày tối đa 90 ngày. |
| `frontend/mobile/lib/app/app_shell.dart`, `main.dart`, `core/api/api_client.dart`, `app/theme/` và các feature hiện có | Flutter dùng cấu trúc `domain/data/presentation`, `ApiClient` chung, theme có token khớp Figma. Tab Người thân hiện là `ComingSoonView`; chưa có feature adherence hoặc API danh sách bệnh nhân liên kết. |
| `work/3.23-adherence-family-consent/01-requirement.md` và gate của task 3.23 | Backend/contract cho quyền người thân đã thuộc task 3.23; task này chỉ dùng contract đó và phải xử lý dữ liệu sức khỏe như thông tin nhạy cảm. |

Kiểm tra phạm vi đã chạy: `python .agents/scripts/scope.py 3.24-adherence-family-view --stage requirement` → OK. Output thô: `work/3.24-adherence-family-view/evidence/requirement-scope.log`.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Bổ sung màn Mobile và luồng đọc API theo cấu trúc Flutter hiện có. |
| `backend` | Không | Dùng `GET /adherence` đã có; không sửa quyết định quyền. |
| `api_contract` | Không | Query, response và lỗi cần dùng đều đã được công bố. |
| `tests` | Không | Test riêng toàn luồng người thân thuộc task 3.25; kiểm tra phù hợp trong `frontend/mobile/test` có thể thuộc task này nếu cần. |
| `docs` | Không | Không sửa tài liệu capstone. |

## 5. Thay đổi API contract

- `contract_change`: **no**.
- Lý do: client chỉ dùng hành vi, query, response và mã lỗi hiện có của `GET /adherence`; không đề xuất endpoint hoặc field mới.
- Endpoint liên quan (chỉ dùng): `GET /adherence?patient_id=<uuid>&from=<YYYY-MM-DD>&to=<YYYY-MM-DD>&group_by=date`.

## 6. Vùng rủi ro và bất biến bị chạm

- **Dữ liệu sức khỏe và phân quyền người thân**: UI chỉ gọi Backend API bằng phiên người dùng, không truy cập Supabase; không tự suy luận quyền từ JWT, không cache kết quả quyền. Mỗi lần vào/xem lại phải chấp nhận 403 từ server và bỏ dữ liệu cũ khỏi màn.
- **Bí mật**: không hiển thị lịch sử của bệnh nhân trước trong lúc tải bệnh nhân mới, không đưa tên thuốc/liều vào thông báo lỗi hoặc log client; không lưu lịch sử vào bộ nhớ offline dùng chung.
- **Múi giờ**: ngày và giờ hiển thị theo `Asia/Ho_Chi_Minh`; trạng thái `cho_xac_nhan` không được coi là bỏ lỡ hoặc đã uống.
- UI/UX: nhãn văn bản đi kèm màu trạng thái; các điều khiển đáp ứng vùng chạm, Semantics, safe area và cỡ chữ lớn.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given nơi gọi cung cấp `patient_id` hợp lệ và API trả 200 với các nhóm ngày, when mở màn, then màn hiển thị ngữ cảnh bệnh nhân, khoảng ngày, summary và các liều của đúng `patient_id`; không có hành động xác nhận/sửa liều. | unit (widget test) |
| AC2 | Given response có `da_uong`, `uong_tre`, `bo_lo`, `cho_xac_nhan`, when hiển thị, then mỗi trạng thái có nhãn dễ hiểu và dấu hiệu ngoài màu; giờ uống thực tế chỉ hiện khi `taken_at` có giá trị. | unit (widget test) |
| AC3 | Given `adherence_rate` có giá trị, when hiển thị tỷ lệ, then ghi rõ đây là tỷ lệ tuân thủ gồm uống đúng giờ và uống trễ, không gắn nhãn “đúng giờ”; given `adherence_rate=null`, then hiển thị trạng thái chưa đủ liều được tính thay vì `0%`. | unit (widget test) |
| AC4 | Given API trả 200 nhưng `groups=[]`, when tải xong, then hiện trạng thái không có lịch sử cho khoảng ngày được chọn và không dựng liều giả. | unit (widget test) |
| AC5 | Given người thân đang xem lịch sử, when API lần kế tiếp trả 403 sau khi bệnh nhân rút consent/tắt chia sẻ/hủy liên kết, then xóa toàn bộ lịch sử cũ và hiện thông báo không còn quyền xem; không thử lấy dữ liệu từ nguồn khác. | unit (widget test) |
| AC6 | Given đang xem bệnh nhân A, when nơi gọi đổi sang `patient_id` B, then không hiển thị dữ liệu A trong lúc tải B; request dùng `patient_id` B và chỉ hiển thị response B. | unit (widget test) |
| AC7 | Given API trả 401, 422 hoặc lỗi mạng/5xx, when tải lịch sử, then hiện lần lượt luồng hết phiên, khoảng ngày không hợp lệ hoặc lỗi có thể thử lại; không để dữ liệu sức khỏe cũ xuất hiện sau lỗi quyền hay đổi bệnh nhân. | unit (widget test) |
| AC8 | Given ngày được chọn và vùng thời gian Việt Nam, when đổi ngày/khoảng xem, then query hợp lệ, không có ngày kết thúc tương lai hoặc khoảng quá 90 ngày; ngày/giờ liều hiển thị theo `Asia/Ho_Chi_Minh`. | unit (widget test) |
| AC9 | Given thiết bị rộng 375dp hoặc nhỏ hơn và cỡ chữ hệ thống lớn, when cuộn/xem các thẻ liều, then không tràn ngang, không bị che bởi thanh điều hướng/vùng an toàn; các nút có nhãn đọc màn hình và vùng chạm tối thiểu theo nền tảng. | manual — cần quan sát trình đọc màn hình và bố cục thiết bị |
| AC10 | Given màn được đối chiếu với Figma S09a/S09b và token foundation, when kiểm tra trực quan, then màu, chữ, khoảng cách, thẻ tiến độ và trạng thái nhất quán với thiết kế gốc, với phần tiêu đề thể hiện đây là dữ liệu của bệnh nhân được chia sẻ. | manual — Figma chưa có frame riêng cho màn này |

## 8. Câu hỏi mở

Không có câu hỏi chặn. Người dùng đã xác nhận màn 3.24 nhận `patient_id` từ nơi gọi; việc lấy danh sách và chọn bệnh nhân thuộc task 5.13.

## 9. Giả định

- Màn dùng response `group_by=date` cho lịch sử cơ bản; cách nhóm theo thuốc không bắt buộc ở task này.
- Tên bệnh nhân chỉ hiển thị khi nơi gọi có dữ liệu tên đáng tin cậy; không suy đoán tên từ `patient_id` hoặc response adherence.
- `adherence_rate` là tỷ lệ `(taken + late) / counted` theo backend; không tự tính lại hoặc gọi là tỷ lệ đúng giờ.
- Figma chưa có màn người thân chuyên biệt; các frame S09a/S09b/S08-3 và token foundation là nguồn hình ảnh được xác minh.

## 10. Phát sinh

- `frontend` hiện ở detached HEAD `ea0e40cb`, khác con trỏ `8102c51a` trong superproject; trước giai đoạn implement phải xử lý theo `wf-git`, xác định đúng nhánh/base và bảo toàn thay đổi hiện có. Chưa sửa file submodule trong giai đoạn requirement.
- Contract hiện không có API liệt kê bệnh nhân liên kết. Người dùng xác nhận màn 3.24 chỉ nhận `patient_id`; khả năng điều hướng đầy đủ sẽ được nối ở task 5.13.

## 11. Size

- `size`: **M**.
- Lý do: chạm luồng đọc dữ liệu sức khỏe và thu hồi quyền người thân, đồng thời cần màn và lớp đọc API trong một submodule; không đủ điều kiện size S dù không đổi contract.

## Bước tiếp theo

- Đang chờ: người duyệt xem requirement.
- Việc cần làm: nếu đồng ý phạm vi và AC, chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view requirement` trong terminal người duyệt; sau đó mới sang giai đoạn plan. Trước implement cần xử lý detached HEAD của `frontend` theo `wf-git`.
- Cập nhật lần cuối: 2026-10-22 16:18 +0700, Codex.
