---
task: 3.23-adherence-family-consent
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-21 18:48 +0700
content_hash: sha256:50da5a783bd24265
inputs:
  01-requirement.md: sha256:59d6784f453d27aa
  02-contract.md: sha256:e50bcda374a39752
---

# 3.23-adherence-family-consent · Plan

## 1. Giải pháp

Giữ endpoint và đường đọc dữ liệu hiện có: `history_http.read_history` xác thực app session, chọn patient từ query hoặc người gọi, `get_adherence_history` gọi `AccessGuardAdapter.authorize_history` trước `SqlAdherenceHistory.read`. PEP chung của `access` đọc consent và liên kết từ DB ở mỗi request, ghi `allowed` trong transaction request hoặc `denied` ở transaction riêng. Response Pydantic và middleware `no-store` đã có; không thêm route, repository, cache hoặc dependency.

Sửa một sai lệch gốc trong `access.domain.rules.decide`: sau khi xác nhận patient tồn tại, từ chối admin trước nhánh tự truy cập và nhánh family, trả `khong_co_quyen` với `ActorRole.ADMIN`. Như vậy admin tự chọn UUID hoặc có liên kết family đều bị 403 và có audit `denied`; các caller của PEP cùng hưởng bất biến QD-32. Giữ ngoại lệ patient không tồn tại: 403 cùng body, không audit vì FK. Dùng test hồi quy tại lớp quy tắc và API để phát hiện ảnh hưởng ngoài ý muốn.

Contract `GET /adherence` đã được duyệt ở giai đoạn trước. Test contract backend hiện giả định 12 ví dụ và so sánh cú pháp schema sinh ra với schema viết tay; cập nhật test để kiểm tra các ràng buộc và giá trị trên wire theo contract mới, giữ ca âm tính về trạng thái liều, bigint, nullable và header. Không sửa contract đã duyệt trong giai đoạn implement.

Test tích hợp đã tìm thấy BUG-ADHERENCE-14: admin-self bị từ chối ở code nhưng INSERT audit thất bại, trả 500. CHECK `access_logs_actor_identity_check` hiện buộc mọi actor trùng patient phải có vai patient. Bổ sung migration mới nới đúng một trường hợp: actor trùng patient, vai admin và result=denied. Mọi tổ hợp hợp lệ cũ vẫn hợp lệ; admin-self allowed, family-self, no-access-self và patient-role truy cập người khác vẫn bị CHECK chặn. Không đổi grant, RLS hoặc trigger append-only. Đây là sửa ràng buộc kỹ thuật để đạt AC3/AC7 đã duyệt, không thay đổi API hay luồng consent.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/3.23-adherence-family-consent/{01-requirement.md,02-contract.md}` | AC1–AC9 và contract đã approved; admin phải bị từ chối theo bất biến dự án. |
| `api_contract/openapi.json` | Đã công bố path, query, schema, lỗi và `no-store`; file còn thay đổi chưa commit từ giai đoạn contract. |
| `backend/src/drugtime/modules/adherence/{adapters/inbound/history_http.py,application/get_adherence_history.py,adapters/outbound/other_modules.py,adapters/outbound/sql_adherence.py}` | Route, thin handler, guard trước reader và truy vấn theo patient đã hiện diện; không cần viết lại. |
| `backend/src/drugtime/modules/access/{domain/rules.py,application/authorize.py,adapters/outbound/facts.py,adapters/outbound/sql_access_log.py}` | `decide()` xét self trước admin; admin self có consent được phép. Audit allowed fail-closed, denied transaction riêng; facts đọc trực tiếp DB. |
| `backend/tests/unit/{test_access_rules.py,test_access_authorize.py,test_contract_adherence.py,test_get_adherence_history.py,test_adherence_history_http.py}` | Có test quy tắc, PEP, luồng trước reader và HTTP; test contract đang dùng ví dụ/tên cũ cần đồng bộ mà không bỏ các ca biên. |
| `backend/tests/integration/{conftest.py,test_adherence_history_access.py,test_adherence_history_api.py,test_access_qd32_admin.py}` | Fixture Postgres `api_role`, test self/family, thu hồi tức thì, đổi patient, audit failure và admin khác patient đã có; thiếu admin tự truy cập và admin có liên kết. |
| `backend/tests/architecture/{test_health_route_enforcement.py,test_module_dependencies.py}` | Route đã có trong registry CI; sửa quy tắc cùng module access nên không thêm import giữa module. |
| `backend/src/drugtime/modules/{medication,adherence}/adapters/outbound/other_modules.py`; tìm caller `access.authorize` và `decide` trong `backend/src` | PEP chung còn bảo vệ thuốc và xác nhận liều; sửa quyền admin ở gốc phải chạy hồi quy các caller này. |
| `backend/supabase/migrations/20261013022744_access_logs_self_audit.sql` | CHECK đồng nhất vai patient với actor=patient gây lỗi denied admin-self; phải thêm migration, không sửa file đã áp dụng. |
| `backend/tests/integration/test_migration_family_link_consent.py` | Có mẫu kiểm CHECK, quyền và trigger bằng DB thật; tái sử dụng fixture và transaction rollback. |
| `work/3.23-adherence-family-consent/05-test-report.md` và evidence test | 59 pass, 1 fail liên quan; full suite 777 pass, 3 fail, 159 skip, 1 xpass. Lỗi admin-self tái hiện trên DB mới nhất. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `api_contract` | `openapi.json` | Sửa (đã hoàn tất ở contract; giữ nguyên khi implement) | Ghi nhận thay đổi chưa commit của giai đoạn đã duyệt để scope của implement nhận đúng trạng thái workspace. |
| `backend` | `src/drugtime/modules/access/domain/rules.py` | Sửa | Từ chối admin trước mọi nhánh cho phép khi patient tồn tại. |
| `backend` | `tests/unit/test_access_rules.py` | Sửa | Hồi quy admin-self, admin có liên kết, matrix read/write và giữ self/family bình thường. |
| `backend` | `tests/unit/test_access_authorize.py` | Sửa | Chứng minh admin-self bị từ chối, audit `denied` ở vai admin và fail-closed nếu audit hỏng. |
| `backend` | `tests/unit/test_contract_adherence.py` | Sửa | Kiểm contract đã duyệt theo hành vi và ràng buộc wire; giữ các ca trạng thái, thời gian, bigint, null và lỗi. |
| `backend` | `tests/integration/test_adherence_history_access.py` | Sửa ở giai đoạn test | Bổ sung API regression admin-self/admin có liên kết; không sửa file này trong giai đoạn implement vì thuộc vùng `integration-test`. |
| `backend` | `supabase/migrations/*_access_logs_admin_self_denied.sql` | Thêm | Chỉ thay CHECK actor identity để cho phép denied admin-self; giữ mọi quyền và append-only. Glob dành cho timestamp do CLI tạo. |
| `backend` | `tests/integration/test_access_log_actor_identity.py` | Thêm ở giai đoạn test | Kiểm các tổ hợp actor/patient/role/result, giữ dữ liệu cũ, quyền và trigger append-only sau migration. |
| `docs` | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | Sửa ở giai đoạn test | Gộp sheet ADHERENCE và Bug Report từ spec task; giữ kết quả của chức năng khác. |

Không dự kiến sửa `history_http.py`, `get_adherence_history.py`, schema response, SQL reader, client hay test fixture. Nếu test phát hiện sai lệch thật ở các file này, ghi mục Phát sinh và xin mở rộng phạm vi trước khi sửa.

## 4. Checklist

- [ ] P1 [backend] Viết hồi quy admin-self và admin có liên kết bị từ chối cho cả read/write; cập nhật kỳ vọng matrix cũ để phản ánh QD-32 — file: `tests/unit/test_access_rules.py` — AC: AC3, AC6; QD-32 — xong khi test mới chứng minh lỗi hiện tại và self/family không phải admin vẫn được phép theo consent.
- [ ] P2 [backend] Đặt nhánh admin-denied sau kiểm `patient_exists` và trước self/family trong `decide()`, giữ reason/role và bỏ nhánh admin dư của `_role` — file: `src/drugtime/modules/access/domain/rules.py` — AC: AC3, AC6, AC7; QD-32 — xong khi các ca P1 pass, patient không tồn tại vẫn 403 không log, family hợp lệ không phải admin vẫn được đọc.
- [ ] P3 [backend] Kiểm PEP của admin-self ghi `denied` ở vai admin, lỗi ghi denied không trả thành công — file: `tests/unit/test_access_authorize.py` — AC: AC7; QD-32 — xong khi các nhánh audit thành công/thất bại đều được assert và pass.
- [ ] P4 [backend] Cập nhật test contract theo ví dụ `family_by_date` và schema đã duyệt; tạo payload pending/empty trong test cho các ca âm tính hiện có, thay so sánh cú pháp schema bằng kiểm ràng buộc và response trên wire — file: `tests/unit/test_contract_adherence.py` — AC: AC1, AC8, AC9 — xong khi giữ được ca bigint, null, status/source/timestamp, query/security/status/header và test pass với contract approved.
- [ ] P5 [backend] Chạy unit liên quan, `pytest tests/unit tests/architecture`, `ruff check .`; lưu output thô — file: không sửa thêm — AC: AC1–AC9; QD-32 — xong khi lệnh có kết quả rõ và không có hồi quy Critical/High do P2.
- [ ] P6 [backend] Ở **giai đoạn test**, bổ sung ca API admin-self (có consent và lịch sử) và admin có liên kết, kiểm 403, body không chứa lịch sử và `access_logs` có `denied` vai admin — file: `tests/integration/test_adherence_history_access.py` — AC: AC3, AC6, AC7; QD-32 — xong khi test chạy với Postgres `api_role` và pass.
- [ ] P7 [backend] Ở **giai đoạn implement**, tạo migration mới trong transaction, thay đúng CHECK actor identity bằng biểu thức giữ nguyên các tổ hợp cũ và thêm riêng admin-self denied; chạy migration trên DB local có audit trước đó để xác nhận mọi dòng cũ giữ nguyên — file: `supabase/migrations/*_access_logs_admin_self_denied.sql` — AC: AC3, AC7 — xong khi migration áp dụng được, không sửa/xóa dữ liệu, không thay grant/RLS/trigger và không sửa migration cũ.
- [ ] P8 [backend] Ở **giai đoạn test**, thêm matrix CHECK trên api_role: patient-self allowed/denied, family-other allowed/denied, admin-other denied và admin-self denied được chấp nhận; admin-self allowed, family/no-access-self và patient-role other bị từ chối. Kiểm UPDATE/DELETE/TRUNCATE vẫn bị chặn cho role ứng dụng và chủ bảng — file: `tests/integration/test_access_log_actor_identity.py` — AC: AC3, AC7; CD3 — xong khi từng tổ hợp và bảo vệ append-only pass trên DB thật, ca vi phạm không để lại dòng.
- [ ] P9 [backend] Ở **giai đoạn test**, chạy lại toàn bộ test tích hợp adherence và các caller PEP liên quan sau `supabase db reset`; xuất OpenAPI runtime để đối chiếu path/query/status/schema với `api_contract/openapi.json`; lưu log — file: không sửa thêm — AC: AC1–AC9 — xong khi các ca self/family/thu hồi/audit/validation/contract đều có bằng chứng pass hoặc lỗi được phân loại.

- [ ] P10 [docs] Ở **giai đoạn test**, cập nhật `testcases.json`, validate/build/merge bằng `testcase_xlsx.py` vào workbook tổng; đọc và bảo toàn các thay đổi đang có, chỉ gộp sau khi xác định thay đổi workbook thuộc task hay đã được chủ sở hữu cho phép — file: `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` — AC: AC1–AC9 — xong khi kết quả khớp evidence mới, Bug Report không che lỗi và sheet khác giữ nguyên.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `test_admin_self_and_linked_denied_every_scope_and_action` (mới hoặc mở rộng trong `test_access_rules.py`) | AC3, AC6; QD-32 | `backend` |
| `test_admin_self_denied_audited_and_audit_failure_fails_closed` trong `test_access_authorize.py` | AC7; QD-32 | `backend` |
| `test_contract_example_validates_and_preserves_number`, các ca negative dose/summary/bigint và kiểm query/security/status/header trong `test_contract_adherence.py` | AC1, AC8, AC9 | `backend` |
| Chạy lại `test_get_adherence_history.py`, `test_adherence_history_http.py`, toàn bộ `tests/unit` và `tests/architecture` | AC1–AC9; các caller của PEP | `backend` |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| `test_self_and_family_success_are_audited_with_minimal_metadata__AC1_AC2` (đã có) | AC1, AC2 | Cả chính chủ và người thân; log allowed, dữ liệu tối thiểu. |
| `test_unlinked_missing_consents_sharing_off_admin_denied_and_audited__AC11` (đã có) | AC3, AC4 | Không liên kết, thiếu từng consent, tắt chia sẻ; 403 và denied. |
| `test_revoke_sharing_off_unlink_denies_immediate_next_request_same_token__AC12` (đã có) | AC5 | Thu hồi hiệu lực ở request kế tiếp, không cache quyền. |
| `test_family_patient_selector_tamper_does_not_read_other_patient__AC11` (đã có) | AC6 | Cross-patient 403 và denied. |
| `test_admin_self_and_linked_history_denied_and_audited` (mới) | AC3, AC6, AC7; QD-32 | Tạo admin có health_data, dữ liệu của chính họ và liên kết đến patient khác; cả hai phải 403, denied. |
| `test_audit_permission_and_commit_failure_fail_closed_without_health__AC13`; `test_denied_audit_survives_outer_transaction_rollback__AC13` (đã có) | AC7 | Ghi log lỗi thì không lộ dữ liệu; denied tồn tại sau rollback. |
| `test_authentication_401_and_no_store_without_health_payload__AC14` (đã có); `test_bad_queries_are_422_without_health_payload__AC14` (đã có) | AC8 | Thiếu/sai token, UUID/ngày/enum lỗi. |
| `test_patient_history_by_date_medication_groups_and_80_percent__AC1_AC3_AC4` và `test_default_partial_and_inclusive_90_day_filters__AC5` (đã có) | AC9 | Runtime theo contract: nhóm, tổng hợp, bộ lọc, timezone, giới hạn 90 ngày. |
| `test_access_log_actor_identity_matrix__AC3_AC7` trong `test_access_log_actor_identity.py` (mới) | AC3, AC7 | Chèn allowed/denied đúng vai và identity bằng api_role; riêng admin-self chỉ nhận denied; tổ hợp sai bị CHECK từ chối. |
| `test_access_logs_remain_append_only_after_actor_identity_migration__AC7` (mới) | AC7; CD3 | UPDATE/DELETE/TRUNCATE vẫn bị từ chối bởi quyền hoặc trigger, kể cả chủ bảng; số dòng/nội dung không đổi. |

## 6. Migration

- File mới: `backend/supabase/migrations/<timestamp>_access_logs_admin_self_denied.sql`; tạo bằng `supabase migration new access_logs_admin_self_denied` khi CLI sẵn sàng. Nếu CLI chưa có, báo rõ giới hạn trước implement; không sửa `.agents`.
- Chỉ đổi `public.access_logs.access_logs_actor_identity_check`, trong một transaction: actor=patient nhận vai patient hoặc riêng vai admin với result=denied; actor khác patient không nhận vai patient. CHECK khác vẫn giữ nguyên.
- Biểu thức mới là tập mở rộng của biểu thức cũ; không cần backfill, không sửa/xóa audit lịch sử. Áp dụng trên DB local có audit và so số lượng/nội dung trước/sau; dữ liệu không tương thích làm migration rollback.
- Không thêm bảng/cột/index/truy vấn/grant/policy. Không có truy vấn mới cần index. Trigger và revoke UPDATE/DELETE/TRUNCATE giữ nguyên, có kiểm hồi quy.
- Chạy toàn bộ chuỗi migration từ DB local sạch. Ưu tiên `supabase db reset`; nếu thiếu CLI, dựng DB riêng từ template0, khởi tạo schema extensions và chạy từ migration rebuild như evidence test trước, ghi rõ không kiểm Supabase Auth/seed.
- Kiểm cả nâng cấp DB có dữ liệu cũ và dựng DB sạch; lưu `evidence/implement-db-reset.log` và `evidence/test-migration.log`.
- Schema/ERD chính thức chưa nằm trong phạm vi sửa; ghi thay đổi CHECK trong artifact và đề xuất đồng bộ tài liệu ở Phát sinh.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| `api_contract` | `feat/3.23-adherence-family-consent` đã tạo ở giai đoạn contract; chưa commit/push. |
| `backend` | Đang ở `feat/3.23-adherence-family-consent`, có các thay đổi implement/test của task; kiểm lại status trước khi sửa. |
| `docs` | Đang ở `feat/3.23-adherence-family-consent`, workbook tổng có thay đổi chưa commit tại thời điểm khảo sát 18:45. Chưa xác định chủ sở hữu/nội dung; không ghi đè trước khi đối chiếu. |
| superproject | Tạo `feat/3.23-adherence-family-consent` khi người dùng yêu cầu commit artifact/con trỏ; hiện ở `main`. |

## 8. Rủi ro

- **Phân quyền chung**: PEP bảo vệ cả medication và xác nhận liều. Từ chối admin sớm sẽ đổi hành vi admin có liên kết family vốn được test cũ cho phép; đây là thay đổi chủ đích theo QD-32. Chạy lại unit và integration của các caller để phát hiện ảnh hưởng.
- **Audit/transaction**: admin-self hiện không log; thay đổi phải tạo `denied` ở transaction riêng, kể cả request chính rollback. Test unit và tích hợp kiểm cả response lẫn `access_logs`.
- **Contract test cũ**: phụ thuộc 12 ví dụ không có trong contract vừa duyệt và so sánh cú pháp JSON Schema. Cập nhật test giữ kiểm các ràng buộc quan trọng, không nới validation runtime để chỉ làm test pass.
- **Công cụ local**: dependency đã có riêng trong scratch; Supabase CLI chưa có trong PATH. Postgres local chạy được và đã dựng DB riêng cho test. Dựng DB riêng không xác minh Supabase Auth/seed; 159 ca full suite đã skip và phải ghi rõ giới hạn.
- **Git/scope**: `api_contract/openapi.json` đã approved nhưng `scope.py --stage plan` xem thay đổi từ giai đoạn contract là ngoài phạm vi. Chỉ commit trên nhánh task vẫn không giải quyết vì script cũng so commit nhánh task với `origin/main`. Không reset, đổi nhánh để che thay đổi hoặc sửa cổng nhằm lấy kết quả xanh.
- **Dữ liệu và tương thích**: ALTER CHECK cần khóa bảng access_logs; transaction phải ngắn, kiểm trên dữ liệu cũ và DB sạch. Không backfill/xóa dữ liệu; không đổi response. Deploy migration trước code từ chối admin-self để tránh cửa sổ 500 do audit.
- **Ràng buộc bị nới quá rộng**: chỉ thêm admin-self denied; matrix DB phải chặn admin-self allowed và role/identity sai. Không cấp thêm quyền hoặc bỏ trigger append-only.
- **Workbook có thay đổi đồng thời**: docs hiện có workbook chưa commit, khác trạng thái của lượt test trước. Đọc lại nội dung và giữ kết quả của người khác; nếu không xác định được chủ sở hữu thì hỏi trước khi merge.
- **Lỗi ngoài phạm vi**: full integration còn fail timestamp dose confirmation và profile response thêm email; chưa đối chiếu baseline sạch. Ghi rõ, không sửa hoặc nới test để làm suite xanh.

## 9. Câu hỏi mở

Thiết kế không có câu hỏi mở. Scope plan/test vẫn chặn thay đổi đã duyệt từ các giai đoạn trước; cần quyết định của người duyệt trước khi coi kiểm phạm vi hoàn tất, không sửa `.agents`.

## 10. Phát sinh

- Code hiện có đã đáp ứng phần lớn PB21; phạm vi implement thực tế tập trung vào lỗ hổng admin-self và đồng bộ test với contract approved.
- Test `test_admin_who_is_valid_family_reads_as_family` đang kỳ vọng trái QD-32; thay kỳ vọng cùng lúc với test hồi quy, không giữ quyền admin-family.
- Người dùng yêu cầu đưa `.agents` về trạng thái ban đầu và không sửa thư mục này nữa. Đã hoàn nguyên đúng 9 file của task quy trình, chuyển `.agents` về `main` tại commit `8493b214`, status sạch; bản diff trước khi hoàn nguyên lưu ở `work/adhoc-20261021-scope-approved-stage/scratch/agents-before-revert.patch`.
- Sau khi hoàn nguyên `.agents`, `scope.py --stage plan` của task này lại exit 1 với `[NGOÀI] api_contract/openapi.json` (`evidence/plan-scope-after-agents-revert.log`). Contract vẫn approved nhưng bản `scope.py` gốc không nhận diện file đã duyệt. `gate.py 3.23-adherence-family-consent plan` trả OK. Không sửa `.agents`, không che thay đổi Git và không báo scope pass.

- Ngày 2026-10-21, người dùng đã reopen plan sau BUG-ADHERENCE-14. Plan bổ sung migration, test DB và workbook tổng; requirement/contract giữ AC và hành vi API đã duyệt. Việc sửa CHECK được giới hạn ở chứng cứ denied admin-self, dù khảo sát requirement ban đầu dự kiến không cần schema.
- Chưa sửa code sản phẩm/migration trong lượt sửa plan. Báo cáo test còn draft và lỗi High vẫn mở.
- Sau khi duyệt plan mới, `04-impl-notes.md` phải được người duyệt reopen trước khi tiếp tục implement vì artifact này đang approved theo plan cũ.

- Tự kiểm lượt sửa plan: `scope.py 3.23-adherence-family-consent --stage plan` exit 1, báo 8 file ngoài phạm vi: contract, 5 file backend đã có từ implement/test, workbook docs và `docs/Team1_DTU/01_Proposal_&_Planning/drugtime_quyet_dinh_theo_chuc_nang.md` từ trạng thái nhánh docs. Log: `evidence/plan-scope-amended.log`. Lượt này chỉ sửa artifact plan; không sửa các file submodule đó. Cần người duyệt xem giới hạn này; không báo scope pass.

## Bước tiếp theo

- Đang chờ: người duyệt xem phạm vi bổ sung migration/test DB/workbook, lỗi High và giới hạn scope.
- Việc cần làm: chạy `python .agents/scripts/gate.py approve 3.23-adherence-family-consent plan`, sau đó `python .agents/scripts/gate.py reopen 3.23-adherence-family-consent implement` trong terminal người duyệt. Agent chỉ tiếp tục implement khi gate cho phép.
- Cập nhật lần cuối: 2026-10-21 18:45 +0700, Codex.
