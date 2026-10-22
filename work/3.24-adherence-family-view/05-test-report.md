---
task: 3.24-adherence-family-view
stage: test
status: draft
---

# 3.24-adherence-family-view · Test

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

- Đang chờ: chạy 6 test case Pending khi có thiết bị và DB local; người duyệt xem báo cáo cùng giới hạn.
- Chưa chuyển review. Sau khi xử lý hoặc chấp nhận rõ các Pending, người duyệt chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view test` trong terminal của họ. Agent không chạy lệnh duyệt.
- Cập nhật lần cuối: 2026-10-22, Codex.
