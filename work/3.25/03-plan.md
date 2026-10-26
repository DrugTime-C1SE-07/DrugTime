---
task: 3.25
stage: plan
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-24 22:15 +0700
content_hash: sha256:13b8c04b8e364a8a
inputs:
  01-requirement.md: sha256:717a7d0a0b7c604b
---

# 3.25 · Plan kiểm thử lịch sử tuân thủ cho người thân

## 1. Giải pháp

Kiểm thử theo ba lớp: unit kiểm công thức/biên và contract, widget/controller kiểm dữ liệu chỉ ở bộ nhớ phiên, integration/E2E kiểm API thật với PostgreSQL và luồng Mobile. Dùng lại fixture `history_data`, PEP và các ca quyền/audit đang có; chỉ thêm ca chưa được chứng minh. Không sửa production code hoặc contract trong task test. Test thất bại do sản phẩm sẽ giữ nguyên và được ghi lỗi kèm chứng cứ.

Thứ tự phụ thuộc: (1) xác minh contract 3.23 có `/adherence` và UI 3.24 có màn lịch sử; (2) chạy baseline, so sánh AC với các test hiện có; (3) bổ sung test unit/widget; (4) bổ sung test tích hợp và E2E; (5) chạy bộ test, lập truy vết và test case Excel. Hiện hai tiền đề ở bước (1) **chưa có** trong checkout; không tuyên bố AC đạt khi chưa chạy được. `summary.adherence_rate` phải tính liều xác nhận hợp lệ ngay cả trước +120 phút theo quyết định người dùng ngày 23/10/2026; liều chưa xác nhận chỉ vào mẫu số sau +120 phút.

Giữ các ca PostgreSQL/PEP trong pytest vì cần kiểm response cùng trạng thái DB/audit. Không dựng thêm Postman collection trùng các ca đó. Ca xuyên thiết bị dùng local DB/backend và Android test package riêng, theo tiền lệ `tests/e2e/mobile_redeem`; không dùng hệ thống deploy hoặc dữ liệu thật.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/3.25/01-requirement.md` (approved 23/10/2026 15:11 +0700) | AC1–AC9; size L, không đổi contract, phạm vi backend/frontend/tests/docs; `docs` chỉ gồm workbook tổng. AC3 có ngoại lệ tính xác nhận trước +120 phút. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 5, 8, 9, 12, 14, 16; baseline `QD-2026-10-03-v1` | QD-03/10/27/28/29/33/42/45 trạng thái ✅; BS-01 🆕. CS-01/04 vẫn ⏳, nên dùng bất biến PEP trong `AGENTS.md` làm tiêu chí kiểm thử, không ghi chúng thành quyết định đã chốt. |
| `api_contract/openapi.json`; `backend/tests/unit/test_contract_adherence.py` | Checkout hiện không có path/schema adherence trong contract chuẩn; unit test contract phụ thuộc path đó. Cần bản 3.23 trước khi xác nhận wire contract hoặc báo phụ thuộc. |
| `backend/src/drugtime/modules/adherence/adapters/inbound/history_http.py`, `application/get_adherence_history.py`, `domain/history.py`; `adapters/outbound/other_modules.py` | Endpoint có `x-health-scope`, gọi authorize trước khi đọc; tính `taken + late` ngay khi log hợp lệ, `pending` tới đúng +120 phút. Không thêm đường kiểm quyền riêng. |
| `backend/tests/architecture/test_health_route_enforcement.py`; `backend/tests/unit/test_access_authorize.py`, `test_get_adherence_history.py` | Có kiểm registry health route, không cache quyền, thứ tự authorize→read và fail-closed. Có thể thêm test AC3 vào file unit hiện có. |
| `backend/tests/integration/test_adherence_history_api.py`, `test_adherence_history_access.py` | Đã phủ nhóm/ngày, biên 120, success/403/audit/thu hồi/rollback/race; `assert_contract` lấy schema từ contract. Tên `__ACn` hiện tham chiếu AC của 3.23, không mặc nhiên tính là bằng chứng AC 3.25. |
| `frontend/mobile/lib/features/family/**`, `frontend/mobile/test/features/family/**` | Chưa có UI lịch sử của 3.24; `FamilyAlertController` và test của nó là mẫu xóa RAM, hủy response đến muộn, widget read-only. Test 3.25 sẽ dùng API thực của 3.24 khi xuất hiện, không tạo UI thay. |
| `tests/e2e/mobile_redeem/run_e2e.py`, `test_run_e2e.py`, `README.md` | Mẫu preflight loopback/thiết bị, redaction token, fixture DB cục bộ và cleanup; runner lịch sử riêng sẽ giữ các bảo vệ đó. |
| `.agents/skills/wf-health-endpoint/SKILL.md`; `.agents/skills/wf-test/SKILL.md`; `.agents/skills/wf-testcase/SKILL.md`; `AGENTS.md` | Cần kiểm PEP, `patient_id`, hai consent, denied log bền, fail-closed, route registry; cuối test phải gộp test case Excel vào file tổng. |
| `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | File tổng hiện có; `01` đã duyệt lại cho phép gộp đúng một sheet chức năng PB21 và dựng lại Report theo `wf-testcase`, giữ các sheet chức năng khác. |
| `frontend/mobile/integration_test/redeem_e2e/**`; `tests/e2e/mobile_redeem/README.md` | E2E cần cả test Flutter và runner Python. Test Flutter mới dùng màn production 3.24, không thay bằng màn giả; chuẩn bị file trong giai đoạn implement, runner trong giai đoạn test. |
| `postman/` và skill `postman:api-testing` | Không có saved request phù hợp trong `postman/collections/`; pytest hiện có kiểm được cả API và PostgreSQL/audit. Giữ bộ test này làm bằng chứng, không tạo collection trùng hoặc suy Pass từ HTTP 200. |

### Quyết định nghiệp vụ áp dụng và truy vết

| Quy tắc (nguồn/trạng thái) | AC | Bước | Test |
|---|---|---|---|
| QD-27/28, mục 8, ✅: người thân chỉ xem; link active + bật chia sẻ + `health_data`/`family_sharing` mỗi request | AC1, AC4, AC5, AC6 | P3, P4, P5, P7 | `test_self_and_family_success...`, `test_unlinked_missing_consents...`, `family_adherence_screen_test`, E2E revoke |
| QD-29, mục 8, ✅: chỉ RAM phiên; xóa lúc mất mạng/vào nền/đăng xuất/thu hồi | AC6 | P3, P4, P7 | `family_adherence_controller_test`, `family_adherence_screen_test`, E2E session |
| QD-33, mục 9, ✅; bất biến PEP trong `AGENTS.md`: audit metadata tối thiểu, denied riêng, fail-closed | AC1, AC4, AC5, AC7 | P5, P6 | `test_adherence_history_access.py`, health route registry |
| QD-03/10, mục 5, ✅; BS-01 🆕: biên −30/+30/+120, hậu xác nhận muộn không tính tuân thủ | AC2, AC3 | P2, P5 | unit biên rate, integration thời điểm/Worker |
| QD-42, mục 12, ✅ + quyết định người dùng 23/10/2026: liều xác nhận hợp lệ được tính ngay; pending tới +120, không có dữ liệu, tỷ lệ đúng giờ và đối soát | AC3, AC8 | P2, P5, P6 | unit rate, integration rate, contract/khả năng biểu diễn QD-42 |
| QD-45, mục 14/16, ✅: contract chuẩn và truy vết PB–test | AC9 | P1, P8 | kiểm path/schema, bảng AC→test→log, testcase Excel |

Các nhánh nguồn chưa xác định đủ để khẳng định kết quả số của tỷ lệ đúng giờ riêng hoặc dữ liệu xung đột/đối soát trong contract hiện tại sẽ được ghi **chưa nghiệm thu** nếu bản 3.23 không đặc tả. Không tự tạo field hay oracle từ tên gợi ý.

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `backend` | `tests/unit/test_get_adherence_history.py` | sửa | Unit test AC3: xác nhận trước +120, pending ở đúng +120, quá hạn và hậu xác nhận. |
| `backend` | `tests/unit/test_contract_adherence.py` | sửa | Kiểm contract `/adherence`, schema/tỷ lệ khi bản 3.23 có; thất bại được báo rõ, không chỉnh contract. |
| `backend` | `tests/integration/test_adherence_history_api.py` | sửa ở giai đoạn test | Ca người thân cho AC2/AC3 và khả năng biểu diễn AC8 bằng dữ liệu DB thật. |
| `frontend` | `mobile/test/features/family/family_adherence_repository_test.dart` | thêm khi UI 3.24 có | Kiểm query `patient_id`, response/error, không lưu bền dữ liệu. |
| `frontend` | `mobile/test/features/family/family_adherence_controller_test.dart` | thêm khi UI 3.24 có | Kiểm đổi bệnh nhân, mất mạng, background, logout, 403 và response đến muộn. |
| `frontend` | `mobile/test/features/family/family_adherence_screen_test.dart` | thêm khi UI 3.24 có | Widget test trạng thái rỗng/chờ/lỗi, dữ liệu đúng bệnh nhân, chỉ xem. |
| `frontend` | `mobile/integration_test/adherence_history_e2e/history_test.dart` | thêm ở implement khi UI 3.24 có | Điều khiển màn production: chọn bệnh nhân, xem lịch sử, đổi bệnh nhân và refresh sau thu hồi; gọi API local thật. |
| `frontend` | `mobile/integration_test/adherence_history_e2e/history_helpers.dart` | thêm ở implement khi UI 3.24 có | Helper phiên/fixture và đồng bộ phase với runner local, không in token hoặc lưu bền lịch sử sức khỏe. |
| `tests` | `e2e/mobile_adherence_history/run_e2e.py` | thêm ở giai đoạn test | Chạy luồng Mobile→API→DB/audit trên môi trường cục bộ, gồm success/revoke/cross-patient. |
| `tests` | `e2e/mobile_adherence_history/test_run_e2e.py` | thêm ở giai đoạn test | Kiểm preflight, redaction, cleanup và kết quả khi thiếu thiết bị/môi trường. |
| `tests` | `e2e/mobile_adherence_history/README.md` | thêm ở giai đoạn test | Hướng dẫn chạy và ma trận AC→phase→bằng chứng. |
| `docs` | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | sửa ở cuối giai đoạn test | Gộp đúng một sheet chức năng lịch sử tuân thủ PB21, giữ các sheet chức năng khác và dựng lại Report/Bug Report bằng script chuẩn. |

Tổng 12 file dự kiến: backend 3, frontend 5, tests 3, docs 1. `work/3.25/testcases.json`, `testcases.xlsx`, các artifact và evidence là đầu ra trong superproject. Nếu cấu trúc UI 3.24 khiến tên file hoặc API test dự kiến không phù hợp, ghi phát sinh và xin cập nhật phạm vi đã duyệt trước khi sửa ngoài bảng.

## 4. Checklist

- [ ] P1 [superproject] Ghi SHA của `backend`/`frontend`/`api_contract`, kiểm path/schema `/adherence` và màn 3.24, so khớp bản đã duyệt; lưu log baseline — file: `work/3.25/evidence/implement-baseline.log` — AC: AC9 — xong khi biết rõ ca có thể chạy và phụ thuộc chưa có, không lấy generated OpenAPI làm chuẩn.
- [ ] P2 [backend] Viết unit test bảng trường hợp `da_uong`, `uong_tre`, pending ở +120, missed sau +120, xác nhận sau +120 và mẫu số 0 — file: `tests/unit/test_get_adherence_history.py` — AC: AC2, AC3 — xong khi từng biên có kỳ vọng số cụ thể từ `01` và test đơn chạy được hoặc fail vì lỗi sản phẩm được ghi.
- [ ] P3 [frontend] Khi 3.24 xuất hiện, test repository gọi đúng `patient_id`, không ghi cache bền, truyền 403/network failure; test controller xóa RAM và vô hiệu response cũ khi đổi bệnh nhân, offline, background, logout, 403 — file: `mobile/test/features/family/family_adherence_repository_test.dart`, `mobile/test/features/family/family_adherence_controller_test.dart` — AC: AC4, AC5, AC6 — xong khi test Flutter chứng minh không có dữ liệu cũ sau mỗi chuyển trạng thái.
- [ ] P4 [frontend] Widget test màn người thân với lịch sử, rỗng, pending, 403; kiểm không có thao tác sửa lịch/xác nhận hộ và không lộ bệnh nhân trước sau đổi lựa chọn. Chuẩn bị test Flutter E2E điều khiển màn production, nhận fixture/phase từ runner local; không sửa cấu hình build production — file: `mobile/test/features/family/family_adherence_screen_test.dart`, `mobile/integration_test/adherence_history_e2e/history_test.dart`, `mobile/integration_test/adherence_history_e2e/history_helpers.dart` — AC: AC1, AC2, AC3, AC6 — xong khi widget test có kết quả thật và test Flutter sẵn sàng chạy xuyên API khi đủ tiền đề; thiếu UI thì ghi Pending, không tạo màn thay.
- [ ] P5 [backend] Sau khi contract 3.23 có trong checkout, chạy và mở rộng ca integration cùng PostgreSQL thật: family success, nhóm/timezone/rate trước và sau +120, xác nhận muộn/Worker, cross-patient, hai consent, sharing off, unlink và cùng token request kế tiếp; đối chiếu response **và** `access_logs` — file: `tests/integration/test_adherence_history_api.py` (tái dùng `test_adherence_history_access.py`) — AC: AC1–AC5, AC7 — xong khi từng kịch bản có kết quả/đường log, ca sai không bị skip hoặc nới lỏng.
- [ ] P6 [backend] Kiểm contract và ca fail-closed: route registry, thứ tự PEP trước đọc, audit `allowed`/`denied` metadata tối thiểu, denied còn sau rollback, lỗi DB/log không trả sức khỏe; đối chiếu khả năng biểu diễn tỷ lệ đúng giờ/liều hủy/xung đột/đối soát theo QD-42 — file: `tests/unit/test_contract_adherence.py` (tái dùng `tests/architecture/test_health_route_enforcement.py`, `tests/integration/test_adherence_history_access.py`, `tests/integration/test_adherence_history_api.py`) — AC: AC1, AC4, AC5, AC7, AC8 — xong khi có test chạy thật hoặc báo rõ field/fixture/contract nào khiến AC8 chưa nghiệm thu.
- [ ] P7 [tests] Khi màn 3.24 và Android local có, chạy E2E người thân chọn bệnh nhân, xem liều, rút consent/thu hồi liên kết rồi xem lại; kiểm preflight chỉ loopback, package test riêng, không in token, cleanup cả khi lỗi — file: `e2e/mobile_adherence_history/run_e2e.py`, `test_run_e2e.py`, `README.md` — AC: AC1, AC4–AC6, AC9 — xong khi có log từng phase hoặc trạng thái Pending với nguyên nhân môi trường cụ thể.
- [ ] P8 [superproject/docs] Ở cuối giai đoạn test, đọc workbook để giữ mã/ID hiện có nếu chức năng đã được bổ sung; lập một chức năng PB21 trong `work/3.25/testcases.json` theo EP, BVA, bảng quyết định và chuyển trạng thái. Chạy `python .agents/scripts/testcase_xlsx.py validate 3.25`, `build 3.25`, `merge 3.25` sau khi chuẩn bị nhánh docs; lưu output vào `work/3.25/evidence/testcase-xlsx.log`. Ghi Pass/Fail chỉ theo log, còn lại Pending; hoàn thiện bảng PB21/QD→AC→test→log và lỗi sản phẩm — file: `work/3.25/testcases.json`, `work/3.25/testcases.xlsx`, `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` — AC: AC1–AC9 — xong khi ba lệnh exit 0, các sheet chức năng khác được giữ, số Fail khớp Bug Report, workbook và báo cáo truy được mọi kết quả thật; nếu script báo xung đột kết quả thì dừng hỏi giữ bên nào.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `test_confirmed_before_deadline_counts_immediately__AC3` và biến thể đúng +30/+120 phút | AC2, AC3 | `backend/tests/unit/test_get_adherence_history.py` |
| `test_unconfirmed_pending_at_deadline_then_missed__AC3`, `test_no_eligible_dose_has_null_rate__AC3`, `test_after_deadline_confirmation_does_not_raise_rate__AC3` | AC3 | `backend/tests/unit/test_get_adherence_history.py` |
| `test_contract_history_fields_and_qd42_representation__AC8` (khi contract 3.23 sẵn sàng) | AC8, AC9 | `backend/tests/unit/test_contract_adherence.py` |
| `family_adherence_repository_test`: query/403/network/no persistent write | AC4–AC6 | `frontend/mobile/test/features/family/` |
| `family_adherence_controller_test`: đổi patient/offline/background/logout/revoke và response muộn | AC5, AC6 | `frontend/mobile/test/features/family/` |
| `family_adherence_screen_test`: lịch sử/rỗng/chờ/403/read-only | AC1–AC3, AC6 | `frontend/mobile/test/features/family/` |
| `test_run_e2e.py`: reject remote DB/API, redact token, cleanup khi lỗi | AC9 | `tests/e2e/mobile_adherence_history/` |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| `test_family_history_rate_transitions__AC1_AC2_AC3` | AC1–AC3; số liều, biên +120, múi giờ | Thêm vào `backend/tests/integration/test_adherence_history_api.py`; dùng `history_data`, không dùng thời gian thật. |
| Ca đang có `test_self_and_family_success...`, `test_unlinked_missing_consents...`, `test_family_patient_selector_tamper...` | AC1, AC4; cross-patient 403 + denied | Tái dùng `backend/tests/integration/test_adherence_history_access.py`, đối chiếu mã lỗi/schema với contract. |
| Ca đang có `test_revoke_sharing_off_unlink_denies_immediate_next_request_same_token...` | AC5; rút quyền tức thì | Kiểm request kế tiếp với cùng token và log `denied`. |
| Ca đang có `test_audit_permission_and_commit_failure_fail_closed...`, `test_denied_audit_survives_outer_transaction_rollback...` | AC7; audit fail-closed/denied bền | Kiểm không trả payload khi lỗi, audit không ghi nội dung y tế. |
| `test_qd42_cancel_conflict_reconcile_contract__AC8` | AC8; loại hủy/xung đột/đối soát | Chỉ thực thi khi bản contract/DB 3.23 có cách biểu diễn; nếu thiếu thì ghi chưa nghiệm thu, không tạo dữ liệu/field giả. |
| `mobile_adherence_history` phase success/revoke/cross-patient | AC1, AC4–AC6, AC9; luồng Mobile→API | Chạy Android local hoặc ghi Pending có lý do. |
| `test_late_sync_worker_log_and_retry_keep_one_occurrence__AC15_AC20`, `test_worker_insert_races_with_valid_late_confirmation__AC15_AC20_AC22` đang có | AC2, AC3; gửi lại cùng client_uuid, Worker chạy đua với xác nhận hợp lệ | Tái dùng `backend/tests/integration/test_adherence_history_api.py`: một occurrence, không ghi đè xác nhận; phân biệt xác nhận hợp lệ đồng bộ muộn với thao tác thực sự sau +120 theo QD-10. |
| Toàn bộ `backend/tests/integration`, `backend/tests/unit tests/architecture`, `flutter test` và E2E liên quan | AC1–AC9; hồi quy quyền, liều và client | Lưu lệnh, số pass/fail/skip và log riêng; không dùng kết quả cũ làm bằng chứng. |

### Manual

- AC6: trên thiết bị thật đưa app vào nền, mất mạng, đổi tài khoản và xem lại; ghi màn/tình trạng sau mỗi bước. Widget test không tự chứng minh lifecycle OS.
- AC9: đối chiếu bảng truy vết với log và workbook; ca không chạy được ghi Pending, không suy ra Pass.

## 6. Migration

Không có. Task chỉ viết/chạy test, không sửa schema hay dữ liệu triển khai. DB local reset sạch trước test tích hợp theo `AGENTS.md`.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `test/3.25` |
| `backend` | `test/3.25` |
| `frontend` | `test/3.25` |
| `tests` | `test/3.25` |
| `docs` | `test/3.25` |

Trước khi sửa submodule ở giai đoạn implement/test: `git status`, `git symbolic-ref -q HEAD`, kiểm thay đổi của người khác; sau đó mới chuyển/tạo nhánh theo `wf-git`. Không commit/push khi người dùng chưa yêu cầu.

Khảo sát phiên 23/10/2026: superproject và bốn submodule đang ở `test/3.15-redeem-flow-tests`; các submodule có working tree sạch nhưng SHA đã khác gitlink của superproject. Phiên plan chỉ sửa `work/3.25/`, giữ nguyên checkout. Giai đoạn implement phải ghi lại trạng thái và tạo/chuyển nhánh `test/3.25` từ baseline đã xác minh, không tự đổi con trỏ hoặc bỏ commit hiện có.

## 8. Rủi ro

- Contract `/adherence` và UI 3.24 vắng trong checkout: test import/compile có thể fail vì thiếu tiền đề. P1 ghi SHA và trạng thái; không vá contract/UI trong 3.25, đánh dấu ca bị chặn.
- QD-42 có phần chưa thể biểu diễn trong response/schema hiện tại; AC8 có thể không đạt. Test giữ kỳ vọng nguồn/contract, lập lỗi hoặc phụ thuộc, không `xfail` để báo xanh.
- Test quyền có thể lộ dữ liệu nếu chỉ kiểm status: P5/P6 so payload, `patient_id`, `access_logs`, no-store và request ngay sau rút quyền; không cache.
- E2E trên điện thoại thật có thể đụng app người dùng: dùng package test riêng, DB/API loopback và preflight trước mọi thay đổi; thiếu điều kiện thì Pending.
- Workbook tổng có thể được tester cập nhật trong thời gian chờ: đọc lại trước merge, giữ các mã/ID cũ và xử lý cảnh báo xung đột kết quả theo `wf-testcase`; chỉ một sheet chức năng PB21 được gộp.

## 9. Câu hỏi mở

Không có câu hỏi mở. Q1 đã được xử lý: `01-requirement.md` được duyệt lại lúc 15:11 +0700 ngày 23/10/2026, bao gồm `docs` chỉ cho file test case tổng. Các khoảng trống contract/UI/QD-42 là phụ thuộc thực thi đã được `01` ghi nhận; chưa đủ bằng chứng thì báo chưa nghiệm thu.

## 10. Phát sinh

- Không có thay đổi production/API mới trong plan. `api_contract` và UI 3.24 chưa có trong checkout như đã ghi ở `01`; đây là phụ thuộc thực thi, không phải quyền sửa chúng ở 3.25.
- Các test backend hiện có mang `__ACn` của task 3.23; báo cáo 3.25 phải ánh xạ lại bằng chứng theo AC1–AC9 hiện hành, không suy từ hậu tố tên test.
- Đã đồng bộ phạm vi workbook theo requirement vừa duyệt lại và bổ sung hai file Flutter integration test còn thiếu để P7 có thể điều khiển màn thật. Không thay đổi AC, nghiệp vụ hoặc production code.
- `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage plan` → OK; log thô: `work/3.25/evidence/plan-scope.log`.

## Bước tiếp theo

- Đang chờ: người duyệt plan; contract 3.23/UI 3.24 để chạy đủ các ca ở giai đoạn sau.
- Việc cần làm: review bản plan đã đồng bộ rồi chạy `python .agents/scripts/gate.py approve 3.25 plan`. Lượt tiếp theo agent dùng `wf-implement`, bắt đầu P1; các file frontend chỉ triển khai khi UI 3.24 có thật. Không bắt đầu implement trong lượt plan này.
- Cập nhật lần cuối: 2026-10-23, Codex.
