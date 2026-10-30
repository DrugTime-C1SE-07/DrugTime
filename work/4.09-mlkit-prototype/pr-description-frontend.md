# feat(ocr): add Android ML Kit packaging prototype

Refs: 4.09 · PB31

Thêm entrypoint thử nghiệm `main_ocr_prototype.dart` để chọn ảnh bao bì có sẵn trên Android, xem raw ML Kit và thời gian xử lý, lưu từng run độc lập rồi xuất JSON cho bộ đo trong superproject. Prototype không tự chọn/lưu thuốc hoặc gọi matching/backend.

Adapter ML Kit Latin, gallery, controller và store tách biệt; phân biệt no_text/input_error/engine_error/cancel, khóa thao tác lặp và cho lưu lại khi lỗi bộ nhớ. Raw/ảnh được giữ nguyên, metadata ghi theo tester xác nhận. Android minSdk24; lock hiện yêu cầu Flutter>=3.47 và Dart>=3.13. Không sửa iOS.

Kiểm chứng đã có: 13 Flutter unit/widget và native smoke emulator trong evidence của task; pilot49 JSON được đo tại superproject. Review hiện tại đọc diff/code/log, không chạy lại native hoặc nhận các ca manual chưa kiểm là Pass. Hạn chế native/lifecycle/share đã được chấp nhận ở mức prototype trong báo cáo test approved; chưa chứng minh sẵn sàng production.

Tái hiện khi cần: từ frontend/mobile, `flutter run -d <android-device-id> -t lib/main_ocr_prototype.dart`, chọn ảnh, điền image_id/metadata thực, chạy OCR và xem raw. Không cần quét lại toàn bộ dataset để review PR code này.

PR liên quan: docs workbook và superproject datasets/report/decision; điền liên kết thật sau khi tạo. Merge frontend trước superproject; sau squash dùng SHA đã merge, không bump con trỏ tới commit chưa push.
