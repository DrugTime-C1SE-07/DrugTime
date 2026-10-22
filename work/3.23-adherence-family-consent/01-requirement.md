---
task: 3.23-adherence-family-consent
title: Người thân xem lịch sử tuân thủ theo consent
type: feature
stage: requirement
size: M
contract_change: yes
affected: [backend, api_contract]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-21 09:22 +0700
content_hash: sha256:59d6784f453d27aa
---

# 3.23-adherence-family-consent · Người thân xem lịch sử tuân thủ theo consent

## 1. Mục tiêu

Người thân đã liên kết với bệnh nhân và được bệnh nhân cho phép xem lịch sử tuân thủ qua `GET /adherence?patient_id=...`. Quyền bị rút phải có hiệu lực ngay ở yêu cầu kế tiếp, không để lộ lịch sử hoặc trạng thái sức khỏe cho người không có quyền.

## 2. Phạm vi

### Trong phạm vi

- Xác nhận và hoàn thiện hành vi đọc lịch sử theo `patient_id` cho người thân: liên kết còn hoạt động, bật chia sẻ, consent `family_sharing` và `health_data` còn hiệu lực.
- Đối chiếu `patient_id` do client gửi với quyền của người gọi ở từng request; ghi access log cho lần được phép và bị từ chối, trả 403 khi thiếu quyền.
- Bảo toàn hành vi chính chủ đọc lịch sử; xác nhận response, mã lỗi và yêu cầu xác thực trong API contract dùng chung.
- Kiểm chứng các ca quyền, thu hồi quyền, fail-closed và không trả dữ liệu sức khỏe khi lỗi.

### Ngoài phạm vi

- Màn hình Mobile của người thân (task 3.24), bộ test riêng cho màn hình (task 3.25).
- Thay đổi thuật toán tính tỷ lệ tuân thủ, xác nhận liều, Worker quét bỏ lỡ, schema database hoặc cấp/thu hồi consent và liên kết.
- Endpoint hoặc cơ chế cache quyền mới.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx` · Sprint 3 Backlog dòng 30; Product Backlog PB21 | Task 3.23 yêu cầu `GET /adherence?patient_id=` theo consent còn hiệu lực; chặn sau khi rút consent. |
| `backend/src/drugtime/modules/adherence/adapters/inbound/history_http.py` | Route `GET /adherence` và tham số `patient_id` đã có; response dùng schema Pydantic, có `no-store`. |
| `backend/src/drugtime/modules/adherence/application/get_adherence_history.py` | Trình tự hiện tại: xác định patient, gọi access guard, rồi mới đọc dữ liệu. |
| `backend/src/drugtime/modules/adherence/adapters/outbound/other_modules.py`; `backend/src/drugtime/modules/access/{api.py,application/authorize.py,adapters/outbound/facts.py,domain/rules.py}` | PEP hiện có kiểm consent `health_data`, `family_sharing`, liên kết đang chia sẻ; audit allowed/denied, denied dùng transaction riêng. |
| `backend/src/drugtime/modules/adherence/adapters/outbound/sql_adherence.py`; `backend/src/drugtime/modules/adherence/adapters/inbound/history_schemas.py` | Truy vấn giới hạn theo patient; response có danh sách liều, nhóm và tổng hợp. |
| `backend/tests/integration/test_adherence_history_access.py`; `backend/tests/unit/test_adherence_history_http.py`; `backend/tests/architecture/test_health_route_enforcement.py` | Đã có mã test cho self/family, thiếu quyền, thu hồi, sửa `patient_id`, audit failure và đăng ký health route; chưa chạy test trong phiên này. |
| `api_contract/openapi.json`; `backend/scripts/export_openapi.py` | Contract viết tay hiện có 24 path nhưng chưa có `/adherence`; script export tạo bản generated riêng. |
| `AGENTS.md`; `.agents/skills/wf-health-endpoint/SKILL.md` | Endpoint dữ liệu sức khỏe bắt buộc đi qua PEP, không cache quyền, audit fail-closed và có test cross-patient. |

Kiểm tra phạm vi đã chạy: `python .agents/scripts/scope.py 3.23-adherence-family-consent --stage requirement` → OK; output thô: `work/3.23-adherence-family-consent/evidence/requirement-scope.log`.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Xác minh hành vi đang có và sửa sai lệch nếu test/contract chỉ ra; test liên quan nằm trong submodule này. |
| `api_contract` | Có | Bổ sung contract công khai cho `/adherence` đang thiếu. |
| `frontend` | Không | UI người thân là task 3.24. |
| `tests` | Không | Test tích hợp liên quan đã nằm trong `backend/tests/integration`; chưa thấy cần test E2E xuyên service cho task backend này. |
| `docs` | Không | Không sửa tài liệu capstone trong task này. |

## 5. Thay đổi API contract

- `contract_change`: **yes**.
- Lý do: endpoint đã có ở runtime backend nhưng chưa xuất hiện trong `api_contract/openapi.json`, là nguồn chuẩn cho client. Công bố path, query `patient_id`, response, xác thực và mã lỗi là thay đổi contract dạng bổ sung.
- Endpoint liên quan: bổ sung `GET /adherence` vào contract; dùng cùng endpoint hiện hữu trong backend, không tạo đường dẫn mới.

## 6. Vùng rủi ro và bất biến bị chạm

- **Dữ liệu sức khỏe**: lịch sử liều là dữ liệu sức khỏe; mọi lượt đọc phải qua PEP và audit trước khi trả dữ liệu.
- **Phân quyền người thân**: `patient_id` từ query không đáng tin; kiểm liên kết, công tắc chia sẻ và consent từ DB ở mỗi request; thu hồi có hiệu lực ở request kế tiếp.
- **Bí mật**: response và log lỗi không được lộ dữ liệu liều hoặc chi tiết nội bộ khi bị từ chối/lỗi.
- Không yêu cầu sửa schema, đường ghi liều hay ranh giới import giữa module theo phạm vi hiện biết.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given bệnh nhân có lịch sử liều và người thân có liên kết đang bật chia sẻ cùng consent `family_sharing` và `health_data` còn hiệu lực, when người thân gọi `GET /adherence?patient_id=<bệnh nhân>`, then trả 200, `patient_id` đúng, lịch sử/nhóm/tổng hợp của bệnh nhân và một dòng audit `allowed` cho scope `lich_su_tuan_thu`. | integration |
| AC2 | Given bệnh nhân tự gọi `GET /adherence` hoặc `patient_id` của mình và còn consent `health_data`, when request hoàn tất, then trả 200 theo hành vi hiện hữu và ghi audit `allowed`. | integration |
| AC3 | Given người gọi không có liên kết đang hoạt động hoặc công tắc chia sẻ tắt, when gọi endpoint với `patient_id` của bệnh nhân, then trả 403, không có dữ liệu lịch sử và ghi `denied`. | integration |
| AC4 | Given người thân có liên kết nhưng thiếu một trong hai consent `family_sharing` hoặc `health_data`, when gọi endpoint, then trả 403, không có dữ liệu lịch sử và ghi `denied`. | integration |
| AC5 | Given một request người thân đã được phép, when bệnh nhân rút consent, tắt chia sẻ hoặc hủy liên kết rồi người thân gửi request kế tiếp bằng cùng token, then request kế tiếp trả 403 và ghi `denied`. | integration |
| AC6 | Given người thân chỉ có quyền với bệnh nhân A, when đổi query `patient_id` sang bệnh nhân B, then trả 403, không đọc lịch sử B và ghi `denied` cho lần truy cập bị từ chối. | integration |
| AC7 | Given ghi audit `allowed` hoặc đọc quyết định quyền thất bại, when gọi endpoint, then request thất bại và không trả lịch sử; given truy cập bị từ chối, then dòng `denied` vẫn tồn tại sau rollback request. | integration |
| AC8 | Given thiếu/sai bearer token hoặc `patient_id` sai định dạng, when gọi endpoint, then nhận tương ứng 401 hoặc 422 và không đọc lịch sử. | unit |
| AC9 | Given client đọc `api_contract/openapi.json`, when tra `GET /adherence`, then thấy query, xác thực, response tối thiểu, mã lỗi và `Cache-Control: no-store` khớp endpoint runtime. | integration |

## 8. Câu hỏi mở

Không có câu hỏi chặn. Phạm vi dữ liệu người thân xem được theo mặc định là schema lịch sử hiện có; nếu Product Owner muốn chỉ số tổng hợp mà không có từng liều/tên thuốc, tiêu chí AC1 và contract phải đổi trước khi duyệt.

## 9. Giả định

- `health_data` là consent theo mục đích cho scope `lich_su_tuan_thu`, cùng `family_sharing`, liên kết còn hiệu lực và `sharing_enabled=true`, theo PEP hiện có.
- Người thân được xem schema lịch sử hiện có của bệnh nhân khi đủ quyền; task không thêm response riêng cho người thân.
- Code/test hiện diện chưa phải bằng chứng pass; giai đoạn sau phải chạy kiểm chứng thực tế trước khi kết luận hoàn thành.

## 10. Phát sinh

- Runtime backend đã có tính năng gần như đầy đủ dù Sprint 3 Backlog đánh dấu task chưa bắt đầu; cần tránh triển khai trùng.
- `api_contract/openapi.json` đang thiếu `/adherence`; đây là khoảng trống contract cần xử lý trong giai đoạn contract.

## 11. Size

- `size`: **M**.
- Lý do: chạm dữ liệu sức khỏe và phân quyền người thân nên không thể là S; phạm vi bổ sung contract và kiểm chứng backend ở hai submodule, không có migration hoặc thay đổi contract phá vỡ đã biết.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: rà soát phạm vi dữ liệu AC1 và contract; nếu đồng ý, chạy `python .agents/scripts/gate.py approve 3.23-adherence-family-consent requirement` trong terminal của người duyệt. Sau đó thực hiện giai đoạn contract theo gate trước khi lập `03-plan.md`.
- Cập nhật lần cuối: 2026-10-21, Codex.
