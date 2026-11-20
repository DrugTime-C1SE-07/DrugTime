---
task: adhoc-20261120-reminder-custom-sound
stage: implement
owner: Ngọc Việt
started_at: 2026-11-20 09:06
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-20 10:07 +0700
content_hash: sha256:3ac2f8e47e35dab4
inputs:
  01-requirement.md: sha256:0d751fb5dbc8c598
  03-plan.md: sha256:0f448eed59ca405c
---

# adhoc-20261120-reminder-custom-sound · Implement

## 1. Tiến độ

Mọi lệnh chạy trong `frontend/mobile`.

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `flutter test test/core/notification/reminder_sound_catalog_test.dart`: 5 pass | `evidence/implement-P1.log` |
| P2 | xong | `flutter test test/core/notification/reminder_sound_validator_test.dart`: 15 pass | `evidence/implement-P2.log` |
| P3 | xong | `flutter test test/core/notification/reminder_sound_store_test.dart`: 5 pass | `evidence/implement-P3.log` |
| P4 | xong | Lần 1 `flutter build apk --debug` báo `No Android SDK found` (Phát sinh 1). Sau khi cài SDK: exit 0, `√ Built build\app\outputs\flutter-apk\app-debug.apk`; có `ReminderSoundChannel*.class` trong `build/app/tmp/kotlin-classes/debug`. Log có 9 dòng `e: Daemon compilation failed: null` (Kotlin daemon lỗi, Gradle tự biên dịch không qua daemon; build vẫn thành công) | `evidence/implement-P4.log`, `evidence/implement-P4-build.log` |
| P5 | xong | `flutter test test/core/notification/reminder_sound_controller_test.dart` + các test P1–P3: 33 pass | `evidence/implement-P5.log` |
| P6 | xong | `flutter test test/core/notification/reminder_notification_scheduler_test.dart`: 17 pass | `evidence/implement-P6.log` |
| P7 | xong | `flutter test test/core/notification/reminder_sync_coordinator_test.dart`: 9 pass | `evidence/implement-P7.log` |
| P8 | xong | `flutter analyze` file đã đổi: không còn issue mới; `flutter test test/core/notification test/app`: 150 pass, 4 fail, cả 4 fail giống hệt khi chạy trên HEAD sạch `d9f29202` (94 pass, 4 fail) | `evidence/implement-P8.log` |
| P9 | xong | `flutter analyze lib/features/profile test/features/profile`: không issue; `flutter test test/features/profile`: 150 pass, 4 fail, giống hệt HEAD sạch (136 pass, 4 fail); `reminder_sound_screen_test.dart` 14 pass gồm 320/375 px × text scale 1.0/2.0 | `evidence/implement-P9.log` |
| P10 | xong | `flutter test` toàn mobile: +1503 ~2 −93; HEAD sạch `d9f29202`: +1433 ~2 −93; danh sách 93 test fail trùng khớp từng dòng (0 fail mới, 0 fail được sửa). `flutter analyze` toàn mobile: 18 issue, HEAD sạch cũng 18, không issue nào nằm trong file của task. `scope.py --stage implement`: OK | `evidence/implement-final-frontend.log`, `evidence/implement-final-baseline-HEAD.log`, `evidence/implement-final-analyze.log`, `evidence/implement-scope.log` |

Baseline: plan ghi 92 fail có sẵn trên `origin/main`; khi đo lại trên HEAD của nhánh (`d9f29202`, chưa có thay đổi của task) là 93. So sánh dùng số đo lại này.

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/adhoc-20261120-reminder-custom-sound` | `mobile/lib/core/notification/reminder_sound.dart` (mới) |
| | | `mobile/lib/core/notification/reminder_sound_validator.dart` (mới) |
| | | `mobile/lib/core/notification/reminder_sound_store.dart` (mới) |
| | | `mobile/lib/core/notification/reminder_sound_native.dart` (mới) |
| | | `mobile/lib/core/notification/reminder_sound_controller.dart` (mới) |
| | | `mobile/lib/core/notification/notification_service.dart` |
| | | `mobile/lib/core/notification/reminder_notification_scheduler.dart` |
| | | `mobile/lib/core/notification/reminder_sync_coordinator.dart` |
| | | `mobile/lib/main.dart`, `mobile/lib/app/app.dart` |
| | | `mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart` |
| | | `mobile/android/app/src/main/kotlin/vn/drugtime/drugtime_mobile/ReminderSoundChannel.kt` (mới), `MainActivity.kt` |
| | | `mobile/android/app/src/main/res/raw/reminder_{chime,gentle,friendly,urgent}.wav`, `keep.xml` (mới) |
| | | Test: `test/core/notification/reminder_sound_{catalog,validator,store,controller}_test.dart` (mới), `notification_service_test.dart`, `reminder_notification_scheduler_test.dart`, `reminder_sync_coordinator_test.dart`, `test/features/profile/reminder_sound_screen_test.dart` (mới), `profile_widget_helpers.dart`, `profile_flow_navigation_test.dart` |

Không sửa: `profile_flow_visual_test.dart` (vẫn pass vì `profileApp` đã cấp scope), `docs/.../Test_Cases.xlsx` (làm ở giai đoạn test).

## 3. Kết quả test cuối

- Toàn mobile: 1503 pass, 2 skip, 93 fail; 93 fail này đều có sẵn trên HEAD sạch, không có fail mới (`evidence/implement-final-frontend.log`, `evidence/implement-final-baseline-HEAD.log`).
- Test mới/sửa của task: 23 test controller, 14 test màn S08-4a, 5 test scheduler, 2 test coordinator, 1 test service, cùng test P1–P3; tất cả pass.
- Build APK debug: thành công (`evidence/implement-P4-build.log`).
- Chưa chạy: kiểm tra trên máy thật (AC3 phần MediaStore, AC13).

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test (task size M).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

### Quyết định nghiệp vụ / AC → code → test

| AC | Code | Test |
|---|---|---|
| AC1 chọn âm, lưu, lên lịch lại | `ReminderSoundController.select`, `onSoundChanged` → `_refreshReminders` (app.dart), scheduler `soundChannel` | `select saves, creates the channel and reschedules__AC1`; `tapping a sound selects it and keeps it on reopen__AC1`; scheduler group `Selected reminder sound` |
| AC2 nghe thử A rồi B | `togglePreview`, `stopPreview`, native `previewDone` | `preview A then B stops A and plays B; B again stops__AC2`, `preview done from native…__AC2`, `preview A then B stops A; B again stops__AC2` (widget) |
| AC3 thêm file hợp lệ | `addFromDevice` → Kotlin `pick/probe/commit` | `adding a valid file commits a neutral name and a channel__AC3 AC14`; phần MediaStore thật: thủ công |
| AC4 file không hợp lệ | `ReminderSoundValidator`, Kotlin `probe` | group `invalid files are not saved__AC4`, validator test, `invalid file shows its message and saves nothing__AC4` |
| AC5 giới hạn 10 | `maxCustom`, `canAdd`, màn S08-4a | `ten customs lock adding until one is deleted__AC5`, `ten customs lock adding; deleting one after confirm unlocks__AC5 AC6` |
| AC6 xóa âm đang chọn | `delete` | `deleting the selected custom falls back to chime and cleans up__AC6`, widget test AC5 AC6, `deleteNotificationChannel reaches the Android plugin__AC6` |
| AC7 file mất → chuông mặc định | `ensureValid` gọi ở `load()` và hook `beforeSchedule` | `missing custom file falls back to chime with a notice__AC7 AC8`, coordinator hook tests, `missing selected custom shows the fallback notice__AC7` |
| AC8 im lặng chỉ khi tự chọn | `ReminderSounds.fallback = chime` | `unknown stored id falls back to chime, never silent__AC8`, catalog test, scheduler test silent |
| AC9 nhắc lại / snooze | scheduler `_notificationDetails` dùng chung | scheduler group `Selected reminder sound` |
| AC10 giữ các trường thông báo | scheduler | `every sound keeps the alarm presentation unchanged__AC10` |
| AC11 âm lượng → cài đặt hệ thống | `openSoundSettings`, Kotlin `ACTION_SOUND_SETTINGS` | `openSoundSettings goes to native__AC11`, `volume row opens system sound settings, no slider__AC11` |
| AC12 iOS / Android < 10 | `customSupported`, màn S08-4a giữ trạng thái chưa khả dụng trên iOS | `custom sounds need Android 10+__AC12 Q2`, `iOS hides custom sounds…__AC12` (controller + widget), `Android 9 shows built-in sounds without the custom group__AC12` |
| AC13 thiết bị thật | — | thủ công, chưa chạy |
| AC14 tên trung tính | id `custom_<16 hex>`, MediaStore `DrugTime nhắc nhở <n>` | test AC3 AC14, store test |
| AC15 hủy trình chọn file | `pick` trả null | `cancelling the picker changes nothing__AC15`, `cancelling the picker shows nothing__AC15` |
| Q1 xóa khi đăng xuất | `clearAll` trong `beforeSignOut` (main.dart) | `clearAll removes every custom and resets to chime__Q1` |

### Nguồn âm thanh, license, checksum

Bốn âm có sẵn do team tự tổng hợp bằng numpy (sóng sin có envelope), không dùng tài nguyên bên thứ ba nên không có ràng buộc license. Script sinh nằm ở `work/adhoc-20261120-reminder-custom-sound/scratch/gen_tones.py` (thư mục scratch, không commit; giữ lại nếu cần sinh lại).

| File | Byte | sha256 |
|---|---|---|
| `reminder_chime.wav` | 57644 | `452a0991036d8dbd47bdc6ee64c77d1fcd7884e134acaac2b1f3e23dbb318059` |
| `reminder_friendly.wav` | 48044 | `f5685cf9a2da38e81b8c9e7832626ffc28e867b00e44f81f92879ba14c4748a4` |
| `reminder_gentle.wav` | 70444 | `e7799072246d0fe0b5dcae016cf030a8ea2106821bc20a9aaabd520d990bdff5` |
| `reminder_urgent.wav` | 54444 | `5aef241f555ceeba6dd05588bafd5ed457d9ea130b1c5200fdd74012aa43dcbe` |

### Điểm nên xem kỹ

- `ReminderSoundChannel.kt` đã biên dịch qua build APK debug nhưng chưa chạy trên thiết bị; hành vi native (trình chọn file, MediaStore, phát âm) kiểm ở giai đoạn test.
- Channel Android không đổi âm được sau khi tạo, nên mỗi âm có channel riêng (`drugtime_reminder_<id>`); channel cũ `reminderChannelId` vẫn được dùng khi scheduler không có `soundChannel` (giữ tương thích test cũ).
- Lỗi khi kiểm tra file tồn tại bị coi như file đã mất → về chuông mặc định (nhắc thuốc phải chắc chắn có âm).
- Màn S08-4a: banner lỗi thêm file đặt ngay trên nút "+ Thêm âm thanh từ máy" (người dùng đang ở cuối danh sách khi bấm thêm); banner "đã chuyển về chuông mặc định" ở đầu màn.
- `dart format` chỉ áp lên phần mã của task; các hunk formatter đụng mã cũ đã được hoàn lại để diff gọn. Riêng `profileApp` trong `profile_widget_helpers.dart` bị thụt lề lại vì được bọc thêm `ReminderSoundScope`.

## 6. Phát sinh

1. **Ban đầu không build được APK**: Android SDK tại `C:\Users\VietD\AppData\Local\Android\Sdk` có `platforms/` và `build-tools/` rỗng. Được người dùng cho phép, agent đã chấp nhận Android SDK License, cài `platforms;android-36`, `build-tools;36.0.0`, `platform-tools`, `ndk;28.2.13676358` bằng `sdkmanager` và chạy `flutter config --android-sdk`. Build sau đó thành công. Còn lại: AC3 phần MediaStore và AC13 cần máy Android 10+ thật.
2. **Âm có sẵn là WAV, không phải `.ogg` như plan.** Máy không có bộ mã hóa ogg; WAV phát được trên mọi phiên bản Android, đổi đuôi không đổi hành vi. File vẫn nằm trong glob `res/raw/**` của plan. Có thể chuyển sang ogg sau để giảm dung lượng (~230 KB tổng).
3. **`clearAll()` gắn ở `beforeSignOut` trong `main.dart` thay vì nhánh logout trong `app.dart`.** Cùng file trong phạm vi. Hệ quả: chạy khi người dùng tự đăng xuất, không chạy khi phiên hết hạn (401); khi đăng nhập lại cùng máy, âm tự thêm vẫn còn. Nếu muốn xóa cả khi hết phiên, cần gọi thêm ở nhánh 401 của `app.dart`.
4. **Lỗi commit file dùng thông báo chung** `Không thêm được âm thanh, vui lòng thử lại` (`ReminderSoundController.addFailedMessage`); AC4 không quy định thông báo cho lỗi ghi file/MediaStore.
5. **Baseline đo lại là 93 fail** (plan ghi 92). Danh sách fail trên nhánh trùng khớp HEAD sạch.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: duyệt implement bằng `python .agents/scripts/gate.py approve adhoc-20261120-reminder-custom-sound implement`, sau đó chạy giai đoạn test (`wf-test`, gồm bộ test case Excel và AC13 thủ công).
- Cập nhật lần cuối: 2026-11-20, Claude Code
