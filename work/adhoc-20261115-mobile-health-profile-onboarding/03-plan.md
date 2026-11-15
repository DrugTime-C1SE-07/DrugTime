---
task: adhoc-20261115-mobile-health-profile-onboarding
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-15 22:50 +0700
content_hash: sha256:33aee035198e1847
inputs:
  01-requirement.md: sha256:c60e413f4f65fe0d
  02-contract.md: sha256:8322c29321d72f58
---

# S08b–S08e · Kế hoạch triển khai

## 1. Giải pháp

- **Flutter.** Dùng entry point Flutter thực tế. CTA S08a mở một wizard chứa S08b và S08c. S08b/S08c dùng chung khung header, tiến độ, lưới chọn và footer; trạng thái chọn đơn/đôi nằm trong form. Hai mục “Thêm … khác” mở bottom sheet trên đúng form, với scrim, safe area, Hủy/Thêm, kiểm nội dung trước khi thêm. Back từ S08c về S08b giữ nháp; back từ S08b về S08a. Dùng một nguồn trạng thái trong phiên, hủy kết quả tải cũ khi phiên/tài khoản đổi hoặc flow bị đóng.
- **Dữ liệu.** Nạp snapshot và hai danh mục qua ApiClient có phiên xác thực. Tải đủ trang `GET /conditions` rồi mới hoàn thành tải. Gắn ID thực với lựa chọn; dùng mapping trình bày để tái tạo tên Việt, icon và thứ tự Figma cho mục đã đối chiếu. Giữ các ID đã lưu ngoài nhóm thiết kế có thể xem/chỉnh, tránh vô tình xóa vì không hiện ở hàng đầu. Lỗi tải có nút thử lại; không hiện dữ liệu rỗng giả.
- **Điều hướng khi lưu.** S08b tiến tới S08c với nháp. Bỏ qua bỏ thay đổi của bước đó khỏi payload; chọn “không có … đã biết” loại trừ mục cụ thể. S08c hoàn tất bằng một PUT chứa các bước đã khai. Chặn gửi lặp khi đang lưu. Nếu mất phản hồi hoặc 409, GET để đối chiếu tập ID và tên đã chuẩn hóa; chỉ báo thành công khi snapshot xác nhận đúng thay đổi đã gửi. Nếu khác, giữ nháp và yêu cầu người dùng so lại trước khi thử với revision mới. Không lưu offline. Nếu cả hai bước bỏ qua thì về Trang chủ. S08e dựng thẻ tóm tắt từ snapshot thành công, dùng biến thể “Không có bệnh nền đã biết” đúng frame khi backend trả `none_known`; `unreported` hiển thị trạng thái chưa khai. “Vào ứng dụng” đóng toàn bộ luồng về Trang chủ.
- **Backend.** Module catalog sở hữu danh mục dị ứng chung đã chốt theo Figma và expose qua `GET /allergens` cùng façade dùng lại để kiểm ID. Module medication sở hữu snapshot và dùng các liên kết `user_conditions` hiện có, chỉ thêm/xóa phần chênh lệch, giữ ID, subtype và stage của liên kết còn chọn. Phần tên tự nhập, dị ứng và xác nhận không có lưu riêng. Đồng bộ cờ xác nhận và revision khi POST/PATCH/DELETE liên kết cũ.
- **Giao dịch.** Dùng chung khóa theo user trên hàng `users` (`FOR NO KEY UPDATE`, cùng thứ tự khóa trước hàng dữ liệu y tế) cho GET snapshot, PUT, ghi liên kết cũ và xóa dữ liệu tài khoản. Sau PEP, lấy khóa, kiểm revision, đổi dữ liệu và ghi thành công trong cùng UoW. Xử lý erasure theo cùng thứ tự khóa, kiểm trạng thái tài khoản dưới khóa trước khi ghi để tránh tái tạo dữ liệu sau erasure. Hồ sơ chưa có revision sử dụng giá trị ban đầu nhất quán đến khi có thay đổi thực.
- **PEP.** Dùng `resolve_access`/Consent Guard/Access Log Writer hiện có và bổ sung chế độ chính chủ cho riêng route mới ở façade access. Selector ngoài chính chủ phải từ chối kể cả có link gia đình. Query sai trả 422 theo contract; từ chối dùng audit độc lập và metadata tối thiểu. Với selector sai/không tồn tại mà không thể dùng làm FK audit, dùng tài khoản chính chủ đã xác thực làm subject audit của lần cố truy cập, không ghi giá trị selector vào log. Giữ hành vi route cũ.

## 2. Khảo sát

| Nguồn đã đọc | Điều rút ra |
|---|---|
| `01-requirement.md`, `02-contract.md`, clone `scratch/api_contract/openapi.json` | Hai artifact đã duyệt. Contract có ba operation mới, lưu cuối luồng, revision chung và schema không phá vỡ. |
| Figma `Prototype_DrugTime / Page 1`, ảnh render của cả 13 node trong requirement | Canvas 375 × 812. S08b có hai nhóm thẻ, S08c có một lưới 2 cột, CTA mặc định mờ và được bật khi có lựa chọn. Thẻ chọn có nền/viền xanh và dấu check. Sheet “Thêm” giữ màn bên dưới scrim. S08e có mascot, hai hàng tóm tắt và CTA đáy. Dữ liệu Reqwise đọc được không xác nhận liên kết prototype. |
| Checkout S08a tại `work/adhoc-20261115-mobile-health-profile-intro/scratch/checkout/frontend`, HEAD `8216e79` | Có router, luồng popup và mã S08a đang có thay đổi cục bộ. CTA Dị ứng vẫn là fallback. Đóng gói phần S08a đã review vào baseline task trước khi sửa; đối chiếu diff với 06-review, không chép demo web. |
| `frontend/mobile/lib/main.dart`, `app/app.dart`, `app/router.dart`, `core/api/api_client.dart`, `features/profile/data/repositories/remote_profile_repository.dart` | ApiClient đã có GET/PUT; profile repository và DI là mẫu dùng lại. Tách repository onboarding để tránh đổi interface profile cũ và các fixture hiện có. |
| `backend/src/drugtime/modules/medication/adapters/inbound/profile_http.py`, `application/manage_user_conditions.py`, `adapters/outbound/sql_user_conditions.py`, `sql_medication.py` | HTTP/UoW, DB link và luồng erasure đã tồn tại. Erasure xóa link bệnh nền, còn bảng người dùng được ẩn danh; cần xóa snapshot rõ ràng. |
| `backend/src/drugtime/modules/catalog/api.py`, `adapters/inbound/conditions_http.py`, `condition_schemas.py`, migration `20260927082912_rebuild_schema_v11.sql` | `GET /conditions` trả id/name phân trang. Không thấy bộ seed đầy đủ 8 tên S08c trong checkout. Bảng cần giá trị nghiệp vụ cho `medical_nature` và `data_role`; không tự gán nhóm lâm sàng cho nhãn rộng. |
| `backend/src/drugtime/modules/access/api.py`, `application/authorize.py`, `domain/rules.py`, `backend/tests/architecture/test_health_route_enforcement.py` | PEP dùng chung có audit chính chủ cho HEALTH_PROFILE; registry kiểm bearer/identity/metadata. User identity có ID và is_admin, quan hệ người thân nằm ở link, không có cờ role caregiver độc lập. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 9 và 11, checkout hiện tại | QD-31/32/33/40 đã chốt. CS-01 và CS-04 còn ⏳ trong tài liệu, còn AGENTS.md và contract đã yêu cầu PEP/audit độc lập cho task này. |
| `06-review.md`, clone Flutter `health_setup.dart` và `health_setup_controller.dart`, clone backend `domain/health_setup.py` | Khi mất phản hồi PUT, Flutter đọc lại và so chuỗi nguyên dạng. Backend lưu tên sau khi cắt khoảng trắng và chuẩn hóa NFC. Backend dùng casefold để phát hiện tên trùng, còn việc xác nhận kết quả lưu phải phân biệt hoa thường. |
| `06-review.md`, `04-impl-notes.md`, `evidence/implement-review-db.log` | Bản sửa AC8 đưa PEP lên trước khi parse JSON, giữ audit allowed và thao tác ghi trong cùng UoW. Ba ca PostgreSQL mới đạt trong scratch và cần đưa vào suite tích hợp của task. |

### Quyết định nghiệp vụ áp dụng

| Quy tắc nguồn | AC | Bước và test |
|---|---|---|
| QD-31 mục 9, đã chốt — consent append-only; flow không tự ghi consent | AC1, AC8 | P4/P6/P8; kiểm lần mở, bỏ qua và consent bị rút. |
| QD-32 mục 9, đã chốt — admin không được vượt quyền | AC8 | P4/P8; admin, người thân có/không có link và selector trỏ sang người khác. |
| QD-33 mục 9, đã chốt — audit allowed/denied tối thiểu, fail-closed | AC8–AC9 | P4/P8; DB audit với body sai schema, JSON lỗi cú pháp hoặc body rỗng, lỗi transaction, log không chứa payload. |
| CS-01/04 mục 9, ⏳ tại nguồn; AGENTS.md và contract bắt buộc với task | AC8–AC9 | P4/P8; CI registry và test denied còn sau rollback. |
| QD-40 mục 11, đã chốt cho gợi ý món ăn — thiếu/chưa biết khác xác nhận không có | AC4, AC6 | P3/P7/P8; test `unreported`, `none_known`, bỏ qua; không sửa luồng gợi ý món ăn. |

## 3. File sẽ thay đổi

Các đường dẫn là tính từ gốc từng submodule. Các dòng baseline S08a được phép mang qua đúng bản đã review khi chưa có trên nhánh đích.

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| api_contract | openapi.json | Sửa | Áp patch contract đã duyệt trên nhánh tích hợp của task. |
| backend | supabase/migrations/*_health_profile_onboarding.sql | Thêm | Bảng snapshot, ràng buộc, RLS và grant. |
| backend | supabase/migrations/*_health_profile_condition_catalog.sql | Thêm nếu cần | Dữ liệu danh mục tham chiếu đã đối soát Q1. |
| backend | src/drugtime/modules/catalog/api.py | Sửa | Expose quyết định danh mục dùng chung và gắn route. |
| backend | src/drugtime/modules/catalog/domain/allergen.py | Thêm | Danh mục chuẩn dị ứng cho cả đọc và kiểm ID. |
| backend | src/drugtime/modules/catalog/adapters/inbound/allergens_http.py | Thêm | Endpoint danh mục xác thực, schema và mã lỗi. |
| backend | src/drugtime/modules/access/api.py | Sửa | Truyền tùy chọn chỉ chính chủ cho route mới. |
| backend | src/drugtime/modules/access/application/authorize.py | Sửa | PEP self-only và audit denied an toàn với selector lạ. |
| backend | src/drugtime/modules/medication/api.py | Sửa | Đăng ký router onboarding. |
| backend | src/drugtime/modules/medication/domain/health_setup.py | Thêm | Snapshot, các trạng thái và chuẩn hóa tên. |
| backend | src/drugtime/modules/medication/application/manage_health_setup.py | Thêm | Use case đọc/ghi, validate, revision, reconcile liên kết. |
| backend | src/drugtime/modules/medication/application/manage_user_conditions.py | Sửa | Đồng bộ revision/cờ trạng thái trên API cũ. |
| backend | src/drugtime/modules/medication/application/profile_ports.py | Sửa | Port snapshot và kiểm khóa/revision. |
| backend | src/drugtime/modules/medication/adapters/inbound/health_setup_http.py | Thêm | GET/PUT, UoW, response lỗi và route metadata. |
| backend | src/drugtime/modules/medication/adapters/inbound/health_setup_schemas.py | Thêm | Schema HTTP và validation. |
| backend | src/drugtime/modules/medication/adapters/inbound/profile_http.py | Sửa | Đưa repo đồng bộ revision vào API link cũ. |
| backend | src/drugtime/modules/medication/adapters/outbound/other_modules.py | Sửa | Access adapter và kiểm ID qua catalog façade. |
| backend | src/drugtime/modules/medication/adapters/outbound/sql_health_setup.py | Thêm | Khóa, đọc/ghi snapshot và revision. |
| backend | src/drugtime/modules/medication/adapters/outbound/sql_medication.py | Sửa | Xóa dữ liệu mới khi erasure theo thứ tự khóa chung. |
| backend | tests/unit/test_health_setup*.py | Thêm | Logic chuẩn hóa, API và đối chiếu OpenAPI mới. |
| backend | tests/unit/test_profile_http.py | Sửa nếu cần | Cập nhật fixture cho port mới, giữ test API cũ. |
| backend | tests/unit/test_profile_use_cases.py | Sửa nếu cần | Cập nhật fixture port và regression revision. |
| backend | tests/architecture/test_health_route_enforcement.py | Sửa | Đăng ký hai health operation mới. |
| backend | tests/integration/test_health_setup*.py | Thêm ở giai đoạn test | DB, phân quyền, migration, erasure và concurrency. |
| frontend | mobile/lib/main.dart | Sửa | Truyền repository API thực vào app. |
| frontend | mobile/lib/app/app.dart | Sửa | Cung cấp dependency theo phiên app. |
| frontend | mobile/lib/app/router.dart | Sửa | Mang baseline S08a và đăng ký flow wizard. |
| frontend | mobile/lib/features/home/presentation/screens/home_screen.dart | Mang baseline nếu thiếu | Kết nối popup → S08a đã review. |
| frontend | mobile/lib/features/profile/presentation/screens/health_profile_intro_screen.dart | Mang baseline và sửa | Gắn CTA sang S08b. |
| frontend | mobile/lib/features/profile/domain/entities/health_setup.dart | Thêm | Trạng thái step, snapshot, nháp, item. |
| frontend | mobile/lib/features/profile/domain/repositories/health_setup_repository.dart | Thêm | API của wizard. |
| frontend | mobile/lib/features/profile/data/repositories/remote_health_setup_repository.dart | Thêm | Adapter API, phân trang và lỗi. |
| frontend | mobile/lib/features/profile/presentation/state/health_setup_controller.dart | Thêm | Nạp, thao tác, lưu, reconcile. |
| frontend | mobile/lib/features/profile/presentation/screens/health_setup_*.dart | Thêm | Wizard, biểu mẫu và màn hoàn tất. |
| frontend | mobile/lib/features/profile/presentation/widgets/health_setup_*.dart | Thêm | Thẻ chọn, sheet nhập, tóm tắt và khung tiến độ. |
| frontend | mobile/assets/images/health_setup/ | Thêm | Mascot và minh họa Figma cần xuất. |
| frontend | mobile/assets/icons/health_setup/ | Thêm | Icon đúng bản Figma khi chưa có asset dùng chung. |
| frontend | mobile/pubspec.yaml | Sửa | Đăng ký assets và khai báo thư viện Dart chuẩn hóa Unicode NFC. |
| frontend | mobile/pubspec.lock | Sửa | Khóa phiên bản thư viện NFC và dependency cần thiết sau khi resolve. |
| frontend | mobile/test/features/home/home_screen_test.dart | Mang baseline nếu thiếu | Hồi quy Trang chủ → popup → S08a. |
| frontend | mobile/test/features/profile/health_profile_intro_screen_test.dart | Mang baseline và sửa | S08a → S08b và back. |
| frontend | mobile/test/features/profile/*health_setup*.dart | Thêm | Adapter, controller, màn và routing widget tests. |

## 4. Checklist

- [ ] P1 [api_contract, frontend] Cố định baseline task. Kiểm hash patch rồi đưa contract đã duyệt vào nhánh task. Trong clone Flutter, tích hợp bản S08a đã review trên nền có popup, tái hiện smoke Trang chủ → S08a trước khi đổi CTA. — file: `openapi.json`, các file baseline trong bảng — AC: AC1, AC2 — xong khi patch đúng SHA và smoke baseline qua.
- [ ] P2 [backend] Thêm schema mới theo mục Migration; chốt danh mục dị ứng 8 mục và đối soát nguồn 8 mục S08c theo Q1, giữ ID và phân loại có sẵn. — file: migrations, catalog — AC: AC2, AC3, AC5, AC10 — xong khi dữ liệu danh mục dùng được qua API và DB sạch khởi tạo thành công.
- [ ] P3 [backend] Cài domain/use case và adapter UoW. Khóa cùng user, validate cả payload trước ghi; bảo toàn link metadata, sync cờ/revision qua API cũ, xóa snapshot ở erasure. — file: medication domain/application/outbound, profile_http — AC: AC4–AC7, AC9, AC10 — xong khi pass unit và so sánh round-trip.
- [ ] P4 [backend] Thêm GET/PUT health setup và GET allergens với schema, response lỗi, no-store; reuse PEP, kiểm chính chủ và đăng ký CI. — file: router, schema, access, registry và unit — AC: AC5–AC9 — xong khi route match contract, unit/architecture pass và fail-closed được kiểm.
- [ ] P5 [frontend] Nối repository vào phiên app, dựng controller. Đọc đủ trang, kiểm snapshot chuẩn, tách lỗi tải và lỗi lưu, giữ nháp và đối chiếu revision khi mất phản hồi. — file: main/app, entity/repo/controller và test — AC: AC3–AC7 — xong khi adapter/controller tests qua.
- [ ] P6 [frontend] Thay fallback S08a bằng wizard, dựng S08b/S08c và hai bottom sheet theo Figma, nối back/skip. Đối chiếu viewport 375 × 812, thứ tự, token, safe area, trạng thái CTA. — file: router, screen/widget, asset và test — AC: AC1–AC4 — xong khi luồng vào qua popup và widget tái hiện đủ 12 trạng thái form.
- [ ] P7 [frontend] Dựng S08e và đóng wizard về Trang chủ. Tóm tắt dựa trên snapshot, chặn xác nhận giả/lặp, thử bỏ qua cả hai và lỗi. — file: screen/widget/controller và test — AC: AC2, AC5–AC7 — xong khi widget xác nhận đúng cả điều hướng và nội dung.
- [ ] P8 [backend, frontend] Test DB thật, luồng staging/thiết bị, đối chiếu ảnh app và Figma của 13 node, kiểm màn hẹp/200% chữ. — file: integration test trong giai đoạn test, evidence task — AC: AC1–AC10 — xong khi có log, ảnh và báo cáo từng trạng thái.
- [ ] P9 [frontend] Đối chiếu tập tên tự nhập ở cả nháp đã gửi và snapshot đọc lại bằng trim rồi NFC qua thư viện Dart tương thích SDK hiện tại. So sánh phân biệt hoa thường, giữ nguyên kiểm trạng thái bước, ID và quy tắc bỏ qua. — file: `pubspec.yaml`, `pubspec.lock`, `health_setup.dart`, test controller — AC: AC7 — xong khi ca mất phản hồi với tên tiếng Việt tổ hợp chỉ gửi PUT một lần, đọc lại xác nhận đã lưu, và ca tên khác thực sự vẫn báo xung đột.

Khi tiếp tục P8, chuyển ba ca đã chạy trong scratch vào `backend/tests/integration/test_health_setup_api.py`. Với link chia sẻ đang hoạt động và selector trỏ sang bệnh nhân khác, kiểm từng body `{}`, JSON sai cú pháp và body rỗng trả 403, mỗi lần ghi đúng một dòng audit denied và không tạo snapshot.

## 5. Test

### Unit, widget và kiến trúc

| Test dự kiến | AC | Nơi chứa |
|---|---|---|
| `test_health_setup_normalizes_and_rejects_blank_duplicate_and_missing_ids`; `test_none_known_excludes_items_and_skip_preserves_step` | AC4, AC5 | backend/tests/unit/test_health_setup_use_cases.py |
| `test_health_setup_noop_and_stale_revision`; `test_retained_condition_link_keeps_metadata` | AC6, AC7, AC10 | Cùng file |
| `test_health_setup_openapi_and_errors`; `test_health_setup_authorization_precedes_payload_access`; kiểm registry | AC5, AC7–AC9 | backend/tests/unit/test_health_setup_http.py và registry |
| `loads all condition pages and maps server snapshot`; `does not show empty or confirmation on error`; `reconciles save after timeout without sending duplicates` | AC3, AC5–AC7 | mobile/test/features/profile/*health_setup*.dart |
| Mất phản hồi PUT, GET trả tên đã NFC hóa tương đương và controller xác nhận lưu với đúng một PUT. GET trả tên khác thì giữ nháp và báo xung đột. | AC7 | mobile/test/features/profile/*health_setup*.dart |
| `welcome opens S08a and exactly one S08b`; `back and skip preserve intended state`; `selection and custom-name variants render`; `success opens S08e once` | AC1–AC7 | mobile/test/features/home và mobile/test/features/profile |
| Đối chiếu ảnh cả 13 frame, keyboard/safe area, chữ lớn và cuộn | AC2 | evidence giai đoạn test |

### Tích hợp

| Test dự kiến | AC | Nơi chứa |
|---|---|---|
| `test_health_setup_roundtrip_selected_custom_and_none_known`; `test_skip_keeps_stored_step`; `test_catalog_order_and_real_condition_ids` | AC3–AC6 | backend/tests/integration/test_health_setup_api.py |
| `test_atomic_save_rolls_back_both_steps`; `test_parallel_put_and_legacy_link_write`; `test_uncertain_write_readback` | AC6–AC7, AC9 | Cùng file |
| `test_patient_self_audit_and_revocation_next_request`; `test_admin_and_cross_patient_denied_with_or_without_link`; `test_missing_selector_target_and_durable_audit_failure` | AC8–AC9 | backend/tests/integration/test_health_setup_access.py |
| `test_cross_patient_invalid_body_audits_denial` với sai schema, JSON lỗi cú pháp và body rỗng | AC8 | backend/tests/integration/test_health_setup_api.py |
| `test_legacy_profile_after_migration_and_write`; `test_db_roles_constraints_and_erasure` | AC10, AC8 | backend/tests/integration/test_health_setup_storage.py |
| Luồng Flutter dùng API staging và tài khoản kiểm thử; vào từ popup, lưu rồi mở lại, test mất mạng | AC1, AC5–AC7 | Báo cáo và evidence của task |

Chạy `pytest tests/unit tests/architecture`, `ruff check .`, `supabase db reset`, bộ test tích hợp tương ứng, `flutter analyze` và `flutter test`. Lưu log theo gate.

## 6. Migration

- Tạo migration mới bằng `supabase migration new health_profile_onboarding`. Bảng `health_profile_setup` có `user_id uuid` PK/FK đến users, ON DELETE CASCADE; `revision bigint` không âm; cờ `allergies_none_known` và `conditions_none_known`; ba mảng text không null (allergen IDs, tên dị ứng tự nhập, tên bệnh nền tự nhập). Dùng default rỗng/false và CHECK phù hợp cho kích thước tên, null phần tử và loại trừ cờ với dữ liệu cùng bước. Danh mục dị ứng ổn định do catalog module kiểm khi ghi; trạng thái bệnh nền suy kết hợp với link DB để tương thích dữ liệu cũ. PK và unique `user_conditions(user_id, condition_id)` phục vụ tra cứu theo user.
- Bật RLS; không thêm policy client. Revoke mặc định từ PUBLIC/anon/authenticated/service_role; cấp API SELECT/INSERT/UPDATE và DELETE cho role thực sự thực thi erasure. Kiểm quyền tối thiểu theo luồng xóa hiện tại. Không sửa access_logs hay migration cũ. Thêm bản ghi tham chiếu công khai nếu cần sau đối soát Q1; không backfill sức khỏe theo suy đoán, không rename/xóa ID bệnh nền có sẵn.
- Reset DB sạch và kiểm trên fixture hồ sơ có dữ liệu cũ. Kiểm quyền SQL từng role, ràng buộc, audit append-only, xóa hồ sơ và cuộc đua lưu/xóa. Ghi schema/ERD là việc phát sinh nếu team yêu cầu.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| Superproject, api_contract, backend, frontend | `feat/adhoc-20261115-mobile-health-profile-onboarding` trên checkout riêng khi root đang làm task khác. |

## 8. Rủi ro

- Các mục rộng như “Tim mạch”, “Thận” và “Hen / COPD” không tương đương tự động với một chẩn đoán cụ thể. Mapping theo ID sau đối chiếu nguồn và giữ nhóm/metadata lâm sàng do danh mục xác nhận, tránh làm sai gợi ý/tương tác.
- Dữ liệu S08a chưa có commit tích hợp trong checkout đã khảo sát. Clone theo HEAD của task trước rồi copy đúng file thuộc diff đã review nếu chưa có nhánh chứa bản đó. Không dùng fixture demo làm entry point thực tế.
- API cũ và onboarding cùng sửa liên kết. Khóa theo user và revision phải bao phủ cả hai, kể cả tác vụ xóa tài khoản. Kiểm test song song và lỗi audit, bao gồm consent rút sau tải.
- Ảnh xuất có viền 1 px và status bar mô phỏng. So vùng nội dung cùng kích thước canvas; dùng insets hệ điều hành cho app, không vẽ hai status bar.
- Khi thêm thư viện NFC, kiểm tương thích SDK và diff lockfile để phát hiện nâng phiên bản dependency không liên quan. Ca đối chứng tên khác bảo đảm app chỉ xác nhận lưu khi dữ liệu đọc lại khớp.

## 9. Câu hỏi mở

- **Q1 — Danh mục bệnh nền.** Đối soát dữ liệu backend mục tiêu trước khi lập mapping 8 ô. Mặc định dùng ID catalog tương đương đã xác nhận; nếu thiếu, thêm bản ghi tham chiếu đúng ngữ nghĩa trong migration đã liệt kê. Nếu danh mục không có ngữ nghĩa tương đương hoặc phân loại bắt buộc còn thiếu, xác nhận với người dùng trước khi nạp mục đó.
- **Q2 — Liên kết prototype.** Ảnh và node đã đối chiếu; kết nối Reqwise chưa cung cấp đích reaction để xác nhận các nhánh Bỏ qua/Tiếp tục. Mặc định triển khai giả định requirement đã duyệt về lưu cuối, bỏ qua và S08e. Nếu đối chiếu prototype cho hành vi khác, báo điểm khác để xử lý trước khi thay hành vi đã duyệt.

## 10. Phát sinh

- `scope.py --stage plan` báo 1.267 file ngoài phạm vi như hai giai đoạn trước. Evidence tại `evidence/plan-scope.log`. Lượt này chỉ ghi dưới thư mục task. Checkout chính đang ở nhánh của task khác; apply contract/triển khai ở clone task và xác minh diff riêng.
- Kiểm lại khi bổ sung P9 cho cùng kết quả 1.267 mục tại root. Xem `evidence/plan-review-scope.log`. Hai clone code giữ nguyên trong lượt cập nhật plan.
- Lưu ảnh đối chiếu ở evidence khi implement/test. Các mẫu bổ sung lỗi tải/lưu và nội dung tóm tắt cho dữ liệu khác frame sẽ dùng cùng token/layout, ưu tiên hiển thị đúng giá trị backend.

## Bước tiếp theo

- Đang chờ duyệt plan. Chạy `python .agents/scripts/gate.py approve adhoc-20261115-mobile-health-profile-onboarding plan`.
- Sau khi duyệt lại, tiếp tục implement từ P9. Giữ bằng chứng bản sửa P4, sau đó cập nhật suite tích hợp và báo cáo ở giai đoạn test.
- Cập nhật ngày 2026-11-15, Codex.

