---
task: 3.24-adherence-family-view
stage: review
status: draft
---

# 3.24-adherence-family-view · Review

## 1. Kết luận

**Đạt, kèm lưu ý: 0 Critical, 0 High mở, 1 Medium mở (R2).** R1 High về mất sheet đã được khắc phục và kiểm lại trong lượt review này. Hai ca manual vẫn Pending và full backend suite có giới hạn môi trường Auth như báo cáo test đã được duyệt; không coi các phần đó là Pass. Không sửa code hoặc workbook trong review.

Lượt review lại sau khi 05 được duyệt: chạy script bảo toàn workbook từ baseline docs/origin/main tại `dfd422fa9211d4a2c40b740cb772b694779ada0f` (đã kiểm ref hiện tại vẫn đúng SHA này), validate spec, kiểm Bug Report và scope. Bằng chứng mới: `evidence/review-r1-preservation.log`, `review-r1-testcases.log`, `review-r1-workbook-status.log`, `review-r1-scope.log`.

## 2. Phạm vi đã review

| Vùng | Cách đọc |
|---|---|
| frontend | `git diff origin/main...HEAD` không có diff commit vì code task còn chưa commit. Đã đọc toàn bộ working diff của app.dart/router.dart/main.dart và toàn bộ 14 file mới trong feature adherence/test bằng nội dung file; không coi diff commit rỗng là không có thay đổi. |
| docs | `git diff --stat origin/main`, so workbook tổng với blob `origin/main:Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, kiểm từng sheet chức năng của task khớp workbook riêng. |
| work | Đọc AC1–AC10, bảng phạm vi plan, testcases.json, đối chiếu 04/05 và log pass/fail/skip; kiểm metadata approval do người dùng tạo. |

`scope.py --stage implement` **OK**, gồm workbook theo vai trò testcase-book và 17 file frontend. Log mới `evidence/review-r1-scope.log`. Scope kiểm đường dẫn; kiểm bảo toàn nội dung workbook được chạy riêng để đóng R1. Không chạy lại toàn bộ Flutter/backend trong lượt review lại vì thay đổi từ lượt review trước chỉ là workbook và artifact; kết quả phần mềm dẫn dưới đây thuộc các log đã chạy ở các giai đoạn trước.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | Route nhận patientId, UI chỉ đọc, bốn trạng thái, tỷ lệ/null đúng nhãn; clear/generation/refetch phù hợp AC1–AC7. AC8 có lỗi qua ngày ở biên cũ nhất (R2). AC9/AC10 còn phần manual Pending đã nêu trong báo cáo được duyệt. |
| Phạm vi | File code và workbook đúng đường dẫn cho phép; đã khôi phục các sheet ngoài task bị mất (R1 đóng). Không sửa backend/contract/schema. |
| Contract | GET /adherence patient_id/from/to/group_by=date, bearer mới mỗi request; field IDs integer và trạng thái/offset khớp contract. Mapper từ chối sai patient/response cơ bản; 401/403/422/network/5xx được phân loại. |
| Bất biến kiến trúc | Client chỉ gọi Backend API; không truy cập Supabase/cache quyền. Đối chiếu PEP/audit backend hiện hữu và log 60 ca. Không đổi idempotency/interaction/schema. |
| Bảo mật | Không thấy credential thật hoặc log response sức khỏe trong phần code mới; dữ liệu chỉ giữ ở controller màn, clear khi refetch/403/đổi patient/dispose, response cũ bị loại. Backend PEP vẫn quyết định quyền. |
| Xử lý lỗi | Có loading/empty/denied/expired/range/network/retry; lỗi rollover có cách tránh bằng chọn ngày hợp lệ khác (R2). |
| Hiệu năng | Query giới hạn tháng và cửa sổ 90 ngày; không thêm DB query/N+1. |
| Chất lượng test | Có HTTP/auth/error, 200→403, A→B, null/status/offset, accessibility 48dp và biên ngày. Đã thêm ca TC-FAMADH-21 đánh Fail Medium cho R2, không che lỗi. Hai ca manual vẫn Pending. |
| Dễ đọc/nhất quán | Dùng theme token và cấu trúc domain/data/presentation; không thêm package. Scroll ngang chỉ trong lịch khi thiếu chiều rộng. |
| Đối chiếu 04/05 | Lần test mix có 633 pass + 1 lỗi fixture tooltip; hai ca fixture đã sửa và pass riêng, đúng báo cáo. Backend adherence 60 pass/17.36s; full suite -x 102 pass + 1 lỗi môi trường auth.users, không được gọi là full pass. |
| Workbook | Validate spec đạt: 21 ca, 18 Pass, 1 Fail Medium, 2 Pending; BUG-FAMADH-21 có trong Report. Workbook đủ 19 sheet, toàn bộ dữ liệu/công thức/vùng gộp 15 sheet baseline được giữ; ALERT và ADHERENCE giữ nguyên ô so với trước khôi phục; FAMADH khớp workbook riêng. Log `review-r1-preservation.log`, `review-r1-workbook-status.log`. |

## 4. Phát hiện

| ID / Mức | Vị trí | Vấn đề và bằng chứng | Đề xuất |
|---|---|---|---|
| R1 — High, **đã đóng** | `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, danh sách worksheet | Lượt trước mất 15 sheet baseline, log `review-master-baseline.log`. Đã khôi phục từ main và ghép 3 sheet task bằng bộ ghi của repo. Review lại xác nhận đủ 19 sheet; mọi ô có dữ liệu/công thức và vùng gộp 15 sheet main khớp baseline; ALERT/ADHERENCE cũng giữ nguyên dữ liệu cũ. Bằng chứng `review-r1-preservation.log`, `review-r1-workbook-status.log`. | Giữ kiểm tra baseline trong quy trình merge workbook; không dùng riêng workbook của nhánh tiền nhiệm làm mốc bảo toàn. |
| R2 — Medium | `frontend/mobile/lib/features/adherence/presentation/state/adherence_controller.dart:35` và `:103` | `today/earliestDate` động nhưng selectedDate giữ nguyên qua refresh. Đặt now=28/10/2026, chọn 31/07/2026 (today−89); chuyển now sang 29/10 rồi refresh: request from=01/08, to=31/07. Backend sẽ trả 422; ngày đang chọn cũng không còn thuộc cửa sổ. Tái hiện bằng `evidence/review-date-rollover-repro.dart`, chạy Flutter test **1 pass** xác nhận có range đảo, log `review-date-rollover.log`. Đây là test tái hiện lỗi, không phải chứng minh sản phẩm đúng. Có cách tránh: chọn ngày hợp lệ khác hoặc mở lại màn, nên Medium theo thang dự án. | Khi load/resume, chuẩn hóa selectedDate vào cửa sổ hiện tại trước khi tính from/to; thêm ca đồng hồ qua ngày ở biên cuối tháng cũ nhất. Nếu sửa code, cần reopen implement. |

Không thay đổi nội dung 05 đã approved hoặc workbook/testcases.json ở review. R1 đã được sửa ở test và được kiểm lại; R2 còn mở với workaround nên Medium theo thang dự án. Không nâng trạng thái hai manual Pending thành Pass.

## 5. Mô tả PR

### Frontend

Tiêu đề: `feat(adherence): add read-only family adherence view`

Thêm route `/family/adherence` nhận `FamilyAdherenceRouteArgs(patientId, patientName?)`, đọc GET /adherence qua ApiClient. Hiển thị summary gồm uống trễ, lịch tuần/tháng và bốn trạng thái chỉ đọc. Xóa dữ liệu trước refetch/403/đổi bệnh nhân, loại response cũ. Dùng theme app và giữ vùng chạm 48dp bằng lịch cuộn ngang khi màn hẹp; không thêm dependency.

Kiểm chứng: 632 test sản phẩm Flutter pass trong lần chạy có thêm script biên; script biên ban đầu lỗi fixture đã sửa và 2 ca pass riêng. Backend adherence hiện hữu 60 ca pass trên DB riêng. Xem log trong work/3.24-adherence-family-view của PR superproject. Manual: mở route với patientId được phép, kiểm bốn trạng thái và tỷ lệ/null, vuốt lịch 320dp, resume sau thu hồi quyền, TalkBack/VoiceOver và đối chiếu Figma S09a/S09b. Hai manual cuối vẫn Pending, không ghi là đã chạy.

Rủi ro công khai: BUG-FAMADH-21/R2 Medium còn mở; để ngày cũ nhất qua nửa đêm có thể tạo from>to, tạm chọn ngày hợp lệ khác hoặc mở lại màn. Task 5.13 mới nối danh sách/chọn bệnh nhân. Liên kết PR docs và superproject sẽ điền bằng URL thật khi người dùng cho phép tạo PR.

### Docs

Tiêu đề: `docs(qa): preserve master test cases and add family adherence coverage`

Giữ 15 sheet baseline, ghép ALERT/ADHERENCE/FAMADH và tái tạo Report bằng script repo. Workbook cuối có 19 sheet; FAMADH 21 ca gồm 18 Pass, 1 Fail Medium, 2 Pending. Đã kiểm dữ liệu/công thức/vùng gộp baseline và kết quả hai sheet cũ; Bug Report giữ BUG-FAMADH-21. Không thay kết quả của các chức năng baseline. Liên kết PR frontend và superproject sẽ điền khi có URL thật.

### Superproject

Tiêu đề: `docs(task): record family adherence implementation and verification`

Lưu artifact requirement/plan/implement/test/review và evidence của task 3.24, gồm lịch sử sửa vùng chạm và bảo toàn workbook. Sau khi commit/push frontend và docs được yêu cầu, mới bump con trỏ tới SHA đã có trên remote; bổ sung URL thật và SHA vào mô tả PR. Hiện chỉ commit work, chưa bump frontend/docs.

Thứ tự dự kiến: frontend và docs hoàn tất PR/merge, rồi superproject bump tới commit đã merge trên remote. Không cần PR backend/contract cho task này. Mọi PR vẫn cần ít nhất một người khác approve và các điều kiện DoD. Chưa tạo PR, push hoặc merge trong review.

## 6. Ghi chú cho quy trình

- Đây là cùng agent/luồng đã implement, không thay thế reviewer PR độc lập. Đã đọc file thực tế, contract và chạy một ca tái hiện mới thay vì chỉ dựa vào báo cáo đã duyệt.
- Phép bảo toàn workbook phải so với nhánh đích PR và workbook ngay trước sửa; kiểm hai sheet của nhánh tiền nhiệm là chưa đủ khi main đã thêm chức năng khác. Lỗi này đã xảy ra trong chính phiên làm trước của agent.
- Các file mới frontend chưa commit nên phải đọc untracked files, không chỉ `git diff main...HEAD`.
- Hai Pending manual và giới hạn Supabase Auth đã có trong test report được duyệt; không nâng thành Pass hoặc coi DoD hoàn tất.

## Bước tiếp theo

- Đang chờ: người duyệt xem kết luận **Đạt, kèm lưu ý** và R2 Medium còn mở.
- Nếu đồng ý, chạy `python .agents/scripts/gate.py approve 3.24-adherence-family-view review` trong terminal người dùng. Agent không chạy lệnh duyệt. Nếu muốn sửa R2 trước khi tiếp tục, cần reopen implement theo gate.
- Sau approval, commit/push frontend và docs, mở PR và bump con trỏ chỉ khi người dùng yêu cầu. Chưa kết luận DoD hoàn tất: còn reviewer PR độc lập, lỗi Medium và hai manual Pending đã công khai.
- Cập nhật lần cuối: 2026-10-22, Codex.
