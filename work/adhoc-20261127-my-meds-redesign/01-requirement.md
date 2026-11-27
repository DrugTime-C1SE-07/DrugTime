---
task: adhoc-20261127-my-meds-redesign
title: Thiết kế lại UI màn S06 "Thuốc của tôi"
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-27 09:19 +0700
content_hash: sha256:9cd317fdd99ae70b
---

# adhoc-20261127-my-meds-redesign · Thiết kế lại UI màn S06 "Thuốc của tôi"

## 1. Mục tiêu

Màn "Thuốc của tôi" (S06) trên Mobile App hiển thị đúng thiết kế mới người dùng cung cấp (spec CSS xuất từ Figma, khung 375×812): header gọn với hai nút tròn, ô tìm kiếm, link tra cứu danh mục, danh sách thuốc chia nhóm "Đang dùng" / "Đã ngừng" bằng thẻ mới. Dữ liệu và hành vi (tìm kiếm, mở chi tiết, thêm thuốc, lịch sử tương tác, trạng thái lỗi/rỗng) giữ nguyên.

## 2. Phạm vi

### Trong phạm vi

- Nền màn: `#F5F7F6`.
- Header (cao 64): tiêu đề "Thuốc của tôi" 28/700 `#211D1D`; bên phải hai nút tròn 48×48:
  - "Lịch sử tương tác": nền `#FFF4E5`, icon khiên `#B4570F`.
  - "Thêm thuốc": nền `#E7F3F1` (`AppColors.brandPrimaryLight`), icon `+` `#01554F`. Thay cho nút `FilledButton "Thêm"` hiện tại.
- Ô tìm kiếm: cao 56, nền trắng, viền `#E4E4E1`, bo 8, icon search `#5B6169`, chữ 17, placeholder `#A6A6A6`. Giữ nút xoá khi có chữ.
- Link "Tra cứu danh mục thuốc ›": 14/600 `#01554F`, cao chạm 44. Link "Lịch sử tương tác" dạng chữ bị bỏ (đã có nút khiên ở header).
- Tiêu đề nhóm "Đang dùng · N", "Đã ngừng · N": 14/600 `#5B6169`.
- Thẻ thuốc (`MedicationCard`): nền trắng, không viền, bo 12, padding 16/12/16/16, gap 12; ô hình viên thuốc 48×48 (giữ `PillTile`/`PillAppearanceTile` hiện có); tên 17/600 `#211D1D`; dòng chi tiết 14/400 `#5B6169`; chevron `#A6A6A6`. Khoảng cách giữa thẻ 12.
- Thuốc sắp hết: chip trong thẻ, nền `#FEF3E2`, bo 8, cao 36, icon tam giác + chữ 14/600 `#92400E`.
- Thuốc đã ngừng: tên `#5B6169`, ô viên thuốc mờ (opacity 0.45).
- Cập nhật widget test bị ảnh hưởng.

### Ngoài phạm vi

- Status bar, home indicator, tab bar (NavBar): thuộc hệ thống / shell, không đổi trong task này.
- Logic dữ liệu, controller, API, entity `Medication`.
- Màn chi tiết thuốc, thêm thuốc, lịch sử tương tác.
- Font Inter: app đang dùng typography hiện có (`app_typography.dart`); không thêm font mới.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `frontend/mobile/lib/features/medication/presentation/screens/my_medications_screen.dart` | Màn S06 hiện có: `_Header` (IconButton lịch sử + `FilledButton "Thêm"`), `LowStockBanner`, `_SearchField`, `Wrap` hai link, `MedicationFilterBar` (Tất cả/Đang dùng/Đã ngừng), section "Đang dùng · N"/"Đã ngừng · N", `_LoadErrorCard`, empty-state. |
| `.../widgets/medication_card.dart` | Thẻ có viền, padding 16, tên/lịch/giờ uống (`_TimesRow`)/tồn kho (`_LowStockBadge`), chevron. |
| `.../widgets/medication_notices.dart` | `LowStockBanner`, `MedicationEmptyState`. |
| `.../widgets/medication_filter_bar.dart` | Hàng chip lọc; chỉ S06 dùng. |
| `frontend/mobile/lib/app/theme/app_colors.dart`, `app_theme.dart` | Đã có `brandPrimaryLight #E7F3F1`, `border #E4E4E1`, `inkMuted #5B6169`, `brand #01554F`, `cautionBg #FEF3E2`, `cautionText #92400E`. Chưa có `#F5F7F6`, `#FFF4E5`, `#B4570F`, `#A6A6A6`, `#E25555`. |
| `frontend/mobile/test/features/medication/medication_screens_test.dart` (group "S06", dòng 167–264, 610–640) | Test đang kiểm `MedicationFilterBar`, nút "Thêm" ở header (AC12–AC14), cảnh báo sắp hết, chip không rớt dòng ở 1.5x. |
| `frontend/mobile/test/features/medication/medication_filter_bar_test.dart`, `pill_appearance_display_test.dart` | Test riêng của filter bar và của `MedicationCard`. |

## 3a. Quyết định nghiệp vụ áp dụng

Không áp dụng: task chỉ đổi trình bày. Đã đối chiếu bất biến 1–7 và vùng rủi ro trong `AGENTS.md`; không chạm luồng dữ liệu, phân quyền hay ghi nhận liều.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | `frontend/mobile`: màn S06, thẻ thuốc, test. |
| `backend` | Không | Không đổi API. |
| `api_contract` | Không | Không đổi API. |
| `tests` | Không | Không có E2E cho màn này. |
| `docs` | Không | — |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: chỉ đổi giao diện; dữ liệu lấy từ `MedicationController` như cũ.
- Endpoint liên quan: chỉ dùng endpoint danh sách thuốc đang có (qua controller), không đổi.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng rủi ro nào. Nút "Lịch sử tương tác" chỉ điều hướng tới màn có sẵn.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given có thuốc đang dùng và đã ngừng, When mở S06, Then thấy tiêu đề "Thuốc của tôi", ô tìm kiếm, link "Tra cứu danh mục thuốc", nhóm "Đang dùng · N" và "Đã ngừng · M" với đúng số thẻ. | unit (widget) |
| AC2 | Given có thuốc, When chạm nút tròn "Thêm thuốc" ở header, Then mở màn thêm thuốc. Given empty-state đang hiện, Then nút "Thêm thuốc" ở header ẩn (giữ quy tắc AC12–AC14 cũ). | unit (widget) |
| AC3 | Given S06, When chạm nút khiên ở header, Then mở `AppRoutes.interactionHistory`; nút có nhãn đọc màn hình "Lịch sử kiểm tra tương tác". | unit (widget) |
| AC4 | Given thuốc đang dùng có `isLowStock`, When hiển thị thẻ, Then thẻ có chip "Sắp hết · …" màu caution; thuốc không sắp hết thì không có chip. | unit (widget) |
| AC5 | Given thuốc đã ngừng, When hiển thị thẻ, Then tên dùng màu `inkMuted` và ô viên thuốc có opacity 0.45. | unit (widget) |
| AC6 | Given gõ từ khoá không khớp, When tìm, Then hiện empty-state "Không tìm thấy …" như cũ; Given tải lỗi, Then hiện thẻ lỗi + "Thử lại" như cũ. | unit (widget) |
| AC7 | Given phóng chữ 1.5x trên màn 375 rộng, When mở S06, Then không có overflow (header, chip sắp hết, thẻ). | unit (widget) |
| AC8 | Given thiết bị thật/emulator, When mở S06, Then bố cục khớp spec (màu, kích thước, khoảng cách) theo mắt người duyệt. | manual — so sánh trực quan với Figma |

## 8. Câu hỏi mở

Q1 [không chặn] Bỏ hàng chip lọc "Tất cả / Đang dùng / Đã ngừng"?
- Ảnh hưởng: thiết kế mới không có hàng chip. Bỏ thì xoá luôn `medication_filter_bar.dart` và test của nó (chỉ S06 dùng).
- Lựa chọn: bỏ và xoá widget / giữ chip dưới link tra cứu.
- Giả định mặc định: bỏ, xoá widget + test.

Q2 [không chặn] Bỏ banner "N thuốc sắp hết" ở đầu danh sách?
- Ảnh hưởng: thiết kế chỉ có chip trong thẻ.
- Lựa chọn: bỏ banner (chỉ còn chip trong thẻ) / giữ cả hai.
- Giả định mặc định: bỏ banner trên S06; giữ class `LowStockBanner` nếu nơi khác còn dùng, không thì xoá.

Q3 [không chặn] Dòng giờ uống (icon đồng hồ + "08:00 · 20:00") trong thẻ?
- Ảnh hưởng: thiết kế chỉ có một dòng chi tiết dưới tên.
- Lựa chọn: bỏ dòng giờ, chi tiết = `scheduleSummary` / gộp giờ vào dòng chi tiết.
- Giả định mặc định: bỏ dòng giờ riêng; dòng chi tiết = `scheduleSummary` (đã ngừng: "Đã ngừng · kết thúc …"). Nhãn đọc màn hình vẫn đọc giờ uống.

Q4 [không chặn] Chấm đỏ (`#E25555`) trên nút khiên nghĩa là gì?
- Ảnh hưởng: app chưa có dữ liệu "có cảnh báo tương tác mới chưa xem"; muốn hiện đúng cần thêm logic/API (ngoài phạm vi).
- Lựa chọn: không hiện chấm / hiện khi có ít nhất một tương tác trong lịch sử (cần dữ liệu) / hiện cố định.
- Giả định mặc định: không hiện chấm trong task này; ghi vào "Phát sinh".

## 9. Giả định

- Spec dán trong chat là nguồn thiết kế; tên thuốc/số liệu trong spec là dữ liệu mẫu.
- Dùng màu có sẵn trong `AppColors`; màu chưa có (`#F5F7F6`, `#FFF4E5`, `#B4570F`, `#A6A6A6`) thêm thành hằng trong `app_colors.dart`.
- Tab bar dưới cùng do shell của app vẽ; padding đáy danh sách đủ để thẻ cuối không bị tab bar che (giữ như hiện tại).

## 10. Phát sinh

- Chấm đỏ trên nút lịch sử tương tác cần nguồn dữ liệu "chưa xem" (xem Q4). Không làm trong task này.

## 11. Size

- `size`: M
- Lý do: không chạm vùng rủi ro, `contract_change: no`, một submodule; nhưng sửa khoảng 4–6 file (màn, thẻ, notices, filter bar, màu, 2–3 file test) và vượt 50 dòng, nên không xếp S.

## Bước tiếp theo

- Đang chờ: người duyệt (và người dùng xác nhận/sửa giả định Q1–Q4 nếu khác).
- Việc cần làm: chạy `python .agents/scripts/gate.py approve adhoc-20261127-my-meds-redesign requirement`, sau đó agent làm giai đoạn plan (`wf-plan`).
- Cập nhật lần cuối: 2026-11-27, Claude Code
