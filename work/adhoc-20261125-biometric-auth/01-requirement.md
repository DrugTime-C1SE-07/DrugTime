---
task: adhoc-20261125-biometric-auth
title: Khóa ứng dụng bằng sinh trắc học (Face ID / vân tay)
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 16:53 +0700
content_hash: sha256:8b92aa54e07435ff
---

# adhoc-20261125-biometric-auth · Khóa ứng dụng bằng sinh trắc học (Face ID / vân tay)

## 1. Mục tiêu

Tính năng bổ sung, tùy chọn, tương tự "Khóa ứng dụng" của Messenger: người dùng đã đăng nhập (phiên vẫn giữ nguyên) có thể bật khóa trong Cài đặt. Khi đã bật, mỗi lần tắt app, chuyển app khác hoặc khóa màn hình điện thoại rồi quay lại, phải quét Face ID, vân tay hoặc nhập mã khóa màn hình của thiết bị mới xem được nội dung. Mục đích: chống xem trộm lịch uống thuốc, lịch sử liều, hồ sơ sức khỏe khi người khác cầm máy. Không phải đăng nhập lại OTP.

## 2. Phạm vi

### Phân tích phương án

| Phương án | Mô tả | Ưu | Nhược | Size |
|---|---|---|---|---|
| **A. App lock cục bộ** (đề xuất cho task này) | Phiên hiện có (JWT mobile, lưu Keychain/Keystore qua `flutter_secure_storage`) giữ nguyên. App hiện màn khóa khi khởi động và mỗi lần quay lại từ nền; mở bằng `local_auth` (Face ID, Touch ID, vân tay Android, fallback mật mã thiết bị). | Chỉ client, không đổi contract, không migration; dữ liệu sinh trắc không rời thiết bị (OS xử lý). | Chỉ là cổng UI: token vẫn đọc được bởi app khi máy đã mở khóa; không thay thế đăng nhập OTP sau khi phiên hết hạn (10 ngày). | M |
| B. Đăng nhập lại bằng sinh trắc (khóa thiết bị ký challenge / passkey) | Khi đăng ký thiết bị, sinh cặp khóa trong Secure Enclave/StrongBox, gửi public key lên backend; đăng nhập = ký nonce sau khi xác thực sinh trắc. | Thay OTP khi phiên hết hạn; server thu hồi được từng thiết bị. | Endpoint mới, bảng `device_credentials`, migration, đổi contract, vùng rủi ro Bí mật + Schema. | L |
| C. Gắn token với khóa yêu cầu sinh trắc | Mã hóa token bằng khóa Keystore/Keychain có access control `biometryCurrentSet` (plugin kiểu `biometric_storage`). | Token không giải mã được nếu chưa xác thực; vô hiệu khi đổi vân tay/khuôn mặt. | Plugin mới, xử lý mất khóa khi đổi sinh trắc, ảnh hưởng background sync (Worker nền cần token khi app khóa). | M |

Đề xuất: làm **A** ngay; ghi B và C thành task sau nếu capstone cần mức bảo mật cao hơn. C xung đột với đồng bộ nền và hành động trên thông báo (cần token khi app chưa mở khóa), nên không gộp vào A.

### Trong phạm vi (phương án A)

- Công tắc "Khóa ứng dụng" (Face ID / vân tay / mã khóa màn hình) trong màn Hồ sơ/Cài đặt; mặc định tắt; chỉ bật được khi thiết bị đã đặt khóa màn hình (`isDeviceSupported`).
- Bật công tắc phải xác thực sinh trắc thành công một lần.
- Màn khóa khi: khởi động lạnh (đã đăng nhập, đã bật khóa); quay lại app ngay sau khi app rời foreground (tắt app, chuyển app, khóa màn hình thiết bị). Không có thời gian chờ.
- Cách mở khóa: Face ID / Touch ID / vân tay, hoặc mã khóa màn hình của thiết bị (PIN/pattern/mật khẩu hệ thống, `biometricOnly: false`). Thiết bị không có sinh trắc nhưng có mã khóa màn hình vẫn bật được khóa. Nút "Đăng xuất" trên màn khóa để vào lại bằng OTP.
- Che nội dung khi app rời foreground (đã bật khóa): hiện lớp che (logo DrugTime) ngay khi app chuyển `inactive`, để ảnh chụp trong app switcher / màn đa nhiệm không lộ dữ liệu.
- Không tự khóa lại do hộp thoại hệ thống mà chính app mở (hộp thoại sinh trắc, quyền thông báo, camera/chọn ảnh OCR).
- Đăng xuất hoặc phiên 401 thì xóa cài đặt khóa cùng phiên.
- Cấu hình native: iOS `NSFaceIDUsageDescription`; Android quyền `USE_BIOMETRIC`, `MainActivity` chuyển sang `FlutterFragmentActivity` (yêu cầu của `local_auth`).
- Câu chữ tiếng Việt, hỗ trợ trình đọc màn hình.

### Ngoài phạm vi

- Phương án B và C (đăng nhập không OTP, mã hóa token bằng khóa sinh trắc).
- Backend, API contract, migration.
- Admin Web.
- Thu thập, lưu hay gửi dữ liệu sinh trắc (OS xử lý hoàn toàn; app chỉ nhận true/false).
- PIN riêng của app.
- Chặn chụp màn hình / quay màn hình (`FLAG_SECURE`): ảnh hưởng chia sẻ ảnh chụp; làm task riêng nếu cần.
- Tùy chọn thời gian chờ (1 phút, 15 phút, 1 giờ như Messenger): bản này khóa ngay; có thể bổ sung sau.
- Thay đổi cơ chế phiên mobile (10 ngày, không refresh).

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `frontend/mobile/pubspec.yaml` | Có `flutter_secure_storage ^10.3.4`, `http`; chưa có `local_auth`. |
| `frontend/mobile/lib/features/auth/data/sources/auth_session_store.dart` | Phiên lưu ở Keychain/Keystore, khóa `auth_session_v1`; có `MemoryAuthSessionStore` cho test. |
| `frontend/mobile/lib/features/auth/domain/entities/auth_session.dart` | Phiên gồm `accessToken`, `expiresAt`, `sessionType`, `profileComplete`; không có refresh token. |
| `frontend/mobile/lib/features/auth/presentation/state/auth_controller.dart:242` | 401 thì xóa phiên, về màn Đăng nhập. |
| `frontend/mobile/lib/core/api/api_client.dart:121` | Xử lý 401 tập trung. |
| `frontend/mobile/lib/app/app.dart:441`, `app/app_shell.dart:100` | Đã có `didChangeAppLifecycleState`; chỗ gắn logic khóa khi resume. |
| `frontend/mobile/android/.../MainActivity.kt:13` | Đang là `FlutterActivity`; `local_auth` cần `FlutterFragmentActivity`. |
| `frontend/mobile/ios/Runner/Info.plist` | Có `NSCameraUsageDescription`, chưa có `NSFaceIDUsageDescription`. |
| `backend/src/drugtime/modules/identity/application/sign_in.py:104` | Phiên mobile là JWT HS256, sống `mobile_session_days` (= 10, `shared/config.py:62`); không refresh, không thu hồi phía server. |
| `backend/src/drugtime/modules/identity/adapters/inbound/http.py` | `/auth`: OTP, complete profile, admin login/refresh, device token. Không cần endpoint mới cho A. |
| `docs` (git grep `biometric|sinh trắc|vân tay|face id`) | Không có kết quả trong file văn bản; file .docx/.xlsx chưa đối chiếu được bằng grep. |

### Quyết định nghiệp vụ áp dụng

Không áp dụng: không tìm thấy quyết định nào về sinh trắc/khóa ứng dụng trong `docs` (đã grep file văn bản). SRS, User Stories dạng .docx chưa đọc được nội dung; nếu SRS có yêu cầu bảo mật thiết bị, người duyệt chỉ ra mục để đối chiếu. Bất biến 1 (client không gọi Supabase) và 4 (JWT chỉ mang danh tính) không bị ảnh hưởng vì A không đổi cách gọi API.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | `frontend/mobile`: dependency `local_auth`, màn khóa, công tắc cài đặt, cấu hình iOS/Android, test. |
| `backend` | Không | Phiên và endpoint giữ nguyên. |
| `api_contract` | Không | Không đổi API. |
| `tests` | Không | Không có luồng xuyên service mới. |
| `docs` | Không (trong task) | Bộ test case Excel cập nhật qua `wf-testcase` ở cuối giai đoạn test. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: khóa sinh trắc là cổng phía client trước khi dùng phiên đã có; request/response, xác thực, mã lỗi không đổi.
- Endpoint liên quan: chỉ dùng endpoint có sẵn; không gọi thêm endpoint nào khi mở khóa.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng rủi ro backend nào trong `AGENTS.md`.
- Liên quan gián tiếp "Bí mật": token tiếp tục nằm ở Keychain/Keystore; task không được ghi token hay kết quả sinh trắc ra log, `SharedPreferences` hay bộ nhớ thường.
- Ghi nhận liều và đồng bộ: khóa app không được chặn đồng bộ nền / outbox và hành động xác nhận liều từ thông báo (xem Q2), nếu không sẽ làm mất xác nhận liều.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given thiết bị chưa đặt khóa màn hình, When mở màn Cài đặt, Then công tắc khóa bị vô hiệu kèm hướng dẫn đặt khóa màn hình; thiết bị có mã khóa nhưng không có sinh trắc vẫn bật được. | unit (widget, mock `LocalAuthentication`) |
| AC2 | Given thiết bị hỗ trợ, When người dùng bật công tắc và xác thực thành công, Then cài đặt khóa lưu bật; xác thực thất bại/hủy thì công tắc giữ tắt. | unit |
| AC3 | Given đã đăng nhập và bật khóa, When khởi động lạnh app, Then hiện màn khóa trước mọi màn có dữ liệu sức khỏe; xác thực thành công thì vào Home. | unit (widget) + manual |
| AC4 | Given đang ở trong app và bật khóa, When app chuyển `paused` (tắt app, chuyển app, khóa màn hình thiết bị) rồi `resumed`, Then hiện màn khóa ngay, không phụ thuộc thời gian ở nền. | unit (giả lập lifecycle) + manual |
| AC4b | Given bật khóa, When app tự mở hộp thoại hệ thống (prompt sinh trắc, xin quyền, camera/chọn ảnh OCR) rồi quay lại, Then không khóa lại và không lặp vô hạn prompt sinh trắc. | unit + manual |
| AC4c | Given bật khóa, When app chuyển `inactive`/`paused`, Then lớp che phủ toàn màn hình được hiện trước khi OS chụp ảnh app switcher; ảnh trong màn đa nhiệm không có dữ liệu sức khỏe. | unit (widget) + manual (iOS, Android) |
| AC4d | Given công tắc khóa tắt, When chuyển app rồi quay lại, Then hành vi như hiện tại (không màn khóa, không lớp che). | unit |
| AC5 | Given màn khóa, When xác thực thất bại hoặc bị hủy, Then vẫn ở màn khóa, không hiện dữ liệu; có nút "Mở khóa" để thử lại (OS cho nhập mã khóa màn hình) và "Đăng xuất". | unit |
| AC6 | Given màn khóa, When bấm "Đăng xuất", Then phiên và cài đặt khóa bị xóa, về màn Đăng nhập OTP. | unit |
| AC7 | Given bật khóa, When API trả 401 hoặc người dùng đăng xuất, Then cài đặt khóa bị xóa cùng phiên; lần đăng nhập sau công tắc mặc định tắt. | unit |
| AC8 | Given bật khóa và app ở nền/đã khóa, When đến giờ nhắc và người dùng bấm hành động xác nhận liều trên thông báo, Then liều vẫn được ghi qua outbox như hiện tại (theo giả định Q2). | unit + manual |
| AC9 | Given iPhone có Face ID và Android có vân tay, When bật khóa và mở khóa, Then hộp thoại hệ thống hiện đúng câu chữ tiếng Việt; Android không crash do `FragmentActivity`. | manual (cần thiết bị thật) |
| AC10 | Given bất kỳ luồng nào ở trên, When kiểm tra log và storage, Then không có token hay kết quả sinh trắc ngoài `flutter_secure_storage`. | unit (review + test store) |

## 8. Câu hỏi mở

Q2 [không chặn] Khi app đang khóa, hành động "Đã uống" trên thông báo và widget có cần mở khóa không?
- Ảnh hưởng: yêu cầu mở khóa an toàn hơn nhưng có thể làm người cao tuổi bỏ xác nhận liều.
- Lựa chọn: không cần mở khóa / cần mở khóa
- Giả định mặc định: không cần mở khóa (ưu tiên tuân thủ dùng thuốc, giống Messenger vẫn cho trả lời nhanh từ thông báo).

Q5 [không chặn] Áp dụng cho cả patient và người thân?
- Ảnh hưởng: vị trí công tắc trong hai luồng điều hướng.
- Lựa chọn: cả hai / chỉ patient
- Giả định mặc định: cả hai, opt-in, mặc định tắt.

(Q1, Q3, Q4 đã được người dùng trả lời ngày 2026-11-25, xem mục 9.)

## 9. Giả định

- Q1 (người dùng trả lời 2026-11-25): làm phương án A, tính năng bổ sung kiểu "Khóa ứng dụng" của Messenger, giữ nguyên phiên đăng nhập. B và C không làm.
- Q3 (người dùng trả lời 2026-11-25): khóa ngay khi tắt app hoặc khóa màn hình rồi vào lại; không có thời gian chờ.
- Q4 (người dùng trả lời 2026-11-25): mở khóa bằng Face ID, vân tay hoặc mã khóa màn hình thiết bị.
- Mục tiêu "chống xem trộm" kéo theo che nội dung trong app switcher (AC4c), trước đây để ngoài phạm vi.
- Cài đặt khóa (bật/tắt) lưu theo thiết bị trong `flutter_secure_storage`, không đồng bộ lên server.
- Dùng plugin chính thức `local_auth` (flutter.dev); không thêm plugin khác.
- Không phát hiện việc đổi vân tay/khuôn mặt đã đăng ký (giới hạn của phương án A; phương án C xử lý).

## 10. Phát sinh

- Phiên mobile là JWT 10 ngày, không refresh và không thu hồi phía server (`sign_in.py:104`). Mất máy thì không có cách vô hiệu phiên từ xa. Ngoài phạm vi task này; nên cân nhắc khi làm phương án B.
- `MainActivity` chuyển sang `FlutterFragmentActivity` có thể ảnh hưởng plugin khác (camera OCR, thông báo); plan cần kiểm lại các luồng đó.

## 11. Size

- `size`: M
- Lý do: một submodule (`frontend`), không đổi contract/migration, nhưng hơn 3 file (dependency, màn khóa, controller, cài đặt, cấu hình iOS + Android, test) và đụng vòng đời app ảnh hưởng thông báo/đồng bộ nền.

## Bước tiếp theo

- Đang chờ: người duyệt (Q2, Q5 không chặn, theo giả định mặc định nếu không có ý kiến).
- Việc cần làm: chạy `python .agents/scripts/gate.py approve adhoc-20261125-biometric-auth requirement`; rồi sang `wf-plan`.
- Cập nhật lần cuối: 2026-11-25, Claude Code (cập nhật theo trả lời Q1, Q3, Q4)
