---
task: 2.24-mobile-outbox
stage: plan
status: draft
---

# Kế hoạch Triển khai: SCRUM-54 (Task 2.24 — Mobile Outbox)

## 1. Mục tiêu (Goal Description)
Xây dựng hàng đợi xác nhận liều uống ngoại tuyến (**Mobile Outbox**) cho ứng dụng DrugTime nhằm đảm bảo:
- **Lưu trữ bền vững (Offline-first):** Khi người dùng bấm "Đã uống", bản ghi được lưu ngay vào SQLite cục bộ (`LocalDb`) ở trạng thái `pending_upload` trước khi gọi mạng.
- **Bất biến & Chống trùng (Atomic Idempotent):** Khử trùng theo `client_uuid` và cặp `(medication_schedule_id, scheduled_at)`. Sử dụng cơ chế `INSERT OR IGNORE` nguyên bản của SQLite làm trọng tài atomic: Nếu bấm đúp hoặc background isolate chạy cùng lúc, hệ thống luôn giữ nguyên bản ghi cũ (không ghi đè `taken_at`) và trả về `client_uuid` ban đầu.
- **Cập nhật phản ứng cho giao diện (Reactive UI):** Cung cấp `Stream<DoseLogSyncState?> watchStatus(String clientUuid)` để giao diện cập nhật ngay trạng thái (`pending_upload` ➔ `synced` / `failed`).
- **Tích hợp tương thích ngược với `SyncEngine`:** Cho phép `DoseOutboxSyncEngine` nhận `DoseOutbox` tùy chọn mà không phá vỡ chữ ký cũ hay làm gãy các unit test hiện có của Bao.

---

## 2. Các quyết định kiến trúc & Quy tắc kỹ thuật chi tiết

1. **Kiến trúc phân lớp & Khả năng tiêm Database (Dependency Injection):**
   - Tách riêng interface `DoseOutbox` bọc ngoài `LocalMedicationStore`.
   - `SqliteDoseOutbox` nhận `Future<Database> Function() getDatabase` qua constructor (không phụ thuộc vào `LocalMedicationStore` để tự chủ toàn bộ câu lệnh SQL):
     - Trong ứng dụng: Nhận `() => localDb.database`.
     - Trong unit test: Nhận `() async => testDatabase` (database mở từ `sqflite_common_ffi`), không cần giả lập `LocalDb` hay `SecureStorage`.
   - > [!WARNING]
     > **Cảnh báo ranh giới module (Team Notice):** `LocalMedicationStore.upsertDoseLog` hiện tại đang ghi đè `taken_at` khi trùng khóa. Do đó, Task 2.07 (Scheduler) và Task 2.11 (Confirmation UI) **tuyệt đối không được gọi `upsertDoseLog` trực tiếp** để ghi nhận liều, mà bắt buộc phải đi qua `DoseOutbox.enqueue`.
   - Trong `sync_engine.dart`: Thêm tham số tùy chọn `DoseOutbox? outbox` vào constructor `DoseOutboxSyncEngine`. Nếu có `outbox` thì gọi qua `outbox`, nếu không thì fallback gọi `_localStore`. Giữ nguyên 100% test hiện có của Bao.
2. **Atomic Idempotency bằng `INSERT OR IGNORE`:**
   - Cú pháp: `INSERT OR IGNORE INTO local_dose_logs (...) VALUES (...)` rồi `SELECT` lại dòng theo cặp khóa `(medication_schedule_id, scheduled_at)`.
   - **Xử lý nuốt lỗi:** Nếu câu `SELECT` sau đó không tìm thấy bản ghi nào ➔ ném `StateError('Failed to insert or retrieve dose log')` ngay lập tức, không trả về null im lặng.
   - **Bảo toàn `taken_at`:** Nếu bản ghi đã tồn tại từ trước, trả về bản ghi cũ và giữ nguyên 100% `taken_at` và `client_uuid` ban đầu.
3. **Bỏ tham số `clientUuid` ở `enqueue` — Luôn tự sinh v4:**
   - Hàm `enqueue` không nhận `clientUuid`, tự sinh UUID v4 bằng `createClientUuid()` để loại bỏ hoàn toàn nguy cơ trùng UUID giữa các lượt uống (BQ-009).
4. **Chuẩn hóa thời gian sang UTC đồng nhất:**
   - Luôn định dạng thời gian bằng `.toUtc().toIso8601String()` cho cả `scheduledAt` và `takenAt` (đồng nhất với `_encodeDateTime` trong `local_models.dart`).
5. **Cập nhật trạng thái có điều kiện bảo toàn dữ liệu (Single-step UPDATE):**
   - `SqliteDoseOutbox` thực thi trực tiếp qua `db.rawUpdate` với tên cột khớp 100% bảng `local_dose_logs` (cột ID máy chủ là `id`, dùng `COALESCE(?, id)` để không vô tình ghi đè NULL khi `serverId` là null):
     - `markSynced`:
       ```sql
       UPDATE local_dose_logs
       SET sync_state = 'synced', id = COALESCE(?, id), synced_at = ?, last_error = NULL, local_updated_at = ?
       WHERE client_uuid = ? AND sync_state <> 'synced'
       ```
     - `markFailed`:
       ```sql
       UPDATE local_dose_logs
       SET sync_state = 'failed', last_error = ?, local_updated_at = ?
       WHERE client_uuid = ? AND sync_state = 'pending_upload'
       ```
   - **Chủ ý thiết kế:** Điều kiện `sync_state <> 'synced'` cho phép bản ghi từng bị `failed` vẫn chuyển được sang `synced` khi server tiếp nhận thành công sau đó.
   - **Kiểm soát phát sự kiện:** Chỉ phát sự kiện vào stream khi `count > 0`.
     - Nếu `clientUuid` không tồn tại: `count == 0` ➔ không lỗi, không phát stream.
     - Nếu dòng đã `synced`: gọi lại `markSynced` thì `count == 0` ➔ không phát lặp; gọi `markFailed` thì `count == 0` ➔ trạng thái `synced` được bảo vệ an toàn khỏi lỗi đến muộn.
6. **Khử triệt để Race Condition, Chuyển tiếp & Rò rỉ trong `watchStatus`:**
   - Dùng một `StreamController<DoseLogSyncState?>` riêng cho mỗi lần gọi `watchStatus(clientUuid)`:
     - `onListen`:
       1. Đăng ký lắng nghe broadcast stream nội bộ, **lọc đúng `entry.key == clientUuid`**.
       2. Khi có sự kiện đúng `clientUuid` tới: đặt cờ `eventReceived = true` **và chuyển tiếp ngay sự kiện vào controller** (`if (!controller.isClosed) controller.add(entry.value)`). *(Sự kiện của các UUID khác không kích hoạt cờ này).*
       3. Gọi query DB bất đồng bộ để lấy trạng thái ban đầu của `clientUuid`.
       4. Nếu `eventReceived == false` (chưa có sự kiện mới nào chen vào giữa lúc đang đọc DB) ➔ emit trạng thái ban đầu (`if (!controller.isClosed) controller.add(initialState)`). Ngược lại, nếu sự kiện mới đã phát rồi thì bỏ qua giá trị đọc DB cũ.
     - `onCancel`:
       Hủy ngay subscription nội bộ và đóng controller để không rò rỉ bộ nhớ.
     - Trả về `controller.stream.distinct()`.
7. **Quy tắc trạng thái `failed` (Quyết định SY-07):**
   - `failed` chỉ dành cho lỗi vĩnh viễn (4xx, trừ 408/429). Lỗi mạng tạm thời hoặc 5xx giữ nguyên `pending_upload`.
8. **Vòng đời `dispose()` an toàn:**
   - Đảm bảo `dispose()` idempotent (gọi lần hai không lỗi).
   - Khi `dispose()` được gọi, đóng broadcast stream nội bộ an toàn; các subscriber đang mở sẽ được đóng tự nhiên qua `onCancel` mà không ném lỗi unhandled state.

---

## 3. Các thay đổi đề xuất (Proposed Changes)

### Component: `frontend/mobile/lib/core/contracts/`

#### [MODIFY] `dose_outbox.dart`
- Chuẩn hóa interface:
  ```dart
  abstract class DoseOutbox {
    Future<LocalDoseLog> enqueue({
      required int medicationScheduleId,
      required DateTime scheduledAt,
      required DateTime takenAt,
    });

    Future<List<LocalDoseLog>> getPendingLogs();

    Future<void> markSynced({
      required String clientUuid,
      required int? serverId,
      required DateTime syncedAt,
    });

    Future<void> markFailed({
      required String clientUuid,
      required String errorMessage,
    });

    Stream<DoseLogSyncState?> watchStatus(String clientUuid);

    Future<void> dispose();
  }
  ```

---

### Component: `frontend/mobile/lib/core/storage/local_db/`

#### [MODIFY] `local_db.dart`
- Tách `_createSchema` thành static method công khai:
  `static Future<void> createSchema(Database db, int version) async`
  để code test dùng chung đúng 100% schema bảng thật.

#### [NEW] `sqlite_dose_outbox.dart`
- Cài đặt `SqliteDoseOutbox implements DoseOutbox`:
  - Constructor:
    ```dart
    SqliteDoseOutbox({
      required Future<Database> Function() getDatabase,
    }) : _getDatabase = getDatabase;

    factory SqliteDoseOutbox.fromLocalDb(LocalDb localDb) =>
        SqliteDoseOutbox(getDatabase: () => localDb.database);
    ```
  - `enqueue`:
    - Chuẩn hóa UTC: `scheduledAt.toUtc()`, `takenAt.toUtc()`.
    - Sinh `client_uuid = createClientUuid()`.
    - Chạy `rawInsert`: `INSERT OR IGNORE INTO local_dose_logs (...) VALUES (...)`.
    - Query `SELECT` lại dòng theo `(medication_schedule_id, scheduled_at)`. Nếu rỗng ➔ ném `StateError`.
    - Trả về `LocalDoseLog` tìm được.
  - `markSynced`:
    - Chạy `rawUpdate`: `UPDATE local_dose_logs SET sync_state = 'synced', id = COALESCE(?, id), synced_at = ?, last_error = NULL, local_updated_at = ? WHERE client_uuid = ? AND sync_state <> 'synced'`.
    - Nếu `count > 0`, phát sự kiện `DoseLogSyncState.synced`.
  - `markFailed`:
    - Chạy `rawUpdate`: `UPDATE local_dose_logs SET sync_state = 'failed', last_error = ?, local_updated_at = ? WHERE client_uuid = ? AND sync_state = 'pending_upload'`.
    - Nếu `count > 0`, phát sự kiện `DoseLogSyncState.failed`.
  - `getPendingLogs`:
    - Query trực tiếp `local_dose_logs` với `sync_state = 'pending_upload'` sắp xếp theo `scheduled_at ASC`.
  - `watchStatus(clientUuid)`:
    - Triển khai controller có cờ `eventReceived`, chuyển tiếp sự kiện đúng `clientUuid` trong `onListen`, đọc DB ban đầu, dọn dẹp trong `onCancel`, `.distinct()`.
  - `dispose`:
    - Đóng broadcast controller nội bộ an toàn, có cờ `_disposed` để idempotent.

---

### Component: `frontend/mobile/lib/core/sync/`

#### [MODIFY] `sync_engine.dart`
- Thêm tham số tùy chọn `DoseOutbox? outbox` vào constructor `DoseOutboxSyncEngine`.
- Gọi qua `outbox` nếu có, fallback `_localStore` nếu không có.

---

### Component: `frontend/mobile/` (Cấu hình dependencies)

#### [MODIFY] `pubspec.yaml`
- Thêm `sqflite_common_ffi: ^2.3.3` vào `dev_dependencies`.
*(Lưu ý môi trường: sqflite_common_ffi trên Windows cần sqlite3.dll tương thích. Mã hóa SQLCipher chưa được kiểm chứng ở tầng test FFI này, phần đó dành riêng cho integration_test trên thiết bị thật).*

---

### Component: `frontend/mobile/test/core/storage/`

#### [NEW] `dose_outbox_test.dart`
- Sử dụng `sqflite_common_ffi` và `LocalDb.createSchema`.
- **Thiết lập dữ liệu mồi (Seed Data):** Trong `setUp`, luôn chèn một bản ghi `LocalMedicationSchedule` hợp lệ vào bảng `local_medication_schedules` trước khi gọi `enqueue`, phòng ngừa trường hợp schema có ràng buộc Foreign Key `medication_schedule_id`.
- Các kịch bản test:
  1. **Enqueue đơn lẻ:** Tạo bản ghi mới thành công với `pending_upload`.
  2. **Bảo toàn `taken_at` khi bấm trùng:** Gọi `enqueue` 2 lần cùng mốc thời gian ➔ giữ nguyên `taken_at` và `client_uuid` của lần 1.
  3. **Đua lệnh bấm đúp (Future.wait):** Chạy đồng thời 2 lệnh `enqueue` trên cùng 1 connection ➔ an toàn, chỉ 1 dòng tồn tại.
  4. **Đua lệnh đa kết nối thật (Multi-connection isolate simulation):**
     - Mở 2 kết nối SQLite riêng biệt tới cùng 1 file DB tạm (`singleInstance: false`).
     - Cấu hình `PRAGMA busy_timeout = 5000;` trên cả hai kết nối để tránh lỗi `SQLITE_BUSY`.
     - Gọi `enqueue` song song từ 2 kết nối ➔ cơ chế `INSERT OR IGNORE` đảm bảo chỉ có 1 dòng duy nhất được ghi vào DB.
  5. **Chuẩn hóa UTC:** Chạy 2 `enqueue` cùng thời điểm (1 Local time +07:00, 1 UTC Z) ➔ nhận diện đúng là trùng lặp, không sinh 2 dòng.
  6. **Stream `watchStatus` & Khử Race Condition:**
     - Emit `pending_upload` ngay khi subscribe.
     - Emit `synced` khi `markSynced` được gọi và chuyển tiếp sự kiện đúng cho UI.
     - Sự kiện của `clientUuid` khác không làm mất giá trị đọc ban đầu của `clientUuid` hiện tại.
     - Gọi `markSynced` lần 2 không phát thêm sự kiện trùng lặp.
     - Trả về `null` cho `clientUuid` không tồn tại.
     - Hủy subscriber giải phóng listener sạch sẽ (`onCancel`).
  7. **Chuyển trạng thái từ `failed` sang `synced` & Bảo toàn ID:**
     - Bản ghi từng `failed` được `markSynced` cập nhật thành công và phát stream `synced`.
     - Gọi `markSynced` với `serverId = null` không xóa `id` máy chủ đã có trước đó (nhờ `COALESCE(?, id)`).
  8. **Bảo vệ trạng thái cuối:** Bản ghi đã `synced` không bị `markFailed` ghi đè.
  9. **An toàn khi UUID không tồn tại:** `markSynced` và `markFailed` với UUID lạ không ném lỗi và không phát stream.
  10. **Lọc `getPendingLogs`:** Bản ghi sau khi `markFailed` sẽ biến mất khỏi danh sách pending.
  11. **Hồi quy `SyncEngine`:** Chạy lại toàn bộ bộ test `test/core/sync/sync_engine_test.dart` đảm bảo 100% pass sau khi cập nhật constructor.

---

## 4. Kế hoạch kiểm tra (Verification Plan)

### Automated Tests
```powershell
cd frontend/mobile
flutter pub get
flutter test test/core/storage/dose_outbox_test.dart
flutter test test/core/sync/sync_engine_test.dart
```

### Tiêu chí nghiệm thu (Definition of Done cho SCRUM-54)
- [ ] Ràng buộc khóa duy nhất `client_uuid` và `(schedule_id, scheduled_at)` được kiểm chứng qua SQLite test thật.
- [ ] Hàm `enqueue` bảo toàn nguyên vẹn `taken_at` của lần bấm đầu tiên khi bị bấm trùng.
- [ ] An toàn chạy đua (race condition) được kiểm chứng cả trên kết nối song song và đa kết nối với `singleInstance: false`.
- [ ] Chuẩn hóa cả `scheduledAt` và `takenAt` về UTC.
- [ ] `watchStatus` phát đúng trạng thái theo thời gian thực cho UI, không nuốt sự kiện, chuyển tiếp đầy đủ sự kiện sau khi lắng nghe, và giải phóng listener khi hủy.
- [ ] Tên cột trong các câu UPDATE khớp 100% schema (`id`, `synced_at`, `last_error`, `local_updated_at`), bảo toàn `id` nhờ `COALESCE(?, id)`.
- [ ] Bản ghi `failed` chuyển được sang `synced` khi đồng bộ thành công, bản ghi `synced` được bảo vệ khỏi lỗi đến muộn.
- [ ] Tích hợp tương thích ngược với `SyncEngine` và toàn bộ test cũ của Bao vẫn pass.
- [ ] 100% unit test của outbox và sync engine pass.


## 5. Thứ tự thực hiện bắt buộc và quy tắc cho Agent

### 5.1 Bước 0: Đọc và xác nhận giả định (CHƯA được sửa file nào)
Đọc đầy đủ các file sau và xác nhận từng giả định. Nếu một giả định SAI, **dừng lại và báo cáo**, không tự đoán cách sửa.
1. `lib/core/storage/local_db/local_db.dart`: có `_createSchema`/`onConfigure` không; `PRAGMA foreign_keys` có bật không; `local_dose_logs` có FK tới `local_medication_schedules` không; tên đủ các cột (`client_uuid`, `medication_schedule_id`, `scheduled_at`, `taken_at`, `sync_state`, `id`, `synced_at`, `last_error`, `local_updated_at`); ràng buộc UNIQUE; cột `id` có UNIQUE/NOT NULL không.
2. `lib/core/storage/local_db/local_models.dart`: định dạng `_encodeDateTime`; tên enum `DoseLogSyncState` và giá trị chuỗi `pending_upload`/`synced`/`failed`; hàm chuyển dòng DB sang `LocalDoseLog`.
3. `lib/core/contracts/dose_outbox.dart`: nội dung hiện tại. Chạy tìm kiếm (grep) mọi nơi dùng `DoseOutbox` và `createClientUuid` trong `lib/` và `test/`. Nếu việc đổi interface làm gãy nơi khác, liệt kê và báo cáo trước khi sửa.
4. `lib/core/sync/sync_engine.dart`: hàm `_uploadBatchWithRetry`, cách đang gọi `markDoseLogSynced`/`markDoseLogFailed`, constructor hiện tại.
5. `test/core/sync/sync_engine_test.dart`: cách khởi tạo `DoseOutboxSyncEngine` trong test cũ.
6. `pubspec.yaml`: phiên bản `sqflite`/`sqflite_sqlcipher` đang dùng, đã có `sqflite_common_ffi` chưa.

### 5.2 Thứ tự làm
1. Ghi lại kết quả Bước 0 (ngắn gọn) trước khi code.
2. Chạy `flutter test test/core/sync/sync_engine_test.dart` TRƯỚC khi sửa để biết trạng thái nền (pass/fail sẵn có). Nếu không chạy được (thiếu Flutter SDK, thiếu `sqlite3`), ghi rõ và tiếp tục.
3. Sửa `pubspec.yaml`, chạy `flutter pub get`. Nếu phiên bản `^2.3.3` xung đột, chọn phiên bản tương thích và ghi lại.
4. Sửa `local_db.dart` (chỉ tách `createSchema` thành static công khai, KHÔNG đổi logic khác), cập nhật nơi gọi.
5. Sửa `dose_outbox.dart` (interface).
6. Viết `dose_outbox_test.dart` TRƯỚC, rồi viết `sqlite_dose_outbox.dart` cho đến khi test pass (TDD).
7. Sửa `sync_engine.dart` (chỉ thêm tham số tùy chọn `outbox` và nhánh gọi), rồi chạy lại test cũ.

### 5.3 Quy tắc bắt buộc
- **Phạm vi file:** chỉ được sửa các file ghi trong mục 3. Cần sửa file khác thì dừng và hỏi.
- **Không dùng** `LocalMedicationStore.upsertDoseLog` trong `SqliteDoseOutbox`.
- **Không đổi** hành vi của `LocalMedicationStore`, `LocalDb` ngoài việc tách `createSchema`.
- **Không thêm** thư viện state management hoặc DI nào.
- `watchStatus`, `markSynced`, `markFailed` sau `dispose()`: không phát sự kiện vào controller đã đóng (kiểm tra cờ `_disposed`), không ném lỗi.
- Mọi `Future`/`StreamSubscription` trong test phải được `await`/hủy, test không được để lại timer hay listener treo.
- Test đa kết nối (kịch bản 4) phải dùng file DB tạm trong thư mục tạm của hệ điều hành và xóa sau test. Nếu test này chập chờn, KHÔNG xóa test; báo cáo nguyên nhân.
- **Không viết** "test pass" hay "đã xác minh" khi chưa chạy lệnh thật. Không chạy được thì ghi "CHƯA CHẠY" kèm lý do.
- Gặp mâu thuẫn giữa kế hoạch và code thật: dừng, nêu rõ mâu thuẫn, đề xuất phương án, KHÔNG tự chọn.

### 5.4 Báo cáo đầu ra (bắt buộc)
Khi xong, trả về đúng các mục sau:
1. Danh sách file đã tạo/sửa (đường dẫn) và tóm tắt thay đổi mỗi file.
2. Kết quả Bước 0: giả định nào đúng, giả định nào sai.
3. Kết quả chạy lệnh: dán nguyên văn dòng tổng kết của `flutter pub get` và hai lệnh `flutter test` (số test pass/fail), kèm kết quả test `sync_engine_test.dart` trước và sau khi sửa.
4. Bảng đối chiếu từng mục Definition of Done: Đạt / Không đạt / Chưa chạy, kèm bằng chứng (tên test).
5. Giới hạn chưa kiểm chứng, ghi rõ: (a) SQLCipher (test dùng DB thường), (b) hành vi trên background isolate thật, (c) mọi thứ chưa chạy được.
6. Các điểm lệch so với kế hoạch và lý do.
7. Việc cần người làm tiếp: báo Bao về tham số `outbox` mới; chạy `integration_test` trên máy thật.

Bắt đầu thực thi.