# Kiểm thử lịch sử tuân thủ — PB21

Collection `collections/DrugTime-Adherence` gọi `GET /adherence` theo `api_contract/openapi.json`.
Path và bảy schema được khôi phục từ commit contract `382fb13`; các endpoint khác giữ nguyên.
Collection được khởi tạo bằng `postman spec generate collection`, sau đó thay dữ liệu giả sinh tự động
bằng biến runtime, ví dụ từ contract và assertion. Contract là nguồn chuẩn; khi đổi interface, cập nhật
contract trước rồi đồng bộ request/example/assertion liên quan, giữ các script đã viết.

## Chạy với API local

1. Khởi động Backend API và Supabase local, dùng DB test. Collection chặn URL ngoài HTTP loopback.
2. Sao chép `environments/Adherence local.environment.yaml` vào một file runtime trong `work/3.25/scratch/`.
   Điền `base_url`, `patient_id` (P đã chia sẻ), `denied_patient_id` (Q tồn tại, không liên kết),
   `from_date`, `to_date` và `family_access_token` (app session mobile, không dùng Supabase access token).
   Cấp token qua biến hiện tại/vault của Postman hoặc file runtime bị ignore; không commit token.
3. Chạy từ gốc superproject:

```powershell
postman collection lint postman/collections/DrugTime-Adherence
postman environment lint 'postman/environments/Adherence local.environment.yaml' --fail-severity warning
postman collection run postman/collections/DrugTime-Adherence -e work/3.25/scratch/local.environment.yaml --no-report-events
```

Có sáu request: nhóm ngày (200), nhóm thuốc (200), thiếu bearer (401), patient không có quyền (403),
`group_by` sai (422), khoảng hơn 90 ngày (422). Các assertion kiểm status, JSON, `Cache-Control: no-store`,
patient, timezone, field theo contract, số liều, tỷ lệ, trạng thái và không lặp occurrence.
Ví dụ chỉ dùng dữ liệu giả, không chứa token. Không gửi run events lên workspace.

## Thu hồi quyền với cùng bearer

Chạy request `Xem lịch sử theo ngày` bằng token F để nhận 200. Thu hồi `health_data`, `family_sharing`,
tắt sharing hoặc hủy link trên DB test bằng luồng sở hữu, chờ transaction commit. Giữ token F, đặt
`denied_patient_id=P`, chạy `Chặn truy cập không có quyền`: phải 403 `khong_co_quyen` ngay request kế tiếp.
Kiểm DB có `allowed` rồi `denied`, đúng actor/scope; `dose_logs` không đổi. Không lưu lịch sử sức khỏe
trong biến môi trường. Collection chỉ đọc; việc dựng fixture/thu hồi thuộc test harness hoặc luồng sản phẩm.

## Kiểm chứng API và DB

```powershell
cd backend
.venv/Scripts/python.exe -m pytest tests/integration/test_adherence_history_api.py tests/integration/test_adherence_history_access.py -q
.venv/Scripts/python.exe -m pytest tests/unit/test_contract_adherence.py -q
```

Pytest kiểm cả PostgreSQL thật, PEP, audit fail-closed, rollback, idempotency và Worker race.
Bằng chứng task: `work/3.25/evidence/test-contract-*.log/xml` và `test-postman-live.log`.
Test API pass không chứng minh lifecycle Android hoặc đã sửa lỗi xác nhận sớm trước giờ dự kiến;
xem `work/3.25/05-test-report.md` cho các lỗi và giới hạn còn mở.
