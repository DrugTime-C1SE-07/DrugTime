---
task: adhoc-20261113-mobile-home-empty
stage: implement
owner: Ngọc Việt
started_at: 2026-11-13
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-14 22:55 +0700
content_hash: sha256:65e5710145df911f
inputs:
  01-requirement.md: sha256:b3edca5e56e36204
  03-plan.md: sha256:4d828faaef3faf4a
---

# Triển khai S05-empty

| Bước | Trạng thái | Bằng chứng |
|---|---|---|
| P1 | Xong | Checkout riêng tại `scratch/checkout`, nhánh `feat/adhoc-20261113-mobile-home-empty`. Figma `31:3957` làm mốc đối chiếu. |
| P2 | Xong | SVG banner, biểu tượng và minh họa từ Figma, Inter và mascot từ assets, dùng lại popup chào mừng. `evidence/implement-pub.log` và `evidence/implement-widget-final.log`. |
| P3 | Đã triển khai, kiểm thử một phần | AppShell, trạng thái dữ liệu, điều hướng và popup. Widget test kiểm trạng thái trước và sau khi tải danh sách trống, mở popup và trở về. Các luồng lỗi, thuốc đã có, quét và đổi tab còn cần kiểm thử tích hợp. |
| P4 | Đã xem bản render, chưa đạt xác nhận AC1 và AC4 | `evidence/home-375x812.png` render từ test với safe area mô phỏng. Hàng lối tắt và navbar gần vị trí Figma, nhưng chưa kiểm khớp đủ màu, bóng và kích thước. Chưa kiểm Trang chủ trên viewport hẹp hoặc chữ lớn. |
| P5 | Đã đối chiếu bộ test Flutter và scope | Bộ test trước lần tinh chỉnh giao diện cuối có 1.028 pass, 1 skip, 5 fail. Cả 5 tên test fail trùng báo cáo task popup. Sau tinh chỉnh, 5 widget test liên quan đều pass. |

## File đã đổi và hành vi cần kiểm

- `HomeScreen`, `HomeNavigationBar`, `AppShell` nối Trang chủ với controller hiện có. Thanh bốn tab chỉ dùng khi danh sách trống đã tải thành công. Lối tắt Người thân gọi lại điều hướng hiện hữu. Các cổng auth và consent không thay đổi (QD-28, QD-31).
- `MedicationController` ghi nhận lần tải thành công. `router.dart` và `AddMedicationScreen` mở capture từ nút Quét vỏ hộp và tái sử dụng logic điền form.
- `WelcomeOnboardingSheet` mở từ Bắt đầu nào, hai góc dưới vuông. Thêm tài nguyên SVG, Inter và khai báo assets cần thiết.
- Chuông mở cảnh báo Người thân. Dumi AI và CTA thiết lập hồ sơ hiện hiển thị thông báo vì chưa có route tương ứng. Không thêm xử lý dữ liệu Dumi (QD-40, QD-41).

## Kiểm tra cuối

- `flutter test --no-pub`: `evidence/implement-final-frontend.log`. Mốc đối chiếu là `../adhoc-20261113-mobile-welcome-popup/evidence/test-flutter-suite-v2.log`. 
- `flutter test --no-pub test/features/home/home_screen_test.dart test/features/auth/welcome_onboarding_sheet_test.dart`: 5 pass, `evidence/implement-widget-final.log`.
- `dart analyze` trên các file đã thay đổi: không có lỗi trước tinh chỉnh kiểu chữ cuối, `evidence/implement-analyze-final.log`.
- `scope.py --stage implement` trên checkout riêng: không có file ngoài phạm vi, `evidence/implement-scope.log`.

## Xác minh nền popup

- Nút Bắt đầu nào xuất hiện khi đã tải thành công danh sách trống. Bottom sheet phủ lên chính instance Trang chủ hiện tại với navbar bốn tab. Để sau đóng sheet và trả về Trang chủ.
- 5 widget test pass, gồm xác nhận S05-empty và navbar vẫn được giữ khi popup mở. Log tại `evidence/implement-popup-background.log`. Ảnh widget test tại `evidence/home-welcome-375x812.png`. Đã xem ảnh, xác nhận nền dimmed hiển thị banner, mascot và ba lối tắt.
- Scope kiểm lại trên checkout riêng, không có file ngoài danh sách đã duyệt.

## Căn chỉnh nền S05-empty phía sau popup

- Đối chiếu node nền `626:10447` trong frame `32:4174`. Ở 375 × 812 với inset trên 44, lời chào bắt đầu y60, nút Bắt đầu nào y132, mascot y118, lớp nền nội dung y212 và ba thẻ lối tắt y224. Giữ vùng chạm nút mở 48 dp và hình nền nút 32 dp.
- Sửa `home_screen.dart` và mở rộng widget test Trang chủ với tên fixture Anh Bẻo cùng các mốc vị trí. Flutter render lại cho thấy ba lối tắt phía sau scrim và Để sau vẫn trả về Trang chủ. Ảnh tại `evidence/implement-popup-background-comparison.png`.
- `flutter test --no-pub --reporter expanded` có 1.028 đạt, 1 bỏ qua, 5 lỗi trùng tên ca với mốc trước sửa. `dart analyze` hai file không có lỗi. Scope implement pass. Log tương ứng `evidence/implement-popup-background-suite.log`, `evidence/implement-popup-background-analyze.log`, `evidence/implement-popup-background-scope.log`.
- Preview Chromium dùng WebAssembly và dữ liệu mẫu. Bản build có JavaScript dự phòng vẫn gặp giới hạn số nguyên trong OCR.

## Kiểm tra chuyển động và bố cục popup

- Chạy lại hai file `test/features/auth/welcome_onboarding_sheet_test.dart` và `test/features/home/home_screen_test.dart` bằng `flutter test --no-pub --reporter expanded`. Năm ca đạt, gồm hình học ở 375 × 812, thao tác đóng bằng vuốt, callback CTA và khả năng tiếp cận nút ở màn hẹp/chữ lớn. Log tại `evidence/implement-motion-widget.log`.
- Đọc `welcome_onboarding_sheet.dart:14` và Flutter SDK `bottom_sheet.dart`. Popup mở từ đáy trong 250 ms, đóng trong 200 ms khi bấm nút, cập nhật theo ngón tay khi kéo và dùng tốc độ thả khi vuốt nhanh. Flutter bỏ qua cập nhật kéo khi route đã chuyển sang `reverse`, do đó không hỗ trợ kéo lại để hủy lần đóng đang diễn ra. Chưa kiểm cử chỉ này trên thiết bị thật.
- Popup dùng chuyển động trượt mặc định khi hệ thống yêu cầu giảm chuyển động. Controller Flutter rút ngắn thời gian trong chế độ này, còn code popup chưa chuyển sang fade hoặc hiện trực tiếp. Chưa xác minh trên iOS/Android.
- Đối chiếu lại ảnh `evidence/implement-popup-background-aligned.png` với `evidence/recheck-welcome-figma.png`. Mép trên popup ở y332, ba lối tắt và CTA có bóng. Bóng ba lối tắt rõ hơn Figma. Hai góc dưới vẫn vuông theo plan, còn frame Figma bo 24 px. Preview web thiếu thanh trạng thái và chỉ báo Home của iOS.

## Sửa chế độ Giảm chuyển động của popup

- `welcome_onboarding_sheet.dart` dùng `AnimationStyle.noAnimation` khi `MediaQuery.disableAnimationsOf(context)` bật. Popup và scrim hiển thị hoặc biến mất ngay khi mở hay đóng bằng nút. Khi tùy chọn tắt, Flutter vẫn dùng chuyển động Material mặc định.
- Test hồi quy trong `welcome_onboarding_sheet_test.dart` kiểm vị trí y332 ở frame đầu và popup biến mất sau khi bấm Để sau. Trước sửa, popup vẫn nằm ở y812 tại frame đầu. Sau sửa, 6 widget test popup và Trang chủ đều đạt. Log tại `evidence/implement-reduced-motion-before.log` và `evidence/implement-motion-fix-widget.log`. Phân tích tĩnh hai file không báo lỗi. Scope đạt tại `evidence/implement-motion-fix-scope.log`.

- Bộ test Flutter đầy đủ có 1.029 đạt, 1 bỏ qua và 5 lỗi trùng chính xác các ca lỗi trong `implement-popup-background-suite.log`. Log tại `evidence/implement-motion-fix-suite.log`.

## Phát sinh

- Plan đã được cập nhật và duyệt để xử lý kéo đảo chiều và bo góc dưới. Chuyển động được xác minh bằng widget test. Chưa đo trên thiết bị iOS hoặc Android thật.

## Triển khai P5–P8 theo plan đã duyệt

- P5 xong. Test hồi quy xác nhận Flutter Material bỏ qua kéo ngược khi popup đang đóng. Log `evidence/implement-popup-interrupt-before.log`.
- P6 xong. Vùng tay nắm điều khiển vị trí popup, tiếp nhận kéo lại khi popup đang trượt ra và chỉ đóng route sau khi hoàn tất. Nội dung vẫn cuộn riêng. 8 ca đạt, gồm kéo ngược, kéo ngắn, vuốt nhanh, Back, Để sau, CTA và Giảm chuyển động. Log `evidence/implement-popup-interrupt-widget.log`.
- P7 xong trên fixture. Ảnh Flutter ở 375 × 812 với inset dưới 34 dp tại `evidence/implement-popup-interrupt-375x812.png`. Mép trên y332, bo bốn góc 24 dp và bóng CTA hiển thị. Preview Chromium đã nạp lại WebAssembly ở `http://127.0.0.1:8761/?preview=full`. Trình biên dịch JS dự phòng vẫn báo giới hạn số nguyên ở OCR.
- P8 xong. Kiểm scope tại checkout task đạt và `dart analyze` hai file sạch. Bộ test Flutter có 1.031 đạt, 1 bỏ qua và đúng 5 lỗi trùng với `implement-motion-fix-suite.log`. Log `evidence/implement-popup-interrupt-scope.log`, `evidence/implement-popup-interrupt-analyze.log` và `evidence/implement-popup-interrupt-suite.log`.

## Hai góc dưới vuông theo yêu cầu cập nhật

- P7 xong. Bề mặt popup chỉ bo hai góc trên 24 dp. Ảnh `evidence/implement-square-popup-375x812.png` xác nhận nền phủ kín mép dưới. Widget test kiểm hình học từ y332 đến y812, inset 34 dp và thao tác ở 320 × 568 với chữ 200%. 8 ca đạt trong `evidence/implement-square-popup-widget.log`.
- Preview Chromium đã nạp bản WebAssembly mới ở 375 × 812. Nhánh JavaScript dự phòng vẫn lỗi hằng số nguyên tại OCR, xem `evidence/implement-square-popup-web.log`.
- P8 xong. `dart analyze` và scope đạt. Bộ test Flutter có 1.031 đạt, 1 bỏ qua và 5 lỗi trùng với `evidence/test-flutter-suite.log`. Bằng chứng mới tại `evidence/implement-square-popup-analyze.log`, `evidence/implement-square-popup-scope.log` và `evidence/implement-square-popup-suite.log`.

## Bóng đổ Trang chủ theo TC-HOMEEMPTY-01

- Chỉnh cục bộ `home_screen.dart`: giảm độ đậm bóng của ba lối tắt và thêm elevation cho hai nút trong thẻ trống. Bóng nút Thêm thuốc đậm hơn nút Quét vỏ hộp.
- Bốn ca fixture Trang chủ đạt trong `evidence/implement-home-shadows-fixture.log`. Ảnh 375 × 812 ở `evidence/implement-home-shadows-375x812.png`. So điểm ảnh với bản trước sửa trong `evidence/implement-home-shadows-pixels.log` xác nhận bóng ba thẻ nhẹ hơn và hai nút đã có bóng. Đây là tinh chỉnh theo ảnh đã có, vì phiên Reqwise mất kết nối khi lấy lại thông số effect Figma.

- Flutter analyze và scope đạt. Bộ test đầy đủ có 1.031 đạt, 1 bỏ qua, 5 lỗi trùng `test-square-popup-suite.log`. Log `evidence/implement-home-shadows-analyze.log`, `evidence/implement-home-shadows-scope.log` và `evidence/implement-home-shadows-suite.log`.
- Preview Chromium tại `http://127.0.0.1:8761/?preview=full` đã tải WebAssembly mới ở 375 × 812. Dart2JS vẫn vướng hằng số int64 trong OCR, xem `evidence/implement-home-shadows-web.log`.

## Vị trí navbar và biểu tượng quét theo TC-HOMEEMPTY-01

- Thêm SVG bốn góc quét và nét ngang theo ảnh Figma tại `assets/icons/home/scan.svg`, kích thước 24 dp. Hành động Quét vỏ hộp vẫn mở route capture hiện có.
- Với inset iOS 34 dp, navbar dùng khoảng cách đáy 20 dp như mẫu. Các inset khác dùng toàn bộ vùng an toàn và tối thiểu 8 dp. Widget test xác nhận navbar ở (16, 734), rộng 343 dp, cao 58 dp trong khung 375 × 812. Chưa xác minh trên điện thoại thật.
- 9 widget test popup/Trang chủ và 4 ca fixture Trang chủ đều đạt. Ảnh `evidence/implement-home-nav-375x812.png`. Log `evidence/implement-home-nav-widget.log` và `evidence/implement-home-nav-fixture.log`. Phân tích tĩnh và scope đạt, log `evidence/implement-home-nav-analyze.log` và `evidence/implement-home-nav-scope.log`.
- Bộ test Flutter có 1.032 đạt, 1 bỏ qua và đúng 5 lỗi trùng `test-home-shadows-suite.log`. Log `evidence/implement-home-nav-suite.log`. Preview Chromium đã cập nhật file WebAssembly và asset `scan.svg`. Bản JavaScript dự phòng vẫn lỗi hằng số int64 ở OCR, log `evidence/implement-home-nav-web.log`.

## Bước tiếp theo

- Duyệt implement bằng `python .agents/scripts/gate.py approve adhoc-20261113-mobile-home-empty implement` để kiểm lại TC-HOMEEMPTY-01 và cập nhật báo cáo test. Các ca lưu qua form, camera và cử chỉ/vùng an toàn trên điện thoại vẫn cần bằng chứng.
