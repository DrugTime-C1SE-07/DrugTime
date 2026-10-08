---
task: 2.13
title: Kiểm thử Admin Medication Catalog CRUD
type: feature
stage: requirement
size: S
contract_change: no
affected: [backend]
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-08 23:01 +0700
content_hash: sha256:b561a2927bdced32
---

# 2.13 · Kiểm thử Admin Medication Catalog CRUD

## 1. Mục tiêu

Xác minh các endpoint quản trị danh mục thuốc hiện có xử lý đúng CRUD, phân trang/tìm kiếm, xác thực và phân quyền admin, validation đầu vào, lỗi không tìm thấy và xóa mềm. Kết quả là bộ unit test ổn định, có thể chạy độc lập trong backend.

## 2. Phạm vi

### Trong phạm vi

- Kiểm thử năm endpoint hiện có: tạo, danh sách, chi tiết, cập nhật và xóa mềm thuốc tại `/admin/medications`.
- Kiểm thử người chưa đăng nhập bị từ chối `401` và người không phải admin bị từ chối `403` trên toàn bộ endpoint CRUD.
- Kiểm thử validation tên thuốc và cặp `source`/`source_ref`.
- Kiểm thử phân trang/tìm kiếm, phản hồi thành công và `404` khi thuốc không tồn tại hoặc đã bị xóa mềm.
- Sửa lỗi test hồi quy có sẵn trong `test_doses_batch_openapi_uses_contract_shape`: biến `paths` chưa được khởi tạo trước khi kiểm tra route medication.
- Chạy bộ test mục tiêu và bộ unit/architecture backend để phát hiện hồi quy.

### Ngoài phạm vi

- Thêm hoặc thay đổi endpoint, request/response, mã lỗi hay yêu cầu xác thực.
- Thay đổi schema/migration của bảng `medications`.
- Xây hoặc kiểm thử giao diện Admin Web.
- CRUD danh mục tương tác thuốc PB05.
- Kiểm thử tích hợp với PostgreSQL thật; task này chỉ xác minh lớp API/service bằng unit test với repository giả lập.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/DrugTime_Gantt_Dashboard.html` | PB04/05 là hạng mục Sprint 2 về Admin Web Dashboard cho Medication & Interaction Catalog CRUD. |
| `backend/src/drugtime/modules/catalog/adapters/inbound/http.py` | Có đủ năm endpoint Admin Medication CRUD, đều phụ thuộc `require_admin`; DELETE trả `204`. |
| `backend/src/drugtime/modules/catalog/adapters/inbound/schemas.py` | Tên thuốc bắt buộc; `source` và `source_ref` phải cùng có hoặc cùng rỗng; các giới hạn field đã được khai báo. |
| `backend/src/drugtime/modules/catalog/application/service.py` | Service chuyển tiếp CRUD tới repository và phát sinh `NotFound` cho get/update/delete không tìm thấy. |
| `backend/src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` | Danh sách chỉ lấy bản ghi chưa xóa, hỗ trợ `ILIKE`, phân trang; delete đặt `deleted_at`; create/update ánh xạ lỗi constraint. |
| `backend/tests/unit/test_catalog_crud.py` | Bộ test hiện có đã phủ auth, role, validation, các luồng CRUD thành công và một phần `404`, nhưng cần được chạy và đối chiếu tiêu chí. |
| `backend/tests/unit/test_app.py` | Toàn suite đang fail tại `test_doses_batch_openapi_uses_contract_shape` vì tham chiếu biến cục bộ `paths` chưa định nghĩa; test lân cận đã lấy `paths` từ OpenAPI runtime. |
| `api_contract/openapi.json` | Contract hiện chỉ có `/catalog/medications`; task kiểm thử này không được phép thay đổi contract. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql` | Bảng `medications` đã có `deleted_at`, unique `(source, source_ref)` và check hai field cùng null/cùng có. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Bổ sung unit test Catalog CRUD và sửa lỗi test OpenAPI làm toàn suite không thể pass. |
| `frontend` | Không | Không thay đổi hay kiểm thử UI trong task này. |
| `api_contract` | Không | Chỉ kiểm thử hành vi endpoint hiện có, không thay đổi hợp đồng. |
| `tests` | Không | Không thêm test E2E hoặc integration xuyên service. |
| `docs` | Không | Artifact task nằm ở superproject, không sửa tài liệu capstone. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: task chỉ kiểm thử hành vi endpoint đã tồn tại; không thêm/sửa/xóa đường dẫn, payload, response, mã trạng thái hay xác thực.
- Endpoint liên quan (chỉ dùng): `POST /admin/medications`, `GET /admin/medications`, `GET /admin/medications/{med_id}`, `PATCH /admin/medications/{med_id}`, `DELETE /admin/medications/{med_id}`.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng rủi ro của dự án: catalog thuốc không phải dữ liệu sức khỏe riêng của patient; không sửa schema, phân quyền người thân, ghi nhận liều, engine tương tác, ranh giới module hay bí mật.
- Phân quyền admin của endpoint vẫn phải được kiểm thử nhưng không thay đổi mô hình phân quyền.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given request không có danh tính, When gọi bất kỳ endpoint Admin Medication CRUD nào, Then API trả `401`. | unit |
| AC2 | Given user đã xác thực nhưng `is_admin=false`, When gọi bất kỳ endpoint Admin Medication CRUD nào, Then API trả `403` với `{"detail":"Admin only"}`. | unit |
| AC3 | Given admin và payload thuốc hợp lệ, When gọi `POST /admin/medications`, Then API trả `201` cùng dữ liệu thuốc đã tạo. | unit |
| AC4 | Given admin, When tạo thuốc với tên rỗng hoặc chỉ cung cấp một trong `source`/`source_ref`, Then API trả `422` và repository không được gọi ghi dữ liệu. | unit |
| AC5 | Given admin và repository có thuốc đang hoạt động, When gọi danh sách với `q`, `skip`, `limit`, Then API trả `200`, đúng `total`, items và chuyển đúng tham số tìm kiếm/phân trang xuống repository. | unit |
| AC6 | Given admin và thuốc đang hoạt động, When gọi GET chi tiết hoặc PATCH với payload hợp lệ, Then API trả `200` với đúng thuốc; khi không tìm thấy thì trả `404` với `Medication not found`. | unit |
| AC7 | Given admin và thuốc đang hoạt động, When gọi DELETE, Then API thực hiện xóa mềm và trả `204` không body; gọi cho thuốc không tồn tại/đã xóa trả `404`. | unit |
| AC8 | Given bộ test catalog CRUD hoàn tất và test OpenAPI đã khởi tạo `paths` từ schema runtime, When chạy test mục tiêu và toàn bộ `tests/unit tests/architecture`, Then tất cả test pass và không phát sinh hồi quy kiến trúc. | unit |

## 8. Câu hỏi mở

Không có. Yêu cầu “Test: catalog crud” được giới hạn ở unit test backend hiện có; kiểm thử DB thật và Admin Web được ghi rõ ngoài phạm vi.

## 9. Giả định

- “catalog crud” trong yêu cầu là Admin Medication Catalog CRUD của PB04 / Task 2.13, không bao gồm Interaction Catalog CRUD PB05.
- Endpoint và schema hiện có là đối tượng cần xác minh, không phải phạm vi thay đổi chức năng.
- Việc sửa `test_app.py` chỉ khởi tạo biến `paths` từ OpenAPI runtime đang được kiểm tra; không thay đổi code sản phẩm hoặc kỳ vọng contract.

## 10. Phát sinh

- `api_contract/openapi.json` chưa chứa các endpoint `/admin/medications` dù backend đã có. Đây là chênh lệch contract ngoài phạm vi task test-only; cần một task riêng nếu các endpoint này phải được client sử dụng chính thức.
- Lần implement đầu phát hiện toàn suite đạt 379/380; lỗi còn lại là `NameError: paths` tại `backend/tests/unit/test_app.py`. Người dùng đã reopen requirement để đưa file này vào phạm vi.
- `scope.py --stage requirement` báo `[NGOÀI]` cho `backend/tests/unit/test_catalog_crud.py` và file test case tổng trong `docs`; đây là thay đổi implement đã tồn tại trước khi requirement được reopen, đã được ghi trong `04-impl-notes.md`, không phải thay đổi phát sinh ở vòng sửa requirement này.

## 11. Size

- `size`: S
- Lý do: chỉ ảnh hưởng một submodule, không đổi contract hay chạm vùng rủi ro; phạm vi giới hạn ở hai file unit test và không quá khoảng 50 dòng bổ sung.

## 12. File sẽ thay đổi (chỉ task S)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `backend` | `backend/tests/unit/test_catalog_crud.py` | Sửa nếu cần | Bổ sung assertion/test còn thiếu để đáp ứng AC1–AC8. |
| `backend` | `backend/tests/unit/test_app.py` | Sửa | Khởi tạo `paths` từ OpenAPI runtime trước các assertion route để toàn suite có thể hoàn tất. |

## 13. Checklist (chỉ task S)

- [ ] P1 [backend] Chạy test mục tiêu để xác định khoảng trống/failure hiện tại — file: `backend/tests/unit/test_catalog_crud.py` — AC: AC1–AC7 — xong khi: có log red/baseline và đối chiếu từng AC.
- [ ] P2 [backend] Bổ sung tối thiểu các assertion/test còn thiếu — file: `backend/tests/unit/test_catalog_crud.py` — AC: AC1–AC7 — xong khi: test mục tiêu pass và chứng minh repository nhận đúng tham số/không bị gọi ở validation lỗi.
- [ ] P3 [backend] Sửa lỗi `NameError: paths` trong test OpenAPI — file: `backend/tests/unit/test_app.py` — AC: AC8 — xong khi: test mục tiêu `test_doses_batch_openapi_uses_contract_shape` pass và không thay đổi code sản phẩm.
- [ ] P4 [backend] Chạy toàn bộ unit và architecture test — file: `backend/tests/unit/test_catalog_crud.py`, `backend/tests/unit/test_app.py` — AC: AC8 — xong khi: có log bằng chứng và toàn bộ test pass.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: đọc artifact này và chạy `python .agents/scripts/gate.py approve 2.13 requirement`; sau đó yêu cầu agent tiếp tục task để thực hiện giai đoạn implement.
- Cập nhật lần cuối: 2026-10-08 23:04, Codex.
