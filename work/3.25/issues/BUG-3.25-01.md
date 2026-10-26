# [Medium][3.23] GET /adherence bỏ sót liều xác nhận sớm hợp lệ

## Phân loại

- **BUG-3.25-01**, phát hiện tại task 3.25 / PB21 / AC3; task sản phẩm xử lý: **3.23**.
- **Medium**: lịch sử và tỷ lệ tuân thủ chưa phản ánh liều đã xác nhận hợp lệ; cách tránh tạm thời là đọc lại sau giờ uống. AC3 chưa đạt vẫn chặn nghiệm thu task 3.25.
- Dose log đã lưu; bằng chứng hiện có là liều bị loại khỏi lịch sử, chưa chứng minh mất bản ghi.

## Môi trường và tái hiện

Lượt test ngày 25/10/2026: backend `49f2f11`, FastAPI TestClient + PostgreSQL/Supabase local thật, api_role và PEP/audit thật. Contract /adherence đã khôi phục trong working tree. Clock cố định, múi giờ Asia/Ho_Chi_Minh; dữ liệu giả.

1. Tạo lịch uống của patient P lúc **08:00 ngày 19/10/2026**, chưa có liều khác trong khoảng kiểm tra. Người thân F có liên kết, chia sẻ và consent hợp lệ.
2. Tại **07:30**, patient xác nhận liều qua luồng ghi nhận liều. Xác nhận được chấp nhận, DB có dose log.
3. Giữ clock lịch sử ở 07:30; F gọi `GET /adherence?patient_id=<P>&from=2026-10-19&to=2026-10-19&group_by=date`.
4. Lặp lại với `group_by=medication`.

## Thực tế / kỳ vọng

Cả hai kiểu nhóm trả **200**, đúng schema, có audit allowed nhưng summary là:

```json
{"total":0,"taken":0,"late":0,"missed":0,"pending":0,"counted":0,"adherence_rate":null}
```

Theo ngoại lệ AC3 đã chốt trong task 3.25, liều xác nhận sớm hợp lệ phải xuất hiện ngay, nhóm chứa một liều và summary:

```json
{"total":1,"taken":1,"late":0,"missed":0,"pending":0,"counted":1,"adherence_rate":100}
```

## Nguyên nhân đã đối chiếu

- `src/drugtime/modules/adherence/domain/history.py::build_history` lọc `row.scheduled_at <= as_of`.
- `src/drugtime/modules/adherence/adapters/outbound/sql_adherence.py`: CTE recorded lọc `dl.scheduled_at <= :as_of`.
- Contract gốc và test cũ vẫn loại liều tương lai kể cả đã xác nhận sớm, trái ngoại lệ AC3. Cần xử lý đồng bộ quy tắc, contract, domain/SQL và kỳ vọng cũ.

## Bằng chứng / hồi quy

Nguồn local trong superproject: `work/3.25/05-test-report.md`, mục 6; TC-FADH-20/52, Bug Report BUG-FADH-20.

- `work/3.25/evidence/test-contract-history-final.log` và `.xml`: **66 Pass/2 Fail**. Hai Fail: `test_family_early_confirmation_counts_immediately__AC3[date|medication]`.
- `work/3.25/evidence/test-contract-targeted.log` và `.xml`: **138 Pass/2 Fail**, hai unit xác nhận sớm.
- Test API mới còn ở working tree tại thời điểm báo cáo: `tests/integration/test_adherence_history_api.py::test_family_early_confirmation_counts_immediately__AC3`.

Từ root superproject, sau khi dựng DB local theo fixture:

```powershell
& backend/.venv/Scripts/python.exe -X utf8 -m pytest backend/tests/integration/test_adherence_history_api.py -k family_early_confirmation_counts_immediately -q
& backend/.venv/Scripts/python.exe -X utf8 -m pytest backend/tests/unit/test_get_adherence_history.py -k confirmed_before_deadline_counts_immediately -q
```

Kết quả trên lấy từ evidence ngày 25/10, không chạy lại khi tạo issue. Evidence và phần chưa commit chưa có URL GitHub.

## Tiêu chí hoàn tất

- [ ] Liều xác nhận sớm hợp lệ xuất hiện ngay và có tỷ lệ đúng ở cả date/medication.
- [ ] Không đưa liều tương lai chưa xác nhận vào lịch sử/mẫu số sai quy tắc.
- [ ] Đồng bộ contract, domain/SQL và test cũ; giữ test hồi quy mới để chứng minh đỏ trước/xanh sau.
- [ ] Chạy lại unit và API/DB lịch sử, biên xác nhận, timezone, idempotency/race; GET không sửa dose log, PEP/audit vẫn đúng.
