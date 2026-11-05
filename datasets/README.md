# Bộ ảnh bao bì và kết quả OCR PB31

## Bản dữ liệu v1 · 2026-10-29

- **49 ảnh, 49 dòng nhãn, 28 ảnh hộp và 21 ảnh vỉ**, 23 nhãn tên sản phẩm khác nhau sau đối chiếu trực quan. Folder là nhóm lưu trữ, không phải nhãn thương hiệu; cùng hoạt chất có thể là các sản phẩm khác nhau.
- [labels.xlsx](labels.xlsx): nhãn tên/strength đã rà theo ảnh; 23 dòng được sửa ở vòng 2026-10-29. Thiếu strength rõ trên ảnh thì để trống; không điền theo folder hoặc ảnh khác. Không dùng raw làm đáp án.
- [annotations.v1.csv](annotations.v1.csv): từng ảnh có nguồn/điều kiện biết được, người/ngày và trạng thái rà soát. Người rà là **Codex visual inspection (AI)**, không giả là người kiểm độc lập; phần nguồn không rõ ghi unknown, watermark không chứng minh URL nguồn gốc.
- [manifest.v1.json](manifest.v1.json): byte hash workbook/49 ảnh, hash bảng annotations, thống kê và giới hạn. Hash dataset là canonical snapshot nhãn/ảnh do reader hiện có tạo; metadata xác minh bổ sung trong manifest không tham gia canonical hash này. Bảng annotations có hash riêng. Đổi nhãn/ảnh phải tạo snapshot mới và chấm lại, không sửa manifest để che thay đổi.
- [Pilot-002](results/pilot-002/report.md): 49/49 ảnh có raw; exact 27/49 (55,1%), partial 5, đủ token tách xa 2, không tìm thấy tên 14, không chữ 1. Median 2615 ms/p95 5267 ms trên emulator. Đây không phải accuracy matching hoặc tốc độ trên điện thoại thật.
- [Quyết định hướng GO](results/pilot-002/decision.md) và [decision.json](results/pilot-002/decision.json): người phụ trách xác nhận trong chat ngày 2026-10-29, tiếp tục ML Kit vào chuẩn hóa/matching. Quyết định kỹ thuật ghi riêng; CLI mode pilot vẫn `not_decided`, không sửa raw/evaluator để sinh go giả.
- **Trạng thái bàn giao: cục bộ, chưa commit/push**, chưa khẳng định nhóm đã pull được. Còn cần người khác rà độc lập nhãn, các ca native/manual đã ghi Pending và review/PR theo quy trình. Không dùng GO để tự miễn kiểm hoặc coi task đã complete.

Tái hiện: từ gốc repo chạy lệnh chấm bên dưới với `--runs datasets/results/pilot-002/raw --output datasets/results/pilot-002`. Nếu nhãn/report thay đổi, `decision.json` đang ghim hash report/snapshot sẽ phải rà soát và cập nhật; không dùng bản quyết định/hash cũ cho dữ liệu mới. Quyết định GO theo hướng có thể giữ nhưng số liệu/chứng cứ phải cập nhật đúng.

Hiện không có file ảnh trùng byte trong 49 ảnh. Các góc nhìn/crop của cùng sản phẩm có thể liên quan dù byte khác; bộ này chưa được chứng minh là các mẫu nguồn độc lập hoặc đại diện toàn bộ điều kiện chụp. Không yêu cầu engine OCR nghiên cứu cũ để đọc hoặc dùng dataset.

Ảnh/nhãn của 4.08, raw ML Kit và báo cáo của 4.09 dùng chung cho 4.12–4.14 và 4.17. Thư mục thường trong superproject, không phải submodule. Bản này đang thu thập/pilot, chưa phải benchmark frozen hoặc kết luận go/no-go.

## Cấu trúc và nhãn

- `images/<product>/<box|blister>/<image_id>.jpg`: ảnh gốc, không đổi byte/định dạng hoặc chụp lại màn hình để test cùng ảnh.
- `labels.xlsx`: một ảnh/một dòng; cột `image_id`, `relative_path` (tính từ datasets), `drug_name`, `strength`. Công cụ tìm header, hỗ trợ bố cục hiện tại B2:E2. Nhãn do người kiểm tra từ ảnh, không lấy raw làm đáp án. Không cần Excel đang mở để chạy.
- `scripts/`: Python 3.10+ standard library, không cần pip package, Flutter hoặc backend để **chấm**. ML Kit vẫn chạy trên Android.
- `results/legacy-pilot/`: bản sao nguyên byte của raw/index cũ trong work; không tự ghép vào dataset hiện tại.
- `results/pilot-001/raw/`: JSON gốc; `run-map.csv` ánh xạ có chứng cứ; `import-index.json` ghi nguồn/hash/thiết bị quan sát lúc nhập.
- `results/pilot-001/{per_image.csv,summary.json,report.md}`: báo cáo tái tạo từ ảnh/nhãn/raw. Work giữ các artifact quy trình và log kiểm tra, không còn là nơi bắt buộc để tìm raw mới.

Tên thuốc ghi đúng bao bì, giữ biến thể như Forte/Original. Hàm lượng chỉ ghi khi nhìn thấy và đã xác minh; trống có nghĩa chưa chấm, không phải 0. Nhãn nhiều thành phần (ví dụ Tiffy) cần quy tắc thành phần–hàm lượng trước khi chấm; hiện ghi `requires_component_protocol`.

## Chạy pilot trên Android

1. Mở emulator, kéo ảnh gốc từ dataset vào máy ảo.
2. Từ `frontend/mobile`, chạy `flutter run -d emulator-5554 -t lib/main_ocr_prototype.dart`.
3. Nhập `image_id` đúng trong workbook, metadata thiết bị/OS/SDK/revision thực; chọn ảnh và chạy OCR. Giữ cả lần đọc sai/no-text. Không điền giá trị như `d` hoặc `dd` cho OS/SDK.
4. Đợi lưu kết quả. JSON nằm trong sandbox app Android, chưa tự xuất vào folder Windows. Dùng cách nhập dưới đây.

## Nhập JSON vào dataset

Các lệnh sau chạy **từ thư mục gốc repository** (thư mục chứa `datasets/`, `frontend/` và `backend/`). Không chạy script trong `frontend/mobile`.

Để nhập qua Android, thêm thư mục `platform-tools` của Android SDK vào `PATH` trên máy đang dùng. Chạy `adb devices` để kiểm tra kết nối; thay `emulator-5554` trong ví dụ bằng serial thiết bị cần nhập.

```powershell
python datasets/scripts/import_android_runs.py --adb adb --serial emulator-5554 --output datasets/results/pilot-001
```

Thiết bị phải online, app prototype debug còn được cài. Script chỉ đọc app, không chạy OCR lại hoặc khởi động/dừng máy ảo. Chỉ rõ serial từ `adb devices` khi có nhiều thiết bị. Nếu run-as bị từ chối, dùng nút xuất JSON trong prototype, chuyển file `<runId>.json` vào thư mục `ocr-export/` ở gốc repository trên máy tính rồi nhập:

```powershell
python datasets/scripts/import_android_runs.py --source ./ocr-export --output datasets/results/pilot-001
```

Script giữ byte gốc, cùng runId giống nhau thì skip, khác nội dung thì báo lỗi và không ghi đè. Mỗi đợt mới dùng `pilot-002`, `pilot-003`… Không sửa file raw; không tạo JSON từ screenshot. Import trả exit 1 nếu có lỗi và ghi lỗi vào import-index; exit 2 nếu không thể bắt đầu. Các raw hợp lệ đã nhập trước lỗi được giữ.

Khi nhập qua ADB, script so hash ảnh lưu trong app với ảnh dataset. Một ảnh khớp duy nhất thì tạo mapping có chứng cứ; không khớp hoặc nhiều ảnh cùng hash thì chưa ánh xạ. Run cũ đã ở legacy được bỏ khỏi pilot mới. Metadata payload không bị sửa; `observed_device` là thông tin đọc lúc import, không phải chứng minh metadata thời điểm quét hoàn toàn chính xác.

Nếu cần mapping thủ công, ghi `run_id,image_id,verified_by,reason` trong run-map.csv sau khi đối chiếu đúng ảnh/byte và nguồn. Không đoán theo tên thuốc OCR. Chỉ có hậu tố file hoặc imageId=1 không đủ để tự nối ảnh.

## Chấm và xem kết quả

```powershell
python datasets/scripts/evaluate_ocr.py --labels datasets/labels.xlsx --runs datasets/results/pilot-001/raw --output datasets/results/pilot-001
```

Mở [report.md](results/pilot-001/report.md) để xem tổng hợp, [per_image.csv](results/pilot-001/per_image.csv) để lọc từng ảnh/run bằng Excel, [summary.json](results/pilot-001/summary.json) để xử lý bằng chương trình.

- Tên chính đạt `exact_name` khi đủ cụm đúng thứ tự, ranh giới từ sau NFC/hoa-thường/whitespace; xuống dòng không làm sai. Không fuzzy/bỏ dấu/sửa chữ.
- `tokens_present_noncontiguous`: đủ từ đúng nhưng nằm rời/đảo thứ tự; chẩn đoán phụ, không tính đạt exact.
- `partial_name`, `name_not_found`: thiếu từ/sai ký tự/không thấy tên. `no_text`, `input_error`, `engine_error`: trạng thái OCR tương ứng.
- `not_run`: chưa có run hợp lệ cho ảnh/thiết bị. `invalid_label`, `invalid_run`, `unmapped`: lỗi dữ liệu/không nối được, vẫn hiện rõ.
- Mỗi ảnh/thiết bị lấy lần sớm nhất theo createdAt rồi runId; lỗi sớm vẫn tính, không chọn lần tốt hơn. Run khác vẫn có trong CSV nhưng `selected=False`.
- Accuracy = exact / số ảnh nhãn hợp lệ đã chạy; no-text/lỗi OCR tính không đạt. Coverage = số ảnh đã chạy / tổng nhãn hợp lệ. Đọc cả hai, không lấy 1/1 làm kết luận cho 17 ảnh. Chưa chạy khác với OCR đọc sai. Không có mẫu số thì N/A.
- Strength phụ chỉ chấm nhãn đơn số + đơn vị; 500mg = 500 mg, không khớp 1500 mg. Đây là chữ xuất hiện, không chứng minh đúng thành phần/sản phẩm.
- Timing median/p95 nearest-rank kèm n, tách thiết bị; không dùng máy ảo để kết luận tốc độ điện thoại, không suy cold/warm từ timing.

Ảnh/nhãn/raw chỉ đọc khi chấm. CSV dùng UTF-8 BOM và bảo vệ giá trị bắt đầu dấu công thức; JSON raw giữ nguyên. Lệnh chấm trả exit 1 khi có lỗi dữ liệu (vẫn xuất báo cáo), exit 2 nếu không thể đọc/chấm. `not_run` tự nó không phải lỗi script.

## Benchmark chính thức có ngưỡng và quyết định hướng

CLI pilot luôn `decision=not_decided`; quyết định hướng GO của người phụ trách ở decision.md/decision.json riêng và không cần ngưỡng tự đặt sau khi đo. Nếu nhóm làm benchmark chính thức có ngưỡng, cần chốt độ phủ, thiết bị, ngưỡng tên/thời gian trước lần đo; không chọn ngưỡng dựa trên điểm đã thấy. Benchmark chính thức không phải điều kiện chặn việc ghi quyết định hướng từ pilot theo requirement mới.

[benchmark-protocol.example.json](results/benchmark-protocol.example.json) là mẫu **draft**, không phải protocol đã duyệt. Tạo bản riêng cho benchmark. `required_devices` dùng đúng device key trong summary; cấu hình `required_config` phải đúng build thực. Thiết bị từ metadata gốc và quan sát ADB cần được đối chiếu, đặc biệt metadata nhập tay sai.

Manifest chính thức có `dataset_hash`, `labels_sha256` và `images` lấy từ `summary.json.snapshot` tại lúc chốt. Mỗi image phải bổ sung `labels_verified=true`, `verified_by`, `verified_at`, `condition` sau khi người kiểm tra xác minh. Thêm `runs` làm sidecar `{ "<runId>": { "phase": "cold" } }` hoặc `warm`; cold là run đầu sau process/engine mới, warm là run tiếp trên engine đã khởi tạo. Không sửa raw để thêm phase. Dataset hash tính từ byte workbook, nội dung nhãn và byte ảnh, nên thay ảnh/nhãn cần snapshot/phiên bản mới.

```powershell
python datasets/scripts/evaluate_ocr.py --labels datasets/labels.xlsx --runs datasets/results/benchmark-001/raw --output datasets/results/benchmark-001 --mode benchmark --protocol datasets/results/benchmark-001/protocol.json --manifest datasets/results/benchmark-001/manifest.json
```

Protocol chưa frozen/thiếu metadata, hash sai, nhãn chưa verified, thiếu ảnh/điều kiện/thiết bị/lần lặp hoặc run trước frozenAt thì `pending`. Khi đủ mới tính go/no-go theo ngưỡng tên và latency trong từng nhóm thiết bị/phase/condition. Hàm lượng phụ không tự trở thành gate. OCR accuracy không phải accuracy matching DB hoặc an toàn dùng thuốc; top-1/top-N toàn luồng thuộc 4.17.

## Kiểm công cụ

```powershell
python -m unittest discover -s datasets/scripts -p "test_*.py" -v
```

Test tạo fixture trong TEMP, không ghi raw giả vào results. Không cần bật emulator để chạy unit test. Máy khác pull superproject sẽ có dataset và công cụ sau khi các file được commit/push theo yêu cầu người quản lý repo.
