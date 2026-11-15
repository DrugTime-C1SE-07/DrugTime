---
task: adhoc-20261115-mobile-health-profile-onboarding
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-15 23:19 +0700
content_hash: sha256:7da07ff4bb3e313c
inputs:
  01-requirement.md: sha256:c60e413f4f65fe0d
  02-contract.md: sha256:8322c29321d72f58
  03-plan.md: sha256:33aee035198e1847
  04-impl-notes.md: sha256:646bf99ea20360e3
  05-test-report.md: sha256:43f2d3acedd3e8c3
---

# S08b–S08e · Review

## 1. Kết luận

**Đạt, kèm lưu ý về kiểm thử trên thiết bị.** 0 Critical, 0 High, 0 Medium, 0 Low còn mở trong phạm vi đã kiểm. Hai phát hiện AC7 và AC8 từ lượt review trước đã được sửa và chạy lại đạt. TC-HSETUP-12 còn Pending vì cần thiết bị, tài khoản test và staging đã triển khai migration.

## 2. Phạm vi

| Submodule | Bản vá đối chiếu | Base |
|---|---|---|
| api_contract | `openapi.patch` | `b542ccb` |
| backend | `backend.patch`, `integration-tests.patch` | `89f5307` |
| frontend | `frontend.patch` | `8216e79`, có popup và dùng diff S08a đã review |

Đối chiếu diff đã review trước và các thay đổi sau review ở route PUT, test backend, so sánh snapshot Flutter, test controller và manifest/lockfile. Cả bốn bản vá đều đạt `git apply --reverse --check` trên clone tương ứng. Kiểm clone riêng xác nhận 1 file contract, 21 file backend kể cả test tích hợp và 35 file Flutter kể cả asset thuộc kế hoạch. Scope tại root báo 1.267 mục đã có từ trước. Xem `evidence/review-final-scope.log` và `evidence/review-final-isolated-scope.log`.

## 3. Kiểm tra theo tiêu chí

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC6 có bằng chứng widget, ảnh dựng hoặc API. AC7–AC8 đạt khi chạy lại. AC9–AC10 được kiểm qua audit fail-closed, rollback, migration và liên kết cũ. S08c dùng mục backend đã xác nhận, seed DB sạch trả danh mục rỗng. Thiết bị/staging và metadata reaction Figma còn chờ. |
| Contract | Ba operation đúng mã, bearer và quy tắc no-store ở hồ sơ. Runtime OpenAPI giữ JSON body bắt buộc và tham chiếu bước hợp lệ. PUT chéo trả 403 cả khi body lỗi, request chính chủ với body lỗi trả 422. Contract đã duyệt giữ nguyên. |
| Phân quyền và dữ liệu | Handler gọi PEP trước khi parse JSON. Audit allowed và thao tác ghi cùng UoW, audit denied bền vững qua giao dịch riêng. Có ca rút consent trên cùng token và ca lỗi audit chặn lưu. RLS, quyền role, ràng buộc snapshot và worker erasure đạt trên PostgreSQL sạch, sau 24 migration và seed. |
| Lỗi và đồng thời | Hai PUT cùng revision cho một 200 và một 409. App đối chiếu ID, trạng thái và tập tên NFC khi mất phản hồi. Tên khác vẫn báo xung đột, bản nháp giữ nguyên. |
| Hiệu năng và khả năng bảo trì | Snapshot tra theo khóa user và dùng liên kết đã có. Backend kiểm ID bệnh nền theo từng lựa chọn. Chưa đo tải danh mục lớn. Dependency Flutter mới chỉ thêm `unorm_dart` 0.3.3 vào lockfile. |
| Test và báo cáo | Lượt review chạy lại 15 ca DB, 14 ca API unit/registry và 6 ca Flutter, tất cả đạt. Báo cáo đã duyệt ghi 1.288 pass, 7 fail trùng baseline, 159 skip và 1 xpass cho suite tích hợp toàn repo. Test case Excel hợp lệ với 14 Pass, 0 Fail, 1 Pending. Workbook tổng mới có bản gộp xem trước trong task. |

## 4. Phát hiện đã đóng

| Mức trước khi sửa | Vị trí | Bằng chứng xác nhận |
|---|---|---|
| High, AC8 | `backend/src/drugtime/modules/medication/adapters/inbound/health_setup_http.py`, `backend/tests/integration/test_health_setup_api.py` | Với liên kết chia sẻ đang bật, body sai schema, JSON lỗi cú pháp và body rỗng đều trả 403, mỗi ca đúng một audit denied, không tạo snapshot. `evidence/review-final-db.log`, `evidence/review-final-route.log`. |
| Medium, AC7 | `frontend/mobile/lib/features/profile/domain/entities/health_setup.dart`, `frontend/mobile/test/features/profile/health_setup_screen_test.dart` | Mất phản hồi rồi GET trả “Hải sản” NFC thì xác nhận lưu với một PUT. GET trả “Hải Sản” thì báo xung đột và giữ nháp. `evidence/review-final-flutter.log`. |

## 5. Mô tả PR dự kiến

Task `adhoc-20261115-mobile-health-profile-onboarding`. Khi được yêu cầu mở PR, các PR dưới đây liên kết chéo theo thứ tự merge.

1. **api_contract** — Thêm OpenAPI cho danh mục dị ứng và GET/PUT hồ sơ onboarding, gồm revision, lỗi, xác thực và cache. AC5–AC9. Kiểm tệp OpenAPI và tham chiếu schema bằng `scratch/check_contract.py`.
2. **backend** — Tạo snapshot chính chủ, tái dùng liên kết bệnh nền và PEP, giữ audit khi request chéo có body lỗi, hỗ trợ revision và erasure. AC4–AC10. Chạy `pytest tests/unit/test_health_setup_http.py tests/architecture/test_health_route_enforcement.py` và bộ test tích hợp hồ sơ trên DB đã áp migration. Bản vá test tích hợp nằm trong backend; đưa vào PR backend sau khi áp bản vá sản phẩm.
3. **frontend** — Nối popup → S08a → S08b/S08c → S08e, tải danh mục backend, giữ nháp, xử lý nhập tay/bỏ qua và đối chiếu NFC khi mất phản hồi. AC1–AC7. Test thủ công với tài khoản staging từ popup, chọn dị ứng và bệnh nền, lưu, mở lại và thử mất mạng khi lưu. S08c có thể rỗng tùy danh mục staging.
4. **superproject** — Bump con trỏ api_contract, backend và frontend sau khi các PR submodule đã merge và commit tồn tại trên remote. Dẫn đến report, workbook và ca staging còn Pending.

## 6. Ghi chú quy trình

- Giữ ba biến thể body lỗi trong bộ kiểm PEP để kiểm cả phản hồi và audit trên DB.
- Lượt review này chỉ cập nhật artifact và bằng chứng. Các thay đổi sản phẩm vẫn ở clone task và bản vá, chưa tạo PR.
- Bằng chứng: `evidence/review-final-db.log`, `evidence/review-final-route.log`, `evidence/review-final-flutter.log`, `evidence/review-final-testcase-validation.log`.

## Bước tiếp theo

- Duyệt review bằng `python .agents/scripts/gate.py approve adhoc-20261115-mobile-health-profile-onboarding review`.
- Chạy TC-HSETUP-12 khi có staging đã áp migration và tài khoản test. Trước khi merge cần review PR theo Definition of Done.
