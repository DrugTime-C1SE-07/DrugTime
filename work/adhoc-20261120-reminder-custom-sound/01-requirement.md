---
task: adhoc-20261120-reminder-custom-sound
title: Âm thanh nhắc nhở S08-4a — chọn, nghe thử và thêm âm thanh từ máy (lưu trên thiết bị)
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-20 11:21 +0700
content_hash: sha256:15b8320b1a1fec90
---

# adhoc-20261120-reminder-custom-sound · Âm thanh nhắc nhở S08-4a

## 1. Mục tiêu

Patient chọn được âm thanh cho thông báo nhắc uống thuốc trên Android: chọn một âm có sẵn, nghe thử, hoặc thêm tối đa 10 âm thanh từ máy. Mọi dữ liệu nằm trên thiết bị. Nhắc thuốc không bao giờ bị im lặng ngoài ý muốn: âm thanh đã chọn mà mất thì app tự quay về chuông mặc định.

## 2. Phạm vi

### Trong phạm vi

- Màn S08-4a (`ReminderSoundScreen`) chuyển từ "chưa khả dụng" sang dùng được trên Android:
  - Chọn một trong các âm có sẵn: Chuông mặc định, Nhẹ nhàng, Âm cha hữu ơi, Khẩn cấp, Chuông điện thoại mặc định, Im lặng (chỉ rung).
  - Nghe thử từng âm; chỉ một âm phát tại một thời điểm.
  - Nhóm "Âm thanh của bạn": thêm file âm thanh từ máy, nghe thử, chọn, xóa.
- Kiểm tra file khi thêm: định dạng (mp3, m4a/aac, ogg, wav; xét cả byte đầu file), dung lượng ≤ 10 MB, thời lượng 1–30 giây, giải mã được.
- Giới hạn 10 âm thanh tự thêm. Đủ 10 thì khóa nút thêm và hiện hướng dẫn xóa bớt.
- Lưu file vào thư mục riêng của app và một bản vào MediaStore (mục Notifications), tên trung tính `DrugTime nhắc nhở <n>`.
- Mỗi âm thanh một Android notification channel. Đổi lựa chọn thì lên lịch lại các nhắc chưa tới giờ theo luồng hiện có (`ReminderSyncCoordinator.refresh`).
- Nhắc lại sau 10 phút (QD-20) và snooze dùng cùng âm thanh đã chọn.
- Quay về "Chuông mặc định" khi âm thanh đã chọn bị xóa hoặc file không còn, kèm thông báo cho người dùng.
- Dòng âm lượng: thay slider bằng lối mở cài đặt âm thanh hệ thống (xem Q4).

### Ngoài phạm vi

- Lưu hay sao lưu âm thanh lên server; khôi phục khi đổi máy hoặc cài lại app (QD-19).
- Âm thanh cho push từ máy chủ (`family_alerts`, nhắc từ người thân) và cho thông báo người thân.
- Chọn âm thanh riêng theo từng thuốc hoặc từng lịch.
- Nhắc tăng dần, phát lặp, điều chỉnh âm lượng trong app.
- Đổi tên, cắt hoặc chỉnh sửa file âm thanh.
- iOS: thêm âm thanh từ máy và âm có sẵn riêng (xem Giả định).
- Đổi giao diện theo Figma S08-4a: thiết kế đã dán chỉ có frame rỗng; bố cục giữ theo màn hiện có.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `frontend/mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart` | Màn S08-4a hiện chỉ là giao diện: banner "Chọn và nghe thử âm thanh chưa khả dụng.", slider âm lượng vô hiệu, 6 dòng âm thanh `unavailable` |
| `frontend/mobile/lib/app/router.dart:64,143` | Route `/profile/notifications/sound`, mở từ `notification_preferences_screen.dart:29` |
| `frontend/mobile/lib/core/notification/notification_service.dart:353-390` | Một kênh nhắc duy nhất `drugtime_reminder_channel`, `Importance.max`, âm mặc định hệ thống; múi giờ cố định `Asia/Ho_Chi_Minh` |
| `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart:40-190` | `AndroidNotificationDetails` là hằng dùng `reminderChannelId`, `fullScreenIntent`, `category: alarm`; `scheduleOccurrences`, `snooze`, `cancelOccurrence` |
| `frontend/mobile/lib/core/notification/reminder_sync_coordinator.dart:37-80` | `refresh(patientId)` hủy rồi lên lịch lại các lượt nhắc chưa tới giờ: dùng được khi đổi âm thanh |
| `frontend/mobile/pubspec.yaml` | Có `flutter_local_notifications ^17.2.2`, `flutter_secure_storage`, `sqflite_sqlcipher`, `path_provider`; chưa có thư viện chọn file và phát audio |
| `frontend/mobile/android/app/build.gradle*` | `minSdk = 24`; ghi MediaStore không cần quyền chỉ từ Android 10 (API 29) |
| `backend/src/drugtime/notification_gateway/fcm.py` | Push máy chủ luôn `channel_id: "family_alerts"`, không có `sound`; không đổi trong task này |
| `api_contract/openapi.json`, `backend/supabase/migrations/` | Không có endpoint hay bảng cài đặt âm thanh; task không cần thêm |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` mục 6, 7.4 | Quyết định nghiệp vụ áp dụng (mục 3a) |

### 3a. Quyết định nghiệp vụ áp dụng

Nguồn: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, baseline `QD-2026-10-03-v1`.

| Mã | Mục nguồn | Quy tắc áp dụng | TT | AC |
|---|---|---|---|---|
| QD-20 | 6.1 | Nhắc lại một lần sau 10 phút cho liều chưa xác nhận: lượt nhắc lại dùng cùng âm thanh đã chọn | ✅ | AC9 |
| QD-26 (hàng 1) | 6.1 | Màn hình khóa chỉ hiện nội dung chung; muốn tắt tiếng nhắc uống thuốc phải chọn riêng | ✅ | AC8, AC10 |
| C-06, BS-03 | 6.3 | Giảm phạm vi iOS, kiểm thử đầy đủ thông báo trên Android | ☑️ / 🆕 | AC12 |
| QD-19 | 7.4 | Giai đoạn 1 chấp nhận mất dữ liệu chỉ có trên máy khi xóa app hoặc mất máy | ✅ | AC7 (quay về mặc định), Ngoài phạm vi |
| NT-06 | 6.1 | Đặt lại nhắc sau khởi động: còn ⏳ đề xuất; task không đổi hành vi này | ⏳ | — |

QD-26 (hàng 2, hộp thư 30 ngày), QD-21, QD-22, QD-23 và mục 6.2 đã đối chiếu: không bị task chạm.

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Có | `frontend/mobile`: màn S08-4a, notification service/scheduler, lưu trữ local, mã Android native (MediaStore), thư viện mới, file âm có sẵn, test |
| backend | Không | Không lưu gì trên server |
| api_contract | Không | Không đổi API |
| tests | Không | Không có luồng xuyên service |
| docs | Có (chỉ file test case) | `Test_Cases.xlsx` qua `wf-testcase` ở giai đoạn test |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: mọi dữ liệu (file, danh sách, lựa chọn) nằm trên thiết bị; không gọi API mới hay đổi API cũ.
- Endpoint liên quan: không có.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng nào trong bảng vùng rủi ro của `AGENTS.md`: không đọc/ghi dữ liệu sức khỏe qua API, không đụng ghi nhận liều, outbox, phân quyền, schema hay module backend.
- Bất biến 7 (múi giờ `Asia/Ho_Chi_Minh`): lên lịch lại dùng `location` hiện có, không đổi.
- Lưu ý an toàn (không phải vùng trong bảng): task sửa đường lập lịch nhắc thuốc. Lỗi làm nhắc không kêu là mức High theo thang `AGENTS.md`, nên có AC7, AC9 và AC13 riêng.
- Bí mật: không có key hay token mới.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given đang dùng "Chuông mặc định", When chọn "Nhẹ nhàng", Then lựa chọn được lưu local, dòng "Nhẹ nhàng" hiện đã chọn sau khi mở lại màn, và các lượt nhắc chưa tới giờ được lên lịch lại trên channel của "Nhẹ nhàng" | unit |
| AC2 | Given đang ở S08-4a, When nhấn nghe thử âm A rồi âm B, Then A dừng, B phát; nhấn lại B thì B dừng | unit (widget, player giả) |
| AC3 | Given có ít hơn 10 âm tự thêm, When chọn file mp3 hợp lệ 15 giây 1 MB, Then file được copy vào thư mục riêng của app, có bản MediaStore tên `DrugTime nhắc nhở <n>`, có channel riêng, và hiện một dòng mới trong "Âm thanh của bạn" | unit + manual |
| AC4 | Given chọn file không hợp lệ, When thêm, Then không lưu gì và hiện đúng thông báo: file .pdf đổi đuôi .mp3 → "Định dạng không hỗ trợ"; 10 MB + 1 byte (10485761 byte) → "File quá lớn (tối đa 10 MB)"; 0,9 giây hoặc 30,1 giây → "Âm thanh phải dài từ 1 đến 30 giây"; file hỏng → "Không phát được file này". Biên hợp lệ: đúng 10 MB (10485760 byte), đúng 1 giây, đúng 30 giây được nhận | unit |
| AC5 | Given đã có 10 âm tự thêm, When mở S08-4a, Then nút "+ Thêm âm thanh từ máy" bị khóa và hiện "Đã đủ 10 âm thanh. Xóa một âm thanh để thêm mới."; xóa một âm thì nút mở lại | unit (widget) |
| AC6 | Given âm tự thêm X đang được chọn, When xóa X, Then lựa chọn chuyển về "Chuông mặc định", nhắc chưa tới giờ được lên lịch lại, channel của X bị xóa, file riêng và bản MediaStore của X bị xóa | unit |
| AC7 | Given âm đã chọn không còn đọc được (file hoặc bản MediaStore bị xóa từ ngoài app), When mở app hoặc trước khi lên lịch nhắc, Then lựa chọn chuyển về "Chuông mặc định", nhắc được lên lịch trên channel mặc định, và S08-4a hiện "Âm thanh bạn chọn không còn, đã chuyển về chuông mặc định" | unit |
| AC8 | Given chọn "Im lặng (chỉ rung)", Then channel tương ứng không phát âm, có rung; lựa chọn này chỉ đạt được khi người dùng tự chọn, không bao giờ là kết quả quay về (QD-26) | unit |
| AC9 | Given đã chọn âm X, When lượt nhắc lại sau 10 phút (QD-20) hoặc snooze được lên lịch, Then dùng channel của X | unit |
| AC10 | Given bất kỳ âm nào được chọn, Then nội dung, `fullScreenIntent`, `category: alarm` và mức hiển thị trên màn hình khóa của thông báo nhắc giữ như hiện tại; chỉ channel thay đổi (QD-26) | unit |
| AC11 | Given ở S08-4a, When nhấn dòng âm lượng, Then mở cài đặt âm thanh của hệ thống; không còn slider vô hiệu | unit (widget, launcher giả) |
| AC12 | Given chạy trên iOS, Then nhóm "Âm thanh của bạn" và nút thêm bị ẩn; app không lỗi khi mở S08-4a | unit (widget, `TargetPlatform.iOS`) |
| AC13 | Given máy Android 10+ thật, When đến giờ nhắc với âm có sẵn và với âm tự thêm, Then nghe đúng âm đã chọn; xóa file âm tự thêm bằng app quản lý file rồi mở app thì nhắc kế tiếp kêu chuông mặc định | manual (cần thiết bị và âm thanh thật) |
| AC14 | Given thêm âm thanh, Then tên trong MediaStore và tên file riêng không chứa tên file gốc của người dùng hay thông tin thuốc | unit |
| AC15 | Given mở trình chọn file, When hủy, Then không có gì thay đổi và không hiện lỗi | unit (widget) |

## 8. Câu hỏi mở

Q1 [không chặn] Khi đăng xuất hoặc đổi tài khoản, âm thanh tự thêm xử lý thế nào?
- Ảnh hưởng: thêm bước dọn dữ liệu vào luồng đăng xuất và một AC.
- Lựa chọn: A. Xóa hết âm tự thêm (file, MediaStore, channel) và trả lựa chọn về mặc định / B. Giữ lại cho người đăng nhập sau.
- Giả định mặc định: A, vì máy có thể dùng chung và cài đặt gắn với người dùng.

Q2 [không chặn] Android 7–9 (API 24–28) cần quyền ghi bộ nhớ để ghi MediaStore. Xử lý thế nào?
- Ảnh hưởng: có xin quyền runtime hay không, thêm nhánh UI.
- Lựa chọn: A. Ẩn tính năng thêm âm thanh trên API < 29, vẫn chọn được âm có sẵn / B. Xin quyền `WRITE_EXTERNAL_STORAGE` trên API < 29.
- Giả định mặc định: A, không xin thêm quyền.

Q3 [không chặn] File cho các âm có sẵn lấy từ đâu, và nhãn "Âm cha hữu ơi" có đúng không?
- Ảnh hưởng: implement cần 4 file âm thanh có giấy phép dùng được (Chuông mặc định, Nhẹ nhàng, Âm cha hữu ơi, Khẩn cấp); nhãn hiện trên màn.
- Lựa chọn: A. Team cung cấp file trước giai đoạn implement / B. Agent chọn âm CC0 và ghi nguồn, giấy phép trong `04` / C. Bỏ bớt âm có sẵn, chỉ giữ "Chuông điện thoại mặc định" và "Im lặng (chỉ rung)".
- Giả định mặc định: B. Nhãn giữ nguyên như màn hiện có cho tới khi có Figma đầy đủ.

Q4 [không chặn] Dòng âm lượng: bỏ slider và mở cài đặt âm thanh hệ thống (A1), hay dùng luồng âm báo thức để nhắc theo âm lượng báo thức (A2)?
- Ảnh hưởng: A2 đổi `AudioAttributesUsage` của channel, nhắc kêu cả khi máy để chế độ im lặng, cần thêm AC và test trên máy.
- Lựa chọn: A1 / A2.
- Giả định mặc định: A1.

## 9. Giả định

- Lưu toàn bộ trên thiết bị, Android là nền tảng chính, tối đa 10 âm tự thêm (phải xóa bớt khi đủ 10), chấp nhận âm tự thêm hiện trong danh sách nhạc chuông của máy với tên trung tính: người dùng đã quyết định trong trao đổi ngày 2026-11-20.
- "Chuông điện thoại mặc định" dùng channel hiện có `drugtime_reminder_channel` (âm mặc định hệ thống), nên người dùng hiện tại không đổi gì cho tới khi tự chọn âm khác.
- Lựa chọn mặc định ban đầu và đích quay về khi mất file là "Chuông mặc định" (âm có sẵn của DrugTime). Nếu Q3 chọn C, đích quay về là "Chuông điện thoại mặc định".
- Trên iOS chỉ hiện các âm có sẵn để xem, nhắc dùng âm mặc định hệ thống như hiện tại (C-06, BS-03).
- Thêm thư viện chọn file và phát audio. Tên và phiên bản cụ thể chốt ở `03-plan.md`.
- Lựa chọn và danh sách âm tự thêm lưu bằng storage local app đang có. Đây không phải dữ liệu sức khỏe, nhưng vẫn không ghi tên file gốc vào log.

## 10. Phát sinh

- Figma S08-4a đã dán chỉ có frame rỗng (nền `#F7F9F8`); khi có thiết kế đầy đủ nên có task chỉnh giao diện riêng.
- Push máy chủ luôn dùng `family_alerts` (`backend/src/drugtime/notification_gateway/fcm.py`); chọn âm cho push là việc riêng nếu cần.

## 11. Size

- `size`: M
- Lý do: chỉ một submodule (`frontend`), `contract_change: no`, không chạm vùng rủi ro. Nhưng cần sửa nhiều file (màn, notification service, scheduler, lưu trữ, mã Android native, file âm thanh, pubspec, test), thêm thư viện, nên vượt S.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Thay đổi vòng này (2026-11-20, sau khi thử trên máy thật): giới hạn dung lượng âm tự thêm tăng từ 2 MB lên 10 MB (10485760 byte) ở mục Phạm vi và AC4. Hệ quả: tối đa 10 âm × 10 MB ≈ 100 MB trên máy.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261120-reminder-custom-sound requirement`; sau đó reopen và cập nhật lần lượt plan (03), implement (04: validator, thông báo, test biên), test (05, testcases.json, file Excel tổng).
- Cập nhật lần cuối: 2026-11-20, Claude Code
