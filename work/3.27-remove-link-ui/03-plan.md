---
task: 3.27-remove-link-ui
stage: plan
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 15:34 +0700
content_hash: sha256:023a89daa93d8110
inputs:
  01-requirement.md: sha256:7b1b722a6068e75c
---

# 3.27-remove-link-ui · Plan

## 1. Giải pháp

1. **Phía Patient — Quản lý và gỡ liên kết:**
   - **Tích hợp API (`RemoteCaregiverRepository`):** Chuyển phương thức `revoke(int linkId)` sang gọi `_api.delete('/family/links/$linkId')` (HTTP DELETE), khớp với hợp đồng OpenAPI `DELETE /links/{id}` (prefix `/family`) đã được phê duyệt ở task 3.26. Xử lý phản hồi `204 No Content` không có body, cũng như xử lý tính idempotent khi liên kết đã ở trạng thái thu hồi.
   - **Định tuyến & URL Prefix:** `AppConfig.apiBaseUrl` trỏ tới gốc Backend API (không có sub-path), trong khi backend FastAPI mount router với `prefix="/family"`. Do đó, đường dẫn `/family/links/$linkId` truyền vào `ApiClient` được phân giải chính xác thành `${apiBaseUrl}/family/links/$linkId`, tuyệt đối không bị lặp hay sai prefix.
   - **Giao diện (`CaregiversScreen`):**
     - Đổi nhãn nút từ "Hủy liên kết" sang "Gỡ liên kết" (giữ Key `revoke-${caregiver.linkId}`).
     - Cập nhật hộp thoại xác nhận: Tiêu đề `Gỡ liên kết với người thân?` (hoặc `Gỡ liên kết với $name?`), nội dung nêu rõ hậu quả: `Người thân này sẽ mất quyền xem thông tin của bạn ngay sau khi liên kết bị gỡ. Bạn có chắc chắn muốn tiếp tục?`.
     - Hai nút: `Hủy` (Key `revoke-cancel`) đóng hộp thoại không gọi API, và `Gỡ liên kết` (Key `revoke-confirm`) tiến hành gọi API.
     - Hiển thị loading indicator trên nút hoặc trạng thái thẻ khi `isBusy` để phản hồi trực quan cho người dùng, đồng thời khóa tương tác ngăn gửi nhiều request trùng lặp.
     - Hiển thị thông báo thành công `Đã gỡ liên kết với $name.` qua SnackBar khi thành công và reload lại danh sách từ server.

2. **Phía Family Member — Xử lý thu hồi quyền và dọn dẹp cache:**
   - **Xác minh luồng 403 có căn cứ:** Việc thu hồi dữ liệu và dọn dẹp cache cục bộ CHỈ được thực hiện khi request truy cập dữ liệu sức khỏe của một bệnh nhân cụ thể (`patientId` xác định rõ ràng, ví dụ `/adherence?patient_id=...`) nhận về HTTP `403 Forbidden` (`AdherenceFailureKind.denied` / `FamilyAlertFailure('forbidden')`). Không xóa nhầm dữ liệu của bệnh nhân khác hoặc khi gặp các lỗi phân quyền chung không gắn với `patientId`.
   - **Lưu trữ cục bộ (`LocalMedicationStore`):** Bổ sung phương thức `Future<void> clearPatientData(String patientId)` trong `LocalMedicationStore` với mặc định rỗng (`async {}`) để không phá vỡ các fake store trong các test hiện hữu (`_FakeStore`, `_FakeLocalMedicationStore`). `SqliteLocalMedicationStore` hiện thực ghi đè: xóa toàn bộ bản ghi thuốc/lịch uống thuộc `patient_user_id` trong `schedulesTable` bên trong một database transaction, bảo đảm tính nguyên tử và không rò rỉ dữ liệu sức khỏe cục bộ của người bệnh đã bị gỡ liên kết (tuân thủ `QD-29`).
   - **Cảnh báo người thân (`FamilyAlertController`):** Bổ sung phương thức `removePatient(String patientId)` để loại bỏ ngay lập tức các cảnh báo thuộc về người bệnh bị gỡ liên kết ra khỏi danh sách hiển thị và reset chi tiết cảnh báo nếu đang mở.
   - **Điều phối danh sách bệnh nhân (`LinkedPatientsController`):**
     - Cung cấp controller quản lý danh sách bệnh nhân hợp lệ của Family Member:
       - Tình huống A (Gặp 403): Hàm `handleRevocation(String patientId)` loại bỏ bệnh nhân khỏi danh sách liên kết hoạt động, tự động dọn sạch cache lịch uống SQLite và cảnh báo liên quan.
       - Tình huống B (Đồng bộ mới): Hàm `syncPatients(List<String> newActivePatientIds)` so sánh danh sách mới với hiện tại, tự động dọn sạch dữ liệu của các bệnh nhân không còn trong danh sách mới trong khi giữ nguyên dữ liệu của các bệnh nhân hợp lệ.
   - **Màn hình tuân thủ (`AdherenceController`):** Kết nối hook `onPatientRevoked` khi nhận `AdherenceFailureKind.denied` (HTTP 403), bảo đảm xóa RAM (`history = null`) và kích hoạt dọn dẹp cache / alert.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `docs/.../drugtime_quyet_dinh_theo_chuc_nang.md` | `QD-29`: không lưu ngoại tuyến dữ liệu sức khỏe người thân, xóa khi phát hiện thu hồi. `QD-30`: hủy liên kết phải xác nhận lại từ đầu. |
| `backend/.../adapters/inbound/http.py` | Route `DELETE /family/links/{id}` trả về 204 No Content, idempotent, 403 khi caller không thuộc link. |
| `frontend/mobile/lib/core/api/api_client.dart` | Đã có sẵn phương thức `delete(String path)` gửi HTTP DELETE và trả `null` khi nhận 204. `baseUrl.resolve(path)` nối path chính xác. |
| `frontend/mobile/lib/core/config/app_config.dart` | `apiBaseUrl` là chuỗi host API gốc; các repository đều dùng leading slash `/family/...`. |
| `frontend/mobile/lib/features/family_link/data/repositories/remote_caregiver_repository.dart` | Phương thức `revoke` đang gọi `_api.post(...)`, cần đổi thành `_api.delete(...)`. |
| `frontend/mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart` | Đã có `_CaregiverCard`, hộp thoại xác nhận hủy và xử lý `_controller.revoke`. Cần cập nhật nhãn, câu chữ, loading spinner. |
| `frontend/mobile/lib/core/storage/local_db/local_medication_store.dart` | Quản lý bảng `schedulesTable` theo `patient_user_id`; có 4 fake store trong các file test khác kế thừa interface này nên cần default implementation. |
| `frontend/mobile/lib/features/family/presentation/state/family_alert_controller.dart` | `FamilyAlert` có `patientId`; controller cần thêm hàm `removePatient(String patientId)`. |
| `frontend/mobile/lib/features/adherence/presentation/state/adherence_controller.dart` | Đã xử lý 403 thành `AdherenceFailureKind.denied` và xóa `history = null`; cần thêm hook thông báo thu hồi. |

## 3. Quyết định nghiệp vụ áp dụng

| Mã | Nguồn & Quy tắc cụ thể | Trạng thái | AC | Bước | Test |
|---|---|---|---|---|---|
| QD-29 | `docs/.../drugtime_quyet_dinh_theo_chuc_nang.md` mục 8: Không lưu ngoại tuyến dữ liệu sức khỏe của người thân; xóa khi phát hiện thu hồi. Vô hiệu hóa cache liên quan khi thu hồi. | ✅ Đã chốt | AC6, AC7, AC8, AC9 | P3, P4, P5, P6 | `local_medication_store_test.dart`, `linked_patients_controller_test.dart`, `adherence_controller_test.dart` |
| QD-30 | `docs/.../drugtime_quyet_dinh_theo_chuc_nang.md` mục 8: Hủy liên kết làm mất quyền truy cập ngay lập tức; muốn liên kết lại phải tạo yêu cầu mới và xác nhận lại từ đầu. | ✅ Đã chốt | AC1, AC2, AC3 | P1, P2 | `remote_caregiver_repository_test.dart`, `caregivers_screen_test.dart` |
| CD2 | `AGENTS.md` Bất biến kiến trúc: Mọi endpoint chạm dữ liệu sức khỏe đi qua PEP, truy cập bị từ chối trả HTTP 403; rút quyền có hiệu lực ngay ở request kế tiếp. | ✅ Đã chốt | AC3, AC6 | P1, P6 | `remote_caregiver_repository_test.dart`, `adherence_controller_test.dart` |
| CD4 | `AGENTS.md` Bất biến kiến trúc: Không cache quyết định phân quyền ở API hay client app. | ✅ Đã chốt | AC5, AC6 | P2, P6 | `caregivers_screen_test.dart`, `adherence_controller_test.dart` |

## 4. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule frontend; được dùng glob. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `frontend` | `mobile/lib/features/family_link/data/repositories/remote_caregiver_repository.dart` | Sửa | Chuyển `revoke(int linkId)` sang gọi `_api.delete('/family/links/$linkId')` (HTTP DELETE 204) |
| `frontend` | `mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart` | Sửa | Cập nhật nhãn nút "Gỡ liên kết", nội dung hộp thoại xác nhận, loading spinner và thông báo SnackBar |
| `frontend` | `mobile/lib/core/storage/local_db/local_medication_store.dart` | Sửa | Bổ sung phương thức `clearPatientData(String patientId)` trong interface (kèm default impl) và `SqliteLocalMedicationStore` |
| `frontend` | `mobile/lib/features/family/presentation/state/family_alert_controller.dart` | Sửa | Bổ sung phương thức `removePatient(String patientId)` để lọc bỏ cảnh báo của bệnh nhân bị gỡ khỏi danh sách |
| `frontend` | `mobile/lib/features/family_link/presentation/state/linked_patients_controller.dart` | Thêm | Controller quản lý danh sách patient hợp lệ của Family Member, điều phối xử lý 403 và đồng bộ mới |
| `frontend` | `mobile/lib/features/adherence/presentation/state/adherence_controller.dart` | Sửa | Bổ sung hook `onPatientRevoked` dọn dẹp cache khi nhận 403 denied |
| `frontend` | `mobile/test/features/family_link/remote_caregiver_repository_test.dart` | Sửa | Unit test xác nhận `revoke` gọi HTTP DELETE `/family/links/{id}` và xử lý 204 thành công |
| `frontend` | `mobile/test/features/family_link/caregivers_screen_test.dart` | Sửa | Widget test cho nút "Gỡ liên kết", dialog xác nhận, loading spinner, thông báo và tự reload khi có lỗi |
| `frontend` | `mobile/test/core/storage/local_medication_store_test.dart` | Thêm | Unit test cho `clearPatientData` xóa schedules của đúng patientId mà không ảnh hưởng patient khác |
| `frontend` | `mobile/test/features/family_link/linked_patients_controller_test.dart` | Thêm | Unit test cho `LinkedPatientsController` (xử lý 403 revocation, đồng bộ danh sách mới, an toàn đa luồng) |
| `frontend` | `mobile/test/features/adherence/adherence_controller_test.dart` | Sửa | Unit test xác nhận 403 denied kích hoạt hook dọn dẹp cache và xóa RAM |

## 5. Checklist

- [ ] P1 [`frontend`] Cập nhật `RemoteCaregiverRepository.revoke` gọi `_api.delete('/family/links/$linkId')` — file: `mobile/lib/features/family_link/data/repositories/remote_caregiver_repository.dart` — AC: AC3 — xong khi: test unit gọi đúng HTTP DELETE và xử lý 204 thành công.
- [ ] P2 [`frontend`] Cập nhật UI màn hình `CaregiversScreen`: nhãn nút "Gỡ liên kết", hộp thoại xác nhận cảnh báo mất quyền xem, loading spinner khi busy, thông báo SnackBar thành công `Đã gỡ liên kết với $name.` — file: `mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart` — AC: AC1, AC2, AC3, AC4, AC5 — xong khi: test widget xác nhận đúng nhãn, đóng dialog khi hủy, gọi repo khi xác nhận, hiển thị loading và xử lý lỗi.
- [ ] P3 [`frontend`] Bổ sung phương thức `clearPatientData(String patientId)` trong `LocalMedicationStore` và `SqliteLocalMedicationStore` để xóa schedules theo `patient_user_id` — file: `mobile/lib/core/storage/local_db/local_medication_store.dart` — AC: AC7 — xong khi: test xác nhận schedules của patientId bị xóa sạch, schedules của patient khác được giữ nguyên.
- [ ] P4 [`frontend`] Bổ sung phương thức `removePatient(String patientId)` trong `FamilyAlertController` — file: `mobile/lib/features/family/presentation/state/family_alert_controller.dart` — AC: AC8 — xong khi: test xác nhận alert của patientId bị loại bỏ khỏi danh sách và reset detail nếu đang mở.
- [ ] P5 [`frontend`] Hiện thực `LinkedPatientsController` quản lý danh sách bệnh nhân liên kết của Family Member, xử lý 403 thu hồi quyền và đồng bộ danh sách mới — file: `mobile/lib/features/family_link/presentation/state/linked_patients_controller.dart` — AC: AC6, AC7, AC8, AC9 — xong khi: test xác nhận xóa patient khỏi danh sách, dọn dẹp cache SQLite và alerts, an toàn khi chạy nhiều lần.
- [ ] P6 [`frontend`] Kết nối hook `onPatientRevoked` trong `AdherenceController` khi gặp 403 denied — file: `mobile/lib/features/adherence/presentation/state/adherence_controller.dart` — AC: AC6 — xong khi: test xác nhận khi 403 trả về thì history bị xóa và hook được kích hoạt.
- [ ] P7 [`frontend`] Viết và cập nhật toàn bộ test unit/widget cho các thay đổi trên — file: `mobile/test/features/family_link/remote_caregiver_repository_test.dart`, `mobile/test/features/family_link/caregivers_screen_test.dart`, `mobile/test/core/storage/local_medication_store_test.dart`, `mobile/test/features/family_link/linked_patients_controller_test.dart`, `mobile/test/features/adherence/adherence_controller_test.dart` — AC: AC1–AC9 — xong khi: `flutter test` toàn bộ 5 file test pass 100%.

## 6. Test

### Unit & Widget

| Test dự kiến | AC | Submodule |
|---|---|---|
| `test_remote_caregiver_repository_revoke_delete_204` | AC3 | `frontend` |
| `test_caregivers_screen_renders_remove_link_button` | AC1 | `frontend` |
| `test_caregivers_screen_cancel_dialog_does_not_call_api` | AC2 | `frontend` |
| `test_caregivers_screen_confirm_dialog_calls_revoke_and_shows_success` | AC3 | `frontend` |
| `test_caregivers_screen_revoke_failure_keeps_item_and_shows_error` | AC4 | `frontend` |
| `test_caregivers_screen_idempotent_revoke_reloads_list` | AC5 | `frontend` |
| `test_adherence_controller_denied_clears_history_and_calls_hook` | AC6 | `frontend` |
| `test_sqlite_local_medication_store_clear_patient_data` | AC7 | `frontend` |
| `test_family_alert_controller_remove_patient` | AC8 | `frontend` |
| `test_linked_patients_controller_handles_revocation_403` | AC6, AC7, AC8 | `frontend` |
| `test_linked_patients_controller_sync_new_patients_removes_old` | AC7, AC8 | `frontend` |
| `test_linked_patients_controller_concurrent_revocation_safety` | AC9 | `frontend` |

### Tích hợp

Không có test tích hợp API mới trong task này do API backend `DELETE /family/links/{id}` đã có bộ integration test DB thật ở task 3.26 (`backend/tests/integration/test_sql_family_links.py`). Mọi kiểm thử của task 3.27 được bao phủ toàn diện ở mức Unit và Widget test trên mobile app.

## 7. Migration

Không có (không thay đổi schema cơ sở dữ liệu server hay local SQLite schema version).

## 8. Nhánh git

| Submodule | Nhánh |
|---|---|
| Superproject | `feat/3.27-remove-link-ui` |
| `frontend` | `feat/3.27-remove-link-ui` |

## 9. Rủi ro

| Rủi ro | Mức độ | Biện pháp giảm thiểu |
|---|---|---|
| Bệnh nhân nhấn liên tục nút Gỡ liên kết gây gửi request trùng lặp | Thấp | `CaregiversController` sử dụng tập hợp `_busy` để khóa nút ngay khi bắt đầu request, ngăn mọi lời gọi trùng. |
| Người thân vẫn hiển thị thông tin bệnh nhân từ cache sau khi bị gỡ liên kết | Trung bình | `LinkedPatientsController` và `AdherenceController` ngay khi nhận 403 sẽ lập tức xóa RAM (`history = null`) và gọi `clearPatientData(patientId)` làm sạch SQLite. |
| Xóa nhầm dữ liệu của bệnh nhân khác khi dọn dẹp cache | Thấp | Mọi truy vấn xóa trong `LocalMedicationStore` và lọc trong `FamilyAlertController` đều có điều kiện `WHERE patient_user_id = ?`, có unit test kiểm tra tính độc lập dữ liệu. |
| Phá vỡ các mock/fake store hiện có khi thêm hàm vào interface `LocalMedicationStore` | Thấp | Thêm default implementation `clearPatientData(String patientId) async {}` ngay trong interface `LocalMedicationStore`, giúp các fake store cũ tiếp tục biên dịch bình thường. |

## 10. Câu hỏi mở

Không có.

## 11. Phát sinh

Không có.

## Bước tiếp theo

- Đang chờ: Người duyệt xem xét và phê duyệt `03-plan.md`.
- Việc cần làm: Người duyệt chạy lệnh duyệt trong terminal:
  ```bash
  python .agents/scripts/gate.py approve 3.27-remove-link-ui plan
  ```
- Cập nhật lần cuối: 2026-10-23 15:30 +0700, Antigravity
