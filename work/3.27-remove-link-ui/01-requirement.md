---
task: 3.27-remove-link-ui
title: Mobile: Giao diện gỡ liên kết người thân và thu hồi dữ liệu khi bị gỡ liên kết
type: feature
stage: requirement
size: M
contract_change: no
affected: [client]
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 15:22 +0700
content_hash: sha256:7b1b722a6068e75c
---

# 3.27-remove-link-ui · Mobile: Giao diện gỡ liên kết người thân và thu hồi dữ liệu khi bị gỡ liên kết

## 1. Mục tiêu

Cho phép người bệnh (Patient) chủ động xem danh sách và gỡ liên kết với người thân (Family Member) thông qua hộp thoại xác nhận rõ ràng về hậu quả thu hồi quyền truy cập. Đồng thời, bảo đảm ứng dụng phía người thân thu hồi, làm sạch tức thì dữ liệu sức khỏe và bộ nhớ cache cục bộ thuộc phạm vi người bệnh đã bị gỡ liên kết khi nhận HTTP 403 hoặc khi đồng bộ danh sách liên kết mới.

## 2. Phạm vi

### Trong phạm vi

1. **Patient — Màn hình quản lý người thân đã liên kết (`CaregiversScreen` / `AppRoutes.caregivers`):**
   - Hoàn thiện giao diện hiển thị danh sách người thân đã liên kết (họ tên nhận diện, ngày chấp thuận, trạng thái chia sẻ).
   - Nút hành động “Gỡ liên kết” cho từng mục người thân còn hiệu lực.
   - Trạng thái trống (empty state) khi không có người thân nào liên kết, kèm điều hướng mở tab Người thân.
   - Cơ chế kéo để làm mới (pull-to-refresh) tải danh sách mới nhất từ server.

2. **Patient — Hộp thoại xác nhận gỡ liên kết:**
   - Hộp thoại cảnh báo hiển thị trước khi gọi API với thông điệp rõ ràng: người thân sẽ mất quyền xem dữ liệu ngay lập tức.
   - Hai lựa chọn: **Hủy** (đóng hộp thoại, không gọi API, giữ nguyên dữ liệu) và **Gỡ liên kết** (tiến hành gọi API).
   - Khóa tương tác / chống gửi lặp (debouncing / busy lock) khi thao tác đang chạy.
   - Hiển thị trạng thái loading phù hợp trong quá trình xử lý.
   - Không xóa người thân khỏi UI trước khi API trả về kết quả thành công.
   - Khi API thành công: tự động đồng bộ lại danh sách từ server và thông báo thành công qua SnackBar.
   - Khi API thất bại: giữ nguyên trạng thái danh sách, hiển thị thông báo lỗi rõ ràng và cho phép người dùng thử lại.
   - Xử lý trường hợp liên kết đã bị thu hồi từ trước (204 idempotent / 404): đồng bộ lại danh sách mới nhất từ server.

3. **Tích hợp API gỡ liên kết (`RemoteCaregiverRepository`):**
   - Cập nhật phương thức `revoke(int linkId)` gọi đúng endpoint `DELETE /family/links/{id}` theo chuẩn contract đã duyệt (SCRUM-134, task 3.26), xử lý phản hồi `204 No Content`.
   - Ánh xạ mã lỗi HTTP (`401`, `403`, `404`, mạng) sang `CaregiverFailureKind` nhất quán.

4. **Family Member — Xử lý khi Patient bị gỡ liên kết:**
   - **Xử lý HTTP 403 Forbidden (`AdherenceFailureKind.denied` / `FamilyAlertFailure('forbidden')`):**
     - Khi request đọc dữ liệu người bệnh trả về 403 do liên kết bị thu hồi, xác định đúng `patientId` bị ảnh hưởng.
     - Xóa dữ liệu hiển thị trong state cục bộ (`history = null` trong `AdherenceController`, xóa alert liên quan trong `FamilyAlertController`).
     - Hiển thị màn hình thông báo mất quyền xem dữ liệu rõ ràng.
     - Xóa cache cục bộ thuộc phạm vi người bệnh đó trong `LocalMedicationStore` (`clearPatientData(String patientId)`).
     - Không xóa nhầm dữ liệu hoặc ảnh hưởng đến các người bệnh khác còn liên kết hợp lệ.
   - **Xử lý đồng bộ danh sách liên kết mới:**
     - Khi danh sách liên kết mới không còn chứa người bệnh cũ, xóa sạch state, danh sách hiển thị và cache cục bộ liên quan của người bệnh đó.
     - Giữ nguyên dữ liệu của các người bệnh vẫn còn liên kết hợp lệ.
   - **An toàn cache:**
     - Thao tác xóa cache theo `patientId` idempotent, an toàn khi cache đã bị xóa hoặc không tồn tại.
     - Xử lý đồng thời an toàn khi nhiều request cùng gặp 403.

5. **Kiểm thử tự động:**
   - Bộ unit test và widget test đầy đủ trên `frontend/mobile` cho cả luồng Patient (hiển thị, hủy, xác nhận, lỗi, busy lock, idempotent) và luồng Family Member (nhận 403, xóa cache theo patientId, bảo toàn patient khác, xử lý đồng thời).

### Ngoài phạm vi

- Sửa đổi backend API hoặc database schema (backend và OpenAPI contract cho `DELETE /family/links/{id}` đã hoàn thành trong task 3.26).
- Sửa đổi các luồng tạo liên kết, quét mã QR, duyệt yêu cầu liên kết (`features/family_link/presentation/screens/enter_link_code_screen.dart`, `scan_link_qr_screen.dart`).
- Triển khai tính năng chỉnh sửa thuốc hoặc can thiệp điều trị từ phía người thân (vi phạm QD-27: người thân chỉ đọc).

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` | `QD-29`: không lưu ngoại tuyến dữ liệu sức khỏe của người thân, chỉ giữ bộ nhớ phiên, xóa khi mất mạng/vào nền/đăng xuất/phát hiện thu hồi; khi thu hồi: vô hiệu cache. `QD-30`: hủy rồi liên kết lại phải tạo yêu cầu mới. |
| `api_contract/openapi.json` | Endpoint `DELETE /links/{id}` (operationId `revokeLink`), response `204 No Content`, errors `401`, `403` (`khong_co_quyen`). Idempotent: gọi lại khi đã revoked vẫn trả 204. |
| `backend/src/drugtime/modules/family/adapters/inbound/http.py` (nhánh `feat-3.26`) | Route `@router.delete("/links/{id}", status_code=204)` với prefix `/family`, gọi `manage_links.revoke_link`. |
| `frontend/mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart` | Màn hình `CaregiversScreen` quản lý người giám sát của Patient, đã có thẻ `_CaregiverCard`, hộp thoại xác nhận hủy liên kết và xử lý `_controller.revoke`. |
| `frontend/mobile/lib/features/family_link/data/repositories/remote_caregiver_repository.dart` | Phương thức `revoke(int linkId)` hiện đang gọi `_api.post('/family/links/$linkId/revoke')`, cần chuyển sang `_api.delete('/family/links/$linkId')` để khớp contract 3.26. |
| `frontend/mobile/lib/features/family_link/presentation/state/caregivers_controller.dart` | Quản lý state danh sách người giám sát, có `_busy` set ngăn spam request, tự động reload danh sách khi có thay đổi. |
| `frontend/mobile/lib/features/adherence/presentation/state/adherence_controller.dart` | Quản lý state xem lịch sử tuân thủ phía Family Member, đã ánh xạ 403 sang `AdherenceFailureKind.denied` và xóa `history = null`. |
| `frontend/mobile/lib/core/storage/local_db/local_medication_store.dart` | Quản lý SQLite lưu trữ lịch uống có cột `patient_user_id`; cần thêm phương thức `clearPatientData(String patientId)` để làm sạch cache khi thu hồi quyền. |

## 4. Quyết định nghiệp vụ áp dụng

| Mã | Nguồn & Quy tắc cụ thể | Trạng thái | AC tương ứng |
|---|---|---|---|
| QD-29 | `docs/.../drugtime_quyet_dinh_theo_chuc_nang.md` mục 8: Không lưu ngoại tuyến dữ liệu sức khỏe của người thân; chỉ giữ bộ nhớ phiên, xóa khi phát hiện thu hồi quyền. Vô hiệu hóa cache liên quan khi thu hồi. | ✅ Đã chốt | AC6, AC7, AC8, AC9 |
| QD-30 | `docs/.../drugtime_quyet_dinh_theo_chuc_nang.md` mục 8: Hủy liên kết làm mất quyền truy cập ngay lập tức; muốn liên kết lại phải tạo yêu cầu mới và xác nhận lại từ đầu. | ✅ Đã chốt | AC1, AC2, AC3 |
| CD2 | `AGENTS.md` Bất biến kiến trúc: Mọi endpoint chạm dữ liệu sức khỏe đi qua PEP, truy cập bị từ chối trả HTTP 403; rút quyền có hiệu lực ngay ở request kế tiếp. | ✅ Đã chốt | AC3, AC6 |
| CD4 | `AGENTS.md` Bất biến kiến trúc: Không cache quyết định phân quyền ở API hay client app. | ✅ Đã chốt | AC5, AC6 |

## 5. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Cập nhật UI/Dialog xác nhận gỡ liên kết trong `CaregiversScreen`, cập nhật endpoint trong `RemoteCaregiverRepository`, bổ sung hàm làm sạch cache theo `patientId` trong `LocalMedicationStore`, xử lý làm sạch dữ liệu trong state Family Member khi nhận 403, bổ sung unit/widget tests. |
| `backend` | Không | Nghiệp vụ `DELETE /family/links/{id}` đã được hiện thực và kiểm thử đầy đủ trong task 3.26 (`origin/feat-3.26`). |
| `api_contract` | Không | Contract `DELETE /links/{id}` (operationId `revokeLink`, 204 No Content) đã được phê duyệt trong task 3.26. |
| `tests` | Không | Test E2E cấp hệ thống không thay đổi; task này tập trung vào UI và local cache của mobile client. |
| `docs` | Không | Tài liệu capstone chính thức không bị sửa đổi. |

## 6. Thay đổi API contract

- `contract_change`: no
- Lý do: Tái sử dụng nguyên vẹn contract `DELETE /links/{id}` (prefix `/family`) đã được phê duyệt ở task 3.26. Không thêm mới hay thay đổi endpoint, payload hay mã trạng thái nào.
- Endpoint liên quan:
  - `DELETE /family/links/{id}` (chỉ dùng): Thu hồi liên kết người thân, trả về HTTP `204 No Content`.
  - `GET /family/caregivers` (chỉ dùng): Lấy danh sách người giám sát đang liên kết của Patient.

## 7. Vùng rủi ro và bất biến bị chạm

- **Phân quyền người thân (`caregiver_links`, consent, thu hồi quyền):** Rút quyền có hiệu lực ngay ở request kế tiếp. Phía Family Member không được tiếp tục hiển thị hoặc khôi phục dữ liệu từ cache cũ sau khi quyền bị thu hồi.
- **Dữ liệu sức khỏe:** Xóa hoặc vô hiệu hóa triệt để dữ liệu tuân thủ, lịch uống và cảnh báo thuộc về người bệnh đã bị gỡ liên kết trong bộ nhớ và cache SQLite cục bộ.

## 8. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | **Given** Patient mở màn hình Người giám sát (`AppRoutes.caregivers`), **When** danh sách tải thành công từ backend, **Then** hiển thị đúng thông tin nhận diện từng người thân (tên hoặc tên mặc định, ngày chấp thuận giờ VN, trạng thái chia sẻ) và mỗi người có nút "Gỡ liên kết". | `unit` (widget) |
| AC2 | **Given** Patient đang xem danh sách người thân và nhấn nút "Gỡ liên kết" của một người thân, **When** hộp thoại xác nhận hiển thị và Patient nhấn "Hủy", **Then** hộp thoại đóng lại, không có request API nào được gửi và danh sách người thân giữ nguyên. | `unit` (widget) |
| AC3 | **Given** Patient mở hộp thoại xác nhận gỡ liên kết với người thân `linkId = 1`, **When** Patient nhấn nút xác nhận "Gỡ liên kết", **Then** app gọi `DELETE /family/links/1`, khóa nút tương tác tránh spam request, nhận phản hồi 204 No Content, tự động tải lại danh sách mới từ server và hiển thị thông báo thành công `Đã gỡ liên kết với...`. | `unit` (widget & repository) |
| AC4 | **Given** Patient xác nhận gỡ liên kết nhưng API trả về lỗi mạng hoặc 5xx, **When** request hoàn tất với lỗi, **Then** người thân vẫn còn nguyên trong danh sách, hiển thị thông báo lỗi phù hợp và cho phép người dùng thử lại. | `unit` (widget) |
| AC5 | **Given** Patient xác nhận gỡ một liên kết nhưng backend phản hồi liên kết đã bị thu hồi trước đó (204 idempotent hoặc 404), **When** request hoàn tất, **Then** app tự động làm mới danh sách và người thân không còn xuất hiện trên màn hình. | `unit` (widget) |
| AC6 | **Given** Family Member đang mở màn hình xem lịch sử tuân thủ (`FamilyAdherenceScreen`) của một Patient đã bị gỡ liên kết, **When** gửi request và backend trả về HTTP 403 Forbidden (`AdherenceFailureKind.denied`), **Then** dữ liệu lịch sử tuân thủ bị xóa sạch khỏi RAM (`history = null`), UI chuyển sang hiển thị thông báo không còn quyền xem lịch sử và không thể tiếp tục xem dữ liệu của người bệnh này. | `unit` (widget & controller) |
| AC7 | **Given** Family Member có dữ liệu lịch uống được cache trong `LocalMedicationStore` cho Patient A và Patient B, **When** liên kết của Patient A bị thu hồi và hàm `clearPatientData(patientIdA)` được thực thi, **Then** toàn bộ bản ghi lịch uống của Patient A trong `schedulesTable` bị xóa sạch, trong khi bản ghi của Patient B được giữ nguyên vẹn. | `unit` |
| AC8 | **Given** Family Member có danh sách cảnh báo trong `FamilyAlertController` chứa cảnh báo của Patient A và Patient B, **When** liên kết của Patient A bị thu hồi và hàm loại bỏ cảnh báo theo `patientId` được gọi, **Then** toàn bộ cảnh báo có `patientId == A` bị loại bỏ khỏi danh sách hiển thị, trong khi cảnh báo của Patient B giữ nguyên. | `unit` |
| AC9 | **Given** nhiều request đồng thời cùng truy cập dữ liệu của một Patient đã bị thu hồi liên kết và đều nhận 403, **When** các tác vụ hoàn tất xử lý lỗi, **Then** ứng dụng không gặp ngoại lệ/crash, cache của Patient vẫn ở trạng thái đã được làm sạch an toàn và không phục hồi dữ liệu cũ. | `unit` |

## 9. Câu hỏi mở

Q1 [không chặn] Tiêu đề AppBar của màn hình Patient quản lý người thân đã liên kết:
- Ảnh hưởng: Nhất quán văn phong giữa menu Hồ sơ và tiêu đề màn hình.
- Lựa chọn:
  - A: Giữ tiêu đề AppBar là `Người giám sát` (khớp với menu "Người giám sát" hiện tại trong Hồ sơ và route `AppRoutes.caregivers`), các nút hành động và hộp thoại cập nhật thành "Gỡ liên kết".
  - B: Đổi tiêu đề AppBar thành `Người thân đã liên kết`.
- Giả định mặc định: Lựa chọn A (giữ tiêu đề AppBar `Người giám sát`, cập nhật nút hành động thành `Gỡ liên kết` và hộp thoại xác nhận theo đúng yêu cầu).

## 10. Giả định

- Backend endpoint `DELETE /family/links/{id}` từ task 3.26 hoạt động đúng chuẩn contract (204 No Content, idempotent, 403 khi không có quyền).
- Tầng client mobile sử dụng `CaregiversController` và `RemoteCaregiverRepository` là nơi duy nhất quản lý các thao tác liên kết người thân phía Patient.
- Family Member truy cập dữ liệu qua `FamilyAdherenceScreen` (`AdherenceController`) và `FamilyAlertInboxScreen` (`FamilyAlertController`), cả hai đều là các điểm tiếp nhận và xử lý lỗi 403 để thu hồi dữ liệu.

## 11. Phát sinh

- Không có.

## 12. Size

- `size`: M
- Lý do: Task thuộc submodule `frontend`, không thay đổi API contract, nhưng chạm vùng rủi ro phân quyền người thân và thu hồi dữ liệu sức khỏe (xóa cache cục bộ SQLite và state bộ nhớ khi gặp HTTP 403), do đó theo quy tắc bắt buộc xếp size M (không được xếp size S).

## Bước tiếp theo

- Đang chờ: Người duyệt xem xét và phê duyệt `01-requirement.md`.
- Việc cần làm: Người duyệt chạy lệnh duyệt trong terminal:
  ```bash
  python .agents/scripts/gate.py approve 3.27-remove-link-ui requirement
  ```
- Cập nhật lần cuối: 2026-10-23 15:20 +0700, Antigravity
