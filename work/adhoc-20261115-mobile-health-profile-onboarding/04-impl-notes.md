---
task: adhoc-20261115-mobile-health-profile-onboarding
stage: implement
owner: Ngọc Việt
started_at: 2026-11-15 17:39 +0700
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-15 22:57 +0700
content_hash: sha256:646bf99ea20360e3
inputs:
  01-requirement.md: sha256:c60e413f4f65fe0d
  02-contract.md: sha256:8322c29321d72f58
  03-plan.md: sha256:33aee035198e1847
---

# S08b–S08e · Triển khai

## 1. Tiến độ

| Bước | Trạng thái | Kiểm tra và bằng chứng |
|---|---|---|
| P1 | Xong | SHA-256 OpenAPI khớp contract. Mang diff S08a đã review và giữ Home/popup từ baseline 8216e79. Smoke widget popup/S08a đạt trong `evidence/implement-focused-frontend-final.log`. |
| P2 | Xong cho phạm vi tạm đã xác nhận | Migration và danh mục dị ứng 8 mục đã có. Chạy 24 migration và seed trên PostgreSQL sạch đạt. Bảng `conditions` có **0 dòng** sau seed. Người dùng xác nhận tạm hiển thị các mục backend đã xác nhận. `evidence/implement-db-api-smoke-final.log`. |
| P3 | Xong | Snapshot, khóa theo user, giữ ID/metadata link, revision, xóa dữ liệu khi erasure. Bài test use case và API roundtrip DB thật đạt. |
| P4 | Xong | Sửa thứ tự PEP cho PUT theo AC8. Ba ca body sai hoặc thiếu đều có audit denied trên PostgreSQL sạch, xem `evidence/implement-review-db.log`. |
| P5 | Xong | App nạp danh mục, giữ nháp và đối chiếu khi đọc lại. Hồi quy tên Unicode được xử lý ở P9. |
| P6 | Xong code và widget cho phạm vi tạm | CTA S08a nối wizard, hai bottom sheet, chọn/bỏ/bỏ qua/quay lại. S08c xử lý riêng danh mục rỗng sau khi tải thành công, vẫn nhập và lưu tên tự khai được. Đối chiếu ảnh đủ trạng thái ở P8. |
| P7 | Xong code và widget | S08e dựng từ snapshot sau lưu, CTA về Trang chủ. Widget đã kiểm nhánh Không có bệnh nền đã biết. Dòng dị ứng tóm tắt dữ liệu thật, nên nội dung có thể khác chữ mẫu “Xem trong hồ sơ”. |
| P8 | Giai đoạn test | Chưa tạo file test trong vùng `tests/integration`. Chưa test tất cả 13 frame trên thiết bị/staging hoặc duyệt giai đoạn implement. |
| P9 | Xong | Chuẩn hóa NFC khi đối chiếu tên. Cả hai ca hồi quy đạt, Dart analyze sạch và lockfile chỉ thêm dependency NFC. |

## 2. File đã thay đổi

| Submodule | Checkout riêng, base | Bản vá |
|---|---|---|
| api_contract | `scratch/api_contract`, b542ccb | `openapi.patch` đã duyệt |
| backend | `scratch/backend`, 89f5307 (pin backend tại workspace) | `backend.patch` |
| frontend | `scratch/frontend`, 8216e79 (base task S08a đã review) | `frontend.patch`, gồm asset Figma dạng PNG |

Cả ba clone dùng nhánh `feat/adhoc-20261115-mobile-health-profile-onboarding`. Kiểm scope trên chính clone nhận 1 file contract, 20 file backend và 34 file frontend, tất cả nằm trong plan. Kiểm toàn workspace báo cùng 1.267 mục ngoài task như giai đoạn plan. Xem `evidence/implement-scope-isolated.log` và `evidence/implement-scope.log`. Chưa commit/push.

## 3. Kết quả kiểm tra

| Kiểm tra | Kết quả | Log |
|---|---|---|
| Pytest route, use case, profile cũ và health route registry | 92 pass với cấu hình test cục bộ. Backend dùng secret ngẫu nhiên cho môi trường test. | `evidence/implement-focused-backend-final.log` |
| Flutter widget/controller Home, popup, S08a và wizard | 10 pass. Kiểm nhánh chọn dị ứng, back, xác nhận không có bệnh nền, hoàn tất, và lưu tên tự nhập khi danh mục backend rỗng. | `evidence/implement-condition-catalog.log` |
| Ruff file Python task | Pass. Ruff toàn repo còn báo lỗi ngoài task trong lượt kiểm. | `evidence/implement-ruff-focused.log`, `evidence/implement-ruff.log` |
| `dart analyze` | 5 lint info ở lượt đầu, 2 info ở file task đã sửa sau đó. Ba info còn lại ở ngoài task. | `evidence/implement-dart-analyze.log` |
| Toàn bộ backend unit + architecture | 2.022 pass, 17 fail. Chạy lại 17 ca trên baseline tái hiện đúng 17 lỗi contract. | `evidence/implement-final-backend.log`, `evidence/implement-backend-baseline.log` |
| Toàn bộ Flutter | 1.038 pass, 1 skip, 6 fail ở lượt đầu. 5 ca Người thân tái hiện trên baseline. Ca wizard mới đã sửa và pass trong lần chạy tập trung, chưa chạy lại toàn bộ suite sau lần sửa đó. | `evidence/implement-final-frontend.log`, `evidence/implement-frontend-baseline.log` |
| PostgreSQL sạch, reset bằng PostgreSQL portable 18.6 | Áp 24 migration và seed, kiểm RLS/grant/check/worker erasure, thao tác API lưu/đọc lại/stale revision/403. Không có Supabase CLI để chạy `supabase db reset`. Tài khoản và bệnh nền mẫu chỉ dùng trong DB kiểm thử cục bộ. | `evidence/implement-db-api-smoke-final.log` |

## 3b. Bộ test case Excel

Làm ở giai đoạn test.

## 4. Migration

`20261115110000_health_profile_onboarding.sql` tạo bảng snapshot. RLS bảo vệ bảng khỏi role client, role API được đọc/ghi, worker chỉ đọc cột chủ sở hữu cần cho xóa và được DELETE. Các liên kết bệnh nền cũ vẫn ở `user_conditions`. Erasure xóa snapshot rõ ràng vì users hiện được ẩn danh thay vì xóa hàng.

## 5. Truy vết nghiệp vụ

- QD-31 và QD-32, AC1/AC8. Flutter giữ cổng consent, API không ghi consent và chỉ đọc/ghi hồ sơ chính chủ qua PEP.
- QD-33, AC8/AC9. Audit ở PEP; smoke thật kiểm 403 cho selector chéo. Ca lỗi audit và rút consent trong suite tích hợp chính thức vẫn thuộc P8.
- QD-40, AC4/AC6. Phân biệt `unreported`, `none_known`, `reported`. Bỏ qua giữ bước đó ngoài payload. Không đổi luồng gợi ý món ăn.

## 6. Phát sinh

- Q1 đã có quyết định của người dùng: **tạm hiển thị các mục backend đã xác nhận**. S08c dùng kết quả `GET /conditions`. Khi API trả danh mục rỗng, màn hướng dẫn nhập thủ công và vẫn cho xác nhận không có bệnh nền. Chưa đủ dữ liệu chuẩn để tái hiện tám ô của Figma trên môi trường thật.
- Liên kết reaction prototype chưa xác minh từ metadata. Code dùng hành vi lưu cuối và bỏ qua trong requirement đã duyệt. Chưa triển khai hoặc chạy thử trên staging.
- AC7 dùng `unorm_dart` 0.3.3 từ pub.dev. Sau khi resolve, lockfile chỉ thêm đúng thư viện này. Flutter SDK cục bộ báo thiếu file plugin Android của `integration_test` ở bước sau resolve. Kiểm Dart và Flutter unit/widget dùng package config đã resolve.
- Scope tại superproject tiếp tục báo 1.267 mục ngoài phạm vi đã có từ trước. Kiểm các clone riêng cho task xác nhận 1 file contract, 21 file backend (kể cả test tích hợp) và 34 file Flutter đều thuộc plan đã duyệt. Xem `evidence/implement-review-scope.log` và `evidence/implement-review-isolated-scope.log`.

## Bước tiếp theo

- Duyệt implement bằng `python .agents/scripts/gate.py approve adhoc-20261115-mobile-health-profile-onboarding implement`.
- Mở lại báo cáo test bằng `python .agents/scripts/gate.py reopen adhoc-20261115-mobile-health-profile-onboarding test` để cập nhật suite tích hợp, báo cáo và workbook ở giai đoạn test. Kiểm trên thiết bị/staging vẫn còn chờ.

## 7. Sửa sai lệch Figma sau kiểm thử

- BUG-HSETUP-02, AC2. Sửa chiều cao và khoảng cách thẻ trong `health_setup_form.dart`, tinh chỉnh padding/viền trường nhập trong `health_setup_custom_sheet.dart`. Dùng chiều cao tối thiểu để thẻ vẫn mở rộng theo nhãn và cỡ chữ. Dùng font Inter cho CTA, khắc phục ký tự ô vuông trong bản render.
- Tại 375 × 812, hàng **Thêm bệnh nền khác** dịch từ khoảng y=539 xuống y=578 và cạnh trên bottom sheet từ khoảng y=535 xuống y=545, khớp các vị trí đã báo trong Figma. Ảnh sau sửa ở `evidence/revised/app-38-5045.png` và `evidence/revised/app-547-11229.png`.
- Chạy 10 bài widget/controller và dựng lại 13 trạng thái Figma trong một lượt, **23 pass**. Log `evidence/implement-figma-spacing.log`. Chưa đo độ khớp toàn màn trên thiết bị thật hoặc chạy lại backend vì lượt sửa chỉ chạm hai widget của Flutter.
- Cập nhật `frontend.patch`; kiểm diff không có lỗi whitespace. Dữ liệu trong ảnh đối chiếu dùng fixture để dựng tám ô S08c; dữ liệu app vẫn đến từ backend như phạm vi tạm đã duyệt.

## 8. Sửa phát hiện High từ review

- AC8. FastAPI nhận request thô. Handler kiểm PEP trước khi parse hoặc validate JSON. Authorization, audit allowed và ghi hồ sơ dùng cùng UoW. Selector ngoài chính chủ đi qua nhánh audit denied của PEP và trả `403 khong_co_quyen`. Request chính chủ với JSON sai hoặc thiếu vẫn trả `422`.
- Schema OpenAPI runtime tiếp tục mô tả JSON body bắt buộc cùng các schema bước. Bài test kiểm tham chiếu schema, mã trạng thái và bearer. OpenAPI contract đã duyệt giữ nguyên.
- `pytest tests/unit/test_health_setup_http.py -q` đạt 5 bài. Ruff đạt trên hai file đã sửa. `evidence/implement-review-http.log`, `evidence/implement-review-ruff.log`.
- Toàn bộ backend unit và architecture với secret giả dành riêng cho test có 2.025 pass và 17 lỗi contract trùng baseline. Lượt đầu thiếu cấu hình secret có thêm 6 lỗi xác thực; sáu lỗi này biến mất khi chạy lại với cấu hình test. `evidence/implement-review-backend-with-session.log`.
- PostgreSQL sạch đạt 15 bài, gồm 12 ca hiện có và 3 ca tái hiện bổ sung đặt trong scratch. Ca mới kiểm body `{}`, JSON lỗi cú pháp và body rỗng với liên kết chia sẻ đang hoạt động. Cả ba trả 403, mỗi ca có một dòng denied và không tạo snapshot cho hai tài khoản. Chuyển ba ca vào suite tích hợp chính thức ở giai đoạn test. `evidence/implement-review-db.log`.
- Đã xuất lại `backend.patch` và kiểm `git apply --reverse --check` đạt trên clone task.

## 9. Đối chiếu tên Unicode khi đọc lại

- AC7. So tập tên sau trim/NFC trong `HealthSetupStep.matches`. Giữ phân biệt hoa thường, kiểm trạng thái bước và ID. Payload giữ tên người dùng nhập; app xác nhận bằng snapshot server khi đọc lại.
- Hồi quy mô phỏng mất phản hồi sau PUT. GET trả “Hải sản” ở dạng NFC thì kết quả phải là đã lưu, chỉ gọi PUT một lần. GET trả “Hải Sản” thì phải giữ nháp và báo xung đột. Trước khi sửa, ca tương đương NFC thất bại đúng như review, còn ca đối chứng đạt. `evidence/implement-nfc-before.log`.
- Sau sửa, luồng popup → S08a → wizard và hai ca mới nằm trong 12 test Flutter đạt. Dart analyze hai file thay đổi không có vấn đề. Suite Flutter đầy đủ có 1.042 pass, 1 skip, 5 lỗi Người thân, khớp tên các ca đã tái hiện trên baseline. `evidence/implement-nfc-focused.log`, `evidence/implement-nfc-analyze.log`, `evidence/implement-nfc-flutter.log`.
- Đã xuất lại `frontend.patch`, kiểm diff và apply ngược thành công. Scope clone riêng đạt với 35 file frontend, 21 file backend và 1 file contract. Scope root vẫn báo 1.267 mục ngoài phạm vi đã có từ trước. `evidence/implement-nfc-isolated-scope.log`, `evidence/implement-nfc-scope.log`.
