---
task: adhoc-20261115-mobile-health-profile-onboarding
title: UI và dữ liệu onboarding hồ sơ sức khỏe S08b–S08e
type: feature
stage: requirement
size: L
contract_change: yes
affected: [frontend, backend, api_contract]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-15 17:17 +0700
content_hash: sha256:c60e413f4f65fe0d
---

# Onboarding hồ sơ sức khỏe S08b–S08e

## 1. Mục tiêu

Từ popup chào mừng, bệnh nhân vào S08a rồi khai báo dị ứng và bệnh nền theo Figma. Khi hoàn tất và mở lại hồ sơ, các lựa chọn phản ánh dữ liệu thực đã lưu trên backend.

## 2. Phạm vi

- Dùng CTA **Tiếp tục đến dị ứng** ở S08a để mở S08b. Nối S08b → S08c → S08e và **Vào ứng dụng** về Trang chủ. Giữ đường vào qua popup và ConsentGate của app.
- Dựng hoặc refactor 13 trạng thái theo bảng dưới. Các lựa chọn mẫu là các trạng thái tương tác của cùng biểu mẫu từng bước. Hỗ trợ chọn/bỏ chọn nhiều mục, mục tự nhập, xác nhận không có đã biết, bỏ qua và quay lại.
- Dùng backend cho danh mục và dữ liệu hồ sơ. Bổ sung khả năng lưu dị ứng, mục tùy chỉnh và trạng thái xác nhận không có đã biết ở nơi contract hiện hành chưa hỗ trợ. Xử lý tải, lỗi và lưu lại qua màn hình.
- Ngoài phạm vi: chỉnh thiết kế Figma, thiết kế lại popup/S08a/Trang chủ hoặc màn chỉnh sửa hồ sơ tổng hợp, khôi phục S08d lưu trữ, tính năng gợi ý món ăn và quy tắc tương tác thuốc.

### Frame Figma · Prototype_DrugTime / Page 1

Các frame bên dưới có kích thước 375 × 812 trên canvas. Bước plan cần đối chiếu ảnh render, component, safe area, style và điểm đích prototype trước khi chốt hành vi chi tiết.

| Màn hoặc trạng thái | Node |
|---|---|
| S08b · Dị ứng thuốc & thực phẩm | 38:4966 |
| S08b1 · Đã chọn Penicillin và Hải sản | 547:9725 |
| S08b · Penicillin | 547:9283 |
| S08b · Hải sản | 547:9504 |
| S08b · Thêm dị ứng khác | 547:10167 |
| S08b · Không có dị ứng đã biết | 547:9946 |
| S08c · Bệnh mãn tính / bệnh nền | 38:5045 |
| S08c · Đã chọn Tăng huyết áp và Tiểu đường | 547:10839 |
| S08c · Đã chọn Tiểu đường | 547:10644 |
| S08c · Đã chọn Tăng huyết áp | 547:10449 |
| S08c · Thêm bệnh nền khác | 547:11229 |
| S08c · Không có bệnh nền đã biết | 547:11034 |
| S08e · Bệnh nền — Không có bệnh nền đã biết | 547:11556 |

## 3. Bối cảnh & nguồn đã đọc

| Nguồn | Hiện trạng |
|---|---|
| [Prototype_DrugTime · S08b](https://www.figma.com/design/aBPUpNPZIXqE44D1Gx8gaJ/Prototype_DrugTime?node-id=38-4966) | Reqwise xác minh tên, node và kích thước đủ 13 frame. Đã đọc cây layer và nội dung của S08b/S08c mặc định, hai frame tự nhập và S08e. S08e ghi “Đã lưu hồ sơ sức khỏe” và có nút “Vào ứng dụng”. Chưa kiểm ảnh render và liên kết prototype của từng frame. |
| `work/adhoc-20261115-mobile-health-profile-intro/01-requirement.md` và checkout S08a trong `scratch/checkout` của task đó | S08a có route `/onboarding/health-profile`. CTA đang dùng phản hồi tạm vì chưa có bước Dị ứng. Baseline triển khai phải có cả popup và S08a. |
| `frontend/mobile/lib/features/profile/` gồm `medical_profile_screen.dart`, `profile_controller.dart`, `profile_repository.dart` | Có màn chỉnh sửa hồ sơ y tế tổng hợp và luồng đọc danh mục, thêm/sửa/xóa liên kết bệnh nền. Chưa thấy biểu mẫu onboarding riêng trong luồng S08a. |
| `api_contract/openapi.json` mục `/profile`, `/conditions`, `/profile/conditions`, `/profile/conditions/{id}` | Đọc hồ sơ cá nhân, danh mục bệnh nền phân trang, thêm/sửa/xóa liên kết bệnh nền qua ID. Danh sách rỗng không mã hóa lý do. Contract chưa có dị ứng, tên bệnh nền tự nhập hoặc xác nhận rõ “không có đã biết”. |

### Quyết định nghiệp vụ áp dụng

Nguồn `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` tại checkout hiện tại.

- Mục 9, QD-33 đã chốt. Audit cả lượt được phép/lượt bị từ chối với metadata tối thiểu. Không ghi được audit bền vững thì chặn đọc và không xác nhận ghi. Áp dụng AC8–AC9.
- Mục 9, QD-31 và QD-32 đã chốt. Onboarding không tự tạo hoặc thay đổi đồng ý; admin không có quyền vượt consent để đọc dữ liệu sức khỏe. Áp dụng AC1, AC8.
- Mục 11, QD-40 đã chốt cho gợi ý món ăn. Nghiệp vụ phân biệt “không có” với thiếu/chưa biết, và chỉ yêu cầu thông tin khi dùng tính năng đó. Luồng này cho bỏ qua và không tự suy ra xác nhận “không có”. Áp dụng AC4, AC6. Tính năng gợi ý món ăn nằm ngoài phạm vi.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng | Lý do |
|---|---|---|
| frontend | Có | UI Flutter, điều hướng, tích hợp API và kiểm thử widget. |
| backend | Có | Dữ liệu còn thiếu, xử lý lưu/đọc, kiểm thử API và audit; dự kiến cần migration. |
| api_contract | Có | Bổ sung contract để lưu và đọc đầy đủ dữ liệu onboarding. |
| tests, docs, .agents | Không dự kiến | Widget test nằm ở frontend, test API và dữ liệu nằm ở backend. |

## 5. Thay đổi API contract

`contract_change: yes`. Đọc danh mục và liên kết bệnh nền từ `GET /conditions` và `GET /profile` theo contract hiện hành. Đối chiếu API ghi bệnh nền hiện có (`POST /profile/conditions`, `PATCH/DELETE /profile/conditions/{id}`). Giai đoạn contract xác định endpoint/schema cho dị ứng, giá trị tự nhập, trạng thái từng bước và hành vi lưu theo Q1. Dữ liệu cũ và các client của hồ sơ tổng hợp phải tiếp tục hoạt động.

## 6. Vùng rủi ro và bất biến bị chạm

- Dữ liệu sức khỏe: đọc/ghi riêng cho người dùng đang xác thực, qua PEP, kiểm consent mỗi request và ghi audit fail-closed. App chỉ gọi Backend API. Không đưa payload sức khỏe vào log.
- Schema: nếu bổ sung lưu trữ, kiểm migration trên DB sạch và đọc tương thích bản ghi cũ.
- Phần danh mục chung chỉ trả dữ liệu danh mục. Luồng onboarding cá nhân không mở quyền truy cập cho người thân hoặc admin.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given Trang chủ đủ điều kiện hiển thị popup, When chọn **Thiết lập hồ sơ sức khỏe** rồi **Tiếp tục đến dị ứng**, Then mở đúng một S08b qua S08a; back từ S08b về S08a và luồng không tự ghi consent. | Widget |
| AC2 | Given dữ liệu kiểm thử đủ tái hiện từng trạng thái frame, When xem tại 375 × 812, Then nội dung, bố cục, icon, typography, màu và trạng thái điều khiển khớp 13 frame. Màn hẹp/chữ lớn vẫn chạm và cuộn được. | Thủ công đối chiếu ảnh và widget |
| AC3 | Given danh mục đã tải, When chọn/bỏ Penicillin, Hải sản, Tăng huyết áp và Tiểu đường, Then màn phản ánh đúng lựa chọn đơn/kép và quay lại bước trước vẫn thấy bản nháp trong cùng phiên. | Widget |
| AC4 | Given trường tự nhập hoặc các mục đã chọn, When nhập giá trị trống hay chọn “không có … đã biết”, Then giá trị trắng không được lưu và xác nhận “không có” loại trừ lựa chọn cụ thể. Khi bỏ qua, dữ liệu đã lưu của bước đó được bảo toàn theo Q1. | Widget và tích hợp |
| AC5 | Given backend có danh mục và hồ sơ đã khai báo, When tải hoặc mở lại luồng, Then lựa chọn hiển thị theo dữ liệu backend, kể cả mục tự nhập đã lưu, và khôi phục trạng thái xác nhận không có nếu đã khai. | Tích hợp |
| AC6 | Given dị ứng đã nhập và bệnh nền đã chọn hoặc xác nhận “không có”, When hoàn tất với phản hồi lưu thành công, Then dữ liệu đọc lại khớp xác nhận, S08e hiện đúng một lần, **Vào ứng dụng** về Trang chủ. Bước bỏ qua không chuyển thành xác nhận “không có”. | Widget và tích hợp |
| AC7 | Given tải hoặc lưu lỗi, When backend trả lỗi hoặc mất mạng, Then app hiển thị trạng thái lỗi, giữ bản nháp để thử lại, không hiện S08e báo đã lưu và không tạo bản ghi trùng khi gửi lại sau phản hồi không chắc chắn. | Widget và tích hợp |
| AC8 | Given consent bị rút hoặc request cố truy cập chéo patient/admin không có quyền, When gọi endpoint sức khỏe, Then trả từ chối, không trả payload hoặc ghi dữ liệu và có dòng audit denied. Sau khi rút consent, request ngay sau đó bị từ chối. | Tích hợp API + DB |
| AC9 | Given ghi audit bền vững thất bại, When đọc hoặc ghi hồ sơ, Then không trả dữ liệu sức khỏe hoặc xác nhận lưu, và giao dịch ghi không để lại thay đổi một phần. | Tích hợp API + DB |
| AC10 | Given DB sạch và hồ sơ cũ chỉ có liên kết bệnh nền, When áp dụng migration và đọc lại hồ sơ, Then các liên kết cũ vẫn đọc được và thiếu dữ liệu khai báo không hiển thị thành “không có đã biết”. | Tích hợp API + DB |

## 8. Câu hỏi mở

Q1 [không chặn requirement] Nên lưu từng bước hay chỉ lưu một lần khi hoàn tất hai bước?

- Ảnh hưởng. Dữ liệu đã ghi khi người dùng thoát giữa luồng và thời điểm xác nhận thành công.
- Lựa chọn. Lưu các bước đã khai khi hoàn tất / lưu từng bước khi bấm Tiếp tục.
- Giả định mặc định. Giữ bản nháp khi chuyển bước, lưu các bước đã khai khi hoàn tất, giữ nguyên dữ liệu ở bước bỏ qua. Nếu bỏ qua cả hai bước và không có thay đổi cần lưu thì về Trang chủ. Nếu lưu thành công, dùng S08e làm màn xác nhận chung; giai đoạn plan đối chiếu đích các nhánh prototype.

## 9. Giả định

- Task mới ngoài backlog. Baseline gồm Trang chủ, popup và S08a của các task trước.
- Penicillin, Hải sản, Tăng huyết áp và Tiểu đường là dữ liệu dùng để tái hiện trạng thái Figma. Dữ liệu chạy thực tế lấy từ backend.

## 10. Phát sinh

- Cần xác nhận trạng thái tích hợp S08a vào nhánh làm việc trước khi triển khai. Bản S08a đã review hiện được ghi nhận trong checkout riêng của task trước.
- Chi tiết nguồn danh mục, ngữ nghĩa mục tự nhập và chuyển trạng thái từ hồ sơ cũ sẽ được chốt ở contract.
- `scope.py --stage requirement` trả exit 1 với 1.267 file ngoài phạm vi, cùng số lượng với kiểm tra requirement S08a trước đó. Lượt này chỉ ghi trong thư mục task. Output thô ở `evidence/requirement-scope.log`.

## 11. Size

`size: L`. Phạm vi gồm UI, backend, API contract, dữ liệu sức khỏe và thay đổi lưu trữ dự kiến.

## Bước tiếp theo

- Đang chờ duyệt requirement. Nếu đồng ý phạm vi và giả định Q1, chạy `python .agents/scripts/gate.py approve adhoc-20261115-mobile-health-profile-onboarding requirement`.
- Sau khi duyệt, làm giai đoạn contract.
- Cập nhật ngày 2026-11-15, Codex.

