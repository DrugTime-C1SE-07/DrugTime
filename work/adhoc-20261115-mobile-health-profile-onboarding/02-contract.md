---
task: adhoc-20261115-mobile-health-profile-onboarding
stage: contract
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-15 17:30 +0700
content_hash: sha256:8322c29321d72f58
inputs:
  01-requirement.md: sha256:c60e413f4f65fe0d
---

# S08b–S08e · Hợp đồng API

## 1. File đã sửa trong submodule contract

- `api_contract/openapi.json` trong checkout riêng `scratch/api_contract`, nhánh `feat/adhoc-20261115-mobile-health-profile-onboarding`, base `b542ccb99f2f5654746be920a7056ecf7849c4c7` (local `main` và `origin/main`).
- `openapi.patch` trong thư mục task là diff có thể áp lên checkout contract. SHA-256 `B1475A7B7D7FAC2D3F025A74A115F898F5355F8EB5CC4B938F33E276A0238FEE`.

## 2. Thay đổi

| Endpoint | Thao tác | Tương thích | Tóm tắt |
|---|---|---|---|
| `GET /allergens` | Thêm | Không phá vỡ | Danh mục dị ứng thuốc, thực phẩm; ID ổn định, tên hiển thị từ backend. |
| `GET /profile/health-setup` | Thêm | Không phá vỡ | Đọc cả hai bước, trạng thái từng bước và phiên bản để đối chiếu khi lưu. |
| `PUT /profile/health-setup` | Thêm | Không phá vỡ | Thay lựa chọn của một hoặc cả hai bước trong một giao dịch; bỏ qua bằng cách không gửi bước. |

## 3. Chi tiết từng endpoint

- `GET /allergens` yêu cầu bearer. Trả `200 {items: [{id, category, name}]}`; thứ tự thuốc trước thực phẩm, giữ thứ tự trả về trong từng nhóm. Danh mục giới hạn theo nhóm thiết kế, trả đầy đủ trong một response. Không nhận query. Mã lỗi `401`, `422`, `500` theo OpenAPI. Bệnh nền tiếp tục dùng `GET /conditions` với phân trang hiện hành.
- `GET /profile/health-setup` trả `200` gồm `revision`, `allergies`, `conditions`. Mỗi bước có `status` là `unreported`, `none_known` hoặc `reported`. Bước `reported` có `catalog_ids` và `custom_names`; ít nhất một mảng có phần tử. Liên kết bệnh nền hiện có được phản ánh trực tiếp trong bước `conditions`. Mã lỗi `401`, `403`, `422`, `500`.
- `PUT /profile/health-setup` nhận `revision` và ít nhất một bước. Bước chủ động xác nhận không có gửi `{status: "none_known"}`; server xóa lựa chọn của bước đó và lưu lời xác nhận. Bước đã khai gửi `reported` và danh sách đầy đủ. Trường bước vắng mặt giữ nguyên; `null` và `unreported` không hợp lệ khi ghi. Tên tự nhập được trim, chuẩn hóa NFC và kiểm trùng theo Unicode casefold. Lựa chọn danh mục dùng ID, có mã validation riêng cho ID không tồn tại. Giữ ID và metadata của các liên kết bệnh nền còn được chọn.
- Lưu thành công trả `200` với snapshot sau lưu. Chốt lưu và phiên bản trong cùng giao dịch, kể cả khi có ghi đồng thời qua API liên kết bệnh nền hiện có. Phiên bản cũ trả `409 health_setup_revision_conflict` mà không ghi. Khi kết quả không chắc chắn hoặc gặp `409`, GET để đối chiếu các bước đã gửi; nếu khác thì xem lại dữ liệu trước khi lưu lại. Bản gửi cùng phiên bản hiện tại và cùng giá trị không tạo mục trùng hoặc tăng phiên bản. Không đưa vào hàng đợi offline.
- Hai operation `/profile/health-setup` chỉ dành cho bệnh nhân chính chủ. PEP và consent `health_data` kiểm mỗi request qua DB; không hỗ trợ quyền người thân hoặc admin ở endpoint này. Selector trỏ ngoài chính chủ trả `403 khong_co_quyen` và audit denied; query khác trả `422`. Response thành công dùng `Cache-Control: no-store`. Nếu audit bền vững không ghi được, trả lỗi, không trả dữ liệu và không commit.
- OpenAPI có schema và ví dụ request, response thành công, `409` và validation `422`. Các lỗi tài khoản, thiếu quyền và lỗi nội bộ tái sử dụng định nghĩa `Profile*`.

## 4. Thay đổi phá vỡ và client bị ảnh hưởng

Không có. Đường dẫn, mã lỗi, schema và metadata của API bệnh nền cũ giữ nguyên. API cũ tiếp tục dùng liên kết bệnh nền theo danh mục; mục bệnh nền tự nhập hiển thị qua endpoint onboarding mới. Mobile onboarding là client mới của ba operation.

## 5. Đối chiếu tiêu chí chấp nhận

| AC | Contract phục vụ |
|---|---|
| AC1–AC3 | Điều hướng và frame thuộc app. `GET /allergens`, `GET /conditions` cấp lựa chọn thực cho AC2–AC3. |
| AC4–AC6 | GET và PUT snapshot; phân biệt bước vắng mặt, chưa khai và xác nhận không có. |
| AC7 | PUT nguyên tử, revision, 409, quy tắc đọc lại khi không rõ kết quả. |
| AC8–AC9 | PEP, đồng ý mỗi request, 403, audit độc lập cho denied, fail closed. |
| AC10 | Snapshot phản ánh liên kết bệnh nền cũ; hồ sơ rỗng chưa xác nhận trả `unreported`. Migration và kiểm DB thuộc bước triển khai. |

## 6. Kiểm tra đã chạy

| Lệnh | Kết quả | Log |
|---|---|---|
| `python scratch/check_contract.py` (tính từ thư mục task) | Parse JSON, resolve tham chiếu nội bộ, ID operation duy nhất, so sánh JSON của route/schema cũ, đối chiếu mã lỗi và tính nhất quán của ví dụ. Chưa chạy validator OpenAPI toàn phần. | `evidence/contract-validate.log` |
| `git diff --check` trong clone và `git apply --check` trên submodule hiện tại | Pass. | `evidence/contract-validate.log` |
| `python .agents/scripts/scope.py adhoc-20261115-mobile-health-profile-onboarding --stage contract` | Exit 1, báo 1.267 file có sẵn ngoài phạm vi, cùng số lượng với requirement. Diff của clone chỉ gồm `openapi.json`. | `evidence/contract-scope.log` |

## 7. Câu hỏi mở

Không có câu hỏi chặn. Contract chọn revision chung cho cả hồ sơ để phát hiện ghi đồng thời. App cần đọc lại và đối chiếu khi có xung đột hoặc mất phản hồi. Bước Plan cần kiểm nguồn danh mục và ánh xạ hiển thị để đủ mục thiết kế, cùng liên kết prototype trước khi quyết định chi tiết điều hướng.

## 8. Phát sinh

- Submodule tại root đang ở nhánh `feat/5.06-admin-queue-api`, pin `4f8144b`. Lệnh tạo worktree bị từ chối ghi ref trong `.git/modules/api_contract`. Clone cục bộ từ main cho phép soạn contract trên nhánh riêng. Patch đã được kiểm có thể áp lên pin hiện tại. Khi tiếp tục, dùng checkout riêng hoặc xác nhận nhánh đích trước khi áp patch. Chưa commit hoặc push.
- Từ chối selector ngoài chính chủ của endpoint mới theo AC8. Endpoint cũ giữ hành vi validation selector hiện hành.

## Bước tiếp theo

- Đang chờ duyệt contract. Đối chiếu `openapi.patch` rồi chạy `python .agents/scripts/gate.py approve adhoc-20261115-mobile-health-profile-onboarding contract`.
- Sau khi duyệt, làm giai đoạn plan.
- Cập nhật ngày 2026-11-15, Codex.

