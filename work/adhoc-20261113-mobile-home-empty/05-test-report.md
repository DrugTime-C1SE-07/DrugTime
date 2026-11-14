---
task: adhoc-20261113-mobile-home-empty
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-14 23:00 +0700
content_hash: sha256:5b5dd1e9c142317e
inputs:
  01-requirement.md: sha256:b3edca5e56e36204
  03-plan.md: sha256:4d828faaef3faf4a
  04-impl-notes.md: sha256:65e5710145df911f
---

# S05-empty và popup chào mừng · Báo cáo kiểm thử

## 1. Môi trường

- Flutter tại checkout `scratch/checkout/frontend/mobile`, nhánh `feat/adhoc-20261113-mobile-home-empty`. Widget dùng fixture cục bộ, mô phỏng vùng an toàn. Task không đổi contract, endpoint hoặc quyền. Không có AC mức tích hợp xuyên dịch vụ hoặc yêu cầu reset DB.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Kiểm tra | Kết quả |
|---|---|---|
| AC1 | So ảnh mới khi popup đóng với node Figma `31:3957`. Đối chiếu riêng hình học popup với plan cập nhật. | Navbar đạt y734 trên fixture iOS và biểu tượng quét đã có hình đúng nhóm nét. TC-HOMEEMPTY-01 vẫn Fail vì chữ CTA và biểu tượng chuông, Hồ sơ còn lệch mẫu. Popup vuông góc dưới theo yêu cầu. |
| AC2 | Widget Trang chủ trước/sau khi tải và unit test controller giữ dữ liệu khi tải lỗi | Đạt phần đã kiểm. Còn kiểm giao diện lỗi/thử lại và trở về Trang chủ sau thêm thuốc. |
| AC3 | Mở popup, Để sau, vuốt nhanh, kéo ngược, Back, CTA một lần và Giảm chuyển động | Đạt trên widget. Còn kiểm mở camera, dữ liệu trả về form và các đích điều hướng từ S05-empty. |
| AC4 | Widget popup ở 320 × 568 và chữ 200% | Hai nút vẫn cuộn tới và chạm được. Còn kiểm navbar và đổi tab từ S05-empty thực tế. |

## 3. Kịch bản chất lượng

Không chạm các kịch bản tích hợp bắt buộc về phân quyền, dữ liệu sức khỏe, đồng bộ liều hoặc tương tác thuốc. Camera và điều hướng trên thiết bị còn Pending.

## 4. Kết quả chạy bộ test

- `flutter test --no-pub --reporter expanded`: 1.031 đạt, 1 bỏ qua, 5 lỗi, 2 phút 53 giây. Năm tên lỗi trùng với `evidence/test-flutter-suite.log`. Log mới `evidence/test-square-popup-suite.log`.
- Chạy riêng `test/features/auth/welcome_onboarding_sheet_test.dart`, `test/features/home/home_screen_test.dart` và `test/features/medication/medication_controller_test.dart`: 13 đạt. Log `evidence/test-square-popup-focused.log`.
- Kiểm ảnh 375 × 812 tại (0, 811), (374, 811) và (187, 811). Cả ba điểm có RGBA (255, 255, 255, 255), xác nhận nền phủ hai góc dưới và giữa mép dưới.
- `scope.py --stage test` tại checkout task báo 32 file frontend ngoài phạm vi. Đây là các thay đổi implement còn trong worktree và đã được duyệt. Lượt test chỉ ghi dưới thư mục task, gồm file tổng trong checkout tài liệu riêng. Log `evidence/test-square-popup-scope.log`.

## 5. Bộ test case Excel

- Spec `testcases.json`, file task `testcases.xlsx`. Validate, build và merge đều thành công. Log `evidence/test-home-nav-xlsx.log`.
- File tổng đã gộp tại `scratch/docs-test-checkout/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, trên nhánh `feat/adhoc-20261113-mobile-home-empty`. Đây là checkout riêng của submodule tài liệu, cùng commit gốc với `docs` hiện tại. Thay đổi workbook đang ở worktree.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| HOMEEMPTY | 16 | 12 | 1 | 3 |

- Pending: TC-HOMEEMPTY-06 lưu qua form, 12 camera, 15 cử chỉ và vùng an toàn trên thiết bị. Bug Report có TC-HOMEEMPTY-01 về kiểu chữ CTA và các biểu tượng còn khác.

## 6. Lỗi và giới hạn

- Các ca bổ sung chưa phát hiện lỗi chức năng sau khi dùng fixture có đủ controller. Bộ test đầy đủ ở lần chạy trước có 5 lỗi nền ở AppShell, liên kết Người thân và QR, cùng một ca skip.
- Kiểm trực quan toàn màn bằng fixture phát hiện sai khác bóng đổ mức Low. Kiểm trên thiết bị vẫn Pending.

## Bổ sung bằng chứng sau review

- Chạy bốn ca bằng `scratch/home_acceptance_test.dart` từ checkout Flutter. Đạt cả bốn assertion của fixture, gồm render Trang chủ, thử lại sau lỗi tải, cập nhật khi trở về từ màn thêm thuốc và chuyển tab/mở Người thân/chuông. Log `evidence/test-home-acceptance.log`.
- AC1, TC-HOMEEMPTY-01 Fail khi so ảnh `evidence/test-home-unobscured.png` với Figma `31:3957`. Navbar bốn tab hiển thị. Bóng thẻ lối tắt đậm hơn mẫu, nút **Thêm thuốc** và **Quét vỏ hộp** thiếu bóng nổi. Mức Low. Tên trong fixture là Bạn và ảnh không có các chỉ báo hệ thống iOS. Hai góc vuông của popup đã xác nhận riêng theo plan cập nhật.
- AC2, ca 05 Pass. Lỗi tải hiển thị nút Thử lại và khi nhấn sau khi phục hồi, Trang chủ hiển thị danh sách trống. Ca 06 đã xác minh qua màn thêm thuốc, controller và quay lại Trang chủ. Để Pending phần nhập và lưu hoàn chỉnh qua form.
- AC3–AC4, ca 14 Pass trên AppShell. Thuốc, Lịch nhắc, Hồ sơ, Người thân và chuông mở đúng màn theo fixture. Ca 12 camera và ca 15 cử chỉ/vùng an toàn trên điện thoại giữ Pending. ADB không thấy thiết bị kết nối, log `evidence/test-home-devices.log`.
- Excel cập nhật kỳ vọng và kết quả. Bảng HOMEEMPTY có 12 Pass, 1 Fail, 3 Pending. Log `evidence/test-home-acceptance-xlsx.log`.

## Kiểm lại sau chỉnh bóng

- 4/4 ca fixture Trang chủ đạt. Log `evidence/test-home-shadows-fixture.log`.
- Bộ test Flutter chạy lại trong 2 phút 58 giây, 1.031 đạt, 1 bỏ qua và đúng 5 lỗi trùng lần kiểm hình dạng popup. Log `evidence/test-home-shadows-suite.log`.
- Đối chiếu ba ảnh Figma, Flutter trước chỉnh và Flutter sau chỉnh trong `evidence/test-home-shadows-comparison.png`. Figma export 377 × 814 gồm viền ngoài, hai ảnh Flutter 375 × 812. Hai nút đã có bóng, nút Thêm thuốc đậm hơn nút Quét vỏ hộp. Bóng ba thẻ lối tắt đã dịu.
- TC-HOMEEMPTY-01 vẫn Fail mức Low. Navbar của fixture ở cao hơn khoảng 14 dp với inset dưới mô phỏng 34 dp. Biểu tượng Quét vỏ hộp khác mẫu. Ảnh Figma có thanh hệ thống iOS còn fixture thì không. Cần xác minh vị trí navbar trên thiết bị.
- Scope test vẫn báo 32 file frontend từ implement đã duyệt. Lượt kiểm thử này chỉ ghi dưới thư mục task. Log `evidence/test-home-shadows-scope.log`.

## Kiểm lại vị trí navbar và biểu tượng quét

- Bốn ca fixture đạt, gồm ảnh Trang chủ 375 × 812 với iOS inset 34 dp, thử lại, quay về sau cập nhật controller và đổi tab/chuông. Log `evidence/test-home-nav-fixture.log`.
- Ca widget kiểm tọa độ navbar đạt riêng, log `evidence/test-home-nav-geometry.log`. Bộ test Flutter đầy đủ có 1.032 đạt, 1 bỏ qua và đúng 5 lỗi trùng lần implement, thời gian 2 phút 18 giây. Log `evidence/test-home-nav-suite.log`.
- Ảnh `evidence/test-home-nav-comparison.png` đặt Figma bên trái và Flutter bên phải. Navbar nằm ở y734 trong fixture iOS, biểu tượng Quét vỏ hộp có bốn góc và nét ngang. Chữ CTA nhẹ hơn mẫu, chuông và Hồ sơ khác nét. Fixture dùng tên Bạn và không render thanh hệ thống.
- Scope test báo 33 file frontend từ implement đã duyệt. Lượt test này ghi dưới thư mục task và checkout tài liệu riêng. Log `evidence/test-home-nav-scope.log`.

## Bước tiếp theo

- Còn ca 06 lưu qua form, 12 camera và 15 thiết bị thật. TC-HOMEEMPTY-01 cần xử lý hoặc thống nhất các sai khác kiểu chữ và biểu tượng trước khi xác nhận khớp Figma toàn màn.
- Khi có thể nghiệm thu báo cáo, chạy `python .agents/scripts/gate.py approve adhoc-20261113-mobile-home-empty test`.
- Cập nhật lần cuối 2026-11-14, Codex.
