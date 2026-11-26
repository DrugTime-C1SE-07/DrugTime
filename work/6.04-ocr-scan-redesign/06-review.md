---
task: 6.04-ocr-scan-redesign
stage: review
status: approved
approved_by: Duc1445
approved_at: 2026-11-26 15:17 +0700
content_hash: sha256:4267639076cba951
inputs:
  01-requirement.md: sha256:645fefcac97207fa
  03-plan.md: sha256:966b0ff836e39e0a
  04-impl-notes.md: sha256:f7b8be27654869ca
  05-test-report.md: sha256:aad584b061591005
---

# 6.04-ocr-scan-redesign · Review

## 1. Kết luận

**Đạt, kèm lưu ý** (`0 Critical`, `0 High`, `0 Medium`, `5 Low` không chặn).

Đánh giá độc lập được thực hiện bởi phiên reviewer (`3e2c9d0d-ffc3-4c37-b436-ba32311131a1`) kết hợp kiểm chứng lại toàn bộ diff trên `frontend` (10 file) và `docs` (`Test_Cases.xlsx`), chạy lại `flutter analyze`, `flutter test`, `scope.py` và `testcase_xlsx.py validate`. Không có lỗi `Critical` hay `High`; đủ điều kiện chốt giai đoạn `review`, commit theo `wf-git` và mở PR khi người dùng cho phép.

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| `frontend` (nhánh `feat/6.04-ocr-scan-redesign`, từ `main` `442cb4e`) | `git -C frontend diff` (8 file sửa) + đọc đầy đủ 2 file mới chưa track (`scan_camera_overlay.dart`, `scan_failure_view.dart`) — hiện chưa commit theo quy tắc cổng |
| `docs` (nhánh `feat/6.04-ocr-scan-redesign`, từ `main` `8d8c743`) | `git -C docs status -s` (`M Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`) + kiểm tra nội dung workbook `69` sheets bằng `openpyxl` — hiện chưa commit |

Kết quả `python .agents/scripts/scope.py 6.04-ocr-scan-redesign --stage implement`: `10/10` file trong `frontend` + `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` đều là **`[OK]`**; `104` file `[NGOÀI]` đều là file tồn đọng sẵn trên workspace/`backend` trước khi bắt đầu task (đã ghi đầy đủ ở mục Phát sinh của `01`, `03`, `04`, `05`).

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | **Đạt** `AC1–AC9` (scrim 4 phía dùng chung `computeScanFrameRect` + góc 28px + pill hướng dẫn dưới khung; hướng dẫn quyền/lỗi camera không có nút `'Cho phép camera'`; sheet `S07-O2` `17px`/`14px` `#01554F` + xóa trạng thái cũ khi hủy; `S07-O2r` pill `matched`/`low_confidence` `#92400E` + shadow, bỏ badge góc phải cũ; màn lỗi `S07-O3e` header `#01554F` + vòng `160×160` + tips badge `40×40` `17px` + thanh đáy 4 nhánh; `OcrController.canRetry` + `_retryOcr()`; dọn ảnh mã hóa & RAM fail-closed; không overflow ở `360×640` với `textScaler = 1.3`). `AC10` (`manual` Android thật) ở trạng thái `Pending` (`TC-OCRUI-21`, `TC-OCRUI-22`). |
| Phạm vi | **Đạt** — đúng `10/10` file trong bảng `03-plan.md` của `frontend` và `Test_Cases.xlsx` của `docs` ở giai đoạn `test`; không sửa file ngoài phạm vi. |
| Contract | **Đạt** (`contract_change: no`) — không sửa `backend` hay `api_contract`; bám đúng đặc tả `POST /catalog/medications/match` (`matched`, `low_confidence`, `no_match`, `items[0]`, `reasons`, `suggested_query`). |
| Bất biến kiến trúc | **Đạt** — tuân thủ Bất biến #1 (client không gọi Supabase trực tiếp, ảnh OCR xử lý hoàn toàn trên thiết bị) và `QD-39` dòng 68–70 (bắt buộc người dùng kiểm tra & xác nhận trước khi tạo lịch, không gán thuốc gần giống, xóa ảnh mã hóa & RAM ngay khi xác nhận/hủy/background/hết hạn 24h/401/rút consent). `wf-db-migration` và `wf-health-endpoint` không áp dụng. |
| Bảo mật | **Đạt** — không hardcode secret, không log dữ liệu nhạy cảm; xử lý fail-closed ở `401 unauthorized`, lỗi `cleanup`, thu hồi consent và đổi phiên (`_isLockedFailure`, zero-fill buffer RAM + `MemoryImage.evict()`, chống phản hồi muộn qua `_generation`, gỡ listener trước `ocr.close()`). Có 1 lưu ý `Low` khi ảnh hết hạn 24h ngay lúc giữ `_Screen.result`. |
| Xử lý lỗi | **Đạt** — không nuốt lỗi; phân nhánh rõ lỗi thử lại được (`canRetry`), lỗi ảnh không thử lại, hết hạn 24h và lỗi khóa fail-closed; có guard `_busy`, `_retryingGallery` và `mounted` sau các `await`. |
| Hiệu năng | **Đạt** — không có vấn đề hiển nhiên; `shouldRepaint` so sánh đúng thuộc tính thay đổi; `ScanBeam` lặp hữu hạn 30 chu kỳ và tôn trọng `disableAnimations`; `_retryOcr()` tái sử dụng văn bản OCR đã đọc khi gặp lỗi mạng/server. |
| Chất lượng test | **Đạt** — reviewer chạy lại độc lập `flutter test --no-pub test/features/medication_capture/ test/features/medication/scanned_schedule_test.dart`: **117 pass / 0 fail / 1 skip** (`ocr_web_id_test.dart:31` `skip: !kIsWeb`, có sẵn hợp lệ); phủ đủ đường thành công, đường lỗi, biên `360×640 1.3x`, TTL 24h và fail-closed `401`/`cleanup`/rút consent. Có 1 gợi ý `Low` tăng thêm assertion. |
| Dễ đọc và nhất quán | **Đạt** — tách sạch `scan_camera_overlay.dart` và `scan_failure_view.dart`, chuẩn hóa token `AppColors`/`AppTextStyles`/`AppSpacing`/`AppSizes`, `flutter analyze` trả **0 issues** (`No issues found!`). Có vài gợi ý `Low` nhỏ. |
| Đối chiếu 04/05 với log trong `evidence/` | **Đạt** — toàn bộ 18 file log trong `work/6.04-ocr-scan-redesign/evidence/` khớp 100% với số liệu báo cáo ở `04` và `05` (`implement-analyze.log`: 0 issues; `implement-medication-capture.log`: 115 pass / 0 fail / 1 skip; `implement-scanned-schedule.log`: 2 pass / 0 fail; `test-integration.log`: 117 pass / 0 fail / 1 skip; `implement-final-frontend.log`: 1787 pass / 15 fail / 2 skip với 15 ca fail ở 7 file module khác; `testcase-xlsx.log` / `testcase_xlsx.py validate`: `OCRUI: 22 test case — Pass 20, Fail 0, Pending 2`, `Test_Cases.xlsx` giữ nguyên 69 sheets & `Report` khớp công thức). |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Low | `frontend/mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart:153-179,985-987` | `_onOcrChanged()` return sớm khi `_screen != _Screen.failure`, nên nếu ảnh hết hạn TTL 24h xảy ra ngay khi người dùng giữ `_Screen.result` mở liên tục 24h (không ẩn app), file mã hóa đã được `OcrController` giải phóng nhưng buffer `_image` trong RAM chưa xóa ngay và `_ocr?.result?.reasons` đọc động có thể mất cờ `strengthUnverified` nếu rebuild. | Lưu `_strengthUnverified` trong `_applyOcrOutcome()` cùng `_checkReminder`, và xử lý `expiredImage`/`cleanup` trong `_onOcrChanged()` cả ở `_Screen.result` (kèm kiểm `identical(_ocr, ocr)`). |
| Low | `frontend/mobile/lib/features/medication_capture/presentation/widgets/ocr_single_result_card.dart:33-40` | Điều kiện hiển thị phần trăm đang kiểm `candidate.score > 0` thay vì `scorePercent > 0`; nếu `0 < score < 0.005`, pill sẽ hiển thị `'Đã nhận diện · 0% khớp'`. | Kiểm `scorePercent > 0` sau khi làm tròn. |
| Low | `frontend/mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart:363-391` | `_retake()` reset `_candidate`, `_busy`, `_failure` nhưng chưa reset `_checkReminder = false` tường minh (hiện luôn được ghi đè lại trong `_applyOcrOutcome()`). | Thêm `_checkReminder = false;` trong `_retake()`. |
| Low | `frontend/mobile/test/features/medication_capture/scan_medication_screen_test.dart:591-598,638,646,821-836` | (1) Test camera AC1 chưa assert trực tiếp `scrimPainter.cutout.size == cornersRect.size`; (2) test 401 chưa tap thử nút `'Đóng'` để kiểm chứng `pop` route; (3) tên và comment test dòng `638, 646` còn nhắc `_nameMissed` sau khi trường này đã được gỡ bỏ. | Bổ sung 2 assertion và cập nhật tên/comment test ở lần bảo trì sau. |
| Low | `frontend/mobile/lib/features/medication_capture/presentation/screens/scan_medication_screen.dart:533-584` | Nhánh `showingResult` (`recognizing`/`result`) dùng vị trí khung xem lại riêng (`top: 48`, `(maxHeight * .38).clamp(120, 220)`) thay vì `computeScanFrameRect(viewport)`, khiến khung dịch nhẹ theo chiều dọc khi chuyển từ camera sang sheet nhận diện. | Giữ nguyên để đảm bảo chiều cao cho `_resultSheet` trên màn nhỏ; cân nhắc gom helper nếu tinh chỉnh chuyển cảnh ở task sau. |

## 5. Mô tả PR

### Thứ tự commit & merge (theo `wf-git`)

1. **`frontend`** (`feat/6.04-ocr-scan-redesign` → `main`) — PR client
2. **`docs`** (`feat/6.04-ocr-scan-redesign` → `main`) — PR cập nhật sổ test case tổng `Test_Cases.xlsx`
3. **Superproject `DrugTime`** (`feat/6.04-ocr-scan-redesign` → `main`) — PR bump con trỏ `frontend` và `docs` (sau khi 2 PR trên đã merge; nếu squash/rebase merge thì cập nhật lại con trỏ tới SHA đã merge trên `origin/main` trước khi merge PR superproject) kèm thư mục `work/6.04-ocr-scan-redesign/`

---

### PR 1 — Submodule `frontend` (`feat/6.04-ocr-scan-redesign` → `main`)

**Tiêu đề:** `feat(medication_capture): redesign and complete blister pack OCR scan and result screens (6.04)`

**Mô tả:**
- **Task:** `6.04-ocr-scan-redesign` (`PB31` — Mobile: Redesign & complete Blister Pack Scan (OCR) & medication recognition result screens)
- **Liên kết PR:** Đi kèm PR cập nhật `Test_Cases.xlsx` ở `DrugTime-docs` (`feat/6.04-ocr-scan-redesign`) và PR bump submodule ở `DrugTime` (`feat/6.04-ocr-scan-redesign`).
- **Tóm tắt thay đổi:**
  - Tách `scan_camera_overlay.dart`: dùng chung `computeScanFrameRect` cho lớp phủ tối 4 phía (`AppColors.cameraScrim`), 4 góc 28px, tia quét `ScanBeam` và vùng cắt `CaptureCropRect`; bổ sung `ScanGuidePill` đặt dưới khung không đè khung trên `360×640` với `textScaler = 1.3`.
  - Chuẩn hóa toàn bộ màn hình `ScanMedicationScreen` theo 2 bộ token nền tối / nền sáng từ `app_theme.dart`; bỏ chiều cao cố định `112px` ở header, chuẩn hóa nút `×` tròn nền nhạt, cải thiện thẻ hướng dẫn quyền/lỗi camera (`denied` / `permanentlyDenied` / `camera.error`) không thêm nút `'Cho phép camera'`.
  - Chuẩn hóa `RecognitionSteps` (`17px`, active `AppColors.brand` `#01554F` Bold) và banner bảo mật `14px Medium` trên `S07-O2`; chuẩn hóa `OcrSingleResultCard` thay badge góc phải cũ bằng pill trạng thái `matched` (`AppColors.safeBg`/`safe`) và `low_confidence` (`AppColors.cautionBg`/`cautionText` `#92400E`) kèm `AppShadows.cardElevation`.
  - Tách `scan_failure_view.dart` (`S07-O3e`): sửa lỗi tương phản header sang `AppColors.brand` (`#01554F`), vòng minh họa `160×160`, thẻ gợi ý 2 huy hiệu icon `40×40` `17px Medium`, thanh đáy nền `AppColors.surface`.
  - Thêm `OcrController.canRetry` và luồng `_retryOcr()` cho lỗi tạm thời (`network`, `server`, `unavailable`, `recognition`), lắng nghe `_onOcrChanged` xóa RAM khi hết hạn 24h và khóa fail-closed khi `401 unauthorized` / `cleanup` / thu hồi consent (`QD-39`).
- **Kiểm thử tự động (AC1–AC9):**
  - `cd frontend/mobile && flutter analyze lib/features/medication_capture test/features/medication_capture` → `0 issues`
  - `cd frontend/mobile && flutter test test/features/medication_capture/ test/features/medication/scanned_schedule_test.dart` → **117 pass / 0 fail / 1 skip** (`ocr_web_id_test.dart` `!kIsWeb`)
- **Hướng dẫn kiểm thử thủ công trên Android thật (`AC10`):**
  1. `TC-OCRUI-21`: Mở `Thêm thuốc` → kiểm tra lớp phủ scrim 4 phía, tia quét, pill hướng dẫn → chụp vỉ thuốc rõ nét (ánh sáng thường) → xác nhận sheet `S07-O2`, thẻ `S07-O2r` có pill xanh lá `'Đã nhận diện · XX% khớp'` → bấm `'Đúng thuốc này'` sang bước 2/3 Lịch uống.
  2. `TC-OCRUI-22`: Bật cỡ chữ hệ thống ~130% → chụp mờ/loá để kiểm tra màn lỗi `S07-O3e` (độ tương phản header `#01554F`, thẻ gợi ý không tràn) → tắt mạng, chụp rõ để hiện nút `'Thử lại'` → bật lại mạng và bấm `'Thử lại'` để xác nhận nhận diện lại không cần chụp mới.
- **Rủi ro & lưu ý:** Không đổi API contract (`contract_change: no`), không chạm `backend` hay DB. Có 5 lưu ý `Low` không chặn đã ghi ở `work/6.04-ocr-scan-redesign/06-review.md`.

---

### PR 2 — Submodule `docs` (`feat/6.04-ocr-scan-redesign` → `main`)

**Tiêu đề:** `test(docs): add OCRUI test cases for task 6.04-ocr-scan-redesign`

**Mô tả:**
- **Task:** `6.04-ocr-scan-redesign` (`PB31`)
- **Liên kết PR:** Merge cùng PR `frontend` (`feat/6.04-ocr-scan-redesign`), trước PR superproject `DrugTime`.
- **Tóm tắt thay đổi:** Gộp sheet `Quét vỉ & kết quả OCR` (`OCRUI`) vào `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` bằng `python .agents/scripts/testcase_xlsx.py merge 6.04-ocr-scan-redesign` (**22 test case: 20 Pass, 0 Fail, 2 Pending** thủ công `TC-OCRUI-21`, `TC-OCRUI-22`; giữ nguyên toàn bộ 68 sheet cũ và cập nhật `Report`).

---

### PR 3 — Superproject `DrugTime` (`feat/6.04-ocr-scan-redesign` → `main`)

**Tiêu đề:** `chore: bump frontend and docs for 6.04-ocr-scan-redesign`

**Mô tả:**
- **Task:** `6.04-ocr-scan-redesign` (`PB31`)
- **Thứ tự merge:** Merge **sau cùng**, sau khi PR `frontend` và PR `docs` đã merge vào `main` (đảm bảo con trỏ submodule trỏ tới commit đã có trên `origin/main`).
- **Tóm tắt thay đổi:**
  - Bump con trỏ submodule `frontend` và `docs` sang commit đã merge của `6.04-ocr-scan-redesign`.
  - Lưu đầy đủ artifact quy trình (`01-requirement.md` → `06-review.md`, `testcases.json`, `testcases.xlsx`, và `evidence/*.log`) trong `work/6.04-ocr-scan-redesign/`.
- **Lưu ý trước khi commit/push superproject:** Loại trừ toàn bộ file tồn đọng ngoài phạm vi (`DrugTime_Pilot_4.01/`, `execute_ducnt_plan/`, thay đổi chưa commit ở `backend/`).

## 6. Ghi chú cho quy trình

- **`wf-testcase` / `testcase_xlsx.py`:** Script đánh số bảng EP theo thứ tự toàn bộ lớp `valid` của mọi field trước rồi mới tới toàn bộ lớp `invalid` (ví dụ `1..5` rồi `6..13`); nên bổ sung ví dụ minh họa đánh số đa-field trong `wf-testcase/SKILL.md` để tránh đánh nhầm thứ tự tuần tự theo từng field.
- **Đồng bộ mã Sprint Backlog:** File `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.xlsx` vẫn đang ghi mã `6.04` là `PB33 (Simple Mode toggle)` trong khi danh sách Sprint 6 thực tế gán `6.04` cho `PB31`; team nên cập nhật lại file backlog trong `docs` để tránh lệch mã khi nghiệm thu Sprint 6.

## Bước tiếp theo

- Đang chờ: người dùng duyệt giai đoạn `review` (phiên reviewer `3e2c9d0d-ffc3-4c37-b436-ba32311131a1` đã kiểm toán độc lập toàn bộ diff, log và bộ test case kết luận **Đạt, kèm lưu ý** — 0 Critical, 0 High, 0 Medium, 5 Low).
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 6.04-ocr-scan-redesign review`, sau đó nếu đồng ý commit/push/tạo PR thì thực hiện theo thứ tự `wf-git` (`frontend` → `docs` → superproject) theo Mục 5.
- Cập nhật lần cuối: 2026-11-26 15:17, Antigravity
