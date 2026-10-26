---
task: 3.25
stage: implement
owner: phucnguyenngoc
started_at: 2026-10-24 22:22 +0700
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-25 11:37 +0700
content_hash: sha256:53df572a97923635
inputs:
  01-requirement.md: sha256:717a7d0a0b7c604b
  03-plan.md: sha256:13b8c04b8e364a8a
---

# 3.25 · Implement — tiếp tục sau review

## 1. Tiến độ hiện tại

Lượt 25/10/2026: người dùng đã mở lại implement. Gate cho phép thực hiện; 01/03 vẫn approved. Tiếp tục P3/P4 sau khi tìm và nhận đúng UI 3.24 đã merge. Chỉ thêm năm file test frontend đúng plan; không sửa production, contract, migration hoặc test integration Python. Giữ kết quả Fail để chuyển lỗi về task sản phẩm.

| Bước | Trạng thái | Kết quả / điều còn thiếu | Evidence |
|---|---|---|---|
| P1 | Xong; đã kiểm lại nguồn phụ thuộc | UI 3.24 thực sự đã merge PR #40; frontend nhận main `b24ee68` gồm #40/#42. Contract #13 cũng merged nhưng main vẫn thiếu adherence do mất nội dung ở merge. Đã xác định commit gây mất. | `implement-resume-gate.log`, `implement-resume-ui-pr.log`, `implement-resume-contract-pr.log`, `implement-resume-*-fetch.log`, `implement-resume-*-checkout.log`, `implement-resume-audit-final.log` |
| P2 | Xong phần test; BUG-3.25-01 còn mở | 24 ca backend bổ sung từ lượt trước giữ nguyên. Kiểm lại P6 trong phiên vẫn có hai Fail −30 phút; không sửa production để làm xanh. | `implement-P2.log` (24/10), `implement-resume-backend.log/xml` (25/10) |
| P3 | Đã viết/chạy repository và controller test; chưa nghiệm thu toàn AC6 | 3 repository + 6 controller đều Pass: query/caller bearer, không trả cache khi offline/403, đổi patient, response muộn, clear invalidates. Widget sự kiện background/offline còn Fail BUG-3.25-02; không coi test gọi `clear()` là chứng minh app tự gọi clear ở các sự kiện này. | `implement-resume-mobile-full.jsonl`, `implement-resume-audit-final.log` |
| P4 | Đã viết widget và chuẩn bị hai file Flutter E2E; chưa nghiệm thu toàn hành trình | Widget: 5 Pass, 2 Fail (background/offline). Read-only, refresh 403/network, đổi patient và logout app Pass. Flutter E2E helper/test qua analyze, chưa chạy thiết bị. Mở route production bằng Navigator, chưa chứng minh thao tác chọn patient từ UI chính. | `implement-resume-mobile-full.jsonl`, `implement-resume-mobile-analyze-final.log` |
| P5 | Chờ giai đoạn test lại | Các kết quả integration của 05 cũ không thay thế lần chạy mới; chưa mở rộng/chạy lại integration ở lượt implement này. Contract hiện vẫn chặn wire assertions. | `05-test-report.md` là báo cáo lượt trước, không sửa approved |
| P6 | Đã kiểm lại unit/route; contract tiếp tục chặn | **88 Pass, 2 Fail, 1 collection error**, exit 1. Lỗi collection `/adherence`; hai Fail BUG-3.25-01. Không sửa test contract hoặc thay bằng generated OpenAPI. AC8 chưa nghiệm thu. | `implement-resume-backend.log`, `implement-resume-backend.xml` |
| P7 | Chờ giai đoạn test lại | Chưa viết Python runner hoặc chạy Android/API/DB. Hai file Flutter chuẩn bị ở P4 có protocol dưới mục 4 để runner sử dụng. | Không có evidence E2E thực thi trong lượt này |
| P8 | Đầu ra test trước đã lưu; cần cập nhật ở lượt test tiếp theo | 45 ca cũ: 24 Pass/1 Fail/20 Pending; workbook docs đã commit `3077e2e` theo yêu cầu. Chưa đưa kết quả widget mới vào workbook ở giai đoạn implement của task L; cần sửa R4 và kết quả AC6 khi test được mở lại. | `commit-workbook*.log`, `review-scope-after-workbook-commit.log`, `05-test-report.md` |

P1/P2 hoàn tất điều kiện bước; P3/P4 đã có đầy đủ năm file dự kiến nhưng còn lỗi sản phẩm/phần chưa chạy, chưa đánh dấu hoàn tất nghiệm thu. P6 chặn contract; P5/P7/P8 cần lượt test tiếp theo. Không chuyển giai đoạn trong lượt này.

## 2. File và Git

### File thay đổi mới trong lượt này

| Submodule | File | Nội dung |
|---|---|---|
| frontend | `mobile/test/features/family/family_adherence_repository_test.dart` | 3 ca dùng production repository/API client với HTTP mock: bearer/query mỗi request, 403 không lấy cache, network không lấy cache, response sai patient. |
| frontend | `mobile/test/features/family/family_adherence_controller_test.dart` | 6 ca dùng production controller: refresh denied/network/401, vô hiệu response cũ, đổi patient, clear, mismatch patient. Exports fixture repository chỉ dùng trong test. |
| frontend | `mobile/test/features/family/family_adherence_screen_test.dart` | 7 ca widget trên production screen/app: chỉ đọc, refresh lỗi, đổi patient, background, offline, logout. Hai ca QD-29 giữ assertion Fail. |
| frontend | `mobile/integration_test/adherence_history_e2e/history_helpers.dart` | Fixture private của package test riêng, session chỉ RAM, route/app/repository production + HTTP local, protocol chờ host thu hồi, cleanup. |
| frontend | `mobile/integration_test/adherence_history_e2e/history_test.dart` | Thiết kế linked/revoke/cross_patient bằng route thật, cùng bearer, kiểm GET/200/403 và xóa dữ liệu hiển thị; chưa thực thi E2E. |

Backend `tests/unit/test_get_adherence_history.py` là thay đổi lượt implement trước, đã commit `49f2f11`; không sửa trong lượt này. Frontend mới có năm file untracked ở trên, chưa commit. Không đổi pubspec/lock/metadata hoặc dependency package; chạy Flutter bằng `--no-pub` với dependency cache có sẵn.

### Nhận phụ thuộc đã merge

- Frontend trước lượt tiếp tục: nhánh `test/3.15-redeem-flow-tests`, HEAD `f9ff26350e65f790ae60e26f0da7c23acb7aa4a8`. Nhánh cũ giữ nguyên để không mất commit redeem.
- Đã fetch và tạo nhánh `test/3.25-family-adherence-history-tests` từ `origin/main`, HEAD `b24ee681aed79caaa69a081cf7605492b33e33c7`, không tạo merge commit. Đây là baseline UI mới; không so số test với baseline 3.15 để kết luận lỗi cũ đã được sửa.
- UI gia đình được gọi từ route `/family/adherence`, implementation nằm ở `features/adherence`. Main cũng có UI `features/adherence_history` cho luồng khác. Test 3.25 kiểm đúng `FamilyAdherenceScreen` của route gia đình, không thay bằng màn demo.
- API contract main fast-forward từ `aaf5eee` tới `585e99cf516c8b01706c0591dc8186985cff59d5`, không chỉnh nội dung hợp đồng hoặc tạo commit. Main vẫn không có adherence.
- Backend giữ `49f2f114e323af660c5d797c7af910cf6400872d`; docs `3077e2e18c0c6e79827261faf06c80aa945eb98f`; tests `ac207f40cd2f78508a79b12150e83569b939cf4c` không đổi file.
- Superproject `test/3.25-family-adherence-history-tests` có gitlink api_contract/backend/docs/frontend/tests khác HEAD. Các checkout phụ thuộc và commit trước được ghi rõ; không stage/bump con trỏ, không push.

Scope: `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage implement` → **exit 0**, năm file frontend `[OK]`, không có `[NGOÀI]`; `evidence/implement-resume-scope.log`. Các dòng `[CHƯA SỬA]` không xét committed code: backend unit đã nằm trong `49f2f11`, workbook trong `3077e2e`.

## 3. Kiểm thử trong phiên 25/10/2026

Các kết quả bên dưới đã thực sự chạy ở lượt này. Test widget dùng HTTP/repository mock hoặc session trong RAM để cô lập UI; không chứng minh PEP/DB/audit thật. Kiểm backend là unit/architecture, không phải integration. Không chạy E2E, không cài app, không reset DB trong lượt implement.

Dart SDK: `C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe`; Flutter tool: `C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot`. Lệnh Flutter/Dart chạy từ `frontend/mobile`; pytest từ `backend`.

| Kiểm tra | Lệnh | Kết quả cuối / evidence |
|---|---|---|
| Toàn Flutter unit/widget | `dart flutter_tools.snapshot test --no-pub --reporter json` với hai đường dẫn tuyệt đối trên | **767 Pass, 3 Fail, 1 skip**, 77.495s, exit 1. JSON testDone đánh dấu skip là success; số Pass đã loại riêng skip. `evidence/implement-resume-mobile-full.jsonl`. |
| Nhóm test 3.25 mới | Trích chính xác `/test/features/family/family_adherence_*` trong JSON của lần chạy toàn bộ | **14 Pass, 2 Fail, 0 skip**; cả hai Fail là background/offline. Không tính nhầm 8 ca cũ cùng tên file ở `features/adherence`. `evidence/implement-resume-audit-final.log`. |
| Analyze năm file mới | `dart analyze test/features/family/family_adherence_repository_test.dart test/features/family/family_adherence_controller_test.dart test/features/family/family_adherence_screen_test.dart integration_test/adherence_history_e2e/history_helpers.dart integration_test/adherence_history_e2e/history_test.dart` | **No issues found, exit 0**. `evidence/implement-resume-mobile-analyze-final.log`. |
| Format | `dart format` trên năm file mới; các lượt chỉnh fixture/helper cũng format lại | exit 0. `evidence/implement-resume-mobile-format.log`, `implement-resume-e2e-format.log`, `implement-resume-mobile-final-format.log`. |
| Backend history/PEP/route/contract | `.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_get_adherence_history.py tests/unit/test_access_authorize.py tests/unit/test_adherence_history_http.py tests/architecture/test_health_route_enforcement.py tests/unit/test_contract_adherence.py -q --continue-on-collection-errors -p no:cacheprovider --junitxml=../work/3.25/evidence/implement-resume-backend.xml` | **88 Pass, 2 Fail, 1 collection error**, 1 warning, 12.40s, exit 1. `evidence/implement-resume-backend.log/xml`. Không sửa backend trong lượt này nên không chạy lại toàn bộ unit backend. |
| Đối chiếu kết quả và nguồn | `backend/.venv/Scripts/python.exe -X utf8 work/3.25/scratch/implement_resume_audit.py` từ superproject | exit 0; đếm skip riêng, xác minh tên test fail, XML, Git trạng thái và SHA256 năm file. `evidence/implement-resume-audit-final.log`. |
| Scope implement | `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage implement` | exit 0; `evidence/implement-resume-scope.log`. |

Fail thứ ba ngoài nhóm mới: `family_tab_screen_test.dart::alert entry displays server unread count and removes it after clear`. Có fail này ở evidence test trước; chưa chạy baseline mới không có năm file 3.25 để khẳng định nguyên nhân. Không sửa file ngoài plan.

Skip duy nhất có sẵn ở baseline UI mới: `live_repository_reads_both_groupings_and_observes_revoke`, lý do `Requires local API/DB fixture; run in stage test.` Không thêm skip/xfail vào test 3.25. Test QR redeem từng fail ở baseline 3.15 không có trên branch main mới, nên không diễn giải việc nó vắng mặt là đã sửa lỗi QR.

Lượt targeted đầu có 13 Pass/3 Fail; hai ca app lỗi ở precondition vì route production chọn ngày hiện tại còn fixture ngày 22/10. Đã sửa fixture app về ngày VN hiện tại (giữ các ca screen/controller riêng theo clock cố định), không thay oracle. Log trước giữ nguyên `implement-resume-mobile-targeted.log`, `implement-resume-mobile-targeted-final.log`, analyze trước có unused helper/lint. Kết quả toàn bộ cuối ở trên mới là bằng chứng bàn giao: ca logout Pass; background/offline Fail sau precondition có dữ liệu đã Pass.

### Truy vết nghiệp vụ → AC → test mới

| Nguồn đã đối chiếu | AC | Bằng chứng / giới hạn |
|---|---|---|
| QD-27/28: gia đình chỉ đọc, kiểm quyền từng request | AC4, AC5, AC6 | Repository mới chỉ gửi GET với patient/bearer mới; mismatch patient bị từ chối. Read-only widget Pass. Đây là mock unit; AC5 consent thật/cùng token và audit vẫn cần test DB. |
| QD-29: xóa dữ liệu khi đổi patient/offline/background/logout/403 | AC6 | Controller đổi patient, response muộn, clear/403/network/401 đều Pass. Widget đổi patient, refresh 403/network, logout Pass; **background và offline Fail BUG-3.25-02**. Chưa chứng minh OS/native cache trên thiết bị thật. |
| QD-33 + bất biến PEP | AC1, AC4, AC5, AC7 | Unit PEP/route được chạy lại; không đổi production. E2E helper dùng HTTP thật, không thay backend authorize, nhưng chưa chạy và chưa có DB/audit evidence mới. |
| QD-03/10/42 + ngoại lệ người dùng 23/10 | AC2, AC3 | Backend regression −30 vẫn Fail; không nới kỳ vọng hoặc sửa nguồn SQL/domain trong task test. |
| QD-42, QD-45 | AC8, AC9 | Đối chiếu path/schema ở commit 382fb13/d9a466e/585e99c; canonical vẫn thiếu. UI sample fixture là nguồn unit của 3.24, không được dùng thay contract chuẩn hoặc tuyên bố wire contract đạt. |

Nghiệp vụ đã đọc lại trong `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`: QD-03/10/27/28/29/33/42/45 giữ trạng thái ✅ của baseline; ngoại lệ AC3 23/10 trong 01/03 approved có ưu tiên cho 3.25. Không suy quy tắc từ behavior đang sai.

### Bằng chứng lịch sử cần giữ

Lượt implement 24/10: nhóm history 61 Pass/2 Fail; toàn backend unit+architecture 1333 Pass/32 Fail/1 collection error; lint toàn backend 31 lỗi ngoài file thay đổi, lint/format file unit Pass. Các log `implement-P2.log`, `implement-P6.log`, `implement-final-backend.log`, `implement-lint-backend.log`, `implement-lint-changed.log`, `implement-format-check.log` là kết quả cũ, không tuyên bố chạy lại toàn bộ trong lượt 25/10. Test/review trước có báo cáo 05/06 và evidence riêng; không chỉnh nội dung approved của 05 để cập nhật lượt mới.

## 3b. Bộ test case Excel

Task L: cập nhật ở giai đoạn test. Workbook/spec cũ hiện giữ đúng kết quả của lượt test trước (45 ca; 24 Pass/1 Fail/20 Pending). Cần đưa BUG-3.25-02, kết quả widget mới và sửa R4 vào đó khi test được mở lại; không dựng/gộp workbook trong lượt implement này. Docs workbook đã commit `3077e2e` và sạch.

## 4. Chuẩn bị Flutter E2E và giới hạn

Hai file P4 đã có và qua analyze; chưa build APK hoặc thực thi. Python runner nằm trong `tests/e2e/mobile_adherence_history/*` thuộc giai đoạn test, chưa viết ở lượt này.

- Package test bắt buộc `vn.drugtime.adherence_e2e`; fixture ở private `/data/data/vn.drugtime.adherence_e2e/files/adherence_fixture.json`. Runner cô lập app trước khi ghi fixture. Helper không đụng secure storage/session của app người dùng.
- Fixture gồm `session` (JSON AuthSession mobile hợp lệ của family), `patient_id` (đã liên kết), `other_patient_id` (không liên kết), `medication_name` (dữ liệu local giả, seed trong ngày VN hiện tại), `scenario` thuộc `linked|revoke|cross_patient`. Session không in ra log hoặc đưa vào asset/dart-define.
- Endpoint đọc từ AppConfig, chỉ cho HTTP loopback/localhost/10.0.2.2. Production `DrugTimeApp`, named route, controller và RemoteAdherenceRepository chạy với API local thật. Auth bootstrap/medication/consent phía Flutter dùng in-memory collaborators; backend PEP/DB consent không mock. Không tuyên bố đã kiểm production login/consent UI hoặc graph `main()` đầy đủ.
- Flutter mở named route bằng Navigator; điều này chưa chứng minh luồng chọn patient từ tab chính. Qua `rg` chưa thấy call site mở `familyAdherence` ngoài khai báo route; cần chủ 3.24 xác minh entrypoint, không thêm màn chọn giả vào test để nghiệm thu hành trình.
- Sau khi thấy dữ liệu, helper ghi `adherence_phase.json` với `{"phase":"history_loaded"}`. Với revoke, host phải mutate consent/sharing/link thật và commit, rồi ghi atomic `adherence_command.json` với `{"command":"revocation_committed"}`. Flutter chờ tối đa 45s rồi refresh bằng cùng bearer, chờ 403/no old data. Host runner sau này cần xác minh DB/access_logs; Flutter HTTP 403 một mình không chứng minh audit.
- Cross-patient scenario đã có route P success rồi mở Q; không giữ P offstage. Đây là kiểm route/API sau thay patient, chưa chứng minh một selector UI. E2E phải được chạy thật ở stage test trước khi ghi Pass.
- Cleanup tháo widget, dispose auth/client, xóa ba file private của fixture/phase/command. Không ghi lịch sử xuống storage. Chỉ fixture local ngắn hạn chứa bearer trong app private để runner chuyển vào.

Không có migration hoặc production change.

## 5. Lỗi và phụ thuộc

### BUG-3.25-01 — Xác nhận sớm bị loại trước giờ dự kiến (giữ nguyên)

- Open, **Medium** ở mức sản phẩm, review chặn AC3 ở mức High. Owner sản phẩm 3.23. Không có bằng chứng mất dose_log, có cách tránh là xem lại tới giờ dự kiến.
- Lịch 08:00, taken_at/as_of 07:30, status da_uong: AC3 đòi total/taken/counted=1, rate 100; thực tế 0/None và không có nhóm. Hai param date/medication fail lại trong `implement-resume-backend.log/xml`.
- Nguyên nhân đã đối chiếu: `domain/history.py::build_history` lọc `row.scheduled_at <= as_of`; `sql_adherence.py` CTE recorded cũng lọc scheduled_at. Cần xử lý cả domain/SQL trong task sản phẩm riêng.
- Test cũ `test_future_occurrences_including_early_confirmed_are_excluded` và `test_early_confirmation_is_excluded_until_scheduled_time__AC6_AC18` còn kỳ vọng ngược AC3 mới. Task 3.23 phải cập nhật các test đó theo quyết định người dùng, không bỏ test mới 3.25 để làm xanh.

### BUG-3.25-02 — Lịch sử người thân còn dữ liệu sau background/offline

- Open, **High** do vi phạm AC6/QD-29 về bảo vệ dữ liệu sức khỏe trong phiên; chuyển task sản phẩm 3.24. Chưa có bằng chứng truy cập chéo patient hoặc lộ dữ liệu thật; mức này không khẳng định một vụ rò rỉ đã xảy ra.
- Baseline frontend `b24ee68`. Tái hiện widget với production `FamilyAdherenceScreen`/`DrugTimeApp`, family đã đăng nhập, repository cấp dữ liệu local giả; kiểm tên thuốc có trước trigger.
- Background: phát inactive → hidden → paused, pump một frame. Kỳ vọng không còn tên thuốc/thẻ liều, xóa history khỏi RAM. Thực tế còn 4 Text `Thuốc A`.
- Offline: mở route gia đình trong DrugTimeApp, load lịch sử hôm nay, emit `false` qua ConnectivityMonitor thật được app đăng ký. Kỳ vọng xóa dữ liệu trước bất cứ GET mới nào. Thực tế vẫn còn 4 Text `Thuốc A`. Ca cuối fail ở assertion sau emit; precondition đã Pass.
- Bằng chứng fail cuối: `family_adherence_screen_test.dart`, hai test `AC6 QD-29: background removes family health data immediately` và `AC6 QD-29: offline removes health data from the actual app`; `implement-resume-mobile-full.jsonl`, đếm/name trong `implement-resume-audit-final.log`.
- Nguyên nhân có code: `FamilyAdherenceScreen.didChangeAppLifecycleState` chỉ refresh khi resumed, không clear khi inactive/hidden/paused. App callback `familyConnectivity.onlineChanges` chỉ clear FamilyAlertController; không clear controller của family history. Controller có cơ chế generation/clear nhưng màn/app chưa gọi tại hai sự kiện này.
- Đề xuất fix ở 3.24: nối invalidation phiên/mạng/lifecycle tới controller family history có sẵn, xóa ngay và vô hiệu response tới muộn, đọc quyền mới khi hợp lệ trở lại. Không tạo cache quyền. Giữ hai test để xác nhận Fail trước/Pass sau; chạy thêm manual lifecycle trên Android thật ở stage test.
- Logout app, refresh 403/network, đổi patient và clear khi request đang chạy đều Pass trong test mới; không gộp chúng thành lỗi khi chưa có chứng cứ.

### Phụ thuộc contract 3.23 — Schema bị mất lúc merge

- GitHub [frontend PR #40](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/40) merged 23/10; [contract PR #13](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/13) cũng merged. Không thể dựa vào trạng thái merged để suy nội dung schema tồn tại.
- Đã đọc spec từ từng blob Git: `382fb13` có `/adherence` và **7** schema Adherence; `d9a466e` (merge main vào nhánh 3.23) mất path và cả 7 schema; `585e99c` main hiện tại vẫn thiếu. `implement-resume-audit-final.log` xác minh độc lập.
- Owner 3.23 cần khôi phục đúng phần contract đã thiết kế, kiểm lại với main hiện hành và review riêng; không checkout snapshot cũ làm chuẩn để né các lỗi hoặc phục hồi production trong phạm vi task test 3.25.

## 6. Phát sinh và ghi chú bàn giao

- UI từng được báo thiếu vì checkout cũ: đã tìm remote refs, kiểm PR merged, fetch và nhận baseline. Không còn ghi P3/P4 bị chặn do UI hoàn toàn vắng. Giới hạn mới là lỗi dữ liệu phiên và entrypoint chưa được chứng minh.
- Contract tuy PR merged vẫn thiếu trong artifact chuẩn; đã xác định merge làm mất nội dung, không hỏi người dùng điều có thể tìm trong Git.
- Hai ca app ban đầu sai ngày fixture đã sửa như mục 3; không đếm lỗi precondition đó thành bug sản phẩm. Analyze cuối không còn warning/info trong năm file mới.
- Khi đếm JSON toàn Flutter ban đầu đã gộp một skip vào success; đã sửa phép đếm và thông báo người dùng. `implement-resume-audit.log` giữ assertion lỗi kiểm đếm cũ; `implement-resume-audit-final.log` mới là kết quả cuối hợp lệ. Không đổi marker hoặc rerun để che skip.
- `05-test-report.md` và testcases/workbook phản ánh lượt test trước. Sau thay đổi 04, approval downstream gắn hash đầu vào sẽ cần kiểm lại; không tự sửa approved hoặc tự approve. `06-review.md` là review trước đợt triển khai mới, chưa phải review năm file này.
- Source scope vẫn đúng plan; không phát sinh file code ngoài bảng. R4 Excel để xử lý khi mở lại test. Không sửa .agents/docs/production.

## Bước tiếp theo

- Implement giữ **draft**, chưa nghiệm thu toàn bộ AC. Cần task sản phẩm 3.23 xử lý BUG-3.25-01 + contract bị mất, task 3.24 xử lý BUG-3.25-02 và xác nhận đường chọn patient vào màn lịch sử.
- Người duyệt có thể đọc phần triển khai test, lỗi và giới hạn rồi duyệt implement khi chấp nhận bàn giao: `python .agents/scripts/gate.py approve 3.25 implement`. Agent không chạy approve. Approval giai đoạn không biến Fail thành Pass.
- Khi implement đã được duyệt lại, người dùng mở lại test bằng `python .agents/scripts/gate.py reopen 3.25 test`; lượt sau hoàn tất P5/P6 DB, P7 runner, cập nhật workbook/Bug Report và sửa R4 bằng kết quả thật. Không bắt đầu test hoặc sửa artifact 05 approved trong lượt implement này.
- Chưa commit năm file frontend hoặc artifact/evidence mới, chưa push. Backend/contract/docs/tests sạch về file; frontend có đúng năm file ở mục 2. Các gitlink superproject chưa stage/bump.
- Lệnh commit chỉ đề xuất khi được yêu cầu: `git -C frontend add -- mobile/test/features/family/family_adherence_repository_test.dart mobile/test/features/family/family_adherence_controller_test.dart mobile/test/features/family/family_adherence_screen_test.dart mobile/integration_test/adherence_history_e2e/history_helpers.dart mobile/integration_test/adherence_history_e2e/history_test.dart`, rồi `git -C frontend commit -m "test(adherence): cover family history session privacy" -m "Refs: 3.25"`. Artifact/evidence chỉ thêm có chủ đích bằng `git add -f -- work/3.25/04-impl-notes.md work/3.25/evidence` rồi commit riêng; không stage scratch. Chỉ bump sau khi các commit submodule đã push theo wf-git.
- Tiếp tục bằng `tiếp tục task 3.25`, luôn chạy gate và đọc 04 hiện tại trước; nếu còn draft đã hoàn tất phần test được phép, chờ review/duyệt implement và phụ thuộc sản phẩm, không tự sửa ngoài plan.
- Bàn giao theo wf-handoff; owner vẫn `phucnguyenngoc`. Cập nhật cuối: 2026-10-25, Codex.
