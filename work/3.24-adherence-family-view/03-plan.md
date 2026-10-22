---
task: 3.24-adherence-family-view
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-22 16:28 +0700
content_hash: sha256:c42bc0a5bb6b51b5
inputs:
  01-requirement.md: sha256:78a2784681c4911b
---

# 3.24-adherence-family-view · Plan

## 1. Giải pháp

- Tạo feature `adherence` trong Flutter theo lớp `domain/data/presentation` hiện có. `RemoteAdherenceRepository` dùng `ApiClient.getJson('/adherence', query: ...)` với app session token do `ApiClient` cung cấp; không gọi Supabase, không thêm lớp cache hoặc tự quyết định quyền. Mapper đọc schema `AdherenceByDateResponse`, giữ nguyên `patient_id`, ngày/giờ có offset, summary và bốn trạng thái liều.
- `FamilyAdherenceScreen` là route chỉ đọc với đối số bắt buộc `patientId`, tùy chọn `patientName`. Route được cấu hình trong `app/router.dart`; `DrugTimeApp` nhận repository qua dependency injection, `main.dart` cung cấp repository remote cho bản mobile. Nơi gọi từ danh sách bệnh nhân sẽ được nối trong task 5.13; không đưa bệnh nhân giả vào tab Người thân.
- Controller sở hữu dữ liệu trong vòng đời màn, tải lại qua API khi vào màn, đổi ngày, refresh và quay lại app. Trước mỗi request, xóa lịch sử đang hiển thị; dùng mã thế hệ/request để response cũ không thể ghi đè sau khi `patientId` đổi hoặc màn bị dispose. Với 403, xóa lịch sử và hiện trạng thái mất quyền; với 401 dùng luồng hết phiên sẵn có của `ApiClient`; 422 và lỗi mạng/5xx có thông báo phù hợp, lỗi mạng có nút thử lại. Không ghi tên thuốc, liều hoặc response vào log.
- Bố cục theo Figma S09a/S09b: tiêu đề có ngữ cảnh người bệnh, dải chọn ngày và lịch tháng trong tối đa 90 ngày gần đây, thẻ summary, danh sách nhóm theo ngày và thẻ liều. Các thẻ liều chỉ hiện trạng thái và thời gian liên quan, không có nút đánh dấu đã uống. Dùng token `app/theme/app_theme.dart`, kích thước chữ tối thiểu 14pt của app, vùng chạm 48dp, `Semantics`, `SafeArea` và cuộn thích ứng; Figma 375 × 812 là điểm đối chiếu, không là kích thước cố định.
- Tỷ lệ hiển thị là `adherence_rate` từ server, nhãn “Tỷ lệ tuân thủ (gồm uống trễ)”; `null` là “Chưa có liều được tính”. Ngày/giờ chuyển sang `Asia/Ho_Chi_Minh` trước khi format, không lấy giờ thiết bị làm chuẩn cho hiển thị lịch sử. Mọi trạng thái có nhãn và biểu tượng ngoài màu.

Chọn route độc lập thay vì thay ngay tab Người thân vì contract chưa có API liệt kê bệnh nhân liên kết; đưa `patient_id` cố định vào tab hoặc dùng dữ liệu mẫu trong bản chạy thật sẽ gây hiểu nhầm và có thể lộ sai bệnh nhân. Route typed arguments cũng cho phép task 5.13 nối điều hướng mà không đổi giao diện lịch sử.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/3.24-adherence-family-view/01-requirement.md` | AC1–AC10 đã duyệt; màn nhận `patient_id` từ nơi gọi, không có patient switcher. |
| `api_contract/openapi.json` (`GET /adherence`, `Adherence*`) | Query tối đa 90 ngày, `group_by=date`; `adherence_rate` gồm uống trễ và có thể `null`; 403 khi mất quyền, response `Cache-Control: no-store`. |
| `frontend/mobile/lib/app/router.dart`, `app.dart`, `app_shell.dart`, `main.dart` | Route tập trung ở router; app hỗ trợ inject repository; `ApiClient` dùng token phiên mỗi request; tab Người thân là placeholder, chưa có patient context. |
| `frontend/mobile/lib/app/theme/app_theme.dart` | Token Figma và thang chữ lớn đã có, dùng lại để tránh màu/spacing cục bộ. |
| `frontend/mobile/lib/core/api/api_client.dart`, `api_exception.dart` | GET có query, callback 401, phân loại lỗi mạng/server; cần map lỗi sang failure của feature. |
| `frontend/mobile/lib/features/medication/data/models/medication_api_mapper.dart`, `data/repositories/remote_medication_repository.dart`, `domain/repositories/medication_repository.dart` | Mẫu mapper, repository và dependency boundary của feature. |
| `frontend/mobile/lib/features/profile/presentation/state/profile_controller.dart`, `data/repositories/remote_profile_repository.dart` | Mẫu clear/generation tránh response cũ tái hiện sau mất quyền hoặc đổi tài khoản. |
| `frontend/mobile/test/features/medication/remote_medication_repository_test.dart`, `medication_screens_test.dart` | Mẫu HTTP test và widget test hiện có; không cần package mới. |
| Figma `Prototype_DrugTime`, Page 1, Reqwise node `75:7848`, `75:8120`, `51:5751` và design foundation | Ngôn ngữ visual cho lịch ngày/tháng, tiến độ, người thân; chưa có frame riêng cho màn này. |
| `.agents/skills/wf-health-endpoint/SKILL.md` | UI phải để backend PEP quyết định ở mỗi request; test phải kiểm đường 403, đổi `patient_id`, và đối chiếu bộ backend integration đã có về consent/audit. |

Kiểm tra phạm vi đã chạy: `python .agents/scripts/scope.py 3.24-adherence-family-view --stage plan` → OK. Output thô: `work/3.24-adherence-family-view/evidence/plan-scope.log`.

## 3. File sẽ thay đổi (ranh giới phạm vi)

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/features/adherence/domain/entities/adherence_history.dart` | thêm | Entity summary, date group, dose/status và khoảng ngày. |
| frontend | `mobile/lib/features/adherence/domain/entities/adherence_failure.dart` | thêm | Failure có loại denied, unauthorized, invalidRange, network, unavailable, invalidResponse. |
| frontend | `mobile/lib/features/adherence/domain/repositories/adherence_repository.dart` | thêm | Cổng đọc lịch sử theo `patientId` và khoảng ngày. |
| frontend | `mobile/lib/features/adherence/data/models/adherence_api_mapper.dart` | thêm | Parse response `group_by=date`, kiểm trường bắt buộc và offset thời gian. |
| frontend | `mobile/lib/features/adherence/data/repositories/remote_adherence_repository.dart` | thêm | Gọi `GET /adherence`, map 401/403/422/network/5xx. |
| frontend | `mobile/lib/features/adherence/presentation/state/adherence_controller.dart` | thêm | Tải, clear, chống response cũ, đổi bệnh nhân và refetch. |
| frontend | `mobile/lib/features/adherence/presentation/screens/family_adherence_screen.dart` | thêm | Màn chỉ đọc, loading/empty/denied/error, lifecycle và responsive layout. |
| frontend | `mobile/lib/features/adherence/presentation/widgets/adherence_summary_card.dart` | thêm | Summary và nhãn tỷ lệ đúng nghĩa. |
| frontend | `mobile/lib/features/adherence/presentation/widgets/adherence_dose_card.dart` | thêm | Thẻ liều với bốn trạng thái, chữ/icon, giờ tương ứng. |
| frontend | `mobile/lib/features/adherence/presentation/widgets/adherence_date_picker.dart` | thêm | Chọn ngày/tháng hợp lệ, giới hạn 90 ngày và ngày tương lai. |
| frontend | `mobile/lib/app/router.dart` | sửa | Route `familyAdherence` và đối số typed/kiểm đầu vào. |
| frontend | `mobile/lib/app/app.dart` | sửa | Inject repository vào router, không giữ lịch sử ở app scope. |
| frontend | `mobile/lib/main.dart` | sửa | Cấu hình repository remote từ `ApiClient` cho app mobile. |
| frontend | `mobile/test/features/adherence/adherence_api_mapper_test.dart` | thêm | Test parse schema, trạng thái, null rate, timezone, dữ liệu sai. |
| frontend | `mobile/test/features/adherence/remote_adherence_repository_test.dart` | thêm | Test query/token, lỗi API, không gọi nguồn khác hoặc cache. |
| frontend | `mobile/test/features/adherence/adherence_controller_test.dart` | thêm | Test clear trước refetch, 403, đổi bệnh nhân, response đến muộn. |
| frontend | `mobile/test/features/adherence/family_adherence_screen_test.dart` | thêm | Widget test nội dung, trạng thái, semantics, kích thước và route. |

## 4. Checklist

- [ ] P1 [frontend] Dựng entity/failure/repository và mapper cho response ngày, giữ đúng `adherence_rate`, `null`, bốn trạng thái và thời điểm có offset — file: `mobile/lib/features/adherence/domain/entities/adherence_history.dart`, `mobile/lib/features/adherence/domain/entities/adherence_failure.dart`, `mobile/lib/features/adherence/domain/repositories/adherence_repository.dart`, `mobile/lib/features/adherence/data/models/adherence_api_mapper.dart` — AC: AC2, AC3, AC4, AC8 — xong khi mapper test dữ liệu hợp lệ/không hợp lệ và biên thời gian pass.
- [ ] P2 [frontend] Dùng `ApiClient` gọi đúng `GET /adherence` với `patient_id`, `from`, `to`, `group_by=date`; map 401/403/422/network/5xx, không cache/quyết định quyền phía client và không log dữ liệu sức khỏe — file: `mobile/lib/features/adherence/data/repositories/remote_adherence_repository.dart` — AC: AC1, AC5, AC6, AC7, AC8 — xong khi HTTP test xác nhận URL/token, 403 và lỗi; backend PEP vẫn là điểm kiểm quyền duy nhất.
- [ ] P3 [frontend] Controller xóa dữ liệu trước mỗi request và khi đổi bệnh nhân/dispose, loại response đến muộn; refetch khi màn được mở lại hoặc app resume, 403 không để dữ liệu cũ — file: `mobile/lib/features/adherence/presentation/state/adherence_controller.dart` — AC: AC5, AC6, AC7 — xong khi test race A→B, 403 sau 200, refetch và dispose pass.
- [ ] P4 [frontend] Làm các widget ngày/tháng, summary, thẻ liều theo Figma/token app; ngày chọn không tương lai và khoảng query ≤90 ngày; trạng thái bằng chữ + icon, không có hành động ghi liều — file: `mobile/lib/features/adherence/presentation/widgets/adherence_date_picker.dart`, `mobile/lib/features/adherence/presentation/widgets/adherence_summary_card.dart`, `mobile/lib/features/adherence/presentation/widgets/adherence_dose_card.dart` — AC: AC2, AC3, AC8, AC9, AC10 — xong khi widget test kiểm nhãn/semantics và không overflow ở 375dp, text scale lớn.
- [ ] P5 [frontend] Dựng màn chỉ đọc với header ngữ cảnh bệnh nhân, loading/empty/denied/error/retry, SafeArea và scroll; khi chuyển ngày hoặc quyền thay đổi không lộ history trước — file: `mobile/lib/features/adherence/presentation/screens/family_adherence_screen.dart` — AC: AC1, AC4, AC5, AC6, AC7, AC9, AC10 — xong khi widget test xác nhận từng trạng thái và không có nút xác nhận/sửa liều.
- [ ] P6 [frontend] Nối route nhận typed `patientId`/`patientName?`, inject repository từ `main.dart` qua `DrugTimeApp`, để tab Người thân chờ luồng bệnh nhân task 5.13 — file: `mobile/lib/app/router.dart`, `mobile/lib/app/app.dart`, `mobile/lib/main.dart` — AC: AC1, AC6, AC7 — xong khi route test mở được với đối số hợp lệ và từ chối đối số thiếu/sai mà không gọi API.
- [ ] P7 [frontend] Chạy format/analyze và Flutter test feature, kiểm thủ công màn 375dp, landscape, text scale lớn, Semantics/TalkBack-VoiceOver và so Figma S09a/S09b — file: `mobile/test/features/adherence/adherence_api_mapper_test.dart`, `mobile/test/features/adherence/remote_adherence_repository_test.dart`, `mobile/test/features/adherence/adherence_controller_test.dart`, `mobile/test/features/adherence/family_adherence_screen_test.dart` — AC: AC1–AC10 — xong khi log của từng lệnh và kết quả manual được lưu ở `work/3.24-adherence-family-view/evidence/` trong giai đoạn test.
- [ ] P8 [frontend] Đối chiếu kiểm quyền/audit của endpoint sẵn có bằng bộ test tích hợp backend task 3.23; không sửa backend hoặc contract trong task này — file: `mobile/test/features/adherence/remote_adherence_repository_test.dart` — AC: AC5, AC6 — xong khi client test 403/cross-patient pass và log backend integration liên quan được tham chiếu/chạy theo điều kiện môi trường ở giai đoạn test.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `adherence_api_mapper_test.dart`: parse đủ bốn status, `taken_at=null`, null/100/biên tỷ lệ, `groups=[]`, offset UTC+7, response thiếu/sai field | AC2, AC3, AC4, AC8 | frontend |
| `remote_adherence_repository_test.dart`: query `patient_id` và ngày, bearer token; 401/403/422/5xx/network; không gọi Supabase, không retry ngầm sau 403 | AC1, AC5, AC6, AC7, AC8 | frontend |
| `adherence_controller_test.dart`: loading/clear, 200→403, A→B với response A đến muộn, refresh/resume, dispose, empty/error | AC4, AC5, AC6, AC7 | frontend |
| `family_adherence_screen_test.dart`: summary đúng nhãn, từng trạng thái liều, empty/denied/error/retry, route hợp lệ/sai, text scale, Semantics, không có nút sửa/xác nhận | AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC9, AC10 | frontend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Client HTTP test trong `mobile/test/features/adherence/remote_adherence_repository_test.dart` với `ApiClient` và server giả: token, query, 403, 401, body lỗi | AC1, AC5, AC7 | Chạy trong Flutter test, không cần DB thật. |
| `backend/tests/integration/test_adherence_history_access.py` hiện có: family được phép, thiếu link/consent, thu hồi, đổi `patient_id`, audit allowed/denied và fail-closed | AC5, AC6; kịch bản PEP/audit của `wf-health-endpoint` | Không sửa file backend. Chạy lại nếu môi trường Postgres/Supabase sẵn có; nếu không, ghi giới hạn và đối chiếu evidence đã duyệt của task 3.23. |
| Quan sát thủ công trên thiết bị/emulator: 375dp, landscape, text scale lớn, safe area, trình đọc màn hình; so bố cục Figma `75:7848`/`75:8120` | AC9, AC10 | Ghi thiết bị/cỡ chữ/ảnh và kết quả trong report; không coi tự động test là bằng chứng manual. |

## 6. Migration

Không có. Task chỉ đọc API hiện hữu, không đổi schema.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/3.24-adherence-family-view` để lưu artifact và sau này bump con trỏ frontend khi commit/push được yêu cầu. |
| frontend | `feat/3.24-adherence-family-view` trước khi sửa file trong implement; hiện detached HEAD, phải xử lý theo `wf-git` và xác minh base với con trỏ superproject. |

## 8. Rủi ro

- **Sai người bệnh hoặc lộ dữ liệu sau thu hồi quyền**: controller xóa trước khi tải, request generation loại response cũ; test A→B, 200→403 và request kế tiếp. Backend PEP/audit vẫn được kiểm chứng bằng integration test hiện có.
- **Nhầm tỷ lệ tuân thủ thành đúng giờ**: dùng số `adherence_rate` từ backend và nhãn rõ “gồm uống trễ”; test `late` và `null`.
- **Không có patient list API**: route yêu cầu `patientId`, không đưa patient cố định vào tab; task 5.13 nối nơi gọi. Kiểm tra route thiếu argument hiện trạng thái an toàn.
- **Frontend detached HEAD và con trỏ lệch**: trước implement phải xác định nhánh/base theo `wf-git`; không sửa submodule khi còn detached HEAD.
- **Figma chưa có frame chuyên biệt**: giữ visual từ S09a/S09b, ngữ cảnh người thân và hành vi chỉ đọc từ requirement; manual review kiểm khác biệt có chủ đích.
- **Môi trường integration backend**: nếu Supabase/Postgres không sẵn có, ghi rõ chưa kiểm lại trong phiên, không dùng test client để khẳng định audit backend pass.

## 9. Câu hỏi mở

Không có. Người dùng đã chọn route nhận `patient_id` từ nơi gọi; tích hợp chọn bệnh nhân thuộc task 5.13.

## 10. Phát sinh

- `frontend` đang detached tại `ea0e40cb`, trong khi superproject ghi con trỏ `8102c51a`; cần xử lý Git trước khi sửa code. Không sửa Git hoặc file frontend ở giai đoạn plan.
- UI này chưa có đường vào hoàn chỉnh từ tab Người thân trong bản chạy thật vì task 5.13/API danh sách bệnh nhân chưa có. Route có thể được gọi bởi nơi có `patientId` sau này và được kiểm bằng widget/route test ngay trong task 3.24.

## Bước tiếp theo

- Đang chờ: người duyệt xem plan và bảng file sẽ thay đổi.
- Việc cần làm: nếu đồng ý, chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view plan` trong terminal người duyệt. Sau đó mới xử lý nhánh frontend và implement.
- Cập nhật lần cuối: 2026-10-22 16:24 +0700, Codex.
