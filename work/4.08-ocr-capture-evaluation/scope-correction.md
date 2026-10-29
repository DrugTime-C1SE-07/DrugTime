# Nội dung thay thế để chốt 4.08/4.09 · 2026-10-29

Nguồn: bảng Sprint mới và yêu cầu trực tiếp của người dùng bỏ nghiên cứu Tesseract khỏi dự án. Đây là đề xuất cụ thể để rà soát trước khi reopen, không thay requirement/plan approved.

## 4.08 · Collect + label packaging sample set

Mục tiêu: bàn giao ảnh bao bì có nhãn cho nhóm, không chạy/đánh giá engine hoặc nghiên cứu góc chụp bằng Tesseract. Không yêu cầu cài engine/ngôn ngữ hoặc hoàn tất script thử nghiệm cũ để đóng task.

Đầu ra: datasets/images, labels.xlsx, README hướng dẫn và bản kê phiên bản/hash/nguồn/xác minh. ID/path một ảnh một dòng, tên thuốc theo bao bì, strength chỉ ghi khi đọc được. Không lấy raw OCR làm đáp án.

AC thay thế đề xuất:

1. Mỗi ảnh có ID duy nhất và một dòng nhãn, đường dẫn tồn tại và không thoát dataset.
2. Người kiểm xác minh tên sản phẩm/biến thể và strength trên từng ảnh; không đoán từ tên folder hoặc raw. Có người/ngày xác minh, phần chưa rõ ghi thiếu.
3. Có thống kê số ảnh/sản phẩm/loại bao bì, điều kiện/nguồn biết được và hạn chế; không tự ghi ảnh web là ảnh chụp thật hoặc bịa góc/thiết bị.
4. Chốt phiên bản ảnh/nhãn/hash và README để dùng lại. Ảnh xử lý từ cùng nguồn không tự tính là các mẫu nguồn độc lập.
5. Bộ dữ liệu được nhóm truy cập qua repo sau commit/push được người dùng yêu cầu; review và phê duyệt theo workflow.

Không thay API/DB/client trong phần bộ dữ liệu. Không chấm hoạt chất bắt buộc, huấn luyện OCR hoặc làm matching; matching thuộc 4.13, top-N toàn luồng thuộc 4.17. Giữ bằng chứng thử nghiệm cũ là lịch sử, không dùng nó làm điều kiện hoàn thành task mới.

## 4.09 · Prototype, measurement và quyết định hướng ML Kit

Giữ prototype Android, raw nguyên vẹn, import/chấm/report và yêu cầu xử lý lỗi/native export. Tên thuốc là chỉ số chính; hàm lượng độc lập. 49/49 ảnh đã có run trong pilot-002, không cần quét lại chỉ vì sửa nhãn hoặc hồ sơ.

AC7 thay thế đề xuất: Given báo cáo pilot Android có raw truy vết, số liệu và giới hạn, When người phụ trách chọn hướng, Then lưu GO/no-go cùng người/ngày/lý do; không đồng nhất với benchmark đạt ngưỡng đặt trước hoặc accuracy matching. Nếu làm benchmark chính thức có ngưỡng, vẫn phải freeze protocol trước lần đo.

Người dùng đã chọn GO trong chat ngày 2026-10-29. Ghi quyết định hướng này trong báo cáo nháp; không đổi summary.generated decision=not_decided thành “đạt benchmark”. Partial/token rời chỉ là đầu vào có thể dùng tiếp, không tính tất cả thành matching đúng.

Để bàn giao: rà nhãn theo ảnh, chấm lại bằng raw hiện có, lưu phiên bản/hash và số liệu; hoàn tất native manual còn thiếu/test report/testcase/review. Không phải chờ 4.12/4.13 hoặc làm thêm nghiên cứu engine cũ. Sửa AC7 cần reopen requirement, không tự tuyên bố AC7 cũ đã đạt.

## Thứ tự và file cần đồng bộ

- 4.08: 01-requirement.md, 03-plan.md, 04-impl-notes.md, sau đó test/review theo nội dung mới; README/data snapshot theo phạm vi được duyệt.
- 4.09: 01-requirement.md, 03-plan.md và các hồ sơ đầu ra bị ảnh hưởng; không sửa app/evaluator để tạo điểm GO giả.
- Không tự xóa công cụ, raw/ảnh hoặc file lịch sử trước đây người dùng đã yêu cầu giữ. Việc bỏ nghiên cứu cũ khỏi phạm vi không đòi xóa bằng chứng.

Lệnh người dùng chạy từ D:\DrugTime để mở artifact đang approved:

```powershell
python .agents/scripts/gate.py reopen 4.08-ocr-capture-evaluation requirement
python .agents/scripts/gate.py reopen 4.08-ocr-capture-evaluation plan
python .agents/scripts/gate.py reopen 4.09-mlkit-prototype requirement
python .agents/scripts/gate.py reopen 4.09-mlkit-prototype plan
```

Sau reopen, agent cập nhật requirement trước; chỉ sau duyệt mới chuyển plan/implement/test/review. Không tự reopen hoặc approve.
