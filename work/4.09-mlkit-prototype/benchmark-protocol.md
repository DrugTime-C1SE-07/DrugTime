# Protocol benchmark OCR · 4.09

> Cập nhật 2026-10-28: nội dung dưới là protocol cũ tên–hoạt chất, giữ để truy lịch sử. Phạm vi hiện hành theo 01/03 mới: tên thuốc chính, hàm lượng phụ, pilot trong datasets/ không cần ngưỡng và luôn not_decided. Xem datasets/README.md và datasets/results/benchmark-protocol.example.json; không áp mẫu cũ bên dưới cho dataset hiện tại. Benchmark chính thức vẫn cần chốt protocol trước lần đo.

Phạm vi mới theo yêu cầu trực tiếp ngày 2026-10-27: **chỉ Android**, không yêu cầu build/test iOS. Requirement và plan Android-only đã được duyệt lại; native trên máy ảo là evidence smoke, không thay yêu cầu kiểm thiết bị Android đã chốt cho benchmark.

Trạng thái: **draft — chưa được chốt, chưa có go/no-go**. File này mô tả protocol đề xuất, không thay phê duyệt requirement/plan. Chỉ bắt đầu benchmark sau khi người dùng chốt các trường còn trống và bộ 4.08 được xác minh. Không chọn ngưỡng sau khi đã xem điểm.

## Đợt A: chạy và bàn giao raw

Tại frontend/mobile:

```powershell
flutter run -t lib/main_ocr_prototype.dart -d <android-device>
```

1. Chỉ chọn ảnh bao bì, không có thông tin cá nhân. Mã ảnh phải trùng manifest 4.08. Không dùng ảnh đơn thuốc.
2. Điền model/OS/nền tảng, revision build và native SDK từ evidence. Android dependency plugin hiện khai báo com.google.mlkit:text-recognition:16.0.1. Thông tin này do người thử xác nhận, không tự suy từ package version. Model nội bộ ML Kit không expose: not_exposed.
3. Chạy, kiểm trạng thái và raw. Thời gian đo bằng Stopwatch chỉ quanh lời gọi engine, không gồm chọn/copy/lưu/share. Không sửa raw. Mỗi lần chạy tạo UUID khác.
4. App lưu trong application-support/ocr_runs của thiết bị: <runId>.json và <runId>/image.<extension>. Không phải thư mục repo. Nếu lưu lỗi, bấm Lưu lại trước khi chạy tiếp; không đóng app khi chưa lưu.
5. Bấm Xuất JSON ở lịch sử để dùng bảng chia sẻ hệ điều hành. Người nhận đọc JSON UTF-8 schemaVersion=1, rawText, imageId/runId, metadata, elapsedMs/status. imagePath là đường dẫn **tương đối riêng trong app**, không phải URL hoặc ảnh gửi kèm. Lấy ảnh nguồn theo imageId từ 4.08. Hủy share không xóa dữ liệu.
6. Nơi bàn giao thủ công đã ghi trong plan: work/4.09-mlkit-prototype/results/runs/*.json; README ghi dataset version và người cung cấp. Theo dõi provenance của raw native hiện có tại results/README.md; không tạo/commit kết quả giả. Chỉ đưa ảnh/kết quả không PHI đã được kiểm tra vào repo; không tự động upload.

Trạng thái JSON: text, no_text, input_error, engine_error. Lỗi lưu/share là thông báo riêng; không đổi status engine. Cancel picker không tạo OCR run. Đóng màn hình chờ engine xong để giải phóng tài nguyên, không thông báo lên UI đã đóng. Android phục hồi ảnh picker sau process death nhưng không tự chạy OCR.

## Đợt B: các trường phải chốt trước đo

- Phiên bản/hash bộ dữ liệu 4.08 và bằng chứng ảnh chụp thật, nhãn đã xác minh (tên thuốc và hoạt chất, Unicode đầy đủ); người xác minh và ngày.
- Thiết bị bắt buộc dưới dạng platform/model (các model Android cần kiểm), OS, revision, package/native SDK/config cố định; lưu evidence build.
- Nhóm điều kiện ảnh, số ảnh tối thiểu và số lần lặp mỗi ảnh/mỗi thiết bị/mỗi cold-warm. Template chưa có số mẫu tối thiểu: người chốt phải bổ sung trước khi freeze; không suy từ pilot.
- Định nghĩa cold: run đầu sau khởi động process/engine mới. Warm: run tiếp sau engine đã được khởi tạo; ghi sidecar phase theo ghi chép thực tế, không tự suy từ latency.
- Normalization đề xuất: Unicode NFC, casefold, gộp whitespace; giữ dấu, không sửa chính tả/fuzzy. Field đúng khi target đầy đủ xuất hiện như token span trong raw. Không đo khả năng matching catalog hoặc an toàn dùng thuốc.
- Ngưỡng accuracy riêng drugName/activeIngredient, áp dụng tổng và từng condition/device/phase; latency p95 cho từng device/phase; số ảnh/số lần lặp đủ đại diện do nhóm chốt.
- Quy tắc chọn cố định: với mỗi imageId/device/phase lấy n run sớm nhất theo createdAt, phá hòa bằng runId. Run lỗi/no-text sớm vẫn được giữ, không chọn run tốt nhất. UUID chưa biết trước đo nên không đóng băng danh sách UUID ngẫu nhiên trong protocol. Bản JSON protocol lưu version/frozenAt trước mọi run, selection=earliest_createdAt_then_runId.

Tạo benchmark-protocol.json từ cấu trúc dưới, để status=draft cho tới khi đã chốt. Ngày, device, số và hash dưới đây là chỗ trống, không phải ngưỡng đề xuất:

```json
{
  "status": "draft",
  "version": null,
  "frozenAt": null,
  "datasetVersion": null,
  "datasetHash": null,
  "requiredDevices": [],
  "requiredConditions": [],
  "repetitions": null,
  "thresholds": {"drugName": null, "activeIngredient": null},
  "latencyP95Ms": null,
  "normalization": "NFC_casefold_whitespace",
  "selection": "earliest_createdAt_then_runId"
}
```

Evaluator nhận bản sao export bổ sung **phase** từ biên bản chạy (cold/warm). Không sửa raw hoặc metadata gốc. Lưu JSON nguyên gốc riêng để đối chiếu; phase sidecar chỉ phục vụ đánh giá. Manifest theo benchmark_manifest.example.json, không dùng nhãn làm input engine. DatasetHash là hash dataset đã xác minh trong 4.08; script so giá trị khai báo, người chạy phải kiểm hash với nguồn và số lượng ảnh thật trước freeze.

```powershell
python work/4.09-mlkit-prototype/scripts/evaluate_ocr.py --protocol work/4.09-mlkit-prototype/benchmark-protocol.json --manifest <verified-manifest.json> --runs <annotated-runs-directory> --output work/4.09-mlkit-prototype/benchmark-report.json
```

Output gồm score đúng/tổng/excluded từng field và condition/device/phase; rows truy vết imageId/runId/status; timing n/median/p95. Nhãn thiếu hoặc chưa xác minh: excluded, không đúng; no_text/error/missing raw với nhãn hợp lệ không tính đúng. Thiếu run/thiết bị/nhóm, protocol draft, sai config, thiếu timing: pending, không tự kết luận go. Đủ evidence nhưng điểm dưới ngưỡng: no-go. Điểm từ fixture unit test không phải benchmark thực tế.

## Native verification còn phải chạy

- Thiết bị Android thật: text/blank/hỏng, offline sau cài model, cancel picker, quyền truy cập thư viện, back/background/process death, double tap, share JSON và đọc trên máy khác.
- Chạy integration_test/ocr_prototype_test.dart với OCR_IMAGE_BASE64 là PNG/JPEG fixture thực, OCR_EXPECTED_TEXT tùy chọn; thiếu ảnh thì ca text được skip và phải ghi pending. Test blank/hỏng vẫn chạy. Không dùng kết quả Windows/widget fake thay native.
- Native test nhận OCR_IMAGE_PATH (đường dẫn ảnh trong sandbox app; dùng trên Windows để tránh giới hạn độ dài tham số) hoặc OCR_IMAGE_BASE64, cùng OCR_IMAGE_ID, OCR_DEVICE_MODEL, OCR_OS_VERSION, OCR_APP_REVISION, OCR_NATIVE_SDK_VERSION, OCR_DEVICE_KIND và OCR_IMAGE_SOURCE. Dùng --dart-define-from-file=<local-json> để truyền ảnh/metadata; không commit file base64 trong scratch. Ca text chạy qua controller + FileOcrStore, lưu raw JSON vào application-support/ocr_runs rồi đọc lại để kiểm export. Picker fixture thay phần chọn thư viện; quyền/gallery/share sheet vẫn cần manual.
- Ví dụ smoke: flutter test integration_test/ocr_prototype_test.dart -d <device> --dart-define-from-file=<local-json>.
- Để thu raw trước khi Flutter dọn test app: đặt biến môi trường OCR_RESULTS_DIR trỏ tới thư mục results của task; chạy `flutter drive --driver=test/features/ocr_prototype/native_export_driver.dart --target=integration_test/ocr_prototype_test.dart -d <device> --dart-define-from-file=<local-json>`. Driver ghi nguyên chuỗi JSON nhận từ app, tạo file riêng run và không overwrite nội dung khác. Không đổi raw hoặc biến kết quả smoke thành benchmark.
- Với OCR_IMAGE_PATH: cài APK debug trước, chép fixture vào sandbox app bằng adb run-as, đối chiếu SHA-256 rồi chạy; không nạp nhãn. Bản APK native test là harness; khi bàn giao ứng dụng cần build lại với `-t lib/main_ocr_prototype.dart`.
- Không có yêu cầu build/test iOS trong phạm vi mới; không dùng kết quả Android để tuyên bố hỗ trợ iOS.
