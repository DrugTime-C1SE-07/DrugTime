---
task: 3.18
stage: requirement
status: draft
size: S
contract_change: no
owner: om-cx
---

# 3.18 · Test: consent-on-link flow (PB16)

## 1. Mục tiêu và phạm vi

- **Mục tiêu**: Kiểm thử luồng liên kết người thân và chia sẻ dữ liệu sức khỏe có điều kiện consent (PB16), đảm bảo tuân thủ nghiêm ngặt các quyết định nghiệp vụ đã chốt (QD-04, QD-28, QD-29, QD-30, QD-33, QD-34).
- **Phạm vi**: 
  - Chỉ thêm/sửa test trong `backend/tests/` và tài liệu trong `work/3.18/`.
  - Không sửa mã nguồn nghiệp vụ trong `backend/src/`.
  - Không thay đổi migration hoặc API contract.
  - Phân loại task: Size S (task test tích hợp/unit, không đổi contract, kiểm chứng các API đã có).

## 2. Tiêu chí chấp nhận (Acceptance Criteria)

1. **AC1**: Người thân gọi API dữ liệu sức khỏe khi link còn `pending` $\rightarrow$ 403 `khong_co_quyen`, ghi `access_logs` `result='denied'`.
2. **AC2**: Bệnh nhân từ chối link (`reject`) $\rightarrow$ link chuyển trạng thái `rejected`, người thân gọi API dữ liệu sức khỏe $\rightarrow$ 403 `khong_co_quyen`, ghi `access_logs` `result='denied'`.
3. **AC3**: Bệnh nhân phê duyệt link (`approve`) hợp lệ $\rightarrow$ link chuyển `active`, nhưng `sharing_enabled` mặc định `false` (an toàn) $\rightarrow$ người thân gọi API dữ liệu $\rightarrow$ 403 `khong_co_quyen`.
4. **AC4**: Bệnh nhân bật chia sẻ (`sharing_enabled=true`) khi đang có consent `family_sharing` và `health_data` $\rightarrow$ người thân gọi API dữ liệu $\rightarrow$ 200 OK, ghi `access_logs` `result='allowed'`, `actor_role='family'`.
5. **AC5**: Bệnh nhân phê duyệt khi chưa có hoặc đã rút consent `family_sharing` $\rightarrow$ API approve trả 403 `consent_revoked`.
6. **AC6**: Bệnh nhân phê duyệt sai `document_version` hoặc `consent_confirmed=false` $\rightarrow$ 422 (`consent_document_outdated` hoặc validation error).
7. **AC7**: Phê duyệt lặp lại (idempotent replay) với cùng bằng chứng $\rightarrow$ 200 OK, giữ nguyên bằng chứng và `sharing_enabled` hiện hành.
8. **AC8**: Rút consent `family_sharing` hoặc `health_data` sau khi đã `active` $\rightarrow$ người thân bị 403 ngay ở request kế tiếp (cùng token JWT), ghi `access_logs` `denied` (QD-28, QD-29).
9. **AC9**: Thu hồi link (`revoked`) $\rightarrow$ người thân bị 403 ngay ở request kế tiếp, ghi `access_logs` `denied`.
10. **AC10**: Liên kết lại sau khi revoke/reject (QD-30) $\rightarrow$ tạo link mới ở trạng thái `pending`, không tự khôi phục phạm vi chia sẻ cũ (`sharing_enabled=false`).
11. **AC11**: Mọi lượt từ chối đều ghi `access_logs` fail-closed với đầy đủ metadata; lượt allowed ghi `access_logs` đồng bộ trong transaction (QD-33).

## 3. File sẽ thay đổi

- `work/3.18/01-requirement.md` (tài liệu đặc tả yêu cầu task)
- `work/3.18/05-test-report.md` (biên bản kiểm thử & bảng khoảng trống)
- `backend/tests/integration/test_family_links_api.py` (bổ sung các test case `__3_18`)
