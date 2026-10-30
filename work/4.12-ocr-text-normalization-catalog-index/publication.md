# Task 4.12 · Publication 2026-10-30

- Backend: https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/44 — draft, main base. Code commit 7e13010; merge origin/main a5c7aa45e1cbe0a277795cd416db83f06ce671c2. Merge giữ nguyên 13 file diff của task và bổ sung thay đổi nền hiện hành.
- Docs: https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/27 — draft, base feat/4.16-selection-confirmation-screen. Commit fd7bb4a40876cb6df022c79d39a94faaca99a532. Phụ thuộc PR cha https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/24; cần hợp nhất workbook với main sau khi PR cha merge.
- Superproject chỉ lưu artifact/evidence task và bump backend/docs tới SHA đã push. Gitlink api_contract/frontend/tests khác từ trước không được stage. Scratch không được commit.

## Kiểm chứng trong lượt publication

- Gate trước publication: 01/03/04/05/06 approved hợp lệ, không còn giai đoạn cần làm. Không sửa các artifact approved.
- Trước merge main: 249 hash backend bằng snapshot trước test; kiểm pattern bí mật trong 243 file publication không có finding. Log evidence/publication-preflight.log. Đây là kiểm pattern, không phải chứng nhận mọi loại bí mật đều được phát hiện.
- Sau merge backend main: 215 unit/architecture pass, 74 integration catalog pass, 0 skip; hai warning Starlette deprecation có sẵn. Log/XML: evidence/publication-unit.log/.xml, evidence/publication-integration.log/.xml.
- Không chạy lại full suite, baseline, lint toàn repo hoặc reset DB trong publication. Các kết quả full suite trong 05 thuộc snapshot trước merge main, không dùng để tuyên bố trạng thái toàn backend hiện tại.
- `git diff --cached --check` backend sạch; workbook commit đúng file đã test, không dựng lại.

## Bước tiếp theo

- PR để draft: dù metadata 06 approved và gate hợp lệ, nội dung 06 vẫn review phiên bản cũ 14 AC/39 ca/full-catalog builder. Bản hiện tại là 23 AC/50 ca/DB retrieval với migration alias GIN. Không diễn giải approval như bằng chứng đã review diff hiện tại.
- Reviewer cần xem diff hiện tại và evidence mới trước khi ready/merge; nếu sửa 06 đã approved, người duyệt phải reopen review theo quy trình trước. Publication không tự sửa hoặc approve 06.
- Docs phụ thuộc PR24; sau merge cha, kiểm base main và giữ cập nhật workbook 4.09/4.16 cùng 4.12. Không merge superproject với gitlink docs nhánh hiện tại vì chưa chứa mọi cập nhật docs/main.
- Merge backend và docs trước, superproject sau. Sau squash/rebase, cập nhật gitlink tới SHA đã merge thực tế trước merge PR superproject.
`git diff --cached --check` superproject exit1 do whitespace/newline trong log/XML evidence nguyên bản. Giữ output thô; không sửa bằng chứng để làm sạch whitespace. File sản phẩm backend đã check sạch.
