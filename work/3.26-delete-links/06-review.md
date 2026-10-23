---
task: 3.26-delete-links
stage: review
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 14:39 +0700
content_hash: sha256:30230b2998330ff3
inputs:
  01-requirement.md: sha256:e9780e264d8de972
  03-plan.md: sha256:6cc904b55d5e24ed
  04-impl-notes.md: sha256:502e1520beba53c6
  05-test-report.md: sha256:a6678a32b2a61b61
---

# 3.26-delete-links · Review

## 1. Kết luận

**Đạt, kèm lưu ý** (Pass with remarks)

Không phát hiện lỗi thuộc mức **Critical** hoặc **High**. Toàn bộ 6 tiêu chí chấp nhận (AC1–AC6), bất biến kiến trúc và yêu cầu bảo mật phân quyền đều được kiểm chứng chặt chẽ với 47 unit tests và 29 integration tests trên PostgreSQL thật.

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| `backend` | `git -C C:\Users\Admin\orca\workspaces\DrugTime-backend\feat-3.26 diff 63b41a9...HEAD` |

**Các file thay đổi (11 files, +1255/-22 lines):**
- Domain: [`src/drugtime/modules/family/domain/link.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/domain/link.py)
- Application: [`src/drugtime/modules/family/application/manage_links.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/application/manage_links.py), [`ports.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/application/ports.py)
- Outbound SQL: [`src/drugtime/modules/family/adapters/outbound/sql_links.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/adapters/outbound/sql_links.py)
- Inbound HTTP: [`src/drugtime/modules/family/adapters/inbound/http.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/adapters/inbound/http.py)
- Module API: [`src/drugtime/modules/family/api.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/api.py)
- Tests:
  - [`tests/unit/test_family_link_rules.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/tests/unit/test_family_link_rules.py)
  - [`tests/unit/test_family_manage_links.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/tests/unit/test_family_manage_links.py)
  - [`tests/unit/test_family_delete_link.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/tests/unit/test_family_delete_link.py)
  - [`tests/unit/test_sql_family_links.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/tests/unit/test_sql_family_links.py)
  - [`tests/integration/test_sql_family_links.py`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/tests/integration/test_sql_family_links.py)

**Kết quả `scope.py --stage implement`:**
- Tất cả 11 file đều nằm trọn vẹn trong module `family` và thư mục test tương ứng của `backend`.
- Không chạm file ngoài phạm vi, không sửa `supabase/migrations/`, không chạm `scan_missed_doses.py` (QD-29).
- *Lưu ý quy trình:* Cột trong bảng "File sẽ thay đổi" của [`03-plan.md`](file:///e:/DrugTIme_main/work/3.26-delete-links/03-plan.md) đặt tiêu đề là `File` thay vì `Đường dẫn` nên script `scope.py` không tự động bóc tách được khi chạy CLI tự động.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| **Đúng yêu cầu** | **Đạt**. Đáp ứng toàn bộ AC1–AC6: Bệnh nhân thu hồi (204), người thân tự rời (204), người lạ/không tồn tại (403), link pending thu hồi được (204), idempotent giữ nguyên `revoked_at` ban đầu và ép `sharing_enabled=false`, link rejected trả 422 cho thành viên và 403 cho người lạ. |
| **Phạm vi** | **Đạt**. Chỉ sửa mã nguồn module `family` và các file test liên quan. |
| **Contract** | **Đạt**. Đường dẫn công khai `DELETE /links/{id}` (không prefix `/family`), responses 204, 401, 403, 422 đúng theo quyết định của Tech Lead. `GET /family/link-code` được giữ nguyên vẹn. |
| **Bất biến kiến trúc** | **Đạt**. Thỏa mãn Schema v11 `CHECK ((status = 'revoked') = (revoked_at IS NOT NULL))` bằng câu lệnh UPDATE đồng thời; tuân thủ PEP (Policy Enforcement Point); không làm lộ sự tồn tại của link (chống enumeration). |
| **Bảo mật** | **Đạt**. Không rò rỉ secret/key; câu lệnh SQL dùng `sqlalchemy.text` tham số hóa triệt để (chống SQLi); `_log.info` chỉ ghi metadata phân quyền (`link_id`, `caller_id`, trạng thái), không ghi thông tin nhạy cảm. |
| **Xử lý lỗi** | **Đạt**. Ánh xạ lỗi domain `FamilyLinkError` $\rightarrow$ 422, `Forbidden("khong_co_quyen")` $\rightarrow$ 403; không nuốt exception ngoài ý muốn. |
| **Hiệu năng** | **Đạt**. UPDATE theo Primary Key `id` kèm điều kiện `WHERE` tối ưu; tối ưu bỏ qua ghi DB khi link đã ở trạng thái `revoked` và `sharing_enabled=false`. |
| **Chất lượng test** | **Đạt**. Bộ test phủ 100% các ca biên, race condition, timing $\le 5$s (QA.02), và kiểm tra cô lập worker scan liều bỏ lỡ. 47/47 unit tests pass, 29/29 integration tests pass. |
| **Dễ đọc và nhất quán** | **Đạt**. Cấu trúc Hexagonal rõ ràng; lint Ruff đạt 0 lỗi (đã giải quyết triệt để F841 và E501). |
| **Đối chiếu 04/05 với log** | **Đạt**. Số liệu test khớp chính xác với [`implement-integration-tests.log`](file:///e:/DrugTIme_main/work/3.26-delete-links/evidence/implement-integration-tests.log) và [`testcase-xlsx.log`](file:///e:/DrugTIme_main/work/3.26-delete-links/evidence/testcase-xlsx.log). |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| **Low** | [`03-plan.md:17`](file:///e:/DrugTIme_main/work/3.26-delete-links/03-plan.md#L17) | Tiêu đề cột trong bảng "File sẽ thay đổi" là `File` thay vì `Đường dẫn` hoặc `Path`, làm `scope.py` không nhận diện được cột. | Giữ nguyên vì artifact đã approved; chú ý dùng đúng `Đường dẫn` ở các task sau. |
| **Low** | [`api.py:35`](file:///C:/Users/Admin/orca/workspaces/DrugTime-backend/feat-3.26/src/drugtime/modules/family/api.py#L35) | Chữ ký hàm façade `revoke_link(..., *, caller_id: UUID \| None = None)` có giá trị mặc định `None`. | Giữ trạng thái OPEN theo chỉ đạo Tech Lead; route HTTP luôn truyền `caller_id=user.id`. |
| **Low** | Submodule `api_contract` | Nhánh contract `feat/SCRUM-134-delete-link-contract` trên local chưa được merge vào nhánh chính của submodule `api_contract`. | Tạo PR cập nhật contract OpenAPI song song với PR backend. |

## 5. Mô tả PR

### PR 1: Submodule `api_contract`
- **Tiêu đề:** `feat(contract): add DELETE /links/{id} endpoint spec (SCRUM-134)`
- **Nhánh:** `feat/SCRUM-134-delete-link-contract` $\rightarrow$ `main`
- **Nội dung:** Bổ sung OpenAPI path `/links/{id}` (method DELETE), khai báo mã phản hồi 204, 401, 403, 422 (`invalid_link_transition`).

### PR 2: Submodule `backend`
- **Tiêu đề:** `fix(family): implement idempotent DELETE /links/{id} API (SCRUM-134)`
- **Nhánh:** `feat-3.26` $\rightarrow$ `main`
- **Mô tả:**
  - Chuyển `DELETE /links/{id}` sang module `family` Hexagonal.
  - Hỗ trợ cả Patient thu hồi và Family Member tự rời khỏi liên kết của mình.
  - Đảm bảo tính idempotent: thu hồi lần hai giữ nguyên `revoked_at` ban đầu qua `COALESCE` và ép `sharing_enabled=false`.
  - Link rejected: thành viên nhận 422, người lạ nhận 403.
  - Ngăn ngừa user enumeration (link không tồn tại trả 403).
  - Bổ sung 47 unit tests và 29 integration tests (đo lường QA.02 $< 5$s và cô lập worker).

### PR 3: Superproject `DrugTime`
- **Tiêu đề:** `chore(task): complete task 3.26 delete family link`
- **Nội dung:** Cập nhật con trỏ submodule `backend` và `api_contract`, commit thư mục artifact [`work/3.26-delete-links/`](file:///e:/DrugTIme_main/work/3.26-delete-links/).
- **Thứ tự merge:**
  1. Merge PR 1 (`api_contract`).
  2. Merge PR 2 (`backend`).
  3. Bump submodule pointers và merge PR 3 (superproject).

## 6. Ghi chú cho quy trình

- **Tiêu đề bảng trong Plan:** Cần lưu ý bảng "File sẽ thay đổi" phải dùng cột `Đường dẫn` (hoặc `Path`) để tương thích hoàn toàn với script tự động `scope.py`.
- **Cổng phê duyệt:** Quy trình duyệt tuần tự có kiểm tra phụ thuộc đầu vào (`inputs`), do đó khi một artifact đầu vào được sửa đổi, cần dùng `reopen` rồi `approve` lại từ đầu chuỗi để cập nhật hash hợp lệ.

## Bước tiếp theo

- Đang chờ: Người duyệt (Tech Lead / Developer).
- Việc cần làm:
  1. Người duyệt chạy lệnh duyệt giai đoạn review trong terminal:
     ```powershell
     python .agents/scripts/gate.py approve 3.26-delete-links review
     ```
  2. Mở PR trên repository `DrugTime-backend` và `DrugTime-api_contract` theo mô tả tại Mục 5.
  3. Commit thư mục `work/3.26-delete-links/` trên superproject.
- Cập nhật lần cuối: 2026-10-23 14:36, Antigravity
