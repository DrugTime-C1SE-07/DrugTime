---
description: "Quy tắc bắt buộc cập nhật README.md trước khi push lên nhánh mới (feat/fix/chore)"
globs: "*"
---

# Quy Tắc Đồng Bộ & Cập Nhật README Khi Push Nhánh Mới

Mỗi khi Agent hoàn thành một tính năng (feature), sửa lỗi (fix), hoặc dọn dẹp/cấu hình (chore) và chuẩn bị push lên một nhánh mới trên GitHub:

## 1. Bắt Buộc Cập Nhật README.md
- **Không bao giờ push nhánh mới mà để `README.md` cũ hoặc sơ sài.**
- Bắt buộc phải kiểm tra và cập nhật file `README.md` của repository hoặc submodule đang thực hiện:
  1. **Mục tiêu của nhánh:** Nhánh này giải quyết vấn đề gì, thêm tính năng gì hoặc tài liệu nào?
  2. **Bản đồ tài nguyên / Thay đổi chính:** Liệt kê các file mới, module mới, API mới hoặc những thay đổi đáng chú ý.
  3. **Hướng dẫn sử dụng / Kiểm thử nhanh:** Các lệnh chạy, test hoặc đường link tra cứu liên quan.

## 2. Quy Trình Commit & Push
1. Hoàn tất code/tài liệu.
2. Cập nhật `README.md` phản ánh chính xác trạng thái của nhánh hiện tại.
3. Commit `README.md` cùng với các thay đổi (hoặc commit riêng: `docs: update README for <branch_name>`).
4. Tiến hành `git push origin <tên-nhánh>` lên GitHub.
5. Đảm bảo khi người dùng hoặc thành viên team truy cập giao diện GitHub của nhánh đó, `README.md` hiển thị rõ ràng ngữ cảnh và nội dung vừa làm.
