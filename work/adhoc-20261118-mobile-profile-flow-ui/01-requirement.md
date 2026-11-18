---
task: adhoc-20261118-mobile-profile-flow-ui
title: Áp dụng Figma cho các màn còn lại của luồng Hồ sơ & Người thân
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-18 10:42 +0700
content_hash: sha256:c338df6345d3cc26
---

# Đồng bộ các màn con của luồng Hồ sơ & Người thân

## 1. Mục tiêu

Đưa UI Flutter của các màn còn lại trong luồng ⑧ Hồ sơ & Người thân về thiết kế Figma đã chốt, tiếp nối S08 đã hoàn thành. Các trường dữ liệu, API và nghiệp vụ hiện hành giữ nguyên; màn hoặc trường chưa được hỗ trợ vẫn có giao diện nhưng phải thể hiện rõ chưa khả dụng.

## 2. Phạm vi

### Trong phạm vi

| Figma — file Prototype_DrugTime, Page 1 | Node | Đối chiếu code / yêu cầu |
|---|---|---|
| S08-1 · Thông tin cá nhân | 51:5527 | PersonalProfileScreen, avatar, biểu mẫu, lưu và trạng thái lỗi. Chỉ các trường ProfileDraft hiện hỗ trợ được sửa/lưu. |
| S08-2 · Hồ sơ sức khỏe | 51:5645 | MedicalProfileScreen, danh mục và sheet bệnh nền; dùng bản Figma vừa chỉnh nền #F5F7F6, thẻ trắng, màu chọn dịu và bóng nhẹ. |
| Các trạng thái S08-2 không dị ứng / không bệnh / cả hai / chưa khai báo | 804:11697, 804:11862, 804:12027, 804:12192 | Chỉ render trạng thái khi có nguồn dữ liệu thật tương ứng. Nếu chưa có thì hiển thị chưa khả dụng; không suy từ danh sách rỗng. |
| S08-2 · Thêm dị ứng / Thêm bệnh nền | 804:12369, 804:12389 | Sheet bệnh nền giữ lưu trực tiếp hiện có. Phần dị ứng chưa hỗ trợ không gửi request hoặc giả lưu. |
| S08-3 · Người giám sát | 51:5751 | CaregiversScreen, thẻ người thân, số lượng thật, chia sẻ, thu hồi và xác nhận thu hồi. |
| Biến thể còn một người / rỗng; dialog thu hồi từng người và người cuối | 804:12437, 804:12587, 804:12737; 804:12890, 804:12900, 804:12910, 804:12920 | Phụ thuộc dữ liệu và người được chọn thực; không hard-code tên Figma. |
| S08-3a · Mời người thân giám sát | 51:5847 | Bổ sung màn chọn cách kết nối; nối tới QR, quét và gửi link hiện có bằng điều hướng UI. |
| S08-3b · Mã QR của bạn | 51:5934 | FamilyLinkCodeScreen, giữ code và qrPayload thật. |
| S08-3c · Quét mã QR người thân | 51:6194 | ScanLinkQrScreen và lối nhập mã, giữ xin quyền camera/parse/gửi hiện có. |
| S08-3d · Đang chờ xác nhận | 51:6246 | LinkRequestResultScreen khi outcome waiting; không giả đã liên kết thành công. |
| S08-3e · Yêu cầu giám sát mới | 51:6288 | IncomingRequestsSection / ApproveLinkSheet / LinkConsentConfirmationScreen; giữ người nhận, phạm vi và xác nhận thực. |
| S08-3f · Đã thêm người giám sát | 51:6365 | UI kết quả thành công khi có outcome hoặc xác nhận thành công thực; nếu không có nguồn thì chưa khả dụng, không dựng thành công sau thao tác xem. |
| S08-3g · Gửi link mời | 51:6433 | ShareInviteLinkScreen, giữ nguồn link, sao chép và share sheet hiện có. |
| S08-4 · Thông báo & Nhắc nhở | 51:6534 | Dựng màn UI thay trang ComingSoon; điều khiển chưa có xử lý/lưu phải bị vô hiệu hóa và gắn nhãn chưa khả dụng. |
| S08-4a · Âm thanh nhắc nhở | 51:6677 | Dựng UI, điều hướng từ S08-4; chưa nối phát âm lượng, chọn âm hoặc lưu tùy chọn khi chưa có chức năng. |
| S08-5 · Cài đặt | 51:6784 | Dựng UI và đường vào phù hợp từ Hồ sơ; giữ đăng xuất hiện hành. Tùy chọn chưa có xử lý phải ghi rõ chưa khả dụng. |
| S08-6 · Quyền riêng tư & Bảo mật | 51:6981 | PrivacySettingsScreen, giữ mục đích consent thật và xác nhận rút; mục bảo mật chưa có xử lý thể hiện chưa khả dụng. |

- Bám Figma về typography, khoảng cách, icon, màu, góc bo, độ nổi khối, header và safe area. Đọc ảnh/layer chi tiết từng màn, overlay và component trước khi triển khai màn đó; danh sách trên mới là kiểm kê phạm vi, chưa phải bằng chứng tất cả màn đã được đo đầy đủ.
- Giữ nút và thông báo đang tải, lỗi, thử lại, khóa thao tác đang gửi, xử lý mất phiên và quyền hiện hành. Bổ sung nhãn khả dụng bằng tiếng Việt, không đưa chi tiết API vào UI.
- Nút lưu chỉ lưu các trường thật đang được hỗ trợ. Màn chỉ có điều khiển chưa khả dụng không có nút lưu hoạt động. MedicalProfileScreen đang lưu trực tiếp qua sheet: không thêm bản nháp toàn màn hoặc request mới để bắt chước nút lưu Figma; nút lưu toàn màn nếu thể hiện phải vô hiệu hóa và giải thích ngắn.
- Cho cuộn khi màn hẹp, bàn phím hoặc chữ lớn. Không cố ép tất cả nội dung vào chiều cao cố định gây đè/cắt.
- Tái sử dụng thay đổi S08 đã hoàn thành, chỉ thay điểm vào cần thiết để tới màn mới; không thiết kế lại S08. Xác minh checkout chứa S08 trước implement.

### Ngoài phạm vi

- Sửa Figma, backend, API contract, entity/mapper/repository/controller và quy tắc phân quyền hoặc lưu dữ liệu.
- Tạo dữ liệu mẫu như tên người thân, tình trạng đã xác nhận, nhóm máu, bác sĩ hoặc chiều cao/cân nặng để thay dữ liệu chưa có.
- Nối health setup onboarding sang hồ sơ chính, mở rộng chức năng dị ứng/khai báo không có bệnh, phát âm, lưu cài đặt, bảo mật đăng nhập hoặc xóa tài khoản.
- Thay đổi các màn onboarding S08a–S08e, frame lưu trữ cũ, tab Người thân ngoài phần dùng chung cần thiết cho luồng này, hoặc trợ giúp chưa có frame đích trong nhóm đã kiểm kê.
- Commit, push, tạo PR nếu người dùng chưa yêu cầu.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn | Điều rút ra |
|---|---|
| Reqwise search_nodes query S08 trong Prototype_DrugTime / Page 1 ngày 2026-11-18 | Xác minh các node và phân biệt nhóm màn hồ sơ với onboarding, bản lưu trữ. |
| Reqwise get_design_context S08-2, S08-3a và các màn 51:5527, 51:6981, 51:6534, 51:6677, 51:6784 | Xác minh cấu trúc phần sức khỏe, mời người thân, các nhãn và nhóm tính năng. Cần tiếp tục đo toàn bộ layer ở plan/implement. |
| Reqwise screenshot S08-2 sau chỉnh ở lượt trước, screenshot S08-3 ở lượt này | S08-2 có thẻ trắng trên nền xanh xám, màu chọn dịu; S08-3 thẻ người giám sát, trạng thái, thu hồi và mời người thân. |
| frontend/mobile/lib/app/router.dart; features/profile/presentation/screens/profile_screen.dart | Có route personal/medical/caregivers/privacy, QR/quét/link/kết quả; Thông báo vẫn ComingSoon; Cài đặt mới có menu đăng xuất. Root frontend chưa có thay đổi S08 ở checkout triển khai trước. |
| features/profile/domain/entities/health_profile.dart; data/repositories/remote_profile_repository.dart | Có fullName/dateOfBirth/gender/email/phone/conditions; phone chỉ đọc, không phải định danh đăng nhập; thiếu chiều cao/cân nặng/dị ứng/nhóm máu/bác sĩ trong HealthProfile. |
| features/profile/presentation/screens/personal_profile_screen.dart; medical_profile_screen.dart qua draft S08-2 đã có | Personal có form và lưu; bệnh nền lưu ngay qua sheet, không có bản nháp toàn màn. |
| features/family_link/presentation/screens/caregivers_screen.dart, scan_link_qr_screen.dart; kết quả rg share_invite_link_screen.dart/link_request_result_screen.dart | Giữ chia sẻ/thu hồi, xác nhận, consent; quét chuyển qua nhập mã và gửi; waiting khác success. |
| features/family/presentation/screens/family_link_code_screen.dart | QR lấy từ code.qrPayload của controller thật; có loading/error/retry. |
| features/consent/presentation/screens/privacy_settings_screen.dart | Mỗi mục đích có grant/withdraw riêng, xác nhận khi rút, đang gửi khóa thao tác. |
| features/family_link/data/repositories/remote_caregiver_repository.dart, remote_family_link_repository.dart; features/family/data/repositories/remote_family_link_code_repository.dart; features/consent/data/repositories/remote_consent_repository.dart | Các endpoint hiện có cần giữ nguyên; không thêm request cho UI chưa khả dụng. |
| work/adhoc-20261118-mobile-profile-s08-ui/06-review.md; work/adhoc-20261118-mobile-health-profile-s08-2-ui/01-requirement.md | S08 đã hoàn tất quy trình; draft S08-2 chưa duyệt, phạm vi hẹp hơn và giờ được bao gồm trong task này. Không triển khai song song hai task vào cùng file. |
| AGENTS.md; .agents/skills/wf-next, wf-requirement; C:/Users/VietD/.codex/skills/figma-ui-code/SKILL.md | Chỉ ghi artifact trước implement, qua cổng duyệt mỗi giai đoạn; giữ thiết kế làm nguồn chuẩn và ghi rõ sai khác nghiệp vụ. |

Các đường dẫn features ở bảng tính từ frontend/mobile/lib/. Figma: https://www.figma.com/design/aBPUpNPZIXqE44D1Gx8gaJ/Prototype_DrugTime?node-id=51-5527 .

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Có | Các màn/widget UI mobile, route thuần điều hướng, tài nguyên và widget test liên quan. |
| backend, api_contract, tests, .agents | Không | Không đổi chức năng backend hoặc hợp đồng. |
| docs | Chưa có thay đổi sản phẩm | Workbook test tổng được xử lý theo wf-testcase cuối test; phải lấy docs mới nhất và gộp vào PROFUI hiện có để tránh trùng module như lưu ý review S08. |

## 5. Thay đổi API contract

- contract_change: no. Không đổi URL, method, payload/response, ý nghĩa trường, xác thực hoặc mã lỗi. UI chỉ gọi các callback và nguồn dữ liệu hiện có.
- Endpoint đang dùng: GET/PUT /profile; GET /conditions; POST /profile/conditions; PATCH/DELETE /profile/conditions/{id}; GET /family/link-code; POST /family/link-requests; GET /family/links?status=pending; GET /family/caregivers; POST /family/links/{id}/approve và /reject; PATCH /family/links/{id}/sharing; DELETE /family/links/{id}; GET/POST /consents; POST /consents/{purpose}/withdraw.
- Không bổ sung API để lấp chỗ trống của Figma. Chi tiết nguồn chia sẻ link và route sẽ đối chiếu thêm ở plan, giữ hành vi hiện hành.

## 6. Vùng rủi ro và bất biến bị chạm

- Dữ liệu sức khỏe: màn cá nhân/sức khỏe/QR có dữ liệu thật, không dùng dữ liệu mẫu hoặc mở rộng quyền; vẫn Backend API, không gọi Supabase trực tiếp.
- Phân quyền người thân: giữ xác nhận, consent, chia sẻ và thu hồi thực. Không để nhãn xanh hoặc màn thành công xuất hiện trước kết quả xác nhận thực; không bỏ điều khiển chia sẻ hiện hành chỉ vì Figma chưa thể hiện.
- Bảo toàn auth và xử lý 403/401; UI không biến tải lỗi/từ chối thành danh sách rỗng hoặc hiển thị mã/hồ sơ cũ.
- Không đổi endpoint/PEP/access log; hồi quy UI là cần thiết nhưng không thay bằng chứng kiểm quyền phía server nếu thực tế phát sinh đổi nghiệp vụ (khi đó dừng, mở rộng phạm vi).

## Quyết định nghiệp vụ áp dụng

Nguồn: docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md, baseline QD-2026-10-03-v1; mục 8 và 9 đã đọc trong phiên. ✅ là đã chốt theo nguồn, không đồng nghĩa đã triển khai hoặc Mentor đã ký; 🆕 là bổ sung, giữ nguyên trạng thái này.

| Quy tắc | Trạng thái nguồn | Áp dụng và truy vết |
|---|---|---|
| QD-04, QD-34: mã cố định không hết hạn, 10 ký tự, nhập chỉ tạo yêu cầu, bệnh nhân chấp thuận mới liên kết | ✅ | QR/code giữ payload thật; không thêm đồng hồ hết hạn hoặc khẳng định liên kết sau quét; AC3, AC4. |
| BS-04: quy tắc gửi lại sau từ chối theo bộ đếm cặp | 🆕, chốt 14/10/2026 | Giữ lỗi/khóa từ backend hiện hành, không tự dựng thời gian chờ mới; AC4, AC7. |
| BS-05: có family_sharing mới lấy/chia sẻ được mã | 🆕, chốt 14/10/2026 | Giữ chặn consent ở QR/link và cảnh báo hiện hành; AC3, AC5. |
| QD-27, QD-28: chỉ xem dữ liệu được chia sẻ, liên kết hoạt động + bật chia sẻ + consent còn hiệu lực | ✅ | Không mở thêm quyền; giữ công tắc chia sẻ thật, nội dung xác nhận và trạng thái đang gửi; AC4, AC5. |
| QD-29, QD-30: thu hồi có hiệu lực; liên kết lại cần yêu cầu mới, không tự khôi phục phạm vi | ✅ | Giữ cleanup, lỗi/khóa quyền và xác nhận thu hồi, không có thành công giả; AC5, AC7. |
| QD-31: grant/withdraw riêng theo mục đích, lịch sử chỉ thêm mới | ✅ | UI quyền riêng tư giữ các callback thật, không gộp consent thành một công tắc tổng; AC5. |
| CS-01, CS-04; bất biến 1/2/4 của AGENTS.md | ⏳ trong tài liệu nghiệp vụ; bắt buộc theo AGENTS.md | Không thay backend/đường truy cập, giữ từ chối 403; AC7, AC9. |

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given từng màn/overlay trong bảng phạm vi, When mở bằng entry point thực ở viewport Figma, Then bố cục, typography, màu, icon, bo góc và shadow khớp frame, khác biệt do dữ liệu/chức năng phải có ghi chú cụ thể. | Widget render + manual đối chiếu ảnh |
| AC2 | Given chức năng hoặc trường chưa có nguồn/xử lý, When mở màn, Then có nhãn chưa khả dụng dễ thấy, điều khiển không gửi request/không ghi dữ liệu/không báo thành công; không thay bằng dữ liệu mẫu. | Widget, kiểm callback/request |
| AC3 | Given mã/link thật và consent hợp lệ, When mở QR hoặc gửi link, Then render/sao chép/chia sẻ đúng payload hiện có; khi chưa consent hoặc tải lỗi thì giữ cảnh báo và thử lại, không lộ mã cũ. | Widget |
| AC4 | Given quét/nhập mã hoặc nhận yêu cầu, When gửi và chấp thuận/từ chối, Then giữ validate, chống gửi lặp, phân biệt waiting/success/error và phạm vi xác nhận; không tự liên kết chỉ bằng điều hướng. | Widget hồi quy |
| AC5 | Given người giám sát hoặc từng mục đích consent, When đổi chia sẻ/thu hồi/rút đồng ý, Then giữ xác nhận, khóa khi gửi, gọi đúng callback với id/purpose thật và xử lý lỗi như cũ; hủy dialog không gửi. | Widget hồi quy + review diff |
| AC6 | Given sửa thông tin cá nhân hoặc bệnh nền, When lưu/thêm/sửa/xóa, Then chỉ dùng field/payload và cơ chế lưu hiện có, giữ validation, read-only phone và thông báo; không gửi trường chưa hỗ trợ hay tạo nút lưu giả. | Widget hồi quy + kiểm diff |
| AC7 | Given đang tải, lỗi mạng, hết phiên hoặc 403, When mở/làm mới/thao tác, Then giữ trạng thái lỗi/thử lại/khóa hoặc cleanup hiện hành, không hiển thị empty/success như dữ liệu hợp lệ. | Widget hồi quy |
| AC8 | Given màn 320 px, chữ lớn, dữ liệu dài, bàn phím hoặc safe area, When cuộn/chạm/quay lại, Then không đè/cắt, thao tác khả dụng tới được và có vùng chạm tối thiểu 48 px; scanner giữ lối nhập mã khi từ chối camera. | Widget layout + manual thiết bị |
| AC9 | Given diff cuối task, When review, Then không đổi backend/contract/entity/mapper/repository/controller hay quy tắc quyền, không mất thay đổi S08 đã duyệt; chỉ điều hướng/UI và kiểm thử được thay theo plan. | Review diff + scope |
| AC10 | Given các màn UI mới, When đi từ Hồ sơ qua Thông báo/Âm thanh/Cài đặt/Mời người thân và quay lại, Then mở đúng màn, không dead-end; đăng xuất thật vẫn qua cơ chế đang có. | Widget điều hướng + manual |

## 8. Câu hỏi mở

Không có câu hỏi chặn. Người dùng đã chọn: “Dựng thêm các màn UI còn thiếu, đánh dấu chức năng chưa khả dụng”. Sai khác UI bắt buộc để giữ nghiệp vụ đã ghi ở phần phạm vi và AC; nếu phát hiện thêm trong plan, ghi riêng để duyệt trước implement.

## 9. Giả định

- Yêu cầu là code Flutter theo Figma, không sửa Figma.
- Nhóm màn còn lại là các màn con S08-1 đến S08-6 cùng biến thể/overlay trong nhóm ⑧, không gồm onboarding hay frame lưu trữ.
- Kiến trúc lưu và dữ liệu hiện có có ưu tiên hơn nội dung minh họa Figma; không khẳng định số điện thoại dùng đăng nhập vì code xác định đó là số liên hệ.

## 10. Phát sinh

- Draft adhoc-20261118-mobile-health-profile-s08-2-ui chưa duyệt nay nằm trong phạm vi task này; tạm không triển khai riêng, không sửa artifact đó.
- S08 đã duyệt còn ở work/adhoc-20261118-mobile-profile-s08-ui/scratch/scope-baseline/frontend theo bàn giao; root frontend vẫn có UI S08 cũ khi đọc phiên này. Plan phải xác minh Git và kế thừa thay đổi, không ghi đè.
- Workspace gốc có thay đổi từ task khác; scope đầu phiên được ghi bằng log, không dọn hoặc sửa những file đó để làm scope pass.
- Kiểm tra thực tế cuối requirement: gate requirement exit 0; scope requirement exit 1: “CHẶN: 1657 file ngoài phạm vi. Ghi vào mục 'Phát sinh' và hỏi người dùng.” Log đầy đủ ở evidence/requirement-scope.log. Danh sách gồm .agents, .claude, .specify, graphify-out, my-project, docs và frontend/admin/.test-build. Lượt này chỉ ghi thư mục work của task; không sửa các file được báo. Chưa đạt scope sạch tại root. Đề xuất ở plan dùng checkout cô lập và kế thừa S08, không dọn thay đổi người dùng; chưa chọn/ghi checkout trong requirement.
- Cần đối chiếu ảnh và layer chi tiết toàn bộ màn ở plan/implement, chưa tuyên bố đạt UI khi mới kiểm kê.

## 11. Size

- size: M: nhiều màn/widget trong một submodule sản phẩm, có dữ liệu sức khỏe và phân quyền người thân; không đủ điều kiện S.

## Bước tiếp theo

- Chờ người dùng duyệt requirement bằng lệnh: python .agents/scripts/gate.py approve adhoc-20261118-mobile-profile-flow-ui requirement.
- Sau duyệt mới lập plan, bảng file cụ thể, ma trận màn/trạng thái và checkout triển khai; chưa sửa code trong lượt requirement.
- Người duyệt xem lưu ý scope tại mục Phát sinh; đề xuất dùng checkout cô lập, bảo toàn workspace hiện tại.
- Bằng chứng: evidence/requirement-gate.log và evidence/requirement-scope.log.
- Cập nhật: 2026-11-18, Codex.
