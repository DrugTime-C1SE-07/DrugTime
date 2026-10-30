---
task: 4.08-ocr-capture-evaluation
stage: plan
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 16:27 +0700
content_hash: sha256:981facafd3a1d985
inputs:
  01-requirement.md: sha256:2c4a08a77f82f9e0
---

# 4.08 · Plan chốt bộ ảnh bao bì có nhãn dùng chung

## 1. Giải pháp

Theo requirement approved ngày 2026-10-29, task chỉ thu thập/gắn nhãn/xác minh/bàn giao dữ liệu, không nghiên cứu hoặc chạy engine OCR. Dùng bộ 49 ảnh hiện tại; chưa tự kết luận mọi ảnh/nhãn đủ chuẩn hoặc đại diện. Giữ ID task để truy lịch sử, không xóa ảnh/raw/công cụ thử cũ.

Ảnh gốc → đối chiếu người đọc → labels.xlsx và bảng xác minh/nguồn → kiểm cấu trúc → snapshot hash/thống kê → README bàn giao. Raw ML Kit chỉ là đầu ra của 4.09, không dùng làm đáp án. Không đổi tên file/ID khi chưa có lý do và ánh xạ; nếu tên folder sai nội dung, nhãn/bảng xác minh ghi đúng ảnh, không gán theo folder.

Đầu ra dùng chung:

- datasets/labels.xlsx: giữ format B2:E2; sửa nhãn chỉ khi ảnh chứng minh sai, không ghi công thức hoặc điền strength không nhìn thấy.
- datasets/annotations.v1.csv: mỗi ảnh có image_id, source_type, source_reference, condition, verified_by, verified_at, verification_status, notes. Nguồn hoặc điều kiện không rõ ghi unknown; người/ngày xác minh chỉ ghi khi đã thực sự kiểm. Phân biệt watermark nhìn thấy với URL nguồn gốc đã xác định.
- datasets/manifest.v1.json: version, ngày snapshot, workbook hash, danh sách ảnh/hash/nhãn, hash tổng, trạng thái xác minh từng ảnh, thống kê theo tên sản phẩm thật và hộp/vỉ. Group folder chỉ là nhóm lưu trữ, không coi các thương hiệu cùng hoạt chất là một sản phẩm.
- datasets/README.md: quy ước/phiên bản/cách tái hiện/thống kê/hạn chế và trạng thái đã đưa lên repo hay mới cục bộ.

Dùng lại datasets/scripts/ocr_dataset.py (load_labels/snapshot) chỉ đọc và Python standard library cho kiểm kê; không viết lại OCR hoặc công cụ chấm. Thao tác dữ liệu/kiểm tra thử ở work/.../scratch; không thêm dependency dự án. Nếu sửa XLSX áp dụng skill spreadsheets, giữ định dạng và mọi nhãn không có bằng chứng cần sửa; sao lưu trước sửa trong work.

## 2. Khảo sát và quyết định áp dụng

| Nguồn | Kết luận |
|---|---|
| 01-requirement.md approved 2026-10-29, AC1–AC6 | Bộ ảnh có nhãn dùng chung; không engine/góc tối ưu |
| Bảng Sprint mới và chỉ dẫn người dùng trong chat | Không dùng backlog repo cũ; không đợi matching hoàn tất |
| datasets/images, labels.xlsx, README.md | 49 ảnh/49 dòng; header B2:E2; phải đối chiếu nhãn và tên thực, không suy từ folder |
| datasets/scripts/ocr_dataset.py: load_labels, snapshot | Có reader/kiểm ID/path/hash phục vụ kiểm bộ dữ liệu; tái dùng chỉ đọc |
| pilot-002 summary/report | Đã có 49 raw ML Kit, không dùng làm đáp án nhãn |
| Proposal_v5 §6.2/6.3, FR01, §8.1/lộ trình; nguồn đối chiếu tại work/4.09-mlkit-prototype/evidence/plan-dataset-source.log | Bao bì/on-device/manual confirmation; không đơn thuốc/PHI |
| scope-correction.md và 04 cũ | Những bước nghiên cứu engine/góc cũ là lịch sử, không điều kiện hoàn thành task mới |

| Quy tắc/nguồn | AC | Bước | Test |
|---|---|---|---|
| Requirement: ID/path một ảnh một dòng, không thoát dataset | AC1 | P1, P3 | T1 |
| Tên/strength theo ảnh, không theo raw/folder/hoạt chất | AC2, AC3 | P2 | T2 |
| Nguồn/điều kiện thật, phiên bản/hash/nhóm dữ liệu | AC4 | P2–P4 | T3, T4 |
| Không PHI/secret hoặc đáp án tự đoán, unknown giữ rõ | AC5 | P2, P4 | T2, T3 |
| Bàn giao qua repo khi người dùng yêu cầu commit/push | AC6 | P5, P6 | T5 |

## 3. File sẽ thay đổi

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| superproject | datasets/labels.xlsx | sửa nếu có bằng chứng sai | Đáp án tên/strength đúng trên ảnh, giữ format |
| superproject | datasets/annotations.v1.csv | thêm | Nguồn/điều kiện/xác minh/thiếu dữ liệu |
| superproject | datasets/manifest.v1.json | thêm | Phiên bản/hash/thống kê/truy vết |
| superproject | datasets/README.md | sửa | Hướng dẫn và trạng thái bàn giao |

4 file dữ liệu/hướng dẫn, không sửa submodule. Ảnh/raw và scripts hiện có chỉ đọc. Task artifact/evidence ở work/4.08-ocr-capture-evaluation, bao gồm testcase sau này. Không sửa .gitignore, api_contract, frontend, công cụ nghiên cứu hoặc xóa lịch sử.

## 4. Checklist

- [ ] P1 [work] Kiểm baseline nhánh/dirty và SHA-256 ảnh/workbook, kiểm kê 49 ảnh/nhãn — AC: AC1 — xong khi: log số ảnh/hàng/ID/path/lỗi trước sửa, không ảnh nào mất.
- [ ] P2 [superproject] Đọc từng ảnh, kiểm tên/strength/nguồn/PHI và ghi annotations; sửa labels chỉ khi ảnh chứng minh sai — file: datasets/labels.xlsx, datasets/annotations.v1.csv — AC: AC2, AC3, AC5 — xong khi: T2/T3 có từng ID và lý do, unknown/pending không bị giả thành verified; không dùng raw chọn đáp án.
- [ ] P3 [work] Chạy reader/kiểm một-một, path, ID, nhãn thiếu và hash ảnh trước/sau — AC: AC1, AC4 — xong khi: T1 đủ ảnh/hàng; lỗi dữ liệu được sửa đúng scope hoặc ghi pending, không bỏ âm thầm.
- [ ] P4 [superproject] Tạo manifest phiên bản v1 và thống kê/hash, nêu quan hệ/ảnh nguồn trùng nếu phát hiện — file: datasets/manifest.v1.json — AC: AC4, AC5 — xong khi: T3/T4 đối chiếu byte thực và trạng thái xác minh; không chỉ so hash khai báo.
- [ ] P5 [superproject] Cập nhật README với số liệu, cách đọc labels/annotations/manifest và hạn chế/phạm vi — file: datasets/README.md — AC: AC4, AC6 — xong khi: người khác tái hiện kiểm bằng hướng dẫn, không phụ thuộc OCR cũ; không tuyên bố đã publish khi chưa push.
- [ ] P6 [work] Chốt impl-notes, evidence và danh sách file bàn giao; sau test/review chỉ commit/push khi người dùng yêu cầu — AC: AC1–AC6 — xong khi: có artifact kiểm chứng, trạng thái Git/publish thật; AC6 chưa kiểm clone/pull phải ghi pending, không tự đóng task.

Không tick plan đã duyệt khi làm; cập nhật tiến độ trong 04. P2 chưa thể gọi xong nếu vẫn còn ảnh chưa đọc/xác minh nhưng báo verified.

## 5. Test và bằng chứng

| Test dự kiến | AC | Nơi và cách kiểm |
|---|---|---|
| T1 kiểm số ảnh/hàng/ID trùng/path tồn tại/escape | AC1 | Reader datasets/scripts/ocr_dataset.py và kiểm kê độc lập ở work/scratch; output thô evidence/implement-dataset-integrity.log |
| T2 đối chiếu từng ảnh→name/strength, giữ thiếu/không rõ | AC2, AC3, AC5 | Manual visual theo image_id; annotations và evidence/implement-label-review.log; không đọc raw làm đáp án |
| T3 đối chiếu nguồn/điều kiện/PHI và trạng thái verified | AC4, AC5 | Manual review annotations; unknown rõ, không suy metadata từ ảnh web |
| T4 thay đổi thử byte/nhãn trong bản sao kiểm snapshot/hash, đối chiếu thống kê | AC4 | Kiểm độc lập scratch/temp, không sửa ảnh gốc; evidence/implement-snapshot-check.log |
| T5 tái hiện README và sau publish clone/pull lấy đủ bộ | AC6 | Thực hiện trong test/bàn giao khi đã được yêu cầu commit/push; chưa có remote commit thì Pending |

Không có API/DB/service-integration, không reset DB hoặc viết test máy móc cho việc sửa nhãn. Nếu dùng unit reader hiện có, dẫn đúng lần chạy/log, không coi unit pass thay manual nhãn. Test stage làm testcase JSON/Excel theo wf-testcase, gộp file tổng docs người dùng đã chỉ định bằng --into; chuẩn bị docs branch theo wf-git. Không sửa file test case tổng trong lượt plan.

## 6. Migration

Không API/DB/schema/health endpoint. Chỉ dữ liệu cục bộ, không áp dụng skill migration/health endpoint.

## 7. Nhánh Git

Superproject giữ feat/datasets-ocr, frontend giữ feat/mlkit-prototype-measurement; docs giữ nhánh test case hiện có khi gộp ở test stage. Không đổi nhánh hoặc bump con trỏ chỉ vì khác tên. Truyền task ID đầy đủ cho gate/scope. Không tự commit/push/stash/reset.

## 8. Rủi ro

- Cùng hoạt chất khác thương hiệu/hàm lượng: lấy đúng chữ trên ảnh, không copy nhãn cả folder.
- Nhãn dài có khoảng trắng/dấu: ghi đúng sản phẩm, không chỉnh theo raw để nâng điểm.
- Nguồn web không rõ hoặc watermark: giữ unknown, không tự bịa URL/thiết bị/góc.
- Nhãn sửa sau khi 4.09 đã chấm: đổi snapshot hash và chấm lại raw 4.09, không nhất thiết OCR lại; không gọi đó là benchmark frozen cũ.
- Chỉ 49 ảnh trong điều kiện nhất định chưa đại diện toàn bộ; ghi giới hạn, không ép thu thêm số mẫu tùy ý để hoàn tất task dữ liệu.

## 9. Câu hỏi mở

Không có câu hỏi chặn triển khai plan. Xác minh dữ liệu còn thiếu phải làm/ghi pending. Việc publish/PR cần yêu cầu commit/push của người dùng sau khi kết quả cụ thể đã chuẩn bị để review.

## 10. Phát sinh

Giữ nguyên script/evidence nghiên cứu cũ làm lịch sử, không chạy lại hoặc yêu cầu hoàn tất. Không sửa requirement approved. Scope ngoài work có dataset/code/file tổng và baseline từ trước; chỉ ghi đúng kết quả, không xóa để làm sạch.

## Bước tiếp theo

- Chờ duyệt: python .agents/scripts/gate.py approve 4.08-ocr-capture-evaluation plan
- Sau duyệt mới dùng wf-implement cập nhật 04 theo P1–P6 mới; không giữ các bước nghiên cứu engine cũ làm điều kiện hoàn thành.
- Cập nhật: 2026-10-29, Codex.

## Tự kiểm plan

- Gate plan OK tại evidence/plan-rescope-gate.log. Scope thực báo “CHẶN: 226 file ngoài phạm vi”, log evidence/plan-rescope-scope.log; đây là dataset/code/file tổng/baseline từ trước đã được người dùng yêu cầu giữ. Không sửa/xóa hoặc xin lại quyền giữ để scope sạch; không có thay đổi sản phẩm trong lượt plan.
- Parser xác nhận 4 dòng phạm vi dưới datasets/, 6 bước P1–P6 và truy vết AC1–AC6; kết quả chung trong work/4.09-mlkit-prototype/evidence/plan-decision-check.log. Chưa chạy unit/native/OCR hoặc thay dữ liệu.
- Không còn yêu cầu engine/góc chụp nghiên cứu cũ, không đổi API/schema/submodule. Requirement vẫn approved; chỉ sửa plan/evidence/scratch của hai task.
