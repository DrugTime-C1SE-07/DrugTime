---
task: 3.24-adherence-family-view
stage: test
status: draft
---

# 3.24-adherence-family-view · Test

## Cập nhật sau khi khởi động dịch vụ — 2026-10-22

Phần này thay thế kết luận và số liệu Pending của lần chạy trước bên dưới.

- Supabase DB đã healthy trên cổng 54322; đã khởi động container `drugtime-redis`. Backend API chạy tại `http://127.0.0.1:8000`: OpenAPI 200, GET /adherence không token trả 401. Log `evidence/test-backend-start.log`. API dùng database task riêng, không phải DB deploy.
- Tạo DB local riêng `drugtime_test_323_734f60b8`, chạy các migration schema từ repo; giữ nguyên DB Supabase local có sẵn. Migration tạo role cấp cluster đã có nên không chạy lại file đầu. Log `evidence/test-db-start.log`.
- `pytest tests/integration/test_adherence_history_access.py tests/integration/test_adherence_history_api.py -q -rA -p no:cacheprovider --tb=short`: **60 pass, 1 warning, 13.18 giây**, không skip. Log `evidence/test-adherence-db.log`. Các ca allowed/denied, cross-patient, rút consent/sharing/unlink request kế tiếp và audit fail-closed đều pass trong phiên này. TC-FAMADH-16/17/18 chuyển Pass.
- Full backend integration: đã chạy cùng lệnh full suite trên DB riêng, tiến độ có E/F ở các nhóm khác và dừng phát output tại 82% hơn hai phút. Kiểm `pg_stat_activity` thấy các kết nối idle, không chờ lock DB. Đã ngắt tiến trình để tránh chờ không giới hạn; **không có kết quả full-suite hoàn tất**, không suy ra số pass/fail hoặc nguyên nhân sản phẩm khi chưa có traceback. Log thô `evidence/test-backend-full-db.log` giữ tiến độ E/F. Kết quả này chưa chứng minh baseline backend sạch; cần điều tra độc lập sau khi sửa lỗi UI.
- Test accessibility bổ sung tại `evidence/calendar-accessibility-repro.dart`: **Fail**, log `evidence/test-calendar-accessibility.log`. TC-FAMADH-20 / **BUG-FAMADH-20, Medium**: ô ngày ở viewport 320dp chỉ có vùng chạm 41.1×52dp; yêu cầu Android tối thiểu 48×48dp. Nguyên nhân: Row chia 7 Expanded trên chiều rộng còn 288dp sau padding. AC9 chưa đạt. Không sửa code sản phẩm trong giai đoạn test.
- Workbook cập nhật: **20 ca = 16 Pass, 1 Fail, 3 Pending**. Pending còn TC-FAMADH-14 (quan sát thiết bị/trình đọc màn hình), 15 (Figma), 19 (đủ biên 90 ngày/lịch tháng). Validate/build/merge đã chạy lại thành công, Bug Report sinh BUG-FAMADH-20; log `evidence/testcase-{validate,build,merge}.log`.
- Ngoại lệ scope 17 file implement vẫn theo xác nhận người dùng ở phiên trước; giai đoạn này chỉ ghi work và workbook tổng, không sửa code frontend/backend.

**Bước tiếp theo hiện hành:** chưa duyệt test hoặc sang review. Người dùng chạy `python .agents/scripts/gate.py reopen 3.24-adherence-family-view implement` trong terminal để cho phép sửa BUG-FAMADH-20; sau đó agent mới sửa widget/test trong phạm vi plan. Theo wf-test bước 6, agent phải ghi lỗi sản phẩm và yêu cầu reopen implement, không sửa trực tiếp trong giai đoạn test. Backend/DB/Redis đang được giữ chạy cho lần kiểm tiếp.

## Lịch sử lần chạy trước khi DB hoạt động

## 1. Môi trường

- Gate test: OK, 04 đã được người dùng duyệt. Flutter 3.47.5/Dart 3.13.4 trên Windows; nhánh frontend `feat/3.24-adherence-family-view`.
- Chạy `D:/Captone/flutter/bin/flutter.bat test --no-pub` tại `frontend/mobile`, với safe.directory cho SDK và tắt analytics.
- Backend dùng Python runtime Codex, dependency sẵn có tại `work/3.23-adherence-family-consent/scratch/python-deps`, PYTHONPATH thêm `backend/src`. Không cài dependency mới.
- Kiểm kết nối Postgres local `127.0.0.1:54322`: timeout cả trong sandbox và khi cho phép kết nối ngoài sandbox. Không có Docker/Supabase CLI trên PATH; chưa reset DB hoặc khởi động service được. Không kết nối DB deploy/chia sẻ. Log: `evidence/test-backend-environment.log`.
- Không sửa code sản phẩm hoặc test frontend/backend trong giai đoạn này. Workbook tổng ở docs trên nhánh task tạo từ `origin/main`, giữ dữ liệu các sheet chức năng của workbook trước phiên này.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Bằng chứng chạy trong phiên | Kết quả |
|---|---|---|
| AC1 | Widget route hợp lệ/sai, hiển thị context, summary và màn chỉ đọc; HTTP query/token | Pass tự động |
| AC2 | Mapper bốn trạng thái và offset; widget nhãn trạng thái | Pass tự động; trình đọc màn hình Pending |
| AC3 | Widget 66.67% và nhãn gồm uống trễ; null rate | Pass |
| AC4 | Widget groups rỗng, không dựng liều giả | Pass |
| AC5 | Controller clear trước refresh; widget 200→403 khi resume, thuốc cũ biến mất | Pass phía client; backend PEP/audit Pending |
| AC6 | Controller A→B, response A đến muộn; repository từ chối sai patient | Pass tự động; backend cross-patient Pending |
| AC7 | Repository 401/callback, 403, 422, 503; widget network/retry | Pass cho các khẳng định tự động đã có |
| AC8 | Query tháng giới hạn today; chặn tương lai/quá cũ; mapper offset UTC+7 | Pass phần tự động; bốn biên cửa sổ 90 ngày và điều hướng lịch tháng Pending |
| AC9 | Widget 320×640, chữ 1.6× không layout exception | Pending phần manual vùng an toàn/landscape/TalkBack/VoiceOver |
| AC10 | Chưa có phiên quan sát màn chạy so với Figma | Pending |

Toàn bộ bằng chứng Flutter nằm ở `evidence/test-integration.log`. Không suy ra Pass manual từ widget test.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test hiện có | Kết quả phiên này |
|---|---|---|
| Không link/consent hoặc đổi patient trái quyền →403 và audit denied | `backend/tests/integration/test_adherence_history_access.py` | Skip: DB không chạy; Pending |
| Rút consent/tắt sharing/unlink rồi request ngay với cùng token | Cùng file, `test_revoke_sharing_off_unlink_denies_immediate_next_request_same_token__AC12` | Skip; Pending |
| Audit/đọc quyền/commit lỗi → fail closed | Cùng file, `test_audit_permission_and_commit_failure_fail_closed_without_health__AC13` | Skip; Pending |
| Client xóa dữ liệu cũ khi 403 và loại response sai bệnh nhân | Bộ adherence Flutter | Pass |

Không đổi ghi nhận liều, schema hoặc engine tương tác; không thêm test cho các vùng đó.

## 4. Toàn bộ bộ test

- Frontend: `flutter test --no-pub` → **630 pass, 0 fail**, 80 giây. Log `evidence/test-integration.log`.
- Backend: `python -m pytest tests/integration -q -rs -p no:cacheprovider --tb=short` → **0 pass, 0 fail, 965 skipped, 1 warning**, 17.28 giây. Fixture session skip do Postgres local timeout. Log `evidence/test-backend-integration.log`. Exit 0 không chứng minh backend đạt.
- Scope test: exit 1, workbook tổng `[OK]`, 17 file frontend từ implement đã duyệt `[NGOÀI]` vì script tính toàn bộ diff nhánh. Không có sửa frontend mới ở giai đoạn test. **Người dùng đã xác nhận “Chấp nhận 17 file implement đã duyệt” trong phiên này.** Không sửa script hoặc che Git state. Log `evidence/test-scope.log`.

## 5. Bộ test case Excel

- Spec `testcases.json`; file riêng `testcases.xlsx`.
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`; đã merge thành công, chưa commit docs vì yêu cầu commit hiện tại chỉ dành cho thư mục work.
- Validate/build/merge đều exit 0: `evidence/testcase-validate.log`, `evidence/testcase-build.log`, `evidence/testcase-merge.log`.
- Hai sheet chức năng cũ giữ nguyên toàn bộ giá trị ô, Report dựng lại: `evidence/testcase-preservation.log`.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Người thân xem tuân thủ (FAMADH) | 19 | 13 | 0 | 6 |

Pending cần chạy tiếp: TC-FAMADH-14 (thiết bị/a11y), 15 (Figma), 16 (quyền/audit DB), 17 (thu hồi ngay), 18 (fail closed), 19 (đủ biên 90 ngày/lịch tháng). Các Pass truy về khẳng định của test tự động hiện có, không chứng minh các nhánh chưa được khẳng định.

## 5b. Lỗi sản phẩm tìm thấy

Không phát hiện lỗi sản phẩm trong các ca đã thực thi. Chưa đủ bằng chứng kết luận mọi AC đạt vì còn 6 Pending.

## 6. Test không ổn định hoặc bị skip

Không thêm retry hoặc nới khẳng định. 965 backend test skip vì cùng fixture yêu cầu DB local. Manual chưa chạy, ghi Pending. Không dùng kết quả backend task 3.23 làm Pass của phiên này.

## 7. Phát sinh

- Ngoại lệ scope của 17 file implement đã được người dùng chấp nhận; giữ log gốc exit 1.
- Môi trường thiếu DB local hoạt động; không tự thay bằng DB khác. Cần khởi động Supabase/Postgres local và reset sạch trước khi chạy lại integration.

## Bước tiếp theo

- Đang chờ: người dùng mở lại implement để sửa BUG-FAMADH-20 (AC9: vùng chạm lịch dưới 48dp).
- Việc cần làm: chạy `python .agents/scripts/gate.py reopen 3.24-adherence-family-view implement` trong terminal người dùng; sau đó agent sửa lỗi và chạy hồi quy. Chưa chuyển review; còn 3 ca Pending như phần cập nhật đầu báo cáo.
- Cập nhật lần cuối: 2026-10-22, Codex.
