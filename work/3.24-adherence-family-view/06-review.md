---
task: 3.24-adherence-family-view
stage: review
status: draft
---

# 3.24-adherence-family-view · Review

## 1. Kết luận

**Chưa đạt: 1 High, 1 Medium; không phát hiện Critical.** Workbook tổng đang thiếu 15 sheet chức năng so với docs/origin/main. Chưa commit/push workbook nên có thể khôi phục từ Git. Không sửa code hoặc workbook trong review.

## 2. Phạm vi đã review

| Vùng | Cách đọc |
|---|---|
| frontend | `git diff origin/main...HEAD` không có diff commit vì code task còn chưa commit. Đã đọc toàn bộ working diff của app.dart/router.dart/main.dart và toàn bộ 14 file mới trong feature adherence/test bằng nội dung file; không coi diff commit rỗng là không có thay đổi. |
| docs | `git diff --stat origin/main`, so workbook tổng với blob `origin/main:Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, kiểm từng sheet chức năng của task khớp workbook riêng. |
| work | Đọc AC1–AC10, bảng phạm vi plan, testcases.json, đối chiếu 04/05 và log pass/fail/skip; kiểm metadata approval do người dùng tạo. |

`scope.py --stage implement` **OK**, gồm workbook theo vai trò testcase-book và 17 file frontend. Log `evidence/review-scope.log`. Scope kiểm đường dẫn, không phát hiện mất sheet trong file được phép.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | Route nhận patientId, UI chỉ đọc, bốn trạng thái, tỷ lệ/null đúng nhãn; clear/generation/refetch phù hợp AC1–AC7. AC8 có lỗi qua ngày ở biên cũ nhất (R2). AC9/AC10 còn phần manual Pending đã nêu trong báo cáo được duyệt. |
| Phạm vi | File code và workbook đúng đường dẫn cho phép; nội dung workbook mất sheet ngoài task (R1). Không sửa backend/contract/schema. |
| Contract | GET /adherence patient_id/from/to/group_by=date, bearer mới mỗi request; field IDs integer và trạng thái/offset khớp contract. Mapper từ chối sai patient/response cơ bản; 401/403/422/network/5xx được phân loại. |
| Bất biến kiến trúc | Client chỉ gọi Backend API; không truy cập Supabase/cache quyền. Đối chiếu PEP/audit backend hiện hữu và log 60 ca. Không đổi idempotency/interaction/schema. |
| Bảo mật | Không thấy credential thật hoặc log response sức khỏe trong phần code mới; dữ liệu chỉ giữ ở controller màn, clear khi refetch/403/đổi patient/dispose, response cũ bị loại. Backend PEP vẫn quyết định quyền. |
| Xử lý lỗi | Có loading/empty/denied/expired/range/network/retry; lỗi rollover có cách tránh bằng chọn ngày hợp lệ khác (R2). |
| Hiệu năng | Query giới hạn tháng và cửa sổ 90 ngày; không thêm DB query/N+1. |
| Chất lượng test | Có HTTP/auth/error, 200→403, A→B, null/status/offset, accessibility 48dp và biên ngày. Thiếu ca đồng hồ chuyển ngày dẫn tới R2. Hai ca manual vẫn Pending. |
| Dễ đọc/nhất quán | Dùng theme token và cấu trúc domain/data/presentation; không thêm package. Scroll ngang chỉ trong lịch khi thiếu chiều rộng. |
| Đối chiếu 04/05 | Lần test mix có 633 pass + 1 lỗi fixture tooltip; hai ca fixture đã sửa và pass riêng, đúng báo cáo. Backend adherence 60 pass/17.36s; full suite -x 102 pass + 1 lỗi môi trường auth.users, không được gọi là full pass. |
| Workbook | Validate spec đạt: 20 ca, 18 Pass, 0 Fail, 2 Pending. Sheet Family adherence view khớp file task, nhưng bản tổng thiếu 15 sheet main (R1). Log `review-testcases.log`, `review-workbook.log`, `review-master-baseline.log`. |

## 4. Phát hiện

| ID / Mức | Vị trí | Vấn đề và bằng chứng | Đề xuất |
|---|---|---|---|
| R1 — High | `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, danh sách worksheet | `origin/main` có 15 sheet chức năng + Report; file working chỉ còn Alert dispatch, Lịch sử tuân thủ, Family adherence view, Report. Mất toàn bộ 15 sheet chức năng main, gồm Đăng nhập người dùng, Lịch uống thuốc, Khung điều hướng app… Log `evidence/review-master-baseline.log` liệt kê đủ 15 tên. Bằng chứng preservation cũ chỉ so với workbook task 3.23 đã thiếu sheet, nên không chứng minh giữ baseline main. Nếu merge file hiện tại sẽ xóa test case của các chức năng khác. | Reopen **test**; lấy workbook baseline từ docs/origin/main, giữ/ghép các sheet task 3.23 cần bảo toàn rồi merge FAMADH bằng script. Kiểm sheet và giá trị ô của mọi sheet baseline trước/sau, không chỉ hai sheet từ workbook cũ. Không sửa hoặc xóa kết quả tester khác mà chưa xử lý xung đột. |
| R2 — Medium | `frontend/mobile/lib/features/adherence/presentation/state/adherence_controller.dart:35` và `:103` | `today/earliestDate` động nhưng selectedDate giữ nguyên qua refresh. Đặt now=28/10/2026, chọn 31/07/2026 (today−89); chuyển now sang 29/10 rồi refresh: request from=01/08, to=31/07. Backend sẽ trả 422; ngày đang chọn cũng không còn thuộc cửa sổ. Tái hiện bằng `evidence/review-date-rollover-repro.dart`, chạy Flutter test **1 pass** xác nhận có range đảo, log `review-date-rollover.log`. Đây là test tái hiện lỗi, không phải chứng minh sản phẩm đúng. Có cách tránh: chọn ngày hợp lệ khác hoặc mở lại màn, nên Medium theo thang dự án. | Khi load/resume, chuẩn hóa selectedDate vào cửa sổ hiện tại trước khi tính from/to; thêm ca đồng hồ qua ngày ở biên cuối tháng cũ nhất. Nếu sửa code, cần reopen implement. |

Không thay đổi nội dung 05 đã approved hoặc workbook/testcases.json ở review để che các phát hiện. Hai phát hiện mới được ghi tại đây; R1 phải xử lý trước khi kết luận đạt.

## 5. Mô tả PR

Chưa soạn mô tả để mở PR vì kết luận Chưa đạt. Chưa tạo PR, push, bump con trỏ hoặc commit frontend/docs. Sau khi khắc phục, cần PR client, workbook docs và superproject theo thứ tự submodule push trước rồi bump con trỏ; vẫn cần một người khác approve PR theo DoD.

## 6. Ghi chú cho quy trình

- Đây là cùng agent/luồng đã implement, không thay thế reviewer PR độc lập. Đã đọc file thực tế, contract và chạy một ca tái hiện mới thay vì chỉ dựa vào báo cáo đã duyệt.
- Phép bảo toàn workbook phải so với nhánh đích PR và workbook ngay trước sửa; kiểm hai sheet của nhánh tiền nhiệm là chưa đủ khi main đã thêm chức năng khác. Lỗi này đã xảy ra trong chính phiên làm trước của agent.
- Các file mới frontend chưa commit nên phải đọc untracked files, không chỉ `git diff main...HEAD`.
- Hai Pending manual và giới hạn Supabase Auth đã có trong test report được duyệt; không nâng thành Pass hoặc coi DoD hoàn tất.

## Bước tiếp theo

- Đang chờ: người dùng mở lại test để sửa R1. Chạy `python .agents/scripts/gate.py reopen 3.24-adherence-family-view test` trong terminal người dùng. Agent không chạy lệnh này.
- Sau khi workbook bảo toàn main và test được duyệt lại, review lại R1. R2 là lưu ý Medium; nếu muốn sửa trước merge thì mở lại implement theo gate, không sửa code trong review.
- Cập nhật lần cuối: 2026-10-22, Codex.
