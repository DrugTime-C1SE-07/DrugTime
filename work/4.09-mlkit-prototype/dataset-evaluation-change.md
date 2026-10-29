# Đề xuất cập nhật 4.09 theo dataset dùng chung

Ngày: 2026-10-28. Trạng thái: đề xuất, chưa triển khai. Nguồn: yêu cầu trực tiếp của người dùng trong chat.

## Hiện trạng đã đọc

- Gate: requirement, plan, implement approved; test draft. Gate test OK tại evidence/test-dataset-change-gate.log.
- Plan đang quy định script và raw trong work/4.09-mlkit-prototype; AC5 còn chấm tên/hoạt chất.
- datasets/ có labels.xlsx với các cột image_id, relative_path, drug_name, strength; header bắt đầu B2. Không giả định header ở A1 hoặc sheet tên Labels.
- Có 17 file JPG trong datasets/images. Có 6 JSON raw lịch sử trong work/4.09-mlkit-prototype/results/runs; các run cũ không mặc nhiên thuộc dataset hiện tại. Năm run cũ imageId=1 chưa có ánh xạ đã xác minh.
- Ảnh chụp màn hình người dùng gửi hiển thị runId 71e2ac39-c00b-45b4-a5ea-f604fda06de5. Chưa có JSON gốc của run này trong 6 file trên; không dựng JSON/raw từ screenshot hoặc bịa elapsedMs/metadata.

## Cấu trúc đích

```text
datasets/
  README.md
  labels.xlsx
  images/                          # giữ nguyên ảnh gốc và tên
  scripts/
    import_android_runs.py         # lấy JSON gốc bằng adb; mặc định chọn thiết bị rõ ràng
    evaluate_ocr.py
    test_evaluate_ocr.py
  results/
    legacy-pilot/
      raw/                         # bản sao byte nguyên vẹn của 6 raw cũ
      provenance/                  # index cũ, hash và mapping nếu xác minh được
    pilot-001/
      raw/                         # JSON mới, filename theo runId
      run-map.csv                  # chỉ ghi ánh xạ đã xác minh, tách khỏi raw
      per_image.csv
      summary.json
      report.md
```

- work/ giữ requirement/plan/impl/test/review và evidence quy trình; dữ liệu dùng chung nằm ở datasets/.
- Bước chuyển ban đầu sao chép và đối chiếu SHA-256; giữ bản cũ để các evidence/link approved còn truy vết được. Không xóa bản cũ trong lần chuyển này.
- Android vẫn lưu ảnh/JSON trong sandbox app. Đường dẫn repo là đích trên máy tính sau export/import, không thể ép app Android ghi trực tiếp vào D:\DrugTime.
- Không tải lại hoặc tự chạy OCR ảnh khi chỉ nhập raw. Không sửa rawText, imageId hoặc metadata trong payload gốc.

## Quy tắc chấm pilot đề xuất

1. Đọc XLSX trực tiếp, tìm header theo tên cột; giữ workbook nguyên vẹn. Kiểm ID trùng, đường dẫn không hợp lệ/thoát datasets, ảnh thiếu, nhãn thiếu.
2. Ghép imageId chính xác với image_id. Cho phép tên file gồm đuôi hoặc ID cũ chỉ qua mapping rõ ràng; ID không rõ => unmapped và không tự đoán từ nội dung chữ.
3. Chọn run sớm nhất có createdAt hợp lệ rồi runId cho mỗi ảnh/thiết bị; giữ mọi run trong bảng chi tiết. Không chọn kết quả đẹp nhất; không gộp máy ảo với điện thoại thật.
4. Chấm tên chính bằng Unicode NFC, casefold và thu gọn whitespace; exact phrase theo ranh giới từ, cho phép xuống dòng giữa các từ. Không bỏ dấu, đổi 0 thành O hoặc fuzzy matching.
5. Báo riêng: exact_name, tokens_present_noncontiguous (đủ token đúng nhưng không thành cụm liên tiếp), partial_name, name_not_found, no_text, input_error, engine_error, not_run, invalid_run, unmapped. Đủ token phải tính cả số lần lặp token; đây là chẩn đoán phụ, không tính đạt exact_name và không dự đoán matching sẽ thành công.
6. Screenshot Decolgen: có Decolgen và FORTE nhưng bị tách bởi chữ khác, nên dự kiến tokens_present_noncontiguous theo phần nhìn thấy. Chỉ chấm chính thức khi có JSON gốc nối đúng ảnh. Không xem dòng UUID là OCR khi chưa kiểm cấu trúc payload.
7. strength là trường phụ độc lập, không chấm hoạt chất và không gộp vào điểm tên. Nhãn trống => unscored. Với nhãn ghép nhiều thành phần, không giả định exact cả chuỗi là phép đo hàm lượng đúng; ghi requires_component_protocol cho tới khi quy tắc thành phần–hàm lượng được thống nhất. Không coi 500 mg xuất hiện ở bất kỳ thành phần nào là đúng cả sản phẩm.
8. Công bố tử/mẫu: exact trên các ảnh đã chạy hợp lệ có nhãn tên; OCR no_text/lỗi tính không đạt. Báo coverage đã chạy/tổng ảnh nhãn hợp lệ và not_run riêng để thiếu kết quả không bị che. Báo mẫu số 0 là null/N/A.
9. Báo theo sản phẩm, loại bao bì lấy từ relative_path; không tự suy góc chụp từ tên file. Timing median/p95/n tách theo thiết bị, chỉ run có thời gian engine hợp lệ; không tính screenshot timing hoặc lỗi như timing thành công.
10. Pilot luôn ghi decision=not_decided. Benchmark chính thức cần snapshot ảnh/nhãn/hash, protocol, ngưỡng và tập thiết bị chốt trước lần đo; không áp ngưỡng sau khi thấy pilot.

## Kiểm thử cần có

- XLSX header lệch B2, nhãn trống, ID trùng, đường dẫn sai; không sửa workbook.
- Exact qua xuống dòng; ranh giới từ; token đủ nhưng tách xa/đảo thứ tự; token thiếu/sai ký tự; token lặp không đủ.
- Missing run/no_text/engine_error, timestamp hỏng, imageId không rõ, run nhiều lần, thiết bị khác nhau; mẫu số và coverage đúng.
- Hàm lượng trống/ghép nhiều thành phần không báo đạt giả; raw gốc bất biến.
- Nhập trùng file giống nhau bỏ qua an toàn; cùng runId khác byte từ chối overwrite; hash bản sao legacy khớp; không chọn ảnh/run tốt nhất.

## File dự kiến thay đổi

- datasets/README.md; datasets/scripts/**; datasets/results/**.
- Các tài liệu hướng dẫn/script cũ trong work/ chỉ cập nhật khi plan cho phép, không sửa artifact đã approved.
- Không cần thay dependency hoặc code nhận diện ML Kit, không đổi API/DB, không triển khai normalization/matching sản phẩm của 4.12/4.13.

## Bước tiếp theo

- Người dùng reopen requirement để cập nhật AC5 và nơi lưu; reopen plan/implement để có thể cập nhật phạm vi và triển khai sau khi đầu vào được duyệt lại.
- Lệnh: python .agents/scripts/gate.py reopen 4.09-mlkit-prototype requirement
- Lệnh: python .agents/scripts/gate.py reopen 4.09-mlkit-prototype plan
- Lệnh: python .agents/scripts/gate.py reopen 4.09-mlkit-prototype implement
- Agent không tự reopen/approve. Chưa sửa datasets, evaluator hoặc raw trong vòng khảo sát này.
