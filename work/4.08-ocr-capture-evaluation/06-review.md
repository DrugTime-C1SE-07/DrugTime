---
task: 4.08-ocr-capture-evaluation
stage: review
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 17:00 +0700
content_hash: sha256:eb22263b24f68187
inputs:
  01-requirement.md: sha256:2c4a08a77f82f9e0
  03-plan.md: sha256:981facafd3a1d985
  04-impl-notes.md: sha256:544eece4a736ff20
  05-test-report.md: sha256:38974180712acae4
---

# 4.08 · Review bộ ảnh bao bì có nhãn v1

## 1. Kết luận

**Đạt, kèm lưu ý** theo phạm vi bộ ảnh mẫu hiện hành và báo cáo test đã được Bao Nguyen duyệt ngày 2026-10-29 16:53 +0700. Không phát hiện Critical/High/Medium trong phần đã review; có 1 lưu ý Low về cách diễn đạt README dùng chung với 4.09.

Đủ chuẩn bị bàn giao bộ dữ liệu cục bộ. Chưa publish/clone từ remote, chưa có PR được người khác approve; không tuyên bố hoàn thành Definition of Done hoặc xác minh nhãn độc lập. Không yêu cầu người dùng kiểm lại toàn bộ 49 ảnh để chốt hồ sơ này.

## 2. Phạm vi đã review

| Phần | Cách đối chiếu |
|---|---|
| Yêu cầu/phạm vi | 01-requirement.md AC1–AC6; 03-plan.md P1–P6; chỉ dẫn mới được ghi và duyệt trong 05-test-report.md |
| Superproject | datasets đang untracked; đọc file thực, không coi git diff rỗng là không có thay đổi |
| Dữ liệu | 49 hàng workbook, 49 path/ảnh, annotations, manifest và README; tái tính hash và thống kê |
| Công cụ dùng chung | Đọc cả 6 file datasets/scripts và cơ chế reader/path/hash; chi tiết review tại 4.09 |
| Docs | Workbook tổng được chỉ định; kiểm read-only ID/status với spec riêng của hai task |

Scope implement trong review: exit 1, **“CHẶN: 226 file ngoài phạm vi”**, `evidence/review-scope.log`. 4 file plan của 4.08 đều được nhận [OK]. Phần ngoài gồm baseline dữ liệu/ảnh/raw/công cụ và output 4.09, file tổng docs, .gitignore/api_contract đã được yêu cầu giữ. Không có chỉnh sửa sản phẩm trong lượt review; không báo toàn repo sạch hoặc xóa baseline để làm xanh.

Gate review OK: `evidence/review-gate.log`. Review này trong cùng hội thoại với implement, không phải chữ ký reviewer PR độc lập.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1: 49 ID/ảnh/hàng khớp. AC2/3: nhãn/strength có nhật ký review trực quan AI, không suy thương hiệu từ hoạt chất; không nhận là human sign-off. AC4: snapshot/annotations hashes khớp, 28 hộp/21 vỉ, 23 tên. AC5: metadata unknown và người rà ghi trung thực. AC6: README/file cục bộ sẵn; publish/clone thuộc bàn giao sau yêu cầu Git |
| Phạm vi | Chỉ dữ liệu mẫu và hồ sơ; không engine Tesseract, không bổ sung quota ảnh/kiểm Android. Cách chấp nhận giới hạn theo 05 approved, không sửa 01/03 approved |
| Contract | Không đổi API/payload HTTP |
| Bất biến kiến trúc | Không API/DB/patient/consent/dose/interaction/schema mới; không có bất biến backend bị tác động |
| Bảo mật | Không thấy credential trong file code/metadata đã đọc; ảnh là bao bì thuốc, kế thừa review ảnh có ghi nguồn AI. Chưa có kiểm ảnh độc lập mới, không giả rằng đã có |
| Xử lý lỗi | Reader báo ID trùng, path sai/thoát root, nhãn/ảnh thiếu, formula/JSON lỗi; không mất hàng âm thầm |
| Hiệu năng | Bộ 49 ảnh phù hợp công cụ cục bộ; không tải qua backend hoặc tác động runtime sản phẩm |
| Chất lượng test | validate spec thành công; 8 ca: 6 Pass/0 Fail/2 Pending. Pending giữ trung thực như giới hạn/việc bàn giao, không biến thành yêu cầu mở rộng |
| Dễ đọc/nhất quán | ID/path giữ ổn định; README còn lời nhắc manual cũ, Low L01 |
| Đối chiếu 04/05 với log | Kiểm lại hash/count/labels/report; 41 unit và 5 host trong evidence trước khớp log, không nhận là chạy test mới. Testbook/spec/master khớp |

Bằng chứng đối chiếu hiện tại: `../4.09-mlkit-prototype/evidence/review-v1-crosscheck.log`. Kiểm hash byte workbook/49 ảnh/annotations, manifest canonical hash, đủ một ảnh một dòng; không làm một lượt visual sign-off mới. `evidence/review-testcase-validation.log`: validate exit 0. Sheet Packaging Dataset trong file riêng/tổng khớp 8 ID và trạng thái.

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Low · L01 (dùng chung với 4.09) | datasets/README.md:11; datasets/README.md:17 | README còn diễn đạt “Còn cần người khác rà độc lập ... native/manual” và “chưa ... kết luận go/no-go”, dễ bị hiểu thành điều kiện chặn chốt hồ sơ hoặc chưa có quyết định hướng. 05 approved mới đã chấp nhận giới hạn prototype và có engineering GO riêng | Khi cập nhật tài liệu bàn giao, phân biệt việc chưa kiểm với điều kiện đóng scope; ghi đã GO kỹ thuật, chưa có benchmark frozen. Hiện lấy 05 approved làm nguồn trạng thái quy trình. Không chặn nhận bộ ảnh mẫu |

Không có Critical/High cần reopen implement. Không sửa README hoặc artifact approved ở giai đoạn review.

## 5. Mô tả PR

Đề xuất **một PR superproject cho bộ datasets dùng chung 4.08/4.09**, do hai task cùng nhánh `feat/datasets-ocr` và cùng README/snapshot. Nội dung đã soạn ở `../4.09-mlkit-prototype/pr-description-superproject.md`. Không stage .gitignore, api_contract hoặc các con trỏ baseline không liên quan.

Phần 4.08: thêm bộ 49 ảnh và labels, annotations, manifest v1; nêu review AI/nguồn unknown, source hash và hướng dẫn dùng lại. AC1–AC5 có evidence cục bộ; AC6 kiểm publish/clone ở bước Git được yêu cầu. Mô tả PR docs cho workbook chung: `../4.09-mlkit-prototype/pr-description-docs.md`. Không có PR backend/contract hoặc frontend riêng do 4.08 thay đổi.

Thứ tự khi được yêu cầu mở PR: frontend prototype nếu chưa merge → docs testcase → superproject datasets/con trỏ hợp lệ. Sau squash phải dùng SHA đã merge, không bump commit chưa push. Lượt này chưa commit/push/mở PR.

## 6. Ghi chú cho quy trình

- Trước đó agent đã mở rộng kiểm độc lập/manual thành việc bắt người dùng làm thêm cho task mẫu. 05 approved ghi chỉ dẫn thu hẹp; review không đặt lại các điều kiện đó.
- Bộ dữ liệu untracked cần đọc file thật; scope toàn repo bao gồm baseline và task liên quan nên phải ghi nguyên kết quả thay vì nhận “sạch”.
- Không sửa approval metadata hay tự nhận đã có reviewer PR độc lập.

## Bước tiếp theo

- Chờ người duyệt đọc kết luận/Low/giới hạn và chạy `python .agents/scripts/gate.py approve 4.08-ocr-capture-evaluation review`.
- Sau duyệt, sẵn sàng commit/push/mở PR khi người dùng yêu cầu; bước publish mới xác nhận nhóm clone/pull được. Không yêu cầu quét lại ảnh hoặc bộ manual mở rộng.
- Cập nhật: 2026-10-29, Codex.
