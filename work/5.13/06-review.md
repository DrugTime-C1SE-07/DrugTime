---
task: 5.13
stage: review
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-10 14:30 +0700
content_hash: sha256:7373b2bdc72d2646
inputs:
  01-requirement.md: sha256:eb0cc2ee1b9c43b1
  02-contract.md: sha256:d57a06a4057ba520
  03-plan.md: sha256:62e63b8e7ead5259
  04-impl-notes.md: sha256:49570617e4a65030
  05-test-report.md: sha256:2ede1e6d13c93c1a
---

# 5.13 · Review

## 1. Kết luận

**Đạt, kèm lưu ý**: 0 Critical, 0 High, 1 Medium, 1 Low trong thay đổi của task. Không phát hiện lỗi buộc reopen implement/test. Không sửa code trong giai đoạn review.

Kết luận áp dụng cho API Backend 5.13, contract và bộ test case; không phải xác nhận toàn suite xanh hay hoàn tất Definition of Done. Vẫn cần ít nhất một người khác approve PR. Đây là lượt tự review bằng agent đã triển khai, chưa phải review độc lập bởi người khác.

## 2. Phạm vi đã review

Đã đối chiếu AC và plan với diff trước khi đọc phần tự thuật 04/05. Đọc các file mới chưa được Git đưa vào diff mặc định, không chỉ diff của file tracked.

| Submodule | Phạm vi và bằng chứng |
|---|---|
| backend | Diff `main...HEAD` kế thừa profile-phone, working diff và nội dung file mới của 5.13: 14 file ứng dụng/migration, 7 unit, 1 architecture, 3 integration. Lưu `evidence/review-backend-inherited.diff`, `evidence/review-backend-working.diff`. |
| api_contract | Working diff README/OpenAPI của 5.13 và diff phone kế thừa so với `origin/main`. Lưu `evidence/review-contract-working.diff`, `evidence/review-contract-inherited.diff`. Local main cũ hơn origin/main; không coi toàn bộ diff lịch sử so với local main là thay đổi 5.13. |
| docs | Workbook tổng: kiểm nội dung chức năng LINKPAT và so hash cell values/formulas của 36 sheet chức năng cũ với snapshot trước merge. Không tuyên bố đã render layout Excel. |
| superproject | Artifact trong work/5.13; không bump con trỏ, commit, push, tạo PR hoặc sửa frontend. |

Kết quả `scope.py 5.13 --stage implement`: **exit 1, chưa pass toàn workspace**, log `evidence/review-implement-scope.log`. 22 file implement và workbook tổng [OK]; 8 [NGOÀI] gồm 2 file contract, 3 integration thuộc các giai đoạn đã approved và 3 Firebase baseline ở frontend. Đây là các thay đổi đã được ghi ở Phát sinh 04/05; review không tạo thêm file sản phẩm ngoài scope. Không thêm các file Firebase vào commit task.

Gate review chạy lại thành công: `evidence/review-gate.log`. Kiểm Excel chạy thật trong review: `testcase_xlsx.py validate 5.13` và `scratch/verify_testcase_book.py`, log `evidence/review-testcase-validate.log`, `evidence/review-testcase-book.log`.

### Lưu ý nhánh trước khi mở PR

Backend HEAD `2d6f3c69b1798b4b37d1bc69633046ab28ce05b9` và contract HEAD `61df4603143bf978a4b1efba18536c2b9fa4c285` đã có thay đổi profile-phone trước task. So với refs main hiện có, Backend có 15 file kế thừa và contract có phần phone tương ứng; workbook docs cũng có lịch sử kế thừa. Thay đổi 5.13 hiện chưa commit. Đây là phụ thuộc nền nhánh, không phải code mới của 5.13.

Chưa fetch remote trong review nên không khẳng định PR trên GitHub hiện sẽ chứa các commit đó. Khi được yêu cầu mở PR, cần refresh refs, đối chiếu main và xử lý thứ tự merge của phần nền trước khi chốt diff PR; không tự rebase, reset hay sửa lịch sử. Giữ nguyên nhánh Backend `feat/list-linked-patients` theo yêu cầu người dùng; superproject hiện ở nhánh cũ, chưa tự chuyển.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC14 có đường code và integration test tương ứng; bảng đối chiếu bên dưới. API phục vụ chọn patient đang có quyền xem, không tạo liên kết hoặc cấp quyền. |
| Phạm vi | Không thay Mobile/Admin, không thêm quyền chia sẻ, không sửa migration đã áp dụng. Scope scan chưa xanh do các file chưa commit của các giai đoạn khác/baseline nêu trên. |
| Contract | GET /family/patients trả items, mỗi mục chỉ có patient_id và patient_full_name nullable. Không nhận query/body; tên trim, rỗng thành null, Unicode codepoint/case-sensitive, null cuối, UUID phân xử. 401/403/422/503 và no-store khớp phạm vi đã duyệt. |
| Bất biến kiến trúc | Use case đặt ở access, gọi family/consent/identity qua public API, không tạo vòng family → access. resolve_access dùng cùng PEP/facts và cả hai consent mỗi request. Route có scope trong registry kiểm kiến trúc. |
| Bảo mật | Không dùng JWT chứa quyền hoặc cache quyết định. Chỉ candidate của caller; bỏ self, active/sharing cần bằng chứng xác nhận hiện có. Admin bị chặn. Tên được đọc sau quyết định quyền. SQL dùng bind parameters. Không thấy secret mới hoặc payload y tế trong code/audit task; không đọc nội dung Firebase baseline. |
| Xử lý lỗi | Allowed audit cùng health UoW; response rời handler sau commit. Lỗi một audit/commit không trả phần danh sách và rollback allowed trước đó. Empty có request audit, admin denied transaction riêng. SQL lỗi được chuyển 503 không lộ SQL; không fabricate tên khi patient biến mất. |
| Migration | Hai migration mới: thêm enum scope trước migration audit. Constraint chỉ nới cho operation danh sách, không mở grant/RLS hay bỏ bảo vệ append-only. Log reset sạch, upgrade có dữ liệu cũ, CHECK và 36 phép sửa/xóa log hỗ trợ kết luận. |
| Hiệu năng | Có N+1 facts/audit theo số patient; xem M1. Names đã batch, candidate không tải toàn bộ patient của hệ thống. |
| Chất lượng test | Có cross-caller, rút quyền với cùng token, khôi phục/link lại, audit/commit fault, schema/quyền DB. Không skip ca của task. Một assertion revoke rộng hơn contract, xem L1. |
| Dễ đọc và nhất quán | Ports/gateway tách đúng tầng; scope mới không mượn scope đọc thuốc/hồ sơ. Không thấy debug print hoặc code chết trong diff task. |
| Đối chiếu 04/05 với log | Số liệu khớp log; baseline failure/skip/lint và scope exit 1 được ghi rõ, không bị biến thành pass. Chi tiết bên dưới. |

### AC và bằng chứng

| AC | Đường thực hiện / kiểm chứng |
|---|---|
| AC1, AC2, AC7, AC9 | Candidate SQL giới hạn caller và quan hệ active có bằng chứng; resolve_access kiểm sharing + family_sharing + health_data. Integration trộn các trạng thái, thiếu từng consent, caller khác, list rỗng và link lại chưa sharing. |
| AC3 | Cùng token gọi lại ngay sau rút từng consent, tắt sharing hoặc revoke; patient bị lọc. Không có cache quyền. |
| AC4, AC6 | Auth hiện có cho 401; admin 403 khong_co_quyen, denied request audit bền vững. Không ghi denied cho candidate chỉ bị lọc. |
| AC5, AC10, AC14 | Scope danh_sach_benh_nhan_lien_ket, mỗi patient trả về một allowed; fault ghi dòng thứ hai và lỗi commit kiểm rollback toàn bộ và không trả dữ liệu một phần. |
| AC8 | Schema strict chỉ ID/tên, test tên trùng, null/blank, Unicode và thứ tự ổn định; không trả email/phone/profile. |
| AC11 | Empty 200 có audit request null subject/link; admin 403 denied độc lập. Fault cả hai nhánh phải fail closed. |
| AC12, AC13 | Reset DB sạch và upgrade trên dữ liệu audit cũ; kiểm enum, constraints, grants/RLS, append-only UPDATE/DELETE/TRUNCATE trên các role. |

Spec Excel hợp lệ: 30 case LINKPAT, 30 Pass/0 Fail/0 Pending, comments truy AC và test đã chạy trong log 75 ca tích hợp. Không có Fail mới cần Bug Report. Kiểm lại workbook trong review xác nhận 36 sheet chức năng cũ giữ nguyên values/formulas và Report có COUNTIF/chart. File tổng không đổi kết quả của chức năng cũ.

### Đối chiếu log

Review này không chạy lại pytest/lint/reset DB; các kết quả dưới đây thuộc implement/test đã approved và đã đọc đối chiếu log trong review.

| Lượt | Kết quả thực tế | Evidence |
|---|---|---|
| Unit task + architecture | 137 passed | implement-task-final.log |
| Toàn unit + architecture | 1964 passed, 11 failed, 1 skipped; 11 lỗi contract cũ tái hiện trên snapshot contract trước task | implement-final-backend.log; implement-contract-baseline.log |
| Full lint | 63 diagnostics ở 13 file không đổi; không phải lint toàn repo pass | implement-final-lint.log; implement-lint-baseline.log |
| Integration task cuối | 75 passed, không fail/skip | test-task-final.log |
| Toàn integration | 1250 passed, 7 failed, 167 skipped, 1 xpassed; ca Unicode thêm sau lượt full đã chạy trong lượt 75 task | test-integration.log |
| Tái hiện baseline integration | Cùng 7 lỗi ở code/contract trước task; DB dùng schema additive hiện tại | test-integration-baseline.log |
| Lý do skip | Fixture auth không lấy được Supabase status phù hợp; 8 ca knowledge thiếu seed. XPASS là marker cũ task 2.10 | test-skip-reasons.log; test-integration.log |
| Lint integration mới | Pass cho cả 3 file | test-task-lint.log |
| Migration | Reset sạch exit 0; upgrade giữ dữ liệu/quyền cũ; CHECK và append-only được kiểm | implement-db-reset.log; implement-db-upgrade.log; test-db-reset.log; test-task-final.log |

Không kết luận 7 failure hoặc 11 failure là do 5.13; cũng không xác nhận toàn bộ hành vi ngoài task đạt. Các hạn chế baseline/môi trường đã được người duyệt chấp nhận ở 04/05, vẫn cần hiển thị trong PR.

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Medium (M1) | backend/src/drugtime/modules/access/application/list_linked_patients.py:39; access/adapters/outbound/facts.py:13 | Mỗi candidate chạy bốn phép đọc facts qua consent/family/identity; mỗi patient được phép thêm một INSERT audit. Tổng số truy vấn tăng tuyến tính, trong khi contract không giới hạn số mục. Không có benchmark chứng minh độ trễ ở danh sách lớn; chưa quan sát timeout thực tế. | Trước khi cần hỗ trợ nhiều liên kết, đo latency/query count ở kích thước đại diện; batch facts/audit trong cùng request/UoW, giữ PEP, không cache quyền và không tự cắt danh sách. Cần reopen plan/implement nếu xử lý trong task này. |
| Low (L1) | backend/tests/integration/test_linked_patients_api.py:109 | Ca revoke chấp nhận cả 200 và 204 dù POST /family/links/{link_id}/revoke trả model 200. Có thể bỏ lọt drift status/body của bước chuẩn bị; assertion request danh sách ngay sau vẫn kiểm thu hồi đúng. | Khi chỉnh test, assert 200 và trạng thái revoked của response đúng contract. Không sửa test đã approved trong review. |

Không có phát hiện Critical/High. Lưu ý nhánh/PR base là điều kiện chuẩn bị PR ở mục 2, không quy thành lỗi runtime của API.

## 5. Mô tả PR

Chưa mở PR; các liên kết dưới đây phải điền URL thật khi được yêu cầu. Mỗi mô tả phải giữ phần baseline/hạn chế, không ghi all tests pass.

### api_contract

**Title:** `feat(contract): define linked patient list API`

Task 5.13: thêm GET /family/patients để người thân chọn bệnh nhân hiện có quyền xem. Chỉ trả ID/tên; yêu cầu liên kết active, chia sẻ bật và cả family_sharing/health_data. Quy định lọc, thứ tự, audit và no-store, cùng 401/403/422/503; không thêm luồng cấp quyền.

Validation: unit contract của task trong lượt 137 pass; HTTP/integration đối chiếu trong lượt 75 pass. Contract có baseline mismatch ngoài task đã nêu ở review. Liên quan: PR Backend, docs và superproject (điền URL thật). Kiểm phần phone kế thừa sau refresh main trước khi chốt diff.

### backend

**Title:** `feat(access): list patients with current caregiver access`

Task 5.13: người thân gọi GET /family/patients nhận đúng bệnh nhân đang được chia sẻ. Kiểm quyền và hai consent ở DB mỗi request; rút quyền loại bệnh nhân ngay lần gọi kế tiếp. Trả ID/tên tối thiểu; ghi audit đúng scope, commit trước response và fail closed khi đọc/ghi audit lỗi. Hai migration additive phục vụ scope và request audit.

Validation: 137 unit/architecture task pass, 75 integration task pass, reset sạch và upgrade giữ audit cũ. Toàn integration: 1250 pass/7 baseline fail/167 skip/1 xpass; unit toàn bộ: 1964 pass/11 baseline fail/1 skip; full lint còn 63 baseline diagnostics. Chi tiết và evidence ở work/5.13. Lưu ý N+1 và assertion revoke trong 06-review. Triển khai migration trước khi bật code mới. Không có AC manual; không thay UI.

Liên quan: PR contract phải merge trước; PR docs cập nhật test case; PR superproject cập nhật pointer sau cùng (điền URL thật). Kiểm commit profile-phone nền trước khi chốt diff.

### docs

**Title:** `test(docs): add linked patient API test cases`

Task 5.13: bổ sung 30 test case LINKPAT và Report tương ứng vào Test_Cases.xlsx, truy AC1–AC14 và 75 integration test đã chạy. Không đổi values/formulas của 36 sheet chức năng cũ. Validate/build/merge bằng testcase_xlsx.py và kiểm nội dung workbook đạt; chưa render layout Excel. Liên quan: PR Backend và superproject (điền URL thật).

### superproject

**Title:** `chore: record task 5.13 artifacts and update submodules`

Task 5.13: lưu requirement/contract/plan/implementation/test/review, test case và evidence; cập nhật pointer contract, Backend, docs tới commit đã push/merge. Không đưa scratch hoặc Firebase baseline vào commit. Ghi URL và SHA merge thật cho các PR liên quan, cùng các baseline failure/skip còn tồn tại. Chưa có pointer mới để ghi ở thời điểm review.

### Thứ tự thực hiện khi người dùng yêu cầu Git

1. Refresh refs và đối chiếu phần nền profile-phone/docs với main; bảo toàn thay đổi chưa commit.
2. Commit/push submodule trước, xác nhận commit có trên remote. Merge contract → backend (bao gồm integration trong backend) → docs workbook → superproject. Không có PR client hoặc tests submodule của task này.
3. Sau squash/rebase merge, dùng SHA đã merge thật để bump pointer; superproject không trỏ tới commit chưa push. Chỉ thực hiện commit/push/mở PR khi người dùng yêu cầu rõ.
4. Cần một người khác approve PR và không còn Critical/High liên quan để đạt DoD. Approval artifact review không thay thế approval PR.

## 6. Ghi chú cho quy trình

- Tên nhánh do người dùng chọn không có mã 5.13; luôn truyền task ID tường minh cho gate/scope, không suy sai từ nhánh superproject cũ.
- Scope scan xét toàn workspace nên hiển thị lại file chưa commit của giai đoạn trước. Ghi rõ từng nhóm và đối chiếu artifact approved; không sửa baseline hoặc khai pass giả.
- Sandbox Git trên Windows có thể không đọc được .git/modules. Diff rỗng hoặc lỗi quyền không phải bằng chứng không có thay đổi; dùng quyền đọc phù hợp rồi kiểm lại.
- Migration/audit request-level là phần phát sinh đã xử lý qua reopen requirement/plan trước implement; không mở rộng tiếp trong review. Hạn chế tự review vẫn cần người review PR độc lập.

## Bước tiếp theo

- Đang chờ: người duyệt xem kết luận, M1/L1 và các hạn chế baseline/PR base.
- Nếu chấp nhận: người duyệt chạy `python .agents/scripts/gate.py approve 5.13 review` trong terminal của mình. Agent không chạy approve.
- Nếu muốn xử lý M1/L1 ngay: người duyệt reopen plan/implement hoặc test tương ứng và duyệt phạm vi trước khi sửa; không sửa artifact approved trực tiếp.
- Sau approval, chỉ commit/push/mở PR khi có yêu cầu rõ; đề xuất lưu artifact/evidence cùng task, loại scratch. Chưa thực hiện các thao tác đó.
- Cập nhật lần cuối: 2026-11-10, Codex.
