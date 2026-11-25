---
task: 5.09-meal-llm-cache
stage: implement
owner: Ngọc Việt
started_at: 2026-11-25 10:40
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 10:29 +0700
content_hash: sha256:e774dbb9dc8e187b
inputs:
  01-requirement.md: sha256:26efb8072acdc0bc
  03-plan.md: sha256:f2192e480440f867
---

# 5.09-meal-llm-cache · Implement

## 1. Tiến độ

Mọi lệnh chạy trong `backend/` bằng `.venv/Scripts/python.exe`.

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `pytest tests/unit/test_ai_meal_config_log.py` → 6 passed | `evidence/implement-P1.log` |
| P2 | xong | `pytest tests/unit/test_ai_meal_cache_key.py` → 12 passed (trước khi sửa công thức: AC1 fail, xem §6) | `evidence/implement-P2.log` |
| P3 | xong | `pytest tests/unit -k meal` → 341 passed, 1 skipped | `evidence/implement-P3.log` |
| P4 | xong | `pytest tests/unit/test_ai_meal_redis_cache.py` → 13 passed | `evidence/implement-P4.log` |
| P5 | xong | `pytest tests/unit/test_ai_meal_suggest_use_case.py` → 38 passed | `evidence/implement-P5.log` |
| P6 | xong | `pytest tests/unit/test_ai_meal_http.py tests/unit/test_contract_ai_meal.py` → 52 passed | `evidence/implement-P6.log` |
| P7 | để giai đoạn test | File thuộc vùng `integration-test` (`backend/tests/integration`) | — |
| P8 | để giai đoạn test | File thuộc vùng `integration-test` | — |
| P9 | xong (phần unit) | ruff trên file của task: pass; `pytest tests/unit tests/architecture` → 2532 passed, 35 failed (đều có sẵn trên `main`, xem §3); integration ở giai đoạn test | `evidence/implement-final-backend.log` |

### Quy tắc / AC đã thực hiện

| AC | Hiện thực | Test unit |
|---|---|---|
| AC1, AC2 | `domain/cache_key.py` | `test_ai_meal_cache_key.py` (12) |
| AC3 | `RedisMealCache.put` `SET ... EX ttl`; TTL ≤ 0 bị từ chối; use case ghi sau parse | `test_put_sets_ttl__AC3`, `test_non_positive_ttl_rejected__AC3`, `test_cache_miss_calls_llm_then_puts_raw__5_09_AC3` |
| AC4 | hit bỏ qua LLM, `served_from_cache=True` | `test_cache_hit_skips_llm_served_from_cache_true__5_09_AC4`, `test_sql_store_writes_served_from_cache__5_09_AC4` |
| AC6 | output từ cache parse + lọc với prompt hiện tại | `test_cache_hit_output_refiltered_with_current_prompt__5_09_AC6` |
| AC7 | lỗi LLM lan ra trước `put` | `test_invalid_llm_output_not_cached__5_09_AC7`, `test_unavailable_llm_not_cached__5_09_AC7` |
| AC8 | `RedisError` → None / bỏ qua; client không retry, timeout cấu hình | `test_get_error_returns_none_and_logs_kind__AC8_AC13`, `test_put_error_swallowed_and_logged__AC8_AC13`, `test_client_built_without_retry_and_with_timeout__AC8` |
| AC9 | cache chỉ chạm sau `access.authorize` | `test_forbidden_never_touches_cache__5_09_AC9` |
| AC10 | gợi ý lại không gọi cache (`bypass`) | `test_refresh_bypasses_cache__5_09_AC10` |
| AC11 | `get_meal_cache()` None khi URL rỗng | `test_get_meal_cache_none_when_url_empty__5_09_AC11`, `test_no_cache_behaves_as_before__5_09_AC11`, `test_no_cache_event_logged_when_off__5_09_AC11` |
| AC12 | entry parse lỗi → `corrupt`, gọi LLM, ghi đè | `test_corrupt_entry_treated_as_miss_and_overwritten__5_09_AC12` |
| AC13 | log `ai_meal cache event=<hit/miss/corrupt/bypass>` ở HTTP; `event=error op kind` ở adapter | `test_cache_event_logged_without_identifiers__5_09_AC13`, `test_log_has_no_key_url_or_value__AC13` |
| AC5, AC6 (tích hợp), AC9 (tích hợp) | — | giai đoạn test (P8) |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/shared/config.py` |
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/modules/ai_meal/domain/cache_key.py` (mới) |
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/modules/ai_meal/application/ports.py` |
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/modules/ai_meal/application/suggest_meals.py` |
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/modules/ai_meal/adapters/outbound/redis_meal_cache.py` (mới) |
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/modules/ai_meal/adapters/outbound/sql_meal_suggestions.py` |
| backend | `feat/5.09-meal-llm-cache` | `src/drugtime/modules/ai_meal/adapters/inbound/http.py` |
| backend | `feat/5.09-meal-llm-cache` | `tests/unit/test_ai_meal_cache_key.py` (mới), `tests/unit/test_ai_meal_redis_cache.py` (mới), `tests/unit/test_ai_meal_suggest_use_case.py`, `tests/unit/test_ai_meal_http.py`, `tests/unit/test_ai_meal_config_log.py` |

Kết quả `python .agents/scripts/scope.py 5.09-meal-llm-cache --stage implement`: 12 file `[OK]`; 1 file `[NGOÀI]` là `frontend/mobile/tool/preview_dose_reminder.dart` — không do task này tạo (xem §6) — log: `evidence/implement-scope.log`

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| backend | `ruff check` trên 12 file của task | pass | `evidence/implement-final-backend.log` |
| backend | `ruff check .` | 69 lỗi, không lỗi nào ở file của task (catalog, OCR, integration family/alert…) | `evidence/implement-final-backend.log` |
| backend | `pytest tests/unit tests/architecture` | 2532 pass / 35 fail / 1 skip; architecture pass | `evidence/implement-final-backend.log` |
| backend | Đối chứng: 9 file fail chạy trên `main` sạch (stash thay đổi của task) | 35 fail giống hệt; 0 fail mới do task | `evidence/implement-baseline-main.log` |

35 fail có sẵn: `test_contract_{consent,device_tokens,medication,notification,openapi_semantics,patient_switcher,profile}.py`, `test_deletion_creation_http.py`, `test_deletion_lifecycle.py`. Các test contract so với `../api_contract/openapi.json`, mà submodule `api_contract` đang checkout nhánh `feat/adhoc-20261118-health-profile-catalog` lệch con trỏ superproject.

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test.

## 4. Migration

Không có. Cột `served_from_cache` đã có ở schema.

## 5. Ghi chú cho người review

- Cache đặt trong use case (`_first_suggestions`), sau `access.authorize`; không phải cache quyết định quyền. Output từ cache vẫn qua `parse_suggestions` với prompt hiện tại nên lọc thực phẩm cần tránh/dị ứng/tên thuốc chạy lại; ảnh và disclaimer chạy như cũ.
- Gọi Redis nằm trong transaction DB (như LLM). Với timeout 1 giây và không retry, tối đa ~2 giây thêm khi Upstash treo.
- `get_meal_cache` tạo client qua `lru_cache` theo (url, ttl, timeout); URL là tham số của cache trong bộ nhớ tiến trình, không bị log.
- `_client` trong `test_ai_meal_http.py` luôn override `get_meal_cache` (mặc định None) để unit test không phụ thuộc `.env`.
- Venv `backend/.venv` thiếu nhóm dev; đã cài `ruff`, `import-linter` (khai báo trong `[dependency-groups] dev`) bằng `uv pip install` để chạy lint và test architecture.

## 6. Phát sinh

- **Lệch nhỏ so với plan P2 (công thức key)**: plan ghi `sha256([version, system, user])`, nhưng chính điều kiện "xong khi" của P2 / AC1 (hoa thường → cùng key) fail với công thức đó vì `clean_list` giữ cách viết hoa của người dùng ("Tôm" ≠ "tôm" trong prompt). Đã sửa thành băm `user.casefold()` (chỉ bỏ hoa thường, giữ dấu: "Cá" ≠ "Cà", có test). Không đổi file, chữ ký hay AC. Log fail trước khi sửa nằm trong lịch sử phiên; log pass: `evidence/implement-P2.log`.
- **Lệch nhỏ so với plan P4 (chữ ký adapter)**: plan ghi `RedisMealCache(url, ttl, timeout, client=None)`; hiện thực là `RedisMealCache(client, ttl)` + hàm `build_client(url, timeout)` để test không cần URL thật. Hành vi như plan.
- **Quan sát ngoài phạm vi**: `clean_list` khử trùng theo `normalize()` (bỏ dấu), nên "Cá" và "Cà" trong cùng một danh sách dị ứng bị gộp làm một. Hành vi có từ 4.26, không thuộc 5.09; đề xuất mở bug riêng.
- `scope.py` báo `frontend/mobile/tool/preview_dose_reminder.dart` `[NGOÀI]`: thay đổi chưa commit của task reminder trong submodule `frontend`, có trước khi task này bắt đầu; không đụng tới. Cần người dùng xử lý (commit ở task reminder hoặc stash) để `scope.py` sạch.
- Nhánh: superproject và `backend` tạo `feat/5.09-meal-llm-cache` từ `origin/main` (backend `f350f40`); đang track `origin/main`, khi push dùng `git push -u origin feat/5.09-meal-llm-cache`.
- Superproject còn thay đổi con trỏ `api_contract`, `docs`, `frontend` không thuộc task; không đụng tới.
- 35 unit test contract/deletion fail có sẵn trên `main` (§3); 69 lỗi ruff có sẵn ở file khác.
- Tài liệu CD10 cần cập nhật thành phần key (Q4) và ghi chú casefold.

## Bước tiếp theo

- Đang chờ: người dùng quyết định về file `[NGOÀI]` của task reminder, rồi người duyệt.
- Việc cần làm: xử lý `frontend/mobile/tool/preview_dose_reminder.dart` (không thuộc task); người duyệt chạy `python .agents/scripts/gate.py approve 5.09-meal-llm-cache implement`; sau đó giai đoạn test (`wf-test`) làm P7, P8 với Redis local.
- Cập nhật lần cuối: 2026-11-25 11:40, Claude Code
