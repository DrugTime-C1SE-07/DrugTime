---
task: adhoc-20261119-profile-s08-figma-align
stage: implement
owner: Ngọc Việt
started_at: 2026-11-19 23:35
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 23:48 +0700
content_hash: sha256:a0228f67e15f474b
inputs:
  01-requirement.md: sha256:ce32e0628d4d0c23
---

# adhoc-20261119-profile-s08-figma-align · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | Nhánh `feat/adhoc-20261119-profile-s08-figma-align` ở superproject, `frontend` (fast-forward `e3ccc31` → `221bbb9` = origin/main, chỉ thêm merge commit PR #84) và `docs` (từ origin/main `2b642c2`, cho file test case) | — |
| P2 | xong | `flutter test test/features/profile/profile_layout_test.dart --plain-name "S08"`: 10 test mới đỏ đúng lý do (màu avatar brandTint, w600, icon 20, màu `#275A92`, bóng xám, height 1.25, "?" thiếu weight) | `evidence/implement-red.log` |
| P3 | xong | `ProfileAvatar` thêm `ringed` (mặc định true); S08 dùng `ringed: false`. Test AC1, AC7 (4 biến thể), AC8 xanh | `evidence/implement-P3-P4.log` |
| P4 | xong | Tên 17/700, icon cài đặt 24, màu icon D5, bóng `_cardShadow`/`_menuShadow`, `_s08Title` 28/34, `_s08Caption` 14/20. Test AC2–AC6 xanh; `flutter analyze lib/features/profile test/features/profile`: No issues found | `evidence/implement-P3-P4.log`, `evidence/implement-analyze.log` |
| P5 | xong | Q1 = A: giữ dòng "Chia sẻ và liên kết". `flutter test test/features/family_link/patient_switcher_home_entry_test.dart`: 3/3 pass | `evidence/implement-P5.log` |
| P6 | xong | `flutter test` toàn bộ mobile: +1315 ~2 −92. Baseline (stash thay đổi): +1304 ~2 −92; tập test fail trùng khớp, không có fail mới | `evidence/implement-final-frontend.log`, `evidence/implement-baseline-frontend.log` |
| P7 | xong một phần | Ảnh test widget 375×812 có navbar: đúng bố cục và các điểm D2–D7; font trong môi trường test không phải Inter nên chưa so pixel được. So trên thiết bị: TC-S08-20 Pending | `evidence/implement-profile-shell.png` |

Truy vết quyết định nghiệp vụ: `01` mục 3a "Không áp dụng"; không có quy tắc nghiệp vụ nào bị đổi.

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/adhoc-20261119-profile-s08-figma-align` | `mobile/lib/features/profile/presentation/screens/profile_screen.dart` |
| frontend | `feat/adhoc-20261119-profile-s08-figma-align` | `mobile/lib/features/profile/presentation/widgets/profile_avatar.dart` |
| frontend | `feat/adhoc-20261119-profile-s08-figma-align` | `mobile/test/features/profile/profile_layout_test.dart` |
| docs | `feat/adhoc-20261119-profile-s08-figma-align` | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (do `testcase_xlsx.py merge`, vai trò `testcase-book`) |

Kết quả `python .agents/scripts/scope.py adhoc-20261119-profile-s08-figma-align --stage implement`: OK — log: `evidence/implement-scope.log` (chạy trước bước merge Excel; file test case thuộc vai trò `testcase-book`)

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `cd frontend/mobile && flutter test` | 1315 / 92 / 2 (baseline 1304 / 92 / 2, cùng tập fail) | `evidence/implement-final-frontend.log` |
| frontend | `flutter test test/features/profile/profile_layout_test.dart` | 23 pass / 2 fail (2 fail sẵn có ở baseline: "S08-1 field is 48 tall…", "unsupported Figma fields…") | `evidence/implement-P3-P4.log`, `evidence/implement-baseline-layout.log` |

## 3b. Bộ test case Excel (chỉ task size S)

- Spec: `work/adhoc-20261119-profile-s08-figma-align/testcases.json` (chức năng `S08`, sheet "Hồ sơ S08"; giữ nguyên TC-S08-01…10 của task trước, thêm TC-S08-11…21).
- File task: `work/adhoc-20261119-profile-s08-figma-align/testcases.xlsx`.
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (merge không có CẢNH BÁO).
- S08: 21 test case — Pass 16, Fail 2, Pending 3. Task này thêm 11: Pass 10, Pending 1.
- Pending cần người chạy: TC-S08-09, TC-S08-10 (từ task trước), TC-S08-20 (so ảnh màn Hồ sơ trên thiết bị với Figma S08).
- Bug: BUG từ TC-S08-07, TC-S08-08 (task trước, logout/401), không có bug mới.
- Log: `evidence/testcase-xlsx.log` (validate, build, merge đều exit 0).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Bóng và line-height đặt bằng hằng cục bộ trong `profile_screen.dart` (`_s08Title`, `_s08Caption`, `_cardShadow`, `_menuShadow`); token dùng chung `AppShadows.cardElevation`, `AppTextStyles.display/caption` không đổi vì màn khác đang dùng.
- `ProfileAvatar(ringed: false)` chỉ dùng ở S08; màn Thông tin cá nhân (72) giữ vòng tint (Q2 mặc định, AC8).
- Thêm `Key('profile-menu')` cho khung menu để test bóng.
- Màu shield `#01554F` vốn đã đúng (nhánh mặc định `AppColors.brand`).
- Chevron `h-chevron-right.svg` stroke `#A6A6A6`: đã khớp, không sửa.
- 92 test fail của toàn bộ mobile có sẵn trên `origin/main` (chủ yếu `medication_screens_test.dart`, `profile_app_lifecycle_test.dart`, 2 test S08-1/S08-2 ở `profile_layout_test.dart`); không thuộc task.

## 6. Phát sinh

- **Cỡ icon trong ô icon menu**: SVG `assets/icons/profile/h-user.svg` (và các icon menu khác) có kích thước gốc 18×18 và `_menu` không đặt slot, nên icon hiển thị 18 thay vì 24 như Figma (`icon/user` 24×24 tại left/top 8). Ngoài 7 điểm D1–D7 đã duyệt; không sửa. Người dùng quyết định bỏ qua (2026-11-20), không mở task riêng.
- `frontend` submodule được fast-forward lên origin/main (`221bbb9`) khi tạo nhánh; superproject cần bump con trỏ khi commit.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261119-profile-s08-figma-align implement`, rồi agent làm giai đoạn review (`wf-review`). Chưa commit, chưa push.
- Cập nhật lần cuối: 2026-11-20 00:10, Claude Code
