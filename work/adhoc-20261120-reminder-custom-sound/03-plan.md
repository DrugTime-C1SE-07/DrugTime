---
task: adhoc-20261120-reminder-custom-sound
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-20 09:04 +0700
content_hash: sha256:0f448eed59ca405c
inputs:
  01-requirement.md: sha256:0d751fb5dbc8c598
---

# adhoc-20261120-reminder-custom-sound · Plan

Q1–Q4 của `01` theo giả định mặc định người dùng đã chấp nhận: Q1 = A (đăng xuất/đổi tài khoản thì xóa hết âm tự thêm và đặt lại lựa chọn), Q2 = A (ẩn thêm âm thanh trên API < 29, không xin quyền mới), Q3 = B (agent chọn âm CC0, ghi nguồn và license ở `04`), Q4 = A1 (bỏ slider, mở cài đặt âm thanh hệ thống).

## 1. Giải pháp

### Luồng dữ liệu

```
S08-4a (ReminderSoundScreen)
  └─ ReminderSoundController (ChangeNotifier, cấp qua ReminderSoundScope trong app.dart)
       ├─ ReminderSoundStore      secure storage: lựa chọn + danh sách âm tự thêm + cờ "đã quay về"
       ├─ ReminderSoundValidator  thuần Dart: dung lượng, byte đầu file, thời lượng
       ├─ ReminderSoundNative     MethodChannel `vn.drugtime.drugtime_mobile/reminder_sound` (Kotlin)
       │     pick / probe / commit+MediaStore / delete / exists / play / stop / openSoundSettings / sdkInt
       ├─ NotificationService     tạo/xóa Android channel theo âm thanh
       └─ onSoundChanged()        → ReminderSyncCoordinator.refresh(user) (luồng lên lịch lại có sẵn)

ReminderNotificationScheduler
  └─ đọc channel hiện hành qua `soundChannel` (callback đồng bộ) cho scheduleOccurrences và snooze
ReminderSyncCoordinator.refresh
  └─ gọi hook `beforeSchedule` (= controller.ensureValid) ngay trước scheduleOccurrences → fallback AC7
```

### Thành phần

1. **Danh mục âm (`reminder_sound.dart`)**: kiểu `ReminderSound` (id ổn định, nhãn, loại `builtin | system | silent | custom`, `channelId`, âm Android). Âm có sẵn:

   | id | Nhãn | Channel | Âm |
   |---|---|---|---|
   | `chime` (mặc định, đích quay về) | Chuông mặc định | `drugtime_reminder_chime_v1` | `res/raw/reminder_chime` |
   | `gentle` | Nhẹ nhàng | `drugtime_reminder_gentle_v1` | `res/raw/reminder_gentle` |
   | `friendly` | Âm cha hữu ơi | `drugtime_reminder_friendly_v1` | `res/raw/reminder_friendly` |
   | `urgent` | Khẩn cấp | `drugtime_reminder_urgent_v1` | `res/raw/reminder_urgent` |
   | `system` | Chuông điện thoại mặc định | `drugtime_reminder_channel` (kênh hiện có) | âm hệ thống |
   | `silent` | Im lặng (chỉ rung) | `drugtime_reminder_silent_v1` | `playSound: false`, `enableVibration: true` |

   Âm tự thêm: id `custom_<uuid v4>`, channel `drugtime_reminder_custom_<uuid>`, âm `UriAndroidNotificationSound(<content uri MediaStore>)`. Mọi channel nhắc giữ `Importance.max` như kênh cũ. Uuid mới cho mỗi lần thêm, không tái dùng id channel (Android khôi phục cài đặt cũ khi tạo lại channel cùng id đã xóa).

2. **Validator (`reminder_sound_validator.dart`)**, thứ tự kiểm và thông báo nguyên văn của AC4:
   - `size > 2 097 152` byte → "File quá lớn (tối đa 2 MB)". Đúng 2 097 152 hợp lệ.
   - Byte đầu không khớp mp3 (`ID3` hoặc frame sync `FF Fx`), m4a (`ftyp` ở offset 4), aac ADTS (`FF F1`/`FF F9`), ogg (`OggS`), wav (`RIFF`…`WAVE`) → "Định dạng không hỗ trợ". Không tin đuôi file.
   - Native báo không giải mã được → "Không phát được file này".
   - `durationMs < 1000` hoặc `> 30000` → "Âm thanh phải dài từ 1 đến 30 giây". 1000 và 30000 hợp lệ.

3. **Native Android (`ReminderSoundChannel.kt`, đăng ký trong `MainActivity.configureFlutterEngine` cạnh kênh keyguard)**:
   - `sdkInt` → `Build.VERSION.SDK_INT`.
   - `pick` → `ACTION_OPEN_DOCUMENT`, `audio/*`; copy luồng vào `cacheDir/reminder_pick.tmp`, ngừng đọc khi vượt 2 MB + 1 byte; trả `{path, size, head(16 byte)}` hoặc `null` khi hủy (AC15).
   - `probe(path)` → `MediaMetadataRetriever` lấy thời lượng + `MediaPlayer.prepare()` để xác nhận giải mã; lỗi trả `decode_failed`.
   - `commit(path, id, number)` → chuyển file vào `filesDir/reminder_sounds/<id>.<ext>`, chèn MediaStore Audio với `IS_NOTIFICATION=1`, `RELATIVE_PATH=Notifications/DrugTime`, `DISPLAY_NAME="DrugTime nhắc nhở <number>"`; trả content uri. Lỗi giữa chừng thì xóa phần đã ghi.
   - `delete(path, uri)`, `exists(uri)` (mở được `openFileDescriptor` hay không), `play(uri | rawName)` / `stop()` (một `MediaPlayer` duy nhất, `USAGE_NOTIFICATION`), `openSoundSettings` (`Settings.ACTION_SOUND_SETTINGS`).
   - Không thêm quyền vào manifest. iOS không đăng ký kênh: Dart không gọi trên iOS.

4. **Store (`reminder_sound_store.dart`)**: theo pattern `SecureProfileAvatarPreferences`. Khóa `reminder_sound_v1` chứa JSON `{selected, customs:[{id, number, path, uri}], fallbackNotice}`. Không lưu tên file gốc (AC14). Dữ liệu theo thiết bị, bị xóa khi đăng xuất (Q1), nên không cần khóa theo user.

5. **Controller (`reminder_sound_controller.dart`)**: `load`, `select`, `addFromDevice`, `delete`, `togglePreview`, `stopPreview`, `ensureValid`, `clearAll`, `openSoundSettings`; trạng thái `customSupported` (= Android và `sdkInt >= 29`), `canAdd` (`customs.length < 10`), `playingId`, `error`, `fallbackNotice`. `number` của âm mới là số nhỏ nhất chưa dùng trong 1–10. Mọi thao tác đổi lựa chọn: tạo channel (idempotent), lưu store, gọi `onSoundChanged`. `ensureValid`: lựa chọn là custom mà `exists(uri)` sai hoặc file riêng mất → xóa custom đó khỏi danh sách, chọn `chime`, bật `fallbackNotice`. Không bao giờ chuyển sang `silent` (AC8). Kèm `ReminderSoundScope extends InheritedNotifier` như `ConsentScope`.

6. **Scheduler**: thay hằng `_androidNotificationDetails` bằng hàm dựng từ `soundChannel()`; mọi trường khác (`importance`, `priority`, `fullScreenIntent`, `category: alarm`, `color`, nội dung) giữ nguyên (AC10). Tham số `soundChannel` tùy chọn, mặc định trả kênh `system` hiện có nên các nơi tạo scheduler cũ và test cũ không đổi hành vi. `snooze` dùng cùng hàm (AC9).

7. **Coordinator**: thêm tham số tùy chọn `beforeSchedule` (Future), gọi trước `_scheduler.scheduleOccurrences` trong `refresh`; lỗi của hook được log và không chặn lập lịch (lập lịch trên channel hiện hành vẫn tốt hơn không nhắc).

8. **NotificationService**: thêm `deleteNotificationChannel(id)` vào wrapper platform (cùng chỗ `resolvePlatformSpecificImplementation` đang dùng). `init()` giữ tạo kênh `drugtime_reminder_channel`.

9. **app.dart / main.dart**: `main.dart` tạo `ReminderSoundController` (native, store, notificationService) và truyền `soundChannel`/`beforeSchedule` cho scheduler/coordinator; `onSoundChanged` gọi refresh với user đang hoạt động. `app.dart` bọc cây bằng `ReminderSoundScope` (tham số tùy chọn, như `_FallbackReminderScheduler`, để test app cũ không vỡ); `_activateReminders` gọi `load()` trước refresh đầu tiên; nhánh `!_auth.isAuthenticated && _wasAuthenticated` gọi `clearAll()` (Q1).

10. **Màn S08-4a**: bỏ `ProfileUnavailable` và slider trên Android. Thẻ âm lượng thành `ProfileFlowRow` "Âm lượng nhắc nhở" mở cài đặt hệ thống (AC11). Nhóm "Chọn âm thanh": 6 dòng, icon play/stop nghe thử (AC2), trailing radio chọn (AC1). Nhóm "Âm thanh của bạn" (chỉ khi `customSupported`): mỗi dòng nghe thử / chọn / xóa (có hộp xác nhận), nút "+ Thêm âm thanh từ máy", khóa kèm "Đã đủ 10 âm thanh. Xóa một âm thanh để thêm mới." khi đủ 10 (AC5). Lỗi AC4 và thông báo fallback AC7 hiện bằng `ProfileUnavailable`/banner có sẵn trong `profile_flow_widgets.dart`. iOS: giữ màn như hiện tại (banner "chưa khả dụng", danh sách vô hiệu), ẩn nhóm "Âm thanh của bạn" (AC12), vì iOS nhắc dùng âm hệ thống (giả định của `01`). Dừng nghe thử khi rời màn.

11. **Âm có sẵn**: 4 file `.ogg` ngắn (≤ 5 giây, ≤ 100 KB mỗi file) trong `android/app/src/main/res/raw/`, cộng `res/raw/keep.xml` (`tools:keep="@raw/reminder_*"`) để resource shrinking không xóa file chỉ được tham chiếu bằng tên chuỗi. Nguồn CC0 (Q3); nguồn, tác giả, license, checksum ghi ở `04`. Không tìm được âm CC0 phù hợp thì tự tổng hợp âm bằng script trong `work/<task>/scratch/` (tác phẩm của team, không vướng license) và ghi rõ ở `04`.

### Cách đã cân nhắc và bỏ

- **Thêm `file_picker` + `just_audio`/`audioplayers`**: bỏ. Vẫn phải viết Kotlin cho MediaStore và thời lượng; picker/player native chỉ thêm khoảng 60 dòng Kotlin và tránh hai dependency mới cùng quyền/manifest merge của chúng.
- **Một channel, đổi âm bằng cách xóa rồi tạo lại cùng id**: bỏ. Android giữ cài đặt cũ của channel cùng id; không đổi được âm.
- **Lưu âm/lựa chọn trên server**: ngoài phạm vi (`01`, QD-19).

### Bất biến

- Bất biến 1: không gọi Supabase, không gọi API mới.
- Bất biến 7: lên lịch lại dùng `location` hiện có (`Asia/Ho_Chi_Minh`), không đổi.
- Các bất biến còn lại không bị chạm (không đụng backend, liều, phân quyền, tương tác thuốc).

## 2. Khảo sát

Quyết định nghiệp vụ: `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, baseline `QD-2026-10-03-v1`, mục 6.1, 6.3, 7.4 đã đối chiếu lại; trạng thái giữ như mục 3a của `01`.

| File đã đọc | Điều rút ra |
|---|---|
| `frontend/mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart` | 45 dòng, StatelessWidget không phụ thuộc; dùng `ProfileFlowHeader`, `ProfileFlowCard`, `ProfileFlowSection`, `ProfileFlowRow(unavailable: true)` |
| `frontend/mobile/lib/shared/widgets/profile_flow_widgets.dart` | Widget dùng chung cho màn hồ sơ; nền `profileFlowCanvas` đã khớp thiết kế |
| `frontend/mobile/lib/app/router.dart:64,143` | Route tạo `const ReminderSoundScreen()`; dependency phải đến qua scope, không qua constructor |
| `frontend/mobile/lib/core/notification/notification_service.dart` | Wrapper platform trừu tượng (test dùng fake); `init()` idempotent tạo `drugtime_reminder_channel` `Importance.max`; `resolvePlatformSpecificImplementation` ở dòng 135, 185, 193 |
| `frontend/mobile/lib/core/notification/reminder_notification_scheduler.dart:46-60,106,123,160,177` | Một hằng `NotificationDetails` dùng cho 4 lời gọi `zonedSchedule` (exact + fallback inexact của `scheduleOccurrences` và `snooze`) — chỉ cần đổi một chỗ |
| `frontend/mobile/lib/core/notification/reminder_sync_coordinator.dart:37-80` | `refresh(patientId)` hủy rồi lên lịch lại; điểm chèn hook trước dòng 62 |
| `frontend/mobile/lib/core/notification/reminder_scheduler.dart`, `lib/app/app.dart:978-995` | Interface `snooze/cancelOccurrence/cancelAllForSchedule`; app có `_FallbackReminderScheduler` khi không được truyền — dùng cùng cách cho controller âm thanh |
| `frontend/mobile/lib/main.dart:74-120` | Nơi tạo `NotificationService`, scheduler, coordinator; thêm controller tại đây |
| `frontend/mobile/lib/app/app.dart:226,285-300,333,827` | `_reminderUser`, nhánh đăng xuất (`familyPushService?.clear()`), refresh nhắc, chỗ cấp `ProfileScope` |
| `frontend/mobile/lib/features/profile/data/repositories/secure_profile_avatar_preferences.dart` | Pattern lưu cài đặt bằng `FlutterSecureStorage` có kiểm hợp lệ khi đọc |
| `frontend/mobile/lib/features/consent/presentation/state/consent_controller.dart:76` | Pattern `InheritedNotifier` scope |
| `frontend/mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt` | Đã có một `MethodChannel` (keyguard) trong `configureFlutterEngine`; thêm kênh thứ hai cùng chỗ |
| `frontend/mobile/android/app/build.gradle*`, `pubspec.yaml` | `minSdk 24`; không có thư viện chọn file/phát audio; `flutter_local_notifications ^17.2.2` có `RawResourceAndroidNotificationSound`, `UriAndroidNotificationSound`, `deleteNotificationChannel` |
| `grep snooze|QD-20|nhắc lại` trong `frontend/mobile/lib` | Mobile không có đường lập lịch "nhắc lại sau 10 phút" riêng: mọi thông báo nhắc cục bộ đi qua `scheduleOccurrences` hoặc `snooze`. "Nhắc lại" từ người thân (`patient_dose_reminders`, 429) là push máy chủ, ngoài phạm vi. AC9 được phủ khi cả hai đường dùng channel đã chọn |
| `frontend/mobile/test/core/notification/*`, `test/features/profile/*` | Có fake platform cho scheduler/service; `profile_flow_visual_test.dart:43` dựng `const ReminderSoundScreen()` không có scope — phải cấp scope giả |

### Quyết định nghiệp vụ áp dụng

| Mã | Mục nguồn / quy tắc | TT | AC | Bước | Test |
|---|---|---|---|---|---|
| QD-20 | 6.1 · nhắc lại 10 phút dùng cùng âm đã chọn | ✅ | AC9 | P6 | `scheduler: snooze uses selected sound channel__AC9`, `scheduler: occurrences use selected sound channel__AC9` |
| QD-26 (hàng 1) | 6.1 · màn khóa chỉ nội dung chung; tắt tiếng phải chọn riêng | ✅ | AC8, AC10 | P1, P5, P6 | `controller: fallback never selects silent__AC8`, `sound: silent channel has no sound but vibrates__AC8`, `scheduler: details unchanged except channel__AC10` |
| C-06, BS-03 | 6.3 · giảm phạm vi iOS, test đủ trên Android | ☑️ / 🆕 | AC12, AC13 | P9 | `screen: iOS hides custom group__AC12`; AC13 thủ công |
| QD-19 | 7.4 · dữ liệu chỉ có trên máy được phép mất | ✅ | AC7 | P5, P7 | `controller: missing custom file falls back to chime__AC7`, `coordinator: beforeSchedule runs before scheduling__AC7` |
| NT-06 | 6.1 · đặt lại nhắc sau khởi động | ⏳ | — | — | Không đổi hành vi; không chốt |

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule; được dùng glob, ví dụ `src/<module>/auth/**`. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/core/notification/reminder_sound.dart` | thêm | Danh mục âm, `ReminderSound`, dựng `AndroidNotificationChannel` theo âm |
| frontend | `mobile/lib/core/notification/reminder_sound_validator.dart` | thêm | Kiểm dung lượng, byte đầu, thời lượng; thông báo lỗi AC4 |
| frontend | `mobile/lib/core/notification/reminder_sound_native.dart` | thêm | Interface + MethodChannel tới Kotlin |
| frontend | `mobile/lib/core/notification/reminder_sound_store.dart` | thêm | Lưu lựa chọn, danh sách âm tự thêm, cờ fallback (secure storage) |
| frontend | `mobile/lib/core/notification/reminder_sound_controller.dart` | thêm | Logic chọn/thêm/xóa/nghe thử/fallback/xóa khi đăng xuất + `ReminderSoundScope` |
| frontend | `mobile/lib/core/notification/notification_service.dart` | sửa | `deleteNotificationChannel` trong wrapper platform |
| frontend | `mobile/lib/core/notification/reminder_notification_scheduler.dart` | sửa | `NotificationDetails` dựng từ channel đã chọn |
| frontend | `mobile/lib/core/notification/reminder_sync_coordinator.dart` | sửa | Hook `beforeSchedule` trước khi lập lịch |
| frontend | `mobile/lib/main.dart` | sửa | Tạo controller, nối scheduler/coordinator |
| frontend | `mobile/lib/app/app.dart` | sửa | Cấp `ReminderSoundScope`, `load()` khi kích hoạt nhắc, `clearAll()` khi đăng xuất |
| frontend | `mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart` | sửa | Màn S08-4a dùng được |
| frontend | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/MainActivity.kt` | sửa | Đăng ký kênh native âm thanh |
| frontend | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/ReminderSoundChannel.kt` | thêm | pick/probe/commit/MediaStore/delete/exists/play/stop/openSoundSettings/sdkInt |
| frontend | `mobile/android/app/src/main/res/raw/**` | thêm | 4 âm `.ogg` có sẵn + `keep.xml` |
| frontend | `mobile/test/core/notification/reminder_sound_*_test.dart` | thêm | Unit test validator, store, controller, danh mục |
| frontend | `mobile/test/core/notification/reminder_notification_scheduler_test.dart` | sửa | Test channel đã chọn cho occurrences và snooze, AC10 |
| frontend | `mobile/test/core/notification/reminder_sync_coordinator_test.dart` | sửa | Test hook `beforeSchedule` |
| frontend | `mobile/test/core/notification/notification_service_test.dart` | sửa | Test `deleteNotificationChannel` |
| frontend | `mobile/test/features/profile/reminder_sound_screen_test.dart` | thêm | Widget test S08-4a |
| frontend | `mobile/test/features/profile/profile_flow_visual_test.dart` | sửa | Cấp scope giả cho `s08-4a` |
| frontend | `mobile/test/features/profile/profile_flow_navigation_test.dart` | sửa | Cấp scope giả nếu điều hướng tới S08-4a cần |
| frontend | `mobile/test/features/profile/profile_widget_helpers.dart` | sửa | Helper bọc `ReminderSoundScope` giả |
| docs | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | sửa | Sheet test case S08-4a (giai đoạn test, `wf-testcase`) |

Không đổi `pubspec.yaml`, `pubspec.lock`, `AndroidManifest.xml`.

## 4. Checklist

- [ ] P1 [frontend] Danh mục âm và dựng channel (6 âm có sẵn, custom theo uuid, `silent` không âm + rung, mọi channel `Importance.max`) — file: `mobile/lib/core/notification/reminder_sound.dart`, `mobile/test/core/notification/reminder_sound_catalog_test.dart` — AC: AC1, AC8, AC10 — xong khi: test danh mục pass, id channel đúng bảng mục 1
- [ ] P2 [frontend] Validator thuần Dart — file: `mobile/lib/core/notification/reminder_sound_validator.dart`, `mobile/test/core/notification/reminder_sound_validator_test.dart` — AC: AC4 — xong khi: test pass cho 5 định dạng hợp lệ, pdf đổi đuôi, biên 2 097 152/2 097 153 byte, 999/1000/30000/30001 ms, decode_failed
- [ ] P3 [frontend] Store secure storage (đọc JSON hỏng thì trả mặc định, không lưu tên gốc) — file: `mobile/lib/core/notification/reminder_sound_store.dart`, `mobile/test/core/notification/reminder_sound_store_test.dart` — AC: AC1, AC14 — xong khi: test round-trip, JSON hỏng, khóa không chứa tên gốc pass
- [ ] P4 [frontend] Interface native Dart + Kotlin `ReminderSoundChannel`, đăng ký trong `MainActivity`; thêm 4 âm `.ogg` + `keep.xml` — file: `mobile/lib/core/notification/reminder_sound_native.dart`, `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/ReminderSoundChannel.kt`, `.../MainActivity.kt`, `mobile/android/app/src/main/res/raw/**` — AC: AC3, AC11, AC14, AC15 — xong khi: `flutter build apk --debug` thành công (log), tên MediaStore đúng `DrugTime nhắc nhở <n>`
- [ ] P5 [frontend] Controller + scope: select, add (đủ luồng pick → validate → probe → commit → tạo channel), delete (đang chọn thì về `chime`, xóa channel/file/MediaStore), toggle preview, ensureValid, clearAll, openSoundSettings, giới hạn 10 — file: `mobile/lib/core/notification/reminder_sound_controller.dart`, `mobile/lib/core/notification/notification_service.dart`, `mobile/test/core/notification/reminder_sound_controller_test.dart`, `mobile/test/core/notification/notification_service_test.dart` — AC: AC1, AC2, AC3, AC4, AC5, AC6, AC7, AC8, AC14, AC15 — xong khi: test controller với native/store/service giả pass, gồm fallback không bao giờ ra `silent`
- [ ] P6 [frontend] Scheduler dùng `soundChannel()` cho occurrences và snooze, giữ nguyên các trường khác — file: `mobile/lib/core/notification/reminder_notification_scheduler.dart`, `mobile/test/core/notification/reminder_notification_scheduler_test.dart` — AC: AC1, AC9, AC10 — xong khi: test mới pass và toàn bộ test scheduler cũ pass không sửa kỳ vọng cũ
- [ ] P7 [frontend] Coordinator hook `beforeSchedule` (lỗi hook được log, vẫn lập lịch) — file: `mobile/lib/core/notification/reminder_sync_coordinator.dart`, `mobile/test/core/notification/reminder_sync_coordinator_test.dart` — AC: AC7 — xong khi: test thứ tự gọi và test hook ném lỗi pass
- [ ] P8 [frontend] Nối dây: `main.dart` tạo controller và truyền callback; `app.dart` cấp scope, `load()` trước refresh đầu, `clearAll()` khi đăng xuất — file: `mobile/lib/main.dart`, `mobile/lib/app/app.dart` — AC: AC1, AC6, AC7, Q1 — xong khi: `flutter analyze` sạch với file đã sửa và test app/lifecycle hiện có không fail thêm so với baseline
- [ ] P9 [frontend] Màn S08-4a: dòng âm lượng mở cài đặt, chọn + nghe thử 6 âm, nhóm "Âm thanh của bạn" (Android ≥ 29), khóa khi đủ 10, banner lỗi/fallback, iOS giữ như cũ và ẩn nhóm custom, dừng nghe thử khi rời màn; cập nhật test helper/visual/navigation — file: `mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart`, `mobile/test/features/profile/reminder_sound_screen_test.dart`, `mobile/test/features/profile/profile_widget_helpers.dart`, `mobile/test/features/profile/profile_flow_visual_test.dart`, `mobile/test/features/profile/profile_flow_navigation_test.dart` — AC: AC1, AC2, AC4, AC5, AC6, AC7, AC11, AC12, AC15 — xong khi: widget test pass ở 320 và 375 px, text scale 1.0 và 2.0 không tràn
- [ ] P10 [frontend] Kiểm tra cuối: `flutter test` toàn mobile so với baseline (92 fail có sẵn trên origin/main), `flutter analyze`, `scope.py --stage implement`; ghi nguồn/license/checksum âm vào `04` — file: (không đổi code) — AC: tất cả — xong khi: không có fail mới so với baseline, log trong `evidence/`

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `reminder_sound_catalog_test`: 6 âm có sẵn đúng id/nhãn/channel; `system` dùng `drugtime_reminder_channel`; `silent` `playSound false` + rung; custom dùng `UriAndroidNotificationSound`; mọi channel `Importance.max` | AC1, AC8, AC10 | frontend |
| `reminder_sound_validator_test`: chấp nhận mp3 (ID3, frame sync), m4a, aac ADTS, ogg, wav; từ chối pdf đổi đuôi `.mp3` → "Định dạng không hỗ trợ"; 2 097 152 nhận, 2 097 153 → "File quá lớn (tối đa 2 MB)"; 999/30001 ms → "Âm thanh phải dài từ 1 đến 30 giây", 1000/30000 nhận; decode_failed → "Không phát được file này"; file rỗng | AC4 | frontend |
| `reminder_sound_store_test`: round-trip; JSON hỏng → mặc định `chime`; dữ liệu lưu không chứa tên file gốc | AC1, AC14 | frontend |
| `reminder_sound_controller_test`: select lưu + tạo channel + gọi `onSoundChanged` | AC1 | frontend |
| `reminder_sound_controller_test`: preview A rồi B → stop A, play B; bấm lại B → stop | AC2 | frontend |
| `reminder_sound_controller_test`: add hợp lệ → commit với id uuid, số `n` nhỏ nhất còn trống, tên `DrugTime nhắc nhở <n>`, tạo channel, thêm vào danh sách | AC3, AC14 | frontend |
| `reminder_sound_controller_test`: add không hợp lệ → không commit, không đổi store, `error` đúng thông báo; file tạm bị xóa | AC4 | frontend |
| `reminder_sound_controller_test`: đủ 10 → `canAdd` false, add bị từ chối không gọi pick; xóa 1 → `canAdd` true | AC5 | frontend |
| `reminder_sound_controller_test`: xóa custom đang chọn → về `chime`, `deleteNotificationChannel`, native delete, `onSoundChanged` | AC6 | frontend |
| `reminder_sound_controller_test`: `ensureValid` khi `exists` false → `chime`, `fallbackNotice` true; khi đang `silent` hay âm có sẵn → không đổi; fallback không bao giờ ra `silent` | AC7, AC8 | frontend |
| `reminder_sound_controller_test`: pick trả null → không đổi gì | AC15 | frontend |
| `reminder_sound_controller_test`: `clearAll` xóa mọi custom (file, MediaStore, channel), đặt `chime` | Q1 | frontend |
| `reminder_sound_controller_test`: `customSupported` false khi sdkInt 28 hoặc iOS | AC12, Q2 | frontend |
| `reminder_notification_scheduler_test`: occurrences dùng channel đã chọn; snooze dùng channel đã chọn; đổi lựa chọn rồi lập lịch → channel mới | AC1, AC9 | frontend |
| `reminder_notification_scheduler_test`: với mọi âm, `importance`, `priority`, `fullScreenIntent`, `category`, `color`, title/body giữ như trước; không truyền `soundChannel` → `drugtime_reminder_channel` | AC10 | frontend |
| `reminder_sync_coordinator_test`: `beforeSchedule` gọi trước `scheduleOccurrences`; hook ném lỗi → vẫn lập lịch và có log | AC7 | frontend |
| `notification_service_test`: `deleteNotificationChannel` gọi xuống implementation Android | AC6 | frontend |
| `reminder_sound_screen_test`: chọn "Nhẹ nhàng" → radio đã chọn, controller nhận select | AC1 | frontend |
| `reminder_sound_screen_test`: icon nghe thử đổi play/stop theo `playingId` | AC2 | frontend |
| `reminder_sound_screen_test`: lỗi thêm hiện đúng thông báo | AC4 | frontend |
| `reminder_sound_screen_test`: 10 âm → nút khóa + "Đã đủ 10 âm thanh. Xóa một âm thanh để thêm mới." | AC5 | frontend |
| `reminder_sound_screen_test`: xóa có hộp xác nhận, hủy thì không xóa | AC6 | frontend |
| `reminder_sound_screen_test`: `fallbackNotice` → hiện "Âm thanh bạn chọn không còn, đã chuyển về chuông mặc định" | AC7 | frontend |
| `reminder_sound_screen_test`: nhấn dòng âm lượng → `openSoundSettings`; không còn `Slider` | AC11 | frontend |
| `reminder_sound_screen_test`: `TargetPlatform.iOS` → không có "Âm thanh của bạn", không lỗi; sdk 28 → cũng ẩn | AC12, Q2 | frontend |
| `reminder_sound_screen_test`: 320/375 px × text scale 1.0/2.0 không overflow | — | frontend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Không có | — | Không chạm backend, API hay vùng rủi ro trong `AGENTS.md`; không có kịch bản chất lượng áp dụng. Phần chỉ kiểm được trên thiết bị đi vào kiểm thử thủ công dưới đây |
| Thủ công trên máy Android 10+ thật: (a) đến giờ nhắc với từng âm có sẵn; (b) thêm mp3 hợp lệ, kiểm có trong danh sách âm thông báo hệ thống tên `DrugTime nhắc nhở 1`; (c) nhắc với âm tự thêm; (d) xóa file bằng app quản lý file, mở app → thông báo fallback, nhắc kế kêu chuông mặc định; (e) snooze; (f) chọn Im lặng → chỉ rung; (g) đăng xuất → âm tự thêm biến mất khỏi MediaStore; (h) bản release (`flutter build apk --release`) vẫn kêu âm có sẵn (kiểm `keep.xml`) | AC3, AC8, AC9, AC13, Q1 | Ghi `Pending` trong bộ test case nếu chưa có thiết bị |

## 6. Migration

Không có. Không đổi schema backend; dữ liệu local nằm trong secure storage với khóa mới `reminder_sound_v1`, không đụng SQLite hiện có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/adhoc-20261120-reminder-custom-sound` (tạo từ `main` mới nhất; hiện đang ở nhánh task trước) |
| frontend | `feat/adhoc-20261120-reminder-custom-sound` |
| docs | `feat/adhoc-20261120-reminder-custom-sound` (giai đoạn test) |

Nếu PR của task `adhoc-20261119-profile-s08-figma-align` chưa merge khi bắt đầu implement, tạo nhánh từ `main` hiện có; hai task không chạm cùng file ngoài `profile_flow_visual_test.dart` (ít khả năng xung đột).

## 8. Rủi ro

| Rủi ro | Phát hiện / giảm thiểu |
|---|---|
| Nhắc thuốc im lặng ngoài ý muốn (High): channel âm tự thêm trỏ tới uri không còn, Android phát im hoặc âm mặc định tùy hãng | `ensureValid` trước mỗi lần lập lịch và khi mở app; fallback chỉ về `chime`; test AC7/AC8; kiểm tay (d) |
| Channel bất biến: người dùng đã chỉnh channel trong cài đặt hệ thống, hoặc tạo lại id cũ khôi phục âm cũ | Id channel có hậu tố `_v1` và uuid cho custom, không tái dùng; đổi âm có sẵn sau này thì tăng `_v2` |
| Resource shrinking xóa file `res/raw` chỉ tham chiếu bằng tên | `keep.xml`; kiểm tay (h) trên bản release |
| Hãng điện thoại xử lý MediaStore khác nhau (đường dẫn `Notifications/`, quét chậm) | Âm phát qua content uri do chính app chèn, không phụ thuộc quét; kiểm trên máy thật; ghi hãng/phiên bản đã thử ở `05` |
| API 24–28 không ghi MediaStore được nếu không xin quyền | Q2: ẩn nhóm "Âm thanh của bạn" khi `sdkInt < 29`; âm có sẵn vẫn dùng được |
| Người dùng hiện tại đang nghe âm hệ thống; sau cập nhật mặc định thành "Chuông mặc định" | Đúng giả định của `01`; ghi vào mô tả PR để người review biết |
| Đổi lựa chọn nhiều lần liên tiếp gây refresh chồng nhau | `ReminderSyncCoordinator.refresh` đã xếp hàng công việc; không thêm cơ chế mới |
| File `.ogg` có sẵn tăng kích thước APK | Giới hạn ≤ 100 KB mỗi file (tổng ≤ 400 KB) |
| Bộ test mobile có 92 fail sẵn trên origin/main | So kết quả với baseline chạy cùng phiên, như task trước |

## 9. Câu hỏi mở

Không có câu hỏi chặn. Một điểm để người duyệt biết (không chặn): trên iOS màn S08-4a giữ trạng thái "chưa khả dụng" như hiện tại vì iOS dùng âm hệ thống (giả định của `01`). Nếu muốn ẩn hẳn mục "Âm thanh" trên iOS, cần reopen `01`.

## 10. Phát sinh

Không có.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261120-reminder-custom-sound plan`; sau đó agent làm giai đoạn implement (`wf-implement`) từ P1.
- Cập nhật lần cuối: 2026-11-20, Claude Code
