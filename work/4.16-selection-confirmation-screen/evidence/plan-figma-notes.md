# Đối chiếu Figma — task 4.16

- Ngày đọc: 2026-10-26; công cụ: Reqwise Figma MCP, chỉ đọc.
- File: `Prototype_DrugTime`; page: `Page 1` (`0:1`); fileKey do bridge trả về là null, chưa có URL được xác minh.
- `get_document_info`: file có 2 page, `Page 1` và `00 · Design Foundation`.
- Đã đọc cây chi tiết: `51:5431` (S07c · Xác nhận thông tin quét), `33:4419` (S07 · Thêm thuốc mới); đọc metadata `140:2` (S06a · Danh mục thuốc (tra cứu)). Đã xem ảnh chụp S07c.
- `search_nodes` với S07: 4 frame (S07, S07a, S07b, S07c). Tìm frame có tên chứa “Không”: 0 kết quả. Cây cấp một Page 1 có 46 phần tử, chưa thấy frame riêng cho chọn nhiều ứng viên/no-result; không khẳng định mọi layer trên mọi page đều đã được rà soát.

## Sự thật từ S07c

- Kích thước 375 × 812; nền #FCFCFC; content rộng 375, padding ngang 17, trên 16, dưới 24; gap 18.
- Header “Xác nhận thông tin”, Back về camera `51:5296`.
- Banner “Đã nhận diện thông tin từ ảnh chụp”; vùng ảnh và “Chụp lại”.
- Các trường: Tên thuốc, Hàm lượng (có bút sửa), Hạn sử dụng, Số lượng.
- Lời nhắc kiểm tra lại do nhận diện tự động có thể sai.
- CTA “Tiếp tục thiết lập lịch uống” điều hướng về `33:4419`; link “Quét lại” về `51:5296`.
- CTA #01554F, trường #E7F3F1, radius 12, chiều cao CTA/trường 48.

## Áp dụng trong plan, không coi là thiết kế Figma đã có

- Tái sử dụng ngôn ngữ hình ảnh và bố cục xem lại → CTA → form thiết lập lịch; dùng token Flutter hiện có (cỡ chữ tối thiểu 14, vùng chạm 48, CTA 56).
- Thêm danh sách ứng viên, chọn một mục và vùng xem lại chỉ đọc theo requirement. Không tự sửa tên/hàm lượng làm lệch ID danh mục.
- Không thêm ảnh OCR thật, hạn sử dụng, tồn kho/số lượng, camera hoặc chức năng quét lại trong task mock. Nguồn tìm kiếm không hiển thị thông báo đã nhận diện từ ảnh.
- No-result và hành động tìm thủ công suy từ AC5/AC6, chưa có frame tương ứng được xác minh.

## Audit của frame nguồn

`layout_audit(51:5431)` trả về nodeCount 87, reportedCount 1:

- 2 issues cùng một node `51:5517`, `hi-bar/light-bg`: vượt parent và bị clip bởi `51:5516`.
- 1 style hint: 7 cỡ chữ (11.5/12.5/13/13.5/14/14.5/17); công cụ đề xuất gom thang chữ.

Đây là vấn đề của thiết kế tham khảo; không sửa canvas trong task này. Flutter dùng SafeArea của hệ điều hành và thang chữ đã có, không sao chép home indicator/clip/cỡ chữ nhỏ. Audit đo cấu trúc, không xác minh đúng nghiệp vụ. Không tạo hay sửa frame; không có stats của thao tác vẽ.
