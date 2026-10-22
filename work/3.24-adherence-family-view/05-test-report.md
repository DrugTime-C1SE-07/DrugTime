---
task: 3.24-adherence-family-view
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-22 21:26 +0700
content_hash: sha256:bc0dd9c7afaf3184
inputs:
  01-requirement.md: sha256:78a2784681c4911b
  03-plan.md: sha256:c42bc0a5bb6b51b5
  04-impl-notes.md: sha256:e5195d96ad85dfb8
---

# 3.24-adherence-family-view · Test sau sửa vùng chạm

## Cập nhật sửa review R1 — bảo toàn workbook tổng

- Người dùng đã reopen test; gate test OK. Chỉ sửa workbook tổng và artifact của task, không sửa code sản phẩm.
- Đã khôi phục workbook từ blob `docs/origin/main` tại commit `dfd422fa9211d4a2c40b740cb772b694779ada0f`, giữ đủ **15 sheet chức năng baseline**. Sao lưu workbook trước sửa trong scratch; không reset checkout docs hoặc xóa nhánh.
- Dùng bộ ghi `.agents/scripts/testcase_xlsx.py` để ghép ALERT từ spec task 3.20 hiện có, ADHERENCE từ spec đã commit trên nhánh task 3.23 và FAMADH của task này. Trước khi ghép đã đối chiếu toàn bộ ID/status/actual với workbook trước sửa: ALERT 11, ADHERENCE 23, FAMADH 20 ca đều khớp, không ghi đè kết quả tester khác. Sau khôi phục, toàn bộ ô có dữ liệu/công thức và vùng gộp của 15 sheet main + 3 sheet task đều khớp nguồn. Log `evidence/test-workbook-restoration.log`.
- Sau đó bổ sung TC-FAMADH-21 cho lỗi Medium R2 của review; giữ nguyên kết quả 20 ca cũ. Workbook hiện có **19 sheet = 18 sheet chức năng + Report**, FAMADH **21 ca = 18 Pass, 1 Fail, 2 Pending**. Report được script tạo lại và có BUG-FAMADH-21 mức Medium.
- Validate/build/merge đều thành công, không có cảnh báo đổi Pass/Fail cũ: `evidence/test-workbook-fix-{validate,build,merge}.log`. Chạy script đọc-only `evidence/verify-master-preservation.py` sau merge: **Pass** toàn bộ 15 sheet baseline và FAMADH khớp workbook riêng, đủ 19 sheet — `evidence/test-workbook-fix-preservation.log`.
- R1 High đã xử lý trong bản workbook working; cần review lại sau khi test được duyệt. Chưa commit docs theo phạm vi yêu cầu commit hiện tại chỉ dành cho work.
- R2 Medium còn mở: đã chạy lại script tái hiện **1 pass xác nhận bug tồn tại** (không phải sản phẩm đúng), log `evidence/test-rollover-known-issue.log`. Request từ 01/08 đến 31/07 sau khi chuyển 28/10→29/10/2026 vẫn tái hiện. TC-FAMADH-21 đánh Fail với kỳ vọng from<=to; không sửa code trong test. Có cách tránh là chọn ngày hợp lệ khác.
- Không chạy lại Flutter/backend toàn bộ vì bản sửa chỉ tác động workbook; số liệu chạy các lượt trước bên dưới được giữ làm lịch sử, không coi là đã chạy lại trong phiên sửa workbook này. Hai ca manual Pending không đổi.
- Scope test vẫn exit 1 do đúng 17 file implement đã được người dùng chấp nhận ngoại lệ, không có thay đổi frontend mới. Workbook `[OK]`; log `evidence/test-workbook-fix-scope.log`.

## 1. Môi trường

- Gate test OK sau khi người dùng duyệt lại 04. Windows, Flutter 3.47.5/Dart 3.13.4; frontend/docs trên nhánh `feat/3.24-adherence-family-view`.
- Backend dùng Python runtime Codex và dependency hiện có trong scratch task 3.23; DB local riêng `drugtime_test_323_734f60b8` trên 127.0.0.1:54322 đã có migration ứng dụng. Không reset DB Supabase của người dùng, không truy cập môi trường deploy.
- Đầu phiên Docker đã tắt; chạy nhóm backend lần đầu bị 60 skip (`evidence/test-adherence-after-fix.log`). Đã khởi động Docker Desktop; Docker thoát một lần, sau lần restart kế tiếp database healthy và 60 ca chạy thật pass. Không tính skip là Pass.
- Không sửa code sản phẩm hoặc test trong frontend/backend ở giai đoạn này. Hai ca biên bổ sung nằm trong `evidence/date-boundary-repro.dart`, chạy từ frontend/mobile để dùng dependency Flutter hiện hữu.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Bằng chứng | Kết quả |
|---|---|---|
| AC1 | Route hợp lệ/sai; query/token; widget context và chỉ đọc | Pass tự động |
| AC2 | Mapper offset/bốn status và widget nhãn | Pass tự động; trình đọc màn hình cần ca manual AC9 |
| AC3 | Tỷ lệ 66.67%, nhãn gồm uống trễ; null không hiện 0% | Pass |
| AC4 | groups=[] không dựng liều giả | Pass |
| AC5 | Widget clear 200→403; DB thật thu hồi consent/sharing/unlink và audit | Pass tự động |
| AC6 | A→B loại response A; mapper sai patient; backend cross-patient 403/audit | Pass tự động |
| AC7 | HTTP 401/callback, 403, 422, 503; network/retry | Pass theo khẳng định test hiện có |
| AC8 | Bốn biên today−90, today−89, today, today+1; query giới hạn; chuyển tháng và khóa ngày ngoài phạm vi; UTC+7 | Pass tự động |
| AC9 | Lịch tuần/tháng tại 320/375dp, chữ 1.6× đạt androidTapTargetGuideline 48dp; cuộn tới cột cuối và chọn đúng ngày | Pass tự động; Pending kiểm thiết bị/safe area/landscape/TalkBack/VoiceOver |
| AC10 | Chưa quan sát màn chạy trên thiết bị để so Figma S09a/S09b | Pending |

## 3. Kịch bản chất lượng

`test_adherence_history_access.py` chạy trên DB thật: family allowed/audit allowed, thiếu link/consent/tắt chia sẻ và cross-patient 403/audit denied, thu hồi quyền request kế tiếp với cùng token, lỗi audit/commit/đọc quyền fail-closed đều **Pass**. Cùng `test_adherence_history_api.py`: **60 pass, 0 skip**, 17.36 giây — `evidence/test-adherence-after-docker-restart.log`.

Client vẫn xóa dữ liệu trước refresh và sau 403, không hiển thị response bệnh nhân cũ. Không đổi schema, ghi nhận liều hay engine tương tác trong task này.

## 4. Lệnh và kết quả

| Lệnh tại thư mục tương ứng | Kết quả | Log |
|---|---|---|
| `flutter test --no-pub test <absolute-path>/evidence/date-boundary-repro.dart` tại frontend/mobile | 633 pass, 1 lỗi script test mới: ép `RawTooltip` thành `IconButton`; cả 632 test sản phẩm pass. Không phải lỗi sản phẩm. | `evidence/test-after-calendar-fix.log` |
| `flutter test --no-pub <absolute-path>/evidence/date-boundary-repro.dart` sau sửa finder đúng loại widget | 2 pass, 0 fail; đủ bốn biên và khóa điều hướng/ngày | `evidence/test-boundary-after-fixture-fix.log` |
| `python -m pytest tests/integration/test_adherence_history_access.py tests/integration/test_adherence_history_api.py -q -rA -p no:cacheprovider --tb=short` | 60 pass, 1 warning, 17.36 giây | `evidence/test-adherence-after-docker-restart.log` |
| `python -m pytest tests/integration -x -q -p no:cacheprovider --tb=short` | 102 pass, 1 error, 1 warning, 24.19 giây; dừng ở lỗi đầu theo `-x` | `evidence/test-backend-first-failure.log` |

**Giới hạn full backend:** lỗi setup `test_auth_flow.py::test_admin_login_and_refresh__AC7_AC3a`: `relation "auth.users" does not exist`. DB task chỉ có schema ứng dụng, chưa có schema/service Supabase Auth đầy đủ cho toàn bộ suite. Đây là hạn chế môi trường chưa chứng minh lỗi backend sản phẩm. Không sửa fixture, skip hoặc nới khẳng định; không kết luận full suite sạch. Lần full suite trước bị ngắt ở 82% còn ở `evidence/test-backend-full-db.log`.

**Scope:** `scope.py ... --stage test` exit 1, workbook `[OK]`, 17 file frontend implement đã duyệt `[NGOÀI]` do script tính toàn bộ diff nhánh. Đây là ngoại lệ người dùng đã chấp nhận ở phiên trước; không có sửa frontend mới trong test. Log `evidence/test-retest-scope.log`.

## 5. Bộ test case Excel

- Spec `testcases.json`; file riêng `testcases.xlsx`; file tổng `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` đã merge. Chưa commit docs theo phạm vi yêu cầu commit hiện tại.
- **21 ca: 18 Pass, 1 Fail (Medium R2), 2 Pending**. Pending: TC-FAMADH-14 (thiết bị/safe area/landscape/trình đọc màn hình), TC-FAMADH-15 (đối chiếu Figma). Số liệu 18 Pass là kết quả được bảo toàn từ các lần chạy trước; ca Fail mới được tái hiện trong phiên sửa R1.
- TC-FAMADH-19 chuyển Pass nhờ hai ca biên mới. TC-FAMADH-20 chuyển Fail→Pass nhờ hồi quy tuần/tháng 320/375dp; người dùng đã xác nhận “Dùng kết quả hồi quy mới (Pass nếu đạt)” trước khi merge. Giữ log fail cũ `test-calendar-accessibility.log` và bản test tái hiện cũ.
- Validate/build/merge thành công: `evidence/testcase-retest-validate.log`, `testcase-retest-build.log`, `testcase-retest-merge.log`, `testcase-retest-merge-final.log`. Cảnh báo Fail→Pass ở log merge đã được người dùng quyết định như trên.
- Hai sheet chức năng cũ giữ nguyên giá trị ô: `evidence/testcase-retest-preservation.log`.

## 5b. Lỗi sản phẩm

**BUG-FAMADH-20 đã sửa và đạt hồi quy** ở lượt trước. **R1 High workbook mất sheet đã khôi phục**, có kiểm tra baseline và cần review lại. **BUG-FAMADH-21 / R2 Medium còn mở** (refresh qua ngày có thể tạo from>to), đã ghi Fail trong workbook với bằng chứng tái hiện mới. Không kết luận mọi AC đã đạt vì còn R2 và hai ca manual Pending.

## 6. Skip và tính ổn định

60 skip đầu phiên do Docker tắt; lần chạy lại DB thật 60 pass. Không thêm retry vào test. Lỗi script finder đã sửa và chạy lại đúng hai ca, không sửa code sản phẩm. Bộ test sản phẩm không thay đổi sau lần chạy full nên không chạy lại toàn bộ lần nữa. Không dùng kết quả cũ của backend làm Pass của phiên này.

## 7. Phát sinh

Full backend integration cần môi trường Supabase Auth đầy đủ để tiếp tục; DB riêng hiện đủ cho nhóm adherence. Ngoại lệ scope 17 file implement và việc cập nhật Fail→Pass workbook đều đã được người dùng chấp thuận. Hai ca manual chưa có thiết bị/phiên kiểm trực quan.

## Bước tiếp theo

- Đang chờ: người duyệt xem bản sửa R1, lỗi Medium R2 và hai ca manual Pending.
- Nếu chấp nhận báo cáo cùng các lưu ý, chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view test` trong terminal người duyệt; sau đó agent mới review lại workbook. Nếu muốn sửa R2 trước review, cần reopen implement theo gate. Không sửa code sản phẩm trong test và không coi task hoàn tất trước review/DoD.
- Cập nhật lần cuối: 2026-10-22, Codex.
