# Ghi chú brainstorm task 5.03 — yêu cầu xóa tài khoản

Ngày ghi: 2026-11-11. Mục đích: ghi nhận trao đổi để cập nhật tài liệu sau; chưa phải đặc tả được duyệt.

## Ý kiến người dùng
- Người dùng bấm xóa tài khoản; trong 30 ngày kể từ thời điểm đó, đăng nhập lại sẽ tự hủy yêu cầu xóa và người dùng tiếp tục sử dụng với dữ liệu cũ.
- Trong 30 ngày đầu, người thân đã liên kết không được xem mọi thông tin liên quan tới tài khoản đang được yêu cầu xóa, dù liên kết vẫn còn.
- Khi đang chờ xóa, không tạo gợi ý món ăn mới từ dữ liệu của tài khoản đó; sau khi đăng nhập lại hủy yêu cầu, người dùng tiếp tục sử dụng bình thường.
- Khi đăng nhập lại hủy yêu cầu, khôi phục quyền xem của người thân theo cài đặt chia sẻ cũ nếu liên kết và consent vẫn còn hiệu lực.
- Sau 30 ngày, dữ liệu cũ không còn; người dùng cần thiết lập lại tài khoản như tài khoản mới bình thường.
- Người dùng cho biết OCR quét lỗi thì không lưu lại kết quả; cần xác định chính xác phạm vi “quét lỗi” khi đặc tả OCR, chưa suy ra toàn bộ ảnh hoặc dữ liệu OCR không được lưu.
- Cần cập nhật tài liệu sau: nội dung này khác QD-35 hiện ghi thời gian hủy 7 ngày.

## Đề xuất của agent, chưa được người dùng chốt
- Hết 30 ngày xóa cứng dữ liệu cá nhân và sức khỏe; xử lý riêng audit tối thiểu và bản sao lưu theo chính sách đã duyệt.
- Xóa cả tài khoản đăng nhập sau thời gian chờ; người dùng đăng ký lại nếu muốn dùng tiếp.

## Cần làm rõ
- Cơ chế xác thực khi đăng nhập lại và cách xử lý chính xác tại thời điểm hết 30 ngày?
- Sau thời gian chờ xóa tài khoản đăng nhập hay giữ để thiết lập lại? Quy tắc tái sử dụng email?
- Trong thời gian chờ có dừng tính năng gợi ý món ăn / xử lý AI không? QD-35 có nói ngừng AI nhưng chưa định nghĩa phạm vi cụ thể; QD-41 nói giai đoạn 1 không gửi dữ liệu sức khỏe tới LLM ngoài, dùng mẫu đã duyệt và quy tắc.
- Admin có vai trò duyệt hay chỉ giám sát, xử lý lỗi? QD-35 mô tả tự động; backlog/schema cũ thể hiện duyệt.
- Quy định dữ liệu chưa đồng bộ, sao lưu, audit, thời điểm hoàn tất và xử lý lỗi xóa.
- Đối chiếu mã task: Sprint 5 Backlog ghi 5.03; Replan Log ánh xạ 5.03 sang 5.13, trong khi work/5.13 đã tồn tại cho nội dung khác.

## Nguồn
- docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md, mục 8, 10, 11 (QD-28, QD-35, QD-41).
- docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx, Product Backlog, Sprint 5 Backlog, Replan Log.
- backend/src/drugtime/modules/ai_meal/adapters/inbound/http.py; backend/src/drugtime/modules/interaction/domain/food_evaluator.py.

## Bước tiếp theo
Tiếp tục brainstorm và xác nhận các câu hỏi mở. Khi bắt đầu phân tích task chính thức, xác định task ID, chạy gate và dùng wf-requirement; chuyển các ý đã chốt sang artifact, sau đó cập nhật tài liệu nguồn theo quy trình được duyệt.



