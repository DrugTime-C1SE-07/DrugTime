# Task report — 3.23-adherence-family-consent

**Task:** Backend `GET /adherence?patient_id=` scoped by consent  
**Cập nhật:** 2026-10-22  
**Trạng thái:** Các artifact requirement, contract, plan, implement, test và review đều đã được duyệt. Đã commit và push contract, backend, workbook cùng artifact/con trỏ superproject trên các nhánh task. Chưa tạo PR; issue đang tạm bỏ qua theo yêu cầu.

## Tóm tắt

Task bổ sung mô tả API và kiểm soát quyền đọc lịch sử tuân thủ qua PEP hiện có. Patient/family chỉ đọc được khi consent và liên kết còn hiệu lực; mỗi request đọc quyền mới từ DB, ghi audit fail-closed, và phản hồi không cache. Test case Excel có **23/23 Pass**.

Review kết luận **Đạt, kèm lưu ý**: không còn phát hiện Critical/High trong diff task; còn hai vấn đề mức Medium liên quan xác minh test và phạm vi Git trước khi phát hành. Kết luận này không có nghĩa là toàn repo đã xanh hoặc task đã đạt Definition of Done: còn cần PR được người khác approve.

## Đã hoàn thành

- Hoàn tất và duyệt sáu artifact giai đoạn: requirement, contract, plan, implement, test, review.
- Cập nhật contract `GET /adherence`, tham số `patient_id`, schema/response, quy tắc consent, audit và `Cache-Control: no-store`.
- Sửa PEP để từ chối admin truy cập dữ liệu sức khỏe qua self/family; giữ kiểm tra patient tồn tại và audit denied.
- Thêm migration `20261021115000_access_logs_admin_self_denied.sql` để cho phép audit **admin-self bị từ chối** mà vẫn giữ ràng buộc identity, quyền DB, trigger append-only và audit cũ.
- Bổ sung unit/integration regression cho admin-self/admin-linked, ma trận actor-role-result, denied audit và ngăn UPDATE/DELETE/TRUNCATE access log.
- Cập nhật workbook testcase: **23 Pass, 0 Fail, 0 Pending**; kiểm tra sheet khác được bảo toàn.
- Chạy kiểm tra DB riêng trên localhost; không dùng DB Supabase hosted. `.agents` được giữ nguyên.

## Bug sản phẩm đã tìm thấy và sửa

**BUG-ADHERENCE-14 — mức High trước khi sửa; hiện đã xử lý và regression pass.** PEP có thể cho admin đi qua nhánh self/family dù admin không được phép đọc dữ liệu sức khỏe. Khi từ chối admin-self, ràng buộc `access_logs_actor_identity_check` cũ lại chặn ghi audit denied, khiến API trả **500 thay vì 403**. Đây là lỗi phân quyền/audit ở endpoint dữ liệu sức khỏe; nếu nhánh cho phép được khai thác, có nguy cơ truy cập sai phạm vi dữ liệu.

**Giải pháp đã triển khai:** từ chối admin tại quy tắc access chung; migration chỉ mở ngoại lệ cho bản ghi `actor_role=admin`, actor trùng patient và `result=denied`. Test API xác nhận admin-self/admin-linked trả 403 và có denied audit; matrix 16 trường hợp và 9 ca thử mutation audit pass. Migration phải được áp dụng trước phiên bản app có thay đổi này.

## Vấn đề còn tồn tại

### 1. Full integration còn 2 test fail — mức Medium về độ tin cậy phát hành

Kết quả trên DB task mới nhất: **803 passed, 2 failed, 159 skipped, 1 xpassed** (`evidence/test-integration-after-migration.log`). Hai fail được ghi nhận ngoài các file sản phẩm của task; chưa xác minh trên baseline sạch nên chưa thể kết luận chúng có sẵn hay là regression.

| Test fail | Thực tế | Ảnh hưởng có thể có | Cách xử lý |
|---|---|---|---|
| `test_post_doses_batch_creates_dose_log_for_authenticated_patient__AC1_AC10_AC18` | Kỳ vọng `scheduled_at=01:00:00Z`, nhận `01:00:59.999000Z` | Kết quả API hoặc kỳ vọng về mốc thời gian của liều không thống nhất; có thể ảnh hưởng hiển thị/đối chiếu giờ uống | Chạy lại riêng trên baseline sạch và task branch với cùng DB/timezone. Xác định quy ước chính xác về giây/microsecond; sau đó sửa phép tính hoặc expectation theo contract, không bỏ assertion. |
| `test_profile_get_put_incomplete_complete__AC01_AC04` | Response có thêm trường `email` so với dict kỳ vọng | Client/test so sánh response có thể lệch schema; chưa có bằng chứng lỗi dữ liệu hoặc bảo mật | So sánh OpenAPI/runtime và hành vi trên baseline. Nếu `email` thuộc contract thì cập nhật expectation; nếu không thì sửa schema/response để loại trường thừa. |

### 2. Unit + architecture còn 34 test fail — mức Medium về độ tin cậy phát hành

Lần chạy cuối: **1183 passed, 34 failed, 8 warnings** (`evidence/implement-final-backend-amended.log`). Fail tập trung ở kiểm tra contract family/medication/notification/profile/OpenAPI và `test_missed_dose_window` dùng fake UOW không tương thích. Không có fail trong test admin-self, contract adherence hoặc architecture; tuy vậy chưa chứng minh 34 fail này tồn tại trên baseline sạch.

**Ảnh hưởng:** CI/gate toàn repo có thể không xanh, khó phát hiện regression của task giữa các lỗi nền.  
**Cách xử lý:** chạy đúng bộ unit + architecture trên baseline sạch và task branch trong cùng môi trường. Phân loại từng sai lệch; đồng bộ contract/runtime hoặc sửa fake UOW/test theo hành vi được chốt. Không skip/nới test chỉ để làm xanh.

### 3. Có 159 integration test bị skip và một xpass

159 skip đều do thiếu Supabase CLI (`Cannot read supabase status`), chủ yếu ở các ca Auth/mobile login. Một ca `test_post_doses_batch_requires_authentication__AC9` xpass do đã đánh dấu xfail trong repo.  
**Mức:** Medium về độ bao phủ xác minh; chưa phải bug sản phẩm được xác nhận.  
**Ảnh hưởng:** chưa xác minh được các kịch bản yêu cầu Supabase Auth.  
**Cách xử lý:** chạy Supabase local/CLI, reset DB thử nghiệm riêng, chạy các ca Auth bị skip; xem xét cập nhật marker xfail sau khi xác nhận nguyên nhân và chính sách test.

### 4. Scope và phạm vi nhánh trước PR — mức Medium về quy trình phát hành

`scope.py --stage implement` trong review exit 1 với ba đường dẫn ngoài phạm vi: hai integration test thuộc stage test đã duyệt và một tài liệu quyết định kế thừa ở nhánh docs. Trước đó scope test cũng báo các file từ stage đã duyệt. Một PR tạo từ toàn bộ nhánh docs có thể kéo theo thay đổi tài liệu/workbook alert không thuộc task. Đây là giới hạn scope/nhánh, không phải lỗi endpoint.

**Cách xử lý:** trước khi mở PR, xác định baseline và commit nguồn của các thay đổi kế thừa; chuẩn bị nhánh/checkout chỉ chứa nội dung task theo quy trình Git, giữ lại bằng chứng scope. Không sửa `.agents`, không rewrite/reset lịch sử để che kết quả. Chỉ bump submodule khi commit đích đã được push và xác nhận trên remote.

## Bằng chứng chính

- `evidence/test-migration.log`: 85 test task liên quan pass.
- `evidence/test-openapi-after-migration.log`: 2 test OpenAPI pass.
- `evidence/test-db-reset-after-migration.log`: dựng DB riêng qua chuỗi migration pass.
- `evidence/test-integration-after-migration.log`: full integration 803 pass / 2 fail / 159 skip / 1 xpass.
- `evidence/implement-final-backend-amended.log`: unit + architecture 1183 pass / 34 fail.
- `evidence/review-scope.log`: scope review còn 3 file ngoài phạm vi.
- `evidence/review-self-selector.log`: selector explicit/omitted trả cùng kết quả, audit allowed.

## Việc cần làm tiếp

1. Xác định baseline sạch cho hai integration fail và 34 unit fail; giải quyết hoặc ghi nhận rõ các lỗi nền trước khi dùng CI làm cổng phát hành.
2. Chạy lại các ca Auth đang skip trong môi trường Supabase local phù hợp.
3. Cô lập đúng thay đổi task khỏi phần kế thừa trước khi tạo PR.
4. Tạo/commit/push PR theo yêu cầu của người dùng; migration chạy trước app; cần ít nhất một reviewer khác approve để đạt Definition of Done.

**Commit đã push:** api_contract `382fb13`, backend `e37deaf`, docs `ee39931`, superproject artifact `b925012` và con trỏ `0f629e5`. Chưa tạo PR/issue, deploy migration hoặc xác minh production.  
**Rủi ro cần nhớ:** 2 integration fail và 34 unit fail chưa được đối chiếu baseline sạch; không thể khẳng định tất cả đều là lỗi có sẵn.


