---
task: 3.25
stage: test
status: draft
---

# 3.25 · Test tích hợp lịch sử tuân thủ cho người thân

## 1. Môi trường

- Gate test exit 0: requirement, plan và implement đều approved; `evidence/test-gate.log`. Không sửa các artifact đã duyệt.
- Windows, backend Python trong `.venv`; chạy pytest trên PostgreSQL/Supabase **local**, không dùng môi trường deploy. Docker Desktop ban đầu chưa chạy, đã khởi động rồi chạy `supabase start` và `supabase db reset` thành công. Không sửa migration.
- Lệnh chuẩn bị từ `backend/`: `..\node_modules\.bin\supabase.cmd start`; `..\node_modules\.bin\supabase.cmd db reset`. Log: `evidence/test-supabase-start.log` (đã bỏ JSON khóa local), `evidence/test-db-reset.log`. Reset áp dụng đến migration `20261021115000_access_logs_admin_self_denied.sql`; cảnh báo không có `supabase/seed.sql`, reset vẫn exit 0.
- API được gọi bằng FastAPI TestClient, PostgreSQL thật; fixture kiểm host loopback và dùng `api_role`, không giả PEP. Fault injection chỉ dùng cho ca lỗi quyền/audit/commit có sẵn. Mốc lịch sử cố định 19/10/2026, `Asia/Ho_Chi_Minh`.
- Nhánh superproject/backend/docs: `test/3.25-family-adherence-history-tests`. Frontend và tests giữ `test/3.15-redeem-flow-tests`, không sửa file trong hai submodule đó. API contract giữ `main`.
- SHA và working tree: `evidence/test-baseline.log`. Backend `d88af5c`, frontend `f9ff263`, contract `aaf5eee`, tests `ac207f4`, docs `b8d7bea`; superproject `c70ab13`. Gitlink khác HEAD đã có từ implement, không bump.
- Sau khi chạy test, người dùng cho phép commit riêng file unit của implement. Backend tạo commit **`49f2f11`** `test(adherence): cover family history rate boundaries`, 1 file, +130/−3; không đổi nội dung test sau lần chạy, không push/bump gitlink. Backend working tree sạch.
- **Phụ thuộc vẫn thiếu:** contract không có `/adherence` hoặc schema `Adherence*`; production UI `frontend/mobile/lib/features/adherence_history` chỉ có `.gitkeep`. Vì P5 yêu cầu có contract, không mở rộng integration trước tiền đề; P7 thiếu UI/test Flutter thật nên không viết/chạy runner thay màn giả. Vẫn chạy nguyên bộ test hiện có để ghi nhận bằng chứng, không skip/xfail/nới assertion.
- Áp dụng `wf-test`, `wf-health-endpoint`, `wf-git`, `wf-testcase` và `postman:api-testing`. Theo plan đã duyệt, dùng pytest hiện có để kiểm đồng thời API/DB/audit, không dựng Postman collection trùng hoặc gửi dữ liệu lên workspace ngoài.

## 2. Kết quả theo tiêu chí chấp nhận

Các hậu tố `__ACn` trong test cũ thuộc task 3.23. Bảng này ánh xạ sang AC **3.25** theo hành vi, không theo số trong tên test. Kết quả Pass của unit không được dùng để nghiệm thu API/DB/Mobile.

| AC 3.25 / nguồn | Test, test case | Kết quả và giới hạn |
|---|---|---|
| AC1 · PB21, QD-27/28/33 | `test_self_and_family_success_are_audited_with_minimal_metadata__AC1_AC2`; TC-FADH-01 | **Pending nghiệm thu**: test đã chạy nhưng fail `KeyError: AdherenceByDateResponse`; dừng trước so payload và audit. Chưa chứng minh đường thành công end-to-end theo contract. |
| AC2 · QD-03/10 | `test_confirmed_before_deadline_counts_immediately__AC3`, test grouping/date/SQL ở `test_adherence_history_api.py`; TC-FADH-20–26,30–32,35–36 | Unit các mốc 0/+30/+30+1µs/+119:59/+120 pass; −30 fail. Integration nhóm/ngày/biên dừng vì contract thiếu. Hai mốc min−1 và +30−1 chưa chạy, Pending. **Chưa đạt toàn AC**. |
| AC3 · QD-42 + ngoại lệ người dùng 23/10; QD-10 | Unit `test_unconfirmed_pending_at_deadline_then_missed__AC3`, `test_no_eligible_dose_has_null_rate__AC3`, `test_after_deadline_confirmation_does_not_raise_rate__AC3`, `test_valid_confirmation_synced_after_deadline_still_counts__AC3`; TC-FADH-20–29 | 24 tham số của test bổ sung implement: **22 pass, 2 fail**. BUG-3.25-01: xác nhận −30 bị loại ở cả hai cách nhóm. +120 vẫn pending; +1µs missed; mẫu số 0 null; uống thực sau hạn không tăng rate; đồng bộ muộn hợp lệ vẫn tính — mới chứng minh unit. **Fail** tại xác nhận sớm, chưa nghiệm thu DB/API. |
| AC4 · QD-27/28/33 | `test_unlinked_missing_consents_sharing_off_admin_denied_and_audited__AC11`; `test_family_patient_selector_tamper...`; TC-FADH-02–06,16–19 | Không liên kết, thiếu từng consent, tắt sharing: **4 pass**, đúng 403/no-store/denied, dose_logs không đổi. Auth thiếu/sai/hết hạn/user erased: **4 pass** 401. Ca sửa patient_id bị chặn trước request sang patient khác bởi contract ở request thành công đầu; **Pending** phần truy cập chéo có tiền sử thành công. |
| AC5 · QD-27/28/33 | `test_revoke_sharing_off_unlink_denies_immediate_next_request_same_token__AC12`; TC-FADH-07–10 | Cả 4 test fail ở schema của request thành công đầu, **chưa thực hiện bước rút quyền**. Không suy ra Pass cho request kế tiếp từ unit hoặc mã nguồn. **Pending**. |
| AC6 · QD-29 | TC-FADH-39–44 | **Pending**: thiếu UI/controller/repository production 3.24. Không chạy widget/lifecycle thiết bị cho lịch sử, chưa chứng minh xóa RAM hoặc read-only. Flutter hồi quy toàn app được ghi riêng, không thay bằng chứng AC6. |
| AC7 · QD-33, bất biến PEP | `test_audit_permission_and_commit_failure_fail_closed_without_health__AC13` (4 tham số), `test_denied_audit_survives_outer_transaction_rollback__AC13`; TC-FADH-11–15 | **5 pass** trên API/DB thật: lỗi quyền/allowed audit/denied audit/commit → 500 không trả sức khỏe, không thay dose_logs; lỗi trước đọc không SELECT history. Denied tồn tại sau outer rollback. Không dùng kết quả này để tuyên bố schema contract đã đạt. |
| AC8 · QD-42 | TC-FADH-37–38 | **Pending/chưa nghiệm thu**: contract không biểu diễn tỷ lệ đúng giờ riêng/xung đột/đối soát; không tự tạo field/công thức. Ca schedule stop/soft delete hiện có cũng fail ở contract, chưa chứng minh loại liều hủy qua API. |
| AC9 · QD-45 | Baseline, log/XML và workbook; TC-FADH-45 | **Pass phần artifact/workbook**: có truy vết PB21/QD → AC → test/test case → log; đã dựng và gộp một sheet FADH, giữ 20 sheet chức năng cũ. Chưa có bản contract/UI/E2E cần để nghiệm thu toàn PB21. |

Log phạm vi lịch sử: `evidence/test-history.log`, kết quả từng test/param ở `evidence/test-history.xml`. Bằng chứng unit trong phiên: `evidence/test-unit.log`, `evidence/test-unit.xml`.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản bắt buộc | Bằng chứng | Kết quả |
|---|---|---|
| Không liên kết hoặc thiếu consent → 403 và denied | TC-FADH-02–04; test access tương ứng | Pass cho người thân không có quyền ở request đầu. |
| Tắt sharing → 403 và denied | TC-FADH-05 | Pass ở request đầu; chưa chứng minh chuyển từ allowed sang denied. |
| Patient selector bị sửa sau khi đọc P thành công → chặn Q | TC-FADH-06 | Pending: contract chặn trước bước đọc Q. |
| Thu hồi từng consent/sharing/unlink, request kế tiếp cùng token | TC-FADH-07–10 | Pending: contract chặn trước mutation; không tuyên bố đã kiểm request kế tiếp. |
| Audit fail-closed; denied bền sau rollback | TC-FADH-11–15 | 5 ca Pass; có assertion response/DB/SQL-read. |
| Gửi lại client_uuid → một bản ghi | TC-FADH-33; `test_late_sync_worker_log_and_retry_keep_one_occurrence__AC15_AC20` | Test chạy nhưng dừng ở schema; chưa chạy hết đối chiếu lịch sử, giữ Pending. |
| Worker chạy đua xác nhận muộn hợp lệ → một liều trễ | TC-FADH-34; `test_worker_insert_races_with_valid_late_confirmation__AC15_AC20_AC22` | Hai thứ tự writer chạy nhưng test fail ở schema cuối; chưa nghiệm thu trọn kịch bản. Không xóa hoặc nới assertion. |
| Thay quy tắc tương tác thuốc → golden scenarios | Không sửa engine, quy tắc hoặc import module trong 3.25 | Không áp dụng cho thay đổi task; full integration vẫn chạy phần test hiện có. |

## 4. Toàn bộ bộ test và lệnh

Các lệnh backend chạy từ `backend/`, tiền tố `.venv/Scripts/python.exe -X utf8 -m`.

| Bộ kiểm tra | Lệnh (sau tiền tố backend) | Kết quả trong phiên | Evidence |
|---|---|---|---|
| Lịch sử API + access | `pytest tests/integration/test_adherence_history_api.py tests/integration/test_adherence_history_access.py -q -p no:cacheprovider --tb=short --junitxml=../work/3.25/evidence/test-history.xml` | **29 pass, 31 fail, 0 skip**, 1 warning; 13.73s; exit 1. Cả 31 fail do thiếu `AdherenceByDateResponse`. | `test-history.log`, `test-history.xml` |
| Toàn unit + architecture | `pytest tests/unit tests/architecture -q --continue-on-collection-errors -p no:cacheprovider --junitxml=../work/3.25/evidence/test-unit.xml` | **1333 pass, 32 fail, 1 collection error**, 8 warnings; 63.46s; exit 1. 2 fail BUG-3.25-01; 30 fail ngoài file task. | `test-unit.log`, `test-unit.xml` |
| Toàn integration | `pytest tests/integration -q --continue-on-collection-errors -p no:cacheprovider --tb=short --junitxml=../work/3.25/evidence/test-integration.xml` | **1052 pass, 49 fail, 1 XPASS, 0 skip**, 5859 warnings; 467.43s; exit 1. 31 fail schema adherence; 18 fail ngoài nhóm lịch sử. | `test-integration.log`, `test-integration.xml` |
| Toàn Flutter test | `dart flutter_tools.snapshot test --reporter compact` (đường dẫn SDK tuyệt đối như log/lệnh phiên) | **643 pass, 2 fail**, 86s, exit 1. Không có test lịch sử 3.24. | `test-mobile.log` |

Lệnh Flutter đầy đủ từ `frontend/mobile/`: `& 'C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe' 'C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot' test --reporter compact`. Chuyển stdout/stderr vào `../../work/3.25/evidence/test-mobile.log`.

Flutter fail tại `family_tab_screen_test.dart::alert entry displays server unread count and removes it after clear` (không thấy text `1 chưa đọc`) và `redeem_acceptance_test.dart::AC2: valid QR fills code and waits for explicit confirmation` (expected true, actual false). Không sửa frontend; chưa điều tra nguyên nhân hoặc khẳng định đây là regression do 3.25.

Các test unit ngoài file task fail chủ yếu ở contract device-token/catalog-search/notification/profile/OpenAPI semantics và 6 ca profile invalid auth 422 thay vì 401; chưa điều tra nguyên nhân trong phạm vi 3.25. Không coi toàn bộ 32 fail là 32 lỗi mới của task.

18 fail integration ngoài nhóm lịch sử gồm 3 ca alert dispatch trả 401 thay vì 200; 1 ca dose timestamp khác kỳ vọng phút; 3 ca notification snapshot/access có field response ngoài bộ kỳ vọng; 10 ca mobile login/profile về số điện thoại hoặc validation profile; 1 ca profile GET có thêm email. Đây là quan sát assertion, chưa có điều tra root cause hay baseline không có diff task để kết luận nguồn gốc. Không tự sửa sản phẩm/contract/test ngoài phạm vi.

### Scope

`backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage test` lần cuối → **OK, exit 0**; `evidence/test-scope.log`: chỉ workbook tổng là thay đổi file chưa commit thuộc vùng test.

Lần đầu exit 1; giữ log `evidence/test-scope-before-commit.log`:

- `[OK] docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- `[NGOÀI] backend/tests/unit/test_get_adherence_history.py`.

File unit là diff **có sẵn từ implement đã approved**, không được sửa trong phiên test. Sau khi hỏi theo `wf-git`, người dùng cho phép lưu riêng phần implement đó; đã commit `49f2f11` rồi chạy lại scope đúng cùng task ID/stage. Không stash/restore, đổi tên nhánh hoặc sửa checker. Scope cuối pass không thay thế kiểm toàn diff ở review: commit unit vẫn thuộc task và cần review theo plan implement. Không có thay đổi production hoặc file mới ngoài plan ở phiên test.

## 5. Bộ test case Excel

- Spec: `testcases.json`; file task: `testcases.xlsx`; file tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Một chức năng: **FADH — Lịch sử tuân thủ cho người thân**, sheet `Lịch sử tuân thủ người thân`.
- Lệnh từ superproject: `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/testcase_xlsx.py validate 3.25`, `build 3.25`, `merge 3.25`; cả ba exit 0, không cảnh báo xung đột kết quả. `evidence/testcase-xlsx.log`.
- Đã so workbook tổng với snapshot trước gộp: giữ nguyên giá trị, công thức, style_id, number format, merged cells, freeze panes, số chart/image của **20 sheet chức năng cũ**. Hai workbook có đúng ID/trạng thái theo spec và một bug FADH tương ứng một ca Fail. `evidence/testcase-verify.log`.
- Kiểm công thức lưu, không có cell kiểu error và bật `fullCalcOnLoad`; chưa render hoặc chạy recalculation trong Excel. Không tuyên bố đã QA bằng native Excel.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| FADH | 45 | 24 | 1 | 20 |

- TC-FADH-20 Fail, Bug Report sinh **BUG-FADH-20**, ánh xạ cùng một lỗi sản phẩm **BUG-3.25-01**, không phải lỗi thứ hai.
- Pending: TC-FADH-01,06–10 (success/cross-patient/revoke bị contract chặn); 30–31 (nhóm/timezone DB); 33–34 (idempotency/race toàn hành vi); 35–36 (hai biên chưa chạy); 37–38 (AC8 chưa có đặc tả); 39–44 (UI/lifecycle/read-only/E2E). Ca Pending có actual rỗng, không dùng số fail pytest do thiếu schema để gán Fail hành vi chưa kiểm được. TC-FADH-45 Pass cho đối chiếu cấu trúc artifact/workbook, không phải xác nhận contract/UI/E2E đạt.
- Phân lớp EP: quyền hợp lệ/không liên kết/thiếu từng consent/sharing off, mẫu số có/không có liều đủ điều kiện. Bảng quyết định quyền R1–R5; BVA −30/+30/+120, ngày 90/91; chuyển trạng thái pending→missed, quyền allowed→denied và phiên app; đoán lỗi quyền/audit/auth/idempotency/race. Các điểm biên chưa chạy được giữ Pending tường minh.

## 5b. Lỗi sản phẩm tìm thấy

### BUG-3.25-01 — Xác nhận sớm hợp lệ bị loại khỏi lịch sử trước giờ dự kiến

- **Open, Medium**, tái hiện lại trong phiên test, không phải lỗi mới so với implement. Chưa có bằng chứng mất dose_log hoặc lộ dữ liệu; có thể xem lại khi tới giờ dự kiến.
- Kỳ vọng theo requirement AC3 đã duyệt và quyết định người dùng 23/10: lịch 08:00, thực uống 07:30 hợp lệ phải xuất hiện ngay, total=taken=counted=1, rate=100.00, một liều, cả nhóm ngày và thuốc.
- Thực tế unit application lúc `as_of=07:30`: summary 0, rate None, không có nhóm. Hai tham số `delay0` của `test_confirmed_before_deadline_counts_immediately__AC3` fail trong `test-unit.log/xml`.
- Nguyên nhân có bằng chứng code từ implement: `domain/history.py::build_history` chỉ giữ `scheduled_at <= as_of`; SQL reader `sql_adherence.py` cũng lọc tương tự. Phiên test không sửa code; chưa xác nhận tái hiện qua DB/API vì contract chưa đủ.
- Test cũ `test_future_occurrences_including_early_confirmed_are_excluded` và integration `test_early_confirmation_is_excluded_until_scheduled_time__AC6_AC18` giữ kỳ vọng loại xác nhận sớm theo task cũ, khác AC3 mới. Không dùng chúng làm bằng chứng AC3 đạt.
- Chuyển task sở hữu 3.23 xử lý theo workflow bug, xác nhận cả domain và SQL reader. Giữ test mới để chứng minh fail trước/pass sau; bổ sung integration ngay sau xác nhận sớm khi contract 3.23 sẵn sàng. Không sửa sản phẩm trong task kiểm thử này.

Contract thiếu `/adherence`/schema và UI thiếu 3.24 là các phụ thuộc đã biết, không đếm thành bug chức năng mới trong Bug Report. Các fail hồi quy ngoài task có log nhưng chưa đủ điều tra để kết luận nguyên nhân/mức nghiêm trọng.

## 6. Test không ổn định hoặc bị skip

- Bộ lịch sử không skip, không xfail, không retry để đổi kết quả. 31 fail schema được giữ nguyên.
- Bộ unit/architecture tiếp tục sau collection error theo `--continue-on-collection-errors`, không xóa test contract bị lỗi.
- Toàn integration có **1 XPASS**: `test_dose_confirmation_api.py::test_post_doses_batch_requires_authentication__AC9` đã có marker xfail từ task 2.10. Giữ nguyên marker; không thêm xfail trong 3.25. Pytest JUnit ghi ca XPASS như testcase thành công, nên đếm XML là 1053 success, còn output pytest phân biệt 1052 passed + 1 xpassed. 5859 warnings chủ yếu SQLAlchemy `Row.t`/`Row._t` và Starlette TestClient deprecation; không tắt warning để báo sạch.
- Mobile E2E và ca lifecycle thật **chưa được chạy**, không gọi là pytest skip. Không cài app lên thiết bị khi chưa có màn/test production cần kiểm.
- Toàn integration có cơ chế `_VerifyBudget` của `test_mobile_login.py` chờ ngân sách GoTrue 18 verify/300 giây; giữ nguyên cơ chế chống rate-limit, không tăng ngân sách để rút ngắn test.

## 7. Phát sinh

- Sandbox chặn ghi evidence, Git ref và đọc Docker config; đã dùng cơ chế xin quyền tool cho đúng thao tác. Không sửa ACL hoặc dùng nơi lưu thay thế để né sandbox.
- Chỉ file workbook docs thay đổi nội dung mới trong submodule; backend unit diff kế thừa implement giữ nguyên và đã commit riêng sau khi người dùng cho phép. Không chỉnh `.agents`/contract/production, không push hoặc bump gitlink.
- Theo `wf-test`, không bổ sung các ca P5/P7 bằng mô hình/UI/contract giả để làm xanh. P5/P6 có bằng chứng phần chạy được, chưa nghiệm thu các ca bị schema chặn; P3/P4/P7 vẫn Pending; P8 đã dựng/gộp và đối chiếu cấu trúc cuối. Native Excel/render chưa kiểm như đã ghi ở mục 5.

## Bước tiếp theo

- **Chưa sẵn sàng duyệt test đạt toàn bộ AC.** Chờ bản contract 3.23/UI 3.24 đúng nguồn và xử lý BUG-3.25-01 ở task sản phẩm; sau đó tiếp tục các ca Pending và chạy lại những kiểm tra bị ảnh hưởng.
- Scope đã pass sau commit unit được người dùng cho phép. Không còn câu hỏi commit đang chờ; chưa có quyền commit workbook/artifact hoặc push.
- Sau khi đủ bằng chứng và scope exit 0, người duyệt đọc báo cáo rồi chạy `python .agents/scripts/gate.py approve 3.25 test` trong terminal của họ. Agent không chạy approve và không bắt đầu review trong lượt này.
- File chưa commit: docs `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, `work/3.25/` bị ignore. Backend sạch ở commit `49f2f11`; frontend/tests không có thay đổi file mới. Superproject chưa stage/bump gitlink, backend HEAD mới chỉ được ghi trong bằng chứng.
- Lệnh commit còn đề xuất khi được yêu cầu: docs: `git -C docs add -- "Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx"`, `git -C docs commit -m "test(adherence): record PB21 cases and results"`. Artifact: `git add -f -- work/3.25/01-requirement.md work/3.25/03-plan.md work/3.25/04-impl-notes.md work/3.25/05-test-report.md work/3.25/testcases.json work/3.25/testcases.xlsx work/3.25/evidence`, rồi `git commit -m "docs: record task 3.25 test evidence"`. Không stage scratch; không bump gitlink trước khi submodule commit được push theo `wf-git`.
- Tiếp tục bằng: `tiếp tục task 3.25 test`; giữ ID rõ vì nhánh có slug. Không sửa artifact approved để cập nhật tiến độ; trạng thái hiện tại nằm trong báo cáo draft này.
- Cập nhật lần cuối: 2026-10-24 23:30 +0700, Codex. Trạng thái cuối: `evidence/test-final-gate.log`; kiểm kết quả XML/Git và credential patterns: `evidence/test-final-check.log`.
