---
task: 5.13
stage: test
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-10 14:06 +0700
content_hash: sha256:2ede1e6d13c93c1a
inputs:
  01-requirement.md: sha256:eb0cc2ee1b9c43b1
  02-contract.md: sha256:d57a06a4057ba520
  03-plan.md: sha256:62e63b8e7ead5259
  04-impl-notes.md: sha256:49570617e4a65030
---

# 5.13 · Test tích hợp

## 1. Môi trường

- Postgres 17 / Supabase local project DrugTime-backend, 127.0.0.1:54322; app dùng api_role, fixture dùng kết nối quản trị local; token app session thật.
- Đã chạy `npx supabase@3.1.0 db reset --no-seed` target local, exit 0; log `evidence/test-db-reset.log`. Không dùng DB deploy hoặc đọc env production.
- Backend `feat/list-linked-patients`, giữ nguyên 22 file implement đã approved; stage test chỉ thêm ba file integration trong plan. Docs tạo nhánh `feat/list-linked-patients` để cập nhật đúng workbook testcase-book theo ngoại lệ workflow.

## 2. Kết quả theo tiêu chí chấp nhận

Ba file test: `backend/tests/integration/test_linked_patients_api.py` (API), `test_linked_patients_fail_closed.py` (lỗi), `test_migration_linked_patients.py` (DB). Lượt cuối **75 passed, 0 failed, 0 skipped, 8.22 giây**, log `evidence/test-task-final.log`. Lượt đầu 74 passed ở `evidence/test-task-integration.log`; ca bổ sung kiểm Unicode/blank và token hết hạn đã chạy thật trong lượt cuối.

| AC | Test (tên hàm rút gọn, có suffix AC trong source) | Kết quả |
|---|---|---|
| AC1 | `test_returns_multiple_patients_with_minimal_fields_and_allowed_logs`, `test_unicode_blank_name_order_is_stable` | Pass |
| AC2 | `test_empty_list_and_admin_denial_durable_request_audit` | Pass |
| AC3 | `test_revocation_applies_next_request_with_same_token` × sharing/health_data/family_sharing/revoke | Pass |
| AC4 | `test_missing_invalid_and_deleted_token`, `test_rejects_selectors_and_body_and_returns_no_store`, admin case | Pass |
| AC5 | `test_audit_insert_or_commit_failure_never_returns_partial_list`, `test_database_or_pep_read_failure_returns_503` | Pass |
| AC6 | admin denied trong `test_empty_list_and_admin_denial_durable_request_audit`; denial writer failure 503 | Pass |
| AC7 | `test_filters_unrelated_inactive_unshared_and_missing_consents` × 8 trạng thái; liên kết lại chưa share trong revoke case | Pass |
| AC8 | minimal fields, tên trùng/null/blank/Unicode; selectors/body 422, no-store | Pass |
| AC9 | no_health case và revoke health_data case | Pass |
| AC10 | N allowed đúng actor/subject/scope trước khi response; scope mới ghi được trên DB | Pass |
| AC11 | empty/admin request audit subject/link null, denied sống sau rollback; audit lỗi thì 503 | Pass |
| AC12 | `test_new_scope_and_request_operation_accepted`, `test_old_constraints_and_records_preserved_after_upgrade`, reset sạch của lượt test | Pass |
| AC13 | `test_audit_remains_append_only_for_all_roles` × 36, `test_minimal_grants_and_request_subject_constraints` | Pass |
| AC14 | lỗi allowed thứ hai/lỗi trước commit ⇒ không có allowed commit một phần; filtered không tạo denied | Pass |

Kiểm nâng cấp constraint AC12 dùng bảng tạm clone và DDL migration thật đổi duy nhất tên bảng đích để không hạ cấp/xóa log append-only đang có. Nâng cấp schema đầy đủ từ bản trước task, seed audit cũ rồi CLI apply enum/constraint đã được kiểm ở P7 implement approved; bằng chứng giữ nguyên tại `implement-db-upgrade.log` và snapshot trước/sau. Không gọi kiểm bảng tạm là một lần reset/nâng cấp toàn DB mới.

## 3. Kịch bản chất lượng đã phủ

Được phép và bị loại theo liên kết/consent, thu hồi ngay với cùng token, không lộ chéo caller, fail-closed audit/commit, denied transaction riêng, grant tối thiểu và append-only. API danh sách không có patient selector; thiếu quyền từng patient là lọc/200 rỗng theo contract, selector gửi thêm là 422; không áp 403 của endpoint patient-specific vào bộ lọc.

| Kịch bản | Bằng chứng | Kết quả |
|---|---|---|
| Chéo caller/không có liên kết/thiếu consent/tắt sharing | I2 tương đương: 8 case lọc; chỉ allowed cho patient đủ quyền | Pass |
| Rút từng consent, tắt sharing hoặc revoke rồi gọi ngay | Cùng token, không sleep; khôi phục consent/share và liên kết lại chưa share được kiểm | Pass |
| Admin không vượt quyền và denied bền vững | 403; connection khác đọc được request denied sau rollback handler | Pass |
| Không trả dữ liệu khi audit/commit/PEP lỗi | 6 case fault injection thật qua HTTP và UoW DB, kiểm không có allowed một phần | Pass |
| Schema/append-only/quyền tối thiểu | 36 role/table/mutation + 6 CHECK cases + enum/grants/RLS | Pass |

Idempotency ghi liều, worker race và golden interaction scenarios không bị đổi bởi task. GET này không có idempotency key; mỗi lần xem hợp lệ là một lượt audit mới theo contract. Không thêm test ngoài phạm vi chức năng để làm giả phủ QA ghi liều.

## 4. Toàn bộ bộ test tích hợp

- Lệnh: `backend/.venv/Scripts/python.exe -m pytest tests/integration -q -p no:cacheprovider`, chạy ngoài sandbox trên Windows để socket nội bộ TestClient và DB local hoạt động.
- Kết quả: **1250 passed / 7 failed / 167 skipped / 1 xpassed**, 234.65 giây; **không phải toàn suite pass**. Log: `evidence/test-integration.log`. Full suite được collect trước khi bổ sung ca Unicode; ca bổ sung đã chạy trong lượt task cuối 75/75, không có ca task nào chưa chạy.
- Đã tái chạy riêng bảy lỗi trên Backend HEAD trước task và snapshot contract trước task, xuất vào scratch; **cùng bảy lỗi tái hiện**. DB dùng schema local additive hiện tại; không tuyên bố đã hạ cấp DB cho phép so sánh này. Log `evidence/test-integration-baseline.log`.
- Lint ba file integration mới: PASS (`evidence/test-task-lint.log`). Không sửa code sản phẩm hoặc test cũ để làm full suite xanh.
- Scope exit 1 (`evidence/test-scope.log`): ba file integration mới và workbook testcase-book đều [OK]. 27 [NGOÀI] gồm 22 file implement đã approved, hai file contract đã approved, ba file Firebase baseline. Stage test không sửa lại 27 file đó; scope scan toàn workspace chưa pass vì chúng vẫn chưa commit.

## 5. Bộ test case Excel

- Spec: `work/5.13/testcases.json`; file task: `work/5.13/testcases.xlsx`.
- File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, nhánh docs `feat/list-linked-patients`.
- Chức năng mới `LINKPAT`, sheet `DS bệnh nhân liên kết`; mã/sheet này chưa có trong file tổng trước khi merge.
- Dùng Python hệ thống đã có openpyxl để chạy đúng `testcase_xlsx.py validate`, `build`, `merge`: cả ba exit 0, không cảnh báo ghi đè kết quả cũ; log `evidence/testcase-xlsx.log`. Không cài thư viện vào môi trường project.
- QA sau merge: **36 sheet chức năng cũ giữ nguyên toàn bộ cell values/formulas**, Report được dựng lại theo script; workbook tổng từ 37 thành 38 sheet. File task/master đều có 30 Pass, công thức COUNTIF và chart Report. Log `evidence/testcase-book-verify.log`; snapshot hash trước merge `evidence/testcase-master-before.json`. Không khẳng định đã render/kiểm trực quan layout Excel.

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Danh sách bệnh nhân được theo dõi (LINKPAT) | 30 | 30 | 0 | 0 |

- Thiết kế: EP, bảng quyết định 8 rule về caller/link/sharing/hai consent, biên danh sách rỗng/nhiều phần tử và tên rỗng/Unicode, chuyển trạng thái thu hồi/khôi phục, lỗi hạ tầng và kiểm bảo mật. Endpoint không có giới hạn số lượng/phân trang hoặc trường input có max nên không tự đặt biên max giả.
- Mọi Pass truy về các test đã chạy trong `test-task-final.log`; comments ghi AC/kỹ thuật/tên test. Không có test Pending của chức năng Backend này. Giao diện Mobile nằm ngoài 5.13 nên không đưa thành case đã chạy.
- Không có Bug Report mới cho LINKPAT (0 Fail). Các bug/kết quả của chức năng khác trong workbook tổng được giữ bởi script, không chuyển thành Pass cho đẹp báo cáo.

## 5b. Lỗi sản phẩm tìm thấy

Không phát hiện lỗi sản phẩm của endpoint 5.13 trong 75 ca tích hợp. Có bảy failure ngoài task tái hiện trên baseline code/contract:

| Nhóm / số case | Kỳ vọng và thực tế | Phân loại |
|---|---|---|
| `test_alert_dispatch_api.py` / 3 | Test yêu cầu notification 200 nhưng nhận 401 | Baseline đã tái hiện; nghi vấn fixture auth không khớp dependency/session hiện có, chưa kết luận lỗi sản phẩm 5.13 |
| `test_dose_confirmation_api.py` / 1 | Test chờ scheduled_at cắt phút, sản phẩm giữ microsecond `01:00:59.999000Z` | Baseline đã tái hiện; assertion cũ khác hành vi hiện tại, ngoài luồng danh sách |
| Notification schema/snapshot / 3 | Assertion required-field set cũ không có `medication_name`, `scheduled_at`, response có hai field này | Baseline code/contract đã tái hiện; lệch contract notification ngoài scope task |

Không sửa, skip hoặc giảm assertion các test này. Nếu muốn xử lý trong task này cần reopen artifact liên quan và duyệt phạm vi; không dùng stage test để thay code sản phẩm.

## 6. Test không ổn định hoặc bị skip

- Task suite 75 case: không skip/xfail, không dùng retry hoặc sleep để che lỗi. Không thấy test task không ổn định trong các lượt đã chạy.
- Đã chạy nhóm auth/mobile-login/knowledge-seed/family-consent với `-rs` để lấy lý do thực tế: 7 passed, **167 skipped**, log `evidence/test-skip-reasons.log`. Các skip thuộc fixture auth không đọc được output của lệnh `npx --no-install supabase status -o env` (không có đầy đủ service/status phù hợp fixture hiện có) và 8 ca knowledge seed chưa nạp dữ liệu thật vì reset `--no-seed`. Không tự sửa fixture ngoài plan hay bật remote/service production để làm chúng xanh.
- Một XPASS thuộc `test_post_doses_batch_requires_authentication__AC9`, marker xfail cũ ghi lý do phụ thuộc identity của task 2.10. Ghi là XPASS, không gộp vào số pass thông thường và không sửa marker ngoài scope.

## 7. Phát sinh

Baseline từ implement approved: 11 unit contract failures, 63 lint diagnostics ở các file không đổi, hai file contract và ba file Firebase ngoài stage test. Không sửa/xóa/skip baseline để làm suite xanh. Thiếu openpyxl ở Backend đã giải quyết bằng Python hệ thống sẵn có, không cần cài package.

- Đã giữ nguyên code/migration/unit tests implement approved trong giai đoạn này; chỉ thêm ba file integration theo plan và dùng ngoại lệ testcase-book của AGENTS để cập nhật workbook tổng. Artifact/evidence/scratch nằm trong work/5.13.
- Bản log pytest dài có fixture repr chứa session test nên đã ẩn nguyên fixture repr/JWT/Bearer trước giữ evidence; không đổi lỗi, expected/actual hoặc số lượng test. Baseline rerun dùng `--tb=short` để tránh lặp lại repr. Không lưu token vào testcase/spec/workbook.
- Full integration/baseline và scope toàn workspace vẫn chưa xanh; người duyệt cần xét hạn chế này. Không có lỗi mới trong task buộc reopen implement.

## Bước tiếp theo

- Đang chờ: người duyệt xem report, baseline và các ca skip ngoài task. AC1–AC14 của 5.13 có test chạy thật, 75 task tests và 30 test case Excel đạt; không còn case task Pending.
- Nếu người duyệt chấp nhận các hạn chế baseline/môi trường ngoài task: chạy `python .agents/scripts/gate.py approve 5.13 test` trong terminal của người duyệt. Sau đó agent dùng wf-review, không tự chuyển sang review trong lượt test này.
- Nếu cần sửa lỗi sản phẩm/contract ngoài task: reopen artifact đúng giai đoạn và duyệt scope trước; không tự sửa code trong stage test. Không commit/push.
- Cập nhật lần cuối: 2026-11-10, Codex.
