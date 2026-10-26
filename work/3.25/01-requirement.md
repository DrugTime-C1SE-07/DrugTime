---
task: 3.25
title: Kiểm thử lịch sử tuân thủ cho người thân
type: feature
stage: requirement
size: L
contract_change: no
affected: [backend, frontend, tests, docs]
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-23 15:11 +0700
content_hash: sha256:717a7d0a0b7c604b
---

# 3.25 · Kiểm thử lịch sử tuân thủ cho người thân

## 1. Mục tiêu

Kiểm chứng người thân chỉ xem được lịch sử tuân thủ của bệnh nhân đã liên kết và đang cho phép chia sẻ, thấy dữ liệu đúng theo quyết định nghiệp vụ, và mất quyền ngay khi bệnh nhân thu hồi. Để lại bộ kiểm thử và bằng chứng có thể chạy lại cho API và luồng Mobile của PB21.

## 2. Phạm vi

### Trong phạm vi

- Kiểm thử `GET /adherence` với vai trò người thân: dữ liệu, nhóm/ngày, khoảng thời gian, trạng thái liều, tỷ lệ, mã lỗi và nhật ký truy cập.
- Kiểm thử chéo bệnh nhân, hai consent, công tắc chia sẻ, hủy liên kết, mất quyền ở request kế tiếp và ghi log thất bại.
- Kiểm thử giao diện Mobile của người thân thuộc 3.24: chọn bệnh nhân, dữ liệu rỗng, lỗi quyền, xóa dữ liệu sức khỏe khỏi bộ nhớ phiên.
- Lập ánh xạ PB21 → ca kiểm thử → kết quả; tái sử dụng test đã có, chỉ bổ sung ca thiếu.
- Viết test case chi tiết cho PB21 trong `work/3.25/testcases.json`/`testcases.xlsx` và gộp đúng một sheet chức năng vào `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` theo `wf-testcase`.

### Ngoài phạm vi

- Xây/sửa API 3.23, giao diện 3.24 hoặc hợp đồng API trong task kiểm thử này.
- Sửa lịch, xác nhận liều hộ bệnh nhân, báo cáo quản trị và cảnh báo FCM.
- Sửa lỗi sản phẩm do test phát hiện; lập lỗi riêng kèm bằng chứng.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx`, `Product Backlog!B28:G28` | PB21: người thân xem lịch sử tuân thủ cơ bản của bệnh nhân đã liên kết; `GET /adherence?patient_id=`, chặn khi consent bị rút. |
| Cùng file, `Sprint 3 Backlog!B30:D32` | 3.23 là Backend API, 3.24 là Mobile view, 3.25 là test lịch sử tuân thủ. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, mục 5, 8, 9, 12, 14, 16 | Quy tắc trạng thái, chia sẻ, kiểm toán, tỷ lệ và contract. Nguồn ghi baseline `QD-2026-10-03-v1`; ✅ đã chốt trong baseline nhưng chưa xác nhận triển khai/chữ ký Mentor. |
| `api_contract/openapi.json` | Checkout hiện tại **chưa có** path `/adherence`; không thể coi code/test hiện tại là contract đã duyệt. |
| `backend/src/drugtime/modules/adherence/adapters/inbound/history_http.py`, `application/get_adherence_history.py`, `domain/history.py` | Backend có endpoint, kiểm quyền trước khi đọc, trả nhóm/tỷ lệ; `summarize()` hiện tính liều `da_uong`/`uong_tre` ngay sau xác nhận, phù hợp với ngoại lệ người dùng chốt ngày 23/10/2026. |
| `backend/tests/integration/test_adherence_history_api.py`, `test_adherence_history_access.py`, `backend/tests/unit/test_get_adherence_history.py` | Đã có test tính toán, biên thời gian, quyền, thu hồi, audit và fail-closed. Test tích hợp đọc schema `/adherence` từ contract đang thiếu. |
| `frontend/mobile/lib`, `frontend/mobile/test`, `tests/e2e` | Chưa thấy màn/test chuyên biệt cho lịch sử tuân thủ người thân; E2E hiện chủ yếu cho login/redeem. |
| `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`; `.agents/skills/wf-testcase/SKILL.md` | File test case tổng có sẵn nhưng chưa có sheet lịch sử tuân thủ; quy trình bắt buộc gộp sheet của task vào đây ở cuối giai đoạn test. |
| `docs/Team1_DTU/02_Requirements/User_Stories/User_Stories.xlsx` | File dài 0 byte, không đọc được; dùng PB21 trong backlog làm nguồn user story. |
| `AGENTS.md`, bất biến và kịch bản chất lượng | PEP, `access_logs` fail-closed, 403 khi từ chối, đọc quyền mỗi request và rút quyền tức thì. |

## 3a. Quyết định nghiệp vụ áp dụng

| Nguồn/mã, trạng thái | Quy tắc trong phạm vi | AC |
|---|---|---|
| Mục 8, QD-27 ✅, QD-28 ✅ | Người thân chỉ xem; cần liên kết `active`, bật chia sẻ, consent `family_sharing` và `health_data` còn hiệu lực tại mỗi request. | AC1, AC4, AC5 |
| Mục 8, QD-29 ✅ | Dữ liệu sức khỏe của người thân chỉ giữ trong bộ nhớ phiên; xóa khi mất mạng, vào nền, đăng xuất hoặc phát hiện thu hồi. | AC6 |
| Mục 9, QD-33 ✅; `AGENTS.md` bất biến 2–4 | Ghi metadata truy cập tối thiểu; từ chối có log riêng; lỗi ghi log chặn trả dữ liệu; không cache quyết định quyền. | AC1, AC4, AC5, AC7 |
| Mục 5, QD-03 ✅, QD-10 ✅ | `da_uong` tới +30 phút, `uong_tre` sau +30 tới +120 phút; xác nhận thực sự sau +120 phút không biến liều bỏ lỡ thành tuân thủ. | AC2, AC3 |
| Mục 12, QD-42 ✅ | Nguồn baseline quy định mẫu số là liều hợp lệ đã vượt cửa sổ 120 phút; không có mẫu số thì không có dữ liệu; tỷ lệ đúng giờ riêng; đối soát/xung đột có quy tắc riêng. Ngoại lệ với liều xác nhận sớm xem quyết định người dùng bên dưới. | AC3, AC8 |
| Người dùng chốt 23/10/2026, điều chỉnh QD-42 cho 3.25 | Áp dụng phương án A, nhưng liều đã xác nhận hợp lệ `da_uong`/`uong_tre` được đưa vào cả tử số và mẫu số **ngay sau xác nhận**, kể cả trước +120 phút. Liều chưa xác nhận vẫn đang chờ đến hết cửa sổ; xác nhận thực sự sau +120 phút tuân QD-10, không vào tử số. | AC3 |
| Mục 14 và 16, QD-45 ✅ | `api_contract/openapi.json` là contract chuẩn; QA truy vết PB–test và bằng chứng phiên bản. | AC9 |

BS-01 (mục 5, 🆕) mới được nhóm bổ sung ngày 04/10, chưa thuộc baseline: liều lưu trữ có ba mã; `cho_xac_nhan` trong response hiện là trạng thái suy diễn. Không thay schema liều trong task này.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Bổ sung/điều chỉnh test tích hợp API và PEP, không sửa production code. |
| `frontend` | Có | Bổ sung widget/controller test cho màn 3.24 và xóa dữ liệu phiên. |
| `tests` | Có | Bổ sung E2E Mobile–API khi môi trường và màn 3.24 sẵn sàng. |
| `api_contract` | Không | Dùng contract đã duyệt của 3.23; path đang thiếu là phụ thuộc của task sở hữu. |
| `docs` | Có | Chỉ sửa `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` để gộp sheet test case PB21 theo quy trình; không sửa tài liệu thiết kế/yêu cầu chính thức khác. |
| `.agents` | Không | Không thay quy trình hoặc script. |

## 5. Thay đổi API contract

- `contract_change`: **no**.
- Lý do: chỉ thêm kiểm thử theo hợp đồng đã duyệt, không thêm/sửa endpoint, field, status hoặc xác thực.
- Endpoint chỉ dùng: `GET /adherence?patient_id=...` với bearer app session. Cần có bản `/adherence` được duyệt trong `api_contract/openapi.json` từ 3.23 trước khi xác nhận kết quả kiểm thử contract. Nếu các phần còn thiếu của QD-42 đòi đổi response, ghi phụ thuộc cho task sở hữu và đánh giá lại phạm vi 3.25.

## 6. Vùng rủi ro và bất biến bị chạm

- **Dữ liệu sức khỏe, phân quyền người thân:** kiểm PEP `resolve_access → Consent Guard → Access Log Writer`, đối chiếu `patient_id`, 403 + `denied`, rút quyền tức thì, audit fail-closed và không lộ bệnh nhân khác.
- **Ghi nhận liều và đồng bộ:** lịch sử sau xác nhận trễ/Worker phải phản ánh một liều duy nhất, không ghi đè xác nhận.
- **Bí mật:** không ghi token vào artifact/log, không chép nội dung y tế vào audit.
- **Múi giờ:** biên thời gian theo `Asia/Ho_Chi_Minh`.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given bệnh nhân có lịch/liều và người thân có liên kết active, bật chia sẻ, hai consent hợp lệ; When gọi `GET /adherence` với đúng `patient_id`; Then nhận lịch sử của bệnh nhân đó theo contract và một log `allowed` chỉ chứa metadata tối thiểu. | integration |
| AC2 | Given liều đúng giờ, trễ, bỏ lỡ và còn chờ; When xem theo ngày/thuốc; Then mỗi liều xuất hiện một lần, trạng thái/giờ theo biên −30/+30/+120 phút và múi giờ VN, tổng cộng khớp dữ liệu nguồn. | integration |
| AC3 | Given một liều được xác nhận hợp lệ `da_uong`/`uong_tre` trước +120 phút, một liều chưa xác nhận trong cửa sổ, một liều quá +120 phút và ca không có liều đủ điều kiện; When xem lịch sử ngay sau mỗi mốc; Then liều đã xác nhận vào cả tử số và mẫu số ngay, liều chưa xác nhận còn chờ tới hết cửa sổ, liều quá hạn vào mẫu số, còn mẫu số bằng 0 thì tỷ lệ là không có dữ liệu. Xác nhận thực sự sau +120 phút theo QD-10 không vào tử số. Kiểm cả thời điểm đúng +120 phút và ngay sau đó. | unit + integration |
| AC4 | Given người thân không liên kết, thiếu một trong hai consent, tắt chia sẻ hoặc sửa `patient_id` sang bệnh nhân khác; When gọi endpoint; Then 403 theo contract, không có dữ liệu sức khỏe, có `denied` cho bệnh nhân tồn tại. | integration |
| AC5 | Given request trước đó thành công; When bệnh nhân rút consent, tắt chia sẻ hoặc hủy liên kết rồi người thân gọi lại với cùng token; Then request kế tiếp 403, có `denied`, không dùng quyền cache. | integration |
| AC6 | Given người thân đã mở màn lịch sử trên Mobile; When chọn bệnh nhân khác, mất mạng, đưa app vào nền, đăng xuất hoặc nhận 403; Then không hiển thị/lưu bền dữ liệu cũ và không cho sửa lịch/xác nhận liều hộ. | unit/widget + manual (vòng đời app thật) |
| AC7 | Given quyền hợp lệ nhưng đọc quyền/ghi `access_logs` thất bại, hoặc request bị từ chối và giao dịch nghiệp vụ rollback; When gọi endpoint; Then fail-closed không trả lịch sử; log `denied` đã ghi còn bền sau rollback. | integration |
| AC8 | Given liều hủy/xung đột hoặc được đối soát hợp lệ; When xem tỷ lệ và thời điểm cập nhật; Then áp dụng QD-42 (loại liều hủy, nhãn tạm thời, tính lại và có thời điểm/phiên bản cập nhật); nếu contract chưa biểu diễn được thì test/báo cáo chỉ rõ phần chưa nghiệm thu. | integration |
| AC9 | Given contract 3.23 và UI 3.24 có trong checkout; When chạy bộ test 3.25; Then có bảng truy vết PB21/QD → test → kết quả, lệnh/log bằng chứng, tách backend, Mobile, E2E và ca chưa chạy được; sheet PB21 được gộp vào file test case tổng, trạng thái Pass/Fail chỉ dựa trên log chạy thật, ca chưa chạy là Pending. | manual (đối chiếu artifact/log và workbook) |

## 8. Câu hỏi mở

Không có câu hỏi mở. Q1 đã được người dùng chốt ngày 23/10/2026: chọn A, với ngoại lệ tính liều đã xác nhận hợp lệ vào tỷ lệ ngay trước +120 phút như mục 3a và AC3. Đây là điều chỉnh của người dùng so với câu chữ QD-42 trong baseline; khi cập nhật tài liệu nghiệp vụ chính thức cần ghi rõ quyết định này.

## 9. Giả định

- 3.23 và 3.24 là tiền đề chạy đầy đủ 3.25; nếu chưa có bản đã duyệt, chỉ chuẩn bị test và ghi ca chưa thể chạy, không tuyên bố đạt.
- Tái sử dụng test backend hiện có; test mới nhắm lỗ hổng PB21/Mobile/QD-42.
- Không tạo Postman collection chỉ để lặp test PostgreSQL và PEP hiện có; `postman/collections/` hiện không có request phù hợp.
- Tập được tính `summary.adherence_rate` gồm liều xác nhận hợp lệ ngay khi xác nhận và liều chưa xác nhận đã qua +120 phút; liều chưa xác nhận còn trong cửa sổ là `pending`. Công thức của tỷ lệ đúng giờ riêng chưa được nêu cụ thể trong nguồn; test ghi rõ khoảng trống nếu contract 3.23 cũng chưa quy định.

## 10. Phát sinh

- Checkout có code/test `GET /adherence` trong `backend`, nhưng `api_contract/openapi.json` chưa có path; test tích hợp đọc schema path này nên chưa thể làm bằng chứng pass.
- Chưa thấy UI 3.24 trong `frontend/mobile/lib` hoặc test tương ứng; E2E Mobile phụ thuộc task đó.
- `User_Stories.xlsx` dài 0 byte; PB21 trong backlog là nguồn khả dụng.
- `domain/history.py` đã cộng liều xác nhận trước +120 phút, phù hợp quyết định người dùng mới; API hiện chưa có tỷ lệ đúng giờ riêng, nhãn xung đột hoặc thời điểm/phiên bản đối soát để nghiệm thu đầy đủ QD-42.
- `.gitignore` hiện bỏ qua toàn bộ `work/`; khi được yêu cầu commit artifact cần thêm có chủ đích bằng `git add -f`, không tự commit trong giai đoạn này.
- Hai thay đổi ngoài phạm vi trong `tests/e2e/mobile_redeem/README.md` và `run_e2e.py` đã được người dùng xử lý. Kiểm tra lại cho thấy submodule `tests` sạch và scope 3.25 đạt; agent 3.25 không sửa hai file này.
- Người duyệt đã mở lại requirement để bổ sung duy nhất file test case tổng thuộc `docs`; bản `03-plan.md` đang draft sẽ được cập nhật và rà lại sau khi `01` được duyệt lại.

## 11. Size

- `size`: **L**.
- Lý do: bốn submodule gồm file test case tổng, chạm dữ liệu sức khỏe/quyền người thân/ghi nhận liều và phụ thuộc contract cùng giao diện; không đủ điều kiện S.
- Kiểm tra phạm vi gần nhất: `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 3.25 --stage requirement` → **OK**; log thô: `work/3.25/evidence/requirement-scope.log`.

## Bước tiếp theo

- Đang chờ: người duyệt requirement vừa mở lại. Contract 3.23 và UI 3.24 là tiền đề chạy test đầy đủ ở giai đoạn sau.
- Việc cần làm: người duyệt xác nhận phạm vi `docs` chỉ gồm file test case tổng và chạy `python .agents/scripts/gate.py approve 3.25 requirement`. Sau đó agent rà và cập nhật `03-plan.md`; không bắt đầu implement trong lượt này.
- Cập nhật lần cuối: 2026-10-23, Codex.
