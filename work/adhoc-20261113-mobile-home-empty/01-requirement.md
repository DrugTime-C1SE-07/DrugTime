---
task: adhoc-20261113-mobile-home-empty
title: Triển khai Trang chủ chưa có thuốc theo Figma
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-13 16:01 +0700
content_hash: sha256:b3edca5e56e36204
---

# S05-empty · Trang chủ (chưa có thuốc)

## Mục tiêu và phạm vi

Thay màn giữ chỗ ở tab Trang chủ bằng màn Flutter theo [S05-empty](https://www.figma.com/design/aBPUpNPZIXqE44D1Gx8gaJ/Prototype_DrugTime?node-id=31-3957). Dựng các thành phần Flutter có tương tác, gồm banner, lời chào, mascot, ba lối tắt **Thêm thuốc**, **Dumi AI**, **Người thân**, thẻ **Chưa có lịch uống thuốc** và thanh điều hướng nổi. Ảnh toàn màn chỉ dùng làm chuẩn đối chiếu.

- Dùng nguồn dữ liệu thuốc sẵn có. Chỉ hiện trạng thái trống khi đã tải thành công và xác định chưa có thuốc. Xử lý tải, lỗi và đã có thuốc riêng, không dựng các biến thể lịch dùng thuốc của S05 trong task này.
- **Thêm thuốc**, **Quét vỏ hộp**, **Người thân** và chuông thông báo dùng các điểm vào hiện có sau khi xác minh đích tương ứng. **Bắt đầu nào!** mở popup chào mừng đã nghiệm thu. Không thêm quy tắc tự mở popup hoặc lưu trạng thái đã xem.
- Phạm vi không gồm dựng các màn Dumi AI, S08a, thay đổi API hoặc làm lại các tab khác.

## Nguồn và đối chiếu

| Nguồn | Kết quả |
|---|---|
| Figma frame `31:3957`, Reqwise screenshot và cây layer | Viewport 375 × 812. Banner cao 236. Ba lối tắt trong khung 335 × 84 ở y224. Thẻ trống 335 × 380 ở y356. Navbar 343 × 58 ở y733. Figma có bốn tab, Trang chủ được tô đậm. |
| `frontend/mobile/lib/app/app_shell.dart` | Tab Trang chủ đang dùng `ComingSoonView`. App có năm tab, thêm Người thân. |
| `frontend/mobile/lib/app/router.dart` và `medication_controller.dart` | Có điểm vào thêm thuốc, capture, cảnh báo Người thân và dữ liệu thuốc. Cần xác minh đích khi lập plan. |
| Task `adhoc-20261113-mobile-welcome-popup` và `adhoc-20261113-mobile-foundation-assets` | Widget popup và assets đã duyệt nằm ở các checkout riêng, chưa merge. Plan phải xác định cách tái sử dụng. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 8, 9 và 11 | QD-28 và QD-31 bảo toàn quy tắc quyền chia sẻ và đồng ý. QD-40/41 giới hạn dữ liệu gợi ý món ăn. Task dùng luồng hiện có, không thay đổi quyền hoặc thêm xử lý dữ liệu. |

## Submodule, contract và rủi ro

`size: M`. Thay đổi frontend, gồm màn, kết nối app shell, tài nguyên và test. `contract_change: no`. Không thêm endpoint hoặc thay đổi quyền truy cập. Giữ cổng consent hiện có khi vào Trang chủ.

## Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Khi mở Trang chủ với fixture đã tải và chưa có thuốc ở 375 × 812, bố cục, mascot, icon, màu, typography, bóng và vị trí navbar khớp Figma. | Manual, ảnh Flutter và Figma |
| AC2 | Khi đang tải, tải thất bại hoặc đã có thuốc, màn không báo sai rằng chưa có thuốc. Khi trở về sau thêm thuốc, dùng trạng thái hiện tại. | Unit, widget |
| AC3 | Khi chạm lối tắt hoặc nút, dùng đúng luồng có sẵn. Bắt đầu nào mở popup, Để sau trả lại đúng Trang chủ. | Unit, widget |
| AC4 | Khi đổi tab hoặc mở Trang chủ lại, các tab và luồng Người thân vẫn truy cập được. Trên màn nhỏ hoặc chữ lớn, có thể cuộn tới các nút và navbar không che thao tác. | Unit, widget |

## Câu hỏi mở và giả định

- Figma có bốn mục ở navbar, Flutter có năm. Mặc định áp dụng navbar bốn mục ở S05-empty và giữ Người thân qua lối tắt có trên Figma. Các tab khác giữ điều hướng hiện tại. Plan xác nhận tác động đến cách chọn tab.
- Chưa thấy route Dumi AI trong router đã khảo sát. Cần kiểm tra điểm vào trước khi triển khai. Nếu chưa có, giữ đúng vị trí và hình thức lối tắt, nêu rõ giới hạn thao tác trong bàn giao.

## Phát sinh và bước tiếp theo

- Checkout chính chứa thay đổi chưa commit của task nhắc thuốc. Triển khai trong checkout riêng.
- Chờ duyệt requirement bằng `python .agents/scripts/gate.py approve adhoc-20261113-mobile-home-empty requirement`. Sau đó lập plan và xác minh tài nguyên, route và phương án tái sử dụng popup.
- Cập nhật lần cuối 2026-11-13, Codex.
