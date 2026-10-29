# Bàn giao 4.08/4.09 · 2026-10-29

4.08 và 4.09 đã duyệt hết; gate hiện trả “không còn (đã xong)” cho cả hai task. Lần sửa đường dẫn cá nhân trong README đã hoàn tất:04 được duyệt lại17:11+0700,05/06 được duyệt lại17:14+0700 với đúng hash04 mới. Không còn approval stale. Đã kiểm225 hash nguồn/kết quả không đổi; không chạy lại OCR/unit/Flutter hoặc yêu cầu kiểm lại49 ảnh.

Trước lần sửa README này, cả hai task đã được duyệt hết, hai review kết luận Đạt kèm lưu ý; evidence Python41 test/5 host và testcase53 Pass/0 Fail/11 Pending giữ nguyên, không nhận là vừa chạy lại.

**Chỉ dẫn mới nhất của người dùng: “đẩy cho tôi”.** Chỉ dẫn này thay thế yêu cầu giữ cục bộ trước đó: được commit/push phần dataset, hồ sơ4.08/4.09 và workbook docs; được cập nhật con trỏ frontend/docs tới commit đã có trên remote. Không đẩy baseline ngoài task, scratch/build/secret. Không mở PR hoặc merge nếu chưa được yêu cầu.

Docs đã commit/push `6fd7c59` trên `codex/4.09-ocr-testcases`; GitHub ls-remote xác nhận đúng SHA. Frontend `281f9ff` đã xác nhận trong origin/feat/mlkit-prototype-measurement sau fetch. Bộ dataset và hồ sơ đã push bằng commit `976286d18cd4679011c16e0a2a41babd437185d8` trên feat/datasets-ocr; GitHub ls-remote xác nhận. Commit kế tiếp chỉ ghi biên bản/bằng chứng xuất bản này. Các câu “local_only” trong snapshot lịch sử đã duyệt không phải trạng thái xuất bản hiện tại.

Khi đóng gói Git phát hiện core.autocrlf=true trên máy hiện tại. Thêm .gitattributes chỉ cho datasets và work của hai task để Git không đổi byte xuống dòng khi checkout; cần bảo toàn SHA-256 raw/report/evidence đã ghi. Không đổi byte ảnh/raw hoặc approval metadata. Scratch và code nghiên cứu Tesseract cũ trong work không đưa vào bản bàn giao hiện hành; evidence lịch sử được giữ để đối chiếu.

Chốt đúng bộ ảnh/prototype; Pending là giới hạn, không buộc chạy thêm8 ca Android hoặc kiểm lại49 ảnh. GO kỹ thuật đã lưu; không chờ benchmark ngưỡng/Tesseract. Đã kiểm clone mới từ GitHub với core.autocrlf=true:225 hash dữ liệu giữ nguyên, báo cáo tái tạo49/49 và exact27,0 lỗi dữ liệu. Evidence: publish-fresh-clone.log, publish-staged-audit.log, publish-docs-push.log, publish-superproject-push.log. Chưa mở PR hoặc có PR approval của người khác; không nhận là đã đạt Definition of Done về PR.

Trạng thái sau khi xuất bản dữ liệu:

- Superproject còn baseline riêng `.agents`, `.gitignore`, `api_contract`, `backend`; không stage hoặc đẩy các thay đổi này. Con trỏ frontend/docs và datasets đã commit đúng phạm vi.
- Frontend feat/mlkit-prototype-measurement sạch; không tạo code commit mới.
- Docs codex/4.09-ocr-testcases sạch sau commit workbook.
- Work artifact/spec/xlsx/evidence đã đưa vào bản bàn giao có chọn lọc dù work bị ignore; không đưa scratch/build hoặc code nghiên cứu OCR cũ vào Git. Scope log cũ là ảnh chụp trước xuất bản, không thay Git status hiện tại.

## Bước tiếp theo

Hoàn tất yêu cầu commit/push. Không cần duyệt lại hoặc quét lại ảnh; chỉ ghi biên bản xuất bản, không sửa artifact approved. Các PR description là bản nháp nếu người dùng yêu cầu mở PR sau này; không tự mở PR/merge.

Cập nhật: 2026-10-29, Codex; không sửa artifact approved.
