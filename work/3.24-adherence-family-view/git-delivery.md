# Bàn giao Git · 3.24-adherence-family-view

- Ngày: 2026-10-22. Người dùng yêu cầu commit và push sau khi mọi artifact 01/03/04/05/06 đã approved.
- Nhánh chung: `feat/3.24-adherence-family-view`.
- Frontend: `923a063697d35adf0882ed4dd0a3fc08bcda7ebb` — `feat(adherence): add read-only family adherence view`; đã push origin, `branch -r --contains HEAD` xác nhận nhánh remote chứa commit.
- Docs: `9aaea08232aa55534cd3d3e3bfca282d22254a5e` — `docs(qa): preserve master test cases and add family adherence coverage`; đã push origin, cùng kiểm tra remote đạt.
- Superproject: cập nhật đúng con trỏ frontend/docs tới hai SHA đã push cùng file bàn giao này, rồi push nhánh task chứa toàn bộ artifact work. Không bump backend/api_contract vì các checkout lệch sẵn có không thuộc thay đổi task 3.24.
- Không đổi nội dung artifact đã approved, không commit scratch, không thêm credential hoặc file môi trường. Không chạy lại test vì không đổi nội dung code/workbook trong bước commit/push; kết quả và giới hạn theo 05/06 đã duyệt.
- Còn mở: R2/BUG-FAMADH-21 Medium; hai ca manual Pending; full backend suite có giới hạn schema Supabase Auth trên DB test riêng. Không coi commit/push là đạt DoD hoặc đã merge.
- Chưa tạo PR hoặc merge; người dùng mới yêu cầu commit/push. Mô tả PR dự kiến ở `06-review.md`.
