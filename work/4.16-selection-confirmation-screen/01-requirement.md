---
task: 4.16-selection-confirmation-screen
title: Mobile — Chọn, xác nhận thuốc và trạng thái không có kết quả
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-26 16:41 +0700
content_hash: sha256:68d21d09eefdb715
---

# 4.16 · Chọn, xác nhận thuốc và trạng thái không có kết quả

## 1. Mục tiêu

Người dùng xem danh sách thuốc ứng viên, chọn đúng thuốc và xác nhận rõ ràng trước khi tiếp tục nhập thông tin sử dụng thuốc. Cùng một màn hình phục vụ đầu vào từ OCR và tìm kiếm; khi không có kết quả, người dùng có đường chuyển sang tìm kiếm thủ công. Thực hiện và kiểm chứng trên mock trước, tích hợp nguồn thật sau khi task 4.13 và 4.15 hoàn thành.

## 2. Phạm vi

### Trong phạm vi

- Màn chọn/xác nhận dùng chung nhận danh sách ứng viên danh mục từ hai nguồn OCR và tìm kiếm; không phụ thuộc thuật toán sinh ứng viên.
- Hiển thị dữ liệu nhận diện sẵn có: tên thuốc, hoạt chất, hàm lượng, dạng bào chế và đơn vị nếu đầu vào có. Thiếu thông tin phải được thể hiện trung thực, không tự bổ sung hàm lượng hoặc quy đổi.
- Chọn một ứng viên, xem lại thông tin, đổi lựa chọn, xác nhận hoặc hủy/quay lại. Chạm vào ứng viên chưa được coi là xác nhận cuối cùng.
- Trạng thái không có kết quả cho cả hai nguồn, có thao tác rõ ràng để mở tìm kiếm thủ công. Nếu đã ở tìm kiếm thủ công thì quay về ô nhập để sửa từ khóa.
- Dữ liệu mock và đường mở demo/test cho cả hai nguồn, đủ kiểm chứng đường đi từ không có kết quả → tìm thủ công → chọn → xác nhận mà không cần 4.13/4.15.
- Trả lựa chọn đã xác nhận về nơi gọi, giữ đúng định danh và dữ liệu của cùng ứng viên; hủy không làm thay đổi dữ liệu form trước đó.
- Unit/widget test và kiểm tra giao diện trên mock; ghi rõ giới hạn nghiệm thu chưa tích hợp backend/OCR thật.

### Ngoài phạm vi

- OCR/camera, upload ảnh, xử lý văn bản OCR thật; fuzzy matching, scoring, ngưỡng confidence và top-N của 4.13.
- Search endpoint/autocomplete và tích hợp thật của 4.15. Không định nghĩa schema giả cho endpoint OCR chưa có trong contract.
- Tạo/sửa endpoint, API contract, migration, lịch uống hoặc bản ghi liều; không gọi thao tác lưu thuốc/lịch từ nút xác nhận lựa chọn.
- Tự tạo thuốc ngoài danh mục, gán thuốc gần giống để vượt chặn, lưu nháp bền vững hoặc gửi yêu cầu bổ sung danh mục. Nếu chưa tìm được thuốc thì chỉ cho tìm lại/hủy; không cho đi tiếp như đã chọn được thuốc.
- Khôi phục chức năng Admin duyệt thuốc OCR không khớp; khuyến nghị liều, quy đổi đơn vị hoặc kết luận an toàn thuốc.
- Thay toàn bộ luồng tìm danh mục đang chạy bằng mock; mock chỉ được dùng ở demo/test hoặc cơ chế preview hiện có, không tự thay nguồn dữ liệu production.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| Yêu cầu người dùng, 26/10/2026 | Mã 4.16; ưu tiên mock, dùng chung OCR/tìm kiếm, không có kết quả phải có đường sang tìm thủ công. |
| `AGENTS.md`; `.agents/skills/wf-next/SKILL.md`; `.agents/skills/wf-requirement/SKILL.md`; `.agents/skills/wf-git/SKILL.md` | Phải lập và duyệt yêu cầu trước code; chỉ ghi artifact task trong giai đoạn này; không commit/push khi chưa được yêu cầu. |
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx`, sheet `Sprint 4 Backlog`, hàng 20/22/23 | 4.13: fuzzy matching/scoring/confidence/top-N; 4.15: search endpoint/autocomplete; 4.16: Selection/confirmation screen + no-result state, PB31, 7 giờ theo cột ước lượng. Trạng thái trong workbook là Not started; không coi đó là trạng thái triển khai đã kiểm chứng. |
| Cùng workbook, sheet `Replan Log`, hàng 97/99/100 và 124/126/127 | Mã 4.13/4.15/4.16 xuất hiện với nội dung khác do lịch sử đánh lại số. Dùng sheet Sprint 4 và tên task trùng yêu cầu hiện tại để xác định phạm vi. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 2/3/14/16 | QD-39 yêu cầu kiểm tra thủ công, không tạo lịch với thuốc ngoài danh mục; QD-38 tách hàm lượng và lượng dùng; QD-45 xác định backlog/contract chuẩn. Chi tiết truy vết ở mục 3a. |
| `docs/Team1_DTU/02_Requirements/Software Requirements Specification/DrugTime_SRS.docx`, đoạn giới thiệu OCR và phần Admin đối soát OCR không khớp | SRS nêu xác nhận trước lưu; phần Admin duyệt OCR là nội dung cũ mâu thuẫn QD-39, không đưa vào task. Chỉ trích đọc nội dung liên quan, không coi toàn bộ SRS đã được rà soát. |
| `api_contract/openapi.json`, `GET /catalog/medications` | API danh mục hiện có nhận q và limit, trả items; items rỗng là không khớp. Có id/name/active_ingredient/strength_text/dosage_form; không có confidence trong response hiện tại. Danh mục không phải dữ liệu sức khỏe; không kiểm consent/access log ở endpoint này. |
| `frontend/mobile/lib/features/medication/domain/entities/medication.dart`, `DrugCatalogItem` | Có id, name, activeIngredient, strength, dosageForm, unit. Không cần suy diễn kiểu dữ liệu nguồn OCR tương lai. |
| `frontend/mobile/lib/features/medication/presentation/widgets/drug_catalog_sheet.dart` | Đang tìm với debounce 300ms, phân biệt đang tải/lỗi/rỗng, giữ thứ tự kết quả; chạm một dòng trả lựa chọn ngay; chưa có bước xác nhận dùng chung, no-result chỉ có hướng dẫn văn bản. |
| `frontend/mobile/lib/features/medication/presentation/screens/add_medication_screen.dart` | `_pickDrug` nhận mục danh mục vào form; form có liều/tần suất/giờ uống riêng. Xác nhận lựa chọn không thay thế kiểm tra thông tin sử dụng trước khi lưu lịch. |
| `frontend/mobile/lib/features/medication/data/repositories/in_memory_medication_repository.dart`; `frontend/mobile/lib/app/router.dart` | Có nguồn danh mục mẫu và hạ tầng route/preview; chưa thấy route OCR/chọn-xác nhận dùng chung trong router đã đọc. Có thể tận dụng khi lập plan, chưa chốt file thực hiện ở requirement. |
| `frontend/mobile/test/features/medication/drug_catalog_sheet_test.dart`; `work/3.05-medication-lookup-search-ui/01-requirement.md` | Đã có các test debounce, kết quả về muộn và nguồn trả lỗi; task 3.05 xác định tìm/chọn chỉ trong luồng nhập thuốc. Cần giữ hồi quy khi nối màn mới vào luồng hiện hữu. Chưa chạy Flutter test trong phiên này. |

### 3a. Quyết định nghiệp vụ áp dụng

Nguồn chính: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, tổng hợp từ hồ sơ quyết định bản 3.1, baseline `QD-2026-10-03-v1`. Ký hiệu ✅ nghĩa là đã chốt trong baseline, chưa xác nhận triển khai/chữ ký Mentor; không coi draft của task này là phê duyệt nghiệp vụ mới.

| Mã, mục, trạng thái nguồn | Quy tắc trong phạm vi | AC / ranh giới |
|---|---|---|
| QD-39, mục 3, kiểm tra kết quả, ✅ | Kết quả OCR và nhập tay đều cần người dùng kiểm tra. Bước này kiểm tra danh tính thuốc và dữ liệu sẵn có; liều/giờ vẫn phải kiểm tra tại form sử dụng thuốc trước tạo lịch. | AC1–AC4, AC9; không tuyên bố xác nhận lựa chọn là đã xác nhận toàn bộ lịch. |
| QD-39, mục 3, thuốc phải có trong danh mục, ✅ | Không gán thuốc gần giống để vượt chặn, không xác nhận thuốc không có trong danh sách đầu vào hợp lệ. | AC5–AC7; lưu nháp/yêu cầu bổ sung nằm ngoài task, không giả báo đã gửi yêu cầu. |
| QD-39, mục 3, vòng đời ảnh/văn bản OCR, ✅ | Không đưa ảnh/văn bản OCR thật vào fixture/log, không thêm lưu trữ dữ liệu OCR trong UI mock. | AC9; xóa/mã hóa dữ liệu OCR thật thuộc giai đoạn tích hợp tương ứng, chưa nghiệm thu ở task mock này. |
| QD-39, mục 3, bỏ Admin duyệt OCR không khớp, ✅ | Không tạo đường điều hướng tới Admin đối soát. | AC6. |
| QD-38, mục 2, hàm lượng/đơn vị, ✅ | Tách hàm lượng khỏi lượng dùng, không tự quy đổi hoặc suy ra thông tin chưa có. | AC2, AC8. Danh sách phép quy đổi còn mở trong nguồn không chặn task vì không thực hiện quy đổi. |
| QD-45, mục 14/16, ✅ | API chuẩn ở `api_contract/openapi.json`; không biến dữ liệu mock thành hợp đồng backend mới. | AC9; tích hợp thật phải đối chiếu contract sau 4.13/4.15. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Có | Màn dùng chung, mock/demo và test mobile. |
| backend | Không | Chưa tích hợp matching/search thật, không đổi nghiệp vụ lưu. |
| api_contract | Không | Không thay giao tiếp API trong phạm vi mock. |
| tests | Không | Kiểm thử Flutter nằm trong frontend; chưa thực hiện E2E xuyên service. |
| docs | Không đối với chức năng | Chỉ đọc tài liệu nguồn. Bộ Excel test case tổng sẽ xử lý theo wf-testcase ở cuối giai đoạn test, khai báo phạm vi tương ứng khi lập plan. |
| .agents | Không | Không thay quy trình. |

## 5. Thay đổi API contract

- `contract_change`: no.
- Task chỉ nhận/trả dữ liệu nội bộ UI trên mock, không thêm/sửa/xóa endpoint, request, response, mã lỗi hay xác thực.
- Endpoint tham chiếu cho tìm kiếm tương lai: `GET /catalog/medications?q=...&limit=...` (q tối đa 100 ký tự, limit mặc định 20/tối đa 50); không bắt buộc gọi endpoint này trong demo mock.
- Không tự đặt endpoint OCR, score, confidence hoặc quy tắc threshold. Trách nhiệm đó nằm ở 4.13/4.15 và contract được duyệt của các task tương ứng.
- `POST /medications` và lưu lịch giữ ngoài phạm vi màn xác nhận; nút xác nhận chỉ trả mục danh mục về bên gọi.

## 6. Vùng rủi ro và bất biến bị chạm

- Chọn nhầm định danh/hàm lượng ảnh hưởng luồng nhập thuốc: phải giữ đúng id gắn với thông tin hiển thị, không tự chọn hoặc xác nhận ứng viên thay người dùng.
- Không thay endpoint/service sức khỏe, PEP, consent, access log, đồng bộ liều hoặc tương tác thuốc. Không cần migration hay thay ranh giới module backend.
- Không dùng dữ liệu bệnh nhân/ảnh OCR thật trong mock hoặc evidence; không thêm nơi lưu dữ liệu sức khỏe.
- Client production chỉ gọi Backend API theo bất biến dự án; mock phải tách khỏi nguồn production. Không truy cập Supabase trực tiếp.

## 7. Tiêu chí chấp nhận

`unit` bao gồm Flutter widget/flow test với fake/mock, không có DB thật. Không dùng mức integration cho các flow chỉ chạy mock.

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given cùng một tập ứng viên danh mục từ mock OCR và mock tìm kiếm, When mở luồng chọn từ từng nguồn, Then đều dùng cùng màn chọn/xác nhận và cùng quy tắc chọn, đổi, xác nhận, hủy. | unit |
| AC2 | Given nhiều ứng viên có tên giống nhau nhưng id/hàm lượng khác, When hiển thị và chọn, Then giữ thứ tự đầu vào, thể hiện rõ dữ liệu nhận diện được cung cấp và giữ đúng id của dòng đã chọn; không tự tính lại điểm/xếp hạng. | unit |
| AC3 | Given danh sách mới mở, When chưa chọn hoặc mới chạm một ứng viên, Then không trả kết quả cuối/tạo thuốc; thao tác xác nhận chỉ khả dụng sau chọn và hiển thị rõ thuốc đang chọn để kiểm tra; When xác nhận, Then trả đúng một kết quả khớp thuốc đang chọn cho lần mở đó. | unit |
| AC4 | Given đã chọn A, When đổi sang B và xác nhận, Then chỉ trả B; Given đã chọn nhưng hủy hoặc dùng Back, Then không trả lựa chọn đã xác nhận và không thay thông tin form trước đó. | unit |
| AC5 | Given nguồn OCR trả danh sách rỗng, When màn mở, Then hiện thông báo không có kết quả và nút tìm kiếm thủ công, không có thuốc được chọn sẵn; When bấm nút, tìm trong mock rồi xác nhận, Then trả đúng kết quả tìm thủ công về luồng gọi ban đầu. | unit |
| AC6 | Given nguồn tìm kiếm trả danh sách rỗng, When người dùng yêu cầu tìm thủ công, Then đến ô nhập có thể sửa từ khóa và tìm lại; không tạo vòng lặp no-result vô ích, không tự tạo thuốc/đi tiếp lưu lịch hoặc điều hướng Admin. | unit |
| AC7 | Given danh sách rỗng hoặc dữ liệu ứng viên mới thay thế danh sách đang hiển thị, When có lựa chọn cũ không còn hợp lệ, Then không xác nhận được lựa chọn cũ; cần chọn lại một ứng viên trong danh sách hiện hành. | unit |
| AC8 | Given ứng viên thiếu hoạt chất/hàm lượng/dạng bào chế/đơn vị tùy chọn, When xem và xác nhận, Then không crash, không hiện `null`, không bịa dữ liệu, tự quy đổi hay trộn hàm lượng với lượng dùng; thông tin thiếu có cách thể hiện trung thực. | unit |
| AC9 | Given đường demo/test với fixture tổng hợp cho hai nguồn và rỗng, When chạy toàn bộ chọn/tìm lại/xác nhận/hủy, Then không cần mạng/backend/OCR thật, không gọi lưu thuốc/lịch, không lưu ảnh/văn bản OCR và không đổi nguồn production; form sử dụng thuốc vẫn sở hữu bước kiểm tra liều/giờ trước tạo lịch. | unit |
| AC10 | Given dữ liệu tên dài, danh sách dài và màn hình nhỏ, When chọn/xem lại/xác nhận hoặc mở bàn phím tìm thủ công, Then các hành động chính vẫn truy cập được và không tràn bố cục; lựa chọn hiện tại và nút có nhãn đọc được bằng accessibility. | unit |
| AC11 | Given bản mock trên thiết bị Android hoặc emulator, When đi hết hai luồng, thao tác Back và no-result → tìm thủ công, Then nút/khả năng cuộn/bàn phím hoạt động đúng và câu chữ tiếng Việt dễ phân biệt chọn với xác nhận. Cần kiểm tra thủ công vì cảm nhận kích thước chạm/bàn phím thiết bị không được chứng minh đầy đủ bằng widget test. | manual |

## 8. Câu hỏi mở

Không có câu hỏi chặn requirement. Hành vi nền tảng đã được yêu cầu người dùng, nguồn quyết định và code hiện tại xác định đủ cho bản mock. Cách bố trí bước xem lại trong cùng màn hoặc màn tiếp theo là quyết định UI ở plan, miễn đáp ứng AC3/AC4.

## 9. Giả định

- Mã task hiện hành là 4.16 theo yêu cầu và sheet Sprint 4; không tiếp tục thư mục `work/3.16-selection-confirmation-screen/` (chỉ có evidence, không có requirement) và không ghi đè task 3.16 consent.
- Một lần mở màn chọn xác nhận một thuốc, phù hợp `_pickDrug` hiện tại. OCR nhiều thuốc có thể gọi màn này cho từng lựa chọn sau, không triển khai chọn nhiều trong task này.
- Bên cung cấp ứng viên chịu trách nhiệm chỉ cung cấp mục danh mục được phép chọn; UI không tự xác minh danh mục với backend khi chạy mock và không hứa kiểm tra hiệu lực dữ liệu thật.
- Sau 4.13/4.15 sẽ có công việc tích hợp thật riêng hoặc mở lại phạm vi task qua gate; hoàn thành mock không đồng nghĩa hoàn thành tích hợp production.

## 10. Phát sinh

- Git status ban đầu báo thay đổi ở submodule backend/docs/frontend. Kiểm tra scope baseline không phát hiện file thay đổi ngoài work; không quy các con trỏ submodule này cho task 4.16, không sửa hoặc commit chúng. Trước implement vẫn phải kiểm tra lại trạng thái và nhánh từng submodule theo wf-git.
- Chưa chạy Flutter test trong giai đoạn phân tích. Không đưa ra kết luận app/mock đã hoạt động.
- Lệnh `python` mặc định trỏ WindowsApps không chạy được trong sandbox; đã dùng Python bundled bên dưới để chạy gate/scope. Không sửa cấu hình Python của máy.
- Chứng cứ gate: `evidence/requirement-gate.log`; baseline scope: `evidence/requirement-scope-baseline.log`; kết quả scope sau khi ghi artifact: `evidence/requirement-scope.log`.

## 11. Size

- `size`: M.
- Lý do: thay đổi màn hình/điều hướng dùng chung hai nguồn, quản lý trạng thái chọn–xác nhận–rỗng, mock và bộ widget/flow test; vượt ngưỡng khoảng 3 file/50 dòng của size S. Chỉ tác động chức năng frontend, không đổi contract hoặc schema.
- File triển khai và checklist chi tiết được lập ở giai đoạn plan sau khi requirement được duyệt.

## Bằng chứng kiểm tra

- Runtime thực tế: `C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8` thay cho `python` trong các lệnh dưới.
- `python .agents/scripts/gate.py 4.16-selection-confirmation-screen requirement`: cho phép bắt đầu requirement; xem `evidence/requirement-gate.log`.
- `python .agents/scripts/scope.py 4.16-selection-confirmation-screen --stage requirement`: baseline không có thay đổi ngoài work; kiểm tra lại sau ghi artifact tại `evidence/requirement-scope.log`.

## Bước tiếp theo

- Đang chờ: người duyệt requirement.
- Việc cần làm: đọc bản yêu cầu rồi tự chạy `python .agents/scripts/gate.py approve 4.16-selection-confirmation-screen requirement` trong terminal. Nếu `python` trên máy chưa sẵn có, dùng runtime bundled như mục bằng chứng.
- Sau khi đã duyệt, lượt tiếp theo dùng wf-next → wf-plan (size M, contract_change no). Chưa được viết code frontend ở giai đoạn này.
- Có thể commit `work/4.16-selection-confirmation-screen/` cùng evidence khi người dùng yêu cầu; chưa commit/push trong lượt này.
- Cập nhật lần cuối: 2026-10-26, Codex.
