---
task: 5.09-meal-llm-cache
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 10:13 +0700
content_hash: sha256:f2192e480440f867
inputs:
  01-requirement.md: sha256:26efb8072acdc0bc
---

# 5.09-meal-llm-cache · Plan

## 1. Giải pháp

Cache-aside nội dung (không phải cache quyết định phân quyền) đặt **trong use case** `suggest_meals`, sau PEP và sau khi dựng prompt, trước `suggester.suggest`.

Luồng gợi ý lần đầu (`previous_suggestion_id is None`) khi cache bật:

```
authorize (PEP, access_logs) → khai báo → suggester None? → đếm lượt → food/conditions → build_prompt
→ key = cache_key(prompt)
→ raw = cache.get(key)                         # adapter fail-open: lỗi Redis → None
→ raw có: parse_suggestions(raw, prompt hiện tại)
     ok  → cache_status = "hit"  (không gọi LLM)
     LlmInvalidOutput → cache_status = "corrupt", coi như miss
→ chưa có kết quả: raw = suggester.suggest(prompt); result = parse_suggestions(raw, prompt)
     (LlmUnavailable / LlmInvalidOutput lan ra như hiện tại → không ghi cache)
     cache.put(key, raw)                       # chỉ sau khi parse thành công; adapter fail-open
→ ảnh → store.insert(..., served_from_cache = cache_status == "hit")
```

- Gợi ý lại (`previous_suggestion_id`): không gọi `cache.get/put` (`cache_status = "bypass"`).
- `cache = None` (URL rỗng): luồng giữ nguyên như hiện tại (`cache_status = "off"`).
- **Cache key** (`domain/cache_key.py`): `"meal_cache:" + sha256(json.dumps([prompt.version, prompt.system, prompt.user]))`. `prompt.user` là JSON `sort_keys` của input đã tối thiểu hóa (bữa ăn, hoạt chất, bệnh nền, thực phẩm cần tránh, dị ứng, hạn chế, sở thích, `phien_ban_prompt`) — đúng quyết định Q4. Tên biệt dược (`drug_names`) không có trong `prompt.user` nên không vào key; chúng chỉ dùng lọc output, và lọc luôn chạy lại khi phục vụ. Hash cả `system` để sửa prompt mà quên tăng `PROMPT_VERSION` vẫn không dùng output cũ.
- Cache lưu raw text LLM; parse + lọc thực phẩm cần tránh/dị ứng/tên thuốc + ảnh + disclaimer chạy lại mỗi lần phục vụ (CD10).
- **Adapter** `RedisMealCache` (`adapters/outbound/redis_meal_cache.py`): `redis.Redis.from_url(url, socket_timeout=t, socket_connect_timeout=t, retry=Retry(NoBackoff(), 0), decode_responses=True)`; `get` = `GET`, `put` = `SET key raw EX ttl`. Bắt `redis.RedisError` (kết nối, timeout, từ chối lệnh do quota) → `get` trả None / `put` bỏ qua, log `ai_meal cache event=error op=<get|set> kind=<tên lớp exception>`. Không log key, URL, nội dung.
- **DI** (`adapters/inbound/http.py`): `get_meal_cache() -> MealCache | None`, None khi `meal_cache_url` rỗng; client tạo một lần qua `lru_cache` như `_claude`. Endpoint log `ai_meal cache event=<hit|miss|corrupt|bypass>` từ `outcome.cache_status` (không log khi `off`).
- **Cấu hình** (`shared/config.py`): `meal_cache_url: SecretStr = ""` (chứa token Upstash), `meal_cache_ttl_seconds: int = 604800` (7 ngày, Q1), `meal_cache_timeout_seconds: float = 1.0`.

Cách bỏ: decorator quanh port `MealSuggester` (CD8 gợi ý). Bỏ vì decorator không biết output đã parse thành công hay chưa (AC7, AC12), không phân biệt gợi ý lại (AC10), và không báo được `served_from_cache` lên use case (AC3, AC4) mà không parse hai lần.

Bất biến: PEP vẫn đứng đầu (bất biến 2); cache không chứa quyết định phân quyền (bất biến 4); key và value không có định danh; không đổi API, không migration.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/5.09-meal-llm-cache/01-requirement.md` (approved) | AC1–AC13, Q4 chốt key = toàn bộ input + `PROMPT_VERSION`; Q1/Q2/Q3/Q5 theo mặc định: TTL 7 ngày, N = 1, gợi ý lại bỏ qua cache, biến `MEAL_CACHE_URL` riêng. |
| `docs/Team1_DTU/03_Design/Architecture/DrugTime – Bổ sung kiến trúc Job Queue (RabbitMQ) + LLM Cache v4.1_1.md` §3, §4, §5, §7 | CD10 (bản bổ sung v4.1, chưa ghi trạng thái duyệt): cache-aside, chỉ cache output đã validate, TTL bắt buộc, fail-open, consent trước cache, kiểm tra an toàn chạy lại. TTL/N chưa chốt ở nguồn. |
| `.agents/skills/wf-health-endpoint/SKILL.md` | Checklist 1–9; mục 4 "không cache quyết định" — cache ở đây là nội dung LLM sau PEP, không phải quyết định quyền; phải test cache không được chạm khi bị từ chối. |
| `backend/src/drugtime/modules/ai_meal/application/suggest_meals.py` | Thứ tự hiện tại và điểm chèn (dòng 174–183). `store.insert` chỉ gọi ở đây. |
| `backend/src/drugtime/modules/ai_meal/application/ports.py` | Pattern Protocol cho port; thêm `MealCache`. |
| `backend/src/drugtime/modules/ai_meal/domain/prompt.py` | `MealPrompt(version, system, user, ...)`, `PROMPT_VERSION = "meal-v2"`, `user` = JSON `sort_keys`; `drug_names` không vào prompt. |
| `backend/src/drugtime/modules/ai_meal/domain/model.py` | `clean_list` chuẩn hóa thứ tự/hoa thường/khoảng trắng → AC1 có sẵn qua prompt. |
| `backend/src/drugtime/modules/ai_meal/domain/parser.py` | `parse_suggestions(raw, prompt, ...)` raise `LlmInvalidOutput` khi JSON/schema sai. |
| `backend/src/drugtime/modules/ai_meal/adapters/inbound/http.py` | DI qua `Depends` + `lru_cache` (`_claude`); ánh xạ lỗi 502/503; log chỉ mã lý do. |
| `backend/src/drugtime/modules/ai_meal/adapters/outbound/sql_meal_suggestions.py` | `served_from_cache` đang hard-code `false`. |
| `backend/src/drugtime/shared/config.py` | Pattern `SecretStr` cho key; `redis_url` hiện dùng cho health, không dùng lại (Q5). |
| `backend/pyproject.toml`, `pip show redis` | `redis>=5.0` đã có (bản cài 8.1.0); redis-py ≥ 6 mặc định retry → phải tắt để giới hạn độ trễ. |
| `backend/tests/unit/test_ai_meal_suggest_use_case.py` | Fake `FakeSuggester`, `FakeStore`, `Calls`, helper `run(...)` — mở rộng thêm `FakeCache`. |
| `backend/tests/unit/test_ai_meal_http.py`, `test_ai_meal_config_log.py` | Test DI/ánh xạ lỗi; `test_settings_repr_hides_secrets__AC9` cho secret. |
| `backend/tests/integration/test_meal_suggestions_api.py`, `test_meal_suggestions_access.py` | `disable_real_llm` (autouse) ép env; `install_fake_llm`, `create_patient`, `add_condition`, `add_rule`, `add_med`, `make.revoke_consent`, `make.access_logs`. |

### Quyết định nghiệp vụ áp dụng

| Quy tắc (nguồn) | Trạng thái nguồn | AC | Bước | Test |
|---|---|---|---|---|
| Key `meal_cache:` + hash input ẩn danh + phiên bản prompt, không định danh (CD10 §3 "Cache key"; mở rộng theo Q4 ở `01` §9) | Bản bổ sung v4.1; Q4 do người dùng chốt | AC1, AC2 | P2 | `test_ai_meal_cache_key.py` |
| Hit dùng lại output, miss gọi LLM (CD10 §3 "Mô tả", §4) | Bản bổ sung v4.1 | AC3, AC4 | P5, P6 | unit use case; integration miss/hit |
| Chỉ lưu output đã validate, kèm TTL (CD10 §3, §5 "Cache") | Bản bổ sung v4.1 | AC3, AC7, AC12 | P4, P5 | unit adapter TTL, use case invalid/corrupt; integration TTL |
| Kiểm tra thuốc–thức ăn + disclaimer chạy lại khi phục vụ (CD10 §3, §4) | Bản bổ sung v4.1 | AC4, AC6 | P5 | unit lọc trên hit; integration rule đổi |
| Đổi thuốc/bệnh/danh mục → key đổi (CD10 §3 "Cache key") | Bản bổ sung v4.1 | AC5, AC6 | P2, P5 | integration AC5, AC6 |
| Fail-open (CD10 §3, R-09) | Bản bổ sung v4.1 | AC8 | P4 | unit adapter lỗi; integration URL sai |
| Consent `ai_meal` chặn trước cache (CD10 §3 "Đánh đổi", §6 mục 5.09) | Bản bổ sung v4.1 | AC9 | P5 | unit forbidden; integration 403 + spy |
| `served_from_cache` trong `meal_suggestions` (CD10 §6 Schema v8) | Bản bổ sung v4.1; cột đã có ở schema v11 | AC3, AC4 | P3, P5 | integration đọc cột |
| TTL, N (CD10 §7) | **Chưa chốt ở nguồn**; `01` theo mặc định 7 ngày, N = 1 | AC3 | P1 | cấu hình được, không hard-code |

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule; được dùng glob, ví dụ `src/<module>/auth/**`. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| backend | `src/drugtime/shared/config.py` | sửa | `meal_cache_url` (SecretStr), `meal_cache_ttl_seconds`, `meal_cache_timeout_seconds` |
| backend | `src/drugtime/modules/ai_meal/domain/cache_key.py` | thêm | Hàm thuần `cache_key(prompt) -> str` |
| backend | `src/drugtime/modules/ai_meal/application/ports.py` | sửa | Protocol `MealCache.get/put` |
| backend | `src/drugtime/modules/ai_meal/application/suggest_meals.py` | sửa | Chèn cache-aside, `cache_status` trong `MealOutcome`, truyền `served_from_cache` |
| backend | `src/drugtime/modules/ai_meal/adapters/outbound/redis_meal_cache.py` | thêm | Adapter Redis fail-open, TTL, timeout, không retry |
| backend | `src/drugtime/modules/ai_meal/adapters/outbound/sql_meal_suggestions.py` | sửa | Tham số `served_from_cache` thay cho `false` cố định |
| backend | `src/drugtime/modules/ai_meal/adapters/inbound/http.py` | sửa | `get_meal_cache()` DI, truyền vào use case, log `cache event` |
| backend | `tests/unit/test_ai_meal_cache_key.py` | thêm | AC1, AC2 |
| backend | `tests/unit/test_ai_meal_redis_cache.py` | thêm | AC3 (TTL), AC8, AC13 với client giả |
| backend | `tests/unit/test_ai_meal_suggest_use_case.py` | sửa | `FakeCache`; AC4, AC6, AC7, AC9, AC10, AC11, AC12 |
| backend | `tests/unit/test_ai_meal_http.py` | sửa | `get_meal_cache` None khi URL rỗng (AC11); log event (AC13) |
| backend | `tests/unit/test_ai_meal_config_log.py` | sửa | `meal_cache_url` không lộ trong repr/dump |
| backend | `tests/integration/test_meal_suggestions_api.py` | sửa | `disable_real_llm` ép `MEAL_CACHE_URL=""` để test cũ không phụ thuộc `.env` |
| backend | `tests/integration/test_meal_suggestions_cache.py` | thêm | AC3, AC4, AC5, AC6, AC8, AC9, AC13 với Redis local thật |

## 4. Checklist

- [ ] P1 [backend] Thêm 3 setting `meal_cache_url: SecretStr = SecretStr("")`, `meal_cache_ttl_seconds: int = 604800`, `meal_cache_timeout_seconds: float = 1.0` — file: `src/drugtime/shared/config.py`, `tests/unit/test_ai_meal_config_log.py` — AC: AC11 — xong khi: test repr/model_dump không chứa giá trị URL đặt thử pass.
- [ ] P2 [backend] Viết `cache_key(prompt)` = `"meal_cache:" + sha256(json.dumps([version, system, user], ensure_ascii=False))` — file: `src/drugtime/modules/ai_meal/domain/cache_key.py`, `tests/unit/test_ai_meal_cache_key.py` — AC: AC1, AC2 — xong khi: test thứ tự/hoa thường/khoảng trắng → cùng key; đổi từng trường trong 7 trường + version → key khác; key không chứa tên thuốc biệt dược, chuỗi input hay UUID — pass.
- [ ] P3 [backend] Thêm tham số `served_from_cache: bool = False` cho `MealSuggestionStore.insert` và `SqlMealSuggestions.insert` (bind `:s` thay `false`) — file: `src/drugtime/modules/ai_meal/application/ports.py`, `src/drugtime/modules/ai_meal/adapters/outbound/sql_meal_suggestions.py` — AC: AC3, AC4 — xong khi: unit hiện có vẫn pass; integration đọc được cột (P8).
- [ ] P4 [backend] Thêm Protocol `MealCache` (`get(key) -> str | None`, `put(key, raw) -> None`, không raise) và adapter `RedisMealCache(url, ttl, timeout, client=None)`: `retry=Retry(NoBackoff(), 0)`, `socket_timeout`/`socket_connect_timeout = timeout`; bắt `RedisError` → None/bỏ qua + log `event=error op kind`; `put` dùng `SET ... EX ttl` — file: `src/drugtime/modules/ai_meal/application/ports.py`, `src/drugtime/modules/ai_meal/adapters/outbound/redis_meal_cache.py`, `tests/unit/test_ai_meal_redis_cache.py` — AC: AC3, AC8, AC13 — xong khi: test với client giả: `set` nhận `ex=ttl`; `ConnectionError`/`TimeoutError`/`ResponseError` ở get → None, ở set → không raise; log không chứa key/URL/giá trị; client thật được tạo với retry 0 và timeout cấu hình — pass.
- [ ] P5 [backend] Sửa `suggest_meals`: tham số `cache: MealCache | None = None`; luồng lần đầu theo §1 (get → parse trên prompt hiện tại → corrupt coi như miss → LLM → parse → put); gợi ý lại không gọi cache; `MealOutcome.cache_status: str = "off"`; `store.insert(..., served_from_cache=cache_status == "hit")` — file: `src/drugtime/modules/ai_meal/application/suggest_meals.py`, `tests/unit/test_ai_meal_suggest_use_case.py` — AC: AC4, AC6, AC7, AC9, AC10, AC11, AC12 — xong khi: các test unit ở §5 pass và toàn bộ test use case cũ vẫn pass.
- [ ] P6 [backend] Thêm `get_meal_cache()` (None khi URL rỗng; client `lru_cache` theo (url, ttl, timeout)), truyền `cache=` vào `suggest_meals`, log `ai_meal cache event=<status>` khi status ≠ `off` — file: `src/drugtime/modules/ai_meal/adapters/inbound/http.py`, `tests/unit/test_ai_meal_http.py` — AC: AC11, AC13 — xong khi: test DI trả None với URL rỗng và không tạo client; test log event pass; OpenAPI export không đổi (`test_contract_ai_meal.py` pass).
- [ ] P7 [backend] Thêm `monkeypatch.setenv("MEAL_CACHE_URL", "")` vào `disable_real_llm` — file: `tests/integration/test_meal_suggestions_api.py` — AC: AC11 — xong khi: bộ integration meal cũ pass dù `.env` dev có URL cache.
- [ ] P8 [backend] Viết test tích hợp cache với Redis local (`redis://127.0.0.1:6379/15`, xóa key `meal_cache:*` bằng SCAN trước/sau mỗi test; fixture báo lỗi rõ nếu Redis không chạy), override `get_meal_cache` bằng `SpyCache` bọc `RedisMealCache` thật để đếm get/put — file: `tests/integration/test_meal_suggestions_cache.py` — AC: AC3, AC4, AC5, AC6, AC8, AC9, AC13 — xong khi: các test tích hợp ở §5 pass, log lưu ở `work/5.09-meal-llm-cache/evidence/`.
- [ ] P9 [backend] Chạy `ruff check .`, `pytest tests/unit tests/architecture`, `pytest tests/integration` — file: (không sửa file) — AC: tất cả — xong khi: pass, log ở `evidence/implement-*.log`.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `test_ai_meal_cache_key.py::test_same_key_regardless_of_order_case_whitespace` | AC1 | backend |
| `test_ai_meal_cache_key.py::test_key_prefix_and_no_identifiers_or_brand_names` | AC1 | backend |
| `test_ai_meal_cache_key.py::test_key_changes_per_field` (parametrize 7 trường + `PROMPT_VERSION`) | AC2 | backend |
| `test_ai_meal_redis_cache.py::test_put_sets_ttl` | AC3 | backend |
| `test_ai_meal_redis_cache.py::test_get_error_returns_none_and_logs_kind` (parametrize ConnectionError, TimeoutError, ResponseError) | AC8, AC13 | backend |
| `test_ai_meal_redis_cache.py::test_put_error_swallowed_and_logged` | AC8, AC13 | backend |
| `test_ai_meal_redis_cache.py::test_log_has_no_key_url_or_value` | AC13 | backend |
| `test_ai_meal_redis_cache.py::test_client_built_without_retry_and_with_timeout` | AC8 | backend |
| `test_ai_meal_suggest_use_case.py::test_cache_miss_calls_llm_then_puts_raw` | AC3 | backend |
| `test_ai_meal_suggest_use_case.py::test_cache_hit_skips_llm_served_from_cache_true` | AC4 | backend |
| `test_ai_meal_suggest_use_case.py::test_cache_hit_output_refiltered_with_current_prompt` (món chứa tên thuốc/thực phẩm cần tránh hiện tại bị lọc) | AC6 | backend |
| `test_ai_meal_suggest_use_case.py::test_invalid_or_unavailable_llm_not_cached` | AC7 | backend |
| `test_ai_meal_suggest_use_case.py::test_forbidden_never_touches_cache` | AC9 | backend |
| `test_ai_meal_suggest_use_case.py::test_refresh_bypasses_cache` | AC10 | backend |
| `test_ai_meal_suggest_use_case.py::test_no_cache_behaves_as_before` | AC11 | backend |
| `test_ai_meal_suggest_use_case.py::test_corrupt_entry_treated_as_miss_and_overwritten` | AC12 | backend |
| `test_ai_meal_http.py::test_get_meal_cache_none_when_url_empty` | AC11 | backend |
| `test_ai_meal_http.py::test_cache_event_logged_without_identifiers` | AC13 | backend |
| `test_ai_meal_config_log.py::test_settings_repr_hides_secrets__AC9` (mở rộng với `meal_cache_url`) | Bí mật | backend |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| `test_meal_suggestions_cache.py::test_miss_calls_llm_stores_with_ttl_served_false` | AC3 | Kiểm `TTL` key ∈ (0, ttl], cột `served_from_cache = false`, LLM 1 lần |
| `test_meal_suggestions_cache.py::test_hit_for_other_patient_same_input_no_llm` | AC4 | Patient thứ hai cùng thuốc/bệnh/khai báo; LLM không gọi; có `access_logs`, disclaimer; `served_from_cache = true` ở dòng của patient thứ hai |
| `test_meal_suggestions_cache.py::test_condition_change_misses_then_revert_hits` | AC5 | `add_condition` → miss; xóa bệnh nền → hit entry cũ |
| `test_meal_suggestions_cache.py::test_medication_added_misses` | AC5 | `add_med` cho patient → miss; patient mới không thêm thuốc → hit entry cũ |
| `test_meal_suggestions_cache.py::test_food_rule_change_misses` | AC6 | `add_rule` cho hoạt chất của patient → miss; món chứa thực phẩm mới bị lọc |
| `test_meal_suggestions_cache.py::test_redis_unreachable_still_201` | AC8 | `MEAL_CACHE_URL=redis://127.0.0.1:1/0`; LLM gọi, 201 |
| `test_meal_suggestions_cache.py::test_denied_never_reads_cache_or_llm` (parametrize: rút consent `ai_meal`, người thân đủ consent, admin, patient khác) | AC9; kịch bản "truy cập chéo → 403 + `denied`", "rút consent → 403 ngay request kế" | Cache đã có entry khớp; `SpyCache.gets == 0`, LLM 0 lần, dòng `denied` |
| `test_meal_suggestions_cache.py::test_cache_events_logged` (caplog) | AC13 | Có `event=miss` rồi `event=hit`, không có UUID/key |
| Bộ `test_meal_suggestions_api.py`, `test_meal_suggestions_access.py`, `test_meal_suggestions_refresh.py` hiện có | Hồi quy | Chạy lại toàn bộ |

## 6. Migration

Không có. Cột `meal_suggestions.served_from_cache` đã có (`backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql:384`).

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/5.09-meal-llm-cache` |
| backend | `feat/5.09-meal-llm-cache` |

## 8. Rủi ro

- **Độ trễ khi Upstash chậm**: redis-py ≥ 6 mặc định retry; không tắt thì một lệnh có thể chờ nhiều lần timeout, vượt ngân sách 10 giây của PB37. Giảm thiểu: `Retry(NoBackoff(), 0)`, timeout 1 giây, test P4 kiểm cấu hình client.
- **Lộ credential**: URL Upstash chứa password. Giảm thiểu: `SecretStr`, chỉ log tên lớp exception, test repr/log.
- **Entry cache bị sửa ngoài ý muốn** (Upstash bị xâm phạm): value đi qua parser + lọc an toàn như output LLM, nhưng văn bản mô tả món vẫn có thể sai lệch. Chấp nhận ở MVP; ghi vào DPIA (task 6.01).
- **Gọi Redis trong transaction DB**: thêm tối đa ~2 giây (2 lệnh × timeout) giữ transaction khi Upstash treo. LLM đã gọi trong transaction từ trước; chấp nhận.
- **Test tích hợp phụ thuộc Redis local**: thiếu Redis thì fixture báo lỗi rõ, không skip âm thầm. Dùng DB 15 và chỉ xóa key `meal_cache:*`.
- **Hit rate thấp** vì key gồm cả dị ứng/hạn chế/sở thích (Q4): chấp nhận vì an toàn; đo qua log `event`.

## 9. Câu hỏi mở

Không có. Q1, Q2, Q3, Q5 của `01` theo giả định mặc định.

## 10. Phát sinh

- Tài liệu CD10 (`docs/.../LLM Cache v4.1_1.md` §3 "Cache key") cần cập nhật thành phần key theo Q4; ngoài phạm vi submodule của task.
- `.env` mẫu/runbook cho `MEAL_CACHE_URL`, `MEAL_CACHE_TTL_SECONDS`, `MEAL_CACHE_TIMEOUT_SECONDS`: backend không có `.env.example`; thuộc runbook 6.20 / task 4.14.
- `scope.py` báo `frontend/mobile/tool/preview_dose_reminder.dart` (thay đổi chưa commit của task reminder trên nhánh hiện tại), không thuộc task này.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve 5.09-meal-llm-cache plan`; trước implement tạo nhánh `feat/5.09-meal-llm-cache` ở superproject và `backend` (skill `wf-git`), rồi `wf-implement` từ P1.
- Cập nhật lần cuối: 2026-11-25, Claude Code
