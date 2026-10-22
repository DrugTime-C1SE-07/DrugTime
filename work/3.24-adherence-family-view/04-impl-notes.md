---
task: 3.24-adherence-family-view
stage: implement
owner: Ngọc Việt
started_at: 2026-10-22 16:29 +0700
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-22 20:53 +0700
content_hash: sha256:e5195d96ad85dfb8
inputs:
  01-requirement.md: sha256:78a2784681c4911b
  03-plan.md: sha256:c42bc0a5bb6b51b5
---

# 3.24-adherence-family-view · Implement

## Lượt sửa BUG-FAMADH-20 sau khi reopen implement

- Gate implement đã mở theo thao tác reopen của người dùng. Chỉ sửa hai file nằm trong plan: `adherence_date_picker.dart` và `family_adherence_screen_test.dart`.
- Nguyên nhân: lịch có 7 cột Expanded nhưng chiều rộng khả dụng ở 320dp sau padding chỉ 288dp, khiến mỗi ô rộng 41.1dp. Bọc phần lịch tuần/tháng bằng `LayoutBuilder` và vùng cuộn ngang, giữ chiều rộng nội dung tối thiểu `7 × AppSizes.tapTarget` (336dp). Khi màn đủ rộng, dùng chiều rộng sẵn có; trên màn hẹp người dùng vuốt phần lịch để xem cột cuối. Không cuộn ngang toàn màn hình.
- Hồi quy bổ sung kiểm cả lịch tuần và tháng tại 320dp, 375dp, text scale 1.6× bằng `androidTapTargetGuideline`; kiểm chọn ngày 21 và cuộn tới Chủ nhật 18 ở cột cuối vẫn nhận đúng callback.
- Trước sửa: ca 320dp fail đúng vùng chạm 41.1dp — `evidence/implement-calendar-before.log`. Sau sửa: hai ca vùng chạm pass — `evidence/implement-calendar-after.log`. Lần chạy đầy đủ sau khi bổ sung kiểm chọn cột cuối: **632 pass, 0 fail, 117 giây** — `evidence/implement-calendar-final-frontend.log`.
- Format: 0 file đổi; analyze: **No issues found** — `evidence/implement-calendar-format.log`, `evidence/implement-calendar-analyze.log`. Scope implement pass, không có file ngoài phạm vi — `evidence/implement-calendar-scope.log`.
- Không cập nhật kết quả Fail trong báo cáo test/workbook thành Pass ở giai đoạn này. Cần duyệt lại implement trước khi chạy lại giai đoạn test; manual TalkBack/VoiceOver và đối chiếu Figma vẫn cần thực hiện.

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
| P8 | đối chiếu xong, chưa chạy lại backend | Client HTTP test 403/cross-patient pass. Đọc log backend task 3.23: `test_adherence_history_access.py` nằm trong bộ 85 pass, gồm thu hồi quyền ở request kế tiếp và audit denied. Giai đoạn test sẽ đánh giá môi trường DB và việc chạy lại backend. | `evidence/implement-P2.log`, `evidence/implement-P8.log`, `../3.23-adherence-family-consent/evidence/test-migration.log` |

## 2. File đã thay đổi

- `frontend/mobile/lib/features/adherence/`: domain entity/failure/repository, mapper, repository HTTP, controller, màn và ba widget mới.
- `frontend/mobile/lib/app/router.dart`, `app.dart`, `main.dart`: route nhận `patientId` hợp lệ, DI repository remote và tải lại khi quay lại màn/app.
- `frontend/mobile/test/features/adherence/`: bốn file test mapper, HTTP, controller và widget/route.
- Không đổi backend, contract, schema hay `pubspec`.

`frontend` đã chuyển khỏi detached HEAD và tạo nhánh `feat/3.24-adherence-family-view` từ `origin/main`; con trỏ superproject chưa bump vì commit frontend chưa được yêu cầu/push. Nhánh superproject đã được tách từ `main` và giữ nhánh cũ dưới tên `feat/3.24-adherence-family-view-inherited`. `scope.py --stage implement` lần cuối **OK: mọi thay đổi nằm trong phạm vi** — `evidence/implement-scope.log`.

## 3. Kết quả test lượt implement ban đầu (trước reopen)

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
- Nhánh superproject ban đầu kế thừa commit task 3.23 nên scope báo 79 file 3.23 `[NGOÀI]`. Đã giữ nguyên lịch sử cũ ở `feat/3.24-adherence-family-view-inherited`, tạo lại nhánh task từ `main` và cherry-pick hai commit chỉ chứa artifact 3.24. Scope sau đó pass; không sửa artifact 3.23.

## Bước tiếp theo

- Đang chờ: người duyệt xem bản sửa BUG-FAMADH-20 và artifact implement.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view implement` trong terminal của họ. Sau đó mới chuyển sang giai đoạn test; agent không chạy lệnh duyệt.
- Cập nhật lần cuối: 2026-10-22, Codex.
