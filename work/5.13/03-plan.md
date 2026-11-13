---
task: 5.13
stage: plan
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-10 13:16 +0700
content_hash: sha256:62e63b8e7ead5259
inputs:
  01-requirement.md: sha256:eb0cc2ee1b9c43b1
  02-contract.md: sha256:d57a06a4057ba520
---

# 5.13 · Plan

## 1. Giải pháp

Triển khai `GET /family/patients` trong module **access**, gắn tag/path family theo contract. Module access đã được phép gọi family, consent và identity; không đặt use case gọi access trong family vì sẽ tạo vòng phụ thuộc. Không đổi API đã duyệt hoặc ma trận kiến trúc.

Luồng xử lý:

1. Xác thực bằng `identity.current_user` và khai báo bearer giống các health route đang có. Query/body thừa bị từ chối theo ValidationError; không lấy chủ danh sách từ ID do client gửi.
2. Admin bị từ chối trước truy vấn ứng viên: gọi audit qua `family.api`, ghi một `denied` operation `list_linked_patients`, subject/link null ở transaction riêng, rồi trả 403. Không bịa patient để gọi PEP patient-specific. Audit thất bại trả 503.
3. Với tài khoản cá nhân, adapter gọi `family.api.sharing_patient_ids` lấy các ID ứng viên thuộc caller. Family sở hữu SQL; access không đọc thẳng bảng family. Distinct ID, bỏ chính caller, không phân trang/cắt ngầm.
4. Bổ sung scope `Scope.LINKED_PATIENTS = danh_sach_benh_nhan_lien_ket`, map consent purpose `health_data`. Tách phần resolve hiện tại của `authorize` thành helper dùng chung: `FactsReader.read → decide` (consent/link guard hiện có). `authorize` cũ giữ nguyên hành vi; PEP dùng cho danh sách tái sử dụng chính helper này, không tự viết biểu thức quyền mới.
5. PEP danh sách loại các ứng viên có decision denied, không ghi denied chỉ vì bộ lọc loại. Với từng patient được phép, ghi một allowed qua `SqlAccessLog` trong UoW hiện tại, actor role family và scope mới. Không dùng `authorize` theo kiểu bắt Forbidden sau khi nó đã ghi denied, vì trái AC7/AC14.
6. Chỉ sau PEP mới lấy tên qua `identity.display_names`, trim/chuẩn hóa thiếu tên thành null, sort bằng thứ tự Unicode của Python rồi UUID tăng dần, null cuối. Không lấy email hay nguyên profile. Trường hợp tên projection không còn có key do patient bị xóa đồng thời: fail-closed, rollback request và trả 503; không trả mục giả hoặc commit log thừa. Tên null là hợp lệ và vẫn có key.
7. Nếu kết quả rỗng: ghi một allowed audit metadata mức request qua `family.api`, subject/link null, cùng UoW; không tạo access_logs cho patient giả. Nếu có kết quả: chỉ N access_logs allowed, không ghi thêm một request-level allowed.
8. Tạo/validate payload và JSON response **bên trong** context UoW; thoát context commit thành công trước khi return response. Lỗi insert/commit/đọc DB làm rollback tất cả allowed và trả 503, không có danh sách một phần. Denied request-level đã ghi transaction riêng vẫn tồn tại.
9. Đăng ký router mới qua access.api, giữ nguyên route admin access-log hiện có. Thêm path mới vào middleware no-store của main, nên cả lỗi 401/403/422/503 đều có header. Route guard bắt lỗi hạ tầng SQLAlchemy bao quanh authentication/dependencies và handler, không chỉ thân use case; không log exception chứa tham số SQL/PII.

Không đổi thông điệp/kiểu lỗi chung hoặc quyền của các endpoint hiện có. Sử dụng response model mới trong file HTTP của access; không import schema/adapters nội bộ của family. Các adapter access gọi module khác chỉ qua `api.py`.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/5.13/01-requirement.md`, `02-contract.md` | Requirement size L đã approved lại 13:03, contract approved 13:05 ngày 2026-11-10; bao phủ AC1–AC14. API không nhận input, trả ID/tên, điều kiện active/sharing/hai consent, audit per-patient + request-level. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 8–9, bản checkout đọc lại trong lượt plan | QD-27–QD-30, QD-32, QD-33 đã chốt; HBR-18 toàn hệ thống còn mở, CS-01/CS-04 trạng thái chờ; không tự nâng trạng thái nguồn. Consent cho riêng API 5.13 đã được chốt ở requirement. |
| `backend/src/drugtime/modules/access/domain/rules.py`, `application/authorize.py`, `application/ports.py`, `adapters/outbound/facts.py` | PEP hiện hữu dùng FactsReader + decide, map scope/purpose, log allowed cùng UoW và denied qua transaction riêng; tái sử dụng policy này, không nhân đôi consent logic. |
| `backend/src/drugtime/modules/access/adapters/outbound/sql_access_log.py`, `access/api.py`, `access/adapters/inbound/http.py` | Writer đã nhận Scope; access.api đang export router admin `/admin/access-logs`; cần aggregator để giữ route này và thêm route list. |
| `backend/src/drugtime/modules/family/api.py`, `application/ports.py`, `adapters/outbound/sql_links.py` | Public API hiện có chiều patient → family. `_ACTIVE` không chỉ kiểm cờ mà còn kiểm bằng chứng xác nhận chia sẻ theo đúng cặp trong `family_link_consent_confirmations`. Query ứng viên mới tái sử dụng cùng định nghĩa liên kết hợp lệ; PEP vẫn đọc lại quyền. Không bỏ kiểm bằng chứng cho liên kết legacy để mở rộng quyền. |
| `backend/src/drugtime/modules/family/adapters/outbound/sql_link_audit.py`, `adapters/inbound/http.py` | Writer request metadata sẵn có: allowed dùng UoW, denied transaction riêng. Kiểu patient_id của allowed hiện không nullable; cần cho phép None ở port/writer, nhưng DB chỉ cho trường hợp list mới không có subject. |
| `backend/src/drugtime/modules/identity/api.py`, `identity/adapters/outbound/sql_users.py` | `display_names` đã là projection tối thiểu, trim/nullable và bỏ user erased. `user_exists` tính cả user erased, nên không coi nó là bằng chứng tên projection luôn có key. Không sửa module identity trong task. |
| `backend/src/drugtime/shared/db.py`, `shared/uow.py`, `main.py`, `adherence/adapters/inbound/history_http.py` | UoW commit khi thoát context; history tạo response trong context trước khi return. Main có middleware no-store theo allow-list route; cần thêm endpoint mới. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql`, `20261015030157_family_link_consent.sql`, `20261021030401_family_link_audit_caregiver_operations.sql`, `20261013022744_access_logs_self_audit.sql`, `20261021115000_access_logs_admin_self_denied.sql` | Enum access scope chưa có loại mới; request audit có CHECK operation, subject/link, result/reason. Bảng log đã có RLS, grant và revoke/trigger append-only; không bỏ chúng. |
| `backend/tests/architecture/test_module_dependencies.py`, `test_health_route_enforcement.py`, `test_family_route_enforcement.py` | access → family được phép; family → access không được. Registry health route kiểm bearer, identity, scope, operationId. Route mới thuộc access router và registry health, không chen vào nhóm metadata-owner routes của family. |
| `backend/tests/unit/test_access_authorize.py`, `test_access_rules.py`, `test_contract_family_caregivers.py`; `tests/integration/conftest.py`, `test_family_caregivers_api.py`, `test_migration_family_link_audit_operations.py`, `test_migration_access_self_audit.py` | Dùng fakes ports ở unit, canonical OpenAPI comparison ở contract test; integration có client + token thật + DB api_role và factory liên kết/consent. Test migration có mẫu snapshot dữ liệu và assert constraints/append-only bằng connection quản trị local. |

### Quyết định nghiệp vụ áp dụng

| Quy tắc / nguồn và trạng thái | AC | Bước | Test |
|---|---|---|---|
| QD-27 mục 8, đã chốt: người thân chỉ xem | AC1, AC8 | P3–P5 | U1, U4, U9, I1 |
| QD-28 mục 8, đã chốt: liên kết hợp lệ + sharing + family_sharing; purpose health_data của 5.13 theo quyết định người dùng trong requirement, không đóng HBR-18 toàn hệ thống | AC1, AC3, AC7, AC9 | P2–P4 | U1–U3, U6, I1–I3 |
| QD-29 mục 8, quy tắc kiểm DB mỗi request, đã chốt | AC3, AC7 | P2–P5 | U2, U7, I3 |
| QD-29 mục 8, quy tắc không lưu bền dữ liệu người thân, đã chốt | AC8; header theo contract | P5 | U8, U9, I6; không sửa Mobile trong task |
| QD-30 mục 8, đã chốt: liên kết lại không tự khôi phục sharing | AC7 | P2, P4 | U3, I2, I3 |
| QD-32 mục 9, đã chốt: admin không vượt quyền | AC4, AC6, AC11 | P2, P4, P5 | U5, U8, I4 |
| QD-33 mục 9, đã chốt: metadata tối thiểu, ghi bền vững trước tiếp tục | AC5, AC6, AC10, AC11, AC14 | P1, P2, P4, P5 | U4, U5, U7, I4, I5, I7 |
| AGENTS bất biến 3 + wf-db-migration: append-only, migration mới, grant tối thiểu | AC12, AC13 | P1, P7, P8 | I8–I11 |
| AGENTS bất biến 2/4 + registry enforcement hiện hữu; nguồn CS-01/CS-04 vẫn chờ nhưng yêu cầu PEP/403 là bắt buộc theo AGENTS | AC3–AC6 | P3, P5, P6 | U7, U8, A1, I3–I5 |

## 3. File sẽ thay đổi (ranh giới phạm vi)

Đường dẫn dưới đây tính từ gốc submodule. Hai glob migration chỉ cho phép đúng hai hậu tố mới; mỗi glob tạo một file timestamp do Supabase CLI cấp. File integration chỉ viết/chỉnh ở giai đoạn test, không sửa khi implement theo scope.py.

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| backend | `supabase/migrations/*_linked_patient_access_scope.sql` | Thêm | Enum scope audit mới, commit trước khi dùng giá trị. |
| backend | `supabase/migrations/*_linked_patient_request_audit.sql` | Thêm | Operation request audit mới và CHECK subject/link được giới hạn đúng operation. |
| backend | `src/drugtime/modules/family/application/ports.py` | Sửa | Port query ứng viên và nullable subject cho allowed request audit. |
| backend | `src/drugtime/modules/family/adapters/outbound/sql_links.py` | Sửa | Query IDs theo caller, reuse định nghĩa active-sharing hợp lệ. |
| backend | `src/drugtime/modules/family/adapters/outbound/sql_link_audit.py` | Sửa | Hỗ trợ None subject với operation mới; giữ writer/transaction hiện có. |
| backend | `src/drugtime/modules/family/api.py` | Sửa | Export IDs ứng viên và hai thao tác audit empty/denied; không import access. |
| backend | `src/drugtime/modules/access/domain/rules.py` | Sửa | Scope mới và map health_data; không đổi policy quyết định quyền. |
| backend | `src/drugtime/modules/access/application/authorize.py` | Sửa | Helper resolve dùng chung cho authorize cũ và PEP lọc danh sách. |
| backend | `src/drugtime/modules/access/application/ports.py` | Sửa | Candidate IDs, tên tối thiểu và request-audit ports. |
| backend | `src/drugtime/modules/access/application/list_linked_patients.py` | Thêm | Use case, view record, PEP filtering, audit, sort/dedup và lỗi fail-closed. |
| backend | `src/drugtime/modules/access/adapters/outbound/linked_patients_gateway.py` | Thêm | Gọi family.api/identity.api; không truy cập private adapters module khác. |
| backend | `src/drugtime/modules/access/adapters/inbound/linked_patients_http.py` | Thêm | Route, strict schemas, input validation, guarded request và transaction trước response. |
| backend | `src/drugtime/modules/access/api.py` | Sửa | Router aggregator giữ admin route và thêm route mới. |
| backend | `src/drugtime/main.py` | Sửa | Bổ sung route no-store; không đổi xử lý lỗi của các route khác. |
| backend | `tests/unit/test_access_rules.py` | Sửa | Map purpose/scope mới và hồi quy policy. |
| backend | `tests/unit/test_access_authorize.py` | Sửa | Helper chung không đổi authorize cũ; thứ tự facts/guard/log. |
| backend | `tests/unit/test_sql_family_links.py` | Sửa | Query ID ứng viên đúng caller, lọc/khử trùng theo port. |
| backend | `tests/unit/test_linked_patients.py` | Thêm | Use case, audit/filter/sort, lỗi và projection tối thiểu. |
| backend | `tests/unit/test_linked_patients_http.py` | Thêm | Token/input/errors, commit-before-response và no-store. |
| backend | `tests/unit/test_linked_patients_gateway.py` | Thêm | Family public facade, adapter tên/IDs và request audit đúng subject/transaction. |
| backend | `tests/unit/test_contract_linked_patients.py` | Thêm | Canonical response/schema/errors/metadata khớp OpenAPI approved. |
| backend | `tests/architecture/test_health_route_enforcement.py` | Sửa | Đăng ký operation/scope/bearer/identity mới. |
| backend | `tests/integration/test_linked_patients_api.py` | Thêm | API/DB thật: dữ liệu, quyền, audit và thu hồi ngay. |
| backend | `tests/integration/test_linked_patients_fail_closed.py` | Thêm | Fault injection audit/commit/DB và denied bền vững. |
| backend | `tests/integration/test_migration_linked_patients.py` | Thêm | Enum, ràng buộc audit mới/cũ, upgrade và append-only/grants. |

Tổng dự kiến: **25 file Backend** (14 file ứng dụng/migration, 7 unit test, 1 architecture test, 3 integration test). Không sửa API contract approved, Frontend, submodule tests, docs hoặc ma trận dependency. Artifact/evidence thuộc `work/5.13/`.

## 4. Checklist

- [ ] P1 [backend] Tạo hai migration mới bằng `supabase migration new linked_patient_access_scope` và `supabase migration new linked_patient_request_audit`; thêm enum và nới CHECK hẹp cho operation mới, giữ CHECK cũ, RLS/grant/trigger — file: hai glob migration ở bảng — AC: AC10–AC13 — xong khi: migration được review về additive schema, enum commit riêng; không có UPDATE/DELETE nhật ký hoặc thay migration cũ.
- [ ] P2 [backend] Thêm query ID theo family caller, reuse `_ACTIVE`; facade query và audit empty/denied qua writer hiện hữu, allowed subject nullable đúng operation — file: bốn file family ở bảng — AC: AC1, AC2, AC6, AC7, AC11 — xong khi: U3/U6/U10 xác nhận đúng ID, null subject, denied dùng transaction riêng; không gọi access từ family.
- [ ] P3 [backend] Thêm scope/purpose và helper resolve chung; giữ authorize hiện hành nguyên hành vi — file: access `domain/rules.py`, `application/authorize.py`, `application/ports.py` — AC: AC1, AC3–AC7, AC9, AC10, AC14 — xong khi: U2/U7 và toàn bộ unit access cũ pass; dùng cùng decide/facts, không cache.
- [ ] P4 [backend] Viết use case và outbound gateways: admin trước candidates; distinct/filter PEP; log allowed đúng scope trước tên; sort tên/null/ID; empty request audit; propagate lỗi để rollback — file: `list_linked_patients.py`, `linked_patients_gateway.py` — AC: AC1–AC11, AC14 — xong khi: U1–U7/U10 pass, không gọi tên trước PEP, không ghi denied cho filtered.
- [ ] P5 [backend] Thêm HTTP route và strict schemas; JSON response validate trong UoW, commit trước return; guard SQLAlchemyError từ dependencies/handler thành 503, global no-store path và router aggregator — file: `linked_patients_http.py`, access/api.py, main.py — AC: AC1–AC6, AC8, AC11, AC14 — xong khi: U8/U9/U11 pass cho mọi response đã đặc tả và fault commit; route admin cũ không đổi.
- [ ] P6 [backend] Bổ sung registry và contract parity test; chạy unit/architecture + lint, lưu log — file: 7 unit test + architecture registry ở bảng — AC: AC1–AC11, AC14 — xong khi: `pytest tests/unit tests/architecture` và `ruff check .` pass, không thêm quan hệ import, wire API khớp contract.
- [ ] P7 [backend] Ở implement, kiểm hai migration trên Supabase **local**: full reset sạch, rồi quy trình nâng cấp riêng từ migration cuối trước task có dữ liệu audit mẫu; lưu snapshot trước/sau và log; chạy unit lại sau migration — file: hai migration; script thử chỉ trong `work/5.13/scratch/` — AC: AC12, AC13 — xong khi: reset/upgrade thật thành công và nhật ký cũ không đổi; không tính skip/no DB là pass. Không ghi/chỉnh file integration ở bước này.
- [ ] P8 [backend, giai đoạn test sau approval implement] Viết/chạy ba file integration trong bảng, bao phủ I1–I11, cross-caller, cùng token sau thu hồi, audit insert/commit fail và phân quyền DB — AC: AC1–AC14 — xong khi: mọi ca chạy thật với api_role/local Postgres, không skip do thiếu DB; log có trong `work/5.13/evidence/`.
- [ ] P9 [backend/work] Chạy lại bộ unit/architecture/integration và lint khi các thay đổi giai đoạn tương ứng đã xong; scope đúng stage và cập nhật artifact/evidence — file: các test ở bảng + artifact task — AC: AC1–AC14 — xong khi: có output thật, tách lỗi baseline khỏi task, không sửa file ngoài plan hay tự approve.

## 5. Test

Các ID U/I/A là nhóm test có parameterization được ghi rõ; tên test dự kiến là tên hàm trong file, có thể thêm suffix cho từng case mà không đổi mục tiêu. Chưa chạy bất kỳ test ứng dụng/DB nào trong lượt plan.

### Unit

| ID / Test dự kiến | AC | Submodule / file |
|---|---|---|
| U1 `test_list_only_authorized_patients` (0/1/nhiều ứng viên; consent caller không ảnh hưởng; không tự thêm caller) | AC1, AC2, AC7, AC9 | backend `tests/unit/test_linked_patients.py` |
| U2 `test_resolve_uses_current_facts_each_call` (sharing, hai consent, quan hệ, patient_exists đổi) và `test_existing_authorize_behavior_unchanged` | AC3–AC7, AC9 | backend `tests/unit/test_access_authorize.py` |
| U3 `test_sharing_patient_ids_are_caller_scoped` (pending/rejected/revoked, sharing off, thiếu bằng chứng legacy, liên kết lại chưa share) | AC1, AC7 | backend `tests/unit/test_sql_family_links.py` |
| U4 `test_allowed_audit_precedes_name_read` và `test_names_sort_deduplicate_and_minimal_projection` (trùng tên, null/blank, Unicode, UUID tie-break) | AC1, AC8, AC10 | backend `tests/unit/test_linked_patients.py` |
| U5 `test_admin_denied_before_candidates` và `test_empty_list_request_audit_has_no_subject` | AC2, AC4, AC6, AC11 | backend `tests/unit/test_linked_patients.py` |
| U6 `test_scope_maps_to_health_data` và `test_family_gateway_calls_public_api_only` | AC1, AC7, AC9, AC10 | backend `test_access_rules.py`, `test_linked_patients_gateway.py` dưới `tests/unit/` |
| U7 `test_filtered_candidates_do_not_write_denied`, `test_audit_or_name_reader_failure_aborts`, `test_no_name_read_when_pep_denies` | AC5, AC7, AC10, AC14 | backend `tests/unit/test_linked_patients.py` |
| U8 `test_http_auth_validation_errors_no_store` (missing/invalid/Supabase token, admin, selector/unknown/duplicate query, mọi body kể cả `{}`) | AC4, AC6, AC8, AC11 | backend `tests/unit/test_linked_patients_http.py` |
| U9 `test_generated_operation_matches_contract` (200/401/403/422/503, schemas, strict fields, no parameters/body, scope/audit metadata) | AC1, AC2, AC4, AC5, AC8 | backend `tests/unit/test_contract_linked_patients.py` |
| U10 `test_request_audit_uses_null_subject_and_existing_writer` (allowed dùng UoW caller, denied transaction riêng) | AC6, AC11 | backend `tests/unit/test_linked_patients_gateway.py` |
| U11 `test_commit_failure_returns_503_before_response` và `test_dependency_sql_failure_returns_503_no_store` | AC5, AC11, AC14 | backend `tests/unit/test_linked_patients_http.py` |
| A1 `test_linked_patient_route_registered` cùng bộ module dependency hiện có | AC3–AC6 | backend `tests/architecture/test_health_route_enforcement.py`; chạy `test_module_dependencies.py` nhưng không sửa ma trận |

### Tích hợp

| ID / Test dự kiến | AC / kịch bản chất lượng | Nơi chứa / ghi chú |
|---|---|---|
| I1 `test_returns_multiple_patients_with_minimal_fields_and_allowed_logs` (trùng tên, null, thứ tự, N logs đúng subject/scope) | AC1, AC8, AC10; tối thiểu dữ liệu | `backend/tests/integration/test_linked_patients_api.py` |
| I2 `test_filters_unrelated_inactive_unshared_and_missing_consents` (cả thiếu health_data, family_sharing, bằng chứng; link cũ đã revoke và link mới chưa share) | AC2, AC7, AC9; không lộ chéo caller | Cùng file I1; kiểm response lẫn audit, không có denied chỉ vì lọc |
| I3 `test_revocation_applies_next_request_with_same_token` (tắt share, rút từng consent, revoke; đồng ý/bật lại chỉ hiện khi đủ quyền) | AC3, AC7, AC9; thu hồi ngay request kế | Cùng file I1; không cache DB facts |
| I4 `test_empty_list_and_admin_denial_durable_request_audit` | AC2, AC4, AC6, AC11; denied sống sau rollback | Cùng file I1; subject/link null, admin không scan bệnh nhân |
| I5 `test_audit_insert_or_commit_failure_never_returns_partial_list` (lỗi dòng allowed thứ 2 và lỗi commit UoW) | AC5, AC10, AC14; log/data fail-closed | `backend/tests/integration/test_linked_patients_fail_closed.py`; kiểm không có allowed commit một phần |
| I6 `test_rejects_selectors_and_body_and_returns_no_store` | AC4, AC8; không dùng patient_id client | Cùng file I1; 422 theo contract, 401 token lỗi; no-store cả lỗi |
| I7 `test_empty_or_denied_audit_failure_returns_503` và `test_database_or_pep_read_failure_returns_503` | AC5, AC6, AC11; không lộ dữ liệu khi hạ tầng lỗi | Cùng file I5; denied thành công vẫn sống sau rollback request, denied ghi lỗi thì 503 |
| I8 `test_new_scope_and_request_operation_accepted` | AC10–AC12 | `backend/tests/integration/test_migration_linked_patients.py`; scope mới và mọi scope cũ đều insert được với role hợp lệ |
| I9 `test_old_constraints_and_records_preserved_after_upgrade` | AC12 | Cùng file I8 + quy trình nâng cấp P7 có snapshot thật trước/sau; operation lạ và các operation cũ thiếu subject/link vẫn bị chặn |
| I10 `test_audit_remains_append_only_for_all_roles` | AC13 | Cùng file I8; hai bảng log/audit × UPDATE/DELETE/TRUNCATE × postgres/service_role/api_role/worker_role/anon/authenticated, dùng transaction/savepoint local không phá audit thật |
| I11 `test_minimal_grants_and_request_subject_constraints` | AC11–AC13 | Cùng file I8; API được insert cần thiết, client/worker không có quyền mới; operation list mới buộc subject/link null, allowed/denied reason vẫn đúng CHECK |

Áp dụng checklist cross-patient của wf-health-endpoint theo **contract danh sách đã duyệt**: không có liên kết/consent ⇒ bị loại/200 rỗng, không phải từ chối cả request; selector patient_id ⇒ 422, không phải một request đọc patient cụ thể. Admin ⇒ 403 + denied. Self không tự xuất hiện. Không áp máy móc kỳ vọng 403/denied của endpoint đọc một patient vào các ca bộ lọc này.

## 6. Migration

1. File mới `*_linked_patient_access_scope.sql`: thêm đúng một enum value `danh_sach_benh_nhan_lien_ket`. Transaction riêng, không insert/use enum mới trong cùng transaction thêm value; chỉ chạy ứng dụng sau khi migration commit.
2. File mới `*_linked_patient_request_audit.sql`: mở `family_link_audit_events_operation_check` thêm `list_linked_patients`; cho allowed của operation này không có subject/link, đồng thời CHECK mới buộc subject/link null cho operation này. Giữ điều kiện subject/link bắt buộc đối với mọi operation cũ, quy tắc allowed/denied/reason và FK actor. Dùng tên constraint đã xác minh, không bỏ qua lỗi bằng IF EXISTS tùy tiện.
3. Không tạo bảng hoặc nới quyền client/worker. Không xóa/thay đổi dữ liệu lịch sử, revoke, RLS hoặc trigger append-only. Các trường thời gian tiếp tục dùng timestamptz/default máy chủ hiện có.
4. Index: query ứng viên dùng `caregiver_links_family_idx (family_user_id,status)` và kiểm bằng chứng bằng unique link_id; PEP dùng index cặp liên kết và `user_consents_one_active_idx (user_id,consent_type)`/`user_consents_user_idx`; tên dùng PK users. Chưa cần index mới; ghi nhận EXPLAIN với fixture nhiều liên kết ở integration nếu query không dùng đường truy cập dự kiến, không thêm index ngoài plan.
5. P7 lưu `implement-db-reset.log`, `implement-db-upgrade.log`, snapshot audit trước/sau. Chỉ reset DB Supabase local đã kiểm host 127.0.0.1/localhost, không production/remote. Quy trình nâng cấp: dựng schema đến migration cuối trước task bằng CLI local, seed audit cũ hợp lệ, chụp snapshot, áp hai migration mới theo thứ tự, kiểm snapshot giữ nguyên và giá trị mới ghi được. Đối chiếu `supabase ... --help` của CLI đang cài trước dùng cờ chọn version; không đoán cờ hoặc chạy thao tác nhầm DB. Quy trình này chạy riêng, không đồng thời với test suite dùng DB đó.
6. Kiểm reset sạch là một lần chạy riêng đến schema mới nhất; không thay thế bằng unit mocks. P8 bổ sung kiểm constraint/RLS/grant/append-only trên DB thật và hồi quy các operation audit cũ. Mọi lệnh/test có output thô trong evidence, không coi skip vì DB tắt là đạt AC12/AC13.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| backend | `feat/list-linked-patients` — đã kiểm ở lượt plan, working tree sạch trước triển khai |
| api_contract | `feat/list-linked-patients` — hai file contract chưa commit từ giai đoạn trước, contract artifact đã approved; không sửa ở plan/implement nếu chưa reopen contract |

Tên nhánh do người dùng chỉ định; luôn truyền task ID `5.13` cho gate vì tên nhánh không chứa backlog ID. Không tự tạo nhánh superproject, commit/push hoặc bump pointer. Trước implement đọc lại status/symbolic-ref để không ghi lên thay đổi mới của người khác.

## 8. Rủi ro

- **Vòng import**: family đang nằm dưới access; route/use case phải ở access, mọi cross-module call qua facade. Kiểm architecture suite, không sửa ALLOWED để làm pass.
- **PEP bị nhân đôi hoặc denied bị ghi nhầm**: dùng chung resolve/decide, policy cũ không đổi; U2/U7 + I2/I3 kiểm quyền lẫn audit.
- **Commit sau khi response gửi**: UoW health nằm trong handler, payload được validate trước commit, return sau context; U11/I5 chặn regression cả lỗi commit.
- **Enum chưa commit**: tách migration scope và request audit, chạy migration trước deploy code. Enum additive không có rollback xóa value đơn giản; rollback ứng dụng không cần xóa enum value hoặc sửa log.
- **CHECK bị nới quá mức**: null subject chỉ cho operation mới; assert mọi operation cũ và quyền cũ không đổi (I9/I11).
- **Danh sách không giới hạn/N+1**: contract hiện không phân trang; query ID/tên theo batch, PEP kiểm từng patient theo logic chuẩn, không cache để giảm truy vấn. Đo bằng fixture nhiều liên kết; nếu cần đổi sang phân trang phải reopen contract, không tự cắt kết quả.
- **Race xóa tài khoản/tên**: phân biệt tên null hợp lệ với patient không còn trong projection; fail-closed, không trả ID không xác định hay commit allowed thừa.
- **Baseline scope**: ba file Firebase ngoài task vẫn được ghi nhận riêng; không stage/xóa/sửa nội dung để scope pass. Hai file contract là đầu ra đã có của task, không phải thay đổi của lượt plan.

## 9. Câu hỏi mở

Không có câu hỏi nghiệp vụ chặn. Đường đi kiến trúc và audit ở plan này dùng cơ chế đã có, không cần mở rộng quan hệ module hoặc đổi contract. Nếu khi implement xuất hiện nhu cầu sửa file ngoài bảng, migration khác hai hậu tố hoặc đổi wire API, phải ghi phát sinh và dừng tại cổng phạm vi để duyệt.

## 10. Phát sinh

- Scope toàn workspace của stage plan sẽ báo hai file contract từ giai đoạn trước và ba file Firebase có sẵn. Lượt plan chỉ tạo artifact/evidence trong work/5.13; không tự dọn baseline. Chỉ kết luận scope toàn workspace đạt nếu script thực sự không còn báo ngoài phạm vi.
- Nếu cần cập nhật schema/C4 chính thức trong docs, hiện chưa có trong requirement/plan; ghi đề xuất để duyệt riêng, không sửa lén docs. Không thay đổi workbook testcase tổng ở lượt plan này.
- P1–P7 là phần implement; P8 thuộc giai đoạn test sau approval implement. Giai đoạn test còn phải theo wf-test/wf-testcase cho artifact test case/report của quy trình; nếu cần thêm file ứng dụng/spec ngoài bảng phải xin mở phạm vi, không dùng yêu cầu artifact để mở rộng code.

## Bước tiếp theo

- Đang chờ: người duyệt xem plan và baseline scope đã nêu; chưa viết code hoặc chạy test/DB reset.
- Lệnh người duyệt: `python .agents/scripts/gate.py approve 5.13 plan`.
- Sau approval: chạy gate implement; dùng wf-implement, wf-git, wf-health-endpoint và wf-db-migration, làm lần lượt P1–P7 trên Backend `feat/list-linked-patients`; chỉ sửa file được liệt kê. Dừng tại artifact implement trước khi P8.
- Kiểm tra lượt plan: `gate.py 5.13 plan` PASS (`evidence/plan-gate.log`); parser `scope.plan_entries` đọc được đúng 25 entry, đều thuộc Backend (`evidence/plan-file-table.log`). Đây là kiểm tra artifact, không phải test ứng dụng.
- `scope.py 5.13 --stage plan` exit 1 (`evidence/plan-scope.log`): báo đúng hai file contract đã có từ giai đoạn trước và ba file Firebase có sẵn nêu trong Phát sinh; không có file Backend ứng dụng bị sửa trong lượt plan. Người duyệt cần ghi nhận baseline khi xét plan; không tuyên bố scope toàn workspace pass hoặc tự dọn file của người dùng.
- Cập nhật lần cuối: 2026-11-10, Codex.
