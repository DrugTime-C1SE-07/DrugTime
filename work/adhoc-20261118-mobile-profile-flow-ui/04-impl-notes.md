---
task: adhoc-20261118-mobile-profile-flow-ui
stage: implement
owner: Ngọc Việt
started_at: 2026-11-18 10:50
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-18 11:35 +0700
content_hash: sha256:e82aa19b16b30fc7
inputs:
  01-requirement.md: sha256:c338df6345d3cc26
  03-plan.md: sha256:0145eb93e75e6160
---

# Implement UI Hồ sơ & Người thân

## 1. Tiến độ

| Bước | Trạng thái | Kiểm tra / kết quả | Evidence |
|---|---|---|---|
| P1 | xong | Clone local frontend 81566509, nhánh task; kế thừa 5 file S08, root/checkout cũ không đổi | implement-P1.log, inherited-s08.patch, implement-git-final.log |
| P2 | xong | Đọc layer/ảnh 27 frame và biến thể/overlay, tạo widget UI chung không API; JSON nguồn lưu lại | figma-primary.json, figma-settings-health-states.json, figma-caregiver-states.json |
| P3 | xong | Personal/medical/sheet: giữ validation/generation/save/delete; placeholder rõ; font và avatar căn cuối | implement-layout-final.log — 60 pass |
| P4 | xong | Thẻ/count thật, sharing/thu hồi, empty và hub; giữ id/cancel/busy | implement-focused-pass.log — 147 pass |
| P5 | xong | Hub/QR/link/scan/nhập mã; giữ payload/camera/parser, không timer/hủy giả; nhóm QR/share căn cuối | implement-focused-pass.log, implement-layout-final.log |
| P6 | xong | Request/consent/outcome thật, không tự bật sharing; sửa overflow header thẻ/footer/sheet khi chữ lớn | implement-focused-pass.log, implement-layout-final.log |
| P7 | xong | Notification/sound/settings và 4 route; thiếu capability disabled; logout callback thật, giữ retry | implement-focused-pass.log |
| P8 | xong | Privacy giữ consent riêng, thêm dòng bảo mật chưa hỗ trợ | implement-focused-pass.log |
| P9 | xong | Test UI, API boundary diff, analyze; không đổi domain/data/state/backend/contract | implement-focused-pass.log, implement-api-boundary.log, implement-analyze-delivery.log |
| P10 | xong phần implement | Toàn mobile/baseline, so lỗi, ảnh, scope/diff-check; manual thiết bị/integration để test stage | implement-final-frontend.log, implement-baseline-full.log, failure-comparison.json, implement-scope-final.log |

Các đường dẫn evidence trong bảng nằm trong thư mục evidence của task. Không sửa 01/03 đã approved.

## 2. File đã thay đổi

**Code thật:** D:/Captone/DrugTime/work/adhoc-20261118-mobile-profile-flow-ui/scratch/workspace/frontend.
Nhánh feat/adhoc-20261118-mobile-profile-flow-ui, HEAD nền 8156650965a4f4bebe60b84ec4568ba3e8810195.
Chưa commit/push. Frontend gốc và checkout S08 cũ không được ghi.

31 file: 24 sản phẩm, 7 test, gồm 5 file kế thừa S08; không cần sửa hết 40 file được phép.
AppShell kế thừa S08 và format. ProfileScreen chỉ đổi entry notifications/settings, giữ logout.
Mở Notifications thuần UI không tự load profile khi quay về.

| Submodule | Đường dẫn tính từ frontend/mobile |
|---|---|
| frontend | lib/app/app_shell.dart |
| frontend | lib/app/router.dart |
| frontend | lib/features/consent/presentation/screens/privacy_settings_screen.dart |
| frontend | lib/features/family/presentation/screens/family_link_code_screen.dart |
| frontend | lib/features/family_link/presentation/screens/caregivers_screen.dart |
| frontend | lib/features/family_link/presentation/screens/enter_link_code_screen.dart |
| frontend | lib/features/family_link/presentation/screens/link_consent_confirmation_screen.dart |
| frontend | lib/features/family_link/presentation/screens/link_request_result_screen.dart |
| frontend | lib/features/family_link/presentation/screens/scan_link_qr_screen.dart |
| frontend | lib/features/family_link/presentation/screens/share_invite_link_screen.dart |
| frontend | lib/features/family_link/presentation/widgets/approve_link_sheet.dart |
| frontend | lib/features/family_link/presentation/widgets/incoming_requests_section.dart |
| frontend | lib/features/profile/presentation/screens/medical_profile_screen.dart |
| frontend | lib/features/profile/presentation/screens/personal_profile_screen.dart |
| frontend | lib/features/profile/presentation/screens/profile_screen.dart |
| frontend | lib/features/profile/presentation/widgets/avatar_picker_sheet.dart |
| frontend | lib/features/profile/presentation/widgets/condition_catalog_sheet.dart |
| frontend | lib/features/profile/presentation/widgets/condition_editor_sheet.dart |
| frontend | lib/features/profile/presentation/widgets/profile_icons.dart |
| frontend | test/app/app_shell_test.dart |
| frontend | test/features/consent/privacy_settings_screen_test.dart |
| frontend | test/features/family_link/share_invite_link_screen_test.dart |
| frontend | test/features/profile/profile_layout_test.dart |
| frontend | test/features/profile/profile_screens_test.dart |
| frontend | lib/features/family_link/presentation/screens/invite_caregiver_screen.dart |
| frontend | lib/features/profile/presentation/screens/notification_preferences_screen.dart |
| frontend | lib/features/profile/presentation/screens/profile_settings_screen.dart |
| frontend | lib/features/profile/presentation/screens/reminder_sound_screen.dart |
| frontend | lib/shared/widgets/profile_flow_widgets.dart |
| frontend | test/features/profile/profile_flow_navigation_test.dart |
| frontend | test/features/profile/profile_flow_visual_test.dart |

Scope checkout: OK — implement-scope-final.log.
git diff --check exit 0 — implement-diff-check.log.
Không có diff domain/data/state/pubspec — implement-api-boundary.log. Không sửa backend/contract.

## 3. Kết quả test cuối

| Phạm vi | Pass / Fail / Skip | Evidence |
|---|---|---|
| Toàn mobile triển khai, trước vài chỉnh font/nhóm QR/share/fixture cuối | 1133 / 82 / 2 | implement-final-frontend.log |
| Toàn mobile baseline sạch 81566509, chạy trong phiên | 1098 / 82 / 2 | implement-baseline-full.log |
| So danh sách test lỗi toàn suite | Cả 82 tên lỗi trùng nhau; only_current=[], only_baseline=[] | failure-comparison.json |
| Sáu file baseline liên quan (profile lifecycle, family tab/redeem/invite/code stability/adherence) | 21 / 8 / 0 | implement-baseline-comparison.log |
| 14 file UI/regression liên quan | 147 / 0 / 0 | implement-focused-pass.log |
| Sau chỉnh font cá nhân | 52 / 0 / 0 | implement-font-final.log |
| Sau căn cuối avatar, QR, nhóm chia sẻ | 60 / 0 / 0 | implement-layout-final.log |
| Analyze 31 file thay đổi | 0 error; warning/info còn lại xem log | implement-analyze-delivery.log |
| Scope / whitespace | Pass | implement-scope-final.log, implement-diff-check.log |

Cwd: scratch/workspace/frontend/mobile. Lệnh thực tế gọi D:/Captone/flutter/bin/cache/dart-sdk/bin/dart.exe và D:/Captone/flutter/bin/cache/flutter_tools.snapshot --suppress-analytics.
Toàn mobile: test --no-pub --reporter expanded.
Baseline cùng lệnh tại scratch/baseline-frontend/mobile.
PUB_CACHE: cache đã có của S08 ở work/adhoc-20261118-mobile-profile-s08-ui/scratch/pub-cache; không đổi manifest/lockfile.

Lượt 147 ca: test --no-pub --reporter expanded với:
- test/features/profile/profile_flow_navigation_test.dart
- test/features/profile/profile_flow_visual_test.dart
- test/features/profile/profile_layout_test.dart
- test/features/profile/profile_screens_test.dart
- test/features/profile/profile_screen_test.dart
- test/features/family_link/caregivers_screen_test.dart
- test/features/family_link/scan_link_qr_screen_test.dart
- test/features/family_link/share_invite_link_screen_test.dart
- test/features/family_link/incoming_requests_test.dart
- test/features/family_link/consent_confirmation_screen_test.dart
- test/features/family_link/enter_link_code_screen_test.dart
- test/features/family/family_link_code_screen_test.dart
- test/features/consent/privacy_settings_screen_test.dart
- test/app/app_shell_test.dart
- define FLOW_CAPTURE_DIR=<task>/evidence/renders.

Lượt 60 ca sau cùng: profile visual/layout/screens + family code screen + share screen, cùng define.
Analyze: analyze --no-pub với danh sách evidence/changed-dart-files.txt.
So lỗi: python -X utf8 -B scratch/compare_failures.py.
Không cộng pass giữa các lượt có ca lặp.

**Giới hạn:** toàn dự án chưa xanh. Danh sách 82 lỗi khớp baseline, không có tên lỗi mới ở lượt toàn suite đã đối chiếu; không khẳng định đã sửa hoặc xác định nguyên nhân mọi lỗi nền. Điều chỉnh UI sau lượt toàn suite đã được kiểm lại ở nhóm liên quan; không tuyên bố full suite chạy lại trên byte cuối. Chưa chạy thiết bị thật, camera/share sheet OS hoặc Backend+DB integration; để Pending giai đoạn test.

### Truy vết nghiệp vụ / AC

| Quy tắc và trạng thái nguồn | Thực hiện | Bằng chứng / AC |
|---|---|---|
| QD-04/34 ✅, BS-05 🆕: mã cố định, QR thật, consent lấy mã | Không timer/refresh giả, giữ code.qrPayload, parser và callback share | code/share/scan tests — AC3, AC4 |
| QD-27/28/29/30 ✅: sharing/consent/liên kết/thu hồi | Giữ switch, ID, xác nhận, busy; success không bật sharing; không sửa state/cache | caregiver/confirmation/privacy tests — AC4, AC5, AC7; lỗi lifecycle nền ghi riêng |
| QD-31 ✅: grant/withdraw riêng | Giữ đủ ba mục đích, xác nhận rút và rollback lỗi | privacy/incoming/consent — AC5 |
| CS-01/04 ⏳ theo nguồn; bắt buộc theo AGENTS | Không đổi endpoint/PEP/Access Log, không Supabase trực tiếp hoặc request cho placeholder | diff boundary, scope — AC7, AC9; integration chưa chạy |
| Thiếu dữ liệu không phải xác nhận không có bệnh | Placeholder/disabled cho trường thiếu; không suy empty thành confirmed none | profile widget/layout — AC2, AC6 |
| Chỉ đổi UI | Route thuần điều hướng; control thiếu không ghi/lưu hoặc báo thành công; logout callback hiện có | navigation và diff — AC2, AC9, AC10 |

Giữ trạng thái quyết định theo bảng nguồn mục 8–9 trong 01/03, không tự chốt điểm còn mở.

## 3b. Bộ test case Excel

Task M: làm ở giai đoạn test theo wf-testcase, chưa tạo/merge workbook.
Dùng docs main mới nhất và module hiện có (PROFUI / module người giám sát), không lấy workbook baseline cũ S08 để ghi đè.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Xem code tại checkout nêu trên; root frontend vẫn không chứa thay đổi task.
- 14 ảnh ở evidence/renders: widget render 375×812, safe area 44/34, pixelRatio 2; Segoe UI thay font runtime, không có status/home indicator OS. Camera là fixture.
- Cỡ chữ lớn test ở 320×640, scale 2.0: header giãn, footer consent xếp dọc, scanner và sheet cuộn được. Bóng bật riêng khi capture, khôi phục trong finally trước invariant.
- Personal bỏ LIÊN HỆ, phone chỉ đọc; chiều cao/cân nặng không dữ liệu minh họa. Medical lưu bệnh nền từng thao tác, CTA toàn màn disabled và có giải thích. Các trạng thái no-allergy/no-condition/both-confirmed không kích hoạt khi thiếu nguồn thật.
- Caregiver giữ ngày chấp thuận/switch thật, không giả quan hệ con trai/con gái. Các biến thể 1/2 người kiểm bằng widget nghiệp vụ, đối chiếu ảnh chi tiết tiếp ở test.
- Result theo outcome thật, dùng mascot có sẵn; không tên patient/hủy request giả hoặc khẳng định sharing đã bật. Consent giữ đủ nội dung và bước xác nhận nên dài hơn Figma.
- Notifications/sound/settings/privacy có dòng chưa khả dụng theo phê duyệt; không giả 70%, số thiết bị hoặc phiên bản. Legal links có route thật.
- Capture settings là direct entry nên thiếu callback logout và disabled; entry từ S08 truyền callback thật đã test. Mã/link thật; nút share dùng system sheet, Zalo/SMS/Email shortcut chưa khả dụng.
- Sheet nền trắng/bo góc trên 24/safe area; giữ catalog/editor/avatar thật. Chưa kết luận trải nghiệm native.
- Không commit/push/PR; chỉ đề xuất commit artifact khi người dùng yêu cầu.

## 6. Phát sinh

- Root bẩn kế thừa, không dọn; scope checkout sạch.
- Formatter từng chạm health_setup_matches_test.dart, đã phục hồi đúng nội dung/line ending từ HEAD; không còn delta, scope cuối pass.
- Log lượt đầu có lỗi fixture/font/restore shadow, tên file test không tồn tại và kỳ vọng UI cũ. Giữ log trung thực, chỉ dùng các lượt pass ở bảng làm bằng chứng đạt.
- Lượt analyze từ tài khoản escalated bị Git dubious ownership và phân tích toàn mobile thay vì file list. Không đổi safe.directory toàn cục; đã tạo danh sách trong sandbox thường và chạy lại scoped. Dùng implement-analyze-delivery.log.
- Không phát sinh cần đổi API/AC hoặc file ngoài bảng.

## Bước tiếp theo

- Chờ duyệt: python .agents/scripts/gate.py approve adhoc-20261118-mobile-profile-flow-ui implement.
- Sau duyệt mới chạy gate test và wf-test, kiểm thiết bị/ảnh/integration khả dụng và workbook. Không tự bắt đầu test stage trong lượt này.
- Cập nhật 2026-11-18, Codex.
