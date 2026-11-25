---
task: 5.09-meal-llm-cache
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-25 11:41 +0700
content_hash: sha256:584f3e2b1dd5bc66
inputs:
  01-requirement.md: sha256:26efb8072acdc0bc
  03-plan.md: sha256:f2192e480440f867
  04-impl-notes.md: sha256:e774dbb9dc8e187b
---

# 5.09-meal-llm-cache · Test tích hợp

> **Giai đoạn test bị bỏ qua theo yêu cầu người dùng (2026-11-25).** Test tích hợp đã viết nhưng **chưa chạy**: máy không có Redis và Postgres local. Không có kết quả pass/fail nào trong báo cáo này. Người duyệt approve báo cáo này là chấp nhận rủi ro đó.

## 1. Môi trường

- Lệnh chuẩn bị: không chạy.
- Lý do:
  - Không có Redis ở `127.0.0.1:6379`.
  - WSL Ubuntu-22.04 không có `redis-server`.
  - Podman machine kẹt ở "Currently starting".
  - Không có Docker hay `supabase` CLI.
  - Postgres cổng 54322 không chạy.
- Nhánh của vùng test tích hợp: `backend` `feat/5.09-meal-llm-cache` (chưa commit).

## 2. Kết quả theo tiêu chí chấp nhận

Mọi test tích hợp nằm ở `backend/tests/integration/test_meal_suggestions_cache.py`. Ruff pass. Bằng chứng unit nằm ở `04-impl-notes.md` §1.

| AC | Test tích hợp | Kết quả | Đã có test unit? |
|---|---|---|---|
| AC3 | `test_miss_calls_llm_stores_with_ttl_served_false__AC3` | chưa chạy | có |
| AC4 | `test_hit_for_other_patient_same_input_no_llm__AC4`, `test_same_patient_repeat_hits__AC4` | chưa chạy | có |
| AC5 | `test_condition_change_misses_then_revert_hits__AC5`, `test_medication_added_misses__AC5` | chưa chạy | **không**; chỉ có unit key (AC2) |
| AC6 | `test_food_rule_change_misses_and_new_avoid_food_filtered__AC6` | chưa chạy | có (lọc lại output) |
| AC8 | `test_redis_unreachable_still_200__AC8` | chưa chạy | có |
| AC9 | `test_denied_never_reads_cache_or_llm__AC9`, với 4 tham số: `consent_revoked`, `family_with_full_consent`, `admin`, `other_patient` | chưa chạy | có (HTTP, store giả) |
| AC10 | `test_refresh_bypasses_cache__AC10` | chưa chạy | có |
| AC13 | `test_cache_events_logged__AC13` | chưa chạy | có |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Truy cập chéo patient, hoặc không có liên kết/consent → 403 và dòng `denied` | `test_denied_never_reads_cache_or_llm__AC9[other_patient, family_with_full_consent, admin]` | chưa chạy |
| Rút consent rồi gửi request ngay → 403 | `test_denied_never_reads_cache_or_llm__AC9[consent_revoked]` | chưa chạy |

## 4. Toàn bộ bộ test tích hợp

- Lệnh: không chạy.
- Kết quả: không có.
- Log: không có `evidence/test-integration.log`.
- `scope.py --stage test`: 2 file test tích hợp `[OK]`. 12 file `[NGOÀI]` là file của giai đoạn implement đã duyệt; chúng còn trong diff vì chưa commit, giai đoạn này không sửa chúng. Log: `evidence/test-scope.log`.

## 5. Bộ test case Excel

Bỏ qua cùng giai đoạn test: chưa có `testcases.json` hay `testcases.xlsx`, và chưa gộp vào file tổng.

## 5b. Lỗi sản phẩm tìm thấy

Không có kết luận vì chưa chạy test.

## 6. Test không ổn định hoặc bị skip

Toàn bộ 13 test tích hợp mới chưa chạy. Bộ test tích hợp có sẵn cũng chưa chạy, gồm `test_meal_suggestions_api.py` sau khi thêm `MEAL_CACHE_URL=""` vào `disable_real_llm`.

## 7. Phát sinh

- Rủi ro còn lại khi bỏ test:
  - Chưa kiểm hành vi thật với Redis: TTL, `SET EX`, `decode_responses`.
  - Chưa kiểm việc lấy dữ liệu thuốc và bệnh nền từ DB thật vào key (AC5).
  - Chưa kiểm cột `served_from_cache` ghi thật xuống Postgres.
  - Chưa kiểm PEP cùng `access_logs` khi cache đang bật.
- Cách chạy về sau:
  - Bật Redis (đặt `TEST_REDIS_URL`) và Postgres (đặt `TEST_ADMIN_DATABASE_URL`).
  - Chạy `cd backend && .venv/Scripts/python.exe -m pytest tests/integration/test_meal_suggestions_cache.py tests/integration`.
- Fixture `redis` cố ý gọi `pytest.fail` chứ không skip khi Redis tắt. Vì vậy CI không có Redis sẽ báo đỏ cho 13 test này.

## Bước tiếp theo

- Đang chờ người duyệt.
- Việc cần làm:
  - Nếu chấp nhận bỏ test, người duyệt chạy `python .agents/scripts/gate.py approve 5.09-meal-llm-cache test`, rồi sang `wf-review`.
  - Nếu muốn chạy test, `gate.py reopen` không cần vì file đang ở `draft`: bật Redis/Postgres rồi bảo agent chạy tiếp.
- Cập nhật lần cuối: 2026-11-25 11:41, Claude Code
