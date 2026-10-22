---
task: 3.23-adherence-family-consent
stage: contract
approved_files:
  api_contract/openapi.json: sha256:8a8b0d74e85db45ec3223554c6b957094432ff1f2f18603b97c528f5884cc65b
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-21 10:30 +0700
content_hash: sha256:e50bcda374a39752
inputs:
  01-requirement.md: sha256:59d6784f453d27aa
---

# 3.23-adherence-family-consent · API contract

## 1. File đã sửa trong submodule contract

- `api_contract/openapi.json`: khai báo `GET /adherence`, tag `adherence`, các schema response và ngoại lệ `groups`/`summary` so với quy ước danh sách `items`.

## 2. Thay đổi

| Endpoint | Thêm / sửa / xóa | Tương thích | Tóm tắt |
|---|---|---|---|
| `GET /adherence` | Thêm vào contract | Không phá vỡ | Công bố endpoint đã tồn tại ở backend: chọn bệnh nhân bằng query `patient_id`, lọc ngày, nhóm theo ngày hoặc thuốc; xác thực, consent, audit, response và lỗi. |

## 3. Chi tiết từng endpoint

### `GET /adherence`

- **Xác thực**: `Authorization: Bearer <app session token>`; thiếu, sai hoặc hết hạn → 401. Admin bị từ chối 403.
- **Request body**: không có. Tất cả query tùy chọn: `patient_id` UUID (mặc định chính người gọi), `from` và `to` dạng `YYYY-MM-DD`, `group_by` là `date` hoặc `medication` (mặc định `date`). `to` mặc định ngày hiện tại tại `Asia/Ho_Chi_Minh`; `from` mặc định 29 ngày trước `to`. Khoảng tối đa 90 ngày bao gồm hai đầu, không chấp nhận `to` ở tương lai.
- **Quyền**: chính chủ cần consent `health_data`. Người thân cần liên kết active với bệnh nhân, bật chia sẻ, consent `family_sharing` và `health_data` của bệnh nhân còn hiệu lực; kiểm từ DB ở mỗi request. `patient_id` từ query luôn được đối chiếu. Truy cập được phép và từ chối với patient tồn tại có audit; lỗi quyền/audit fail-closed. Thu hồi quyền có hiệu lực ở request kế tiếp.
- **200**: JSON `AdherenceHistoryResponse`, một trong `AdherenceByDateResponse` hoặc `AdherenceByMedicationResponse` theo `group_by`; có `patient_id`, `from`, `to`, `timezone`, `as_of`, `summary`, `groups`. Nhóm ngày sắp theo ngày giảm dần; nhóm thuốc sắp theo `medication_id` tăng dần. `AdherenceDose` chỉ chứa id/tên thuốc, id lịch, thời điểm dự kiến/xác nhận, trạng thái và nguồn trạng thái. `adherence_rate` là `null` khi `counted=0`, kể cả khi chỉ có liều chờ xác nhận.
- **401**: `ErrorDetail`, `detail` là câu mô tả, client không so khớp nội dung.
- **403**: `ErrorDetail`; chính chủ thiếu `health_data` → `consent_revoked`; người thân thiếu quyền/consent/chia sẻ, admin, hoặc patient không tồn tại → `khong_co_quyen`. Không có dữ liệu sức khỏe trong response. Patient không tồn tại hiện không ghi audit do FK của `access_logs`.
- **422**: `ValidationError` cho query sai định dạng/enum/UUID; `ErrorDetail` cho `invalid_adherence_date_range`, `adherence_range_too_large`, `adherence_end_date_in_future`.
- **500**: `ErrorDetail` với `Internal server error` khi lỗi nội bộ, gồm kiểm quyền/audit; không trả lịch sử.
- **404/409**: endpoint đọc hiện không phát sinh hai mã này, nên không thêm response giả vào contract.
- **Header**: tất cả mã trên có `Cache-Control: no-store`.
- **Ví dụ**: response 200 cho người thân xem một liều đã uống và response 403/422 nằm trong `api_contract/openapi.json` tại `paths./adherence.get.responses`.
- **Idempotency**: không áp dụng vì endpoint chỉ đọc.

## 4. Thay đổi phá vỡ và client bị ảnh hưởng

Không có thay đổi phá vỡ: chỉ bổ sung đặc tả của endpoint đang chạy, giữ nguyên path, query, response và mã lỗi backend hiện có. Không đổi client trong giai đoạn này.

## 5. Đối chiếu tiêu chí chấp nhận

| AC | Endpoint phục vụ |
|---|---|
| AC1, AC2 | `GET /adherence` 200, patient selector, schema `AdherenceHistoryResponse`, audit được phép. |
| AC3, AC4, AC5, AC6 | `GET /adherence` 403 theo kiểm liên kết, chia sẻ và consent ở mỗi request; không trả dữ liệu. |
| AC7 | `GET /adherence` 500 fail-closed và 403 với audit denied ở transaction riêng. |
| AC8 | `GET /adherence` 401 và 422. |
| AC9 | Path, query, schema, response, bảo mật và `no-store` đã khai báo trong `api_contract/openapi.json`. |

## 6. Kiểm tra đã chạy

| Lệnh | Kết quả | Log |
|---|---|---|
| `python work/3.23-adherence-family-consent/scratch/validate_contract.py` | Đạt: parse JSON, tham chiếu `$ref`, status/header, tên schema mà test tích hợp dùng và ví dụ 200. | `work/3.23-adherence-family-consent/evidence/contract-validate.log` |
| `git -C api_contract diff --check` | Exit 0, không có lỗi whitespace. | `work/3.23-adherence-family-consent/evidence/contract-diff-check.log` |
| `python .agents/scripts/scope.py 3.23-adherence-family-consent --stage contract` | Đạt; chỉ `api_contract/openapi.json` ngoài `work/`. | `work/3.23-adherence-family-consent/evidence/contract-scope.log` |
| `python backend/scripts/export_openapi.py --out work/3.23-adherence-family-consent/scratch/openapi.generated.json` | Chưa chạy được: Python trong môi trường không có `fastapi`. Cần đối chiếu generated OpenAPI ở môi trường có dependencies tại giai đoạn test. | `work/3.23-adherence-family-consent/evidence/contract-export-attempt.log` |
| `PYTHONPATH=backend/src python -c "... decide(AccessFacts(...)) ..."` | Phát hiện `admin_self_allowed=True`, `log_role=None` khi admin chọn chính UUID và có `health_data`; không khớp contract và bất biến admin. | `work/3.23-adherence-family-consent/evidence/contract-admin-self-check.log` |

## 7. Câu hỏi mở

Không có câu hỏi chặn. Theo requirement đã duyệt, người thân đủ quyền xem cùng schema lịch sử mà chính chủ xem.

## 8. Phát sinh

- Backend đã có mã và test cho endpoint này; test tích hợp `test_adherence_history_api.py` đọc `AdherenceByDateResponse`/`AdherenceByMedicationResponse` từ contract. Bản contract mới giữ đúng tên schema đó.
- Patient không tồn tại trả 403 cùng body như patient không được phép nhưng không ghi `denied` vì không có bản ghi patient cho FK. Đây là ngoại lệ hiện hữu cần người duyệt biết; các AC từ chối với patient tồn tại vẫn phải audit.
- PEP hiện xử lý nhánh self trước nhánh admin; phép kiểm tra thuần cho thấy admin có `health_data` tự truy cập được và không có audit. Contract giữ yêu cầu admin nhận 403 theo bất biến dự án; giai đoạn plan cần đưa sửa lỗi gốc và test hồi quy admin-self vào phạm vi backend.
- `git fetch origin` cho `api_contract` không kết nối được GitHub; nhánh task `feat/3.23-adherence-family-consent` được tạo tại commit mà superproject đang trỏ tới, trùng `origin/main` cục bộ. Chưa xác minh remote mới hơn.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: rà soát `api_contract/openapi.json` và các giới hạn ở mục 8; nếu đồng ý, chạy `python .agents/scripts/gate.py approve 3.23-adherence-family-consent contract` trong terminal của người duyệt. Sau đó mới lập `03-plan.md` theo gate.
- Cập nhật lần cuối: 2026-10-21 09:27, Codex.
