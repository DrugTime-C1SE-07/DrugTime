# 5.13 · Bàn giao PR

Ngày 2026-11-10. Cả sáu artifact đã approved. Người dùng tự review/merge; agent chỉ commit, push và mở PR, không merge hoặc bật auto-merge.

| Repo | Commit đã push | PR |
|---|---|---|
| api_contract | 7aa4d087e253985e01c75f6d3ead4205f07aae41 | https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/22 |
| backend | d24e32814550f18ad5e9c5939d666f3fe7962988 | https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/52 |
| docs | 24bd762cb308d40779eff4dfe6053d20ddbbd6b4 | https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/35 |

- Nhánh task ở cả bốn repo: feat/list-linked-patients. Superproject tạo nhánh task từ trạng thái hiện có; diff cây so với origin/main sau fetch không có thay đổi nền ngoài task trước khi cập nhật pointer/artifact.
- Fetch xác nhận các commit profile-phone kế thừa đã thuộc origin/main; PR task không kèm lại diff đó.
- Thứ tự merge: contract → backend → docs → superproject. Nếu squash/rebase làm SHA thay đổi, cập nhật pointer trong PR superproject tới SHA đã merge trước khi merge PR này.
- Không stage frontend/tests hoặc ba Firebase baseline. Chỉ bump backend, api_contract, docs tới commit đã push. work/5.13/scratch không được commit.
- Đã kiểm artifact/evidence trước khi stage: không có mẫu JWT/GitHub token khớp trong 62 file ngoài scratch. Không lưu credential của Git/CLI vào artifact.
- Git diff --check của code/contract đạt. Khi stage evidence, Git báo trailing whitespace ở output pytest và context dòng trống trong bản diff; giữ nguyên bằng chứng, không sửa nội dung log để che cảnh báo. Không phải thay đổi whitespace trong code sản phẩm.
- Số liệu kiểm thử và hạn chế baseline giữ nguyên 04/05/06; không chạy lại pytest trong bước xuất bản PR. Cần một người khác review PR theo DoD.

## Bước tiếp theo

Người dùng review và tự merge theo thứ tự trên. PR superproject chứa các artifact đã duyệt, evidence và workbook task để tiếp tục trên máy khác. Không tự chỉnh các artifact approved sau khi xuất bản.
