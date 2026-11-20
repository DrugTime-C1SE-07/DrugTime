---
task: adhoc-20261120-reminder-custom-sound
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-20 10:18 +0700
content_hash: sha256:1bb2aec62c959ea6
inputs:
  01-requirement.md: sha256:0d751fb5dbc8c598
  03-plan.md: sha256:0f448eed59ca405c
  04-impl-notes.md: sha256:3ac2f8e47e35dab4
---

# adhoc-20261120-reminder-custom-sound · Test tích hợp

## 1. Môi trường

- Task chỉ đổi `frontend/mobile`, không chạm backend, API, DB hay vùng rủi ro trong `AGENTS.md` (`01` mục 6, `03` mục 5 "Tích hợp: Không có"). Không reset DB, không khởi động service; không có test mới trong vùng `integration-test` (`tests`, `backend/tests/integration`, `backend/tests/interaction_scenarios`).
- Máy: Windows 11, Flutter từ `D:\Captone\flutter`, Android SDK `%LOCALAPPDATA%\Android\Sdk` (android-36, build-tools 36.0.0, NDK 28.2.13676358).
- Nhánh: frontend `feat/adhoc-20261120-reminder-custom-sound` (code của implement, chưa commit); docs `feat/adhoc-20261120-reminder-custom-sound` tạo từ `origin/main` (`ebff569`).

## 2. Kết quả theo tiêu chí chấp nhận

Mọi test tự động dưới đây chạy trong lần `flutter test` toàn mobile ở mục 4 và pass.

| AC | Test | Kết quả |
|---|---|---|
| AC1 | `select saves, creates the channel and reschedules__AC1`; `tapping a sound selects it and keeps it on reopen__AC1`; `occurrences and snooze use the selected channel__AC1 AC9`; `changing the selection applies to the next schedule__AC1`; store `round-trips selection…__AC1` | pass |
| AC2 | `preview A then B stops A and plays B; B again stops__AC2`; `preview done from native clears the playing state__AC2`; widget `preview A then B stops A; B again stops__AC2`; `leaving the screen stops the preview` | pass |
| AC3 | `adding a valid file commits a neutral name and a channel__AC3 AC14` (native giả lập) | pass; phần MediaStore thật: Pending (TC-RSOUND-07) |
| AC4 | group `invalid files are not saved__AC4` (4 thông báo); validator `formatOf__AC4`, `checkFile__AC4` (2097152 nhận, 2097153 từ chối), `checkDuration__AC4` (1000/30000 nhận, 999/30001 từ chối); widget `invalid file shows its message and saves nothing__AC4`; `commit failure shows a retry message…` | pass |
| AC5 | `ten customs lock adding until one is deleted__AC5`; widget `ten customs lock adding; deleting one after confirm unlocks__AC5 AC6` | pass |
| AC6 | `deleting the selected custom falls back to chime and cleans up__AC6`; `deleteNotificationChannel reaches the Android plugin__AC6`; widget AC5 AC6 | pass |
| AC7 | `missing custom file falls back to chime with a notice__AC7 AC8`; `beforeSchedule runs before scheduling and its fallback applies__AC7`; `a failing beforeSchedule is logged and reminders are still scheduled__AC7`; widget `missing selected custom shows the fallback notice__AC7` | pass; trên máy thật: Pending (TC-RSOUND-23) |
| AC8 | `unknown stored id falls back to chime, never silent__AC8`; `silent keeps vibration and plays no sound__AC8`; `silent channel has no sound but vibrates__AC8` | pass |
| AC9 | `occurrences and snooze use the selected channel__AC1 AC9` | pass; nghe trên máy thật: Pending (TC-RSOUND-22) |
| AC10 | `every sound keeps the alarm presentation unchanged__AC10`; `without a sound source the existing reminder channel is used__AC10` | pass |
| AC11 | `openSoundSettings goes to native__AC11`; `volume row opens system sound settings, no slider__AC11` | pass |
| AC12 | `custom sounds need Android 10+__AC12 Q2`; `iOS hides custom sound…__AC12` (controller + widget); `Android 9 shows built-in sounds without the custom group__AC12` | pass |
| AC13 | Thủ công (a)–(h) | Pending: cần máy Android 10+ thật; (h) bị chặn bởi lỗi build release có sẵn (mục 7) |
| AC14 | `adding a valid file commits a neutral name…__AC3 AC14`; `stored data never contains the original file name__AC14` | pass |
| AC15 | `cancelling the picker changes nothing__AC15`; `cancelling the picker shows nothing__AC15` | pass |
| Q1 | `clearAll removes every custom and resets to chime__Q1` | pass (mức controller); trên máy thật: Pending (TC-RSOUND-24) |

Không có AC mức `integration`.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Không áp dụng: task không chạm dữ liệu sức khỏe qua API, phân quyền người thân, ghi nhận liều/đồng bộ, tương tác thuốc, schema, ranh giới module backend hay bí mật | — | — |
| Lưu ý an toàn của `01`: lỗi làm nhắc không kêu (High) | AC7, AC9, AC10 ở trên; nghe thật ở TC-RSOUND-22, TC-RSOUND-23 | pass tự động; phần thiết bị Pending |

## 4. Toàn bộ bộ test tích hợp

- Bộ test tích hợp backend/E2E: không chạy. Task không đổi file nào trong vùng `integration-test` hay backend; máy hiện không có `docker`/`supabase` để chạy `supabase start`. Đây là bỏ qua có lý do, không phải test bị skip.
- Bộ test của submodule bị sửa: `cd frontend/mobile && flutter test`
  - Kết quả: 1503 pass, 2 skip, 93 fail, 3 phút 42 giây. 93 test fail trùng khớp từng dòng với danh sách chạy trên HEAD sạch `d9f29202` ở giai đoạn implement; không có fail mới, không có fail thuộc file của task.
  - Log: `evidence/test-mobile-full.log`, danh sách fail `evidence/test-mobile-failed-list.log`, baseline `evidence/implement-final-baseline-HEAD.log`.
- `flutter build apk --release`: fail (mục 7), log `evidence/test-release-build.log`.
- `scope.py --stage test`: báo 28 file `[NGOÀI]` (mục 7). Log `evidence/test-scope.log`.

## 5. Bộ test case Excel

- Spec: `testcases.json` · File task: `testcases.xlsx` · File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (sheet mới "Âm thanh nhắc nhở", mã `RSOUND`)
- Log: `evidence/testcase-xlsx.log` (validate, build, merge đều exit 0, không có cảnh báo ghi đè)

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Âm thanh nhắc nhở (RSOUND) | 30 | 25 | 0 | 5 |

- Test case `Pending` cần người chạy trên máy Android 10+ thật:
  - TC-RSOUND-07: âm vừa thêm có trong danh sách âm thông báo hệ thống tên `DrugTime nhắc nhở 1` (AC3, AC14).
  - TC-RSOUND-21: bản release còn đủ 4 âm trong `res/raw` (AC13 h). Bị chặn cho tới khi build release chạy được.
  - TC-RSOUND-22: nghe đúng âm ở lượt nhắc và snooze; Im lặng chỉ rung (AC9, AC13 a/c/e/f).
  - TC-RSOUND-23: xóa file bằng app quản lý file → thông báo quay về, nhắc kế tiếp kêu Chuông mặc định (AC7, AC13 d).
  - TC-RSOUND-24: đăng xuất xóa bản MediaStore (Q1, AC13 g).
  - Khi chạy, ghi hãng và phiên bản Android đã thử vào file tổng (rủi ro hãng xử lý MediaStore khác nhau trong `03`).
- Bug đã ghi vào Bug Report: không có.

## 5b. Lỗi sản phẩm tìm thấy

Không có lỗi của task. Lỗi có sẵn ngoài task ở mục 7.

## 6. Test không ổn định hoặc bị skip

- 2 test skip trong bộ mobile là skip có sẵn, không thuộc task.
- Không test nào của task bị skip hay nới lỏng.

## 7. Phát sinh

1. **`flutter build apk --release` fail ở R8**: `ERROR: R8: Missing class com.google.mlkit.vision.text.chinese.ChineseTextRecognizerOptions$Builder` (và các ngôn ngữ devanagari, japanese, korean), tham chiếu từ plugin OCR `google_mlkit_text_recognition`. Task không đụng OCR hay cấu hình Gradle/ProGuard, nên đây là lỗi có sẵn của dự án (suy luận từ nội dung lỗi; chưa build release trên HEAD sạch để xác nhận). Hệ quả: chưa kiểm được `keep.xml` giữ âm trong bản release (TC-RSOUND-21). Đề xuất: task riêng thêm keep rule từ `build/app/outputs/mapping/release/missing_rules.txt` (`-dontwarn com.google.mlkit.vision.text.**`) vào `android/app/proguard-rules.pro`.
2. **`scope.py --stage test` báo 28 file `[NGOÀI]`**. Script so toàn bộ thay đổi của nhánh với `origin/main`; ở giai đoạn test chỉ chấp nhận vùng `integration-test` và `testcase-book`, nên 28 file code đã implement đều bị tính. Giai đoạn test không sửa file nào trong số đó; `scope.py --stage implement` chạy lại cho kết quả `OK: mọi thay đổi nằm trong phạm vi.` (`evidence/test-scope-implement-recheck.log`). Thay đổi duy nhất của giai đoạn test ngoài `work/` là `docs/.../Test_Cases.xlsx` (`[OK]`).
3. **Xung đột file Excel tổng với PR S08.** Nhánh docs của task này tạo từ `origin/main`; nhánh docs `feat/adhoc-20261119-profile-s08-figma-align` (chưa merge) cũng sửa `Test_Cases.xlsx`. File binary nên git không tự gộp được. PR nào merge sau thì chạy lại `python .agents/scripts/testcase_xlsx.py merge <task-id>` của task đó trên nhánh đã cập nhật main, thay vì gộp tay.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: xem Phát sinh 2 (scope báo ngoài phạm vi do cách script tính ở giai đoạn test); nếu đồng ý, duyệt bằng `python .agents/scripts/gate.py approve adhoc-20261120-reminder-custom-sound test`. Sau đó review (`wf-review`, nên chạy phiên mới). Song song: chạy 5 test case Pending trên máy thật và cập nhật file tổng.
- Cập nhật lần cuối: 2026-11-20, Claude Code
