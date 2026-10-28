---
task: 4.16-selection-confirmation-screen
stage: test
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-28 10:40 +0700
content_hash: sha256:6f3c7c38451a6df1
inputs:
  01-requirement.md: sha256:68d21d09eefdb715
  03-plan.md: sha256:5eee2adbfe7e1076
  04-impl-notes.md: sha256:4d2fac667536668a
---

# 4.16 · Kiểm thử chọn và xác nhận thuốc

## Cập nhật ngày 28/10/2026 — đã thực hiện các case Pending

Đã thực hiện đủ 6 case Pending: **5 Pass, 1 Fail**. Tổng MEDPICK hiện tại: **52 case — 50 Pass, 2 Fail, 0 Pending**. TC-28/51 cùng một lỗi layout Medium; TC-51 giữ kết quả phiên trước. Người dùng xác nhận TC-52 đạt thao tác và bổ sung **“talkback hoạt động bình thường”**; TalkBack Pass theo kết quả kiểm tay của người dùng. Test vẫn draft; người dùng đã chấp nhận lỗi layout Medium và hoãn sửa, có thể trình người duyệt xem xét cùng ngoại lệ này.

Các mục 1–8 bên dưới lưu kết quả phiên 27/10 để truy vết. Kết quả mới, giới hạn và bàn giao hiện tại nằm ở mục 9; các số Pending cũ trong mục 1–8 không còn là trạng thái mới nhất.

## 1. Môi trường

- Requirement, plan và implement đã được duyệt; gate test cho phép bắt đầu (`evidence/test-gate.log`). Không sửa artifact đã duyệt.
- Flutter 3.47.5 / Dart 3.13.4, Windows; frontend/docs trên `feat/4.16-selection-confirmation-screen`.
- Mọi kiểm thử chức năng trong phạm vi là UI/widget/flow với fixture tổng hợp. Không có AC integration backend/PostgreSQL/OCR trong 01/03; không reset DB, không tạo test tích hợp giả và không nghiệm thu tích hợp thật 4.13/4.15.
- Android thật: LM G710 (`LMG7103f11b938`), Android 13, kích thước gốc 1440×3120, density 560, font 1.0. Harness ở `scratch/selection_device_test.dart`, driver ở `scratch/selection_driver.dart`; chỉ dùng widget/route sản phẩm và fixture mock, không ảnh/văn bản OCR/người bệnh thật.
- Runtime CLI: `C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot`; Python: `backend/.venv/Scripts/python.exe -X utf8` vì alias `python` WindowsApps không chạy được.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test / truy vết | Kết quả trong phiên 27/10/2026 |
|---|---|---|
| AC1 | T1/T13; TC-MEDPICK-30/46; hai nguồn cùng panel và bốn preset | Pass widget/flow |
| AC2 | T2; TC-31; thứ tự, cùng tên/hàm lượng khác, object/id gốc | Pass |
| AC3 | T3/T14/T15; TC-32/33/34/49; chọn tạm, confirm rõ ràng, khóa lặp | Pass |
| AC4 | T4/T5/T14; TC-34/35/36/48; đổi/hủy/Back và giữ form | Pass |
| AC5 | T6/T8; TC-37/39; OCR rỗng → tìm tay → trả caller một lần | Pass |
| AC6 | T7/T8/T16/T19/T20; TC-38/39; sửa query tại sheet hiện tại, retry/hủy | Pass |
| AC7 | T9/T18; TC-40/41; thay dữ liệu cùng id/xóa/đổi query/response cũ | Pass |
| AC8 | T10; TC-42; metadata thiếu không suy diễn | Pass |
| AC9 | T13–T20; TC-46/47/48/49 và hồi quy TC-01–24 | Pass trong phạm vi mock; chưa chạy binary release/OCR/API thật |
| AC10 | T11/T12; TC-43/44/45; sáu tổ hợp kích thước/chữ, semantics và modal keyboard; TC-51 thiết bị thật | Pass widget, **Fail Android màn nhỏ/chữ lớn**: vùng xem lại 21.34 dp < một dòng chữ 35 dp |
| AC11 | T21/T22; TC-50/51 thiết bị tự động; TC-52 nghiệm thu bằng tay | **Chưa đạt**: TC-51 Fail; TC-52 Pending, chưa kiểm TalkBack/cảm nhận chạm bằng tay |

Log unit/widget/flow: `evidence/test-medication.log` (172 pass). Tên T là mã truy vết trong 03; tên test thực tế nằm trong comments của testcases.json, không giả định trùng tên dự kiến.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản áp dụng | Test | Kết quả |
|---|---|---|
| Không xác nhận nhầm thuốc/hàm lượng; chỉ trả object hiện hành | Panel, flow, sheet; T2–T10/T18 | Pass |
| Hủy không thay dữ liệu form; lựa chọn không tạo thuốc/lịch | T13/T14/T15, spy lưu và HTTP guard | Pass |
| Response cũ/query mới không khôi phục lựa chọn | T9/T18/T19 | Pass |
| Giới hạn query 0/1/99/100/101 Unicode rune, whitespace/emoji | T17/T20; TC-02/03/04/09–12 | Pass |
| Màn nhỏ/chữ lớn/bàn phím và semantics | T11/T12, TC-51 | Pass widget; Fail thực tế ở 360×616 dp, font 1.5, keyboard 325.5 dp |

Không thay endpoint/service sức khỏe, consent/caregiver, liều/Worker, interaction engine, schema hoặc ranh giới module. Các kịch bản cross-patient/thu hồi consent/idempotency liều/race/interaction không áp dụng cho phạm vi UI mock này.

## 4. Kết quả chạy lại bộ test

Các lệnh Flutter chạy từ `frontend/mobile`, output thô lưu bằng `2>&1 | Tee-Object <log>`, giữ exit code của lệnh:

| Lệnh | Kết quả | Evidence |
|---|---|---|
| `flutter test --no-pub test/features/medication --reporter expanded` | 172 pass, 0 fail; 27 giây theo reporter | `evidence/test-medication.log` |
| `flutter test --no-pub --reporter expanded` | 830 pass, 1 skip, 2 fail; 91 giây theo reporter; exit 1 | `evidence/test-full-flutter.log` |
| `flutter analyze --no-pub` | No issues found; 56 giây; exit 0 | `evidence/test-analyze.log` |
| `flutter drive --no-pub -d LMG7103f11b938 --dart-define=DRUGTIME_PREVIEW=true --driver=<task>/scratch/selection_driver.dart --target=<task>/scratch/selection_device_test.dart` | Android font 1.0: luồng chính Pass; reporter +2 gồm một case chính và teardown, không phải hai kịch bản độc lập | `evidence/test-android-normal-v5.log` |
| Cùng lệnh drive, wrapper `scratch/run_large_android.ps1` đặt 720×1280/density 320/font 1.5 rồi khôi phục | Android 360×616 dp: regression Fail, viewport 21.34 < 35 dp; exit 1 | `evidence/test-android-large-regression-v2.log` |

`<task>` là đường dẫn tuyệt đối `D:/DrugTime/source/DrugTime/work/4.16-selection-confirmation-screen`. Đây là UI tự động trên thiết bị thật; không phải E2E OCR/backend thật và không thay nghiệm thu bằng tay. Ảnh normal/large đã được agent đọc; Flutter surface không bao gồm pixel bàn phím hệ thống, inset được đo trực tiếp từ FlutterView. Wrapper lưu cấu hình trước/sau và khôi phục đúng 1440×3120, density 560, font 1.0 trong `finally`.

### Hai lỗi toàn suite ngoài task

1. `family_tab_screen_test.dart`: `alert entry displays server unread count and removes it after clear`; kỳ vọng `1 chưa đọc`, thực tế không thấy. Log còn báo thiếu scope của fixture family/consent.
2. `family_link_code_stability_test.dart`: `4. Tích hợp vòng đời phiên...`; kỳ vọng `PATIENT10X` sau đăng nhập lại, thực tế không thấy.

Hai tên/triệu chứng trùng với baseline đã được tái hiện trên `origin/main` sạch `ccdc3ad` ở giai đoạn implement (04 và `evidence/implement-baseline-family.log`). Phiên test này chạy lại toàn suite hiện tại, **không chạy lại checkout main sạch**; không coi chứng cứ cũ là lần chạy mới. Không sửa test family hoặc sản phẩm ngoài plan để làm xanh suite. Không báo toàn suite pass.

### Scope

- Scope cuối: workbook docs được `[OK]`, **exit 1 vì 14 file ngoài phạm vi**, không báo scope pass. Log: `evidence/test-scope-final.log` (baseline tại `evidence/test-scope.log`). `git -C frontend diff --check`: exit 0 (`evidence/test-diff-check.log`). Gate cuối vẫn giữ 01/03/04 approved, 05 draft, chưa có 06: `evidence/test-final-gate.log`.
- `scope.py --stage test` đếm cả thay đổi của giai đoạn trước nên báo 13 frontend file đã có từ implement được duyệt; SHA-256 của 13 file được chụp khi bắt đầu test và kiểm lại không đổi. Không sửa code/test frontend trong giai đoạn này.
- Còn thay đổi ngoài task tại `backend/src/drugtime/modules/catalog/fetchers.py`, nhánh backend `feat-3.26`; agent không tạo/sửa file đó. Người dùng xác nhận **“Giữ nguyên và ghi rõ khi bàn giao”** trong phiên 27/10/2026. Không sửa script scope hoặc che kết quả scope thô.

## 5. Bộ test case Excel

- Spec: `testcases.json`; file task: `testcases.xlsx`; file tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Dùng lại chức năng `MEDPICK`, sheet `Chọn thuốc danh mục`; giữ nguyên ID 01–29, bổ sung 30–52. Case chọn cũ được cập nhật bước **Xác nhận thuốc** theo hành vi mới.
- Theo lựa chọn người dùng **“Chuyển case chưa chạy lại sang Pending”**, các case API/DB/thiết bị backend thật chưa chạy lại không giữ Pass từ 3.05. Không thay kết quả của chức năng khác.
- Validate/build/merge cuối đều exit 0 bằng `.agents/scripts/testcase_xlsx.py`; log: `evidence/testcase-xlsx.log`. Kiểm file cuối exit 0: `evidence/test-output-verification-final.log`; 52 ID không trùng, đúng 45/1/6, một bug Medium; giữ nguyên value/formula/style/number format của 20 sheet không liên quan. 13 frontend file giữ nguyên SHA-256 từ lúc bắt đầu stage test (hash ở `evidence/test-stage-input-hashes.json`).
- Bản render chỉ đọc bằng artifact-tool; đã đọc ảnh bảng/cột, tổng Report và dòng Bug Report, nội dung không bị cắt. Tổng Report được tính/render đúng 45 Pass/1 Fail/6 Pending. Log/ảnh: `evidence/test-excel-render-final.log`, `evidence/excel-*-final-*.png`. Không xuất lại XLSX bằng thư viện khác; chỉ script chuẩn ghi workbook. Chưa chạy native Microsoft Excel để xác minh recalculation ở ứng dụng đó; workbook có fullCalcOnLoad.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| MEDPICK | 52 | 45 | 1 | 6 |

Pending: TC-MEDPICK-25/26/27/28/29 (API/DB/backend thật chưa chạy lại); TC-52 (người kiểm thực hiện T21/T22, cảm nhận câu chữ/chạm/cuộn/TalkBack). TC-25–29 thuộc hồi quy cũ ngoài nghiệm thu mock 4.16, không phải yêu cầu tích hợp mới của task này. TC-50 Android mặc định Pass; TC-51 Android màn nhỏ/chữ lớn Fail và sinh đúng một Bug Report `BUG-MEDPICK-51` mức Medium.

## 5b. Lỗi sản phẩm tìm thấy

**BUG-MEDPICK-51 — Medium — Vùng danh sách/xem lại không đủ hiển thị một dòng khi mở bàn phím trên màn nhỏ, chữ lớn.**

- Tái hiện: Android 13 LM G710, `wm size 720x1280`, density 320, font 1.5 → viewport 360×616 dp. Mở OCR · Không có kết quả → Tìm kiếm thủ công → nhập `no-match` → tìm lại → `Paracetamol`, giữ keyboard mở, cuộn/chạm `demo-500`.
- Kỳ vọng theo AC10/AC11: có thể đọc/xem lại thông tin lựa chọn và thao tác xác nhận trên thiết bị; ít nhất một dòng metadata phải đọc trọn trong vùng cuộn.
- Thực tế: keyboard thật 325.5 dp; list viewport **21.34 dp**, trong khi một dòng `AppTextStyles.body` ở scale 1.5 cao **35 dp**. Chọn đã xảy ra (confirm bật) nhưng vùng xem lại bị cắt thành dải hẹp. `Hàm lượng: 500 mg` không được dựng trong vùng cache hiện tại; ảnh cho thấy dải chữ bị cắt ngay trên nút confirm. Không phải chọn sai object hay không nhận sự kiện chạm.
- Nguyên nhân đã đối chiếu: `DrugCatalogSheet` dùng `SizedBox(height: constraints.maxHeight * 0.92)` sau khi host trừ keyboard; header tìm kiếm và CTA giữ chiều cao, phần `Expanded`/ListView còn lại quá thấp. Widget matrix dùng inset giả 220 dp nên chưa đại diện keyboard thật 325.5 dp ở cấu hình này.
- Bằng chứng: `evidence/test-android-large-v4.log`, `evidence/test-android-large-regression-v2.log`, `evidence/android-large-selection-debug.png`, `evidence/android-large-unreadable-review.png`. Regression đã chạy và fail với **21.34 < 35**, exit 1; cần pass sau fix, không tăng retry/timeout để che lỗi. Cấu hình màn/font đã được khôi phục ở cuối log.
- Mức Medium vì có cách tránh: đóng bàn phím hoặc giảm cỡ chữ. Không có bằng chứng chọn sai thuốc/lưu sai dữ liệu. Cần sửa layout trong implement và chạy lại Android+regression; **không sửa code sản phẩm ở stage test**.

Hai lỗi family toàn suite báo riêng ở mục 4; không gán thành lỗi MEDPICK hoặc sửa ngoài phạm vi.

Các lượt harness lỗi đầu được giữ nguyên: khởi tạo route thiếu ConsentScope; đọc sai inset từ MediaQuery đã removeViewInsets; chờ debounce chưa đúng; finder chọn panel bên dưới sheet hoặc center của dòng nằm ngoài viewport. Đã sửa harness trong scratch để chờ trạng thái và chạm phần thực sự nhìn thấy, vẫn assert vùng chạm và hành vi. Sau đó xác nhận `confirm enabled=true` nhưng review viewport không đọc được; đây là lỗi sản phẩm nêu trên, không còn quy mọi failure cho harness.

## 6. Test không ổn định hoặc bị skip

- Một test live adherence bị skip theo điều kiện cấu hình có sẵn tại `test/features/adherence_history/adherence_history_live_repository_test.dart`. Không thay skip hoặc biến môi trường để che lỗi.
- Không tuyên bố kiểm TalkBack/cảm nhận chạm bằng tay hoặc release binary. T21/T22 vẫn cần ghi nghiệm thu thủ công tại `evidence/test-manual-selection.log`.

## 7. Phát sinh

- Sandbox chặn ghi evidence và Flutter/ADB cache; đã chạy lệnh cần thiết qua escalation được chấp thuận, không đổi quyền máy/repo.
- Build Android có cảnh báo tương thích tương lai của Gradle/AGP/Kotlin và SDK XML. Không đổi toolchain trong task UI này.
- Lượt `test-android-large-regression.log` dừng sau khi yêu cầu chụp liên tiếp cùng một trạng thái bị treo. Đã dừng runner, chủ động khôi phục cấu hình gốc, bỏ ảnh trùng và chạy lại trọn lượt tại `test-android-large-regression-v2.log`; bản v2 mới là regression cuối. Không gọi log bị ngắt là test hoàn tất.
- Helper tổng hợp Excel lần đầu đọc nhầm encoding UTF-16 của Tee-Object và chưa điền case Android vào spec; kiểm Bug Report bắt được thiếu bug (`evidence/test-output-verification.log`). Đã sửa helper đọc BOM, cập nhật spec và chạy lại validate/build/merge/verify thành công; không dùng workbook trung gian làm bản bàn giao. Giữ evidence lượt lỗi và kết quả cuối riêng.
- Không commit/push, không bump con trỏ submodule. Các con trỏ có sẵn vẫn giữ nguyên.

## 8. Bàn giao theo wf-handoff

- `05` vẫn draft; không sửa `01/03/04` đã duyệt. Trạng thái chính thức tiếp tục là test, đang chờ mở lại implement để sửa bug.
- Thay đổi chưa commit của task: 13 frontend file từ implement (liệt kê tại mục 2 của 04, stage này không đổi), workbook `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, artifact `05`, spec/workbook task và evidence. Superproject còn các con trỏ api_contract/backend/docs/frontend/tests khác base; không stage chúng. Thay đổi backend fetchers ngoài task giữ nguyên theo xác nhận người dùng.
- Danh sách `git status --short --branch`: `evidence/test-git-status.log`; đã soạn lệnh stage/commit/push tường minh trong `evidence/test-handoff-commands.txt`, **chưa chạy**. Chỉ dùng khi người dùng yêu cầu; không stage scratch, không bump tới commit chưa push.
- Người tiếp tục: sau khi người dùng reopen implement, gõ `continue task 4.16`; đọc bug và regression ở mục 5b trước khi sửa. Cần lưu/commit artifact/evidence cùng task nếu chuyển máy; scratch hiện chỉ ở workspace này, các lệnh Git đã soạn không stage scratch theo quy tắc dự án.

## 9. Thực thi các case Pending — 28/10/2026

### Kết quả

| Test case | Kết quả mới | Bằng chứng |
|---|---|---|
| TC-MEDPICK-25 | Pass; dấu/không dấu/hoa thường với tên và hoạt chất, cả hai route | `evidence/test-pending-catalog-search-rerun.log` |
| TC-MEDPICK-26 | Pass; loại thuốc đã gỡ, schema, limit, ưu tiên tiền tố/thứ tự | Cùng log catalog |
| TC-MEDPICK-27 | Pass; Android → RemoteMedicationRepository → API → PostgreSQL thật; 5 query đúng id=153, loại id=154 đã gỡ. Chạm chỉ chọn, form chỉ đổi khi Xác nhận. Không tạo thuốc/lịch/đơn | `evidence/test-pending-TC27-android-final.log`, `evidence/test-pending-device-response.json` |
| TC-MEDPICK-28 | **Fail, Medium**; vùng xem lại 21.34 dp < một dòng 35 dp khi keyboard 325.5 dp, màn 360×616 dp/chữ 1.5 | `evidence/test-pending-TC28-android-confirmed.log`, `evidence/pending-28-selected-review.png` |
| TC-MEDPICK-29 | Pass; %, _ và backslash tìm nguyên văn, không wildcard khớp mọi thuốc | Cùng log catalog |
| TC-MEDPICK-52 | Pass thao tác và TalkBack theo người dùng; xác nhận bổ sung: “talkback hoạt động bình thường” | `evidence/test-manual-selection.log` |

Catalog suite: **43 pass, 0 fail, 0 skip trong 9.86s**, một cảnh báo deprecation Starlette/httpx. DB local reset sạch thành công; chỉ dùng host `127.0.0.1:54322`. Lệnh từ backend: `.venv/Scripts/python.exe -X utf8 -m pytest tests/integration/test_catalog_search.py -v -ra`. Log start/reset: `evidence/test-pending-supabase-start.log`, `evidence/test-pending-db-reset.log`.

TC-27: lệnh `flutter drive --no-pub -d LMG7103f11b938 --dart-define=QA_CASE=AC4 --driver=<task>/scratch/pending_catalog_driver.dart --target=<task>/scratch/pending_catalog_device_test.dart`, exit 0. Báo cáo JSON xác nhận đủ 5 query đã đến server; id đã gỡ không có trong kết quả; `add_calls=0`, DB `meds/schedules/prescriptions=0/0/0` trước và sau. Session fixture dùng danh tính tổng hợp, không kiểm login và không ghi token ra evidence.

TC-28: cùng target qua wrapper `scratch/run_pending_large_android.ps1`, `QA_CASE=AC14`. Lượt cuối `test-pending-TC28-android-confirmed.log` chạy qua hướng dẫn, loading có barrier, 503 được tiêm một lần tại fixture, retry/no-result, query 99 ký tự, tìm hoạt chất qua API/DB thật, cuộn và chạm item. `selected=true`, không ghi bản ghi cá nhân; assert khả năng đọc Fail **21.34 < 35**, exit 1. Đây là cùng nguyên nhân với BUG-MEDPICK-51 ở mục 5b, không phải hai nguyên nhân độc lập. Bug Report có hai dòng `BUG-MEDPICK-28` và `BUG-MEDPICK-51`, cùng Medium. Có cách tránh bằng đóng bàn phím hoặc giảm cỡ chữ. Không sửa code sản phẩm để làm xanh test.

TC-52: người dùng trực tiếp kiểm, agent ghi nhận phản hồi. Màn sản phẩm `DrugSelectionDemoScreen` được mở từ QA entry trong scratch bằng `flutter run --no-pub --no-resident -d LMG7103f11b938 --dart-define=DRUGTIME_PREVIEW=true --target=<task>/scratch/manual_selection_app.dart`, exit 0. Đây là UI demo tổng hợp; không coi là nghiệm thu OCR/API mới của 4.13/4.15. Người dùng đã bổ sung xác nhận “talkback hoạt động bình thường”; TalkBack Pass theo người kiểm, agent không tự nhận đã thao tác. Không đo riêng cấu hình màn/font trong lượt người dùng thao tác. Kết quả người dùng không thay thế regression màn nhỏ TC-28/51; AC10/AC11 tổng thể vẫn chưa đạt do lỗi layout.

### Excel và phạm vi

- Spec `testcases.json`, workbook task `testcases.xlsx` và workbook tổng `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` đã cập nhật **50 Pass / 2 Fail / 0 Pending**. Chỉ đổi 6 case từng Pending; 46 case khác giữ nguyên nội dung/kết quả lịch sử, không gọi là đã chạy lại trong phiên này.
- Validate/build/merge đều exit 0, không cảnh báo xung đột kết quả: `evidence/test-pending-testcase-validate.log`, `test-pending-testcase-build.log`, `test-pending-testcase-merge.log`. Kiểm workbook/spec/ID/Bug Report và bảo toàn 20 sheet không liên quan: `evidence/test-pending-output-verification.log`.
- Đã tính lại và render bản đọc bằng artifact-tool, không xuất XLSX bằng tool khác. Kiểm ảnh các case vừa cập nhật, dòng chức năng, TC-52 và Bug Report; không thấy nội dung bị cắt. Log `evidence/test-pending-excel-after.log`, ảnh `evidence/excel-pending-after-*.png`. Tỷ lệ Report: 100% executed, 50/52 pass và 2/52 fail. Chưa kiểm recalculation trong native Excel.
- 13 file frontend giữ nguyên SHA-256 so với đầu stage test; không sửa frontend/backend/tests hay artifact 01/03/04 đã approved. Không chạy lại full Flutter/backend integration suite vì yêu cầu lượt này là các Pending và không có thay đổi code sản phẩm; kết quả toàn suite ở mục 4 là bằng chứng 27/10.
- Scope cuối vẫn exit 1 do 13 file frontend của implement được duyệt và file backend `catalog/fetchers.py` ngoài task đã có từ trước; workbook docs được phép. Không coi scope là pass. Log `evidence/test-pending-scope.log`; người dùng đã yêu cầu giữ nguyên file backend ở phiên trước. Diff check `evidence/test-pending-diff-check.log`; gate `evidence/test-pending-final-gate.log`.

### Các lượt chưa dùng để kết luận

- Lượt catalog đầu bị ngắt sau collect; chỉ log `test-pending-catalog-search-rerun.log` là lần chạy hoàn tất.
- TC-28 v1/v2 chờ frame/response chưa đúng; v3/v4 cho thấy panel rỗng đã có nhưng ListView chưa dựng thông báo trước cuộn. Đã sửa harness bằng thao tác cuộn và chờ trạng thái; không bỏ/nới assertion, không tăng timeout/retry để che lỗi. Chỉ lượt `confirmed` là kết quả sản phẩm cuối.
- `test-pending-TC28-android-final.log` không chạy được do Gradle `BindException: Address already in use`; không tính lỗi hạ tầng này là Fail sản phẩm. Đã chạy lại thành công phần build và tái hiện lỗi layout ở log `confirmed`.
- Helper đối chiếu log TC-27 ban đầu đòi đủ dòng native stdout đã fail vì log chuyển tiếp bất đồng bộ thiếu đoạn cuối. Đã chạy lại với báo cáo JSON và xác minh đủ 5 query/counter, không lấy helper fail làm kết quả testcase.
- Khi cài lượt Android đầu, Flutter tự gỡ/cài lại gói `vn.drugtime.drugtime_mobile` vì chữ ký debug khác (`INSTALL_FAILED_UPDATE_INCOMPATIBLE`); dữ liệu local của bản app trước có thể đã mất. Ghi nhận trong log TC-27 đầu, không che hành vi này.
- Wrapper đã khôi phục size/density/font sau mỗi lượt; server fixture do agent tạo đã dừng và ADB reverse tcp:58905 đã gỡ. Supabase local/Docker được giữ chạy. Demo đã được mở lại, không còn tự động thao tác trên điện thoại. `evidence/test-pending-execution-results.json` lưu exit từng lệnh.

### Chấp nhận lỗi layout — 28/10/2026

Người dùng xác nhận **“thôi bỏ qua lỗi đó cũng được”** sau khi được giải thích lỗi xảy ra ở màn nhỏ 360×616 dp, cỡ chữ hệ thống 1.5 và bàn phím mở. Ghi nhận một lỗi layout Medium đã biết được chấp nhận trong task 4.16, hoãn sửa. Bằng chứng quyết định: `evidence/test-layout-risk-acceptance.log`.

TC-28/51 vẫn Fail, giữ nguyên actual/expected và bằng chứng tái hiện; tổng vẫn **50 Pass / 2 Fail / 0 Pending**. Ngoại lệ này không biến lỗi thành đã sửa hoặc AC10/AC11 thành Pass. Đây là quyết định chấp nhận rủi ro để trình duyệt, không phải phê duyệt stage. Artifact 01/03/04 đã approved giữ nguyên.

Đã cập nhật ghi chú cả hai dòng Bug Report và workbook tổng. Validate/build/merge: `evidence/test-layout-acceptance-xlsx.log`; kiểm nội dung/số liệu/bảo toàn workbook: `evidence/test-layout-acceptance-verification.log`.

## Bước tiếp theo

- Đã hoàn tất yêu cầu thực hiện các testcase Pending; không còn case Pending trong MEDPICK. TalkBack đã được người dùng xác nhận hoạt động bình thường, ghi trong TC-52 và evidence/test-manual-selection.log.
- Người dùng đã chấp nhận lỗi layout Medium ở TC-28/51 và hoãn sửa. Có thể trình duyệt báo cáo test với ngoại lệ đã ghi; AC10/AC11 vẫn có phần không đạt ở cấu hình này. Chỉ bắt đầu review sau khi test được duyệt qua gate.
- Người duyệt xem báo cáo và ngoại lệ chấp nhận lỗi, rồi tự chạy `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/gate.py approve 4.16-selection-confirmation-screen test` nếu đồng ý. Agent không chạy approve và chưa bắt đầu review. Nếu sửa layout về sau, mở lại implement và chạy lại TC-28/51 trước khi đổi kết quả.
- Không commit/push hoặc bump con trỏ. Lệnh Git dự kiến vẫn ở `evidence/test-handoff-commands.txt`; khi chuyển máy cần commit artifact/spec/workbook/evidence của task theo wf-git. Các thay đổi ngoài task giữ nguyên.
- Bổ sung xác nhận TalkBack ngày 2026-10-28; validate/build/merge và kiểm workbook: `evidence/test-talkback-xlsx.log`, `evidence/test-talkback-verification.log`. Tổng vẫn 50 Pass / 2 Fail / 0 Pending; TC-28/51 giữ nguyên.
- Cập nhật: 2026-10-28, Codex. Trạng thái chính thức: 01/03/04 approved, 05 draft.
