---
task: 3.25
stage: review
status: draft
---

# 3.25 · Review kiểm thử lịch sử tuân thủ người thân

## 1. Kết luận

**Chưa đạt — 0 Critical, 3 High, 0 Medium, 0 Low.** Chưa đủ điều kiện nghiệm thu toàn PB21 hoặc chuẩn bị PR sẵn sàng merge. Gate đã xác nhận requirement/plan/implement/test approved; approval báo cáo không biến Fail/Pending thành Pass.

Bản này thay review ngày 25/10 theo checkout và evidence ngày 26/10/2026. Giữ bản cũ tại `evidence/review-refresh-before-20261026.md`. R2 cũ (contract/PEP chưa chạy được) và R4 cũ (steps TC02/06/35 sai) được đóng. R1 giữ; R3 thu hẹp thành khoảng trống AC6 trên thiết bị; R5 tách riêng entrypoint PB21 còn thiếu. BUG-3.25-01 vẫn có severity sản phẩm Medium và owner 3.23; việc AC3 chưa đạt là High theo wf-review, không đổi severity issue thành High.

## 2. Phạm vi đã review

Đã đọc AC1–AC9 và bảng file/checklist của 03; đọc toàn bộ delta riêng 3.25 gồm unit backend, integration bổ sung, năm file test/helper Flutter, bản fix privacy bốn file production và widget test, ba file runner Python/README, contract khôi phục và 14 file Postman. Đọc thêm đường route/main, màn/controller/repository gia đình và test PEP hiện có. Workbook được đối chiếu chỉ đọc với spec và baseline, không sửa.

| Repo | HEAD / cách đối chiếu | Phạm vi |
|---|---|---|
| backend | `49f2f11`; `git -C backend diff main...HEAD`, `diff d88af5c..HEAD`, `diff HEAD` | Unit của task đã commit; 150 dòng thêm/3 dòng xóa integration còn working tree. Acceptance redeem trong main diff thuộc baseline 3.15. |
| frontend | `46275fa`; `git -C frontend diff b24ee68..HEAD` | Test commit a147ed4 và fix privacy 46275fa; working tree sạch. Delta task lưu tại `evidence/review-refresh-frontend-task.diff`. |
| tests | `ac207f4`; đọc ba file untracked `e2e/mobile_adherence_history/*` | Runner mới 3.25; redeem và hai pyc đã có ở HEAD là baseline, không phải file mới của lượt này. |
| api_contract | `585e99c`; `git -C api_contract diff HEAD`; so JSON với `382fb13` | Khôi phục đúng `/adherence` và bảy schema nguồn; không đổi JSON của endpoint/schema khác. Chưa commit. |
| docs | `3077e2e`; so workbook working tree với spec/task workbook và snapshot trước P7 | 53 ID và mọi trường case khớp; 20 sheet chức năng khác giữ nguyên theo script đối chiếu. Chưa commit delta retest. |
| superproject | `fix/3.25-02-family-history-privacy`; Postman/work | Review chỉ ghi 06, evidence và scratch. Không sửa 01/03/04/05, code, contract, collection, workbook hoặc gitlink. |

`main...HEAD` được kiểm kê ở cả năm repo. Frontend main local cũ nên diff bao gồm 70 file/7442 dòng thêm của baseline UI/demo; không tuyên bố đã review độc lập toàn bộ phần baseline này trong lượt hiện tại. Đọc delta task so với b24ee68 và các đường production liên quan; không dùng nhận xét này để kết luận Đạt cho toàn nhánh rộng hơn. Các thay đổi kế thừa cần tách base trước PR.

### Phạm vi và phát sinh

- `scope.py 3.25 --stage implement`: exit 1, **19 file ngoài phạm vi**. Integration backend và ba runner thuộc stage test nên bị checker implement liệt kê thêm.
- `scope.py 3.25 --stage test`: exit 1, **15 file ngoài phạm vi**: contract và 14 file Postman, đúng delta mà 05 approved đã ghi nhận được người dùng cho phép ở lượt trước.
- `scope.py 3.25 --stage review`: exit 1, **20 file ngoài phạm vi**, gồm toàn bộ working tree sản phẩm/test/workbook có sẵn. Không có file ngoài work được review này sửa.
- Log: `review-refresh-scope-implement.log`, `review-refresh-scope-test.log`, `review-refresh-scope.log`. Không gọi scope là Pass, không sửa checker/plan approved, không commit/stash/restore để che thay đổi. Không xin lại quyền sửa các file cũ vì lượt review chỉ đọc chúng. Cần xử lý phạm vi/base rõ ràng trước PR; gate vẫn là nguồn trạng thái giai đoạn.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1/4/5/7 có integration thật; AC2 được phủ nhưng ngoại lệ sớm của AC3 còn Fail. AC6 widget Pass, Android route có Pass, vẫn thiếu native/selector/cache. AC8 nêu rõ phần contract chưa biểu diễn, đúng nhánh báo giới hạn trong AC. AC9 có workbook/truy vết, không đồng nghĩa PB21 hoàn tất. |
| Phạm vi | Task test không tự sửa backend sản phẩm. Fix privacy và khôi phục contract là delta được ghi nhận từ các lượt riêng. Ngoại lệ scope được giữ nguyên như trên; committed diff được đọc riêng vì scope chỉ xét working tree. |
| Contract | Unit contract chạy lại trong nhóm backend không còn collection error. Path/bảy schema khớp blob 382fb13, phần JSON khác khớp HEAD. Câu “chỉ trả liều đã đến as_of” vẫn trái ngoại lệ xác nhận sớm AC3 (R1); không coi khôi phục schema là đã chốt lại nghiệp vụ này. |
| Bất biến kiến trúc | GET gọi AccessGuardAdapter → access.authorize trước reader; target patient được chuyển vào PEP; quyền đọc từ DB mỗi request. Allowed audit nằm trong giao dịch, chỉ trả sau commit; denied writer riêng. Route có scope/registry/no-store. Không thêm import giữa module, schema, engine tương tác hoặc đường client→Supabase. |
| Bảo mật | Runner chặn môi trường ngoài local, dùng api_role; package Android riêng, không ghi đè package có sẵn. Bearer qua stdin vào app-private, không asset/dart-define/output; relay không giữ payload hoặc bearer thô. Scan JWT trong log mới không thấy pattern raw. Đây là kiểm tra có phạm vi, không phải bảo đảm không còn mọi loại secret trong toàn repo. |
| Xử lý lỗi | PEP/audit lỗi fail-closed, denied còn sau rollback có evidence integration. Runner cleanup thử các bước còn lại khi một bước lỗi; không DELETE/UPDATE audit, giữ fixture local và tắt sharing. Handshake revoke Fail đầu chưa rõ nguyên nhân được giữ, không tuyên bố đã sửa tận gốc hoặc che bằng retry. |
| Hiệu năng | Thay đổi backend là test; không thêm query production/N+1. History reader hiện dùng một SELECT snapshot; không có benchmark/load test trong lượt review. |
| Chất lượng test | Oracle số cụ thể cho biên −30/+30/+120 và +1µs; kiểm GET không đổi dose log, cùng bearer thu hồi, audit, fail-closed, Worker race. Flutter kiểm xóa UI/offstage và bỏ response muộn bằng generation. Runner kiểm guard/redaction/cleanup. Harness route có bootstrap in-memory và mở bằng Navigator nên không chứng minh full login/selector/main graph. Không thêm skip/xfail hoặc nới assertion. |
| Dễ đọc/nhất quán | Các file task Python qua Ruff; diff whitespace cả committed/working của năm repo sạch. Không thấy debug log sức khỏe/credential mới trong delta đã đọc; giữ các hạn chế nguồn ở README/report. |
| 04/05 so với log | 04 là snapshot trước privacy fix; 05 mới hơn và ghi rõ retest. Đếm XML/JSONL khớp số nêu dưới, tách hidden loading/skip/XPASS. Không sửa câu Bước tiếp theo cũ trong artifact approved. |

### Checklist wf-health-endpoint

PEP có sẵn được dùng trước reader; đối chiếu patient/consent/link/sharing mỗi request; không cache quyền; allowed audit fail-closed, denied giao dịch riêng; dữ liệu tối thiểu và no-store; 401/403/422/500 theo contract; registry route có test. Nhóm integration history/PEP trong log P7 gồm self/family success, unlinked, hai consent, sharing off, tamper Q, thu hồi cùng token, audit lỗi/rollback và auth — các ca quyền này Pass. Hai ca Fail thuộc tính tỷ lệ sớm, không phải bằng chứng lộ dữ liệu. Không dùng widget hoặc HTTP 403 riêng lẻ để suy audit DB đã đúng.

### Kiểm tra thực sự chạy trong lượt review này

Đường log dưới đây tương đối từ `work/3.25/evidence/`. Python backend là `.venv/Scripts/python.exe`; từ superproject thêm tiền tố `backend/`.

| Kiểm tra / lệnh | Kết quả | Evidence |
|---|---|---|
| `python -X utf8 .agents/scripts/gate.py 3.25 review` | exit 0 | `review-refresh-gate.log` |
| Từ backend: `python -B -X utf8 -m pytest tests/unit/test_get_adherence_history.py tests/unit/test_adherence_history.py tests/unit/test_adherence_history_http.py tests/unit/test_sql_adherence.py tests/unit/test_contract_adherence.py tests/unit/test_access_authorize.py tests/architecture/test_health_route_enforcement.py -q -p no:cacheprovider --tb=short --junitxml=../work/3.25/evidence/review-refresh-backend.xml` | **144 Pass, 2 Fail**, exit 1; 27.12s; 1 deprecation warning | `review-refresh-backend.log/xml` |
| Từ mobile: `dart flutter_tools.snapshot test --no-pub --reporter json test/features/family/family_adherence_repository_test.dart test/features/family/family_adherence_controller_test.dart test/features/family/family_adherence_screen_test.dart` | **17 Pass, 0 Fail/Skip**, exit 0; event done 24.468s | `review-refresh-mobile.jsonl` |
| Từ root: `python -B -X utf8 -m pytest tests/e2e/mobile_adherence_history/test_run_e2e.py -q -p no:cacheprovider --basetemp=work/3.25/scratch/pytest-review-refresh-runner --junitxml=work/3.25/evidence/review-refresh-runner.xml` | **19 Pass, 0 Fail/Skip**, exit 0; 1.77s | `review-refresh-runner.log/xml` |
| `python -B -X utf8 .agents/scripts/testcase_xlsx.py validate 3.25` | exit 0; **53 ca: 46 Pass/1 Fail/6 Pending** | `review-refresh-testcase-validate.log` |
| `python -B -X utf8 work/3.25/scratch/p7_evidence.py --verify` | exit 0; XML/spec/workbook, 20 sheet khác, hash 01/03/04 không đổi | `review-refresh-evidence.log` |
| `python -B -X utf8 work/3.25/scratch/review_refresh_audit.py` | exit 0; đếm độc lập log mới, so mọi field case JSON/workbook, contract blob, trạng thái Git/whitespace; manifest 105 file | `review-refresh-audit.log`, `review-refresh-input-hashes.json` |
| `backend/.venv/Scripts/ruff.exe check tests/e2e/mobile_adherence_history backend/tests/unit/test_get_adherence_history.py backend/tests/integration/test_adherence_history_api.py --output-format concise` | exit 0, All checks passed | `review-refresh-lint.log` |
| `rg -n 'familyAdherence|FamilyAdherenceRouteArgs|/family/adherence' frontend/mobile/lib` | Chỉ khai báo/nối availability/observer/route, không có caller mở lịch sử trong UI | `review-refresh-entrypoint.log` |

Dart/tool dùng đường tuyệt đối `C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe` và `C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot`. Mọi output thô được giữ; không dùng log unit để chứng minh integration đã chạy lại.

### Evidence lịch sử đã đọc và đếm lại, không chạy lại trong review

| Bộ | Kết quả / giới hạn |
|---|---|
| P7 full integration | `test-p7-integration.log/xml`: **1089 Pass, 20 Fail, 1 XPASS**. XML có 1090 success vì chứa XPASS. History API/PEP **66 Pass, 2 Fail**, cả hai là early-confirmation date/medication. 18 tên Fail ngoài history giữ từ suite trước, không gán thành hồi quy mới của 3.25. |
| Android route | `test-p7-android.log`: linked Pass, revoke handshake Fail, cross chưa chạy; `test-p7-android-revoke-diagnostic.log`: revoke Pass; `test-p7-android-final.log`: revoke/cross_patient Pass. Không có một lần all-three xanh trong cùng invocation; có evidence Pass riêng cho cả ba scenario, revoke hai lần Pass. Emulator task tạo đã dọn theo `test-p7-emulator-cleanup.log`. |
| Postman live local | `test-postman-live-summary.json` và log: **9 lượt, 14 request, 75 assertion, 0 failure**; local API/DB thật, không mock/publish/report events. Đây là evidence cũ, không chạy lại CLI hoặc HTTP trong review. |
| Mobile full trước | `test-bug02-mobile-full.jsonl`: **770 Pass, 1 Fail, 1 Skip**; ca family unread fixture thiếu scope vẫn là lỗi suite đã được 05 ghi. Review chỉ chạy lại ba file targeted, không tuyên bố full suite xanh. |

Không reset DB, khởi động API/emulator, chạy native E2E, chạy toàn backend/full Flutter hoặc Postman live trong lượt này vì các blocker đã rõ và không đổi sản phẩm.

### Workbook và truy vết

- JSON, task workbook và master có đúng **53 ID, 46 Pass, 1 Fail, 6 Pending**; mọi trường metadata/actual/status/comments khớp. 47 ca đã thực thi có dẫn chứng tồn tại; các ca backend đối chiếu tên test/XML và ca widget đối chiếu JSONL. Fail TC20 có `BUG-FADH-20` ánh xạ `BUG-3.25-01`; không còn Bug Report mở cho TC40/41 đã retest Pass.
- TC40/41 nêu rõ chỉ là widget; không biến hai Pass này thành nghiệm thu OS. TC37/38/39/42/43/44 Pending, actual rỗng; comments mô tả phần route Android đã đạt và phần còn thiếu.
- R4 cũ đã sửa: TC02 không tạo liên kết; TC06 có request P rồi tamper Q cùng token; TC35 thực hiện POST batch trước −30 và kiểm không tạo log. Test integration tương ứng Pass trong evidence P7.
- 20 sheet chức năng khác được script đối chiếu với snapshot trước P7. Không export hoặc ghi workbook trong review. Layout/recalculation giữ evidence `test-p7-workbook-render.log` của stage test; chưa render lại/native Excel trong lượt này, không coi kiểm cell cấu trúc là chứng minh layout.

## 4. Phát hiện

| ID / mức | Vị trí | Vấn đề và tác động | Đề xuất |
|---|---|---|---|
| R1 · High · còn mở | `backend/tests/unit/test_get_adherence_history.py:197`; `backend/tests/integration/test_adherence_history_api.py:715`; `backend/src/drugtime/modules/adherence/domain/history.py:153`; `backend/src/drugtime/modules/adherence/adapters/outbound/sql_adherence.py:77` | **AC3 sai với xác nhận sớm hợp lệ.** Lịch 08:00, xác nhận/đọc 07:30: expected total/taken/counted=1, rate=100; actual 0/null. Hai unit Fail lại trong review; hai ca DB thật Fail ở P7. Contract khôi phục và test cũ còn loại liều tương lai dù đã xác nhận, trái quyết định 01. | Owner 3.23 sửa đồng bộ domain/SQL, contract và kỳ vọng cũ theo workflow bug; giữ regression đỏ trước/xanh sau. Không đưa liều tương lai chưa xác nhận vào mẫu số. Sau fix, mở lại test 3.25 và chạy unit/integration hai grouping, timezone, biên/idempotency/race/PEP. |
| R3 · High · đã thu hẹp | `work/3.25/testcases.json:671`, `:726`, `:742`; `tests/e2e/mobile_adherence_history/README.md` mục Giới hạn; `frontend/mobile/integration_test/adherence_history_e2e/history_test.dart:23` | **AC6 chưa đủ bằng chứng trên thiết bị.** Widget đã chứng minh background/offline/logout/late-response sau fix và route Android có 403/clear, nhưng chưa có thực thi OS lifecycle/offline/logout, cache bền và response muộn trên thiết bị. Native harness chỉ chạy linked/revoke/cross_patient. Đây là khoảng trống nghiệm thu vùng rủi ro, không khẳng định bug privacy vẫn tồn tại. | Mở lại test 3.25 khi chuẩn bị chạy: bổ sung thao tác OS thật, mất/kết nối lại mạng, logout và kiểm không lưu/khôi phục dữ liệu sau response muộn/restart; giữ Pending đến khi có log. Dùng package riêng, API/PEP/DB thật; không dùng widget hoặc absence-of-Text thay chứng cứ storage. |
| R5 · High · tách từ khoảng trống hành trình | `frontend/mobile/lib/app/router.dart:229`; `frontend/mobile/lib/features/family_link/presentation/screens/family_tab_screen.dart:104`; `frontend/mobile/integration_test/adherence_history_e2e/history_helpers.dart:140` | **Thiếu entrypoint lịch sử người thân trong UI production hiện tại.** Tìm toàn lib không có caller của AppRoutes.familyAdherence/FamilyAdherenceRouteArgs hoặc literal route; tab Người thân chỉ mở alert/mã/liên kết. Test bỏ qua bước chọn bệnh nhân bằng pushNamed trực tiếp, nên Pass route chưa chứng minh người dùng vào được PB21 từ UI. | Owner 3.24 xác minh và cung cấp entrypoint/chọn patient thật theo thiết kế được duyệt. Sau đó test 3.25 đi từ tab Người thân → chọn P → lịch sử, đổi Q và thu hồi. Nếu có entrypoint ngoài checkout, nhận đúng baseline và kiểm lại; không dựng selector giả để nghiệm thu. |

R2 cũ **đã đóng**: schema chuẩn có lại trong working tree; integration 66/2 chạy qua contract và phủ quyền/thu hồi/audit. Điều này không giải quyết xung đột nghiệp vụ R1. R4 cũ **đã đóng** qua steps/spec/workbook và evidence API tương ứng. Lượt handshake đỏ chưa rõ nguyên nhân được giữ như giới hạn độ ổn định; không suy lỗi sản phẩm mới hoặc thêm severity khi chưa có căn cứ.

AC8/TC37–38 tiếp tục chưa nghiệm thu phần nghiệp vụ chưa đặc tả, nhưng AC8 đã cho phép báo rõ giới hạn khi contract không biểu diễn được; không tự tạo field/công thức và không đếm thành lỗi mới.

## 5. Mô tả PR

Chưa soạn mô tả PR sẵn sàng merge vì còn High, theo wf-review bước 7. Chưa commit/push/mở PR/bump gitlink. Khi xử lý xong phải review lại delta mới, chốt baseline để tránh kéo lịch sử redeem/UI demo không thuộc task.

Thứ tự dự kiến: phụ thuộc contract 3.23 → backend sản phẩm 3.23 → frontend sản phẩm 3.24/privacy → các test backend/frontend/tests 3.25 → docs workbook → superproject. Phải xác nhận commit submodule đã push trước khi bump. Mô tả PR sau này phải nêu rõ kết quả suite đỏ ngoài task và giới hạn còn được chấp nhận, không ghi toàn bộ suite Pass.

## 6. Ghi chú cho quy trình và bàn giao

- 05 và review cũ được đọc khi khôi phục trước delta, nên đây không phải blind review hoàn toàn. Đã kiểm nguồn, chạy lại targeted, đếm XML/JSONL và so workbook/contract độc lập; không che thứ tự này.
- User báo approved test; agent chỉ chạy gate xác minh, không chạy approve/reopen hoặc sửa metadata approved. 01/03/04/05 giữ nguyên theo manifest; câu Bước tiếp theo cũ trong approved artifact là lịch sử.
- Sandbox chặn lần đầu ghi evidence; đã dùng escalation đúng lệnh, không sửa ACL hoặc đổi nơi để né. Một lệnh đọc JSON bằng Python -c lỗi quoting PowerShell, đã đọc lại bằng ConvertFrom-Json; lỗi này không phải kết quả test sản phẩm.
- Skill áp dụng: wf-next, wf-review, wf-git, wf-health-endpoint; postman:api-engineer để tái sử dụng contract/collection/evidence; Spreadsheets cho đối chiếu chỉ đọc; wf-handoff để giữ thông tin tiếp tục. Không phát sinh nhu cầu API workspace/network hoặc thay đổi schema.

Các thay đổi chưa commit được giữ nguyên: backend integration; api_contract/openapi.json; ba file runner trong tests; workbook docs; 14 file Postman ở superproject; work/3.25 (bị ignore) và năm gitlink khác HEAD superproject. Frontend sạch ở mức file, commit fix 46275fa đã là baseline để test. Chi tiết branch/SHA/file ở `review-refresh-audit.log`, superproject ở `review-refresh-superproject-status.log`.

Nếu người dùng yêu cầu lưu, chỉ stage có chủ đích sau khi kiểm staged diff:

```powershell
# Artifact/evidence; không stage scratch hoặc gitlink cùng lệnh này.
git add -f -- work/3.25/01-requirement.md work/3.25/03-plan.md work/3.25/04-impl-notes.md work/3.25/05-test-report.md work/3.25/06-review.md work/3.25/testcases.json work/3.25/testcases.xlsx work/3.25/evidence
git commit -m "docs: refresh task 3.25 review findings" -m "Refs: 3.25"
# Code/test/workbook còn dở: commit riêng từng repo, không commit scratch.
git -C backend add -- tests/integration/test_adherence_history_api.py
git -C backend commit -m "test(adherence): verify family history integration boundaries" -m "Refs: 3.25"
git -C tests add -- e2e/mobile_adherence_history/run_e2e.py e2e/mobile_adherence_history/test_run_e2e.py e2e/mobile_adherence_history/README.md
git -C tests commit -m "test(adherence): add isolated Android history runner" -m "Refs: 3.25"
git -C docs add -- "Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx"
git -C docs commit -m "test(adherence): record family history retest evidence" -m "Refs: 3.25"
```

Contract/Postman cần đối chiếu phạm vi và commit riêng khi được yêu cầu. Sau mỗi commit, chỉ push khi người dùng yêu cầu: `git -C <repo> push -u origin <nhánh-task>`; kiểm `git -C <repo> branch -r --contains HEAD`, rồi mới đề xuất bump superproject. Không áp dụng lệnh placeholder nguyên văn. Các lệnh trên chỉ được soạn, chưa chạy.

## Bước tiếp theo

- **Đang chờ người dùng/owner sản phẩm**, review đã hoàn tất ở mức phát hiện nhưng vẫn draft và kết luận Chưa đạt. Owner 3.23 xử lý R1; owner 3.24 xử lý/xác minh R5; QA hoàn tất R3 khi tiền đề sẵn sàng.
- Khi sẵn sàng chạy lại, người duyệt dùng `python .agents/scripts/gate.py reopen 3.25 test`; nếu phải sửa test/helper thuộc implement thì mở lại implement trước. Không sửa approved artifact trực tiếp. Phiên tiếp tục chạy gate trước; không mở lại implement 3.25 để sửa domain/SQL ngoài phạm vi task test.
- Sau khi test được duyệt lại, cập nhật 06 theo bằng chứng mới, kiểm cả R1/R3/R5 và scope. Chỉ khi mọi High được xử lý mới đề nghị `python .agents/scripts/gate.py approve 3.25 review`. Agent không chạy lệnh này.
- Nếu tiếp tục chỉ rà kết luận hiện tại, gõ `xem review 3.25`; không dùng continue để lặp lại các test vừa chạy khi chưa có code/evidence mới.
- Cập nhật: **2026-10-26, Codex**. Manifest đầu vào giữ ở `evidence/review-refresh-input-hashes.json`; kiểm bàn giao cuối ở `evidence/review-refresh-final-check.log`.
