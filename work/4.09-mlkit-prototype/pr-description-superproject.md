# feat(ocr): add shared packaging dataset and ML Kit pilot decision

Refs: 4.08, 4.09 · PB31

Đưa ảnh/nhãn và raw OCR vào thư mục datasets dùng chung ở superproject để các task normalization, matching và kiểm toàn luồng dùng lại, thay vì phải tìm kết quả trong work cá nhân. Datasets là thư mục thường, không tạo submodule mới.

4.08 bàn giao49 ảnh có ID/path ổn định, labels.xlsx, annotations.v1.csv, manifest.v1.json và README:28 hộp/21 vỉ,23 tên sản phẩm. Nhãn được rà theo ảnh, không theo raw/folder; strength không đọc được giữ trống. Nguồn chưa rõ ghi unknown, người rà ghi đúng AI; không nhận là xác minh độc lập hoặc bộ đại diện mọi điều kiện.

4.09 có công cụ import JSON nguyên byte, chấm exact tên riêng với token rời/partial/no_text, báo cáo CSV/JSON/Markdown và quyết định **GO tiếp tục ML Kit Android** từ pilot. Pilot-002 phủ49/49, exact27/49 (55.1%), partial5/token rời2/name_not_found14/no_text1; median2615ms/p95 5267ms trên emulator. GO là quyết định hướng kỹ thuật riêng; summary tự động vẫn not_decided. Đây không phải accuracy matching hoặc đạt ngưỡng benchmark đặt trước.

Kiểm chứng: evidence trước có41 Python unit và5 host checks; review tái tính số liệu, đối chiếu actual image/workbook/annotations/raw/report hashes và64 testcase trong file tổng. Không OCR lại hoặc đổi raw để đạt điểm. Các ca chưa kiểm giữ là giới hạn prototype theo05 approved, không yêu cầu chạy lại49 ảnh. Nghiên cứu Tesseract cũ không là dependency hay điều kiện hoàn thành; dữ liệu lịch sử được giữ tách biệt.

Tái hiện chấm nếu cần, từ gốc superproject:

```powershell
python datasets/scripts/evaluate_ocr.py --labels datasets/labels.xlsx --runs datasets/results/pilot-002/raw --output <review-output-directory>
```

Dùng output riêng khi review để giữ nguyên các file đang ghim hash trong decision. Nếu sửa nhãn/ảnh/report sau này, tạo snapshot và cập nhật chứng cứ quyết định đúng phiên bản.

Lưu ý review Low: README còn một số câu manual/go-no-go cũ; nguồn trạng thái hiện hành là05 approved và decision.json. Dữ liệu hiện cục bộ, sau push mới kiểm việc clone/pull của nhóm. Không đưa scratch, .env, .gitignore/api_contract hoặc con trỏ baseline không liên quan vào commit này.

Liên kết PR frontend/docs: bổ sung URL thật sau khi tạo. Thứ tự merge frontend → docs → superproject. Chỉ bump con trỏ tới commit đã push/đã merge; cập nhật SHA sau squash. Cần ít nhất một người khác approve PR để đạt Definition of Done.
