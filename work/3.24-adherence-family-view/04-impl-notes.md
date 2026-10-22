---
task: 3.24-adherence-family-view
stage: implement
status: draft
owner: Ngọc Việt
started_at: 2026-10-22 16:29 +0700
---

# 3.24-adherence-family-view · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `flutter test --no-pub test/features/adherence/adherence_api_mapper_test.dart`: 3 pass; parse bốn trạng thái, ngày/giờ có offset, null rate, dữ liệu sai. | `evidence/implement-P1.log` |
| P2 | xong | `flutter test --no-pub test/features/adherence/remote_adherence_repository_test.dart`: 6 pass; query/token từng request, 401/403/422/503, sai patient. | `evidence/implement-P2.log` |
| P3 | xong | `flutter test --no-pub test/features/adherence/adherence_controller_test.dart`: 4 pass; clear trước refresh, 403, A→B, giới hạn ngày. | `evidence/implement-P3.log` |
| P4 | xong phần code/test tự động | Widget test: 6 pass; bốn trạng thái, tỉ lệ, màn 320dp với chữ 1,6× không overflow. Đối chiếu trực quan với Figma trên thiết bị chuyển sang giai đoạn test. | `evidence/implement-P4-P6.log` |
| P5 | xong phần code/test tự động | Cùng widget test: loading, empty, denied xóa thuốc cũ, network retry, giao diện chỉ đọc. | `evidence/implement-P4-P6.log` |
| P6 | xong | Cùng widget test: route hợp lệ nhận `patientId`, route sai từ chối mà không gọi API; `test/app/app_shell_test.dart` trong lần chạy hồi quy pass. | `evidence/implement-P4-P6.log`, `evidence/implement-feature-tests.log` |
| P7 | xong phần implement | `dart format` không đổi; `dart analyze` không có issue; toàn bộ `flutter test --no-pub` 630 pass. Quan sát thiết bị, landscape và trình đọc màn hình chuyển sang giai đoạn test. | `evidence/implement-format.log`, `evidence/implement-analyze.log`, `evidence/implement-final-frontend.log` |
| P8 | đối chiếu xong, chưa chạy lại backend | Client HTTP test 403/cross-patient pass. Đọc log backend task 3.23: `test_adherence_history_access.py` nằm trong bộ 85 pass, gồm thu hồi quyền ở request kế tiếp và audit denied. Chưa chạy lại vì môi trường hiện không có lệnh Python/Supabase trên PATH; giai đoạn test sẽ đánh giá môi trường DB. | `evidence/implement-P2.log`, `evidence/implement-P8.log`, `../3.23-adherence-family-consent/evidence/test-migration.log` |

## 2. File đã thay đổi

- `frontend/mobile/lib/features/adherence/`: domain entity/failure/repository, mapper, repository HTTP, controller, màn và ba widget mới.
- `frontend/mobile/lib/app/router.dart`, `app.dart`, `main.dart`: route nhận `patientId` hợp lệ, DI repository remote và tải lại khi quay lại màn/app.
- `frontend/mobile/test/features/adherence/`: bốn file test mapper, HTTP, controller và widget/route.
- Không đổi backend, contract, schema hay `pubspec`.

`frontend` đã chuyển khỏi detached HEAD và tạo nhánh `feat/3.24-adherence-family-view` từ `origin/main`; con trỏ superproject chưa bump vì commit frontend chưa được yêu cầu/push. `scope.py --stage implement` lần đầu báo 79 file task 3.23 ngoài phạm vi do nhánh superproject khởi tạo từ task 3.23 thay vì `main`; không phải file mới sửa trong task 3.24. Xem `evidence/implement-scope.log` và mục Phát sinh.

## 3. Kết quả test cuối

- `flutter test --no-pub`: **630 pass**, 0 fail — `evidence/implement-final-frontend.log`.
- `dart analyze` trên feature, router, app, main và test: **No issues found** — `evidence/implement-analyze.log`.
- `dart format` trên cùng phạm vi: 0 file thay đổi — `evidence/implement-format.log`.
- `flutter pub get` thành công để tải dependency đã khai báo; thay đổi tự động của `pubspec.lock` đã được hoàn nguyên, không thuộc phạm vi task — `evidence/implement-pub-get.log`.

## 3b. Bộ test case Excel

Làm ở giai đoạn test (task size M).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Giao diện dùng token `AppColors`/`AppTextStyles` của app và pattern Figma S09a/S09b đã đọc qua Reqwise. Figma chưa có frame riêng cho view này.
- Tỷ lệ hiển thị là `adherence_rate` từ server, giữ đến hai chữ số thập phân; nhãn nói rõ gồm uống trễ. Thời gian liều hiển thị theo UTC+7; dữ liệu được xóa trước mỗi request, 403, đổi người bệnh và dispose.
- Route độc lập chờ task 5.13 cung cấp màn chọn bệnh nhân; không dùng `patientId` giả trong bản chạy thật.
- Chưa kiểm trực quan trên emulator/thiết bị, landscape hoặc TalkBack/VoiceOver; thực hiện ở giai đoạn test. Test widget hiện xác nhận bố cục không overflow ở 320dp và chữ 1,6×.

## 6. Phát sinh

- Sau khi cập nhật `frontend` lên `origin/main`, tab Người thân đã là `FamilyTabScreen` thay vì placeholder như khi lập plan; vẫn chưa có API danh sách bệnh nhân liên kết. Route nhận `patientId` trong plan vẫn phù hợp và không đụng file ngoài bảng đã duyệt.
- Nhánh superproject `feat/3.24-adherence-family-view` kế thừa commit task 3.23. `scope.py` tính diff từ `origin/main` nên báo 79 file 3.23 `[NGOÀI]`, dù 17 file frontend của 3.24 đều `[OK]`. Cần tách nhánh task từ `main` và giữ nguyên nhánh cũ như bản lưu, rồi chạy lại scope; không sửa artifact 3.23.

## Bước tiếp theo

- Đang chờ: tách nhánh superproject khỏi lịch sử 3.23, chạy lại scope và hoàn tất artifact.
- Việc cần làm: commit thư mục `work/3.24-adherence-family-view/` theo yêu cầu người dùng. Sau khi scope đạt, người duyệt xem implement và chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view implement` trong terminal của họ; agent không chạy lệnh duyệt.
- Cập nhật lần cuối: 2026-10-22 16:53 +0700, Codex.
