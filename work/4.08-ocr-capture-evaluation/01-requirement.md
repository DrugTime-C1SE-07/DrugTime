---
task: 4.08-ocr-capture-evaluation
title: Thu thập và gắn nhãn bộ ảnh bao bì thuốc dùng chung
type: feature
stage: requirement
size: M
contract_change: no
affected: []
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 16:19 +0700
content_hash: sha256:2c4a08a77f82f9e0
---

# 4.08 · Thu thập và gắn nhãn bộ ảnh bao bì thuốc dùng chung

## 1. Mục tiêu

Bàn giao bộ ảnh hộp/vỉ thuốc có nhãn đã đối chiếu với ảnh, có mã ảnh ổn định, phiên bản và hướng dẫn để cả nhóm dùng cho OCR/matching. Đây là task dữ liệu mẫu; không có yêu cầu nghiên cứu, tích hợp hoặc đánh giá engine OCR.

## 2. Phạm vi

### Trong phạm vi

- Bộ ảnh gốc tại datasets/images, ID duy nhất và đường dẫn tương đối ổn định; phân nhóm sản phẩm/bao bì để tra cứu. Tên folder không phải đáp án khi khác chữ in trên ảnh.
- datasets/labels.xlsx theo format hiện hành: image_id, relative_path, drug_name, strength. drug_name là tên sản phẩm in trên bao bì, gồm biến thể cần phân biệt; strength chỉ ghi khi nhìn thấy và xác minh được. Không dùng raw OCR để tạo hoặc sửa đáp án cho khớp kết quả.
- Kiểm tra người/ngày xác minh nhãn; ghi trường chưa rõ hoặc không có đáp án. Cùng hoạt chất không tự coi là cùng thương hiệu; không suy strength từ ảnh khác hoặc tên folder.
- Ghi nguồn ảnh khi xác định được và điều kiện chụp biết được; phân biệt ảnh web/ảnh chụp, không bịa góc/thiết bị/ánh sáng. Không có yêu cầu thu thêm một số ảnh tùy ý nếu bộ hiện tại đủ scope được nhóm chấp nhận; báo rõ giới hạn.
- Chốt phiên bản/hash ảnh và workbook, thống kê số ảnh/sản phẩm/loại bao bì, README cách thêm/đọc nhãn và dùng lại. Ảnh xử lý từ cùng nguồn không tự tính là mẫu nguồn độc lập.
- Bộ ảnh/nhãn/README là thư mục thường trong superproject. Sau người dùng yêu cầu commit/push, nhóm clone/pull lấy được; không tuyên bố đã chia sẻ nếu mới lưu cục bộ.
- Hồ sơ duyệt/evidence trong work/4.08-ocr-capture-evaluation. Giữ ID task hiện có để không mất truy vết; không đổi tên thư mục task chỉ vì đổi mô tả.

### Ngoài phạm vi

- Chạy, đánh giá, huấn luyện engine OCR hoặc nghiên cứu góc tối ưu bằng công cụ thử nghiệm cũ. Không cần cài binary/ngôn ngữ OCR hay hoàn tất script nghiên cứu cũ để đóng 4.08.
- Prototype/accuracy ML Kit/go-no-go (4.09); camera/crop/preprocessing (4.10); gọi OCR sang matching (4.11); normalization/index (4.12); matching/top-N (4.13); benchmark toàn luồng (4.17).
- API/backend/DB, bucket hoặc submodule mới, dữ liệu patient/đơn thuốc, LLM, sửa app.
- Xóa ảnh/raw/evidence cũ hoặc công cụ của người dùng; commit/push khi chưa được yêu cầu rõ.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn | Điều rút ra |
|---|---|
| Bảng Sprint 4 mới người dùng cung cấp trong chat | 4.08 là Collect + label packaging sample set; không đánh giá engine. Không dùng backlog repo cũ để thay phân công này. |
| Chỉ dẫn người dùng ngày 2026-10-29 và scope-correction.md | Loại yêu cầu nghiên cứu OCR cũ khỏi phạm vi hiện hành; người dùng đã reopen requirement/plan. |
| datasets/images, labels.xlsx, README.md | Hiện có 49 ảnh và 49 nhãn về cấu trúc. Nhãn được điền từ ảnh nhưng vẫn cần đối chiếu/xác minh; không tự coi số hàng bằng số ảnh là verified hoàn toàn. |
| datasets/results/pilot-002/summary.json và report.md | 49 ảnh có raw ML Kit; đây là kết quả 4.09, không phải nguồn đáp án cho 4.08. |
| Proposal_v5.docx §6.2/6.3, FR01, §8.1 và lộ trình, nguồn đã đối chiếu tại work/4.09-mlkit-prototype/evidence/plan-dataset-source.log | Bao bì thuốc/on-device/manual confirmation; không OCR đơn thuốc. |
| 04-impl-notes.md và các script/evidence lịch sử trong work/4.08 | Bản nghiên cứu cũ được giữ để truy lịch sử; các bước nghiên cứu engine/góc chụp không còn là điều kiện hoàn thành task mới. |
| AGENTS.md, wf-requirement và wf-git | Không sửa approval metadata, không tự duyệt; nhánh superproject và frontend độc lập theo yêu cầu người dùng. |

### Quyết định nghiệp vụ áp dụng

| Quy tắc/nguồn | Trạng thái | AC |
|---|---|---|
| Bảng task mới và chỉ dẫn 2026-10-29: bộ ảnh có nhãn dùng chung, không nghiên cứu OCR | Chỉ dẫn người dùng; ghi lại để duyệt requirement | AC1–AC6 |
| Tên sản phẩm chính, hàm lượng độc lập khi thấy trên ảnh | Người dùng đã chốt trong chat | AC2, AC3 |
| Proposal: bao bì thuốc, không đơn thuốc/PHI | Giữ bất biến phạm vi sản phẩm | AC5 |
| Task 4.12/4.13/4.17 theo bảng mới | Ngoài phạm vi 4.08, không đợi matching để bàn giao dữ liệu | AC6 |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Không | Không sửa mobile trong task bộ ảnh. |
| backend | Không | Không API/schema. |
| api_contract | Không | Không đổi HTTP contract. |
| tests | Không | Kiểm dữ liệu cục bộ, không E2E service. |
| docs | Không | Chỉ đọc tài liệu nguồn; hồ sơ task ở work/. |
| .agents | Không | Giữ nguyên workflow/skill. |

Superproject có thay đổi dữ liệu/hướng dẫn dưới datasets và artifact dưới work; affected=[] vì không sửa submodule.

## 5. Thay đổi API contract

contract_change: no. Không thêm/sửa endpoint, payload, mã lỗi hoặc xác thực; không cần gọi backend để thu thập/xác minh ảnh.

## 6. Vùng rủi ro và bất biến

- Không chứa PHI/credential/token trong ảnh/nhãn/nguồn. Không thêm endpoint sức khỏe, schema, module dependency hoặc interaction logic.
- Nhãn tên/strength sai có thể làm sai phép đo/chọn sản phẩm về sau: đáp án phải do người kiểm đối chiếu ảnh; không sửa theo raw hoặc suy thương hiệu từ hoạt chất.
- Chỉ công bố nguồn/điều kiện đã biết; dữ liệu thiếu ghi rõ. Thử nghiệm không thay xác nhận thuốc thủ công.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given bộ ảnh và workbook, When kiểm dữ liệu, Then mỗi ảnh có ID duy nhất và đúng một dòng nhãn, đường dẫn tồn tại/không thoát datasets, không bỏ âm thầm hàng lỗi. | unit/công cụ + manual thống kê |
| AC2 | Given ảnh đọc được tên sản phẩm, When người kiểm đối chiếu nhãn, Then drug_name đúng tên/biến thể trên bao bì; tên folder hoặc raw không thay đáp án ảnh, có người/ngày xác minh. | manual: xác minh đáp án |
| AC3 | Given strength nhìn thấy hoặc bị thiếu/mờ/nhiều thành phần, When gắn nhãn, Then chỉ điền nội dung xác minh được, phần chưa rõ để trống/ghi thiếu; không suy sản phẩm/hàm lượng chỉ từ hoạt chất. | manual: đọc bao bì |
| AC4 | Given phiên bản dữ liệu bàn giao, When kiểm snapshot/README, Then có hash ảnh/nhãn, số ảnh/sản phẩm/bao bì, nguồn/điều kiện đã biết và hạn chế; ảnh xử lý cùng nguồn không được tính như mẫu độc lập mà không ghi quan hệ. | unit/công cụ + manual review |
| AC5 | Given ảnh hoặc metadata không phù hợp (PHI, secret, nguồn/nhãn không xác minh), When rà soát, Then loại/tách hoặc ghi rõ pending, không bịa đáp án/nguồn để làm bộ dữ liệu đầy đủ. | manual |
| AC6 | Given bộ dữ liệu đã chốt và người dùng cho commit/push, When nhóm clone/pull, Then lấy được ảnh/nhãn/README và tái hiện kiểm tra từ hướng dẫn; không phụ thuộc công cụ nghiên cứu OCR cũ. | manual bàn giao/Git |

## 8. Câu hỏi mở

Không có câu hỏi chặn việc cập nhật requirement. Xác minh nhãn, ghi nguồn/phiên bản và đưa dữ liệu lên repo là công việc bàn giao còn phải có bằng chứng, không tự coi đã làm. Không tự yêu cầu số mẫu/ngưỡng/góc mới ngoài chỉ dẫn.

## 9. Giả định

- Dùng 49 ảnh hiện có làm phiên bản đầu dự kiến; chỉ chốt sau rà scope và nhãn, không khẳng định đại diện mọi sản phẩm/điều kiện.
- Người dùng muốn giữ superproject ở feat/datasets-ocr, frontend ở feat/mlkit-prototype-measurement; không chuyển nhánh hoặc bump con trỏ vì khác tên.
- Không xóa bằng chứng cũ. Không cần hoàn tất nghiên cứu OCR cũ để đạt các AC thay thế này.

## 10. Phát sinh

- Requirement/plan cũ đã mở rộng sang nghiên cứu engine/góc chụp; người dùng bỏ phần này và đã reopen. Vòng này thay requirement, chưa sửa plan/implement hoặc dữ liệu.
- Các output cũ chỉ là lịch sử, không nguồn hoàn thành AC mới. Không xóa chúng hoặc tự đổi status approved ở bất cứ artifact nào.
- Repo còn thay đổi nền và datasets đã có từ trước; không sửa hoặc xóa chúng để làm scope sạch. Scope cuối phải được lưu đúng kết quả thực tế.

## 11. Size

size: M. Bộ ảnh/nhãn, kiểm dữ liệu và bàn giao nhiều file vượt khoảng 3 file/50 dòng; không đổi contract hoặc submodule.

## Bước tiếp theo

- Chờ người dùng duyệt: python .agents/scripts/gate.py approve 4.08-ocr-capture-evaluation requirement
- Sau duyệt, lượt kế tiếp cập nhật 03-plan.md theo AC1–AC6 này, thay các bước nghiên cứu OCR cũ. Chưa bắt đầu plan/implement/test trong lượt requirement.
- Cập nhật: 2026-10-29, Codex.

## Kiểm tra requirement sau đổi phạm vi · 2026-10-29

- Gate requirement OK, log evidence/requirement-rescope-gate.log. Chỉ sửa requirement và ghi chú/evidence/scratch trong work; chưa sửa plan, code, dữ liệu hoặc file approved.
- Scope báo nguyên văn “CHẶN: 226 file ngoài phạm vi”, log evidence/requirement-rescope-scope.log: .gitignore (1), api_contract (2), datasets (222), docs (1). Đó là thay đổi dữ liệu/công cụ/file tổng và baseline đã có trước vòng sửa; người dùng đã yêu cầu giữ/tạo/điền/kiểm. Không sửa, xóa hoặc xin lại quyền giữ chúng để làm scope sạch.
- Không chạy OCR/test/build hoặc thay app trong vòng requirement. Các số liệu pilot là nguồn hiện có đã ghi rõ, không là lần kiểm mới.
