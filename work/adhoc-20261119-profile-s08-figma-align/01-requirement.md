---
task: adhoc-20261119-profile-s08-figma-align
title: Căn màn Hồ sơ (S08) khớp lại Figma
type: feature
stage: requirement
size: S
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 23:30 +0700
content_hash: sha256:ce32e0628d4d0c23
---

# adhoc-20261119-profile-s08-figma-align · Căn màn Hồ sơ (S08) khớp lại Figma

## 1. Mục tiêu

Màn Hồ sơ của mobile app hiển thị đúng thông số Figma S08 (bản CSS người dùng dán ngày 2026-11-19) ở các điểm còn lệch sau task `adhoc-20261118-mobile-profile-s08-ui` và các task gộp sau đó: avatar, độ đậm tên, cỡ icon cài đặt, màu nét icon menu, bóng đổ, line-height, và số dòng menu.

## 2. Phạm vi

### Trong phạm vi

Đối chiếu Figma S08 với `frontend/mobile/lib/features/profile/presentation/screens/profile_screen.dart` (main `f990689`, frontend `e3ccc31`):

| # | Điểm | Figma S08 | Code hiện tại |
|---|---|---|---|
| D1 | Số dòng menu | 6 dòng (user, heart, users, bell, shield, circle-help), khung cao 437 | 7 dòng: thêm "Chia sẻ và liên kết" (icon `h-users`) giữa "Người giám sát" và "Thông báo & Nhắc nhở" |
| D2 | Avatar thẻ hồ sơ | Hình tròn `#01554F` đặc 56, chữ viết tắt Inter 17/700 `#FFFFFF`, line-height 26 | `ProfileAvatar(size: 56)`: vòng `brandTint` 6, lõi 44, chữ `(56-12)/3` ≈ 14.7, weight 400 |
| D3 | Tên trong thẻ | 17/700, line-height 24, `#211D1D` | 17/600 (`_profileHeading`) |
| D4 | Icon cài đặt ở header | 24×24, nét `#01554F` | 20×20 |
| D5 | Màu nét icon menu | user `#20568F`, heart `#A12E50`, users `#624394`, bell `#8A4E0B`, shield `#01554F`, help `#256749` | `#275A92`, `#B51F4A`, `#604497`, `#874607`, brand, `#21684D` |
| D6 | Bóng đổ | Thẻ: `0 1 3 rgba(1,85,79,.0392)`, `0 4 12 rgba(1,85,79,.0784)`. Nhóm menu: `0 1 3 rgba(33,54,49,.0314)`, `0 3 12 rgba(33,54,49,.051)` | Cả hai dùng `AppShadows.cardElevation` (xám `rgb(28,32,36)`, spread -2) |
| D7 | Line-height | Tiêu đề "Hồ sơ" 28/34; phụ đề (số điện thoại, phụ đề menu) 14/20 | `AppTextStyles.display` height 1.25 (35); `caption` height 1.4 (19.6) |

### Ngoài phạm vi

- Thanh điều hướng dưới (`app_shell.dart`): đã khớp Figma (351×68, bo 24, bóng brand, tab chọn `#D9EEFC`/`#0B5A8A`).
- Sửa token dùng chung `AppShadows.cardElevation`, `AppTextStyles.display`, `AppTextStyles.caption`: màn khác đang dùng; chỉ đổi giá trị cục bộ ở màn S08.
- Avatar ở màn Thông tin cá nhân (`personal_profile_screen.dart`, `ProfileAvatar(size: 72)`): giữ nguyên vòng tint.
- Nội dung chữ các dòng menu: bản spec dán vào không có text, giữ nguyên.
- Màu chevron `#A6A6A6` trong SVG `h-chevron-right`: chưa xác minh, chỉ sửa nếu kiểm ở implement thấy lệch (ghi vào "Phát sinh").
- Status bar và home indicator: do hệ điều hành vẽ.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `frontend/mobile/lib/features/profile/presentation/screens/profile_screen.dart` | Cấu trúc S08: header, `_ProfileCard`, 7 dòng `_menu`, `_profileHeading` 17/600 dùng chung cho tên và tiêu đề menu; bảng màu icon ở `_menu` |
| `frontend/mobile/lib/features/profile/presentation/widgets/profile_avatar.dart` | Avatar có vòng `brandTint` padding 6, chữ `(size-12)/3`, không đặt weight; dùng ở `profile_screen` (56) và `personal_profile_screen` (72) |
| `frontend/mobile/lib/app/theme/app_theme.dart` | `AppShadows.cardElevation` dùng thêm ở `link_request_result_screen.dart`, `shared/widgets/profile_flow_widgets.dart`; `display` 28/700 h1.25; `caption` 14/400 h1.4 `#5B6169`; `brandTint`, `brand`, `dividerSoft` khớp Figma |
| `frontend/mobile/lib/app/theme/app_typography.dart` | Font family `Inter` |
| `frontend/mobile/lib/app/app_shell.dart` | Navbar đã khớp Figma |
| `frontend/mobile/lib/app/router.dart`, grep `shareAndLink` | Dòng "Chia sẻ và liên kết" là lối vào duy nhất tới `AppRoutes.shareAndLink` |
| `frontend/mobile/test/features/family_link/patient_switcher_home_entry_test.dart:32` | Test của task 5.14 bấm `share-and-link-tile` |
| `frontend/mobile/test/features/profile/profile_layout_test.dart:231` | Test S08 hiện có: thẻ 88, dòng menu ≥ 72, ô icon 40, divider soft |
| `work/adhoc-20261118-mobile-profile-s08-ui/01-requirement.md`, `03-plan.md` | Task trước đặt mục tiêu "nhóm sáu mục điều hướng"; dòng thứ bảy được thêm sau bởi task 5.14 |

## 3a. Quyết định nghiệp vụ áp dụng

Không áp dụng. Task chỉ đổi trình bày (màu, cỡ, bóng, line-height) của màn S08; không đổi dữ liệu, quyền hay luồng nghiệp vụ. Đã đối chiếu: phạm vi task trước `adhoc-20261118-mobile-profile-s08-ui` (thiết kế S08). Riêng D1 có thể ảnh hưởng luồng "Chia sẻ và liên kết" (task 5.14), xem Q1.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Có | `frontend/mobile`: màn Hồ sơ, widget avatar, test layout |
| backend | Không | Không đổi API |
| api_contract | Không | Không đổi API |
| tests | Không | Không có E2E cho màn này |
| docs | Không | Không đổi tài liệu chính thức |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: chỉ đổi giao diện client; dữ liệu vẫn lấy qua `ProfileScope` sẵn có.
- Endpoint liên quan: chỉ dùng endpoint hồ sơ hiện có (qua `ProfileController.load`), không đổi.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng rủi ro nào. Màn đọc dữ liệu hồ sơ qua controller sẵn có; không thêm lời gọi API, không đổi phân quyền hay ghi nhận liều.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given hồ sơ có `fullName` "Nguyễn Văn An", When mở S08, Then avatar thẻ là hình tròn 56×56 màu `#01554F` không có vòng tint, chữ "VA" cỡ 17, weight 700, màu trắng | unit (widget test) |
| AC2 | Given mở S08, When đọc style tên trong thẻ, Then 17/700, height 24/17, màu `#211D1D`; tiêu đề dòng menu vẫn 17/600 | unit (widget test) |
| AC3 | Given mở S08, When đo icon cài đặt trong nút header, Then icon 24×24, nút vẫn 48×48 nền `#E7F3F1` | unit (widget test) |
| AC4 | Given mở S08, When đọc màu icon từng dòng menu, Then user `#20568F`, heart `#A12E50`, users `#624394`, bell `#8A4E0B`, shield `#01554F`, help `#256749` | unit (widget test) |
| AC5 | Given mở S08, When đọc `BoxDecoration` của thẻ và nhóm menu, Then bóng đúng hai lớp Figma ở D6 cho từng khối | unit (widget test) |
| AC6 | Given mở S08, When đọc style, Then tiêu đề "Hồ sơ" 28/700 height 34/28; số điện thoại và phụ đề menu 14/400 height 20/14 `#5B6169` | unit (widget test) |
| AC7 | Given hồ sơ không có tên (`fullName` null), When mở S08, Then avatar vẫn hiện "?" theo kiểu D2 và không lỗi layout ở 320 và 375 rộng, text scale 1.0 và 2.0 | unit (widget test) |
| AC8 | Given mở màn Thông tin cá nhân, When nhìn avatar 72, Then vẫn có vòng tint như trước (không bị D2 ảnh hưởng) | unit (widget test) |
| AC9 | Theo Q1 (mặc định giữ dòng): Given mở S08, When bấm `share-and-link-tile`, Then mở `AppRoutes.shareAndLink`; test 5.14 `patient_switcher_home_entry_test.dart` vẫn pass | unit (widget test) |
| AC10 | Given đã sửa xong, When chạy `cd frontend/mobile && flutter test`, Then toàn bộ test pass, không test cũ nào phải xóa | unit |
| AC11 | Given app chạy trên máy/emulator 375 rộng, When mở tab Hồ sơ, Then ảnh chụp so với Figma S08 không lệch thấy được ở D2–D7 | manual (cần so mắt với Figma) |

## 8. Câu hỏi mở

Q1 [không chặn] Dòng "Chia sẻ và liên kết" (D1) xử lý thế nào?
- Ảnh hưởng: xóa dòng thì màn `shareAndLink` không còn lối vào nào và test 5.14 phải đổi; giữ dòng thì nhóm menu cao 509 thay vì 437 như Figma.
- Lựa chọn: A. Giữ dòng, coi Figma S08 chưa cập nhật tính năng 5.14 / B. Xóa dòng và chuyển lối vào sang chỗ khác (cần thêm thiết kế, ngoài phạm vi) / C. Xóa dòng, chấp nhận mất lối vào.
- Giả định mặc định: A.

Q2 [không chặn] Avatar màn Thông tin cá nhân (72) có cần bỏ vòng tint giống S08 không?
- Ảnh hưởng: có thì AC8 đảo lại và phải đối chiếu thêm Figma màn đó.
- Lựa chọn: giữ vòng / bỏ vòng.
- Giả định mặc định: giữ vòng (chỉ S08 trong phạm vi).

## 9. Giả định

- Bản CSS Figma người dùng dán ngày 2026-11-19 là nguồn đúng cho S08.
- Màu shield `#01554F` trùng `AppColors.brand`, hiện đã đúng; chỉ kiểm lại bằng test (AC4).
- Đổi line-height và bóng chỉ cục bộ ở S08 bằng style/hằng riêng, không đổi token dùng chung.

## 10. Phát sinh

- Hook `.agents` doctor báo 10 skill `speckit-*` có frontmatter ngoài danh sách cho phép (trước khi người dùng `git clean`); không liên quan task.

## 11. Size

- `size`: S
- Lý do: không chạm vùng rủi ro, `contract_change: no`, 1 submodule, 3 file (2 code + 1 test), ước tính khoảng 50 dòng.

## 12. File sẽ thay đổi (chỉ task S)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `frontend/mobile/lib/features/profile/presentation/screens/profile_screen.dart` | sửa | D3–D7 (và D1 nếu Q1 ≠ A) |
| frontend | `frontend/mobile/lib/features/profile/presentation/widgets/profile_avatar.dart` | sửa | D2: tham số tắt vòng tint, chữ 17/700 cho S08 |
| frontend | `frontend/mobile/test/features/profile/profile_layout_test.dart` | sửa | Test AC1–AC8 |

## 13. Checklist (chỉ task S)

- [ ] P1 [frontend] Tạo nhánh `feat/adhoc-20261119-profile-s08-figma-align` ở superproject và `frontend` theo `wf-git` — file: không — AC: — — xong khi: `git -C frontend branch --show-current` ra đúng tên
- [ ] P2 [frontend] Viết test AC1–AC8 trước, chạy thấy đỏ — file: `frontend/mobile/test/features/profile/profile_layout_test.dart` — AC: AC1–AC8 — xong khi: log đỏ lưu `evidence/implement-red.log`
- [ ] P3 [frontend] `ProfileAvatar` thêm tùy chọn không vòng, chữ 17/700; S08 dùng tùy chọn đó — file: `profile_avatar.dart`, `profile_screen.dart` — AC: AC1, AC7, AC8 — xong khi: test AC1, AC7, AC8 xanh
- [ ] P4 [frontend] Tên 17/700; icon cài đặt 24; màu icon D5; bóng D6; line-height D7 — file: `profile_screen.dart` — AC: AC2–AC6 — xong khi: test AC2–AC6 xanh
- [ ] P5 [frontend] Xử lý D1 theo Q1 — file: `profile_screen.dart` — AC: AC9 — xong khi: test 5.14 pass
- [ ] P6 [frontend] Chạy `flutter test` và `flutter analyze` toàn bộ mobile — file: không — AC: AC10 — xong khi: log `evidence/implement-flutter-test.log` pass
- [ ] P7 [frontend] Chụp màn 375×812 (golden capture `PROFILE_CAPTURE_DIR` hoặc emulator) so Figma — file: không — AC: AC11 — xong khi: ảnh lưu `evidence/` và ghi nhận xét trong `04-impl-notes.md`

## Bước tiếp theo

- Đang chờ: người dùng xác nhận Q1, Q2 (hoặc chấp nhận giả định mặc định) và người duyệt.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261119-profile-s08-figma-align requirement`, sau đó agent làm giai đoạn implement từ P1.
- Cập nhật lần cuối: 2026-11-19 23:27, Claude Code
