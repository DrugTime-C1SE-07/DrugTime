---
task: 3.23-adherence-family-consent
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-21 19:14 +0700
content_hash: sha256:bc45764fd5ea65fd
inputs:
  01-requirement.md: sha256:59d6784f453d27aa
  02-contract.md: sha256:e50bcda374a39752
  03-plan.md: sha256:50da5a783bd24265
  04-impl-notes.md: sha256:8b2da5c24bddbce8
  05-test-report.md: sha256:ea2f0480b2c00db3
---

# 3.23-adherence-family-consent · Review

## 1. Kết luận

**Đạt, kèm lưu ý** đối với thay đổi của task: 0 Critical, 0 High, 2 Medium về kiểm chứng/phạm vi phát hành, 0 Low. Không phát hiện lỗi sản phẩm mới cần sửa trong diff task. Chưa kết luận toàn repo xanh hoặc đủ điều kiện merge.

BUG-ADHERENCE-14 đã được xử lý: admin-self bị 403 và có denied vai admin; migration chỉ cho phép tổ hợp audit này, không cho admin-self allowed. Bằng chứng 85 ca liên quan pass và đối chiếu trực tiếp code/SQL/test.

Đây là lượt tự review trong cùng phiên đã implement; không thay thế người khác approve PR theo Definition of Done.

## 2. Phạm vi đã review

| Submodule | Diff và phạm vi |
|---|---|
| backend | `git diff main...HEAD` không có commit mới; đọc toàn bộ `git diff` của rules, 3 unit test, test API; đọc cả 2 file untracked: migration và test actor identity. Tổng 7 file task. |
| api_contract | Đọc toàn bộ diff working tree openapi.json (552 dòng thêm, 1 dòng sửa): GET /adherence, 7 schema, tag và quy ước groups/summary. HEAD bằng origin/main tại a2fcb3e; local main chậm 10 commit nên diff main...HEAD lớn là baseline đã có trên remote, không phải thay đổi task. |
| docs | Workbook: sheet ADHERENCE 23 ca và Report; đối chiếu spec với từng expected/actual/status. Sheet chức năng khác giữ nguyên theo log preservation. HEAD bằng local main tại ec1d67d; so origin/main còn kế thừa tài liệu quyết định và workbook alert-dispatch từ trước task, ghi ở M2. |
| superproject | Artifact trong work/3.23-adherence-family-consent; chưa stage/commit/bump con trỏ. Không review các thay đổi frontend hoặc task khác để đưa vào PR này. |

Đọc thêm đường chạy hiện hữu: history_http → get_adherence_history → AccessGuardAdapter → access.authorize → facts/consent/family/identity; SqlAdherenceHistory; SQL audit; schema response; registry CI health route và các caller dùng PEP.

Kết quả `scope.py --stage implement` trong lượt review: **exit 1**, 3 file ngoài phạm vi: hai file integration thuộc giai đoạn test đã duyệt và tài liệu quyết định trên nhánh docs. Các file sản phẩm/migration/unit/contract và workbook được nhận đúng. Log: `evidence/review-scope.log`. Không báo scope pass; không sửa .agents hay thao tác Git để che kết quả.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC9 có test và code tương ứng. Self/family đúng consent; unlinked/sharing-off/missing consent/cross-patient/admin bị từ chối. Rút quyền đọc lại DB ở request kế tiếp. |
| Phạm vi | Thay đổi task khớp 9 file của plan. Scope gốc không phân biệt giai đoạn; có thay đổi kế thừa docs cần xử lý trước PR, M2. |
| Contract | Path/query/auth/status/header và schema khớp runtime theo test; fingerprint file hiện tại khớp approved_files của 02-contract (thuật toán file-NUL + bytes). Không thay contract sau duyệt. |
| Bất biến kiến trúc | Guard trước reader; patient selector được đối chiếu; JWT chỉ giải danh tính, user role lấy từ DB; consent/link không cache. Allowed audit cùng transaction, denied transaction riêng. Route đã có registry; không thêm import giữa module. |
| Bảo mật | SQL bind tham số; response model chọn trường, no-store; không thêm credential/PHI/log payload trong diff sản phẩm. Migration không cấp quyền hoặc thay RLS; admin-self allowed bị CHECK chặn, mutation audit bị chặn cả chủ bảng. |
| Xử lý lỗi | Audit/permission/commit lỗi fail-closed; dữ liệu không trả khi lỗi. BEGIN/COMMIT bảo vệ thay CHECK; dữ liệu cũ hợp lệ vẫn hợp lệ. Patient không tồn tại giữ 403 không audit do FK, đúng contract. |
| Hiệu năng | Không thêm truy vấn/N+1/index requirement. Migration cần khóa/validate bảng access_logs; áp dụng trước app, thời gian khóa production chưa đo. |
| Chất lượng test | Regression trước/sau có thật; API kiểm 403/body/no-store/audit/không đổi liều. Matrix kiểm SQLSTATE CHECK và rollback; mutation kiểm permission/trigger rõ. Full suite lỗi/skip được công khai, M1. |
| Dễ đọc và nhất quán | Sửa tại quy tắc chung; migration một mục đích, giữ biểu thức cũ và một ngoại lệ; tái sử dụng fixture. Không dependency hay abstraction mới trong sản phẩm. |
| Đối chiếu 04/05 với log | Đã mở log và đối chiếu 85 pass; 803 pass/2 fail/159 skip/1 xpass; 1183 pass/34 fail unit; bảo toàn 63 audit/grant/trigger và matrix16. Số liệu khớp, không bỏ qua fail/skip. |
| Test case Excel | Validate exit0, 23 Pass/0 Fail/0 Pending; master expected/actual/status khớp spec. AC đều có ca. BUG-ADHERENCE-14 có lịch sử fail và hồi quy pass; không còn bug fail trong sheet task. |

### Kiểm tra bổ sung trong lượt review

- `scratch/review_self_selector.py`: gọi API thật trên DB task local bằng token thử, so request bỏ patient_id với truyền UUID chính mình. Hai response giống nhau và có hai allowed audit vai patient. Pass: `evidence/review-self-selector.log`.
- Validate spec: `evidence/review-testcase-validate.log`.
- Fingerprint contract và đối chiếu master workbook: `evidence/review-contract-workbook.log`. Fingerprint approval dùng tiền tố `file\0` (theo implementation từng tạo manifest), không phải SHA-256 thuần bytes.
- Không chạy lại toàn bộ suite vì code sản phẩm không thay đổi sau lượt test được duyệt; dùng log hiện có và thêm đúng phép kiểm selector cần xác nhận.
- Không thực hiện deploy/kiểm môi trường production hoặc sửa code ở giai đoạn review.

## 4. Phát hiện và lưu ý

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Medium — kiểm chứng | `work/3.23-adherence-family-consent/05-test-report.md:63`, `:69`, `:119` | Repo chưa có kết quả full suite xanh: 2 fail integration (dose timestamp/profile), 34 fail unit ngoài phần sửa, 159 Auth skip vì CLI; chưa xác nhận baseline sạch. Không phải phát hiện hồi quy mới từ migration, nhưng giới hạn kết luận phát hành. | Người review PR quyết định gate CI/baseline cho lỗi hiện có; bổ sung Supabase Auth/CLI để chạy ca skip khi đủ môi trường. Không sửa hoặc skip thêm test để làm xanh. |
| Medium — phạm vi PR | `work/3.23-adherence-family-consent/evidence/review-scope.log:10`; nhánh docs `ec1d67d` so `origin/main=dfd422f` | Scope vẫn bị chặn bởi integration đã duyệt; docs còn commit kế thừa ngoài task (tài liệu quyết định, alert-dispatch workbook). Tạo PR trực tiếp theo mọi thay đổi nhánh có thể đưa cả nội dung ngoài task vào PR. | Trước khi tạo PR, xác nhận baseline/commit docs kế thừa đã được xử lý hoặc chọn checkout/nhánh phù hợp để PR chỉ mang workbook task; không tự sửa lịch sử, reset hoặc sửa .agents. Giữ log scope làm bằng chứng và nêu giới hạn trong PR. |

Không yêu cầu reopen implement vì không tìm thấy Critical/High mới trong thay đổi task. Các lưu ý trên chưa được coi đã giải quyết bằng review này.

## 5. Mô tả PR dự thảo

Chưa tạo PR, chưa commit/push. Điền URL các PR liên quan khi người dùng yêu cầu tạo; không dùng placeholder làm liên kết thật.

### api_contract

**Title:** `feat(contract): document consent-scoped adherence history`

GET /adherence công bố patient selector, nhóm ngày/thuốc, consent/link ở mỗi request, audit fail-closed và no-store. Bổ sung schema và ví dụ; giữ response của endpoint hiện hữu. AC1–AC9; kiểm OpenAPI/runtime và response trên wire đã pass.

Liên quan backend 3.23. Không đưa các commit vốn đã có trên origin/main vào phần mô tả thay đổi task. Merge contract trước backend.

### backend

**Title:** `fix(access): deny admin health access and preserve denied audits`

Admin có consent tự truy cập hoặc có liên kết người thân trước đây có thể qua nhánh cho phép của PEP. Từ chối admin sau kiểm patient tồn tại, trước self/family. Migration mới cho phép ghi riêng audit denied admin-self để API trả 403 đúng thay vì 500 do CHECK.

Không đổi route, reader, schema response, consent flow hoặc grant. Bảo toàn audit cũ và append-only; deploy migration trước app.

Validation: 85 ca integration của task pass; 16 tổ hợp CHECK và 9 ca mutation; 2 test contract runtime pass; 23 testcase Excel pass. Full integration 803 pass/2 fail/159 skip/1 xpass; unit+architecture 1183 pass/34 fail; lint task pass, lint toàn repo còn66 lỗi ngoài phần sửa. Nêu rõ các log và giới hạn M1/M2 trong PR.

Lệnh trọng tâm: `pytest tests/integration/test_access_log_actor_identity.py tests/integration/test_adherence_history_access.py tests/integration/test_adherence_history_api.py`; chỉ DB local sạch, app api_role. Không có AC manual bắt buộc. PR liên quan contract và workbook docs.

### docs

**Title:** `test(adherence): record consent and audit regression cases`

Gộp sheet ADHERENCE 23 ca Pass, gồm quyền/thu hồi/cross-patient/audit/constraint/append-only và cập nhật Report. Đối chiếu spec/evidence; giữ values/formulas/styles/merged cells của chức năng khác. Chỉ đưa workbook task vào PR sau khi xử lý baseline kế thừa ở M2; không gộp tài liệu quyết định ngoài task vào PR này.

### superproject

**Title:** `chore: deliver adherence consent artifacts and submodule pointers`

Lưu artifact/evidence của 3.23 và bump đúng các submodule đã commit/push, đã xác nhận SHA có trên remote. Không stage frontend, .agents hoặc work của task khác. Đính kèm URL PR contract/backend/docs. Merge superproject sau các PR thành phần; nếu squash/rebase đổi SHA thì cập nhật con trỏ về commit merge thật.

**Thứ tự:** contract → backend (bao gồm integration tests) → docs → superproject. Vẫn cần ít nhất một người khác approve PR.

## 6. Ghi chú cho quy trình

- Review cùng phiên implement có nguy cơ thiên kiến; đã đọc diff và đường chạy trước khi đối chiếu 04/05, nhưng vẫn cần người review khác.
- Lỗi schema ban đầu cho thấy unit fake audit chưa đủ chứng minh AC7; API test trên Postgres thật tìm được CHECK gây500, đã bổ sung matrix và append-only lâu dài.
- Scope gốc xem thay đổi của mọi giai đoạn là thay đổi hiện tại, nên các lần quay lại implement/test/review tạo false positive. Người dùng yêu cầu giữ .agents nguyên trạng; lượt này chỉ ghi bằng chứng, không sửa quy trình.
- Artifact cũ có câu trạng thái tại thời điểm tạo (ví dụ test còn draft); trạng thái hiện hành lấy từ frontmatter/gate, không sửa artifact đã approved.
- Issue vẫn tạm bỏ qua theo yêu cầu người dùng.

## Bước tiếp theo

- Đang chờ: người duyệt đọc review và hai lưu ý.
- Việc cần làm: chạy `python .agents/scripts/gate.py approve 3.23-adherence-family-consent review` trong terminal người duyệt. Chỉ commit/push/tạo PR khi người dùng yêu cầu rõ; không tự coi task đạt Definition of Done trước PR approval.
- Cập nhật lần cuối: 2026-10-21 19:12 +0700, Codex.
