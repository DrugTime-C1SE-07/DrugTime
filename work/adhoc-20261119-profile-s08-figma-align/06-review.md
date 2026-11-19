---
task: adhoc-20261119-profile-s08-figma-align
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 23:52 +0700
content_hash: sha256:afa5da78995c2ca2
inputs:
  01-requirement.md: sha256:ce32e0628d4d0c23
  04-impl-notes.md: sha256:a0228f67e15f474b
---

# adhoc-20261119-profile-s08-figma-align · Review

## 1. Kết luận

Đạt, kèm lưu ý (0 Critical, 0 High, 0 Medium, 3 Low).

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| frontend | `git -C frontend diff` (thay đổi chưa commit trên nhánh `feat/adhoc-20261119-profile-s08-figma-align`, HEAD `221bbb9` = origin/main); bản lưu: `scratch/lib.diff`, `scratch/test.diff` |
| docs | `git -C docs status --short`: chỉ `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (file nhị phân, kiểm bằng `testcase_xlsx.py validate`) |

Kết quả `scope.py --stage implement`: `OK: mọi thay đổi nằm trong phạm vi.`

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC10 có code và test widget tương ứng: avatar đặc 56 + chữ 17/700 (`profile_avatar.dart:35-50`, `profile_screen.dart:394`); tên 17/700 (`profile_screen.dart:399-401`); icon cài đặt 24 (`profile_screen.dart:137-139`); màu icon menu (`profile_screen.dart:262-268`); bóng thẻ/menu (`profile_screen.dart:174-179`, `379`, hằng `326-361`); tiêu đề 28/34 và phụ đề 14/20 (`_s08Title`, `_s08Caption`); avatar không tên "?" ở 320/375 × scale 1.0/2.0; màn Thông tin cá nhân giữ vòng tint. AC11 (so trên thiết bị) là `manual`, còn Pending (L3) |
| Phạm vi | `scope.py` OK; 3 file frontend + file test case tổng, đúng bảng "File sẽ thay đổi" của `01`. Lệch cỡ icon menu 18/24 đã ghi "Phát sinh" và người dùng quyết định bỏ qua (L2) |
| Contract | Không áp dụng (`contract_change: no`, chỉ UI) |
| Bất biến kiến trúc | Không chạm: không gọi API mới, không truy cập Supabase, không đụng dữ liệu sức khỏe hay phân quyền |
| Bảo mật | Không có secret, log hay dữ liệu nhạy cảm mới trong diff |
| Xử lý lỗi | Không có đường lỗi mới; nhánh `c.avatar == null` giữ nguyên |
| Hiệu năng | Không đáng kể; một `TextStyle.copyWith` mỗi lần build (L1) |
| Chất lượng test | 15 test widget mới (kể cả 4 biến thể "?") khẳng định giá trị cụ thể (kích thước, màu, weight, height, bóng); có test hồi quy cho màn khác dùng `ProfileAvatar` (vòng tint 60). Không `skip`, `print`, `TODO` trong diff |
| Dễ đọc và nhất quán | Hằng cục bộ đặt cạnh `_profileHeading` theo pattern sẵn có; `ringed` mặc định `true` nên nơi gọi cũ không đổi hành vi. Comment tiếng Việt trong code (`profile_screen.dart:326`, `profile_avatar.dart:9`) theo thói quen file hiện có |
| Đối chiếu 04/05 với log trong `evidence/` | Khớp: `implement-final-frontend.log` `+1315 ~2 -92`, `implement-baseline-frontend.log` `+1304 ~2 -92` như bảng mục 3 của `04`. `testcase_xlsx.py validate`: S08 21 test case, Pass 16, Fail 2, Pending 3, khớp mục 3b. 92 fail có sẵn trên origin/main, không thuộc task |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Low | `frontend/mobile/lib/features/profile/presentation/screens/profile_screen.dart:399-401` | Style tên dùng `_profileHeading.copyWith(fontWeight: FontWeight.w700)`, tạo object mới mỗi lần build và lệch kiểu với các hằng `_s08*` bên cạnh | Tách hằng `const _profileName = TextStyle(...)`; có thể để task sau |
| Low | `profile_screen.dart` `_menu` (icon trong ô 40) | Icon menu hiển thị 18×18 theo kích thước gốc SVG, Figma là 24×24 | Người dùng đã quyết định bỏ qua (04 mục 6); không làm gì trong task này |
| Low | AC11 / TC-S08-20 | So ảnh màn Hồ sơ trên thiết bị với Figma S08 chưa chạy (môi trường test không dùng font Inter) | Người review PR chạy tay theo mục 5 rồi cập nhật TC-S08-20 trong file test case tổng |

## 5. Mô tả PR

Thứ tự merge (theo `wf-git`): 1) `frontend`, 2) `docs`, 3) superproject (bump con trỏ tới commit đã merge của hai submodule). Hiện chưa commit, chưa push.

### PR 1 · frontend

**Tiêu đề**: `feat(mobile): align profile screen S08 with Figma`

- Task: `adhoc-20261119-profile-s08-figma-align` (size S).
- Tóm tắt: màn Hồ sơ khớp Figma S08: avatar thẻ là hình tròn brand đặc 56 với chữ 17/700 (`ProfileAvatar(ringed: false)`); tên 17/700; icon cài đặt 24; màu nét icon menu theo Figma; bóng riêng cho thẻ và khung menu; tiêu đề 28/34, phụ đề 14/20. Token dùng chung (`AppShadows.cardElevation`, `AppTextStyles.display/caption`) không đổi.
- AC và test: `mobile/test/features/profile/profile_layout_test.dart`, nhóm "Figma metrics" (15 test mới). `flutter test`: 1315 pass / 92 fail / 2 skip; baseline origin/main 1304 / 92 / 2, cùng tập fail.
- Test tay (AC11): chạy app trên thiết bị 375×812, mở tab Hồ sơ, so với frame Figma S08: avatar đặc, bóng nhẹ của thẻ và menu, cỡ chữ tiêu đề/phụ đề. Màn "Thông tin cá nhân" vẫn có vòng tint quanh avatar 72.
- Rủi ro: thấp, chỉ UI. `ProfileAvatar.ringed` mặc định `true` nên nơi gọi khác không đổi. Icon menu vẫn 18 (lệch Figma đã được chấp nhận).
- Liên quan: PR docs (Test_Cases.xlsx), PR superproject (bump con trỏ).

### PR 2 · docs

**Tiêu đề**: `docs(testing): add S08 Figma alignment test cases`

- Task: `adhoc-20261119-profile-s08-figma-align`.
- Tóm tắt: sheet "Hồ sơ S08" trong `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` thêm TC-S08-11…21 (Pass 10, Pending 1: TC-S08-20 so trên thiết bị). Sinh bằng `testcase_xlsx.py merge`, không có cảnh báo.
- Rủi ro: không có. Sau khi chạy tay TC-S08-20, cập nhật trạng thái trong file này.
- Liên quan: PR frontend; merge sau PR frontend.

### PR 3 · superproject

**Tiêu đề**: `chore: bump frontend and docs for adhoc-20261119-profile-s08-figma-align`

- Task: `adhoc-20261119-profile-s08-figma-align`.
- Tóm tắt: bump `frontend` tới commit đã merge của PR 1 (bao gồm fast-forward từ `e3ccc31` lên `221bbb9` = origin/main lúc tạo nhánh) và `docs` tới commit đã merge của PR 2; thêm artifact `work/adhoc-20261119-profile-s08-figma-align/` (01, 04, 06, testcases, evidence).
- Rủi ro: không bump tới commit chưa push; merge sau cùng.

## 6. Ghi chú cho quy trình

- Review chạy trong cùng phiên và cùng tool với implement, không độc lập như `wf-review` khuyến nghị; người review PR nên tự xem diff.
- Bộ test toàn mobile có 92 fail sẵn trên origin/main; nên có task riêng sửa để kết quả test của task sau có ý nghĩa hơn.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261119-profile-s08-figma-align review`; sau đó (khi người dùng yêu cầu) commit/push và mở PR theo mục 5.
- Cập nhật lần cuối: 2026-11-20 00:30, Claude Code
