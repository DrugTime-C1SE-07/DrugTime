---
task: adhoc-20261118-mobile-profile-flow-ui
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-18 10:47 +0700
content_hash: sha256:0145eb93e75e6160
inputs:
  01-requirement.md: sha256:c338df6345d3cc26
---

# Áp dụng Figma cho các màn còn lại của Hồ sơ & Người thân · Plan

## 1. Giải pháp

### Checkout và kế thừa S08

- Chỉ triển khai sau khi plan được duyệt, tại `work/adhoc-20261118-mobile-profile-flow-ui/scratch/workspace/frontend`, trong superproject cô lập cùng thư mục workspace. Nhánh superproject/frontend: `feat/adhoc-20261118-mobile-profile-flow-ui`.
- Tại implement, clone từ repo local, kiểm HEAD và origin/main hiện có; dùng baseline frontend đã xác minh `81566509` nếu chưa có cập nhật khác. Nếu baseline đã thay đổi, đối chiếu trước khi copy, không ghi đè file mới. Không pull root, stash, reset hoặc dọn workspace người dùng.
- Kế thừa đúng 5 file chưa commit của S08 từ `work/adhoc-20261118-mobile-profile-s08-ui/scratch/scope-baseline/frontend`: app_shell.dart, profile_screen.dart, profile_icons.dart, profile_screens_test.dart, profile_layout_test.dart. Lưu patch/hash vào evidence và ghi diff kế thừa riêng trong 04; không sửa checkout S08. Không commit/push trong task khi chưa được yêu cầu.
- Copy artifact của task vào work của checkout cô lập để chạy gate/scope ở đúng repo; đồng bộ kết quả và evidence trở lại artifact gốc. Chỉ tạo thư mục/checkout trong scratch sau khi bắt đầu implement. Scope root có thay đổi kế thừa không thuộc task, phải ghi riêng; scope checkout triển khai phải pass.

### Thành phần trình bày

- Tạo `shared/widgets/profile_flow_widgets.dart` chứa các thành phần riêng cho nhóm màn: header con, bề mặt thẻ, nút có bóng và nhãn “Chưa khả dụng”. Dùng AppColors/AppTextStyles/AppRadius/AppShadows khi khớp Figma; giữ override theo frame tại thành phần này, không đổi AppTheme toàn ứng dụng. Các widget thuần nhận dữ liệu/callback, không tự gọi API.
- Header thấp hơn status bar theo SafeArea; không vẽ giờ/battery/home indicator trong app. Đo mốc Figma 375 × 812 với top 44, bottom 34, header 56, lề ngang 20; kích thước và nền từng frame lấy từ Reqwise, không ép mọi màn dùng một nền. Nội dung cuộn; chiều cao tối thiểu thay chiều cao cố định khi chữ lớn.
- Icon ưu tiên Lucide/SVG sẵn có; màu theo Figma. Không tạo hiệu ứng trang trí mới, gradient hoặc chuyển động không có trong nguồn. Bóng gắn vào card/nút cần phân tầng, không gắn mọi control.
- Lưu bảng đo, ảnh nguồn và đối chiếu từng frame/overlay trong work/evidence. Mỗi màn phải được đọc ảnh + layer (kể cả component/overlay gốc) trước khi sửa; kiểm các biến thể theo ma trận requirement. Kết quả đo không lưu trong bộ nhớ riêng của tool làm nguồn duy nhất.

### Ma trận triển khai và sai khác đã được requirement cho phép

| Nhóm | Hướng triển khai | Giới hạn giữ nghiệp vụ |
|---|---|---|
| S08-1 | Thẻ avatar, trường tên, ngày sinh/giới tính, chiều cao/cân nặng, số điện thoại và email, CTA có bóng theo 51:5527. Giữ date picker, validation, generation, loading/denied và avatar picker. | Chiều cao/cân nặng không có trong ProfileDraft: hiển thị chưa khả dụng, không dùng số 158/54 của Figma. Phone chỉ đọc; diễn đạt là số liên hệ, không nói dùng để đăng nhập. Layer LIÊN HỆ đang ẩn trong ảnh Figma phải tiếp tục ẩn. |
| S08-2 | Giữ bệnh nền thật dạng chip/tile, chức năng thêm/sửa/xóa và danh mục; đặt các nhóm dị ứng, nhóm máu, bác sĩ theo bố cục mới của 51:5645. | Các nhóm/trạng thái không có nguồn hiển thị nhãn chưa khả dụng và control disabled, không suy rỗng thành đã xác nhận. Bệnh nền tiếp tục lưu tại sheet. CTA toàn màn disabled, chú thích ngắn bệnh nền lưu khi hoàn tất từng thao tác. |
| Sheet sức khỏe | Chỉnh nền, bo góc, spacing, trường và nút của sheet bệnh nền theo phần tương ứng 804:12389. Phần dị ứng nếu dựng dạng sheet phải có nhãn chưa khả dụng và không lưu. | Giữ trường subtype/stage, generation guard, nội dung lỗi, xác nhận xóa; không thay hành vi để rút ngắn giống hình Figma. Không bật control giả để người dùng nhập rồi mất dữ liệu. |
| S08-3 | Header, đếm items thật, thẻ avatar/tên/trạng thái, nút thu hồi và hộp thoại theo 51:5751 cùng biến thể một người/rỗng. Thêm đường vào màn mời. | Giữ công tắc sharing thật dù Figma không vẽ; chỉ hiển thị đang theo dõi/chia sẻ theo trạng thái thực. Không dùng quan hệ “con trai/con gái” khi entity không có dữ liệu. Giữ lối mở tab Người thân của empty cũ. |
| S08-3a | Tạo InviteCaregiverScreen với các option QR, quét QR và gửi link; push route hiện có. | Không fetch hoặc tạo yêu cầu khi chỉ mở hub. Quét vẫn theo vai trò và quy tắc hiện có, không đổi chủ thể dữ liệu. |
| S08-3b/g | FamilyLinkCodeScreen và ShareInviteLinkScreen dùng card mã/link, icon và các nút theo Figma. | Không có timer “Còn hiệu lực”, không “Làm mới mã” hoạt động vì code cố định. Giữ backend qrPayload/link thật. Share dùng system share sheet hiện có; shortcut Zalo/SMS/Email chưa có capability riêng hiển thị chưa khả dụng, không giả share thành công. Không thêm dependency/native intent để mở rộng chức năng. |
| S08-3c | Header và khung scan trên nền tối; lối nhập mã, nhãn quyền và lỗi. | Giữ scannerBuilder, camera lifecycle, permission recovery, parse payload và chống gửi lặp. Không thêm upload ảnh/flash nếu chưa được hỗ trợ hiện hành; nếu Figma có thì disabled. |
| S08-3d/f | Dùng LinkRequestResultScreen theo outcome waiting/accepted hiện có, minh họa trạng thái và nút Xong. | Waiting không có tên/avatar patient vì response không cung cấp, không có hủy request hoạt động. Accepted không khẳng định đã bật chia sẻ. Không thêm polling hoặc suy success theo thời gian. Nếu hướng bệnh nhân chưa có success riêng, dùng UI kết quả ngay sau approve trả thành công, giữ return bool và refresh hiện hành. |
| S08-3e và xác nhận | Chỉnh IncomingRequestsSection, LinkConsentConfirmationScreen và ApproveLinkSheet theo request thật và bề mặt Figma. | Giữ các bước đồng ý rõ ràng, scope/consentDocumentVersion, xác nhận từ chối, khóa khi gửi; không gộp hay bỏ checkbox ở luồng đang yêu cầu. Không đổi controller. |
| S08-4/4a | Tạo NotificationPreferencesScreen và ReminderSoundScreen; dựng nhóm và control đúng Figma, nhãn chưa khả dụng, điều hướng âm thanh hoạt động. | Các switch/slider/radio/lưu disabled; không lưu local preference, không gọi controller nhắc thuốc. Giá trị minh họa không trình bày như cài đặt hiện tại; hiển thị “Chưa khả dụng” thay 70%/chuông đã chọn. |
| S08-5 | Tạo ProfileSettingsScreen, entry từ nút cài đặt của S08. Các link điều khoản/quyền riêng tư dùng route thật; đăng xuất gọi callback đang có từ ProfileScreen. | Không nhân bản signOut logic hay bỏ cleanup/retry/_loggingOut. Khi đang logout khóa back/action như cần để chống thao tác lặp. Phiên bản dùng giá trị runtime có sẵn nếu có, nếu không hiển thị chưa khả dụng, không hard-code 1.0.0. Các tùy chọn ngôn ngữ/đơn vị/tối/xóa tài khoản disabled. |
| S08-6 | Đổi trình bày PrivacySettingsScreen theo nhóm/bề mặt Figma; thêm các dòng bảo mật disabled; liên kết quản lý người giám sát dùng route thật. | Giữ ba mục đích consent thật với callback riêng, xác nhận rút và trạng thái lỗi. Không gộp “chia sẻ ẩn danh” thành family_sharing/ai_meal. Không dùng số thiết bị/người có quyền giả; không đưa bảo đảm mã hóa không được xác minh vào thông báo mới. |

### Điều hướng và tương tác

- Bổ sung route thuần UI `profileInvite`, `profileNotifications`, `profileReminderSound`, `profileSettings` trong AppRoutes; giữ nguyên các route public hiện có, kiểu đối số và return value.
- ProfileScreen chuyển entry Thông báo từ ComingSoon tới route thật; cài đặt tới màn S08-5. Truyền callback `_logout` hiện có cho màn cài đặt qua route args được định kiểu, giữ đường đăng xuất cũ khả dụng và test retry. Nếu không có callback (direct route), không tự tạo auth flow: thông báo chưa khả dụng cho logout ở entry thiếu context, không crash.
- CaregiversScreen mở màn mời, các thành phần incoming tiếp tục dùng controller/scope đã cấp; không fetch lại khi rebuild. Return bool/result phải tiếp tục được caller xử lý như trước.

## 2. Khảo sát

| File/nguồn đã đọc | Điều rút ra |
|---|---|
| 01-requirement.md, approved bởi Ngọc Việt 2026-11-18 10:42 +0700 | 10 AC; UI các chức năng thiếu phải hiện chưa khả dụng. Không đổi contract. |
| docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md, mục 8–9 đọc lại ở plan | Baseline QD-2026-10-03-v1; giữ ✅/🆕/⏳, các điểm còn mở không được tự biến thành nghiệp vụ đã chốt. |
| Git status checkout S08; root frontend log; .gitmodules | S08 có đúng 5 file chưa commit trên feat/adhoc-20261118-mobile-profile-s08-ui. Root frontend baseline 81566509. Branch main cho các submodule. |
| frontend/mobile/lib/app/router.dart, app/theme/app_theme.dart | Route đã có cho profile/family/consent; token và tapTarget 48; không cần đổi theme toàn cục. |
| features/profile/presentation/screens/personal_profile_screen.dart, medical_profile_screen.dart; widgets/condition_editor_sheet.dart | Personal có bottom CTA và guard generation; medical chỉ conditions, editor lưu trực tiếp và xóa dữ liệu khi generation invalid. |
| features/family_link/presentation/screens/link_request_result_screen.dart, link_consent_confirmation_screen.dart, enter_link_code_screen.dart; widgets/incoming_requests_section.dart, approve_link_sheet.dart | waiting/accepted là hai kết quả khác; detail consent và approve sheet có guard/xác nhận. Giữ đường gọi và return hiện hành. |
| features/family_link/presentation/state/link_request_controller.dart qua rg | Outcome từ repository, route result pushReplacement; không cần sửa state. |
| Các test scan_link_qr_screen, consent_confirmation_screen, privacy_settings_screen, family_link_code_security qua rg tên test; danh sách test profile/family/consent | Có test sai QR, gửi lặp, quyền camera, dismiss không đồng ý, grant/withdraw/retry, xử lý mã lỗi. Tái chạy, không thay expected nghiệp vụ để khớp UI. |
| Reqwise contexts 51:5934, 6194, 6246, 6288, 6365, 6433, 6534, 6677, 6784, 6981; screenshot 51:5527 và 51:6981 | Xác định mâu thuẫn timer/hủy/chia sẻ, UI cài đặt chưa có capability. Screenshot personal không hiển thị LIÊN HỆ dù layer text tồn tại. |

Đường dẫn features/test viết rút gọn ở phần khảo sát tương đối với frontend/mobile/lib và frontend/mobile/test; bảng file bên dưới là đường dẫn chính xác. Skill dùng: wf-plan, wf-git, figma-ui-code. Không đổi endpoint/schema nên không có migration hoặc triển khai wf-health-endpoint cho backend; giữ nguyên đường gọi và test rủi ro ở phần 5.

### Quyết định nghiệp vụ áp dụng

| Nguồn mục 8–9 / nội dung | TT nguồn | AC | Bước | Test |
|---|---|---|---|---|
| QD-04/QD-34 mã cố định, không hết hạn, 10 ký tự, QR; nhập chỉ tạo pending và không lộ hồ sơ | ✅ | AC3, AC4 | P5, P6 | T3, T4 |
| QD-34 chống dò/giới hạn; BS-04 thay quy tắc gửi lại sau từ chối | ✅ / 🆕 14/10/2026 | AC4, AC7 | P6, P10 | T4, T7; giữ lỗi/rate limit của controller, không tái triển khai thuật toán ở UI |
| BS-05 cần family_sharing để lấy/chia sẻ mã | 🆕 14/10/2026 | AC3, AC5 | P5 | T3 |
| QD-27 chỉ xem; QD-28 liên kết + sharing + consent; QD-30 liên kết lại không khôi phục quyền | ✅ | AC4, AC5 | P4, P6, P8 | T4, T5 |
| QD-29 mất quyền/xóa cache phiên; không offline dữ liệu người thân | ✅ | AC5, AC7 | P4, P8, P10 | T5, T7; hồi quy sẵn có, không đổi cơ chế quyền/cache |
| QD-31 grant/withdraw riêng; không sửa lịch sử | ✅ | AC5 | P8 | T5 |
| CS-01/CS-04; AGENTS bất biến 1/2/4 | ⏳ theo nguồn, bắt buộc theo AGENTS | AC7, AC9 | P9, P10 | T7, T9; không sửa Backend/PEP, nếu cần đổi phải dừng mở phạm vi |

## 3. File sẽ thay đổi (ranh giới phạm vi)

40 file frontend được phép dưới đây: 25 file sản phẩm và 15 file test/helper; chỉ sửa những file cần thiết sau đối chiếu. Bao gồm 5 file kế thừa S08 để scope kiểm đúng, không coi đó là thiết kế lại S08.

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | mobile/lib/app/router.dart | Sửa | Route thuần UI mới và typed args, giữ route cũ. |
| frontend | mobile/lib/app/app_shell.dart | Sửa (kế thừa) | Giữ thay đổi nền/navbar S08, không đổi tab khác. |
| frontend | mobile/lib/shared/widgets/profile_flow_widgets.dart | Thêm | Widget trình bày dùng chung cho luồng. |
| frontend | mobile/lib/features/profile/presentation/screens/profile_screen.dart | Sửa | Kế thừa S08; entry notifications/settings, giữ logout callback. |
| frontend | mobile/lib/features/profile/presentation/screens/personal_profile_screen.dart | Sửa | S08-1, trường chưa khả dụng và giữ form thật. |
| frontend | mobile/lib/features/profile/presentation/screens/medical_profile_screen.dart | Sửa | S08-2 và trạng thái không hỗ trợ. |
| frontend | mobile/lib/features/profile/presentation/screens/notification_preferences_screen.dart | Thêm | S08-4. |
| frontend | mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart | Thêm | S08-4a. |
| frontend | mobile/lib/features/profile/presentation/screens/profile_settings_screen.dart | Thêm | S08-5 và callback logout hiện có. |
| frontend | mobile/lib/features/profile/presentation/widgets/profile_icons.dart | Sửa | Kế thừa màu icon S08, dùng tiếp cho màn con. |
| frontend | mobile/lib/features/profile/presentation/widgets/profile_form_fields.dart | Sửa | Style field thuộc profile, giữ validator. |
| frontend | mobile/lib/features/profile/presentation/widgets/avatar_picker_sheet.dart | Sửa | Bề mặt sheet avatar. |
| frontend | mobile/lib/features/profile/presentation/widgets/condition_catalog_sheet.dart | Sửa | Style danh mục/thêm bệnh. |
| frontend | mobile/lib/features/profile/presentation/widgets/condition_editor_sheet.dart | Sửa | Style editor, giữ generation và save/delete. |
| frontend | mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart | Sửa | Thẻ, empty, dialog và mở hub mời. |
| frontend | mobile/lib/features/family_link/presentation/screens/invite_caregiver_screen.dart | Thêm | S08-3a hub. |
| frontend | mobile/lib/features/family_link/presentation/screens/share_invite_link_screen.dart | Sửa | S08-3g. |
| frontend | mobile/lib/features/family_link/presentation/screens/scan_link_qr_screen.dart | Sửa | S08-3c. |
| frontend | mobile/lib/features/family_link/presentation/screens/enter_link_code_screen.dart | Sửa | Đồng bộ UI nhập mã từ scanner, giữ submit. |
| frontend | mobile/lib/features/family_link/presentation/screens/link_request_result_screen.dart | Sửa | S08-3d/f theo outcome thật. |
| frontend | mobile/lib/features/family_link/presentation/screens/link_consent_confirmation_screen.dart | Sửa | S08-3e, bảo toàn xác nhận. |
| frontend | mobile/lib/features/family_link/presentation/widgets/incoming_requests_section.dart | Sửa | Thẻ yêu cầu, phần dùng chung trong phạm vi. |
| frontend | mobile/lib/features/family_link/presentation/widgets/approve_link_sheet.dart | Sửa | Sheet giữ checkbox/phiên bản consent. |
| frontend | mobile/lib/features/family/presentation/screens/family_link_code_screen.dart | Sửa | S08-3b, code thật. |
| frontend | mobile/lib/features/consent/presentation/screens/privacy_settings_screen.dart | Sửa | S08-6 + consent thật. |
| frontend | mobile/test/features/profile/profile_screens_test.dart | Sửa | Kế thừa S08, regression form và medical. |
| frontend | mobile/test/features/profile/profile_layout_test.dart | Sửa | Kế thừa layout S08, narrow/text scale. |
| frontend | mobile/test/features/profile/profile_widget_helpers.dart | Sửa | Fixture dữ liệu/route và safe area dùng cho render. |
| frontend | mobile/test/features/profile/profile_flow_navigation_test.dart | Thêm | Entry mới, disabled capability, giữ logout. |
| frontend | mobile/test/features/profile/profile_flow_visual_test.dart | Thêm | Fixture render từng màn/trạng thái có thể dựng. |
| frontend | mobile/test/features/family_link/caregivers_screen_test.dart | Sửa | Chia sẻ/thu hồi, empty, hub. |
| frontend | mobile/test/features/family_link/scan_link_qr_screen_test.dart | Sửa | Layout scanner, giữ camera/QR regression. |
| frontend | mobile/test/features/family_link/share_invite_link_screen_test.dart | Sửa | Link/copy/share và disabled shortcut. |
| frontend | mobile/test/features/family_link/incoming_requests_test.dart | Sửa | Thẻ incoming và outcome. |
| frontend | mobile/test/features/family_link/consent_confirmation_screen_test.dart | Sửa | Giữ approve/reject/close/busy. |
| frontend | mobile/test/features/family_link/invite_link_flow_test.dart | Sửa | Điều hướng mời/link và kết quả. |
| frontend | mobile/test/features/family_link/enter_link_code_screen_test.dart | Sửa | Giữ nhập/parse/submit và lỗi. |
| frontend | mobile/test/features/family/family_link_code_screen_test.dart | Sửa | Mã thật, không timer, reload/error. |
| frontend | mobile/test/features/consent/privacy_settings_screen_test.dart | Sửa | Consent thật và security chưa khả dụng. |
| frontend | mobile/test/app/app_shell_test.dart | Sửa | Entry từ tab profile và hồi quy navbar. |

Không thêm dependency hoặc asset mới dự kiến: dùng Flutter/Lucide/QR đã có. Nếu cần asset Figma không thể tái dùng hoặc test/helper ngoài bảng thì ghi Phát sinh và xin mở phạm vi trước khi sửa. Workbook test tổng thuộc ngoại lệ wf-testcase tại giai đoạn test, không sửa trong plan.

## 4. Checklist

- [ ] P1 [frontend] Chuẩn bị checkout cô lập và kế thừa 5 file S08, lưu baseline/hash/diff — file: 5 file kế thừa trong bảng — AC: AC9 — xong khi: nhánh đúng, scope xác định được và diff kế thừa tách rõ; root/S08 checkout không bị ghi.
- [ ] P2 [frontend] Đọc ảnh/layer tất cả frame và overlay của requirement, lập ma trận viewport/token/trạng thái; dựng widget chung — file: profile_flow_widgets.dart — AC: AC1, AC8 — xong khi: mỗi frame có nguồn ID, ảnh, đo và mapping, widget chung không chứa API/state nghiệp vụ.
- [ ] P3 [frontend] Cập nhật personal/medical và sheet profile, các trường thiếu disabled — file: personal_profile_screen.dart, medical_profile_screen.dart và 5 widget profile trong bảng — AC: AC1, AC2, AC6, AC7, AC8 — xong khi: form/save/delete giữ test nghiệp vụ, không dữ liệu giả, render cùng viewport không overflow.
- [ ] P4 [frontend] Cập nhật caregivers và dialog cho nhiều/một/không có người, giữ sharing — file: caregivers_screen.dart — AC: AC1, AC4, AC5, AC7, AC8 — xong khi: dữ liệu thật, hủy không gọi, pending khóa, thu hồi/refresh đúng callback.
- [ ] P5 [frontend] Dựng hub mời, style QR/link/scanner/nhập mã, giữ code cố định và quyền camera — file: invite_caregiver_screen.dart, family_link_code_screen.dart, share_invite_link_screen.dart, scan_link_qr_screen.dart, enter_link_code_screen.dart — AC: AC1, AC2, AC3, AC4, AC7, AC8, AC10 — xong khi: có lối vào/ra thật, QR/share đúng payload, không timer hoặc hủy giả, scan lặp gửi một lần.
- [ ] P6 [frontend] Style request/consent/result theo outcome thật — file: link_request_result_screen.dart, link_consent_confirmation_screen.dart, incoming_requests_section.dart, approve_link_sheet.dart — AC: AC1, AC2, AC4, AC5, AC7, AC8 — xong khi: waiting khác accepted; không đổi quyền hoặc mặc định sharing; back/dismiss không approve.
- [ ] P7 [frontend] Tạo notifications/sound/settings và route, đổi entry S08 cần thiết — file: 3 màn profile mới, router.dart, profile_screen.dart — AC: AC1, AC2, AC9, AC10 — xong khi: chuyển màn/quay lại được, disabled control không lưu, logout callback/retry hiện có vẫn hoạt động.
- [ ] P8 [frontend] Cập nhật privacy với dòng security chưa hỗ trợ và consent thật — file: privacy_settings_screen.dart — AC: AC1, AC2, AC5, AC7, AC8 — xong khi: grant/withdraw riêng, lỗi trả trạng thái cũ, không ẩn xác nhận hoặc gộp mục đích.
- [ ] P9 [frontend] Bổ sung/chỉnh test ở đúng 15 file cho điều hướng, request spy, disabled và render; review diff bảo toàn domain/data/state — file: toàn bộ test trong bảng — AC: AC1–AC10 — xong khi: target tests và analyze pass hoặc ghi fail có bằng chứng/baseline, không sửa kỳ vọng nghiệp vụ để bỏ lỗi.
- [ ] P10 [frontend] Chạy hồi quy liên quan, đối chiếu ảnh 375×812 và layout 320/textScale 2.0/keyboard, scope/diff-check, cập nhật 04 — file: bảng file test, work/task/evidence và 04 — AC: AC1–AC10 — xong khi: mọi màn có kết quả đạt/chưa đạt cụ thể, scope checkout pass, không Critical/High mới chưa xử lý; dừng chờ duyệt implement.

## 5. Test

### Unit / widget (làm trong implement)

| ID, test dự kiến | AC | Nơi chứa |
|---|---|---|
| T1 personal/medical render with real values; validation/save payload unchanged; unimplemented fields disabled, empty != confirmed none | AC1, AC2, AC6 | profile_screens_test.dart, profile_flow_visual_test.dart |
| T2 every profile flow screen remains reachable at 320px, scale 2.0, long names and keyboard; buttons reachable with bottom inset | AC1, AC8 | profile_layout_test.dart, profile_flow_visual_test.dart |
| T3 QR/link payload exactly from repository; loading/error/consent deny; no expiry or refresh-code behavior; share/copy existing callbacks | AC2, AC3, AC7 | family_link_code_screen_test.dart, share_invite_link_screen_test.dart; chạy lại family_link_code_security_test.dart/stability_test.dart không sửa |
| T4 repeated QR detected once, denied/permanent-denied permission fallback; invalid/rate-limited submit; waiting has no patient identity, accepted no implicit sharing | AC4, AC7, AC8 | scan_link_qr_screen_test.dart, enter_link_code_screen_test.dart, invite_link_flow_test.dart; chạy controller/message tests hiện có |
| T5 real caregiver id and sharing, revoke cancel/confirm/busy; request approve/reject/close; grant/withdraw each consent and rollback on failure | AC4, AC5 | caregivers_screen_test.dart, incoming_requests_test.dart, consent_confirmation_screen_test.dart, privacy_settings_screen_test.dart |
| T6 UI-only screens disabled controls make no repository calls, no success snackbar; all navigation entries and back; legal links use real routes | AC2, AC10 | profile_flow_navigation_test.dart, app_shell_test.dart |
| T7 first load vs error vs denied/401 cleanup; no cached QR/health data shown after denial, correct retry | AC3, AC5, AC7 | test hiện có trong profile/family/family_link/consent; bổ sung assertion ở file đã cho phép, không sửa controller |
| T8 S08 card/menu/navbar retained after route changes; settings logout invokes original callback, busy/retry/no duplicate call | AC9, AC10 | profile_flow_navigation_test.dart, app_shell_test.dart; chạy lại profile_logout_retry_test.dart và profile_app_lifecycle_test.dart |
| T9 diff/scope only approved UI/route/tests; baseline inherited S08 preserved | AC9 | git diff --check, scope.py trong checkout, kiểm diff domain/data/state/backend rỗng |

- Chạy Flutter test các thư mục `test/features/profile`, `test/features/family_link`, `test/features/family`, `test/features/consent` và `test/app/app_shell_test.dart`; sau đó test toàn mobile một lần nếu target đã ổn để phát hiện ảnh hưởng widget dùng chung. Không coi baseline fail là pass.
- SDK hiện có `D:/Captone/flutter`; có thể gọi dart + flutter_tools.snapshot trực tiếp như task S08 nếu flutter.bat vẫn treo. Dùng task-local PUB_CACHE, không sửa lockfile hoặc dependencies. Flutter analyze theo file đã thay; ghi rõ cảnh báo kế thừa.
- Nếu fixture dùng font thay thế hoặc widget render thiếu UI hệ điều hành, báo rõ trong evidence; không dùng ảnh đó để kết luận font thiết bị thật đã khớp.

### Tích hợp / thủ công ở giai đoạn test

| Kiểm tra | AC / kịch bản chất lượng | Phạm vi và bằng chứng |
|---|---|---|
| UI gọi repository bằng spy và chạy regression quyền đã có | AC3–AC7; thu hồi/consent/mất phiên | Widget test không được gọi là tích hợp API+DB. |
| Nếu môi trường Backend+DB có sẵn: request ngay sau rút family_sharing/gỡ liên kết và truy cập chéo patient | AC5, AC7; QA 403 và access_logs denied | Chạy kịch bản integration hiện có trong backend/tests/integration hoặc tests, không thêm/sửa backend/test tích hợp ngoài phạm vi. Ghi exact command và log. Nếu chưa xác định test/env, ghi chưa chạy/Pending, không suy từ widget pass. Không reset DB hay thay dữ liệu ngoài môi trường test đã xác nhận. |
| Thiết bị thật: scanner/camera, system share, clipboard, safe area, bàn phím, chữ lớn và logout | AC3, AC8, AC10 | Manual, lý do plugin/OS không được xác minh đầy đủ bằng widget. Chưa có thiết bị thì Pending. |
| So Figma từng màn, overlay, nhiều/một/rỗng, error/loading và placeholder | AC1, AC2, AC8 | Ảnh cùng viewport; kiểm scrim, lớp nền, góc sheet, nút và lối thoát; ghi sai khác nghiệp vụ được phép riêng. |
| Workbook | Toàn bộ AC | wf-testcase cuối test; lấy docs main mới nhất, ghép đúng module hiện có (PROFUI cho hồ sơ; kiểm mapping module người giám sát), không overwrite kết quả hay tạo sheet trùng. |

Không có file tích hợp mới dự kiến. Nếu phát hiện cần sửa endpoint/PEP hoặc test server để thay nghiệp vụ, dừng và mở rộng requirement/plan theo quy trình.

## 6. Migration

Không có. Không đổi schema, backend, endpoint hoặc contract.

## 7. Nhánh git

| Repo | Nhánh / vị trí |
|---|---|
| Superproject cô lập | feat/adhoc-20261118-mobile-profile-flow-ui tại work/task/scratch/workspace |
| frontend cô lập | feat/adhoc-20261118-mobile-profile-flow-ui; baseline đã kiểm 81566509 + patch S08 |
| docs nếu merge workbook cuối test | feat/adhoc-20261118-mobile-profile-flow-ui từ main mới nhất, checkout cô lập riêng; không sửa docs root detached |

Không commit/push/PR trong plan hoặc tự động khi implement xong. Giữ checkout S08 và root nguyên vẹn. Khi người dùng yêu cầu commit sau này, tách rõ diff kế thừa và task mới; submodule trước, superproject sau, không bump SHA chưa push.

## 8. Rủi ro

- Figma chứa trạng thái/timer/dữ liệu không được backend cung cấp: dùng ma trận sai khác ở mục 1; disabled và nhãn rõ thay control giả, test request count 0.
- Approve thành công không có nghĩa sharing=true: giữ controller và copy mô tả; test trạng thái theo dữ liệu, không tự bật switch.
- UI consent có nhiều thông tin hơn Figma: giữ đầy đủ nội dung bắt buộc, cho cuộn, không rút gọn để vừa frame.
- Thay widget shared có thể ảnh hưởng tab Người thân hoặc onboarding: giới hạn vào widget riêng/optional style, chạy regression callers; không sửa global theme.
- S08 chưa commit và root bẩn: dùng clone task mới, copy đúng patch đã xác minh, scope tại checkout; không dọn workspace. Ghi vị trí code thật trong bàn giao.
- Baseline S08 từng có hai profile lifecycle test fail do login overflow/timeout, full suite có fail chưa phân loại hết: tái kiểm trong phiên implement, ghi baseline đối chiếu nếu còn; không sửa login ngoài phạm vi hoặc khẳng định toàn bộ lỗi là có sẵn.
- Workbook docs baseline cũ có nguy cơ mất các sheet mới: không dùng workbook scratch của S08 làm nguồn merge; đọc main hiện có và giữ ID/kết quả cũ.

## 9. Câu hỏi mở

Không có câu hỏi chặn. Các khác biệt để giữ nghiệp vụ và điều khiển chưa khả dụng nằm trong requirement đã duyệt và được cụ thể hóa ở đây; thay đổi mới ngoài ma trận phải báo trước khi sửa.

## 10. Phát sinh

- Root scope requirement báo 1657 file ngoài phạm vi; không thuộc thay đổi trong task. Plan chỉ ghi work/task. Tiếp tục ghi log scope root trung thực; implement bắt buộc checkout cô lập sạch để kiểm delta.
- Kiểm cuối plan: gate plan pass; bảng phạm vi đã đếm đúng 40 hàng (25 sản phẩm, 15 test/helper). Scope plan exit 1 với nguyên văn: “CHẶN: 1657 file ngoài phạm vi. Ghi vào mục 'Phát sinh' và hỏi người dùng.” Danh sách kế thừa từ workspace đã ghi ở requirement, không dọn/xóa để vượt kiểm tra. Việc duyệt plan bao gồm phương án checkout cô lập P1, sau đó scope delta ở checkout phải pass; chưa có code hoặc test sản phẩm nào được chạy/sửa ở plan.
- Không sửa draft S08-2 cũ, không chạy task đó song song vào cùng medical_profile_screen.dart.

## Bước tiếp theo

- Chờ duyệt plan: `python .agents/scripts/gate.py approve adhoc-20261118-mobile-profile-flow-ui plan`.
- Sau duyệt đọc wf-implement, chạy gate implement và bắt đầu P1. Chưa sửa code sản phẩm, tạo nhánh hoặc ghi submodule ở giai đoạn này.
- Evidence: evidence/plan-gate.log; evidence/plan-scope.log (root có thay đổi kế thừa; không coi pass nếu script báo lỗi).
- Cập nhật: 2026-11-18, Codex.
