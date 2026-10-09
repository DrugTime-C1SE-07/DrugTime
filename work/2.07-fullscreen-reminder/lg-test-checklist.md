# Checklist kiểm thử Full-Screen Intent trên LG G7 ThinQ (Android 13)

Thiết bị: **LG G7 ThinQ (LM-G710)**, Android 13 (API 33, Build TQ3A.230901.001), Device ID: `LMG7103f11b938`.  
Package ID: `vn.drugtime.drugtime_mobile`.

---

## 1. Chuẩn bị & Cài đặt lên thiết bị

### 1.1. Lệnh cài đặt bản build độc lập (KHÔNG dùng `flutter run`)
Để kiểm tra chính xác các trạng thái app bị tắt, màn hình tắt và vuốt khỏi recents mà không bị ảnh hưởng bởi tiến trình gỡ lỗi (debug bridge / vmservice), bắt buộc build APK rồi install:
```powershell
cd frontend/mobile
flutter build apk --debug
flutter install -d LMG7103f11b938
```
*(Nếu cài trực tiếp qua adb: `adb -s LMG7103f11b938 install -r build/app/outputs/flutter-apk/app-debug.apk`)*.

---

### 1.2. Kiểm tra quyền hệ thống trên LG G7 (CẦN KIỂM TRÊN LG)
ROM tùy biến của LG G7 (TQ3A.230901.001) có thể có chính sách cấp quyền khác với AOSP tiêu chuẩn. Cần kiểm tra và ghi lại trạng thái thực tế:

1. **Quyền `USE_FULL_SCREEN_INTENT`**:
   ```powershell
   adb -s LMG7103f11b938 shell cmd appops get vn.drugtime.drugtime_mobile USE_FULL_SCREEN_INTENT
   ```
   - **Cần kiểm trên LG**: Quyền này có được cấp mặc định khi cài xong không?
   - Kết quả thực tế: `[CẤP MẶC ĐỊNH / BỊ TẮT / KHÔNG CÓ TRONG APPOPS]`

2. **Quyền `SCHEDULE_EXACT_ALARM`**:
   ```powershell
   adb -s LMG7103f11b938 shell cmd appops get vn.drugtime.drugtime_mobile SCHEDULE_EXACT_ALARM
   ```
   - Kết quả thực tế: `[allow / default / ignore]`

3. **Cài đặt Pin & Tự khởi chạy trên ROM LG**:
   - Vào **Cài đặt > Ứng dụng > DrugTime > Pin**: Chọn **Không hạn chế (Unrestricted)** để tránh ROM LG kill app ngầm.

---

## 2. Các kịch bản kiểm thử (Test Cases)

### Kịch bản A: Thiết bị đang ở màn hình khóa (Lock Screen)
- **Thiết lập**: Bật app, đặt thông báo thử nghiệm sau 1 phút. Nhấn nút nguồn để màn hình khóa lại (máy có mã PIN/Pattern hoặc vuốt khóa).
- **Hành vi mong đợi**:
  - Đúng 60 giây, chuông và rung thông báo kích hoạt.
  - Activity của DrugTime tự động hiển thị đè lên màn hình khóa (`showWhenLocked = true`).
  - **Bảo mật NT-02 qua `LockscreenPrivacyGate`**: Màn hình hiển thị Privacy Mask (chỉ hiện "Đến giờ uống thuốc", nút "Mở khóa thiết bị để xem chi tiết / xác nhận", và nút nhanh "Đã uống cữ này"). Tuyệt đối **KHÔNG** lộ tên thuốc hay liều dùng.
  - Bấm "Mở khóa thiết bị": Hệ thống yêu cầu mở khóa (PIN/vân tay). Sau khi mở khóa, màn hình bung đầy đủ `DoseReminderScreen` chứa danh sách các thuốc cần uống.
- **Cách ghi lại bằng chứng**:
  ```powershell
  adb -s LMG7103f11b938 logcat -d -s ActivityTaskManager FlutterLocalNotificationsPlugin > work/2.07-fullscreen-reminder/evidence/test-A-lockscreen.log
  ```

---

### Kịch bản B: Thiết bị tắt màn hình (Screen Off / Sleep)
- **Thiết lập**: Đặt thông báo sau 1 phút. Nhấn nút nguồn để tắt hẳn màn hình điện thoại (màn hình đen, máy vào chế độ ngủ).
- **Hành vi mong đợi**:
  - Đúng giờ hẹn, màn hình điện thoại tự động **bật sáng** (`turnScreenOn = true`).
  - Activity hiển thị đè lên màn hình khóa với giao diện bảo vệ của `LockscreenPrivacyGate` như Kịch bản A.
- **Cách ghi lại bằng chứng**: Quan sát thực tế màn hình sáng lên và lưu logcat.

---

### Kịch bản C: Ứng dụng bị vuốt tắt khỏi danh sách gần đây (App Swiped from Recents)
- **Lưu ý quan trọng**: Chỉ vuốt app khỏi màn hình Đa nhiệm (Recents / Overview). **TUYỆT ĐỐI KHÔNG** dùng lệnh `adb shell am force-stop` vì lệnh force-stop của Android sẽ xóa sạch mọi báo thức trong `AlarmManager`.
- **Thiết lập**: Đặt thông báo sau 1 phút. Mở giao diện đa nhiệm của Android và vuốt tắt DrugTime. Nhấn nút nguồn khóa màn hình.
- **Hành vi mong đợi**:
  - Đến giờ hẹn, `ScheduledNotificationReceiver` bắt Alarm broadcast, kích hoạt Full-Screen Intent khởi động app (`cold start`) lên màn hình khóa.
  - `LockscreenPrivacyGate` bảo vệ thông tin thuốc.
- **Cách ghi lại bằng chứng**:
  ```powershell
  adb -s LMG7103f11b938 logcat -d | Select-String "drugtime" > work/2.07-fullscreen-reminder/evidence/test-C-recents.log
  ```

---

### Kịch bản D: Thiết bị đang mở khóa và người dùng đang ở app khác (Unlocked / Other App in Foreground)
- **Thiết lập**: Đặt thông báo sau 1 phút. Nhấn Home và mở ứng dụng khác (ví dụ Chrome hoặc Cài đặt). Thiết bị vẫn đang mở khóa và người dùng đang tương tác bình thường.
- **Hành vi mong đợi**:
  - Đến giờ hẹn, hệ điều hành Android **KHÔNG** bật toàn màn hình làm gián đoạn người dùng.
  - Thay vào đó, Android hiển thị **Heads-Up Banner** (banner nổi) ở đỉnh màn hình có tiêu đề "Đến giờ uống thuốc" và nút action "Đã uống".
  - Người dùng có thể nhấn vào banner để mở ứng dụng vào màn xác nhận liều, hoặc bấm "Đã uống" ngay trên banner.
- **Cách ghi lại bằng chứng**: Chụp ảnh màn hình heads-up banner:
  ```powershell
  adb -s LMG7103f11b938 exec-out screencap -p > work/2.07-fullscreen-reminder/evidence/test-D-headsup.png
  ```

---

### Kịch bản E: Ứng dụng DrugTime đang mở trực tiếp (Foreground)
- **Thiết lập**: Người dùng đang mở sẵn ứng dụng DrugTime trên màn hình.
- **Hành vi mong đợi**:
  - Đến giờ hẹn, ứng dụng bắt sự kiện thông báo qua callback và **tự động chuyển hướng (navigate)** thẳng vào màn hình xác nhận liều `AppRoutes.doseReminder` (tuân thủ NT-11).
- **Cách ghi lại bằng chứng**: Giao diện tự động chuyển cảnh vào màn hình nhắc liều thuốc.

---

## 3. Bảng tổng hợp kết quả kiểm thử trên LG G7

| Ca kiểm thử | Trạng thái thiết bị | Kỳ vọng hiển thị | Kết quả thực tế trên LG G7 | Đạt? |
|---|---|---|---|---|
| A | Màn hình khóa | Sáng màn hình, hiện Activity đè khóa, LockscreenPrivacyGate che tên thuốc | Chờ kiểm thử | [ ] |
| B | Màn hình tắt | Tự động bật sáng màn hình, hiện Activity | Chờ kiểm thử | [ ] |
| C | Vuốt tắt khỏi Recents | Vẫn nổ báo thức, cold start Activity đè khóa | Chờ kiểm thử | [ ] |
| D | Mở khóa, app khác mở | Hiện Heads-Up Banner nổi ở đầu màn hình | Chờ kiểm thử | [ ] |
| E | App đang foreground | Tự động điều hướng vào màn xác nhận liều | Chờ kiểm thử | [ ] |
| Quyền | Quyền Full-Screen Intent | Cần kiểm tra trạng thái mặc định trên LG | Chờ kiểm tra | [ ] |

---

## 4. Kết quả kiểm thử thực tế trên Realme Q (Android 11 - API 30)

Thiết bị: **Realme Q (RMX1971)**, Android 11 (API 30), Device ID: `dc278021`.  
Package ID: `vn.drugtime.drugtime_mobile`.

### 4.1. Trạng thái cấp quyền hệ thống
- `android.permission.USE_FULL_SCREEN_INTENT`: Được hệ thống Android 11 cấp mặc định (`granted=true`).
- `SCHEDULE_EXACT_ALARM`: Android 11 (API 30) chưa giới hạn appop này (xuất hiện từ API 31), cho phép đặt Exact Alarm bình thường.
- Cài đặt thông báo: Kênh `drugtime_reminder_channel` ("Nhắc uống thuốc") đã được kích hoạt đầy đủ: Màn hình khóa, Biểu ngữ nổi (Heads-up), Nhạc chuông, Rung. (Ảnh: `evidence/realme-notif-enabled.png`).

### 4.2. Bảng kết quả thực nghiệm trên thiết bị Realme Q

| Ca kiểm thử | Trạng thái thiết bị | Kỳ vọng hiển thị | Kết quả thực tế trên Realme Q | Đạt? | Bằng chứng |
|---|---|---|---|---|---|
| **A** | Màn hình khóa (Keyguard Locked) | Sáng màn hình, hiện Activity đè khóa; **bảo mật NT-02**: che toàn bộ tên thuốc, chỉ hiện Privacy Gate | `LockscreenPrivacyGate` kích hoạt: Icon ổ khóa, "Đến giờ uống thuốc", ẩn hoàn toàn tên thuốc và liều dùng, có nút "Mở khóa thiết bị". | **ĐẠT (PASS)** | `evidence/realme-test-A-lockscreen-privacy.png` |
| **B** | Màn hình tắt (Screen Off / Sleep) | Màn hình tự động bật sáng (`turnScreenOn = true`), Activity đè lên màn khóa | Màn hình tự động bật sáng (`mWakefulness=Awake`, `Display Power: state=ON`), chuông reo, rung, hiện màn hình nhắc thuốc. | **ĐẠT (PASS)** | `evidence/realme-full-screen-result.png` |
| **C** | Tương tác mở khóa (Unmask after Unlock) | Sau khi người dùng mở khóa máy, giao diện tự động bung chi tiết thuốc | Sau khi mở khóa qua Keyguard prompt / vuốt mở khóa, màn hình tự động unmask và hiện `DoseReminderScreen` (Panadol Extra 500mg, 1 viên sau ăn, nút "Đã uống", "Nhắc lại", "Bỏ qua"). | **ĐẠT (PASS)** | `evidence/realme-test-A-unmasked-after-unlock.png` |
| **D** | Mở khóa, app khác hoặc home | Xuất hiện **Heads-Up Banner** nổi ở đỉnh màn hình, không cướp toàn màn hình | Banner thông báo trắng nổi ở đỉnh màn hình ("Nhắc uống thuốc: Đã đến giờ uống thuốc theo lịch", nút action "ĐÃ UỐNG"). | **ĐẠT (PASS)** | `evidence/realme-test-D-headsup.png` |
| **E** | Nút Action Uống nhanh | Bấm nút action "ĐÃ UỐNG" trên thông báo | Callback `NotificationService` nhận `take_dose_action`, `ReminderNotificationScheduler` ghi nhận uống cữ thuốc thành công. | **ĐẠT (PASS)** | Nhật ký sự kiện trên màn hình `realme-full-screen-result.png` |

