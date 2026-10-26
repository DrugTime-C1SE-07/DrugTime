---
task: 3.25
stage: review
status: draft
---

# 3.25 · Review kiểm thử lịch sử tuân thủ cho người thân

## 1. Kết luận

**Chưa đạt** — 0 Critical, 3 High, 1 Medium, 0 Low. Chưa đủ bằng chứng nghiệm thu PB21 hoặc mở PR sẵn sàng merge. Các High bên dưới là chặn nghiệm thu AC/bằng chứng vùng rủi ro; không phải ba lỗi sản phẩm mới. BUG-3.25-01 đã được ghi ở implement/test vẫn giữ mức sản phẩm Medium vì có cách tránh; review xếp việc AC3 chưa đạt là High theo `wf-review`.

Gate review được phép chạy. Requirement/plan/implement/test đều approved theo gate, nhưng approval giai đoạn không làm các kết quả Fail/Pending thành Pass. Không sửa artifact approved hoặc production code trong phiên review.

## 2. Phạm vi đã review

Đã đọc requirement AC1–AC9, bảng file/checklist của plan; toàn bộ diff text từ main tới HEAD ở backend/frontend/tests; đối chiếu workbook nhị phân bằng nội dung và style; đọc 04/05 và kiểm log/XML. Không mở PR/commit/push/bump gitlink.

| Submodule | Lệnh diff / mốc đối chiếu | Kết quả phân biệt phạm vi |
|---|---|---|
| backend | `git -C backend diff main...HEAD`; `git -C backend diff d88af5c HEAD` | 2 file so main: acceptance redeem 3.15 và unit history. Delta riêng 3.25 chỉ `tests/unit/test_get_adherence_history.py`, commit `49f2f114e323af660c5d797c7af910cf6400872d`. |
| frontend | `git -C frontend diff main...HEAD`; `git -C frontend diff f9ff263 HEAD` | 7 file về redeem, metadata/dependencies đã có ở baseline; delta 3.25 rỗng. HEAD `f9ff26350e65f790ae60e26f0da7c23acb7aa4a8`. |
| tests | `git -C tests diff main...HEAD`; `git -C tests diff ac207f4 HEAD` | 3 file text redeem đã đọc; 2 file pyc là binary cũ. Delta 3.25 rỗng. HEAD `ac207f40cd2f78508a79b12150e83569b939cf4c`. |
| docs | `git -C docs diff main...HEAD`; `git -C docs diff HEAD -- "Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx"` | Workbook đã có thay đổi cũ so main. Delta 3.25 là workbook chưa commit, so trực tiếp với blob HEAD `b8d7bea4d5b97f468fcdff7d114ad366dae16e36`: thêm FADH và cập nhật Report, giữ 20 sheet chức năng cũ. |
| api_contract | Đọc `openapi.json`, không sửa | HEAD `aaf5eee8e7212fbbd0a53e772c404325698fa76d`; không có `/adherence` hoặc schema bắt đầu `Adherence`. |

`backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage implement` → exit 0, `evidence/review-scope-implement.log`. Scope chỉ thấy workbook chưa commit; dòng `[CHƯA SỬA]` của unit không có nghĩa test chưa viết: thay đổi đã nằm trong commit `49f2f11` và được review riêng bằng diff baseline. Không dùng scope để miễn kiểm commit hoặc gán các file kế thừa 3.15 thành thay đổi mới của 3.25.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1 chưa nghiệm thu; AC2 một phần; AC3 Fail tại xác nhận sớm; AC4 thiếu ca đổi patient sau thành công; AC5 chưa thực hiện thu hồi; AC6 thiếu UI/test; AC7 có 5 ca integration Pass trong evidence trước; AC8 có báo rõ phần chưa nghiệm thu; AC9 đạt phần truy vết/workbook nhưng tiền đề contract/UI còn thiếu. |
| Phạm vi | Delta riêng task chỉ unit history và workbook đúng plan; không sửa production/schema/contract. Các thay đổi kế thừa đã đối chiếu baseline, không tự đưa vào PR 3.25. |
| Contract | Chưa thể xác nhận tương thích: contract chuẩn thiếu path/schema. 31 ca history integration dừng ở `AdherenceByDateResponse`; unit contract có collection error `/adherence`. Không thay bằng generated OpenAPI hoặc model production. |
| Bất biến kiến trúc | Mã hiện có gọi `AccessGuardAdapter → access.authorize` trước reader; facts được đọc mỗi lần, allowed audit cùng transaction và denied qua writer riêng; route có `x-health-scope`/audit-self/no-store. Unit/health-route chạy lại phù hợp. Chưa đủ integration Pass cho success/cross-patient/revoke, nên không kết luận mọi bất biến đã được chứng minh. Task không thay Worker/schema/interaction engine/module dependency/client data path. |
| Bảo mật | Test mới dùng ID sinh ngẫu nhiên, tên thuốc giả, không thêm credential hoặc in lịch sử. Unit `access=Mock()` chỉ là cô lập tính toán, không chứng minh quyền DB. Các ca unauthorized/fail-closed có bằng chứng trước; khoảng trống cross-patient/revoke và RAM còn là High. Không phát hiện lỗ hổng mới từ delta task; chưa thể xác nhận an toàn toàn luồng. |
| Xử lý lỗi | Các test reader/audit failure không biến lỗi thành lịch sử rỗng; unit/route đã chạy lại. 5 ca integration fail-closed/rollback có XML trước chứng minh; không chạy lại DB trong review. Không nới assertion/skip/xfail để đổi kết quả. |
| Hiệu năng | Không thêm đường production/truy vấn/N+1; unit có kiểm một lệnh SQL chỉ đọc. Không có benchmark/load test trong phạm vi review. |
| Chất lượng test | 24 ca mới có oracle cụ thể cho date/medication, fixed clock, Decimal, đúng +120/+1µs, mẫu số rỗng, QD-10 và sync muộn. Lần chạy lại: 22 Pass, 2 Fail trong nhóm mới. Test sớm cũ vẫn khẳng định điều ngược AC3, cần xử lý ở task sản phẩm. Ca Mobile/E2E chưa tồn tại. Bước Excel có lệch cụ thể R4. |
| Dễ đọc và nhất quán | Helper unit theo pattern application hiện có; không debug/TODO mới. Ruff check và format file thay đổi Pass; `git diff --check main...HEAD` backend exit 0. |
| Đối chiếu 04/05 với log | Tổng XML khớp báo cáo; 24 Pass/1 Fail/20 Pending của spec và workbook khớp nguồn. Không có Pass tự động thiếu XML tương ứng; TC-FADH-45 là kiểm cấu trúc thủ công có log, không phải Pass API/UI. 20 Pending có actual rỗng. |

### Checklist endpoint sức khỏe (`wf-health-endpoint`)

- PEP có sẵn, patient selector được chuyển vào authorize trước reader: đã đối chiếu code; unit xác minh thứ tự và không đọc khi bị chặn.
- Consent/link/sharing đọc lại mỗi request: code hiện có, unit không cache Pass; integration thu hồi cùng token chưa chạy tới mutation (R2).
- Allowed audit fail-closed; denied writer tách giao dịch; response no-store/tối thiểu: code và 5 ca lỗi/rollback trong log cũ phù hợp; success schema chưa xác minh.
- 403 cho denied và 401 cho xác thực có bằng chứng; wire success contract còn thiếu.
- Registry health route được kiểm lại trong phiên. Chưa đạt điều kiện đủ các ca integration sức khỏe đã chạy và Pass; không đánh dấu checklist bảo mật hoàn tất.

### Kiểm tra thực hiện trong phiên review

| Kiểm tra | Lệnh | Kết quả / evidence |
|---|---|---|
| Gate | `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/gate.py 3.25 review` | exit 0; `evidence/review-gate.log`. |
| Scope implement | `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage implement` | exit 0; `evidence/review-scope-implement.log`; giới hạn committed diff như mục 2. |
| Validate testcase | `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/testcase_xlsx.py validate 3.25` | exit 0, 45 ca: 24 Pass/1 Fail/20 Pending; `evidence/review-testcase-validate.log`. |
| Unit lịch sử/PEP/route | Từ backend: `.venv/Scripts/python.exe -X utf8 -m pytest tests/unit/test_get_adherence_history.py tests/unit/test_adherence_history.py tests/unit/test_access_authorize.py tests/unit/test_adherence_history_http.py tests/architecture/test_health_route_enforcement.py -q -p no:cacheprovider --junitxml=../work/3.25/evidence/review-unit.xml` | **118 Pass, 2 Fail, 1 warning**, 12.73s, exit 1; `evidence/review-unit.log`, `review-unit.xml`. Hai Fail đều delay0 (−30 phút), date/medication; không có DB/API thật trong lần này. |
| Lint | Từ backend: `.venv/Scripts/python.exe -X utf8 -m ruff check tests/unit/test_get_adherence_history.py` | exit 0; `evidence/review-lint.log`. |
| Format | Từ backend: `.venv/Scripts/python.exe -X utf8 -m ruff format --check tests/unit/test_get_adherence_history.py` | exit 0; `evidence/review-format.log`. |
| Whitespace | `git -C backend diff --check main...HEAD` | exit 0; `evidence/review-diff-check.log` ghi `exit_code=0`, không có lỗi whitespace. |
| Đối chiếu độc lập Git/XML/workbook | `backend/.venv/Scripts/python.exe -X utf8 work/3.25/scratch/review_audit.py` | exit 0; `evidence/review-audit.log`. Đọc blob workbook docs HEAD bằng Git, so 20 sheet cũ (values/formulas/style/format/merge/pane/chart/image), so IDs/result/evidence của mọi ca Pass/Fail. Không sửa Excel. |

Bằng chứng trước đây được đọc lại, **không phải test chạy mới trong review**:

| Bộ | Đếm lại từ XML / đối chiếu stdout |
|---|---|
| `test-history` | 60 ca = 29 success + 31 failure; cả 31 failure chứa schema thiếu `AdherenceByDateResponse`. |
| `test-unit` | 1366 ca = 1333 success + 32 failure + 1 collection error. Trong 24 ca mới: 22 success/2 failure. |
| `test-integration` | 1102 ca XML = 1053 success + 49 failure. Stdout phân biệt **1052 passed + 1 xpassed**, không phải 1053 passed sạch. Không có skip XML. |
| Flutter | `test-mobile.log`: 643 Pass, 2 Fail. Hai lỗi ở family unread count và QR redeem 3.15; chưa có baseline để gán nguyên nhân cho 3.25. Chưa chạy lại Flutter trong review. |

Workbook task/master đều chứa đúng 45 ID/trạng thái như spec và một BUG-FADH-20 ánh xạ BUG-3.25-01. Các ô không có stored error, fullCalcOnLoad bật. Chưa render hoặc kiểm recalculation trong Excel; đối chiếu cấu trúc không chứng minh bố cục hay cached formula values. Không sửa workbook trong review.

## 4. Phát hiện

| ID / mức | Vị trí | Vấn đề, ảnh hưởng | Đề xuất |
|---|---|---|---|
| R1 · High | `backend/tests/unit/test_get_adherence_history.py:188`, assertion dòng 197; `backend/src/drugtime/modules/adherence/domain/history.py:153`; `backend/src/drugtime/modules/adherence/adapters/outbound/sql_adherence.py:77` | **AC3 vẫn Fail:** lịch 08:00, xác nhận hợp lệ 07:30, đọc ngay 07:30 trả total/count=0/rate=None thay vì 1/100%. Tái hiện lại cả date/medication. Đây là BUG-3.25-01 đã biết (mức sản phẩm Medium); AC chưa đạt là chặn nghiệm thu High. `backend/tests/unit/test_adherence_history.py:90` và integration `test_adherence_history_api.py:359` còn kỳ vọng loại liều sớm, ngược requirement mới. | Task sở hữu 3.23 xử lý cả domain + SQL và kỳ vọng cũ theo workflow bug; giữ test 3.25 đỏ trước/xanh sau. Bổ sung ca API/DB family đọc ngay sau xác nhận sớm rồi chạy hồi quy. Không sửa sản phẩm trong task test 3.25. |
| R2 · High | `backend/tests/integration/test_adherence_history_api.py:44`; `backend/tests/integration/test_adherence_history_access.py:121`, `:137`; `api_contract/openapi.json`; `work/3.25/testcases.json:178` | **Thiếu bằng chứng các AC quan trọng/vùng rủi ro:** contract không có `/adherence`/schema; 31 failure và collection error vẫn tồn tại. Test sửa patient_id dừng trước đọc Q; cả bốn ca thu hồi dừng trước mutation. Do đó chưa chứng minh AC1, phần integration AC2/AC3, phần cross-patient AC4, AC5, idempotency/race lịch sử. Đây là phụ thuộc và khoảng trống nghiệm thu, chưa phải bằng chứng endpoint lộ dữ liệu. | Nhận contract đúng nguồn từ 3.23, kiểm phiên bản rồi hoàn tất P5/P6 theo plan; chạy success/cross-patient/thu hồi từng consent/sharing/unlink cùng token và đối chiếu audit thật. Giữ assert_contract, không bỏ schema check hoặc thay contract bằng model production. AC8 tiếp tục ghi rõ phần contract chưa biểu diễn. |
| R3 · High | `work/3.25/testcases.json:667` (TC-FADH-39–43), `:747` (TC-FADH-44); `frontend/mobile/lib/features/adherence_history/.gitkeep` | **AC6 chưa có test/bằng chứng:** checkout không có UI/controller/repository production 3.24. Chưa có test đổi patient/offline/background/logout/403, loại response muộn, không lưu bền/read-only; E2E lịch sử chưa viết/chạy. Không thể nghiệm thu quyền riêng tư dữ liệu phiên từ Flutter hồi quy redeem/family khác. | Khi 3.24 có đúng checkout, hoàn tất P3/P4 unit/widget và Flutter integration test trong implement; tiếp tục P7 local Mobile→API→DB cùng manual lifecycle thiết bị ở test. Giữ Pending cho tới khi có log thực. |
| R4 · Medium | `work/3.25/testcases.json:118`, `:178`, `:606`; hai workbook sheet `Lịch sử tuân thủ người thân`, TC-FADH-02 (row 10), TC-FADH-06 (row 14), TC-FADH-35 (row 43) | **Các bước case chưa tái hiện được đúng kỳ vọng:** TC02 vừa đòi F active với P vừa nói không liên kết; không có bước bỏ liên kết. TC06 data=Q/expected 403 nhưng steps chỉ GET P nên bỏ request tamper sang Q. TC35 chỉ GET lịch sử nhưng expected từ chối xác nhận trước −30, chưa có bước gửi xác nhận/tạo dữ liệu thích hợp. Các trạng thái hiện tại có XML hoặc Pending trung thực, nhưng người chạy tay theo steps sẽ kiểm sai nhánh. | Sau khi mở lại test, sửa precondition/steps từng case cho đúng một tình trạng, tách request P thành công và request Q bị chặn; định nghĩa thao tác xác nhận theo contract chuẩn cho TC35. Dựng/gộp workbook lại bằng script chuẩn, giữ ID/trạng thái chỉ theo evidence. Không đổi các ca này thành Pass khi chưa chạy. |

Không đếm các fail hồi quy ngoài task thành lỗi 3.25 mới khi chưa có điều tra/baseline. Các file pyc và dependency/metadata trong diff kế thừa 3.15 cần được chủ task đó xử lý khi chuẩn bị PR; review này không tự sửa hoặc xóa chúng.

## 5. Mô tả PR

Chưa soạn mô tả PR sẵn sàng merge vì kết luận Chưa đạt và còn High theo `wf-review` bước 7. Khi xử lý xong, review lại rồi soạn PR cho từng submodule thực sự có delta và superproject. Không đưa các commit kế thừa 3.15 vào phạm vi 3.25 mà không rà lại base/merge order. Thứ tự dự kiến theo vai trò: backend → frontend nếu có test mới → tests nếu có runner mới → docs workbook → superproject; nếu contract 3.23 thay đổi thì merge phụ thuộc đó trước.

## 6. Ghi chú cho quy trình

- `05` đã được đọc khi khôi phục tiến độ trước khi đọc hết diff, lệch thứ tự blind review của skill. Đã kiểm chứng riêng bằng toàn diff, chạy lại pytest, đối chiếu XML và workbook từ blob Git; không mô tả đây là blind review hoàn toàn.
- Artifact 04/05 approved vẫn có mục Bước tiếp theo cũ nói đang chờ duyệt. Trạng thái hiện hành lấy từ gate/frontmatter; không sửa artifact approved để cập nhật câu chữ.
- Scope chỉ thấy uncommitted files, không thay thế committed diff. Approval chỉ là cho qua giai đoạn, không phải kết quả Pass các AC còn thiếu. Không áp dụng tự động approve/reopen từ agent.
- Sandbox từ chối ghi evidence ở lượt đầu; đã xin escalation cho các lệnh ghi đúng `work/3.25`, không sửa ACL/đổi nơi lưu để né kiểm soát.

## 7. Phát sinh và kiểm tra cuối

- Kiểm tra bàn giao cuối exit 0: evidence/review-handoff-check.log xác minh review draft, 3 High/1 Medium, đủ log dẫn chiếu, vị trí ba hàng workbook và Git status. Hai lượt kiểm tra hỗ trợ trước bị lỗi mã hóa stdin và chưa có file log cho lệnh diff không output; giữ riêng log lỗi, đã chạy lại kiểm tra bằng script lưu UTF-8 và ghi rõ exit code. Không phải lỗi test sản phẩm.

- `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage review` → **exit 1**; `evidence/review-scope.log` ghi nguyên văn: `[NGOÀI] docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` và `CHẶN: 1 file ngoài phạm vi. Ghi vào mục 'Phát sinh' và hỏi người dùng.`
- Đây là workbook đã thay đổi trong giai đoạn test approved, có trong bảng file của plan; không phải file được sửa ở review. Đã đối chiếu blob docs HEAD và baseline để xác định nguồn. Scope review không cho sửa workbook; không tự commit/stash/restore/chỉnh checker để làm scope xanh.
- Đã xử lý sau khi người dùng yêu cầu commit ngày 25/10/2026: docs commit `3077e2e18c0c6e79827261faf06c80aa945eb98f`, `test(adherence): record PB21 cases and results`, footer `Refs: 3.25`, chỉ workbook PB21. Kiểm lại workbook trước commit exit 0; docs working tree sạch, scope review sau commit exit 0. Evidence: `commit-workbook-check.log`, `commit-workbook.log`, `commit-workbook-details.log`, `commit-workbook-status.log`, `review-scope-after-workbook-commit.log`. R1–R3 vẫn High; chưa push hoặc bump gitlink.
- Gate cuối của phiên review trước cho biết 01/03/04/05 approved, 06 draft; `evidence/review-final-gate.log`. Bàn giao theo `wf-handoff`; tiến độ và lệnh tiếp tục nằm trong mục dưới. Không sửa các mục Bước tiếp theo cũ của artifact approved.

## Bước tiếp theo

- Người dùng đã mở lại implement và cho phép commit riêng workbook. Gate hiện tại: 01/03 approved, 04 draft, 05 approved, 06 draft; giai đoạn kế tiếp implement (`evidence/commit-final-gate.log`). Phụ thuộc contract 3.23/UI 3.24 và R1–R4 vẫn chưa xử lý; kết luận review giữ Chưa đạt.
- Implement đã được mở lại. Phiên tiếp tục chạy gate implement, kiểm lại phụ thuộc rồi làm P3/P4 và bổ sung kiểm chứng AC3 trong phạm vi khi đủ tiền đề. Khi implement hoàn thiện và được duyệt lại, mở lại test bằng `python .agents/scripts/gate.py reopen 3.25 test`, xử lý R2/R4/P7 và chạy lại các bộ bị ảnh hưởng. Agent không tự chạy reopen hay sửa 01/03/04/05 approved.
- BUG-3.25-01 thuộc task sản phẩm riêng; không mở rộng 3.25 thành sửa domain/SQL. Nhận contract/UI đúng nguồn rồi kiểm lại baseline và phạm vi trước khi tiếp tục. Nếu chưa có phụ thuộc, giữ các Pending và kết luận Chưa đạt.
- Sau khi tất cả High được xử lý: cập nhật review còn draft, chạy gate/scope/validate và kiểm chứng lại; chỉ khi kết luận đạt thì người duyệt chạy `python .agents/scripts/gate.py approve 3.25 review`. Không dùng approve review để biến Fail/Pending thành nghiệm thu.
- Tệp chưa commit: docs đã sạch sau commit `3077e2e`; superproject `work/3.25/` bị ignore (review/evidence mới cùng artifact cũ). Backend/frontend/tests sạch ở mức file; gitlink backend/docs/frontend/tests khác HEAD superproject đã có từ trước. Không stage/bump gitlink trong review.
- Workbook đã commit theo yêu cầu; chưa có yêu cầu commit artifact. Lệnh artifact chỉ đề xuất: `git add -f -- work/3.25/01-requirement.md work/3.25/03-plan.md work/3.25/04-impl-notes.md work/3.25/05-test-report.md work/3.25/06-review.md work/3.25/testcases.json work/3.25/testcases.xlsx work/3.25/evidence`, rồi `git commit -m "docs: record task 3.25 review findings"`. Không stage scratch. Chỉ push khi được yêu cầu; chỉ bump sau khi commit submodule đã có trên remote theo wf-git.
- Tiếp tục bằng: `tiếp tục task 3.25` (implement đã mở lại), kiểm lại các phụ thuộc trước khi viết test còn thiếu; phiên sau chạy gate trước, đọc review này.
- Cập nhật lần cuối: 2026-10-25, Codex.



