# Feature Specification — Hàng chờ yêu cầu xóa dữ liệu

**Feature Branch** · Đề xuất `feat/5.07-admin-request-queue-ui`

**Created** · 2026-11-17  
**Status** · Draft  
**Input** · Admin dashboard: request queue UI (Sprint 5, task gốc 5.07, PB35).

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Xem yêu cầu chờ duyệt (Priority: P1)

Quản trị viên được cấp quyền mở hàng chờ từ dashboard để biết yêu cầu nào đang chờ và yêu cầu nào đã chờ lâu nhất.

**Kiểm thử độc lập** · Chuẩn bị yêu cầu ở nhiều trạng thái, trong đó có hai yêu cầu chờ duyệt trùng thời điểm gửi và đủ dữ liệu cho hai trang.

1. Khi quản trị viên mở hàng chờ, trang hiển thị đúng tổng số yêu cầu chờ duyệt và bốn trường mỗi dòng: mã yêu cầu, mã người gửi, thời điểm gửi theo giờ Việt Nam và trạng thái “Chờ duyệt”. Yêu cầu cũ nhất đứng đầu, cùng giờ thì mã yêu cầu nhỏ hơn đứng trước.
2. Khi chuyển trang rồi quay lại với tập dữ liệu ổn định, quản trị viên thấy đúng các dòng theo thứ tự đã nêu và nhận biết được trang hiện tại.
3. Khi một mục đã rời trạng thái chờ duyệt hoặc một mục mới được ghi nhận, lần làm mới thành công phản ánh danh sách và tổng số mới. Rút đồng ý riêng lẻ không tạo dòng trong hàng chờ.

### User Story 2 - Nhận biết trạng thái tải và khôi phục (Priority: P2)

Quản trị viên cần phân biệt hàng chờ trống với dữ liệu đang tải hoặc tạm thời không đọc được.

**Kiểm thử độc lập** · Lần lượt mô phỏng phản hồi chậm, hàng chờ rỗng, lỗi mạng và lỗi dịch vụ, rồi khôi phục kết nối.

1. Khi lần tải đầu đang diễn ra, giao diện báo đang tải. Khi tải thành công với tổng bằng 0, giao diện báo hàng chờ trống.
2. Khi tải thất bại, giao diện báo lỗi và có thao tác thử lại. Khi thử lại thành công, hiển thị dữ liệu từ lần đọc mới.
3. Khi tổng số dương nhưng trang hiện tại rỗng do hàng chờ thu hẹp, giao diện đưa người dùng về một trang còn hợp lệ.

### User Story 3 - Bảo vệ thông tin hàng chờ (Priority: P1)

Thông tin hàng chờ chỉ được hiển thị cho quản trị viên có quyền đọc hiện hành.

**Kiểm thử độc lập** · Thử mở màn hình khi chưa đăng nhập, hết phiên hoặc sai vai trò. Sau khi xem được dữ liệu, thu hồi quyền và làm mới.

1. Khi phiên hết hiệu lực và không thể khôi phục, yêu cầu đăng nhập lại. Khi người dùng có phiên hợp lệ nhưng thiếu quyền, hiển thị thông báo từ chối truy cập.
2. Sau khi biết lượt đọc bị từ chối hoặc người dùng đăng xuất, giao diện xóa các dòng và tổng số đã hiển thị. Tải trực tiếp và thao tác quay lại cũng không làm lộ dữ liệu khi truy cập bị từ chối.

### Edge Cases

- Các yêu cầu có cùng thời điểm vẫn giữ thứ tự ổn định khi dữ liệu nguồn không thay đổi.
- Nếu hai lần đọc chồng nhau, kết quả đến muộn của lần đọc cũ không được thay thế trang mới hơn hoặc khôi phục dữ liệu sau khi quyền truy cập bị từ chối.
- Mã người gửi dài vẫn đọc được đầy đủ. Điều hướng và thao tác tải lại sử dụng được bằng bàn phím.
- Số lượng và vị trí có thể thay đổi giữa hai lượt tải khi hàng chờ thay đổi. Điều hướng phản ánh kết quả đọc thành công gần nhất.

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001** · Dashboard cung cấp mục điều hướng tới hàng chờ cho quản trị viên. Giao diện chỉ hiển thị dữ liệu sau khi lượt đọc được cấp quyền.
- **FR-002** · Hàng chờ hiển thị duy nhất các yêu cầu xóa dữ liệu đang chờ duyệt, theo thứ tự thời điểm gửi rồi mã yêu cầu tăng dần. Mỗi mục hiển thị đủ bốn trường đã mô tả ở User Story 1.
- **FR-003** · Giao diện hiển thị tổng số, phân trang và cung cấp thao tác làm mới. Trang hết dữ liệu sau khi hàng chờ thu hẹp được xử lý như User Story 2.
- **FR-004** · Giao diện phân biệt đang tải, có dữ liệu, hàng chờ rỗng, lỗi tạm thời, hết phiên và từ chối quyền. Lỗi tạm thời có thao tác thử lại.
- **FR-005** · Giao diện loại bỏ dữ liệu đã hiển thị khi đăng xuất hoặc khi một lần đọc xác nhận phiên không còn hiệu lực hay quyền đã bị thu hồi. Màn hình giới hạn dữ liệu từng mục ở bốn trường đã nêu.
- **FR-006** · Các thao tác của hàng chờ chỉ đọc. Phạm vi phiên bản này kết thúc ở danh sách, điều hướng giữa các trang và làm mới. Xác minh hồ sơ, duyệt, từ chối, gửi yêu cầu và thực thi xóa thuộc các luồng riêng.
- **FR-007** · Người dùng có thể mở mục hàng chờ, chuyển trang, làm mới và thử lại bằng bàn phím. Mã người gửi có thể được đọc đầy đủ.

### Key Entities *(include if feature involves data)*

- **Yêu cầu xóa dữ liệu** · Một yêu cầu do người dùng gửi, nhận diện bằng mã yêu cầu và mã người gửi. Thời điểm gửi xác định thứ tự ưu tiên, trạng thái xác định việc xuất hiện trong hàng chờ.
- **Hàng chờ** · Tập yêu cầu đang chờ duyệt tại thời điểm đọc, có tổng số và các trang để quản trị viên duyệt danh sách.

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001** · Với 45 yêu cầu chờ duyệt và 3 yêu cầu ở trạng thái khác trong dữ liệu kiểm thử ổn định, tổng hiển thị là 45 và mỗi yêu cầu hợp lệ xuất hiện đúng một lần khi duyệt hết các trang.
- **SC-002** · Ít nhất 4 trong 5 người kiểm thử vai trò quản trị viên tìm được hàng chờ và xác định đúng mã yêu cầu chờ lâu nhất trong 30 giây kể từ dashboard, ngay ở lần thử đầu.
- **SC-003** · Trong mọi ca chưa đăng nhập, hết phiên không khôi phục được, sai vai trò và thu hồi quyền, màn hình hiển thị 0 dòng và không hiển thị tổng số khi quyền đọc bị từ chối.
- **SC-004** · Trong kiểm thử đầu cuối, 100% yêu cầu xóa đã ghi nhận và còn chờ duyệt xuất hiện khi tải hoặc làm mới tại mốc 60 giây kể từ lúc ghi nhận. Phép thử này phụ thuộc luồng gửi yêu cầu sẵn sàng.

## Assumptions

- Dùng vai trò Admin hiện hành cho tác nhân quản trị viên phụ trách tuân thủ. Hàng chờ dùng dữ liệu đọc do task 5.06 cung cấp.
- Dùng mặc định 20 mục mỗi trang và làm mới theo thao tác người dùng. Mốc 60 giây là thời gian để dữ liệu khả dụng khi đọc, theo QA.01.
- Xác nhận mốc 60 giây từ lúc ghi nhận cần môi trường chạy được cả luồng gửi yêu cầu và đọc hàng chờ. Các hành vi giao diện còn lại có thể kiểm thử với dữ liệu chuẩn bị sẵn.

