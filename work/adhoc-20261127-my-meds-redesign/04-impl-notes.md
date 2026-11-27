---
task: adhoc-20261127-my-meds-redesign
stage: implement
owner: Ngọc Việt
started_at: 2026-11-27 09:25
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-27 09:37 +0700
content_hash: sha256:c8bfe74d6380e84f
inputs:
  01-requirement.md: sha256:9cd317fdd99ae70b
  03-plan.md: sha256:42cf2a0c69c802c9
---

# adhoc-20261127-my-meds-redesign · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `git checkout -b feat/adhoc-20261127-my-meds-redesign origin/main` ở `frontend` và superproject | — |
| P2 | xong | Thêm `canvasCool`, `inkFaint`, `historyTint`, `historyIcon`; `flutter analyze lib/app/theme lib/features/medication test/features/medication` → chỉ 1 warning unused import (đã sửa ở P5) | `evidence/implement-P2-P5-analyze.log` |
| P3 | xong | `MedicationCard` mới; test AC4, AC5 trong `pill_appearance_display_test.dart` pass | `evidence/implement-P6.log` |
| P4 | xong | Header `_RoundAction` x2, `_SearchField` 56/bo 8, `_CatalogLink`, bỏ banner/filter/`_filter`, nền `canvasCool`, lề 20 | `evidence/implement-P6.log` |
| P5 | xong | Xoá `medication_filter_bar.dart`, test của nó, `LowStockBanner`; grep `MedicationFilterBar\|LowStockBanner` trong `lib`, `test` rỗng | — |
| P6 | xong | `flutter test --reporter failures-only test/features/medication/medication_screens_test.dart test/features/medication/pill_appearance_display_test.dart` → `+27 -1`; test fail duy nhất "chọn thuốc, đổi tần suất, lưu và thấy trong danh sách" cũng fail trên `main` sạch (stash) — `tap(find.text('Thuốc'))` tìm thấy nhiều widget | `evidence/implement-P6.log`, `evidence/implement-P6-baseline-main.log` |
| P7 | xong (có lỗi có sẵn) | `flutter analyze`: 13 issue, không issue nào trong file của task. `flutter test --reporter failures-only`: `+1780 ~2 -15` (xem mục 3) | `evidence/implement-final-analyze.log`, `evidence/implement-final-frontend.log` |
| P8 | chưa làm | Cần chạy app trên emulator/thiết bị để so trực quan với spec (AC8) | — |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/lib/app/theme/app_theme.dart` |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/lib/features/medication/presentation/screens/my_medications_screen.dart` |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/lib/features/medication/presentation/widgets/medication_card.dart` |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/lib/features/medication/presentation/widgets/medication_notices.dart` |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/lib/features/medication/presentation/widgets/medication_filter_bar.dart` (xoá) |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/test/features/medication/medication_filter_bar_test.dart` (xoá) |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/test/features/medication/medication_screens_test.dart` |
| frontend | `feat/adhoc-20261127-my-meds-redesign` | `mobile/test/features/medication/pill_appearance_display_test.dart` |

Kết quả `python .agents/scripts/scope.py adhoc-20261127-my-meds-redesign --stage implement`: 8 file `[OK]`; `[NGOÀI]` `.agents/core.md`, `AGENTS.md` — sửa từ trước task, task không chạm, không commit cùng task — log: `evidence/implement-scope.log`

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `cd mobile && flutter test --reporter failures-only` | 1780 pass / 15 fail / 2 skip | `evidence/implement-final-frontend.log` |

15 test fail, không file nào render S06 hay `MedicationCard`:

| File test | Số fail | Ghi chú |
|---|---|---|
| `test/features/medication/medication_screens_test.dart` ("chọn thuốc, đổi tần suất…") | 1 | Fail cả trên `main` sạch (`evidence/implement-P6-baseline-main.log`) |
| `test/app/adherence_demo_bootstrap_test.dart` | 1 | Fail cả trên `main` sạch (baseline chạy dở, `evidence/implement-final-frontend-baseline-main.log`) |
| `test/features/interaction_check/interaction_flow_test.dart` | 5 | Luồng `AddMedicationScreen`, task không sửa; chưa chạy baseline xác nhận |
| `test/features/drug_food_warning/food_warning_flow_test.dart` | 2 | Như trên |
| `test/features/family_link/patient_switcher_home_entry_test.dart` | 2 | Home, ngoài phạm vi; chưa xác nhận baseline |
| `test/features/profile/profile_layout_test.dart` | 2 | Profile, ngoài phạm vi; chưa xác nhận baseline |
| `test/shared/widgets/mascot/mascot_artwork_test.dart` | 2 | Mascot, ngoài phạm vi; chưa xác nhận baseline |

Baseline toàn suite trên `main` bị người dùng dừng giữa chừng; chỉ 2 lỗi đầu đã xác nhận có sẵn.

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Theo Q1–Q4 của `01`: bỏ hàng chip lọc, banner sắp hết, dòng giờ uống trên thẻ; không có chấm đỏ trên nút khiên.
- Nút thêm ở header đổi từ `FilledButton "Thêm"` sang nút tròn `Icons.add` key `medication-add-button`, tooltip "Thêm thuốc". `openAddScreen` trong test đổi theo.
- Thuốc đã ngừng: ô viên thuốc giữ màu, bọc `Opacity(0.45)` (key `medication-card-stopped-tile`) thay cho `muted`.
- Placeholder ô tìm dùng `#A6A6A6` đúng spec; tương phản với nền trắng khoảng 2.4:1, dưới AA. Cân nhắc đổi về `inkMuted` nếu người duyệt ưu tiên người lớn tuổi.

## 6. Phát sinh

- Các test fail ngoài S06 (mục 3) chưa có baseline đầy đủ.
- `AGENTS.md`, `.agents/core.md` có thay đổi chưa commit từ trước task.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: chạy app so trực quan với spec (P8/AC8), rồi `python .agents/scripts/gate.py approve adhoc-20261127-my-meds-redesign implement`.
- Cập nhật lần cuối: 2026-11-27, Claude Code
