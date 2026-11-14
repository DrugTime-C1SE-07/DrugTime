---
task: adhoc-20261113-mobile-home-empty
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-14 21:02 +0700
content_hash: sha256:4d828faaef3faf4a
inputs:
  01-requirement.md: sha256:b3edca5e56e36204
---

# Kế hoạch triển khai S05-empty

## 1. Giải pháp

Dựng màn Flutter từ Figma `31:3957` và gắn vào tab Trang chủ qua `AppShell`. Banner, mascot, ba lối tắt, thẻ trống và navbar dùng widget Flutter. Đối chiếu màu, chữ, bóng và vị trí ở 375 × 812. Dùng safe area hệ điều hành và chừa vùng cuộn bên dưới navbar để các nút vẫn chạm được trên màn nhỏ.

Dùng `MedicationScope` và controller hiện có. Theo dõi lần tải thành công theo vòng đời controller để danh sách khởi tạo rỗng không bị hiểu thành chưa có thuốc. Tái sử dụng logic tải sẵn có, tránh hai lần tải chồng nhau từ Trang chủ và tab Thuốc. Khi lỗi, dùng thông báo và thao tác thử lại hiện có. Khi đã có thuốc, cung cấp lối vào danh sách thuốc, không mô phỏng lịch hôm nay.

Navbar riêng cho S05-empty ánh xạ trực tiếp bốn tab qua `AppTab`, tránh dùng chỉ số của danh sách rút gọn để truy cập enum. Lối tắt Người thân gọi cùng logic chọn tab đang dùng. Các trạng thái khác giữ navbar hiện có và badge Người thân.

Giữ điểm vào `showWelcomeOnboardingSheet`, modal barrier, nội dung cuộn và callback hiện có. Tắt drag mặc định của Material và chuyển quyền xử lý kéo sang vùng đầu popup có tay nắm. Vùng nội dung tiếp tục cuộn độc lập. Dùng cùng một vị trí hiển thị cho thao tác kéo và chuyển động lúc thả. Khi thả theo hướng đóng, chỉ pop route sau khi popup trượt hết. Nếu người dùng giữ và kéo lên trong lúc đó, dừng chuyển động tại vị trí hiện tại và cho phép giữ popup mở. Với Giảm chuyển động, giữ cách mở và đóng bằng nút tức thì đã triển khai, đồng thời kết thúc thao tác kéo mà không chạy thêm animation sau khi thả.

Theo yêu cầu cập nhật, popup giữ hai góc trên bo 24 dp, hai góc dưới vuông và nền phủ hết chiều ngang tới mép dưới viewport. Giữ phần đệm của nội dung theo vùng an toàn hiện có và dùng chỉ báo Home do hệ điều hành cung cấp. Đối chiếu lại mép trên y332 và các vị trí nội dung ở 375 × 812.

## 2. Khảo sát và truy vết

| Nguồn | Kết quả |
|---|---|
| Figma `31:3957` | Banner 236 dp, ba lối tắt trong hàng 335 × 84, thẻ tại y356, navbar 343 × 58 với Trang chủ được chọn. Dùng đúng mascot vui vẻ và mascot nấu ăn cho Dumi AI. |
| `app_shell.dart`, `router.dart`, `my_medications_screen.dart`, `add_medication_screen.dart` | Có route thêm thuốc và flow capture trả `CaptureResult`. Nút Quét vỏ hộp cần dùng lại luồng nhận kết quả và điền form thêm thuốc, không bỏ kết quả khi camera đóng. |
| `router.dart` | Có inbox cảnh báo Người thân, chưa xác nhận có inbox thông báo chung tương ứng Figma. Dùng route inbox có sẵn cho phạm vi cảnh báo được hỗ trợ, giữ kiểm tra auth/consent và nêu giới hạn tại bàn giao. |
| `medication_controller.dart` | Có `isLoading`, `loadError`, danh sách và reset khi đăng xuất. Chưa phân biệt danh sách rỗng lúc khởi tạo với tải thành công. |
| Checkout task welcome popup, Foundation và frame Figma `32:4174` | Tái sử dụng các file đã nghiệm thu nếu baseline chưa có. Frame Figma bo cả bốn góc 24 px. |
| `welcome_onboarding_sheet.dart`, `welcome_onboarding_sheet_test.dart` và Flutter SDK `material/bottom_sheet.dart` | Route Material hiện pop ngay khi vuốt đạt ngưỡng và bỏ qua drag update khi animation ở trạng thái `reverse`. Test hiện có phủ hình học, vuốt đóng, Giảm chuyển động, cỡ chữ lớn và callback CTA. |

QD-28 và QD-31 (mục 8–9 của tài liệu quyết định nghiệp vụ) giữ nguyên qua cổng hiện tại và test điều hướng AC3–AC4. QD-40/41 (mục 11) được giữ qua việc không thêm thu thập dữ liệu hoặc gửi dữ liệu cho Dumi AI. Đã tìm trong Flutter hiện tại và chưa thấy màn Dumi AI. Lối tắt sẽ có phản hồi “Dumi AI chưa khả dụng” nếu vẫn chưa có route. S08a chưa có route tương ứng. Callback CTA của popup sẽ báo luồng thiết lập chưa khả dụng thay vì chuyển sang màn khác.

## 3. File sẽ thay đổi

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/features/home/presentation/screens/home_screen.dart` | Thêm | Banner, lối tắt và các trạng thái Trang chủ. |
| frontend | `mobile/lib/features/home/presentation/widgets/home_navigation_bar.dart` | Thêm | Navbar S05-empty. |
| frontend | `mobile/lib/app/app_shell.dart`, `mobile/lib/app/router.dart` | Sửa | Gắn tab, callback và dữ liệu đầu vào cho route thêm thuốc khi cần. |
| frontend | `mobile/lib/features/medication/presentation/state/medication_controller.dart`, `mobile/lib/features/medication/presentation/screens/add_medication_screen.dart` | Sửa nếu cần | Phân biệt tải thành công, tái sử dụng capture và điền form. |
| frontend | `mobile/lib/features/auth/presentation/widgets/welcome_onboarding_sheet.dart` | Thêm hoặc sửa | Dùng lại popup, giữ kéo đảo chiều và chỉ bo hai góc trên. |
| frontend | `mobile/assets/icons/home/*.svg`, `mobile/assets/icons/welcome/*.svg`, `mobile/assets/icons/navigation/*.svg`, `mobile/assets/icons/navigation/LICENSE-Lucide.txt`, `mobile/assets/icons/pill-id/*.svg`, `mobile/assets/fonts/Inter-*.ttf`, `mobile/assets/fonts/OFL-Inter.txt`, `mobile/pubspec.yaml` | Thêm hoặc sửa nếu thiếu | Tài nguyên cần dùng, giữ mascot PNG sẵn có. |
| frontend | `mobile/test/features/home/home_screen_test.dart`, `mobile/test/app/app_shell_test.dart`, `mobile/test/features/auth/welcome_onboarding_sheet_test.dart`, `mobile/test/features/medication/medication_controller_test.dart` | Thêm hoặc sửa | Kiểm trạng thái, tương tác, popup và hồi quy tab. |

## 4. Checklist và test

- [ ] P1 [frontend] Tạo checkout riêng nhánh `feat/adhoc-20261113-mobile-home-empty` cho superproject và frontend. Xác nhận trạng thái baseline và lưu ảnh Figma. AC1–AC4.
- [ ] P2 [frontend] Đối chiếu tài nguyên Figma và đóng gói đúng file cần dùng, tái sử dụng popup. AC1, AC3. Xong khi Flutter tải được tài nguyên và popup đóng/mở trên host.
- [ ] P3 [frontend] Dựng màn và nối AppShell, trạng thái tải và các hành động. AC2–AC4. Widget test kiểm loading, lỗi, rỗng, đã có thuốc, quay về sau thêm, callback popup, scan và đường vào Người thân.
- [ ] P4 [frontend] So ảnh Flutter với Figma ở 375 × 812. Kiểm chữ lớn và màn hẹp, nút không bị navbar che. AC1, AC4.
- [ ] P5 [frontend] Thêm test hồi quy cho thao tác giữ và kéo lên giữa lúc popup đang đóng. Xác nhận test thất bại trên route Material hiện tại. AC3.
- [ ] P6 [frontend] Nối vùng tay nắm với chuyển động có thể ngắt và chỉ pop sau khi trượt hết. Widget test kiểm kéo nhẹ rồi thả trở về, vuốt nhanh để đóng, kéo ngược giữ popup, đóng bằng Để sau và nút Back, callback CTA đúng một lần, Giảm chuyển động và khả năng cuộn khi chữ lớn. AC3–AC4.
- [ ] P7 [frontend] Chỉnh Material dùng `BorderRadius.vertical(top: Radius.circular(24))`. Cập nhật `welcome_onboarding_sheet_test.dart` để kiểm bán kính góc dưới bằng 0, bề mặt rộng 375 dp chạm mép dưới y812 và mép trên giữ y332. Kiểm nút Để sau vẫn chạm được với inset dưới 34 dp, màn hẹp và chữ lớn. Render lại ảnh và cập nhật preview từ bản build sau sửa. AC1, AC3–AC4.
- [ ] P8 [frontend] Chạy test Flutter, kiểm scope và đối chiếu lỗi nếu có với baseline. AC1–AC4.

Không có migration hoặc test xuyên service. Rủi ro chính là hai task phụ thuộc chưa merge, thay đổi thứ tự tab và kết quả quét vỏ hộp. Kiểm bundle, kiểm ánh xạ từng tab và kiểm việc chuyển kết quả quét vào form.

Kiểm tranh chấp giữa thao tác vuốt, Back và CTA để route chỉ đóng một lần. Che phủ tương tác với màn nền cho đến khi route đóng hoàn tất. Kiểm vùng tay nắm không chặn thao tác cuộn và ghi rõ thiết bị đã dùng để kiểm safe area.

## Kiểm tra phạm vi

- `gate.py adhoc-20261113-mobile-home-empty plan` đạt. `scope.py adhoc-20261113-mobile-home-empty --stage plan` tại workspace chính báo 1.267 file ngoài phạm vi. Lượt cập nhật này chỉ ghi kế hoạch và log dưới `work/adhoc-20261113-mobile-home-empty/`. Chi tiết tại `evidence/plan-popup-motion-scope.log`.

## Bước tiếp theo

- Đang chờ duyệt kế hoạch. Chạy `python .agents/scripts/gate.py approve adhoc-20261113-mobile-home-empty plan` từ gốc repo.
- Sau khi duyệt, tiếp tục P7–P8 cho thay đổi hai góc dưới. P5–P6 đã triển khai và có bằng chứng trong `04-impl-notes.md`. Nếu cổng implement yêu cầu mở lại ghi chú đã duyệt, chạy `python .agents/scripts/gate.py reopen adhoc-20261113-mobile-home-empty implement`.
- Cập nhật lần cuối 2026-11-14, Codex.
