---
task: adhoc-20261127-my-meds-redesign
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-27 09:21 +0700
content_hash: sha256:42cf2a0c69c802c9
inputs:
  01-requirement.md: sha256:9cd317fdd99ae70b
---

# adhoc-20261127-my-meds-redesign · Plan

## 1. Giải pháp

Chỉ đổi lớp trình bày của `frontend/mobile`, không đổi controller, entity hay repository. Q1–Q4 theo giả định mặc định trong `01` (người dùng đã xác nhận).

- **Màu**: thêm 4 hằng vào `AppColors` trong `app_theme.dart` (class mà màn S06 đang import): `canvasCool #F5F7F6`, `historyTint #FFF4E5`, `historyIcon #B4570F`, `inkFaint #A6A6A6`. Màu còn lại đã có: `brandTint`, `border`, `inkMuted`, `ink`, `brand`, `cautionBg`, `cautionText`. Không dùng `app_colors.dart` (class trùng tên khác, màn S06 không import).
- **`my_medications_screen.dart`**:
  - `Scaffold(backgroundColor: AppColors.canvasCool)`.
  - `_Header`: tiêu đề `AppTextStyles.display` (28/700). Bên phải hai nút tròn 48×48 dùng chung một widget `_RoundAction` (`Material` hình tròn + `InkWell` + `Tooltip`/`Semantics`): nút khiên (`Icons.shield_outlined`, nền `historyTint`, icon `historyIcon`, tooltip "Lịch sử kiểm tra tương tác", giữ key `medication-interaction-history-icon-button`) và nút thêm (`Icons.add`, nền `brandTint`, icon `brand`, tooltip "Thêm thuốc", key mới `medication-add-button`). Nút thêm vẫn ẩn khi empty-state hiện (`showAdd` như cũ). Không có chấm đỏ (Q4).
  - Bỏ `LowStockBanner` và `MedicationFilterBar` khỏi màn; bỏ state `_filter`; luôn hiện cả hai nhóm (nhóm rỗng tự ẩn như `_section` hiện tại).
  - `_SearchField`: `InputDecoration` riêng: `filled` trắng, cao 56, viền `border` bo 8 (focus vẫn viền `brand` theo theme), hint màu `inkFaint`, chữ 17. Giữ nút xoá.
  - Thay `Wrap` hai link bằng một link "Tra cứu danh mục thuốc" + `Icons.chevron_right` 16, chữ 14/600 `brand`, cao chạm 44, vẫn gọi `_showNotBuilt`. Bỏ link chữ "Lịch sử tương tác" (key `medication-interaction-history-button`).
  - Khoảng cách theo spec: header→search 8, search→link 8, link→nhóm 12, tiêu đề nhóm→thẻ 8, giữa thẻ 12, cuối nhóm→nhóm sau 16. Lề ngang 20.
- **`medication_card.dart`**:
  - `Material` trắng, không viền, bo 12; padding `fromLTRB(16,16,12,16)`; `Row(crossAxisAlignment: center)`, gap 12.
  - Tên 17/600 (`ink`, đã ngừng `inkMuted`); chi tiết 14/400 `inkMuted` (`scheduleSummary` hoặc "Đã ngừng · kết thúc …").
  - Bỏ `_TimesRow` (Q3); bỏ dòng tồn kho thường (chỉ giữ chip khi sắp hết, theo spec). Nhãn semantics giữ nguyên (vẫn đọc giờ uống, tồn kho).
  - `_LowStockBadge` → chip cao 36, bo 8, padding ngang 12, icon `Icons.warning_amber_rounded` 16, chữ 14/600 `cautionText`, cách dòng chi tiết 4.
  - Đã ngừng: tile không truyền `muted` mà bọc `Opacity(0.45)` (spec giữ màu viên thuốc, chỉ mờ đi).
  - Chevron 24 màu `inkFaint`.
- **Xoá code chết**: `medication_filter_bar.dart` (chỉ S06 dùng) + test của nó; `LowStockBanner` trong `medication_notices.dart` (không nơi nào khác dùng).

Cách khác đã bỏ: giữ `MedicationFilterBar` ẩn đi để dùng sau — YAGNI, người dùng đã đồng ý xoá (Q1).

## 1a. Quyết định nghiệp vụ áp dụng

Không áp dụng (như `01` mục 3a): chỉ đổi trình bày; đã đối chiếu bất biến 1–7 và bảng vùng rủi ro trong `AGENTS.md`.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `frontend/mobile/lib/features/medication/presentation/screens/my_medications_screen.dart` | Cấu trúc màn hiện tại (xem `01`). `_filter` chỉ dùng cho `MedicationFilterBar` và `_section`. |
| `.../widgets/medication_card.dart` | `PillTile`/`PillAppearanceTile` nhận `muted`; `_TimesRow`, `_LowStockBadge`, semantics label. |
| `.../widgets/medication_notices.dart` | `LowStockBanner` chỉ S06 dùng (grep `lib`, `test`). `MedicationEmptyState` giữ. |
| `.../widgets/medication_filter_bar.dart` | Chỉ S06 và `medication_filter_bar_test.dart` dùng. |
| `frontend/mobile/lib/app/theme/app_theme.dart` | `AppColors` (canvas, brandTint, cautionBg…), `AppTextStyles.display` 28/700, `AppRadius`, `AppSpacing`. |
| `frontend/mobile/lib/shared/widgets/pill_icon.dart`, `.../widgets/pill_appearance_icon.dart` | `muted` đổi nền sang xám; spec mới muốn giữ màu + opacity 0.45. |
| `frontend/mobile/test/features/medication/medication_screens_test.dart` | Group S06 (dòng 167–264) dùng `FilledButton 'Thêm'` cho nút header, `MedicationFilterBar`, banner "1 thuốc sắp hết", chip lọc; test 1.5x chip (dòng 610–625). |
| `frontend/mobile/test/features/medication/medication_filter_bar_test.dart` | Chỉ test widget sẽ xoá. |
| `frontend/mobile/test/features/medication/pill_appearance_display_test.dart` | Test `MedicationCard` theo key `medication-card-appearance` — giữ key. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/app/theme/app_theme.dart` | sửa | Thêm 4 hằng màu |
| frontend | `mobile/lib/features/medication/presentation/screens/my_medications_screen.dart` | sửa | Header, search, link, bỏ banner/filter, nền |
| frontend | `mobile/lib/features/medication/presentation/widgets/medication_card.dart` | sửa | Thẻ thuốc theo spec |
| frontend | `mobile/lib/features/medication/presentation/widgets/medication_notices.dart` | sửa | Xoá `LowStockBanner` |
| frontend | `mobile/lib/features/medication/presentation/widgets/medication_filter_bar.dart` | xóa | Code chết (Q1) |
| frontend | `mobile/test/features/medication/medication_filter_bar_test.dart` | xóa | Test của widget đã xoá |
| frontend | `mobile/test/features/medication/medication_screens_test.dart` | sửa | Cập nhật group S06 + test 1.5x |
| frontend | `mobile/test/features/medication/pill_appearance_display_test.dart` | sửa | Test thẻ: chip sắp hết, đã ngừng mờ |

## 4. Checklist

- [ ] P1 [frontend] Tạo nhánh `feat/adhoc-20261127-my-meds-redesign` ở `frontend` và superproject (theo `wf-git`) — file: — — AC: — — xong khi: `git branch --show-current` đúng tên ở cả hai.
- [ ] P2 [frontend] Thêm hằng `canvasCool`, `historyTint`, `historyIcon`, `inkFaint` — file: `mobile/lib/app/theme/app_theme.dart` — AC: AC8 — xong khi: `flutter analyze` file sạch.
- [ ] P3 [frontend] Viết lại `MedicationCard` (layout, chip 36, opacity 0.45, chevron, bỏ `_TimesRow`) — file: `mobile/lib/features/medication/presentation/widgets/medication_card.dart` — AC: AC4, AC5 — xong khi: test P6 phần thẻ pass.
- [ ] P4 [frontend] Viết lại header (`_RoundAction` x2), search, link tra cứu; bỏ banner, filter, `_filter`; nền `canvasCool` — file: `mobile/lib/features/medication/presentation/screens/my_medications_screen.dart` — AC: AC1, AC2, AC3, AC6 — xong khi: test P6 phần màn pass.
- [ ] P5 [frontend] Xoá `LowStockBanner`, `medication_filter_bar.dart`, `medication_filter_bar_test.dart` — file: `mobile/lib/features/medication/presentation/widgets/medication_notices.dart`, `.../medication_filter_bar.dart`, `mobile/test/features/medication/medication_filter_bar_test.dart` — AC: — — xong khi: `grep -r "MedicationFilterBar\|LowStockBanner" mobile/lib mobile/test` rỗng.
- [ ] P6 [frontend] Cập nhật test (bảng 5) — file: `mobile/test/features/medication/medication_screens_test.dart`, `mobile/test/features/medication/pill_appearance_display_test.dart` — AC: AC1–AC7 — xong khi: hai file test pass.
- [ ] P7 [frontend] Chạy `flutter analyze` + `flutter test --reporter failures-only` toàn suite, lưu log vào `work/adhoc-20261127-my-meds-redesign/evidence/` — AC: tất cả — xong khi: exit 0.
- [ ] P8 [frontend] Chụp màn S06 trên emulator/thiết bị để người duyệt so với spec — AC: AC8 — xong khi: ảnh trong `evidence/`.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `medication_screens_test`: "S06 hiện tiêu đề, tìm kiếm, link tra cứu, nhóm Đang dùng · 4 và Đã ngừng · 1" (thay test lọc cũ; kiểm không còn banner "1 thuốc sắp hết") | AC1 | frontend |
| AC11/AC12/AC13/AC14 cũ: đổi `headerAdd` sang `find.byKey(Key('medication-add-button'))`; AC11 bỏ dòng `MedicationFilterBar`; AC12 bỏ dòng `MedicationFilterBar`, thêm tap nút thêm → `AddMedicationScreen` | AC2 | frontend |
| "nút khiên mở lịch sử tương tác" — tap key `medication-interaction-history-icon-button` → màn `interactionHistory`; `find.byTooltip('Lịch sử kiểm tra tương tác')` | AC3 | frontend |
| `pill_appearance_display_test`: "thẻ sắp hết có chip Sắp hết · …; thẻ không sắp hết thì không" | AC4 | frontend |
| `pill_appearance_display_test`: "thẻ đã ngừng: tên màu inkMuted, tile bọc Opacity 0.45" | AC5 | frontend |
| "tìm theo hoạt chất và báo khi không có kết quả" (giữ), AC14 thẻ lỗi (giữ) | AC6 | frontend |
| Thay test "hàng chip S06 không rớt dòng 1.5x" bằng "S06 không overflow ở 1.5x, màn 375×812" (cuộn hết danh sách, `takeException` null) | AC7 | frontend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Không có | — | Không chạm API/DB; AC8 là manual. |

## 6. Migration

Không có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/adhoc-20261127-my-meds-redesign` |
| frontend | `feat/adhoc-20261127-my-meds-redesign` |

Hiện cả hai đang ở `feat/adhoc-20261125-biometric-auth`. Nhánh mới cắt từ `main` (mặc định) — xem Q1.

## 8. Rủi ro

- **Mất lối tắt lọc nhanh** khi danh sách dài: chấp nhận theo Q1; tìm kiếm vẫn có.
- **Mất banner tổng sắp hết**: người dùng phải thấy chip từng thẻ; chip nằm ngay trong nhóm "Đang dùng" nên vẫn dễ thấy.
- **Chữ 17 + chip 36 ở 1.5x** có thể tràn ngang 375: chip dùng `Flexible` + text wrap; AC7 bắt lỗi.
- **Opacity 0.45** làm tile thuốc đã ngừng tương phản thấp: chỉ là ảnh trang trí, tên/chi tiết vẫn giữ màu `inkMuted` đạt AA.
- Test khác ngoài thư mục medication tham chiếu banner/filter: grep ở P5 bắt.

## 9. Câu hỏi mở

Q1 [không chặn] Nhánh `feat/adhoc-20261127-my-meds-redesign` cắt từ đâu?
- Ảnh hưởng: cắt từ nhánh biometric thì PR kéo theo commit biometric chưa merge.
- Lựa chọn: `main` / `feat/adhoc-20261125-biometric-auth`.
- Giả định mặc định: `main` (task độc lập với biometric).

## 10. Phát sinh

- Chấm đỏ trên nút lịch sử tương tác (Q4 của `01`) — không làm.
- `scope.py` báo `AGENTS.md`, `.agents/core.md` ngoài phạm vi: hai file đã sửa từ trước task này (có trong `git status` đầu phiên), task không chạm. Cần người dùng commit/stash trước implement để scope sạch.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: chạy `python .agents/scripts/gate.py approve adhoc-20261127-my-meds-redesign plan`, rồi agent làm giai đoạn implement (`wf-implement`) từ P1.
- Cập nhật lần cuối: 2026-11-27, Claude Code
