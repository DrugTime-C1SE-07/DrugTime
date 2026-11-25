---
task: 5.09-meal-llm-cache
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 11:43 +0700
content_hash: sha256:d1cce32a9adb47a9
inputs:
  01-requirement.md: sha256:26efb8072acdc0bc
  03-plan.md: sha256:f2192e480440f867
  04-impl-notes.md: sha256:e774dbb9dc8e187b
  05-test-report.md: sha256:584f3e2b1dd5bc66
---

# 5.09-meal-llm-cache · Review

## 1. Kết luận

**Chưa đạt**

- Code sản phẩm không có lỗi Critical. Không có lỗi High nào nằm ở logic.
- Còn 2 phát hiện High về bằng chứng:
  - Test tích hợp cho vùng rủi ro chưa từng chạy, nên AC5 không có bằng chứng nào.
  - Thiếu bộ test case Excel.
- Hai điểm này là hệ quả của quyết định bỏ giai đoạn test (`05` đã được duyệt với nội dung đó). Theo thang của skill review, chúng vẫn là High.
- Nếu người duyệt chấp nhận rủi ro, hãy ghi rõ quyết định đó vào PR.

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| backend | `git -C backend diff` (working tree so với `f350f40` = `origin/main`; chưa commit) và đọc đủ 5 file mới chưa track |

Kết quả `scope.py --stage implement` (log `evidence/review-scope.log`):
- 12 file `[OK]`.
- 2 file `[NGOÀI]` là `backend/tests/integration/test_meal_suggestions_{api,cache}.py`. Hai file này thuộc giai đoạn test và nằm trong bảng của plan (P7, P8), nên không phải lệch phạm vi.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC4 và AC6–AC13 đều có code tương ứng. AC5 (đổi thuốc hoặc bệnh nền thì key đổi) chỉ được đảm bảo gián tiếp: key băm toàn bộ prompt (AC2 có unit test), còn đường đọc dữ liệu từ DB vào prompt chưa test với cache (H1). |
| Phạm vi | Đạt (xem §2). Hai lệch so với plan đã ghi ở mục "Phát sinh" của `04`: công thức key thêm `casefold`, và chữ ký adapter. |
| Contract | Không đổi hình dạng API, đúng `contract_change: no`. Cột `served_from_cache` chỉ ghi vào DB, không trả cho client. |
| Bất biến kiến trúc | #2 PEP: cache chỉ được chạm sau `access.authorize` (`suggest_meals.py`, `_first_suggestions` gọi sau PEP); có unit test `test_forbidden_never_touches_cache__5_09_AC9`. #4: không cache quyết định quyền; cache chỉ giữ raw output LLM. Có ghi `access_logs` (không đổi so với trước). Không có migration. Import `redis` trong adapter outbound của `ai_meal` không tạo quan hệ mới giữa các module. |
| Bảo mật | URL là `SecretStr` và không bị log. Log adapter chỉ có `kind` của exception. Key không chứa định danh (sha256). `.env` đã nằm trong gitignore. Không có SQL ghép chuỗi. |
| Xử lý lỗi | Bắt `RedisError` để fail-open. Không có retry, timeout 1 giây. Nhưng TTL cấu hình sai thì mọi request trả 500 (M1). |
| Hiệu năng | Mỗi request tối đa một GET và một SET. Mỗi cấu hình có một connection pool qua `lru_cache`. Gọi Redis nằm trong transaction DB, thêm tối đa khoảng 2 giây khi Redis treo (đã ghi ở `04` §5). |
| Chất lượng test | Unit test có ý nghĩa: kiểm cả hit, miss, corrupt, bypass, lỗi Redis, TTL và log, cùng nhánh từ chối. Test tích hợp đã viết nhưng chưa chạy (H1). |
| Dễ đọc và nhất quán | Theo pattern hexagonal và DI của module (`get_meal_suggester`, `get_meal_images`). Không có code chết hay `print`. |
| Đối chiếu 04/05 với log trong `evidence/` | `implement-final-backend.log`: `35 failed, 2532 passed, 1 skipped`, khớp `04` §3. `implement-baseline-main.log` cho cùng 35 fail. `05` ghi đúng là không chạy; không có `test-integration.log`. |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| High | `backend/tests/integration/test_meal_suggestions_cache.py` (cả file); `05` §4 | 13 test tích hợp chưa từng chạy. Chúng là bằng chứng duy nhất cho AC5, cho Redis thật (TTL, `SET EX`) và cho PEP cùng `access_logs` khi cache bật. Vùng rủi ro "Dữ liệu sức khỏe" và "Phân quyền người thân" không có bằng chứng tích hợp. | Chạy `pytest tests/integration` với Redis và Postgres local trước khi merge, lưu log. Hoặc người duyệt ghi rõ việc chấp nhận rủi ro trong PR. |
| High | `work/5.09-meal-llm-cache/` (không có `testcases.json`) | Thiếu bộ test case Excel theo `wf-testcase` (skill review xếp mức High). | Dựng `testcases.json` (các AC dạng unit ghi `Pass` kèm log implement; các AC tích hợp ghi `Pending`), rồi chạy `validate`, `build`, `merge`. |
| Medium | `backend/src/drugtime/modules/ai_meal/adapters/inbound/http.py:95-101`, `backend/src/drugtime/shared/config.py:58` | Khi `MEAL_CACHE_TTL_SECONDS<=0`, `RedisMealCache` raise `ValueError` bên trong dependency của mọi request, nên endpoint trả 500 thay vì fail-open. Cấu hình sai chỉ lộ ra lúc chạy. | Kiểm ở `Settings` (`Field(gt=0)`) để lỗi ngay khi khởi động. Hoặc bắt lỗi trong `get_meal_cache`, log ra rồi trả None. |
| Low | `backend/src/drugtime/modules/ai_meal/application/suggest_meals.py:103` | Output cache hợp lệ nhưng bị lọc hết món vì tên biệt dược của người này (tên biệt dược không nằm trong key) sẽ raise `no_valid_suggestion`, bị coi là `corrupt`, rồi bị ghi đè cho mọi người dùng key đó. Kết quả vẫn đúng, chỉ gây thêm lần gọi LLM và log `corrupt` gây hiểu nhầm. | Chấp nhận được. Có thể tách `no_valid_suggestion` khỏi `invalid_json` khi đo hit rate. |
| Low | `backend/tests/integration/test_meal_suggestions_cache.py:59` | Fixture gọi `pytest.fail` khi không có Redis, trong khi bộ tích hợp skip khi không có Postgres. CI không có Redis sẽ báo 13 test đỏ. | Cố ý theo plan. Ghi chú trong PR, hoặc thêm service Redis vào CI. |
| Low | CD10 trong `docs` | Tài liệu chưa cập nhật thành phần key (Q4) và ghi chú casefold, như đã nêu ở mục "Phát sinh" của `04`. | Cập nhật trong task docs riêng. |

## 5. Mô tả PR

Chưa soạn vì kết luận là **Chưa đạt**. Nếu người duyệt chấp nhận hai High (bỏ test), PR backend `feat/5.09-meal-llm-cache` cần ghi:

- Tóm tắt CD10 cache-aside.
- AC và unit test chứng minh: bảng "Quy tắc / AC đã thực hiện" trong `04`.
- Rủi ro: test tích hợp chưa chạy, và test sẽ fail khi thiếu Redis.

Thứ tự merge theo `wf-git`: PR backend merge trước, rồi đến PR superproject bump con trỏ `backend` cùng artifact `work/5.09-meal-llm-cache/`.

## 6. Ghi chú cho quy trình

- Quy trình chưa có cách bỏ giai đoạn test một cách chính thức cho task M. Hiện người duyệt approve một `05` ghi "chưa chạy", rồi review lại phải xếp việc đó là High. Nên quyết định xem có cần trạng thái "waived" hay không.
- `scope.py --stage implement` báo file test tích hợp là `[NGOÀI]` khi chạy ở giai đoạn review, vì nó lấy toàn bộ diff chưa commit. Nên cho stage `review` gộp phạm vi implement và test.
- Agent đã sửa artifact đã duyệt trong lúc người dùng approve, làm approval hết hiệu lực. Bài học: kiểm trạng thái trước mỗi lần sửa.

## Bước tiếp theo

- Đang chờ người dùng.
- Việc cần làm (chọn một):
  - Chạy test tích hợp và dựng bộ test case: `gate.py reopen 5.09-meal-llm-cache test`, chạy với Redis và Postgres, rồi review lại.
  - Chấp nhận rủi ro: người duyệt chạy `python .agents/scripts/gate.py approve 5.09-meal-llm-cache review`, sửa M1 nếu muốn (cần reopen implement), rồi commit và mở PR.
- Cập nhật lần cuối: 2026-11-25 11:50, Claude Code
