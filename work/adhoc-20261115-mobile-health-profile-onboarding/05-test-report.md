---
task: adhoc-20261115-mobile-health-profile-onboarding
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-15 23:09 +0700
content_hash: sha256:43f2d3acedd3e8c3
inputs:
  01-requirement.md: sha256:c60e413f4f65fe0d
  02-contract.md: sha256:8322c29321d72f58
  03-plan.md: sha256:33aee035198e1847
  04-impl-notes.md: sha256:646bf99ea20360e3
---

# S08b–S08e · Báo cáo kiểm thử

## 1. Môi trường

- Checkout backend `scratch/backend`, nhánh `feat/adhoc-20261115-mobile-health-profile-onboarding`, base `89f5307`. Thêm `tests/integration/test_health_setup_api.py`, bản vá `integration-tests.patch`.
- Dùng PostgreSQL portable 18.6 riêng, chỉ nghe loopback. Tạo database sạch cho mỗi lượt và chạy 24 migration cùng seed. Tái sử dụng fixtures chạy FastAPI bằng `api_role` với app token. Không có Supabase CLI nên chưa chạy `supabase db reset` hay stack Supabase chính thức.
- Lệnh backend từ root là `python work/adhoc-20261115-mobile-health-profile-onboarding/scratch/run_database_check.py tests/integration/test_health_setup_api.py` hoặc thay đối số cuối bằng `tests/integration` để chạy toàn bộ.
- Flutter dùng SDK cục bộ và widget fixture. `scratch/capture_health_setup_test.dart` tạo ảnh 375 × 812 cho 13 node. Danh mục tám bệnh nền trong ảnh dùng fixture đối chiếu. Bảng `conditions` từ seed backend của repo vẫn rỗng theo phạm vi hiển thị tạm đã xác nhận. Không dùng kết quả ảnh fixture làm bằng chứng rằng staging đã có danh mục.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Bằng chứng | Kết quả |
|---|---|---|
| AC1 | Widget Home/popup và S08a, route fixture trong `test-review-flutter.log`. | Pass kiểm widget. Thử xuyên suốt trên thiết bị với API staging còn Pending. |
| AC2 | 13 ảnh dựng lại tại `evidence/test-review-render/`. So tọa độ với hai ảnh Figma và chạy thêm ca 320 dp, chữ 200%, inset bàn phím mô phỏng. | Pass hồi quy hai sai lệch khoảng cách và ca chữ lớn trên widget. Chưa đối chiếu toàn màn trên thiết bị thật. |
| AC3 | Widget chọn Penicillin và Hải sản, chuyển bước rồi quay lại. | Pass. Ảnh fixture dựng được trạng thái chọn một/hai mục. |
| AC4 | Widget nhập tên khi danh mục rỗng; API kiểm tên trắng/trùng sau chuẩn hóa, none_known và giữ bước bỏ qua. | Pass. |
| AC5 | Fixture DB có liên kết cũ, danh mục và lựa chọn tự khai. GET trước/sau PUT. | Pass tại DB cục bộ. |
| AC6 | Lưu snapshot thật; widget kết thúc tại S08e rồi về Trang chủ. | Pass tại DB và widget. |
| AC7 | Cạnh tranh PUT cùng revision, gửi lại giá trị đã lưu, legacy PATCH làm revision cũ hết hiệu lực. Mô phỏng mất phản hồi và GET trả tên NFC tương đương hoặc tên khác chữ hoa. | Pass. Tên tương đương xác nhận lưu, tên khác báo xung đột và giữ nháp. Mỗi ca gọi PUT một lần. |
| AC8 | GET/PUT sau khi rút consent, selector chéo có hoặc thiếu liên kết chia sẻ, admin và ID đích lạ. Chạy thêm ba ca PUT chéo với body sai schema, JSON lỗi cú pháp và body rỗng. | Pass. Ba biến thể mới đều trả 403, ghi đúng một audit denied mỗi ca và không tạo snapshot. |
| AC9 | Chèn lỗi khi ghi audit, và chèn lỗi trong transaction sau thao tác ghi trước commit. | Pass. 500, đọc lại snapshot không đổi. |
| AC10 | Migration trên DB sạch; đọc liên kết seed thử kiểu cũ, bảo toàn ID và metadata, kiểm RLS/grant/xóa. | Pass tại PostgreSQL 18.6. |

- `evidence/test-review-api.log` — **15 pass** trong 23,25 giây trên PostgreSQL sạch. `evidence/test-review-ruff.log` xác nhận lint test tích hợp đạt.
- `evidence/test-review-flutter.log` — **12 pass** cho Home/popup, S08a, wizard và hai ca đối chiếu Unicode.
- `evidence/test-review-render.log` — **14 pass**, gồm 13 trạng thái dựng ảnh và ca 320 dp ở chữ 200% có cuộn, nhập qua hai sheet rồi hoàn tất.
- `evidence/test-review-spacing.log` — mép vùng trắng hàng thêm bệnh nền y=579 và mép trên sheet y=545 trên cả ảnh Flutter mới và ảnh Figma đã lưu, đo tại x=92.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Kết quả |
|---|---|
| Chính chủ có consent, người thân có/không có liên kết, admin, đích không tồn tại | Chính chủ 200 và audit allowed. Các truy cập ngoài chính chủ trả 403 và có audit denied. |
| Selector chéo khi có link chia sẻ đang hoạt động và body sai hoặc thiếu | 403 `khong_co_quyen` cho cả ba body. Mỗi ca có đúng một dòng denied, không tạo snapshot cho hai tài khoản. |
| Rút `health_data` rồi dùng cùng token tại request kế tiếp | 403 `consent_revoked` cho GET/PUT. Snapshot không bị ghi. |
| Audit lỗi hoặc transaction lỗi trước commit | 500. Không phản hồi payload sức khỏe và DB không lưu hai bước. |
| Hai PUT cùng revision, gửi lại sau readback, liên kết ghi qua API cũ | Một 200, một 409; giữ đúng một liên kết. Gửi nội dung đã lưu với revision hiện tại giữ snapshot. PATCH cũ làm snapshot trước đó hết hiệu lực. |

## 4. Toàn bộ bộ test tích hợp

- Từ root, đặt `HEALTH_TEST_PORT=55441` và chạy `python work/adhoc-20261115-mobile-health-profile-onboarding/scratch/run_database_check.py tests/integration`. Output `evidence/test-integration-rerun.log`.
- 1.288 pass, 7 fail, 159 skip, 1 xpass trong 293,77 giây. Cả bảy ca lỗi thuộc cảnh báo, xác nhận liều hoặc API thông báo, trùng tên với baseline 89f5307. Xem `evidence/test-integration-baseline.log` và `evidence/test-review-baseline-compare.log`.
- Lượt khởi động suite đầu dùng lại cổng của lượt tập trung khi phiên PostgreSQL trước còn đang kết thúc. Sau reset, fixture suite mất kết nối và bỏ qua toàn bộ. Giữ `evidence/test-integration.log` để đối chiếu sự cố môi trường. Kết quả báo cáo lấy từ lượt chạy lại trên cổng riêng.
- `scope.py --stage test` trả exit 1 với 1.267 mục có sẵn ở root. Clone riêng đạt kiểm phạm vi. Lượt này chỉ sửa test tích hợp đã duyệt trong clone backend và cập nhật artifact của task. Patch test đã được xuất lại và kiểm apply ngược. Log `evidence/test-review-scope.log`, `evidence/test-review-isolated-scope.log`.

## 5. Bộ test case Excel

- Spec `testcases.json`, workbook task `testcases.xlsx`, bản gộp `Test_Cases-preview.xlsx`. Validate, build và merge bản sao đều thành công. Xem `evidence/testcase-xlsx-review.log`.
- Workbook chính thức tại `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`. Submodule docs đang detached HEAD và có thay đổi backlog của workspace, nên merge vào bản sao để giữ nguyên workspace chính.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---:|---:|---:|---:|
| Thiết lập hồ sơ sức khỏe (HSETUP) | 15 | 14 | 0 | 1 |

- Pending `TC-HSETUP-12` chạy trên thiết bị và API staging, gồm đọc lại và mất mạng.

## 5b. Lỗi sản phẩm tìm thấy

- **BUG-HSETUP-02 (Low), AC2 — đã kiểm lại đạt.** Hàng “Thêm bệnh nền khác” và mép trên bottom sheet từng lệch lần lượt khoảng 39 px và 10 px. Sau bản sửa Flutter, tọa độ kiểm lại trùng hai ảnh Figma. Giữ ảnh trước sửa ở `evidence/app-38-5045.png`, `evidence/app-547-11229.png` và ảnh sau sửa trong `evidence/test-recheck/`.
- Hai phát hiện từ review về AC7 và AC8 đã kiểm lại đạt qua `TC-HSETUP-14` và `TC-HSETUP-15`. Các lỗi suite tích hợp ngoài luồng nằm ở mục 4.
- CTA trong ảnh widget đã hiển thị chữ tiếng Việt. Status bar và home indicator trong Figma thuộc chrome mô phỏng, app dùng insets của hệ điều hành. Chưa xác nhận kết xuất trên thiết bị qua TC-HSETUP-12.

## 6. Test không ổn định hoặc bị skip

- Các ca tập trung của task chạy đầy đủ, không đánh dấu skip. Suite toàn repo có skip theo fixture môi trường, chi tiết trong log.
- Ca `test_five_rejections_via_endpoint_block_24h_others_unaffected__AC9` từng trả `Retry-After: 86401` ở lượt kiểm trước. Ca đạt trong suite lượt này, cũng như hai lượt chạy riêng trước đó trên nhánh task và baseline. Chưa xác định nguyên nhân. Xem `evidence/test-recheck-family-repeat.log` và `evidence/test-recheck-family-baseline.log`.
- Ca 320 dp ban đầu dùng font widget mặc định cho nút và cho kết quả layout không đại diện. Lượt cuối nạp font Inter giống app, dùng lại kích thước và inset đã đặt, và đạt. Giữ log đầu ở `evidence/test-recheck-narrow.log`.

## 7. Phát sinh

- Match đầy đủ danh mục S08c trên môi trường thật cần dữ liệu xác nhận từ backend. Kết quả fixture chỉ xác nhận bố cục có thể dựng và các nhánh có thể thao tác.
- Giữ hành vi điều hướng đã duyệt. Chưa xác minh phản ứng prototype bằng metadata từ Figma.

## Bước tiếp theo

- Đang chờ duyệt test. Chạy `python .agents/scripts/gate.py approve adhoc-20261115-mobile-health-profile-onboarding test` để chuyển review.
- Ca thiết bị/staging TC-HSETUP-12 cần tài khoản và backend test đã triển khai migration.
