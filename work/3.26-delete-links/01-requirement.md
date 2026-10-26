---
task: 3.26-delete-links
title: Chuyển DELETE /links/{id} từ prototype sang module family thật trên Hexagonal
type: feature
stage: requirement
size: M
contract_change: no
affected: [backend]
status: approved
approved_by: DrugTime Team
approved_at: 2026-10-23 14:34 +0700
content_hash: sha256:e9780e264d8de972
---

# 3.26-delete-links · Chuyển DELETE /links/{id} sang module family Hexagonal

## 1. Mục tiêu

Chuyển đổi endpoint và nghiệp vụ `DELETE /links/{id}` (SCRUM-134, Backlog 3.26, PB17) từ bản prototype chạy mock_db (`backend/app/routers/links.py` trên nhánh `feat/api-contract`) sang module `family` thật trên kiến trúc Hexagonal Modular Monolith (`src/drugtime/modules/family/`).

## 2. Phạm vi

### Trong phạm vi

1. **Domain (`domain/link.py`):**
   - Hỗ trợ chuyển trạng thái từ `ACTIVE` và `PENDING` sang `REVOKED`.
   - Cập nhật `sharing_enabled = False` và `revoked_at = now` khi thu hồi.
   - Idempotent: nếu link đã ở trạng thái `REVOKED`, trả về link hiện tại mà không sửa đổi `revoked_at`.

2. **Application (`application/manage_links.py` & `application/ports.py`):**
   - Kiểm tra quyền sở hữu liên kết: chỉ `patient_user_id` của link hoặc `family_user_id` của chính link đó mới được quyền thu hồi / tự rời.
   - Nếu link không tồn tại hoặc caller không thuộc link, từ chối với `Forbidden("khong_co_quyen")` (HTTP 403 `{"detail": "khong_co_quyen"}`).
   - Ghi nhận `revoke` vào cơ sở dữ liệu qua port `Links`.

3. **Outbound SQL (`adapters/outbound/sql_links.py`):**
   - Câu lệnh `UPDATE caregiver_links` cập nhật đồng thời trong CÙNG MỘT câu:
     `status = 'revoked'`, `revoked_at = :revoked_at`, `sharing_enabled = false`.
   - Điều kiện quyền sở hữu nằm trong mệnh đề `WHERE`:
     `WHERE id = :id AND (patient_user_id = :caller_id OR family_user_id = :caller_id)`.
   - Thỏa mãn ràng buộc toàn vẹn Schema v11: `CHECK ((status = 'revoked') = (revoked_at IS NOT NULL))`.

4. **Inbound HTTP (`adapters/inbound/http.py`):**
   - Nối endpoint `DELETE /links/{id}` (với router prefix `/family`), trả về HTTP `204 No Content`.
   - Xóa `DELETE /family/links/{id}` khỏi TODO comment.
   - Sử dụng dependency xác thực chuẩn `identity.current_user`.

5. **Unit & Contract Tests:**
   - Bộ kiểm thử unit trong `tests/unit/test_family_manage_links.py` và `tests/unit/test_family_http.py` (hoặc `test_family_delete_link.py`) bao phủ đầy đủ các ca:
     - Bệnh nhân thu hồi link thành công (204).
     - Người thân tự rời link thành công (204).
     - Người lạ hoặc link không tồn tại $\rightarrow$ 403 `khong_co_quyen`.
     - Thu hồi lần hai $\rightarrow$ 204 và không đổi `revoked_at`.
     - Link `pending` cũng thu hồi được $\rightarrow$ chuyển `revoked`, giữ bản ghi.
     - Sau khi gỡ, PEP từ chối truy cập dữ liệu sức khỏe với 403 và ghi nhận audit log `denied`.

### Ngoài phạm vi

- Không sửa schema CSDL (không migration, không thêm cột hay bảng mới).
- Không sửa logic tạo liên kết hay duyệt liên kết (QD-30).
- Không sửa các module khác ngoài `family` và test của nó.

## 3. Tiêu chí chấp nhận (AC)

- [ ] AC1: Caller là bệnh nhân sở hữu link $\rightarrow$ link chuyển sang `revoked`, `revoked_at = now`, `sharing_enabled = false`, trả về HTTP 204.
- [ ] AC2: Caller là người thân thuộc link $\rightarrow$ link chuyển sang `revoked`, `revoked_at = now`, `sharing_enabled = false`, trả về HTTP 204.
- [ ] AC3: Caller không thuộc link hoặc link_id không tồn tại $\rightarrow$ trả về HTTP 403 `{"detail": "khong_co_quyen"}`.
- [ ] AC4: Link ở trạng thái `pending` $\rightarrow$ gỡ thành công sang `revoked`, không xóa bản ghi CSDL.
- [ ] AC5: Gọi thu hồi lần 2 trên link đã `revoked` $\rightarrow$ trả về HTTP 204, `revoked_at` giữ nguyên mốc thời gian lần đầu.
- [ ] AC6: Sau khi thu hồi, `family.has_active_sharing_link` trả về `False`, khiến cơ chế phân quyền PEP (`access.authorize`) lập tức từ chối quyền truy cập của người thân.
