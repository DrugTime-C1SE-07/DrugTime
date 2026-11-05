---
task: 3.26-delete-links
title: Kế hoạch chuyển DELETE /links/{id} sang module family Hexagonal
stage: plan
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 14:34 +0700
content_hash: sha256:6cc904b55d5e24ed
inputs:
  01-requirement.md: sha256:e9780e264d8de972
---

# 3.26-delete-links · Kế hoạch kỹ thuật

## 1. Bảng file sẽ thay đổi

| Submodule | File | Trách nhiệm |
|---|---|---|
| `backend` | `src/drugtime/modules/family/domain/link.py` | Cập nhật `transition_link`: hỗ trợ PENDING $\rightarrow$ REVOKED, ACTIVE $\rightarrow$ REVOKED (tắt `sharing_enabled=False`), và idempotent khi đã REVOKED. |
| `backend` | `src/drugtime/modules/family/application/ports.py` | Thêm phương thức `revoke` trong Protocol `Links`. |
| `backend` | `src/drugtime/modules/family/application/manage_links.py` | Hàm `revoke_link` kiểm tra quyền sở hữu (`caller_id` là bệnh nhân hoặc người thân), raise `Forbidden("khong_co_quyen")` nếu không có quyền, xử lý idempotent. |
| `backend` | `src/drugtime/modules/family/adapters/outbound/sql_links.py` | Câu lệnh `_REVOKE_LINK` UPDATE đồng thời `status='revoked', revoked_at=:now, sharing_enabled=false` với điều kiện sở hữu trong `WHERE`. |
| `backend` | `src/drugtime/modules/family/adapters/inbound/http.py` | Bổ sung endpoint `DELETE /links/{id}`, xóa TODO comment. |
| `backend` | `src/drugtime/modules/family/api.py` | Cập nhật hàm tiếp xúc `revoke_link`. |
| `backend` | `tests/unit/test_family_manage_links.py` | Cập nhật và bổ sung ca kiểm thử unit cho `revoke_link`. |
| `backend` | `tests/unit/test_family_delete_link.py` | Thêm bộ test TDD bao phủ các kịch bản của endpoint HTTP và tích hợp PEP. |

## 2. Thứ tự thực hiện

1. **Bước 1 (TDD - Test trước):**
   - Viết các test case trong `tests/unit/test_family_manage_links.py` và `tests/unit/test_family_delete_link.py` tương ứng với các ca từ `test_links_api.py`.
2. **Bước 2 (Domain & Application):**
   - Sửa `domain/link.py` để `transition_link` chấp nhận `PENDING` và `ACTIVE`, đồng thời đặt `sharing_enabled=False`.
   - Sửa `manage_links.py` và `ports.py` để thêm kiểm tra `caller_id`.
3. **Bước 3 (Outbound SQL):**
   - Triển khai `SqlLinks.revoke` với câu SQL UPDATE 3 trường và WHERE kiểm tra sở hữu.
4. **Bước 4 (Inbound HTTP):**
   - Nối router endpoint `@router.delete("/links/{id}")` trong `http.py`.
5. **Bước 5 (Kiểm thử & Báo cáo):**
   - Chạy `python -m pytest` trên toàn bộ test module family và access control.
