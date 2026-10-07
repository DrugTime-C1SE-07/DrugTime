Task 2.21 xây dựng cơ chế tự động đồng bộ danh mục thuốc DAV theo chuỗi:

`Celery Beat → runtime.tick → kiểm tra chu kỳ 7 ngày → RabbitMQ → catalog.sync → khóa run trong PostgreSQL → tải DAV → parse/normalize → upsert → kết thúc run`

Đây là job nền hoàn toàn; không có request từ Mobile/Admin và không thay đổi API contract.

## 1. Khi Worker khởi động

Script [start_worker.sh](D:/DrugTime/source/DrugTime/backend/scripts/start_worker.sh) chạy:

```bash
celery --app drugtime.worker:celery_app worker --beat \
  --without-gossip --without-mingle
```

Một process hiện đảm nhiệm cả:

- Celery Worker: nhận và xử lý message.
- Celery Beat: phát message theo lịch.

Trước khi chạy, script bắt buộc phải có `CELERY_BROKER_URL`. Nếu thiếu, process dừng ngay, tránh vô tình dùng broker không đúng trong production.

Khi import [worker.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/worker.py):

1. Nạp file môi trường.
2. Import `catalog.tasks` để task `catalog.sync` được đăng ký vào Celery.
3. Tạo hai lịch Beat:

| Beat entry                  | Task                |   Chu kỳ |
| --------------------------- | ------------------- | -------: |
| `drugtime-periodic-tick`    | `runtime.tick`      | 300 giây |
| `drugtime-worker-heartbeat` | `runtime.heartbeat` |  60 giây |

`runtime.tick` không phải job DAV riêng. Nó là “nhịp tim nghiệp vụ” chung, cứ 5 phút kiểm tra nhiều loại công việc.

## 2. Cấu hình RabbitMQ/Celery

[shared/celery.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/shared/celery.py) tạo Celery app với broker lấy từ `CELERY_BROKER_URL`.

Các cấu hình đáng chú ý:

- `timezone="Asia/Ho_Chi_Minh"`.
- `task_ignore_result=True`: không lưu kết quả task vào result backend.
- `worker_prefetch_multiplier=1`: mỗi worker process chỉ lấy trước một message.
- `broker_pool_limit=1`: giới hạn connection pool với RabbitMQ.
- Tắt task events và remote control.
- Worker production tắt gossip và mingle.
- `broker_connection_retry_on_startup=True`: thử kết nối lại nếu RabbitMQ chưa sẵn sàng khi worker khởi động.

Message DAV chỉ chứa:

```python
args = ["dav_drugbank"]
kwargs = {"triggered_by": "scheduler"}
```

Toàn bộ dữ liệu thuốc được worker tải trực tiếp từ DAV, không đi qua RabbitMQ.

## 3. Beat kích hoạt `runtime.tick`

Cứ 300 giây, Beat gửi task tên `runtime.tick` vào RabbitMQ.

Worker nhận message và gọi:

```python
job_runner.tick()
```

Trong [job_runner.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/runtime/job_runner.py), tick lần lượt chạy:

1. Quét liều bị bỏ lỡ.
2. Kiểm tra DAV có đến hạn đồng bộ không.
3. Tiếp tục các yêu cầu xóa dữ liệu đang dở.

Mỗi bước được bọc bằng `try/except` riêng:

```python
for name, step in (...):
    try:
        step()
    except Exception:
        log.exception(...)
```

Do đó:

- Quét missed dose lỗi vẫn tiếp tục kiểm tra DAV.
- Kiểm tra DAV lỗi vẫn tiếp tục xử lý data erasure.
- Lỗi một phần không làm hỏng toàn bộ tick.

Riêng bước DAV gọi:

```python
catalog.sync_if_due(unit_of_work)
```

Runtime chỉ import public facade `catalog.api`, không truy cập thẳng repository nội bộ, nên vẫn giữ ranh giới module.

## 4. Quyết định có cần đồng bộ hay không

Logic nằm trong [catalog/api.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/modules/catalog/api.py).

Nguồn được cố định là:

```python
source = "dav_drugbank"
```

Facade mở transaction đọc PostgreSQL và thực hiện hai truy vấn.

### 4.1. Kiểm tra có run đang chạy

Repository chạy tương đương:

```sql
SELECT EXISTS (
    SELECT 1
    FROM catalog_sync_runs
    WHERE source = 'dav_drugbank'
      AND status = 'dang_chay'
);
```

Nếu kết quả là `true`, hàm trả về ngay:

```python
return None
```

Không tạo message RabbitMQ mới.

### 4.2. Lấy lần thành công gần nhất

Nếu không có run đang chạy, repository chạy:

```sql
SELECT max(finished_at)
FROM catalog_sync_runs
WHERE source = 'dav_drugbank'
  AND status = 'thanh_cong';
```

Nó chỉ xét run thành công. Run `that_bai` không làm lùi lịch đồng bộ.

Ví dụ:

- Thành công gần nhất: 10 ngày trước → đến hạn.
- Thành công gần nhất: 3 ngày trước, dù hôm qua có một run thất bại → chưa đến hạn.
- Chưa từng thành công → đến hạn ngay.

Transaction chỉ đọc đến đây rồi đóng.

## 5. Policy chu kỳ 7 ngày

[scheduling.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/modules/catalog/application/scheduling.py) chứa policy thuần:

```python
return now - last_success_at >= timedelta(days=7)
```

Các trường hợp:

| Trạng thái           | Kết quả      |
| -------------------- | ------------ |
| Chưa từng thành công | Đến hạn      |
| 6 ngày 23:59:59      | Chưa đến hạn |
| Đúng 7 ngày          | Đến hạn      |
| Hơn 7 ngày           | Đến hạn      |

Cả `now` và `last_success_at` bắt buộc phải có timezone. Timestamp naive làm hàm ném `ValueError`.

Clock hiện lấy `datetime.now(UTC)`. Việc trừ hai timestamp timezone-aware vẫn cho khoảng thời gian chính xác; timezone Celery là `Asia/Ho_Chi_Minh` để điều phối lịch.

## 6. Enqueue task đồng bộ

Nếu policy trả về `false`, tick kết thúc mà không enqueue gì.

Nếu trả về `true`, facade gọi:

```python
enqueue_sync(
    "dav_drugbank",
    triggered_by="scheduler",
)
```

[job_queue.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/modules/catalog/adapters/outbound/job_queue.py) dùng:

```python
celery_app.send_task(
    "catalog.sync",
    args=["dav_drugbank"],
    kwargs={"triggered_by": "scheduler"},
)
```

`send_task()` serialize message và gửi tới RabbitMQ. Hàm trả về Celery task ID, nhưng không chờ job chạy và không chờ kết quả.

Điểm quan trọng: “kiểm tra đến hạn” và “enqueue” không atomic. Hai tick đồng thời có thể cùng đọc thấy chưa có run rồi cùng enqueue. Task chấp nhận khả năng đó và dùng PostgreSQL làm hàng rào cuối cùng.

## 7. Worker nhận `catalog.sync`

Task nằm trong [catalog/tasks.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/modules/catalog/tasks.py):

```python
@celery_app.task(
    name="catalog.sync",
    acks_late=True,
    reject_on_worker_lost=True,
    autoretry_for=(TransientCatalogSyncError,),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
```

Ý nghĩa:

- `acks_late=True`: không ACK ngay khi nhận; chỉ ACK sau khi hàm hoàn thành.
- `reject_on_worker_lost=True`: nếu process xử lý bị mất, Celery yêu cầu broker giao lại message.
- `max_retries=3`: tối đa ba lần retry ngoài lần chạy đầu.
- `retry_backoff=True`: thời gian đợi tăng dần.
- `retry_jitter=True`: thêm độ ngẫu nhiên, tránh nhiều worker retry đồng loạt.

Task mặc định source là `dav_drugbank`. Nếu message truyền source khác:

```python
raise ValueError("unsupported catalog source")
```

Lỗi này không thuộc loại transient nên không retry.

## 8. Giành quyền chạy bằng PostgreSQL

Task gọi `run_sync()` trong [service.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/modules/catalog/service.py).

Việc đầu tiên là mở một transaction riêng và gọi:

```python
run_id = repository.start_run(...)
```

Repository trong [repository.py](D:/DrugTime/source/DrugTime/backend/src/drugtime/modules/catalog/repository.py) thực hiện:

```sql
INSERT INTO catalog_sync_runs (source, triggered_by)
VALUES (:source, :triggered_by)
ON CONFLICT DO NOTHING
RETURNING id;
```

Schema đã có unique partial index:

```sql
CREATE UNIQUE INDEX catalog_sync_runs_one_running_idx
ON catalog_sync_runs (source)
WHERE status = 'dang_chay';
```

Do đó, cùng một source chỉ có tối đa một dòng `dang_chay`.

### Khi task thắng race

`RETURNING id` trả về một ID. Transaction kết thúc bình thường và commit dòng run.

Task tiếp tục tải dữ liệu.

### Khi task thua race

`ON CONFLICT DO NOTHING` không trả dòng nào, nên `run_id=None`.

Service trả về ngay:

```python
if run_id is None:
    return
```

Task thua race:

- Không gọi DAV.
- Không parse.
- Không upsert.
- Không sửa run mà task khác đang sở hữu.
- Kết thúc thành công và ACK message.

Đây là lớp bảo vệ thực sự trước hai message đồng thời. Kiểm tra `is_running()` ở scheduler chỉ giúp giảm message dư thừa.

## 9. Tải dữ liệu DAV

Task tạo fetch callback:

```python
fetch_dav_drugbank_pages(
    settings.catalog_dav_drugbank_url
)
```

Fetcher có thể trả nhiều payload/page. Service xử lý tuần tự:

```text
page 1 → parse → normalize từng dòng
page 2 → parse → normalize từng dòng
...
```

Parser chuyển payload bytes thành danh sách record thô.

Mỗi record sau đó qua `normalize_record()` để chuyển thành `NormalizedMedication`.

Nếu một record bị lỗi `ValueError` trong normalize:

- Record đó bị bỏ qua.
- Biến `failed` tăng 1.
- Các record hợp lệ khác vẫn tiếp tục được xử lý.

Nếu cuối cùng không còn record hợp lệ:

```python
raise ValueError("DAV returned no valid medication records")
```

Đây là lỗi dữ liệu cố định, không retry tự động.

## 10. Upsert danh mục thuốc

Khi đã có danh sách normalized, service mở transaction mới.

Repository đọc tất cả `source_ref` hiện có của `dav_drugbank` để tính số insert/update, sau đó chạy batch upsert theo khóa:

```text
(source, source_ref)
```

SQL có dạng:

```sql
INSERT INTO medications (...)
VALUES (...)
ON CONFLICT (source, source_ref)
DO UPDATE SET ...
```

Hệ quả:

- Chưa tồn tại `(source, source_ref)` → insert.
- Đã tồn tại → update chính dòng đó.
- Message bị giao lại với cùng snapshot → không sinh thêm dòng thuốc trùng.

Đây là lớp idempotency của dữ liệu thuốc.

## 11. Soft-delete thuốc không còn trong DAV

Chỉ khi `failed == 0`, repository mới soft-delete các thuốc của source không xuất hiện trong snapshot mới:

```sql
UPDATE medications
SET deleted_at = now()
WHERE source = :source
  AND source_ref != ALL(:refs)
  AND deleted_at IS NULL;
```

Nếu có dù chỉ một record normalize thất bại, hệ thống bỏ qua toàn bộ bước soft-delete.

Lý do: snapshot khi ấy không hoàn chỉnh; soft-delete có thể xóa nhầm thuốc chỉ vì record của nó không parse được.

## 12. Đánh dấu run thành công

Trong cùng transaction với upsert, repository cập nhật run:

```sql
UPDATE catalog_sync_runs
SET status = 'thanh_cong',
    finished_at = now(),
    records_inserted = :inserted,
    records_updated = :updated,
    records_failed = :failed
WHERE id = :id;
```

Khi thoát `unit_of_work` bình thường:

- Upsert thuốc commit.
- Soft-delete, nếu có, commit.
- Trạng thái run thành công commit cùng transaction.

Sau đó `run_sync()` trả về, Celery task hoàn thành và ACK message RabbitMQ.

Lần tick kế tiếp sẽ thấy `latest_success_at` mới và không enqueue lại trong 7 ngày.

## 13. Luồng khi có lỗi

Mọi exception sau khi đã giành được `run_id` đi vào:

```python
except Exception as exc:
    repository.fail_run(...)
    raise
```

Repository mở transaction mới và cập nhật:

```sql
UPDATE catalog_sync_runs
SET status = 'that_bai',
    finished_at = now(),
    error_details = jsonb_build_object(
        'message', :error
    )
WHERE id = :id;
```

Chuỗi lỗi bị cắt tối đa 2.000 ký tự.

Sau khi ghi run thất bại, exception được ném lại cho Celery wrapper phân loại.

### Lỗi được retry

Các lỗi sau được đổi thành `TransientCatalogSyncError`:

- HTTP `429`.
- HTTP `5xx`.
- `httpx.TransportError`: timeout, mất kết nối, DNS hoặc transport tương tự.
- SQLAlchemy `OperationalError`: lỗi DB mang tính vận hành/tạm thời.

Celery retry với exponential backoff và jitter, tối đa ba retry.

Mỗi retry gọi lại `run_sync()` từ đầu và tạo một `catalog_sync_runs` mới. Vì attempt trước đã được chuyển sang `that_bai`, unique index không còn chặn attempt sau.

### Lỗi không retry

Các lỗi sau được ném thẳng:

- Source không được hỗ trợ.
- HTTP `4xx` khác `429`.
- Dữ liệu DAV không có record hợp lệ.
- `ValueError` mang tính dữ liệu/cấu hình.
- Các exception không nằm trong nhóm transient đã khai báo.

Run được ghi `that_bai`, task fail và không retry tự động.

## 14. Các kịch bản quan trọng

### Chưa đến hạn

```text
Beat tick
  → không có run đang chạy
  → thành công gần nhất < 7 ngày
  → không enqueue
```

### Đến hạn bình thường

```text
Beat tick
  → không có run đang chạy
  → đã đủ 7 ngày
  → enqueue catalog.sync
  → worker giành running slot
  → fetch/parse/normalize
  → upsert
  → run = thanh_cong
  → ACK
```

### Hai tick cùng enqueue

```text
Message A ─┐
           ├→ INSERT running
Message B ─┘
```

- A insert thành công và chạy.
- B gặp unique conflict, nhận `run_id=None`, kết thúc no-op.
- Không có hai lượt fetch/upsert song song.

### Redelivery sau khi đã cập nhật thành công

Nếu dữ liệu đã commit nhưng ACK chưa tới RabbitMQ:

- Message có thể được giao lại.
- Upsert theo `(source, source_ref)` không tạo thuốc trùng.
- Có thể tạo thêm một run audit mới, nhưng số dòng thuốc không tăng.

### Lỗi HTTP 500

```text
attempt 1 → run thất bại → retry
attempt 2 → run thất bại → retry
attempt 3 → run thất bại → retry
attempt 4 → run thất bại → kết thúc
```

Tối đa bốn lần thực thi tính cả lần đầu.

## 15. Một lỗ hổng đáng chú ý trong implementation hiện tại

Có một khoảng trống giữa ý định requirement và code thực tế:

1. `start_run()` commit một dòng `dang_chay`.
2. Worker bắt đầu tải hoặc xử lý DAV.
3. Process bị kill đột ngột trước khi `fail_run()` hoặc `finish_run()`.
4. RabbitMQ giao lại message nhờ `acks_late`.
5. Message giao lại gọi `start_run()`.
6. Dòng `dang_chay` cũ vẫn tồn tại nên unique index làm insert mới thất bại.
7. Service coi đây là “task khác đang chạy”, trả về thành công.
8. Celery ACK message giao lại.

Kết quả: run cũ có thể mắc kẹt vĩnh viễn ở `dang_chay`, và mọi tick sau đó đều bỏ qua source.

Vì vậy implementation hiện tại chống duplicate concurrency tốt, nhưng chưa hoàn chỉnh cho trường hợp “worker chết sau khi commit running slot”. Muốn thực sự đạt mục tiêu redelivery, cần thêm một cơ chế như:

- lease/timeout cho run;
- heartbeat và reclaim run stale;
- hoặc task identity cho phép đúng message redelivery tiếp quản run cũ.

Đây nên được xem là finding quan trọng trước khi duyệt implement hoặc trong task 2.22 khi test RabbitMQ thật.

## 16. Trạng thái hiện tại

Theo [04-impl-notes.md](D:/DrugTime/source/DrugTime/work/2.21/04-impl-notes.md):

- P1–P7 đã hoàn thành.
- Unit + architecture: `133 pass, 4 skip`.
- Ruff pass.
- Secret scan pass.
- Integration test PostgreSQL/RabbitMQ chưa nằm trong giai đoạn implement hiện tại.
- Artifact implement vẫn là `draft`.
- Scope audit còn bị chặn bởi 17 file thay đổi có sẵn ngoài phạm vi task.

Nói ngắn gọn: luồng happy path, due policy, retry classification, quota config và chống chạy song song đã được triển khai; nhưng task chưa được bàn giao hoàn chỉnh và nhánh worker-crash để lại run `dang_chay` cần được xử lý hoặc ghi nhận rõ trước khi coi AC5/AC6 là được bảo đảm end-to-end.
