---
task: 5.09-meal-llm-cache
title: Cache output LLM gợi ý bữa ăn trên Redis (CD10)
type: feature
stage: requirement
size: M
contract_change: no
affected: [backend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 10:08 +0700
content_hash: sha256:26efb8072acdc0bc
---

# 5.09-meal-llm-cache · Cache output LLM gợi ý bữa ăn trên Redis (CD10)

## 1. Mục tiêu

Giảm số lần gọi LLM (chi phí và độ trễ) khi nhiều lần yêu cầu gợi ý bữa ăn có cùng input đã ẩn danh, bằng cache-aside trên Redis (Upstash) trước LLM provider. Cache không được vượt qua kiểm soát consent, không làm gợi ý bỏ qua kiểm tra an toàn, và lỗi cache không được làm hỏng tính năng (fail-open).

## 2. Phạm vi

### Trong phạm vi

- Tính cache key tất định từ input đã tối thiểu hóa (không định danh) cộng phiên bản prompt, prefix `meal_cache:`.
- Tra cache trước khi gọi LLM ở luồng gợi ý lần đầu (`POST` gợi ý bữa ăn không có `previous_suggestion_id`).
- Chỉ lưu raw output LLM đã qua parse/validate thành công, luôn kèm TTL.
- Khi phục vụ từ cache: chạy lại parse + lọc (thực phẩm cần tránh, dị ứng, tên thuốc), giữ chỗ ảnh, gắn disclaimer, ghi `meal_suggestions` với `served_from_cache = true`, ghi `access_logs` như luồng hiện tại.
- Fail-open: Redis không kết nối được, timeout, từ chối lệnh (hết quota), hoặc entry hỏng → bỏ qua cache, gọi LLM, vẫn trả gợi ý.
- Cấu hình: URL cache riêng (Upstash `rediss://`) và TTL qua biến môi trường; URL rỗng thì tắt cache.
- Log sự kiện hit / miss / lỗi cache để đo hit rate, không chứa định danh hay nội dung.
- Unit test và test tích hợp (Postgres + Redis local thật).

### Ngoài phạm vi

- Gợi ý lại (`previous_suggestion_id`, task 5.11): không tra, không ghi cache (xem Q3).
- Nhiều biến thể N > 1 mỗi key (xem Q2).
- Readiness `/health` báo trạng thái Upstash (task 4.13).
- Tạo database Upstash, secret trên Render, đo độ trễ (task 4.15, 4.16).
- DPIA bổ sung Upstash (task 1.19 / 6.01).
- Xóa chủ động entry cache khi thuốc/bệnh nền đổi: không cần, key tự đổi theo input (CD10).
- Job xóa dữ liệu 5.08: cache không chứa định danh nên không thuộc phạm vi xóa (CD10 §4).
- Sửa engine kiểm tra thuốc–thực phẩm, prompt, parser.
- Dashboard hit rate.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx` (Sprint 5 Backlog, Replan Log) | 5.09 = PB37 "Backend: LLM API integration (meal-suggestion prompt + parsing)", 12h, Not started; phần tích hợp LLM thực tế đã làm ở 4.26/5.03, còn lại là cache CD10. |
| `docs/Team1_DTU/03_Design/Architecture/DrugTime – Bổ sung kiến trúc Job Queue (RabbitMQ) + LLM Cache v4.1_1.md` §3, §4, §5, §6 (5.09, 5.12), §7 | Quyết định CD10: cache-aside trên Upstash, key không định danh, prompt version trong key, chỉ cache output đã validate, TTL bắt buộc, fail-open, consent chặn trước khi tra cache, kiểm tra an toàn chạy lại mỗi lần phục vụ. TTL và N chưa chốt (§7). |
| `backend/src/drugtime/modules/ai_meal/application/suggest_meals.py` | Thứ tự hiện tại: PEP (`authorize` WRITE, `Scope.MEAL`, consent) → khai báo bắt buộc → `suggester is None` → đếm lượt → đọc thuốc/bệnh nền/quy tắc → `build_prompt` → `suggester.suggest` → `parse_suggestions` → ảnh → `store.insert`. Đây là chỗ chèn cache. |
| `backend/src/drugtime/modules/ai_meal/application/ports.py` | Port `MealSuggester.suggest(prompt) -> str` trả JSON thô; CD8 cho phép đặt cache như decorator quanh port này. |
| `backend/src/drugtime/modules/ai_meal/domain/model.py` | `MealSuggestionInput` đã trim/khử trùng/sắp xếp mọi danh sách "để cùng dữ liệu luôn cho cùng prompt và cache key ở 5.09". Input gồm cả dị ứng, hạn chế, sở thích, bữa ăn. |
| `backend/src/drugtime/modules/ai_meal/domain/prompt.py` | `PROMPT_VERSION = "meal-v2"`; prompt user chứa bữa ăn, bệnh nền, dị ứng, hạn chế, thực phẩm cần tránh, hoạt chất, sở thích (JSON `sort_keys`). `drug_names` (biệt dược) không vào prompt, chỉ dùng lọc output. |
| `backend/src/drugtime/modules/ai_meal/adapters/outbound/sql_meal_suggestions.py` | `INSERT ... served_from_cache = false` cố định; cột đã có. |
| `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql:384` | `served_from_cache boolean NOT NULL DEFAULT false` — không cần migration. |
| `backend/src/drugtime/modules/ai_meal/adapters/inbound/http.py` | `LlmUnavailable` → 503, `LlmInvalidOutput` → 502, tắt tính năng → 503 `llm_disabled`. |
| `backend/src/drugtime/shared/config.py`, `backend/pyproject.toml` | Đã có `redis>=5.0` và `redis_url` (Redis local dùng cho health). Chưa có cấu hình cache riêng. |
| `api_contract/openapi.json` | Không có field `served_from_cache` hay tham số cache trong response; cache không lộ ra API. |
| Tìm trên mọi nhánh remote của `backend` (`upstash`, `meal_cache`, `MealCache`) | Chưa có cài đặt cache nào. |

## Quyết định nghiệp vụ áp dụng

| Nguồn | Quy tắc | Trạng thái theo nguồn | AC |
|---|---|---|---|
| CD10 §3 "Mô tả" | Cache hit dùng lại output; miss gọi LLM | Đề xuất bổ sung kiến trúc v4.1 (chưa ghi trạng thái duyệt) | AC3, AC4 |
| CD10 §3 "Mô tả" | Chỉ lưu output đã validate JSON, kèm TTL | như trên | AC3, AC7 |
| CD10 §3 "Mô tả", §4 | Kiểm tra thuốc–thức ăn và disclaimer luôn chạy lại khi phục vụ | như trên | AC4, AC6 |
| CD10 §3 "Mô tả", R-09 | Cache lỗi → fail-open gọi thẳng LLM | như trên | AC8 |
| CD10 §3 "Cache key" | Prefix `meal_cache:`, hash input ẩn danh + phiên bản prompt, không `user_id`; đổi thuốc/bệnh/danh mục → key đổi | như trên | AC1, AC2, AC5, AC6 |
| CD10 §3 "Đánh đổi", §6 (5.09) | Rút consent `ai_meal` chặn trước khi tra cache | như trên | AC9 |
| CD10 §5 "Cache" | Mọi key có TTL | như trên | AC3 |
| Schema v8 (CD10 §6) | `meal_suggestions.served_from_cache`; không lưu cache key trong bảng | như trên | AC3, AC4 |
| CD10 §7 | TTL (đề xuất 7 ngày), N (đề xuất 1–2), loại bữa trong key | **Chưa chốt** | Q1, Q2 |

Điểm không nhất quán: danh sách thành phần key ở CD10 (hoạt chất, bệnh, thực phẩm cần tránh, prompt version, có thể bữa) thiếu dị ứng, hạn chế, sở thích, trong khi prompt hiện tại có chứa chúng → đã chốt dùng toàn bộ input (mục 9, Q4).

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Module `ai_meal`: adapter cache, use case, cấu hình, store ghi `served_from_cache`, unit + integration test (`backend/tests/integration`). |
| `api_contract` | Không | Hình dạng API không đổi. |
| `frontend` | Không | Client không biết cache tồn tại. |
| `tests` | Không | Test tích hợp đặt trong `backend/tests/integration`. |
| `docs` | Không | Không ghi artifact vào docs. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: cache nằm sau API. Endpoint, field, mã trạng thái, lỗi giữ nguyên; `served_from_cache` chỉ ghi DB, không trả ra response.
- Endpoint liên quan: chỉ dùng endpoint tạo gợi ý bữa ăn hiện có (`create_meal_suggestions_endpoint` trong `ai_meal/adapters/inbound/http.py`).

## 6. Vùng rủi ro và bất biến bị chạm

- **Dữ liệu sức khỏe** (bất biến 2): endpoint gợi ý đọc thuốc/bệnh nền. Tra cache phải nằm sau PEP (`authorize` + consent + `access_logs`); hit vẫn ghi `access_logs` và `meal_suggestions`. Nội dung cache dẫn xuất từ dữ liệu sức khỏe nên key không được chứa định danh, value không được chứa định danh.
- **Phân quyền người thân / consent**: rút consent `ai_meal` có hiệu lực ngay ở request kế tiếp, kể cả khi có entry cache.
- **Bí mật**: URL Upstash chứa token → chỉ ở biến môi trường, không vào code, log, message lỗi.
- **Ranh giới module**: adapter mới nằm trong `ai_meal`; không thêm import chéo module (`pytest backend/tests/architecture` phải pass).

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given hai input chỉ khác thứ tự, hoa thường, khoảng trắng trong danh sách, When tính cache key, Then key giống nhau, bắt đầu bằng `meal_cache:` và không chứa `user_id`, `patient_id`, tên thuốc biệt dược hay chuỗi input thô. | unit |
| AC2 | Given input khác nhau ở đúng một trong: bữa ăn, hoạt chất, bệnh nền, thực phẩm cần tránh, dị ứng, hạn chế, sở thích, `PROMPT_VERSION`, When tính key, Then key khác nhau. | unit |
| AC3 | Given cache trống, When patient có consent gọi tạo gợi ý, Then LLM được gọi đúng 1 lần, trả 201, Redis có key `meal_cache:*` với TTL > 0 và ≤ TTL cấu hình, và dòng `meal_suggestions` mới có `served_from_cache = false`. | integration |
| AC4 | Given cache đã có entry cho tổ hợp input X, When một patient khác (hoặc cùng patient) có input X gọi tạo gợi ý, Then LLM không được gọi, trả 201 cùng hình dạng response, có disclaimer, có dòng `access_logs` cho request, và dòng `meal_suggestions` mới của đúng patient đó có `served_from_cache = true`. | integration |
| AC5 | Given patient đã có gợi ý được cache, When thêm/ngưng một thuốc (đổi hoạt chất) hoặc đổi bệnh nền rồi gọi lại, Then là cache miss: LLM được gọi, và gọi lại với dữ liệu cũ (hoàn tác thay đổi) trong TTL thì hit entry cũ. | integration |
| AC6 | Given entry cache đã lưu, When danh mục quy tắc thuốc–thực phẩm đổi làm danh sách thực phẩm cần tránh của patient đổi, Then là cache miss; và món trong output (kể cả output lấy từ cache) chứa thực phẩm cần tránh hiện tại hoặc tên thuốc vẫn bị lọc như output mới từ LLM. | integration |
| AC7 | Given LLM trả output không parse/validate được, When tạo gợi ý, Then trả 502 `llm_invalid_output` như hiện hành và không có key nào được ghi vào cache; `LlmUnavailable` → 503, không ghi cache. | unit |
| AC8 | Given Redis không kết nối được, timeout, hoặc từ chối lệnh ở bước đọc hoặc ghi, When tạo gợi ý, Then vẫn gọi LLM và trả 201, không lộ lỗi cache ra response; thời gian chờ Redis mỗi lệnh bị giới hạn (timeout cấu hình, mặc định ≤ 1 giây) để không vượt ngân sách 10 giây của PB37. | unit + integration (dừng Redis / URL sai) |
| AC9 | Given entry cache khớp input của patient, When người thân, admin, người đang chờ xóa, hoặc chính patient đã rút consent `ai_meal` gọi tạo gợi ý, Then trả 403, có dòng `denied` trong `access_logs`, cache không bị đọc và LLM không được gọi. | integration |
| AC10 | Given request gợi ý lại có `previous_suggestion_id` hợp lệ, When tạo gợi ý, Then không đọc và không ghi cache; LLM được gọi như hiện hành. | unit |
| AC11 | Given URL cache rỗng (mặc định), When tạo gợi ý, Then hành vi giống hệt hiện tại, không mở kết nối Redis, `served_from_cache = false`. | unit |
| AC12 | Given entry cache hỏng (không phải JSON hợp lệ theo parser), When hit, Then coi như miss: gọi LLM, trả 201, ghi đè entry bằng output hợp lệ mới. | unit |
| AC13 | Given mỗi request đi qua cache, When xảy ra hit, miss hoặc lỗi cache, Then có một dòng log sự kiện (`hit` / `miss` / `error` + loại lỗi), không chứa cache key, `user_id`, nội dung gợi ý hay URL/credential Redis. | unit |

## 8. Câu hỏi mở

Q1 [không chặn] TTL của entry cache là bao nhiêu?
- Ảnh hưởng: chi phí LLM ↔ độ mới gợi ý; giá trị kiểm trong AC3.
- Lựa chọn: 7 ngày / 1 ngày / khác
- Giả định mặc định: 7 ngày (đề xuất CD10 §7), cấu hình được qua biến môi trường.

Q2 [không chặn] Số biến thể N mỗi key?
- Ảnh hưởng: N > 1 cần lưu danh sách, chọn ngẫu nhiên/xoay vòng và lấp N lần gọi LLM mỗi key.
- Lựa chọn: N = 1 / N = 2
- Giả định mặc định: N = 1 (đơn giản nhất; người dùng muốn món khác thì đã có "gợi ý lại" của 5.11, vốn bỏ qua cache).

Q3 [không chặn] Gợi ý lại (`previous_suggestion_id`) có dùng cache không?
- Ảnh hưởng: prompt gợi ý lại chứa danh sách món đã gợi ý nên gần như không bao giờ trùng; cache lại chỉ tốn lệnh ghi Upstash.
- Lựa chọn: bỏ qua cache hoàn toàn / tra và ghi như lần đầu
- Giả định mặc định: bỏ qua cache hoàn toàn (AC10).

Q5 [không chặn] Dùng chung `REDIS_URL` hiện có hay biến riêng cho cache?
- Ảnh hưởng: CD10 tách cache (Upstash) khỏi broker; dùng chung làm cache tranh bộ nhớ với Redis local/khác.
- Lựa chọn: biến riêng `MEAL_CACHE_URL` (rỗng = tắt) / dùng `REDIS_URL`
- Giả định mặc định: biến riêng `MEAL_CACHE_URL`, rỗng = tắt cache (AC11); thêm `MEAL_CACHE_TTL_SECONDS`.

## 9. Giả định

- (Q4, người dùng chốt 2026-11-25) Cache key = `meal_cache:` + hash toàn bộ input đã tối thiểu hóa mà prompt dùng (bữa ăn, hoạt chất, bệnh nền, thực phẩm cần tránh, dị ứng, hạn chế, sở thích) + `PROMPT_VERSION` (AC1, AC2). Rộng hơn danh sách trong CD10; cần ghi chú vào tài liệu CD10.
- Phần "LLM API integration (prompt + parsing)" của PB37 đã xong ở 4.26/5.03/5.11; 5.09 còn lại là cache CD10.
- Cache lưu raw text LLM trả về (chuỗi JSON), không lưu kết quả đã lọc hay `image_id`; parse + lọc + ảnh chạy lại mỗi lần phục vụ.
- Không cần migration: `served_from_cache` đã có ở schema.
- Cache value không chứa định danh vì output LLM chỉ sinh từ prompt đã tối thiểu hóa (QD-41).
- Test tích hợp dùng Redis local (cùng instance `supabase start` / Redis dev), không gọi Upstash thật.

## 10. Phát sinh

- Tài liệu CD10 ghi thành phần key thiếu dị ứng/hạn chế/sở thích so với prompt thực tế; đã chốt key dùng toàn bộ input (Q4), cần cập nhật tài liệu kiến trúc.
- Hook doctor báo `backend`, `docs`, `api_contract` đang checkout commit khác con trỏ superproject; cần xử lý (skill `wf-git`) trước khi implement.
- `scope.py --stage requirement` báo `frontend/mobile/tool/preview_dose_reminder.dart` ngoài phạm vi: file thay đổi sẵn có từ task reminder trên nhánh hiện tại, không do task này tạo; cần commit/stash ở task kia trước khi bắt đầu nhánh 5.09.
- Nhánh hiện tại là `fix/adhoc-20261120-reminder-notification-dedup`; task này cần nhánh `feat/5.09-meal-llm-cache` ở superproject và `backend`.

## 11. Size

- `size`: M
- Lý do: một submodule (`backend`), không migration, không đổi contract; nhưng chạm vùng dữ liệu sức khỏe, consent và bí mật nên không được xếp S.

## Bước tiếp theo

- Đang chờ: người duyệt; Q1, Q2, Q3, Q5 không chặn, theo giả định mặc định nếu không có ý kiến khác.
- Việc cần làm: sau khi chốt, người duyệt chạy `python .agents/scripts/gate.py approve 5.09-meal-llm-cache requirement`; sau đó giai đoạn plan (`wf-plan`).
- Cập nhật lần cuối: 2026-11-25, Claude Code
