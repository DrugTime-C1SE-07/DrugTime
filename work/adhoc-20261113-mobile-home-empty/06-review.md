---
task: adhoc-20261113-mobile-home-empty
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-14 23:07 +0700
content_hash: sha256:93b52e2f5d46297e
inputs:
  01-requirement.md: sha256:b3edca5e56e36204
  03-plan.md: sha256:4d828faaef3faf4a
  04-impl-notes.md: sha256:65e5710145df911f
  05-test-report.md: sha256:5b5dd1e9c142317e
---

# S05-empty và popup chào mừng · Review

## 1. Kết luận

**Đạt để bàn giao UI, kèm lưu ý.** Phạm vi bàn giao do người dùng chốt gồm UI Trang chủ S05-empty và popup chào mừng, kể cả mở, kéo và đóng popup. Lưu qua form, quét camera và nối điều hướng nghiệp vụ được chuyển sang công việc sau. Còn khác biệt trực quan với Figma và chưa kiểm vùng an toàn, cử chỉ trên thiết bị thật.

Kết luận này áp dụng cho bàn giao UI. AC của requirement đã duyệt và trạng thái test giữ nguyên làm bằng chứng lịch sử. Tiêu chí merge toàn task vẫn chưa đạt vì bộ Flutter còn 5 ca đỏ và các luồng trong requirement gốc chưa được xác nhận đầy đủ.

## 2. Phạm vi đã review

| Submodule | Phạm vi |
|---|---|
| frontend | Checkout task. `git diff origin/main...HEAD` không có thay đổi đã commit. Kiểm `git diff HEAD` và đọc các file Dart, test mới từ `git ls-files --others --exclude-standard`. |
| docs | Checkout riêng trên nhánh task. Diff worktree có một workbook. Mở lại file bằng openpyxl, xác nhận sheet HOMEEMPTY có tiêu chí góc dưới vuông và sheet Report tồn tại. |

Scope implement đạt tại checkout task. Log `evidence/review-home-nav-scope.log`.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | Hình dạng popup, đường đóng/mở và Giảm chuyển động có bằng chứng. AC toàn màn chưa được xác nhận đầy đủ. |
| Phạm vi | Các file frontend nằm trong bảng plan. Workbook nằm trong checkout docs của task. |
| Contract và kiến trúc | Không có thay đổi contract hoặc API. Điểm vào frontend tái sử dụng router, controller và luồng capture hiện có. |
| Bảo mật | Không thấy credential hoặc điểm truy cập dữ liệu mới trong diff Dart. |
| Xử lý lỗi | Controller giữ danh sách khi tải lỗi, Trang chủ có Thử lại. Fixture xác nhận Thử lại sau lỗi tải. |
| Hiệu năng | Không thấy truy vấn mới. Chuyển động popup dùng translation trên widget con có sẵn. Chưa đo trên điện thoại. |
| Chất lượng test | Bốn ca fixture và ca kiểm tọa độ navbar đạt. Ba ca HOMEEMPTY còn Pending. Hai ca AppShell Người thân vẫn fail trong suite. |
| Dễ đọc và nhất quán | Hình dạng dùng Material. Vùng tay nắm và vùng cuộn có bộ xử lý riêng. |
| Đối chiếu log | 1.032 pass, 1 skip và 5 fail. Năm tên lỗi trùng lần chạy trước. Validate Excel đạt, 12 Pass, 1 Fail, 3 Pending. |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Low | `mobile/lib/features/home/presentation/screens/home_screen.dart:163`, `:285`, `:308` và `mobile/lib/features/home/presentation/widgets/home_navigation_bar.dart:33` | Chữ CTA nhẹ hơn Figma và biểu tượng chuông, Hồ sơ khác nét. Navbar đạt y734 với inset iOS 34 dp, biểu tượng quét đã cập nhật. | Chỉnh các khác biệt còn lại hoặc thống nhất mức sai khác chấp nhận được cho TC-HOMEEMPTY-01. |
| Medium | `mobile/lib/features/home/presentation/widgets/home_navigation_bar.dart:95` | Khoảng cách đáy 20 dp phụ thuộc vào đúng giá trị inset 34 dp trên iOS. Fixture chỉ kiểm cấu hình này, chưa có bằng chứng thao tác và vùng an toàn trên thiết bị. | Kiểm trên iOS có Home indicator và thiết bị khác trước khi coi vị trí navbar đã đạt trên mọi máy. |

## 5. Mô tả PR

Frontend: bàn giao UI S05-empty và popup chào mừng cho task `adhoc-20261113-mobile-home-empty`. Kiểm bằng ảnh fixture 375 × 812, ca tọa độ navbar và widget test popup. Lưu ý khác biệt chữ CTA, biểu tượng và vùng an toàn trên thiết bị thật.

Docs: bổ sung bảng HOMEEMPTY và báo cáo test. Giữ kết quả 12 Pass, 1 Fail, 3 Pending như đã chạy. Superproject ghi nhận artifact task. Nếu sau đó mở PR, cập nhật con trỏ superproject sau khi các thay đổi frontend và docs đã được đưa lên remote.

## 6. Ghi chú cho quy trình

Scope giai đoạn test tính cả 33 thay đổi implement chưa commit trong worktree. Scope implement chạy lại và đạt. Review dùng bằng chứng của giai đoạn test đã duyệt.

## Bước tiếp theo

- Chờ người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261113-mobile-home-empty review`. Review là giai đoạn cuối theo `wf-next`.
- Bàn giao từ checkout `scratch/checkout/frontend` và `scratch/docs-test-checkout`, cùng nhánh `feat/adhoc-20261113-mobile-home-empty`. Code UI, workbook và artifact bàn giao còn ở worktree. Preview và bằng chứng xem trong báo cáo test. Luồng nghiệp vụ sẽ được nối trong công việc sau.
- Cập nhật lần cuối 2026-11-14, Codex.
