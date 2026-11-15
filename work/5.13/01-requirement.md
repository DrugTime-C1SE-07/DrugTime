---
task: 5.13
title: Backend API liệt kê bệnh nhân đã liên kết
type: feature
stage: requirement
size: L
contract_change: yes
affected: [backend, api_contract]
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-10 13:03 +0700
content_hash: sha256:eb0cc2ee1b9c43b1
---

# 5.13 · Backend API liệt kê bệnh nhân đã liên kết

## 1. Mục tiêu

Task 5.13 cung cấp API để Mobile lấy danh sách bệnh nhân mà người thân đang đăng nhập hiện được phép xem, làm nguồn dữ liệu cho bộ chọn bệnh nhân của task 5.14. Sau khi chọn một bệnh nhân, Mobile dùng định danh bệnh nhân đó khi tải các chức năng theo dõi; task 5.15 bảo đảm dữ liệu hiển thị thuộc đúng bệnh nhân đang chọn, và task 5.16 kiểm tra không lẫn/lộ dữ liệu giữa các bệnh nhân. Giá trị nghiệp vụ thuộc PB22: một người thân có thể theo dõi nhiều thành viên gia đình trong cùng tài khoản.

Ví dụ: một người con liên kết với cả bố và mẹ. API 5.13 cung cấp các bệnh nhân có thể chọn; chọn bố thì các chức năng theo dõi dùng định danh bố, chuyển sang mẹ thì dùng định danh mẹ. Endpoint này cung cấp lựa chọn bệnh nhân; các endpoint chức năng tiếp theo vẫn phải kiểm tra quyền hiện hành của đúng bệnh nhân ở mỗi request.

### Truy vết với các task và Product Backlog liên quan

| Mục | Quan hệ với 5.13 |
|---|---|
| PB22; Sprint 5, task 5.13–5.16 | Cùng thực hiện luồng chuyển giữa nhiều bệnh nhân: 5.13 cấp danh sách, 5.14 hiển thị bộ chọn, 5.15 dùng đúng ngữ cảnh bệnh nhân, 5.16 kiểm tra không lộ chéo dữ liệu. Đây là mục đích trực tiếp, có ánh xạ tường minh trong backlog. |
| PB09, PB15, PB19 | Mô hình và luồng tạo liên kết Patient–Family Member cung cấp dữ liệu đầu vào để có bệnh nhân trong danh sách. |
| PB02, PB16, PB17, PB18 | Consent, cho phép chia sẻ, hủy liên kết và tạm dừng chia sẻ quyết định quyền hiện hành; danh sách phải phản ánh thay đổi theo requirement đã chốt. |
| PB21 – lịch sử tuân thủ của bệnh nhân liên kết | Chức năng sử dụng bệnh nhân đã chọn để xác định cần xem lịch sử của ai. Đây là quan hệ sử dụng suy ra từ PB22 và trường `patient_id` trong AC của PB21, không phải mapping trực tiếp của task 5.13. |
| PB26, PB27, PB28 – thông tin thuốc, tương tác thuốc–thuốc, thuốc–thực phẩm | Các chức năng xem theo từng bệnh nhân hưởng lợi từ cùng bộ chọn/ngữ cảnh PB22; vẫn kiểm consent riêng ở mỗi lần gọi. |
| PB39 – gợi ý món ăn cho bệnh nhân liên kết | Dùng ngữ cảnh bệnh nhân đã chọn và consent tương ứng khi xem gợi ý. |
| PB20 – cảnh báo bỏ lỡ liều | Backend xác định bệnh nhân từ sự kiện liều và gửi đến người thân có quyền. Backlog không cho thấy việc gửi cảnh báo cần gọi API danh sách 5.13. |

## 2. Phạm vi

### Trong phạm vi

- Cung cấp API cho tài khoản người thân lấy danh sách bệnh nhân đồng thời có liên kết hoạt động, bật chia sẻ, consent `family_sharing` và `health_data` còn hiệu lực. Thiếu một điều kiện thì bệnh nhân không xuất hiện.
- Trả `patient_id` làm khóa kỹ thuật và tên hiển thị để client chọn đúng bệnh nhân; giao diện chỉ hiển thị tên. Đây là giả định đề xuất để duyệt requirement, không thêm thông tin nhận diện khác.
- Kiểm tra quyền hiện thời từ dữ liệu máy chủ ở mỗi request; ghi audit theo chính sách áp dụng cho dữ liệu người thân.
- Quy định phản hồi khi không có bệnh nhân nào đủ điều kiện và khi xác thực/phân quyền hoặc ghi audit thất bại.
- Bổ sung phân loại audit cho hành động liệt kê bệnh nhân liên kết bằng migration mới: mở rộng enum `access_data_scope` cho scope `danh_sach_benh_nhan_lien_ket`, không dùng nhầm scope thuốc/hồ sơ.
- Hỗ trợ audit metadata ở mức request cho danh sách rỗng và lượt gọi bị từ chối trước khi có patient cụ thể. Nếu cần mở rộng operation/ràng buộc của kho audit sẵn có thì giới hạn thay đổi cho hành động này, không tạo patient giả và không nới quyền sửa/xóa nhật ký.

### Ngoài phạm vi

- Giao diện chọn/chuyển bệnh nhân trên Mobile (nằm trong phần còn lại của PB22, không thuộc task backend 5.13).
- Trả dữ liệu sức khỏe, lịch thuốc, liều, cảnh báo hoặc hồ sơ chi tiết của bệnh nhân.
- Tạo, chấp thuận, từ chối, thu hồi liên kết hay thay đổi công tắc chia sẻ/consent.
- Lưu danh sách bệnh nhân vào bộ nhớ bền vững phía client.
- Đổi dữ liệu nhật ký cũ, đổi nghĩa scope hiện có, thay đổi các luồng cấp/rút quyền hoặc mở quyền đọc DB trực tiếp cho client.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx` – Sprint 5 Backlog, dòng 5.13 | Task 5.13 là PB22, “Backend: list linked patients API”, trạng thái Not started. |
| Cùng workbook – Product Backlog, PB22 | User story: Family Member muốn theo dõi nhiều người thân; tiêu chí cấp PB gồm component chọn bệnh nhân và dữ liệu phải đúng theo bệnh nhân được chọn. Phần UI không nằm trong task 5.13. |
| Cùng workbook – Product Backlog, dòng 8–48; Sprint 5 Backlog, dòng 20–23 | Đã rà toàn bộ PB; đối chiếu các PB về mô hình/liên kết (PB09, PB15, PB19), quyền (PB02, PB16–PB18), theo dõi theo bệnh nhân (PB21, PB26–PB28, PB39) và cảnh báo PB20. Sprint 5 ánh xạ trực tiếp 5.13–5.16 vào PB22, phân chia backend danh sách, UI bộ chọn, ngữ cảnh dữ liệu và kiểm thử lộ chéo. |
| `docs/Team1_DTU/02_Requirements/Software Requirements Specification/DrugTime_SRS.docx` – FR1.10, BR-07–BR-09, BR-24 và UC.15 “Manage Multiple Linked Patients” | Family Member được quản lý nhiều Patient theo phạm vi từng bệnh nhân đã cho phép. UC.15 yêu cầu hiển thị các quan hệ Patient–Family Member khả dụng, khi chọn thì xác minh quan hệ còn hợp lệ và xác định phạm vi quyền tương ứng; thu hồi quyền phải khiến phạm vi đó không còn được phép. UC.15 đặt tiền điều kiện có ít nhất một quan hệ áp dụng, nhưng không đặc tả schema API, hành vi danh sách rỗng, consent cụ thể hay audit cho riêng thao tác liệt kê. |
| `api_contract/openapi.json` – `GET /family/caregivers`, `GET /patients/{patient_id}/schedules` | Đã có API cho bệnh nhân liệt kê người chăm sóc và API đọc dữ liệu theo `patient_id`; chưa tìm thấy API để người thân liệt kê bệnh nhân liên kết. |
| `backend/src/drugtime/modules/family/adapters/inbound/http.py` – route `/family/caregivers` | Backend đã có luồng liệt kê người chăm sóc theo chiều ngược lại; có thể tham khảo cấu trúc module, không mặc định tái dùng được chính sách quyền của route đó. |
| `backend/src/drugtime/modules/family/application/list_caregivers.py`; `adapters/outbound/sql_links.py` – `_LIST_CAREGIVERS` | Đã xác minh code: caller được dùng làm `patient_id`, SQL lọc `l.patient_user_id = :p AND l.status = 'active'`, trả thông tin `family_user_id` và trạng thái chia sẻ. Đây là danh sách ai đang theo dõi tôi; không phải danh sách tôi được theo dõi ai. |
| Frontend ref local `origin/main`: `mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart`, `data/repositories/remote_caregiver_repository.dart`, `presentation/screens/family_tab_screen.dart` | Đã có màn Hồ sơ → Người giám sát, gọi `GET /family/caregivers`, hiển thị tên, ngày chấp thuận, công tắc chia sẻ và gỡ liên kết. Tab Người thân chứa yêu cầu đang chờ, mã mời, chức năng nhập/quét mã và hộp thư cảnh báo. Code checkout hiện tại ở nhánh `feat/health-profile-UI` cũ hơn phần này, nên đã đọc thêm ref `origin/main` bằng `git show`/`git grep`; không fetch hay chuyển nhánh. |
| Frontend ref local `origin/main`: `mobile/lib/features/family_link/presentation/state/linked_patients_controller.dart` và kết quả tìm toàn bộ `mobile/lib` | Đã có model `LinkedPatient` và controller nhận `initialPatients`/`syncPatients` từ bên ngoài, xử lý gỡ patient khi thu hồi quyền. Chưa thấy nơi khởi tạo/sử dụng controller bên ngoài chính file này, chưa thấy repository gọi API lấy danh sách bệnh nhân. Đây là phần chuẩn bị state, chưa phải luồng API danh sách 5.13 hoàn chỉnh. Kết luận giới hạn ở checkout và các ref local đã đọc. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` – mục 8, QD-27–QD-30 và phần “Còn mở” | Người thân chỉ xem; chia sẻ cần liên kết hoạt động + bật chia sẻ + consent `family_sharing`; thu hồi có hiệu lực ngay; không lưu ngoại tuyến dữ liệu sức khỏe. Ma trận endpoint/mục đích cho người thân còn mở, không tự suy rộng ngoài quyết định. |
| `AGENTS.md` – bất biến 2, 4; vùng rủi ro “Phân quyền người thân” | Dữ liệu sức khỏe phải qua PEP, quyền đọc lại từ DB ở mỗi request; rút quyền có hiệu lực ở request tiếp theo; truy cập bị từ chối trả 403. |
| `.agents/skills/wf-health-endpoint/SKILL.md` | Cần dùng PEP hiện có, kiểm tra quan hệ/consent, access log fail-closed, dữ liệu tối thiểu và test cross-patient. |
| `backend/src/drugtime/modules/access/domain/rules.py`, `application/authorize.py`, `adapters/outbound/facts.py` | PEP hiện tại kiểm consent theo scope: thuốc, lịch sử tuân thủ, tương tác và hồ sơ dùng `health_data`; người thân cần thêm `family_sharing` và active sharing link. Chưa có scope riêng cho danh sách bệnh nhân. `authorize` ghi allowed cùng transaction và denied qua cơ chế riêng. Đây là hiện trạng kỹ thuật, không tự coi là quyết định nghiệp vụ mới cho API 5.13. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql` – enum `access_data_scope`, bảng `access_logs` | `data_scope` là enum chỉ có năm loại hồ sơ/thuốc/tuân thủ/tương tác/món ăn; thêm loại liệt kê bệnh nhân cần migration, không chỉ thêm giá trị trong Python. |
| `backend/supabase/migrations/20261015030157_family_link_consent.sql`, `20261021030401_family_link_audit_caregiver_operations.sql` | Audit liên kết có ràng buộc operation, subject và link; phải thiết kế cách ghi sự kiện danh sách rỗng/denied mức request mà không bịa patient hay link. Nếu mở rộng ràng buộc thì dùng migration mới và giữ append-only/grant tối thiểu. |
| `backend/supabase/migrations/20261013022744_access_logs_self_audit.sql`, `20261021115000_access_logs_admin_self_denied.sql`; `.agents/skills/wf-db-migration/SKILL.md` | Access log có revoke và trigger bảo vệ khỏi UPDATE/DELETE/TRUNCATE. Phần mở rộng không được vô hiệu các bảo vệ đó; cần kiểm migration từ DB sạch và trên dữ liệu cũ. |
| `work/5.13/02-contract.md` – bản draft phát hiện migration, chưa approved | Đã có bản đề xuất API/audit để review. Requirement được người dùng reopen ngày 2026-11-10 để bổ sung phạm vi schema và nâng size L; bản contract cần đối chiếu lại sau approval mới. |

### Quyết định nghiệp vụ áp dụng

Nguồn: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 8–9, bản đang có trong checkout. Giữ nguyên trạng thái của nguồn.

| Quyết định | Quy tắc áp dụng | Trạng thái nguồn | Tiêu chí |
|---|---|---|---|
| QD-27, mục 8 | Người thân chỉ xem, không được sửa dữ liệu hay xác nhận hộ. API chỉ cung cấp danh sách lựa chọn. | Đã chốt | AC1, AC8 |
| QD-28, mục 8 | Chia sẻ cần liên kết active, bật chia sẻ và `family_sharing`; kiểm lại ở mỗi request. | Đã chốt | AC1–AC3, AC7 |
| QD-29, mục 8, quy tắc kiểm quyền | Kiểm tra quyền tại DB mỗi request, không cache quyết định quyền; thu hồi có hiệu lực ngay. | Đã chốt | AC3, AC7 |
| QD-29, mục 8, quy tắc ngoại tuyến | Không lưu bền dữ liệu sức khỏe của người khác. Task chỉ cung cấp API; phần vòng đời state Mobile ngoài phạm vi. | Đã chốt | AC8 (response tối thiểu); không có AC lưu trữ Mobile trong task này |
| QD-30, mục 8 | Liên kết lại cần yêu cầu và xác nhận mới, không khôi phục chia sẻ cũ. | Đã chốt | AC7 |
| QD-32, mục 9 | Admin không có quyền vượt consent để xem dữ liệu y tế. | Đã chốt | AC4 |
| QD-33, mục 9 | Audit chỉ metadata tối thiểu, mô tả đúng hành động và subject; không ghi bền vững được thì chặn chia sẻ dữ liệu. | Đã chốt; cách phân loại/ghi audit mới là đề xuất trong requirement mở lại | AC5, AC6, AC10, AC11, AC14 |
| AGENTS bất biến 3; wf-db-migration | Access log chỉ ghi thêm, schema thay đổi bằng migration mới, giữ dữ liệu cũ và quyền tối thiểu. | Quy tắc bắt buộc của dự án | AC12, AC13 |
| HBR-18, mục 8, Còn mở | Ma trận endpoint/mục đích trong tài liệu nguồn vẫn mở. Riêng API 5.13, người dùng đã chọn ẩn patient khi thiếu `health_data` trong phiên 2026-11-10; không coi quyết định này là cập nhật toàn bộ HBR-18. | Nguồn còn mở; phạm vi 5.13 đã có quyết định của người dùng | AC1, AC3, AC9 |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Thêm API/use case, PEP/scope, audit và migration mở rộng enum/ràng buộc cần thiết; test tích hợp/schema nằm trong Backend. |
| `api_contract` | Có | API liệt kê bệnh nhân chưa có trong OpenAPI hiện hành; cần chốt endpoint và schema response. |
| `tests` | Không | Kiểm thử API với DB đặt trong `backend/tests/integration`, unit/architecture đặt trong Backend; chưa có nhu cầu sửa submodule E2E riêng. |
| `frontend` | Không | Task 5.13 là backend; UI chọn bệnh nhân thuộc phần khác của PB22. |
| `docs` | Không | Backlog là nguồn tham chiếu; task này không yêu cầu sửa tài liệu sản phẩm. |

## 5. Thay đổi API contract

- `contract_change`: yes
- Lý do: thêm thao tác API cho client lấy danh sách bệnh nhân đã liên kết; cần đặc tả endpoint, response, lỗi và bảo mật.
- Endpoint liên quan (thêm / sửa / xóa / chỉ dùng): dự kiến thêm endpoint danh sách bệnh nhân liên kết cho người thân. Path, method và schema cụ thể sẽ được chốt ở giai đoạn contract sau khi requirement được duyệt.

## 6. Vùng rủi ro và bất biến bị chạm

- **Dữ liệu sức khỏe / phân quyền người thân**: response chứa định danh và tên bệnh nhân, đủ để suy ra quan hệ chia sẻ; phải qua PEP theo đúng thứ tự, kiểm tra DB mỗi request, không tin patient ID từ client, không cache quyền.
- **Audit**: ghi log được phép trước khi trả dữ liệu; lỗi ghi log phải fail-closed. Lượt bị từ chối cần ghi `denied` ở transaction riêng theo cơ chế hiện có.
- **Schema**: cần migration mới cho scope audit danh sách; có thể cần mở rộng operation/ràng buộc audit mức request sau khi đối chiếu kho sẵn có ở plan. Không sửa migration đã áp dụng, không đổi/xóa nhật ký cũ, không mở quyền DB cho client. Kiểm reset DB sạch và khả năng giữ dữ liệu cũ sau nâng cấp.
- **Nhật ký chỉ ghi thêm**: giữ revoke và trigger chống UPDATE/DELETE/TRUNCATE trên access log và kho audit được dùng; không gỡ bảo vệ để hỗ trợ scope mới.
- **Thu hồi quyền**: consent bị rút, liên kết bị hủy hoặc chia sẻ bị tắt phải khiến bệnh nhân không còn xuất hiện trong request kế tiếp.
- **Tối thiểu dữ liệu**: không trả medication, schedule, dose, profile hay các thông tin không cần cho việc nhận diện/chọn bệnh nhân.
- **QD-29**: API không yêu cầu và không hàm ý lưu danh sách/dữ liệu bệnh nhân người thân vào bộ nhớ bền vững của client.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given tài khoản cá nhân có từ hai quan hệ đồng thời thỏa liên kết `active`, chia sẻ bật và cả consent `family_sharing`, `health_data` còn hiệu lực, When gọi API danh sách, Then nhận đúng các bệnh nhân đó, mỗi người một lần, với `patient_id` và tên hiển thị; không có dữ liệu thuốc/lịch/liều/hồ sơ. | integration |
| AC2 | Given người thân không có quan hệ nào đủ điều kiện, When gọi API danh sách, Then nhận danh sách rỗng theo schema, không tiết lộ bệnh nhân không được chia sẻ. | integration |
| AC3 | Given một quan hệ đang được liệt kê, When bệnh nhân tắt chia sẻ, rút consent `family_sharing` hoặc `health_data`, hoặc hủy liên kết rồi người thân gọi lại ngay với cùng token, Then bệnh nhân đó không còn trong kết quả request kế tiếp. | integration |
| AC4 | Given người gọi chưa xác thực hoặc là admin không có quyền người thân, When gọi API, Then nhận lỗi theo contract và không trả danh sách bệnh nhân. | integration |
| AC5 | Given có lỗi khi ghi access log cho request hợp lệ, When người thân gọi API, Then request thất bại và không trả dữ liệu bệnh nhân. | integration |
| AC6 | Given lỗi quyền hoặc truy cập không hợp lệ được xác định là lượt từ chối theo PEP, When API xử lý request, Then trả 403 theo contract, không làm lộ bệnh nhân ngoài quyền và có bản ghi `denied` bền vững theo cơ chế audit hiện có. | integration |
| AC7 | Given danh sách ứng viên trộn patient đủ quyền, patient của người thân khác, liên kết pending/rejected/revoked, active nhưng sharing tắt hoặc thiếu `family_sharing`, và liên kết lại chưa bật chia sẻ, When caller lấy danh sách, Then chỉ patient đủ quyền của chính caller xuất hiện; các mục bị lọc không khiến toàn bộ danh sách thất bại với 403. | integration |
| AC8 | Given hai patient được phép xem có cùng tên, When gọi API, Then cả hai xuất hiện với `patient_id` khác nhau và tên tương ứng; response không chứa email, điện thoại, ngày sinh, ảnh hoặc dữ liệu sức khỏe. Client có thể dùng ID kỹ thuật để phân biệt dù UI chỉ hiển thị tên. | integration |
| AC9 | Given liên kết active, sharing bật và `family_sharing` còn hiệu lực nhưng patient không có `health_data` hiện hành, When gọi API danh sách, Then patient đó bị loại khỏi kết quả; các patient khác đủ cả bốn điều kiện vẫn được trả bình thường. | integration |
| AC10 | Given request trả N bệnh nhân đủ quyền, When request thành công, Then có đúng N access log `allowed` cho request đó, mỗi patient một dòng với actor caller và scope `danh_sach_benh_nhan_lien_ket`; không ghi nhầm thành đọc thuốc/hồ sơ, không chứa tên hay nội dung y tế. Log bắt buộc bền vững trước response. | integration |
| AC11 | Given caller không có bệnh nhân đủ quyền hoặc admin gọi API, When xử lý request, Then danh sách rỗng vẫn là 200 với một sự kiện audit metadata mức request; admin là 403 với denied bền vững ở transaction riêng. Không tạo patient/link giả, không duyệt patient của admin để ghi log. Nếu audit bắt buộc không ghi được thì không trả thành công và lỗi theo contract. | integration |
| AC12 | Given DB local sạch, When chạy toàn bộ migration bằng `supabase db reset` ở giai đoạn được phép, Then schema dựng thành công, nhận scope audit mới và sự kiện request-level cần thiết; các scope/operation cũ tiếp tục hợp lệ. Given DB ngay trước migration mới có dữ liệu audit cũ đại diện, When áp dụng migration mới, Then nội dung và số dòng cũ được giữ nguyên, không cần sửa migration đã áp dụng. | integration |
| AC13 | Given schema sau migration, When API ghi audit hợp lệ thì ghi được; When thử UPDATE, DELETE hoặc TRUNCATE các bảng log/audit được dùng thì bị chặn theo revoke/trigger hiện có, kể cả role quyền cao bị trigger bảo vệ. Quyền anon/authenticated và worker không được mở rộng để phục vụ endpoint API. | integration |
| AC14 | Given request có nhiều bệnh nhân đủ quyền, When một lần ghi allowed bắt buộc thất bại giữa quá trình, Then request lỗi theo contract, không trả danh sách một phần và không commit một phần các allowed của request. Given một ứng viên bị bộ lọc loại, When các patient còn lại được trả, Then không tạo denied chỉ vì ứng viên bị lọc. | integration |

## 8. Câu hỏi mở

Không còn câu hỏi chặn. Các quyết định người dùng và giả định dưới đây là đầu vào để người duyệt xem xét requirement; agent không tự duyệt artifact.

Q1 [đã trả lời] Khi patient rút `health_data` nhưng vẫn còn liên kết active, sharing bật và `family_sharing`, có còn xuất hiện trong danh sách lựa chọn không?
- Ảnh hưởng: điều kiện lọc và AC9; quyết định ánh xạ mục đích consent cho API 5.13 ở HBR-18.
- Lựa chọn: loại khỏi danh sách vì không còn quyền xem thuốc/lịch sử / vẫn liệt kê danh tính quan hệ nhưng các endpoint dữ liệu sức khỏe tiếp tục từ chối.
- Quyết định người dùng ngày 2026-11-10: “Ẩn khi thiếu health_data (đề xuất)”.
- Áp dụng: loại khỏi danh sách khi thiếu một trong hai consent `health_data` và `family_sharing`, cùng điều kiện active + sharing bật. Đã cập nhật AC1, AC3, AC9.

### Các câu hỏi đã trao đổi và giả định đề xuất để duyệt

Q-ID [không chặn] Diễn giải “chỉ hiển thị tên” và khóa kỹ thuật của API
- Ảnh hưởng: response contract và khả năng client gọi các API dữ liệu tiếp theo cho đúng bệnh nhân. Tên có thể trùng, nên chỉ có tên không đủ định danh an toàn cho request sau.
- Lựa chọn: API trả `patient_id` và tên nhưng giao diện chỉ render tên / API response chỉ có tên và client phải có cách định danh khác.
- Giả định đề xuất để duyệt: chỉ hiển thị tên trên UI, nhưng API trả `patient_id` như khóa kỹ thuật không hiển thị cùng tên; không có field hiển thị nào khác. ID cần để gọi các API theo patient và phân biệt tên trùng; không coi đây là một field UI bổ sung.

Q2 [đã trả lời] Chính xác quan hệ nào được coi là “linked patient” có thể xem lúc này?
- Ảnh hưởng: bệnh nhân nào xuất hiện sau khi liên kết được tạo, bị tắt chia sẻ, rút consent, bị thu hồi hoặc đang chờ xử lý.
- Lựa chọn: chỉ `active` + sharing bật + consent `family_sharing` còn hiệu lực / mọi liên kết active dù chia sẻ tắt hoặc thiếu consent, có cờ trạng thái / bao gồm cả pending.
- Quyết định người dùng: chỉ hiện người mà caller được phép xem.
- Diễn giải áp dụng: chỉ trả bệnh nhân đủ ba điều kiện QD-28 và consent `health_data` theo Q1; pending, revoked, sharing tắt và thiếu consent đều không xuất hiện. Mỗi request đọc lại DB nên thay đổi có hiệu lực ngay.

Q3 [đã trả lời một phần] Thông tin nào cần thiết để phân biệt bệnh nhân trong bộ chọn?
- Ảnh hưởng: schema response và mức độ dữ liệu cá nhân được tiết lộ. Tên trùng có thể khiến UI khó phân biệt; thêm thông tin như ngày sinh/ảnh giúp nhận diện hơn nhưng tăng dữ liệu nhạy cảm.
- Lựa chọn: `patient_id` + tên / thêm một dấu hiệu tối thiểu do sản phẩm chọn (ví dụ ký tự đầu email hoặc nhãn do bệnh nhân đặt) / trả thêm ngày sinh hay ảnh.
- Quyết định người dùng: chỉ hiển thị tên, không hiển thị thông tin nào khác.
- Diễn giải đề xuất: API trả `patient_id` ẩn để client định danh khi gọi API tiếp theo (xem Q-ID), không thêm field hiển thị.
- Giả định mặc định: UI chỉ render tên; response chứa `patient_id` làm khóa kỹ thuật và tên. Không trả email, số điện thoại, ngày sinh, ảnh hay dữ liệu sức khỏe.

Q4 [không chặn] Danh sách cần thứ tự ổn định hay phân trang ngay từ đầu?
- Ảnh hưởng: contract, độ phức tạp phía client và xử lý khi có nhiều liên kết; thứ tự ổn định giúp người dùng tìm lại bệnh nhân quen thuộc.
- Lựa chọn: không phân trang, sắp theo tên / không phân trang, sắp theo thời điểm liên kết / phân trang bằng cursor với thứ tự xác định.
- Giả định mặc định: không phân trang vì backlog không nêu giới hạn hoặc nhu cầu lớn; sắp theo tên hiển thị, tie-break bằng ID. Nếu team có giới hạn số liên kết cụ thể thì cần xác nhận trước khi thiết kế contract.

Q5 [đã trả lời, gộp vào Q1] Consent `health_data` cho danh sách quan hệ
- Ảnh hưởng: consent mà backend phải kiểm trước khi đưa một Patient vào danh sách và phạm vi quyền SRS yêu cầu xác định sau khi chọn Patient. HBR-18 còn mở, SRS UC.15 chỉ nói phạm vi được Patient cho phép mà không ánh xạ consent theo endpoint.
- Lựa chọn: yêu cầu cả `health_data` và `family_sharing` / yêu cầu `family_sharing` cho danh sách quan hệ, còn `health_data` chỉ kiểm ở các endpoint trả dữ liệu sức khỏe.
- Quyết định trong phạm vi task: cần cả `health_data` và `family_sharing` theo câu trả lời Q1; không tự cập nhật trạng thái HBR-18 toàn hệ thống.
- Audit: dù consent nào được chọn, endpoint đọc `caregiver_links` phải đi qua PEP và access log fail-closed theo `wf-health-endpoint`; cần chốt ở contract cách ghi sự kiện cho một request trả nhiều Patient.

## 9. Giả định

- Task chỉ triển khai API backend trong PB22; UI chuyển bệnh nhân không thuộc 5.13.
- Quyết định đã chốt với người dùng: kết quả chỉ gồm quan hệ đủ điều kiện ở đúng thời điểm request: `active` + sharing bật + consent `family_sharing` và `health_data` hiện hành.
- Theo UC.15, khi người thân chọn một Patient, hệ thống còn phải xác minh quan hệ hiện hành và xác định phạm vi quyền của đúng Patient đó; việc endpoint liệt kê không tự cấp quyền truy cập dữ liệu sức khỏe.
- Giả định đề xuất để duyệt: giao diện chỉ hiển thị tên bệnh nhân; `patient_id` là khóa kỹ thuật, không hiển thị.
- Danh sách rỗng là thành công, không phải lỗi 404.

## 10. Phát sinh

- HBR-18 toàn hệ thống còn mở trong tài liệu nguồn; người dùng đã chốt hai consent cần có cho riêng 5.13. Bản requirement mở lại bổ sung scope audit và migration, size L. Contract/plan cần chốt cách lưu audit request-level theo các ràng buộc đang có; không gán log sai thành đọc thuốc/hồ sơ hoặc dùng patient giả. Không còn phát sinh schema ngoài phạm vi requirement này nếu chỉ mở rộng enum/operation/ràng buộc phục vụ audit mới và giữ nguyên bảo vệ nhật ký.
- Ma trận kiến trúc hiện cho access → family/consent/identity, không có family → access. Plan phải dùng PEP và giữ ranh giới này. Nếu cần quan hệ module mới hoặc sửa tài liệu C4/schema chính thức trong docs thì nêu phát sinh để duyệt trước; lần cập nhật này chưa mở rộng phạm vi docs.
- Baseline từ giai đoạn contract trước khi reopen: `api_contract/openapi.json` và `api_contract/README.md` đang có bản draft của chính task 5.13. Ba file Firebase untracked `frontend/mobile/android/app/google-services.json`, `frontend/mobile/firebase.json`, `frontend/mobile/lib/firebase_options.dart` đã có trước task. Scope toàn workspace có thể đánh dấu các file này ngoài giai đoạn requirement; không sửa/xóa chúng để làm scope pass. Lượt reopen này chỉ sửa artifact/evidence trong `work/5.13/`.

## 11. Size

- `size`: L
- Lý do: có migration mở rộng scope audit và có thể mở rộng ràng buộc audit mức request, theo tiêu chí size L trong wf-requirement. Phạm vi submodule vẫn là Backend và API contract; test schema/tích hợp nằm trong Backend. API mới là thay đổi cộng thêm, không phá vỡ API cũ.

## Bước tiếp theo

- Nhánh Backend: đã xác nhận bằng `git -C backend branch --show-current` trong phiên này là `feat/list-linked-patients`; không tạo/chuyển nhánh superproject.
- Đang chờ: người duyệt xem requirement đã bổ sung migration, audit request-level và AC10–AC14; không còn câu hỏi nghiệp vụ chặn.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve 5.13 requirement` trong terminal của họ. Sau approval mới, agent đối chiếu bản draft `02-contract.md` với requirement mới, cập nhật AC mapping và Bước tiếp theo rồi dừng để duyệt contract. Không bắt đầu plan/implement trong lượt requirement này.
- Kiểm tra phạm vi: `python .agents/scripts/scope.py 5.13 --stage requirement`; log lượt reopen lưu `work/5.13/evidence/requirement-reopen-scope.log`, cần ghi nhận rõ các file baseline ở mục Phát sinh. Log gate lưu `work/5.13/evidence/requirement-reopen-gate.log`. Không chạy test ứng dụng hoặc DB reset trong giai đoạn phân tích này; AC12–AC14 là yêu cầu kiểm thử cho các giai đoạn sau, chưa phải kết quả đã chạy.
- Kết quả lượt reopen: gate nhận size L, requirement draft và contract draft. Scope exit 1, báo năm file baseline đã liệt kê trong Phát sinh (hai file contract từ giai đoạn trước và ba file Firebase có sẵn); không tuyên bố scope toàn workspace đạt. Người duyệt cần xem/ghi nhận baseline này khi duyệt lại; lượt reopen không thay đổi năm file đó.
- Cập nhật lần cuối: 2026-11-10, Codex.
