---
task: 3.25
stage: test
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-26 07:01 +0700
content_hash: sha256:baf76b965fbe7115
inputs:
  01-requirement.md: sha256:717a7d0a0b7c604b
  03-plan.md: sha256:13b8c04b8e364a8a
  04-impl-notes.md: sha256:53df572a97923635
---

# 3.25 · Kiểm thử lịch sử tuân thủ người thân

**Cập nhật Android sáng 26/10/2026:** cả ba scenario production route đã có **Pass trên emulator** với API/DB thật: `linked`, `revoke`, `cross_patient`; `revoke` Pass ở hai lần chạy lại. Lượt đầu dừng vì handshake, nguyên nhân chưa xác định, giữ log đỏ. AVD `Pixel_7` do task khởi động trên `emulator-5580` đã được dừng; package test và reverse mapping đã được dọn, không wipe/snapshot hoặc đụng app người dùng. Chưa nghiệm thu toàn hành trình/OS/selector/cache bền.

**Lượt P7 ngày 25–26/10/2026: đã thêm runner trong đúng ba file của plan; 19 kiểm tra host-runner Pass, lint sạch. Ba kịch bản host HTTP → API/PEP → DB/audit đạt; ba scenario route Android có Pass theo các lượt bên dưới.**

Toàn bộ backend integration vừa chạy trên DB local reset sạch: **1089 Pass, 20 Fail, 1 XPASS**, exit 1, 470.54s. Nhóm history API/PEP là **66 Pass, 2 Fail**, cùng lỗi xác nhận sớm BUG-3.25-01. Workbook vẫn **46 Pass, 1 Fail, 6 Pending**; giữ Pending cho ca có tiêu chí chưa được chứng minh dù route Android đạt. 01/03/04 không đổi; 05 giữ draft, chưa chạy review hoặc commit/push.

## 0. Lượt P7 — kết quả mới nhất

### Runner và baseline

- Thêm `tests/e2e/mobile_adherence_history/run_e2e.py`, `test_run_e2e.py`, `README.md`, đúng ba file P7 đã duyệt. `tests` sạch trước khi sửa; tạo nhánh `test/3.25-family-adherence-history-tests` từ HEAD `ac207f4` hiện có, giữ nguyên commit của nhánh redeem. Backend `49f2f11`, frontend fix `46275fa`; không sửa production, contract hoặc Flutter trong lượt này.
- Runner dùng chung guard Supabase local, chọn thiết bị, redaction và Factory của bộ test đang có; không tạo cơ chế phân quyền riêng. API chạy bằng `api_role`; fixture được commit, audit đọc từ kết nối DB mới. Không sửa schema hoặc role/password trong runner.
- Cả emulator và điện thoại luôn build package riêng `vn.drugtime.adherence_e2e` từ bản copy nguồn trong thư mục tạm; từ chối nếu package đó đã tồn tại. Bearer qua stdin vào app-private file, không đưa vào asset/dart-define, vùng chung hoặc output. Relay chỉ giữ patient/status/no-store và cờ so HMAC bearer, không giữ payload lịch sử/token.
- Ba scenario `linked`, `revoke`, `cross_patient`. Revoke đợi phase `history_loaded`, thu hồi `family_sharing` bằng transaction thật rồi mới ghi command atomic. Flutter dùng cùng bearer ở GET kế tiếp; kiểm đúng chuỗi request và allowed/denied audit. Cross-patient giữ denied cho patient Q đã tồn tại.
- Cleanup thử mọi bước dù một bước lỗi: dừng/xóa fixture/gỡ riêng package test, bỏ reverse mapping đã tạo, tắt sharing của link fixture, dừng cây tiến trình API riêng. Audit và người dùng giả giữ ở DB local theo quy tắc append-only, không DELETE/UPDATE access_logs. Cần reset local để làm sạch dữ liệu giả.

### Lệnh và evidence mới

Lệnh từ superproject, trừ DB reset và backend integration chạy từ `backend/`.

| Kiểm tra | Lệnh/phạm vi | Kết quả | Evidence |
|---|---|---|---|
| Gate | `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/gate.py 3.25 test` | exit 0 | `test-continue-gate.log` |
| Android preflight | `backend/.venv/Scripts/python.exe -X utf8 tests/e2e/mobile_adherence_history/run_e2e.py --preflight` | **exit 2 / Pending**, không có Android online; không seed/build/install ở lần preflight | `test-p7-preflight.log` |
| Runner unit | `backend/.venv/Scripts/python.exe -B -X utf8 -m pytest tests/e2e/mobile_adherence_history/test_run_e2e.py -q -p no:cacheprovider --basetemp=work/3.25/scratch/pytest-p7-post-android --junitxml=work/3.25/evidence/test-p7-runner-final.xml` | **19 Pass, 0 Fail/Skip**, exit 0, 1.53s | `test-p7-runner-final.log/xml` |
| Lint/format | `backend/.venv/Scripts/ruff.exe check tests/e2e/mobile_adherence_history --output-format concise`; `ruff format` trên hai file Python mới | exit 0, All checks passed | `test-p7-lint-final.log`, `test-p7-format-final.log` |
| DB sạch | `..\node_modules\.bin\supabase.cmd db reset` | exit 0, toàn migration áp dụng | `test-p7-db-reset.log` |
| Toàn integration | `.venv/Scripts/python.exe -X utf8 -m pytest tests/integration -q -p no:cacheprovider --tb=short --basetemp=../work/3.25/scratch/pytest-p7-integration --junitxml=../work/3.25/evidence/test-p7-integration.xml` | **1089 Pass, 20 Fail, 1 XPASS**, exit 1, 470.54s | `test-p7-integration.log/xml` |
| Host HTTP/PEP/DB | `backend/.venv/Scripts/python.exe -B -X utf8 work/3.25/scratch/p7_host_check.py` | **3/3 scenario đạt, exit 0**, 5 HTTP requests; API/DB local thật, không Android | `test-p7-host-final.log` |
| Emulator | `C:/Android/emulator/emulator.exe -list-avds`; khởi động `Pixel_7 -no-window -no-audio -no-snapshot -port 5580`; runner `--preflight --device emulator-5580` | AVD đã có, boot hoàn tất, preflight exit 0 | `test-p7-avds.log`, `test-p7-emulator-preflight.log` |
| Android lượt đầu | `backend/.venv/Scripts/python.exe -B -X utf8 tests/e2e/mobile_adherence_history/run_e2e.py --device emulator-5580` | linked **Pass**, revoke handshake **Fail**, exit 1; cross_patient chưa chạy ở lượt này | `test-p7-android.log` |
| Android diagnostic | Cùng runner, `--device emulator-5580 --scenario revoke` | revoke **Pass**, 2 GET cùng bearer; allowed→denied audit, exit 0 | `test-p7-android-revoke-diagnostic.log` |
| Android cuối | Cùng runner, `--device emulator-5580 --scenario revoke --scenario cross_patient` | **2/2 Pass**, mỗi scenario 2 GET và audit đúng, exit 0 | `test-p7-android-final.log` |
| Dọn emulator | Kiểm package `vn.drugtime.adherence_e2e` không còn, reverse list rỗng, `adb -s emulator-5580 emu kill` | exit 0, dừng đúng emulator do task tạo | `test-p7-emulator-cleanup.log` |
| Đối chiếu | `backend/.venv/Scripts/python.exe -B -X utf8 work/3.25/scratch/p7_evidence.py --verify` | Spec/task/master khớp, 20 sheet khác và hash 01/03/04 giữ nguyên | `test-p7-final-verify.log` |

Host check thay riêng hai hàm build/mobile-dispatch bằng driver HTTP trong script scratch; vẫn thực thi server lifecycle, seed, revoke, relay, verify_db và disable_link của runner. Đây là kiểm phần host, **không phải E2E Mobile**. Không có thao tác chọn patient từ tab chính, phiên đăng nhập production hoặc sự kiện vòng đời Android trong lần chạy này. Không dùng test server giả trong runner unit để chứng minh quyền DB.

Các lượt Android dùng Flutter helper thật và local API, không thay hai hàm như host check. Linked kiểm 200/no-store, thuốc giả hiện trên production named route, không có thao tác sửa/xác nhận hộ và allowed audit. Revoke chờ phase rồi thu hồi consent commit trước command, refresh cùng bearer → 403, không còn text thuốc kể cả offstage và denied audit. Cross-patient đóng route P, mở Q không liên kết → 403 và không còn dữ liệu P; DB ghi allowed P/denied Q. Auth/medication/consent bootstrap phía Flutter vẫn in-memory theo 04, không dùng đây để chứng minh full graph main()/đăng nhập/selector production.

### Lỗi suite và giới hạn

- Nhóm history/PEP chạy trong full integration: **66 Pass/2 Fail**, không Skip. BUG-3.25-01 vẫn sai `total/taken/counted=0`, `rate=null` khi xác nhận −30 phút; expected 1/1/1 và 100. Cả date/medication đều đỏ, không nới assertion. Giữ severity Medium/owner 3.23 như issue đã có.
- So với `test-contract-integration.xml` trước đây: 18 tên test Fail cũ vẫn còn; hai Fail tăng thêm trong full suite là hai ca family early-confirmation đã biết. 18 lỗi còn lại thuộc alert auth, dose timestamp, notification schema, mobile login validation và profile; không tuyên bố runner mới gây ra hoặc đã sửa chúng. XPASS có sẵn: `test_post_doses_batch_requires_authentication__AC9` với xfail của task 2.10. JUnit ghi 1090 success vì tính cả XPASS; số Pass 1089 lấy từ tổng kết pytest.
- Lượt host đầu đã đạt ba scenario nhưng **exit 1** vì Windows còn giữ backend.log. Đã sửa runner dùng `taskkill /PID <pid-do-runner-tạo> /T /F` để dừng cả launcher và uvicorn con; unit bảo vệ và host check cuối exit 0. Giữ log đỏ `test-p7-host.log`, không gộp thành một lần E2E Pass.
- Lượt runner unit đầu 14 Pass/1 error do quyền thư mục pytest Temp; chuyển basetemp vào scratch, không sửa oracle. Các bản log trước giữ lịch sử; bản cuối 19 Pass mới là kết quả bàn giao. Hai file bytecode phát sinh khi đọc helper cũ đã được dọn/khôi phục; không sửa helper redeem.
- Không chạy lại Mobile unit/widget, unit backend hoặc Postman trong lượt P7 vì không đổi sản phẩm; kết quả retest BUG-3.25-02 và unit/contract bên dưới là evidence lịch sử. Các lượt Android route mới được báo riêng trong bảng.
- Android lượt đầu linked đạt nhưng revoke bị handshake Fail; bản runner khi đó báo generic và đã xóa log tạm, nên không đủ dữ liệu để xác định nguyên nhân. Không quy thành bug sản phẩm hoặc tuyên bố đã sửa tận gốc. Đã bổ sung diagnostic redaction, ưu tiên giữ lỗi Flutter khi watcher cũng lỗi, build đúng integration-test target để tránh đổi qua production main. Không thêm auto-retry/nới assertion/tăng timeout. Revoke sau đó chạy riêng Pass và chạy cùng cross-patient Pass lần nữa. Đây là hai lượt chạy lại có evidence, không xóa lần Fail đầu; độ ổn định vẫn cần theo dõi khi CI chạy dài hạn.

### AC → test → kết quả hiện tại

| AC | Bằng chứng mới / giới hạn |
|---|---|
| AC1 | History/PEP integration và host linked có 200/no-store, đúng patient/liều, allowed audit; Mobile chọn patient Pending. |
| AC2–AC3 | Nhóm integration 66/2 có grouping, timezone, biên, retry client_uuid và Worker race. Xác nhận −30 vẫn Fail ở hai grouping; chưa nghiệm thu toàn AC. |
| AC4–AC5 | Integration cross-patient, hai consent/sharing/unlink và cùng token request kế tiếp đạt; host và Android route revoke/cross-patient kiểm 403, xóa text cũ, cùng bearer và denied audit bằng API/DB thật. Chưa chứng minh selector UI. |
| AC6 | Giữ 17/17 unit/widget Pass của bản fix 46275fa từ lượt trước; Android route read-only/revoke/cross-patient có Pass. OS/offline/logout/cache bền, response muộn trên thiết bị và selector UI thật Pending. |
| AC7 | Integration fail-closed, audit lỗi và denied sau rollback chạy lại đạt trong full suite. |
| AC8 | TC37/38 vẫn Pending vì thiếu oracle/khả năng biểu diễn tỷ lệ đúng giờ riêng và hủy/xung đột/đối soát trong contract. Không tự tạo schema. |
| AC9 | 53 ID giữ nguyên; evidence/README/report/workbook đã cập nhật, chưa nghiệm thu toàn PB21. |

### Workbook và phạm vi

- Đã chạy validate/build/merge bằng script chuẩn dự án, exit 0: `test-p7-testcase-{validate,build,merge}.log`. Giữ **46 Pass/1 Fail/6 Pending**, chỉ một Bug Report `BUG-FADH-20`; Pending TC37/38/39/42/43/44 có actual rỗng. Bổ sung kết quả integration mới và phần Android đã kiểm vào comments của ca Pending, nêu rõ phần chưa chứng minh; giữ evidence unit/widget/Postman cũ cho các ca không chạy lại.
- Đối chiếu spec/task/master và giữ 20 sheet chức năng khác: `test-p7-final-verify.log`. Không có xung đột trạng thái. Artifact Tool recalculation cho 46/1/6/53, thay TC40 tạm trong RAM kiểm công thức đổi 45/2/6/53 rồi khôi phục; không export đè workbook chuẩn. Render và xem vùng TC20, TC39–44, totals và Report; không thấy cắt chữ. `test-p7-workbook-render.log`, `test-p7-workbook-*.png`. Chưa kiểm native Excel.
- Scope cuối ở `test-p7-scope.log`: các file P7 và workbook trong plan; 15 file contract/Postman từ lượt trước vẫn bị checker báo ngoài plan, đã được người dùng cho phép riêng như bản báo cáo trước. Không sửa plan approved/checker để né; không gọi scope là Pass.
- Chưa commit/push/bump gitlink. Thay đổi mới: ba file P7 trong tests, spec/workbook và artifact/evidence work/3.25; workbook docs cập nhật. Delta backend integration, canonical contract/Postman và gitlink có sẵn giữ nguyên. Trạng thái Git chi tiết: `test-p7-git-status.log`.

Các mục 1–6 dưới đây giữ thông tin **lượt retest BUG-3.25-02 trước P7**. Các số liệu “lượt này” bên dưới chỉ nói lượt retest đó; bảng mục 0 là kết quả mới nhất.

**Retest BUG-3.25-02 ngày 25/10/2026 trên frontend `46275fa`: hai ca offline/background đã Pass; cả nhóm family history 17 Pass/0 Fail/0 Skip.** Phản hồi tới muộn không khôi phục lịch sử sau khi app bị vô hiệu truy cập; online/resumed gọi lại và xử lý denied mà không hiện dữ liệu cũ. Kết luận ở mức unit/widget; Android OS và Mobile → API → DB vẫn Pending.

Task chưa đạt toàn bộ AC: BUG-3.25-01 vẫn Fail trong hai ca backend xác nhận sớm. Toàn Mobile còn một Fail đã có trước bản sửa và một Skip có sẵn. Không sửa sản phẩm hoặc assertion trong lượt retest.

## 1. Phạm vi và baseline lượt retest

- Người dùng yêu cầu: “tiếp tục task 3.25, đã sửa lỗi BUG-3.25-02, test lại cho tôi”. Gate cho phép test, 01/03/04 approved; 05 draft. Không đổi approval hoặc sửa artifact đã duyệt.
- Frontend `46275fa`, nhánh `fix/3.25-02-family-history-privacy`, sạch trước/sau test. Commit sửa năm file: app, router, FamilyAdherenceScreen, AdherenceController và widget test; parent `a147ed4` là baseline đỏ của task.
- Backend `49f2f11`; giữ nguyên thay đổi integration từ lượt trước. Contract/Postman và workbook docs đã có thay đổi từ lượt trước; không ghi đè chúng ngoài hai kết quả retest và báo cáo liên quan.
- Chỉ chạy Flutter unit/widget, analyze file sửa, backend unit/contract liên quan và kiểm workbook trong lượt này. Không chạy HTTP Postman, DB reset, integration backend hoặc Android E2E lại vì bản sửa chỉ ở frontend. Kết quả API/DB/Postman trước đây được giữ làm bằng chứng lịch sử, không tuyên bố vừa chạy.
- Flutter dùng fixture thuốc giả; backend unit không dùng dữ liệu thật. Không tạo credential, đổi schema hoặc ghi dữ liệu deploy.
- Áp dụng wf-next, wf-test, wf-git, wf-health-endpoint, wf-testcase và Spreadsheets. File 05 trước retest được lưu ở `evidence/test-bug02-report-before.md` để giữ toàn bộ chi tiết và lệnh cũ.

## 2. Kết quả thực thi trong lượt này

Từ `frontend/mobile/`, tiền tố Flutter là `C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot`.

| Bộ kiểm | Lệnh/phạm vi | Kết quả thực tế | Bằng chứng |
|---|---|---|---|
| Family history | `test --no-pub --reporter json` với ba file `family_adherence_repository_test.dart`, `family_adherence_controller_test.dart`, `family_adherence_screen_test.dart` | **17 Pass, 0 Fail/Skip**, exit 0; event done 12.458s | `test-bug02-family-mobile.jsonl`, `test-bug02-family-mobile-stderr.log` |
| Toàn Mobile | `test --no-pub --reporter json` | **770 Pass, 1 Fail, 1 Skip**, exit 1; event done 92.359s | `test-bug02-mobile-full.jsonl`, `test-bug02-mobile-full-stderr.log` |
| Analyze bản sửa | `analyze --no-pub` trên năm file của commit 46275fa | **No issues found**, exit 0; 12.5s | `test-bug02-analyze.log` |
| Backend history unit/contract | Từ backend: `.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_adherence_history.py tests/unit/test_get_adherence_history.py tests/unit/test_adherence_history_http.py tests/unit/test_sql_adherence.py tests/unit/test_contract_adherence.py -q -p no:cacheprovider --tb=short --junitxml=../work/3.25/evidence/test-bug02-backend-history.xml` | **113 Pass, 2 Fail, 0 Skip**, exit 1; 13.04s, một deprecation warning | `test-bug02-backend-history.log/xml` |

Không cộng testDone hidden/loading vào số test thực thi; ca skipped được đếm riêng. Hai JSONL Flutter mới do PowerShell ghi UTF-16; script kiểm chứng đọc theo BOM. Lệnh đầu trong sandbox bị chặn ghi evidence trước khi chạy test; lần chạy có quyền ghi mới là bằng chứng ở bảng.

### BUG-3.25-02 · Đã xác nhận fix ở widget

- `AC6 QD-29: background removes family health data immediately`: đã có Thuốc A trước trigger; inactive/hidden/paused xóa cả text offstage. Resumed bắt đầu request mới; paused lần nữa rồi cho response thành công tới muộn không khôi phục dữ liệu. Refresh trong paused không phát sinh GET. Resume tiếp theo đọc mới; denied không trả lại dữ liệu cũ.
- `AC6 QD-29: offline removes health data from the actual app`: qua production DrugTimeApp/route, emit offline xóa dữ liệu ngay; emit online gọi đọc mới, chưa hiện lịch sử cũ; denied hiển thị `Không còn quyền xem lịch sử`.
- Ca mới `AC6: unavailable history rejects late reads and reloads on return`: unavailable ban đầu không GET; khi available thì load; vô hiệu trong lúc request đang chạy bỏ response cũ; bật lại gọi đọc mới.
- Các ca đổi patient, logout, refresh denied/network/unauthorized, clear response muộn, sai patient từ repository và màn chỉ đọc đều Pass. Không thêm cache hoặc dùng widget làm bằng chứng về quyền DB.
- TC-FADH-40/41 chuyển Fail → Pass theo log mới; issue cập nhật kết quả retest nhưng vẫn để checklist Android Pending. Chưa nghiệm thu vòng đời OS/capture RAM hoặc cache bền trên thiết bị.

### Fail/Skip còn lại

- Toàn Mobile Fail ở `test/features/family_link/family_tab_screen_test.dart`, test `alert entry displays server unread count and removes it after clear`: fixture dựng FamilyTabScreen thiếu ConsentScope và FamilyLinkScope, sau đó không thấy `1 chưa đọc`. Cùng ca/cùng lỗi đã có trong `implement-resume-mobile-full.jsonl` trước fix; hai file test/screen đó không đổi giữa a147ed4 và 46275fa. Không gán thành hồi quy mới hoặc tự sửa ngoài phạm vi.
- Skip có sẵn: `live_repository_reads_both_groupings_and_observes_revoke`, lý do `Requires local API/DB fixture; run in stage test.` Không thêm hoặc gỡ skip. Đây vẫn là khoảng trống bằng chứng chạy thật trong lượt retest.
- Hai Fail backend đều thuộc `test_confirmed_before_deadline_counts_immediately__AC3[delay0-da_uong-counts0-date|medication]`: expected total/taken/counted=1, rate=100; actual total/taken/counted=0, rate=null. BUG-3.25-01 **Medium**, owner 3.23, còn mở. Bằng chứng API/DB trước đây: `test-contract-history-final.log/xml`; lượt này chỉ tái xác nhận bằng unit.

## 3. AC và vùng rủi ro

| AC | Trạng thái sau retest |
|---|---|
| AC1–AC2 | Giữ bằng chứng lịch sử API/DB, grouping/timezone/biên/idempotency/race. Chưa nghiệm thu toàn AC2 do ca xác nhận sớm. Không chạy lại integration trong lượt này. |
| AC3 | **Fail** BUG-3.25-01; hai ca unit vẫn đỏ. Contract gốc mô tả chỉ liều đã đến giờ còn khác ngoại lệ xác nhận sớm trong AC3 đã duyệt. |
| AC4–AC5 | Nhóm repository/controller/widget liên quan Pass lại; API/DB/Postman cross-patient và request ngay sau thu hồi giữ evidence lịch sử. Chưa chạy lại chúng. |
| AC6 | **17/17 unit/widget Pass**, BUG-3.25-02 đã xác nhận fix trong phạm vi này. Android OS, cache bền và hành trình thật chưa xác minh. |
| AC7 | Giữ bằng chứng cũ PEP/audit fail-closed và denied bền sau rollback; backend unit/contract liên quan chạy lại như bảng. Không dùng unit thay DB. |
| AC8 | TC37/38 Pending: contract chưa mô tả đầy đủ tỷ lệ đúng giờ riêng, xung đột/đối soát; không tự tạo oracle. |
| AC9 | Spec/workbook/report/issue và log đã cập nhật; task chưa hoàn tất do Fail/Pending còn lại. |

Kịch bản cross-patient, consent/sharing/unlink, same bearer request kế tiếp, fail-closed, denied rollback, retry client_uuid và Worker race đã có evidence ở lượt trước. Không thay engine tương tác hoặc logic backend trong bản sửa; không lặp toàn bộ backend/integration ở lượt retest frontend.

## 4. Bằng chứng lịch sử giữ nguyên

- Contract `/adherence` và bảy schema đã khôi phục từ blob `382fb13`, kiểm phần còn lại không đổi: `test-contract-restore.log`, `test-contract-final-audit.log`. 20 ca contract adherence đã Pass trước và nằm trong nhóm unit/contract vừa chạy lại.
- Nhóm integration history cuối đợt trước **66 Pass/2 Fail**, `test-contract-history-final.log/xml`. Hai Fail là xác nhận sớm. Full backend unit trước **1353 Pass/32 Fail**; full integration trước **1083 Pass/18 Fail/1 XPASS**. Không gọi đây là kết quả mới.
- HTTP Postman trước **9 lượt, 14 request, 75 assertion, 0 failure**, có DB audit, cùng bearer thu hồi request kế tiếp; `test-postman-live.log`, `test-postman-live-summary.json`. Không publish workspace; bearer tạm đã xóa ở lượt trước.
- Contract/Postman ngoài plan cũ là phần người dùng đã yêu cầu trực tiếp ở lượt trước; chi tiết lint/guard/HTTP/schema và các lỗi suite ngoài task nằm trong bản 05 lưu trước retest.

## 5. Bộ test case Excel

- Spec `testcases.json`; file task `testcases.xlsx`; tổng `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`. Giữ nguyên 53 ID và cấu trúc sheet; chỉ cập nhật TC40/41 và evidence những ca family được retest.
- **53 ca: 46 Pass, 1 Fail, 6 Pending**. Một dòng Bug Report còn `BUG-FADH-20` tương ứng BUG-3.25-01. TC40/41 không còn là lỗi mở trong Bug Report; lịch sử đỏ giữ ở log/issue/bản báo cáo cũ.
- Người dùng đã chọn **“Cập nhật thành Pass theo retest”** để thay Fail cũ của TC40/41 trong file tổng. Cảnh báo merge hai dòng là thay kết quả có chủ ý theo lựa chọn này, không phải xung đột chưa giải quyết.
- Validate/build/merge bằng `.agents/scripts/testcase_xlsx.py`, log `test-bug02-testcase-{validate,build,merge}.log`. Đối chiếu spec/task/master, chỉ còn một bug và 20 sheet chức năng khác giữ nguyên: `test-bug02-final-verify.log`.
- Các Pass/Fail ngoài nhóm retest giữ kết quả lịch sử với log nguồn riêng; không tuyên bố mọi test case chạy lại trong phiên này. Pending TC37/38 (AC8), TC39/42/43/44 (OS/cache bền/Android E2E); actual vẫn rỗng.
- Render và recalculation bằng Artifact Tool: tổng 46/1/6/53; đổi TC40 thành Fail trong bộ nhớ cho 45/2/6/53 rồi khôi phục, không export đè workbook chuẩn. Đã xem ảnh vùng TC40/41 và Report: nội dung đọc được, không thấy cắt chữ; ảnh tổng cũng được render. Log `test-bug02-workbook-render.log`. Không kiểm native Excel.

## 6. Phạm vi và bàn giao

- `gate.py 3.25 test` exit 0 (`test-bug02-gate.log`). `scope.py 3.25 --stage test` exit 1, đúng **15 file contract/Postman từ lượt trước** đã được người dùng cho phép (`test-bug02-scope.log`); backend integration và workbook đúng vùng. Frontend fix là baseline đã commit để retest, không có file frontend chưa commit. Không coi scope là Pass hoặc sửa checker/plan approved để né.
- Chưa commit/push/bump gitlink trong lượt này. Frontend bản fix đã có commit và sạch. Delta có sẵn: backend integration, contract, Postman local, workbook docs; cập nhật mới ở work/3.25 và workbook theo kết quả retest. 01/03/04 giữ nguyên hash.
- Chỉ đề xuất lưu khi người dùng yêu cầu: `git -C docs add -- "Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx"` và commit `test(adherence): record family history privacy retest`; superproject `git add -f -- work/3.25/05-test-report.md work/3.25/issues/BUG-3.25-02.md work/3.25/testcases.json work/3.25/testcases.xlsx work/3.25/evidence` rồi commit riêng, không stage scratch. Không bump submodule tới commit chưa push.

## Bước tiếp theo

1. P7 đã có runner, kiểm host và các kết quả route Android ở mục 0. Cần theo dõi handshake Fail đầu chưa rõ nguyên nhân; khi tái kiểm, chạy preflight và README, giữ cả log Fail lẫn Pass. Emulator do task tạo đã dừng; không dùng app thật hoặc emulator của task khác.
2. AC6 còn thao tác OS/offline/logout/cache bền, response muộn trên thiết bị và đường chọn patient từ UI chính. BUG-3.25-02 chỉ được xác nhận fix ở unit/widget cho offline/background đến thời điểm này. TC39/42/43/44 giữ Pending dù các route Android đã có Pass.
3. Owner 3.23 xử lý BUG-3.25-01 và chốt contract/ngoại lệ xác nhận sớm, cùng oracle AC8 (TC37/38). Giữ hai ca integration đỏ; không sửa sản phẩm trong stage test. 18 Fail suite ngoài history và một Fail Mobile lịch sử cần task sở hữu xử lý.
4. Giữ 05 draft; người duyệt có thể chấp nhận báo cáo cùng giới hạn bằng `python .agents/scripts/gate.py approve 3.25 test`. Agent không chạy approve, không chuyển review; approval không biến Fail/Pending thành Pass. Quy tắc dừng tại `.agents/skills/wf-test/SKILL.md`, bước 8: “Dừng ở đó.”
5. Nếu cần lưu: `git -C tests add -- e2e/mobile_adherence_history/run_e2e.py e2e/mobile_adherence_history/test_run_e2e.py e2e/mobile_adherence_history/README.md`, commit `test(adherence): add isolated Android history runner` với footer `Refs: 3.25`; commit workbook docs và work/3.25 riêng, chỉ khi người dùng yêu cầu. Superproject hiện nhánh fix/3.25-02; cần chọn nhánh task thích hợp trước commit artifact, không bump tới commit chưa push. Không stage scratch/bytecode.
6. Tiếp tục bằng `continue 3.25`, đọc gate và mục 0 báo cáo này trước. Cập nhật 26/10/2026, Codex; bàn giao theo wf-handoff, chưa commit/push.
