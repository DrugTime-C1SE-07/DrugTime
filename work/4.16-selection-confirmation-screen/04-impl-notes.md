---
task: 4.16-selection-confirmation-screen
stage: implement
owner: phucnguyenngoc
started_at: 2026-10-26 20:25
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-26 21:58 +0700
content_hash: sha256:4d2fac667536668a
inputs:
  01-requirement.md: sha256:68d21d09eefdb715
  03-plan.md: sha256:5eee2adbfe7e1076
---

# 4.16 · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | Panel: chọn/đổi/confirm một lần/reset/thiếu metadata, danh sách 30 mục/tên dài; 6 tổ hợp màn/chữ và semantics pass | `evidence/implement-medication-final-v2.log` |
| P2 | xong | Hai nguồn dùng chung panel; hủy/Back null, tìm thủ công trả caller một lần; dispose an toàn | `evidence/implement-medication-final-v2.log` |
| P3 | xong | DI, debounce/generation/limit/error/retry, query đổi xóa chọn, no-result focus cùng ô; keyboard matrix và modal CTA trên bàn phím pass | `evidence/implement-medication-final-v2.log` |
| P4 | xong | Bốn preset offline + thiếu/dài; chặn HTTP ngoài dự kiến, spy lưu 0, injected search không gọi repo; route chặn production/cho preview debug | `evidence/implement-medication-final-v2.log` |
| P5 | xong | Form chỉ đổi sau confirm, chọn Losartan rồi hủy giữ Amlodipin và liều/giờ; spy không lưu trước Lưu; validation cũ pass | `evidence/implement-medication-final-v2.log` |
| P6 | xong, có lỗi baseline | Format/analyze/scope đạt; medication 172 pass; toàn suite 830 pass/1 skip/2 fail đã tái hiện trên main sạch | `evidence/implement-final-frontend.log`, `evidence/implement-baseline-family.log` |
| P7 | giai đoạn test | Sau duyệt 04: Android, Excel, 05 | Chưa chạy |

## 2. File đã thay đổi

Frontend: nhánh `feat/4.16-selection-confirmation-screen`, base `origin/main` (`ccdc3ad`). Đúng 13 file của bảng 03-plan.md, gồm 7 file thêm và 6 file sửa:

- Panel: `mobile/lib/features/medication/presentation/widgets/drug_selection_panel.dart`.
- Screen/typed helper: `mobile/lib/features/medication/presentation/screens/drug_selection_screen.dart`.
- Picker production: `mobile/lib/features/medication/presentation/widgets/drug_catalog_sheet.dart`.
- Fixture/demo: `mobile/lib/features/medication/data/models/drug_selection_demo_fixtures.dart`, `mobile/lib/features/medication/presentation/screens/drug_selection_demo_screen.dart`.
- Route/entry preview: `mobile/lib/app/router.dart`, `mobile/lib/features/medication/presentation/screens/add_medication_screen.dart`.
- Tests mới: `mobile/test/features/medication/drug_selection_panel_test.dart`, `drug_selection_flow_test.dart`, `drug_selection_demo_test.dart`.
- Tests cập nhật: cùng thư mục `drug_catalog_sheet_test.dart`, `medication_lookup_widget_test.dart`, `medication_screens_test.dart`.

Scope implement: mọi thay đổi trong phạm vi; workbook docs chưa sửa vì thuộc P7/giai đoạn test. Log `evidence/implement-scope.log`.

## 3. Kết quả test cuối

| Lệnh trong frontend/mobile | Kết quả | Log |
|---|---|---|
| `flutter test --no-pub test/features/medication --reporter expanded` | 172 pass, 0 fail | `evidence/implement-medication-final-v2.log` |
| `flutter analyze --no-pub` | No issues found | `evidence/implement-analyze-final.log` |
| `flutter test --no-pub --reporter expanded` | 830 pass, 1 skip, 2 fail; không báo toàn suite pass | `evidence/implement-final-frontend.log` |
| `dart format --output=none --set-exit-if-changed <13 file Dart ở mục 2>` | 13 files, 0 changed, exit 0 | `evidence/implement-format-check-final.log` |
| `git -C frontend diff --check` (từ gốc) | Exit 0, không lỗi whitespace | `evidence/implement-diff-check.log` |
| `scope.py 4.16-selection-confirmation-screen --stage implement` (từ gốc) | 13 frontend file OK, không file ngoài phạm vi | `evidence/implement-scope.log` |

### Kiểm chứng lỗi có sẵn

Không sửa hai file test family ngoài phạm vi. Đã xuất toàn bộ `mobile` từ `origin/main` **ccdc3adff1dda6e6664a63d02e7d9e09c7ceb212** bằng `git -C frontend archive --format=zip --output=<task>/scratch/baseline.zip origin/main mobile`, giải nén vào `scratch/baseline/`, chạy `flutter pub get --offline`, rồi chạy:

`flutter test --no-pub test/features/family_link/family_tab_screen_test.dart test/features/family/family_link_code_stability_test.dart --reporter expanded`

Kết quả trên main sạch: **10 pass, 2 fail**, trùng hai case của toàn suite sau thay đổi:

1. `family_tab_screen_test.dart`: `alert entry displays server unread count and removes it after clear` — fixture thiếu `ConsentScope` và `FamilyLinkScope`, không hiện `1 chưa đọc`.
2. `family_link_code_stability_test.dart`: case `4. Tích hợp vòng đời phiên...` — không thấy `PATIENT10X` sau đăng xuất/đăng nhập lại.

Evidence: `evidence/implement-baseline-pub.log`, `evidence/implement-baseline-family.log`. Bản baseline không có code 4.16; chỉ nằm trong scratch, không commit. Một test live adherence bị skip vì chưa có cấu hình live theo skip sẵn tại `test/features/adherence_history/adherence_history_live_repository_test.dart:45`; task không đổi skip hoặc môi trường live.

Runtime: Flutter 3.47.5, Dart 3.13.4. Gọi CLI bằng `C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot <lệnh>`; formatter dùng dart.exe trực tiếp. Output lưu bằng `2>&1 | Tee-Object -FilePath <log>`. Không coi widget/flow fake là integration backend/OCR thật.

## 3b. Bộ test case Excel

Task M: làm ở giai đoạn test.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

Đã đối chiếu QD-38/39/45 ở nguồn nghiệp vụ, trạng thái ✅ là chốt baseline, chưa phải xác nhận triển khai/Mentor ký. Giữ ID/metadata, xác nhận trước trả về, hàm lượng tách liều; không tạo thuốc ngoài danh mục, OCR/storage/API mới. AC11 và T21/T22 thuộc nghiệm thu Android ở giai đoạn test, không suy từ widget test.

| Truy vết | Thực hiện và bằng chứng |
|---|---|
| QD-39 → AC1/3/4/9 → P1/2/3/5 | T1/T3–T5/T14/T15: cả hai nguồn, chọn chưa trả, đổi/hủy giữ form, confirm trả đúng item một lần; spy lưu chỉ chạy ở nút Lưu. Medication 172 pass. |
| QD-39 → AC2/5/6/7 → P1–P4 | T2/T6–T9/T16: không xếp lại/gán gần giống; no-result chỉ tìm lại/hủy, kết quả tìm tay về caller; refresh/query xóa chọn cũ; không có đường Admin. |
| QD-38 → AC2/8/9 → P1/4/5 | T2/T10/T14/T15: giữ object/id, thiếu field hiện Chưa có thông tin, fixture unit rỗng, không quy đổi liều/hàm lượng. |
| QD-45 và vòng đời OCR → AC9 → P4/P6 | T13/T16: fixture tổng hợp riêng, injected lookup offline, spy không lưu, production picker tiếp tục controller; không ảnh/văn bản OCR thật hay endpoint mới. |
| AC10 → P1/P3 | T11/T12: 320×568 và 375×812, scale 1/1.5/2, 30 ứng viên/tên dài, semantics selected/button/enabled; bàn phím giả lập và test modal CTA/query nằm trên inset. |

Log các test trên: `evidence/implement-medication-final-v2.log` và lượt toàn suite. Không có build release/Android thủ công trong giai đoạn này; chặn release được viết bằng `preview && kDebugMode`, test route kiểm preview true/false ở debug, chưa tuyên bố đã chạy binary release.

Cách mở demo sau khi chạy app debug preview (`--dart-define=DRUGTIME_PREVIEW=true`): Thêm thuốc mới → **Mẫu · Xem thử chọn và xác nhận thuốc**; hoặc route `/medications/selection-demo`. Chọn một trong bốn preset, tìm thủ công bằng `Paracetamol`; kết quả chỉ hiện trong phiên demo. Phần chọn danh sách/no-result là UI theo AC ở plan; không tuyên bố có frame Figma riêng. Không coi mock là tích hợp thật của 4.13/4.15.

## 6. Phát sinh

- Python WindowsApps không chạy được; dùng runtime bundled `C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8`.
- Gate implement: được phép bắt đầu. Frontend sạch trước sửa; fetch origin xác nhận task 3.25 đã merge vào main (PR45). Base frontend là origin/main ccdc3ad, không kéo commit chưa merge.
- Các con trỏ backend/docs/frontend khác baseline đã có trước task; không commit/bump chúng.
- Khi chuẩn bị nhánh, lần đầu nhánh superproject kế thừa hai commit 3.25 chưa merge; scope vì thế báo 280 file lịch sử ngoài task. Đã giữ nhánh đó tại `codex/4.16-initial-base`, tạo lại nhánh `feat/4.16-selection-confirmation-screen` từ `origin/main` **67fbc39**, không reset/rebase/xóa lịch sử và không sửa các file cũ. Scope sau đó đạt; các checkout submodule vẫn giữ nguyên nên api_contract/tests cũng hiện con trỏ khác base main, không phải code mới của 4.16.
- Git thao tác nhánh và Flutter SDK lock/cache cần quyền ghi ngoài sandbox mặc định; chạy lệnh được auto-review cho phép. Không có từ chối auto-review còn chặn.
- Lượt test đầu phát hiện vấn đề cuộn vùng xem lại ở danh sách dài, inset keyboard và các finder nằm ngoài viewport; đã sửa trong panel/sheet/test đúng plan. Modal host dành inset một lần, sheet dùng khoảng trống được cấp; tiêu đề phụ thu gọn khi không gian thấp, CTA vẫn ngoài vùng cuộn. Test modal bổ sung xác minh CTA nằm trên bàn phím.
- Lượt analyze đầu có deprecated semantics API/prefer_const; đã sửa, analyze cuối sạch. Một lượt medication lỗi compile vì thiếu import `Tristate`, đã thêm import; log v2 đạt 172. Giữ log các lượt lỗi ban đầu để truy vết, không dùng làm kết quả cuối.
- Sau chỉnh semantics, formatter phát hiện 2 file test; đã format và kiểm lại 13 file/0 changed.
- Hai lỗi full-suite đã có trên main sạch, là giới hạn baseline cần theo dõi ở task family riêng; không sửa file ngoài plan để làm xanh toàn suite.
- Artifact `work/` đang bị ignore theo `.gitignore` hiện hành; chưa commit/push, chưa sửa ignore. Khi người dùng yêu cầu commit artifact cần stage tường minh theo wf-git; không stage scratch.

## Bước tiếp theo

- Đang chờ: người duyệt implement. P1–P6 đã xong (6/6 bước thuộc implement); P7 thuộc giai đoạn test.
- Đọc 04, đặc biệt 2 lỗi baseline và phạm vi mock; tự chạy `python .agents/scripts/gate.py approve 4.16-selection-confirmation-screen implement` trong terminal. Nếu Python alias chưa chạy được: `& 'C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' -X utf8 .agents/scripts/gate.py approve 4.16-selection-confirmation-screen implement`.
- Sau duyệt, lượt tiếp theo dùng wf-next → wf-test: chạy nghiệm thu Android T21/T22, ghi AC11, bộ test case Excel theo wf-testcase và 05-test-report.md. Chưa tạo 05 hoặc Excel trong lượt implement.
- Có thể commit artifact/evidence và code khi người dùng yêu cầu; chưa commit/push.
- Cập nhật lần cuối: 2026-10-26, Codex.
