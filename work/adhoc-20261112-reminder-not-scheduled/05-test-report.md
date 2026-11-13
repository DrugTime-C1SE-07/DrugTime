---
task: adhoc-20261112-reminder-not-scheduled
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-13 16:29 +0700
content_hash: sha256:210e9f334c4b4697
inputs:
  01-requirement.md: sha256:6b92750b479c1d4b
  03-plan.md: sha256:20d603a93ddf82f9
  04-impl-notes.md: sha256:799e77ed366cf960
---

# adhoc-20261112-reminder-not-scheduled · Test tích hợp

> Vòng 3 (2026-11-13), sau khi sửa M3 (chỉ xin quyền lần đầu sau khi cài, plan mục 1c). Số liệu dưới đây là của vòng 3; log vòng 1, 2 vẫn giữ trong `evidence/`.

## 1. Môi trường

- Lệnh chuẩn bị: không có. Task chỉ đổi client `frontend/mobile`; không đổi backend, schema hay contract, nên không reset DB hay khởi động service.
- Nhánh: frontend `fix/adhoc-20261112-reminder-not-scheduled` (từ `origin/main` @ `f7c2efb4`, thay đổi implement chưa commit).
- Thiết bị: LG G710 (Android 13) có kết nối, nhưng người dùng tự chạy case thủ công; chưa có kết quả gửi về, nên các case thủ công vẫn `Pending`. Chưa có máy Android 14+.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test | Kết quả |
|---|---|---|
| AC1 (hồi quy) | `reminder_sync_coordinator_test` "refresh schedules full-screen reminders…", `api_schedule_remote_data_source_test` (7 test, gồm 3 test sai kiểu L1), `reminder_wiring_test` | pass |
| AC2 | `reminder_notification_scheduler_test` nhóm `snooze` (2 test); `reminder_sync_coordinator_test` "refresh keeps a snoozed reminder…" (hồi quy H1) | pass (tự động); trên thiết bị: chưa chạy (TC-REMIND-16) |
| AC3 | `reminder_sync_coordinator_test` "refresh cancels reminders of a schedule removed…", "refresh skips occurrences already recorded…" (M2), `medication_controller_test` "ghi thành công gọi onChanged…", `reminder_wiring_test` "a successful medication change refreshes reminders again" (L2) | pass |
| AC4 | `reminder_wiring_test` (thứ tự quyền: thông báo rồi toàn màn hình, M1; lần đầu sau khi cài thì hỏi, đã hỏi rồi thì không hỏi nhưng vẫn `refresh`, M3); `notification_service_test` nhóm `requestNotificationsPermission` (2 test); `secure_storage_test` (M3) | pass (tự động); trên thiết bị: chưa chạy (TC-REMIND-13, -18) |
| AC5 | Thủ công Android 14+ (TC-REMIND-14, -15) | chưa chạy, cần thiết bị |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Gửi lại cùng `client_uuid` → một bản ghi liều (vùng "Ghi nhận liều và đồng bộ") | `sync_engine_test` hiện có, chạy lại; task không đổi outbox | pass |
| Truy cập chéo patient → 403 + `denied` | Không áp dụng trực tiếp: task dùng endpoint `GET /patients/{id}/schedules` có sẵn (PEP ở backend), không đổi backend. Client xử lý 403 bằng cách báo lỗi và giữ lịch cục bộ: `api_schedule_remote_data_source_test` "propagates API errors" | pass |
| Rút consent / hủy liên kết, các kịch bản Worker và tương tác thuốc | Không áp dụng: không chạm vùng đó | — |

## 4. Toàn bộ bộ test tích hợp

- Lệnh: `cd frontend/mobile && flutter test <9 file liên quan> -j 1 -r expanded` (coordinator, data source, wiring, medication controller, scheduler, notification service, schedule sync, sync engine, secure storage). Chạy tuần tự để log ghi đúng tên từng test.
- Kết quả: 81 pass, 0 fail, 0 skip. Log: `evidence/test-integration-r3.log`.
- Toàn bộ `flutter test` của mobile đã chạy ở implement vòng 3: 1045 pass, 1 skip, 5 fail có sẵn trên `main` (`evidence/implement-final-frontend-r3.log`, `evidence/implement-final-frontend-r3-failures.log`, so với `evidence/implement-baseline-main-failures.log`).
- Bộ tích hợp backend (`backend/tests/integration`) **không chạy**: task không đổi backend, máy không có `supabase` CLI.
- `scope.py --stage test`: 13 file `frontend/mobile/**` báo `[NGOÀI]`; đó là thay đổi của implement (đều `[OK]` ở `--stage implement`, chưa commit). Giai đoạn test không sửa file sản phẩm hay test. Log: `evidence/test-scope-r3.log`.

## 5. Bộ test case Excel

- Spec: `testcases.json` · File task: `testcases.xlsx` · File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` — **chưa merge** (PT1).
- Log: `evidence/testcase-xlsx-r3.log` (`validate`, `build` exit 0)

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Nhắc uống thuốc toàn màn hình (REMIND, mới) | 26 | 20 | 0 | 6 |

- Thêm ở vòng 2: TC-REMIND-19 (H1 giữ nhắc hoãn cữ), -20 (M2 bỏ liều đã ghi nhận), -21 (L1 sai kiểu → `ApiException`), -22, -23 (M1 xin quyền thông báo), -24 (L2 sửa thuốc lập lại nhắc). Cập nhật TC-REMIND-10 (thứ tự quyền).
- Thêm ở vòng 3: TC-REMIND-25 (đã hỏi quyền thì không hỏi lại, vẫn lập nhắc), -26 (cờ chỉ `true` lần đầu, giữ qua lần mở sau). Sửa TC-REMIND-13: thêm bước đóng hẳn app rồi mở lại, kỳ vọng không hỏi lại.
- Test case `Pending` cần người chạy trên Android 14+: TC-REMIND-13…18 (không đổi). TC-REMIND-13 giờ kiểm cả hộp thoại quyền thông báo do app tự xin (M1).
- Bug đã ghi vào Bug Report: không có.

## 5b. Lỗi sản phẩm tìm thấy

Không có.

## 6. Test không ổn định hoặc bị skip

- Không có test không ổn định trong các lần chạy của task.
- 5 test fail có sẵn trên `main` (vùng người thân), ngoài phạm vi; xem `04-impl-notes.md` PS2.

## 7. Phát sinh

- **PT1 — Chưa merge vào file tổng.** Submodule `docs` đang detached HEAD @ `965ace0` và có thay đổi chưa commit không thuộc task (xóa `Product-and-Sprint-backlog-DrugTime.xlsx`, thêm `.ods`). Theo `wf-git`, không đụng thay đổi của người khác. Khi `docs` sạch hoặc người dùng đồng ý, chạy `python .agents/scripts/testcase_xlsx.py merge adhoc-20261112-reminder-not-scheduled` trên nhánh `fix/adhoc-20261112-reminder-not-scheduled` của `docs`.
- **PT2 — Kiểm thử trên thiết bị (P8) chưa làm.** Người dùng tự chạy TC-REMIND-13…17 trên LG Android 13; TC-REMIND-18 và phần Android 14 của TC-13 cần máy Android 14+. Kết quả cập nhật vào `testcases.json` (TC-REMIND-13…18) rồi build lại; ghi `evidence/test-device-android14.md`.

## Bước tiếp theo

- Đang chờ: người duyệt (và người dùng chạy TC-REMIND-13…18 trên thiết bị)
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261112-reminder-not-scheduled test`; sau đó review lại (`wf-review`, nên ở phiên/tool khác). Merge file tổng khi `docs` sạch (PT1).
- Cập nhật lần cuối: 2026-11-13, Claude Code
