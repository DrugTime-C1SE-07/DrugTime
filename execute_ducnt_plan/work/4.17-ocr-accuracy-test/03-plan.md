---
task: 4.17-ocr-accuracy-test
stage: plan
status: approved
approved_by: Duc1445
approved_at: 2026-11-14 10:33 +0700
content_hash: sha256:91a7c5f2ee7e1d5d
inputs:
  01-requirement.md: sha256:95d4f73b8f3d2a81
---

# 4.17 · Plan: Test OCR accuracy across multiple packaging samples (PB31)

## 1. Giải pháp

Xây dựng bộ kịch bản kiểm thử đo lường định lượng và script benchmark có khả năng tái tạo độc lập (AGENTS.md §5 & §6) cho pipeline đối sánh OCR thuốc (`normalize_ocr_text` → `lookup_ocr_candidates` → `score_ocr_matches`) trên tập **33 mẫu bao bì thực nghiệm độc lập** (đã tinh lọc loại bỏ 16 mẫu trùng lặp và tích hợp mẫu thực IMG_049 Hapacol Extra theo yêu cầu Reviewer).

Toàn bộ quy trình kiểm thử được thiết kế theo 4 khối cốt lõi:

1. **Khối dữ liệu & Toàn vẹn hình ảnh (Data Integrity & Decoupling)**:
   - Xác thực cấu trúc 33 ảnh mẫu bao bì thực nghiệm trong `datasets/images/` (gồm 12 nhóm bao bì sau khi bổ sung `hapacol_extra/`).
   - Cung cấp cơ chế kiểm chứng toàn vẹn file ảnh bằng mã băm SHA256 đối soát với `datasets/manifest.v1.json` (33/33 ảnh khớp `image_sha256`, bao gồm IMG_049 `hapacol_extra_front_01.jpg`).
   - Tận dụng cơ chế decoupled raw OCR: pipeline kiểm thử benchmark sử dụng trực tiếp 33 kết quả OCR thô đối chiếu với bảng nhãn `datasets/labels.xlsx` (đã chuẩn hóa đúng 33 dòng độc lập kèm cột `active_ingredient`), đảm bảo tái tạo 100% tất định mà không phụ thuộc vào thiết bị di động hay camera vật lý.

2. **Khối kịch bản đo lường đa chiều (Multi-Perspective Accuracy Measurement)**:
   - **Góc nhìn 1 — Báo cáo chính thức trên Seed thực tế (`10_knowledge_base.sql`)**:
     + *Nhóm A1 (10 mẫu)*: Có hoạt chất và hàm lượng tương ứng trong seed (Efferalgan 500mg: 4 mẫu; Atorvastatin 10mg: 6 mẫu). Đo lường Top-1 và Top-3 Active Ingredient Accuracy và Strict Brand Accuracy với mẫu số cố định = 10.
     + *Nhóm A2, A3, A4 (23 mẫu)*: Thuốc khác hàm lượng hoặc ngoài danh mục seed (A2: 4 mẫu; A3: 12 mẫu; A4: 7 mẫu). Đo lường Tỷ lệ an toàn (Safety Fallback Rate) với mẫu số cố định = 23. Yêu cầu bắt buộc: 100% các mẫu này phải trả về `status = "no_match"` hoặc `status = "low_confidence"` với `preselected_id = null`, kích hoạt tìm kiếm thủ công theo PB31 và QD-39.
   - **Góc nhìn 2 — Báo cáo chẩn đoán thuật toán (Diagnostic Benchmark trên 14 cặp Catalog đầy đủ)**:
     + Chạy với catalog giả lập 14 cặp sản phẩm/hàm lượng từ nhãn với mẫu số cố định = 33.
     + Đo lường năng lực chuẩn hóa chuỗi và fuzzy matching cốt lõi: Top-1, Top-3 Diagnostic Accuracy và MRR (Mean Reciprocal Rank), đối chiếu với chỉ tiêu kỹ thuật nội bộ đề xuất Top-3 > 85%.
   - **Đo lường độ trễ (Latency Benchmark)**:
     + Thu thập thời gian xử lý (`elapsed_ms`) từng mẫu, tính toán average, median, và p95 latency.

3. **Khối script benchmark tái tạo được (Deterministic Benchmark Runner)**:
   - Viết bộ test unit/benchmark tại `backend/tests/unit/test_ocr_accuracy_benchmark.py` và script thực thi `backend/scripts/benchmark_ocr_accuracy.py`.
   - Script hỗ trợ chạy độc lập một lệnh, xuất bảng kết quả tổng hợp chi tiết ra màn hình console và tự động lưu evidence log chuẩn vào `work/4.17-ocr-accuracy-test/evidence/accuracy_report.log`.

4. **Khối tài liệu hóa và đồng bộ chất lượng (Quality & Documentation)**:
   - Tổng hợp số liệu và phân tích các trường hợp nhận diện lỗi vào `work/4.17-ocr-accuracy-test/04-impl-notes.md` và `work/4.17-ocr-accuracy-test/05-test-report.md`.
   - Biên soạn test case chi tiết bằng `work/4.17-ocr-accuracy-test/testcases.json` và gộp vào file tổng của dự án `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` bằng công cụ `testcase_xlsx.py` (`wf-testcase`).

---

## 1a. Quyết định nghiệp vụ áp dụng

| Mã quyết định | Nguồn quy định | Tóm tắt quy tắc | AC liên quan | Bước Pn | Test kiểm chứng |
|---|---|---|---|---|---|
| **PB31** | `Product-and-Sprint-backlog-DrugTime.xlsx` (Sprint 4 Backlog & Product Backlog) | Quét bao bì trên thiết bị di động; khi confidence thấp hoặc không khớp thì chuyển sang tìm kiếm thủ công (manual search fallback) với truy vấn gợi ý. | AC3 | P3 | `test_safety_fallback_out_of_seed_groups_a2_a3_a4` |
| **QD-39** | `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md:68` | Mọi kết quả OCR và nhập tay phải được người dùng kiểm tra lại tên thuốc, hàm lượng, đơn vị, liều trước khi tạo lịch. Thuốc chưa có trong danh mục → không gán thuốc gần giống để vượt chặn (`preselected_id = null`). | AC1, AC3 | P3, P4 | `test_safety_fallback_out_of_seed_groups_a2_a3_a4` |
| **QD-33** | `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` | Dữ liệu văn bản OCR và ảnh không lưu trữ vĩnh viễn và không log chuỗi OCR vào hệ thống; chỉ log metadata (status, top_score, candidates count, reasons, elapsed_ms). | AC5 | P5 | `test_ocr_benchmark_logging_metadata_only` |
| **Contract `/catalog/medications/match`** | `api_contract/openapi.json:2160-2240` | Quy định 3 trạng thái: `matched` (có `preselected_id`), `low_confidence` (`preselected_id = null`), `no_match` (`preselected_id = null`, items rỗng). Hỗ trợ cờ `strength_unverified` khi tên thuốc chỉ có 1 hàm lượng trong catalog. | AC1, AC2, AC3 | P2, P3 | `test_in_seed_accuracy_group_a1`, `test_safety_fallback_out_of_seed_groups_a2_a3_a4` |

---

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/4.17-ocr-accuracy-test/01-requirement.md` | Đã cập nhật tinh lọc về đúng 33 mẫu độc lập (sau khi xử lý Lỗi A và Lỗi B theo Reviewer), quy định 6 AC, phân loại thành 4 nhóm A1 (10), A2 (4), A3 (12), A4 (7). |
| `datasets/manifest.v1.json` | Đã cập nhật danh sách 33 ảnh mẫu vật lý (kèm IMG_049 `hapacol_extra_front_01.jpg`), `total_images = 33`, 100% hash SHA256 đã khớp với file trên đĩa. |
| `datasets/annotations.v1.csv` | Đã xóa 16 bản ghi duplicate (IMG_033–IMG_048) theo Phương án (a), bổ sung dòng IMG_049 Hapacol Extra, tổng cộng đúng 33 dòng dữ liệu. |
| `datasets/labels.xlsx` | 33 dòng nhãn (từ dòng 3 đến dòng 35), gồm 6 cột: `image_id`, `relative_path`, `drug_name`, `strength`, `active_ingredient`. 100% dòng đã được nạp đầy đủ. |
| `datasets/images/README.md` | Mô tả các thư mục nhóm bao bì thuốc thực nghiệm (12 nhóm sau khi thêm `hapacol_extra/`) và nguyên tắc kiểm thử decoupled. |
| `datasets/results/pilot-002/raw/*.json` | Chứa kết quả nhận diện text thô trích xuất từ ML Kit cho các mẫu thực nghiệm. Đã tích hợp raw JSON cho Hapacol Extra từ kho pilot thực tế. |
| `backend/tests/unit/test_ocr_real_output.py` | Unit test từ task 4.14 chuẩn hóa raw OCR text, có fixture `REAL_OCR_SAMPLES` nạp các mẫu thực nghiệm. |
| `backend/src/drugtime/modules/catalog/application/match_ocr_text.py` | Pipeline matching nhận `(uow, raw_text, limit, policy, reader)` -> trả về `OcrMatchOutcome(items, status, top_score, preselected_id, reasons, suggested_query)`. |
| `backend/tests/unit/test_catalog_ocr_match_scoring.py` | `FakeReader` mô phỏng đầy đủ hành vi substring matching và trigram fuzzy fallback in-memory, cho phép benchmark độc lập, nhanh chóng và tất định mà không cần khởi động Postgres/Docker. |
| `backend/supabase/seeds/10_knowledge_base.sql` | Chứa 59 thuốc mẫu chính thức trong cơ sở tri thức của hệ thống. |
| `.agents/scripts/testcase_xlsx.py` | Công cụ chuẩn của dự án để validate, build và merge test case vào `Test_Cases.xlsx`. |

---

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| `superproject` | `datasets/manifest.v1.json` | Sửa | Cập nhật và kiểm chứng mã băm SHA256 cho toàn bộ 33 ảnh mẫu |
| `superproject` | `datasets/annotations.v1.csv` | Sửa | Chuẩn hóa danh sách 33 mẫu nhãn độc lập (loại bỏ 16 duplicate, thêm IMG_049) |
| `superproject` | `datasets/images/**` | Thêm / Sửa | Lưu trữ và xác thực cấu trúc 33 ảnh bao bì mẫu vật lý trong các nhóm thư mục |
| `superproject` | `datasets/labels.xlsx` | Sửa | Chuẩn hóa bảng nhãn ground-truth 33 dòng gồm 6 cột (kèm `active_ingredient`) |
| `superproject` | `datasets/results/pilot-002/raw/**` | Thêm / Sửa | Lưu trữ và chuẩn hóa dữ liệu raw OCR text trích xuất từ thiết bị |
| `backend` | `tests/unit/test_ocr_accuracy_benchmark.py` | Thêm | Bộ test đo lường định lượng Top-1/Top-3 accuracy, safety fallback rate, latency trên 33 mẫu OCR |
| `backend` | `scripts/benchmark_ocr_accuracy.py` | Thêm | Script thực thi benchmark độc lập, xuất bảng tổng hợp chi tiết và evidence log |
| `docs` | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | Sửa | Cập nhật các test case độ chính xác OCR PB31 vào workbook tổng bằng `testcase_xlsx.py merge` |

---

## 4. Checklist

- [ ] P1 [superproject] Xác thực cấu trúc 33 ảnh mẫu bao bì trong `datasets/images/` (gồm thư mục mới `hapacol_extra/box/`), kiểm chứng tính sẵn sàng và toàn vẹn của các file ảnh gốc; chạy script kiểm tra đối soát và cập nhật mã băm `image_sha256` của từng ảnh trong `datasets/manifest.v1.json` (33 ảnh, `total_images = 33`) — file: `datasets/manifest.v1.json`, `datasets/annotations.v1.csv`, `datasets/images/**` — AC: AC1 — xong khi: script kiểm tra xác nhận 33/33 ảnh tồn tại, khớp cấu trúc thư mục và 33/33 mã SHA256 trong manifest khớp chính xác với file trên đĩa.
- [ ] P2 [backend] Xây dựng benchmark test suite và runner script có khả năng tái tạo độc lập (`tests/unit/test_ocr_accuracy_benchmark.py` và `scripts/benchmark_ocr_accuracy.py`) tải 33 mẫu OCR từ `datasets/results/pilot-002/raw/*.json` và nhãn từ `datasets/labels.xlsx` — file: `backend/tests/unit/test_ocr_accuracy_benchmark.py`, `backend/scripts/benchmark_ocr_accuracy.py` — AC: AC1 — xong khi: script nạp thành công 33 mẫu raw JSON và đối chiếu chính xác với 33 nhãn ground truth.
- [ ] P3 [backend] Thực thi benchmark Góc nhìn 1 (Đánh giá trên Seed thực tế `10_knowledge_base.sql`) đo lường Top-1/Top-3 cho 10 mẫu nhóm A1 và đo lường Safety Fallback Rate cho 23 mẫu nhóm A2/A3/A4 — file: `backend/scripts/benchmark_ocr_accuracy.py`, `backend/tests/unit/test_ocr_accuracy_benchmark.py` — AC: AC2, AC3 — xong khi: tính toán và xuất rõ tỷ lệ Top-1/Top-3 cho nhóm A1 (mẫu số = 10) và tỷ lệ fallback an toàn cho nhóm A2..A4 (mẫu số = 23), kiểm chứng `preselected_id = null` cho toàn bộ các ca fallback.
- [ ] P4 [backend] Thực thi benchmark Góc nhìn 2 (Diagnostic Benchmark trên Catalog 14 cặp đầy đủ) đo lường Top-1, Top-3, MRR và phân vị độ trễ (average, median, p95 elapsed_ms) cho toàn bộ 33 mẫu — file: `backend/scripts/benchmark_ocr_accuracy.py`, `backend/tests/unit/test_ocr_accuracy_benchmark.py` — AC: AC4 — xong khi: xuất kết quả Top-1, Top-3 trên 33 mẫu chẩn đoán, đối chiếu minh bạch với chỉ tiêu kỹ thuật nội bộ đề xuất Top-3 > 85%, xuất bảng phân vị độ trễ.
- [ ] P5 [backend] Xuất báo cáo tổng hợp chi tiết từng mẫu ra console và ghi nhận vào evidence log `work/4.17-ocr-accuracy-test/evidence/accuracy_report.log` — file: `work/4.17-ocr-accuracy-test/evidence/accuracy_report.log` — AC: AC5 — xong khi: log được ghi đầy đủ bảng kết quả 33 mẫu và các chỉ số đo lường.
- [ ] P6 [docs] Biên soạn test spec `work/4.17-ocr-accuracy-test/testcases.json`, tạo `testcases.xlsx` và thực hiện `testcase_xlsx.py merge 4.17-ocr-accuracy-test` để cập nhật vào `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` — file: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`, `work/4.17-ocr-accuracy-test/testcases.json` — AC: AC6 — xong khi: lệnh `testcase_xlsx.py validate`, `build`, và `merge` đều thoát mã 0.
- [ ] P7 [work] Soạn thảo ghi chú triển khai `work/4.17-ocr-accuracy-test/04-impl-notes.md`, tổng hợp số liệu đo lường, phân tích các trường hợp lỗi/giới hạn thuật toán và đối chiếu checklist — file: `work/4.17-ocr-accuracy-test/04-impl-notes.md` — AC: AC1, AC2, AC3, AC4, AC5 — xong khi: hoàn tất `04-impl-notes.md` với đầy đủ bằng chứng, sẵn sàng cho review giai đoạn implement.

---

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `test_load_and_validate_33_samples_and_labels` | AC1 | `backend` |
| `test_in_seed_accuracy_group_a1` | AC2 | `backend` |
| `test_safety_fallback_out_of_seed_groups_a2_a3_a4` | AC3 | `backend` |
| `test_diagnostic_catalog_accuracy_and_latency` | AC4 | `backend` |
| `test_ocr_benchmark_logging_metadata_only` | AC5 | `backend` |

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| `test_ocr_matching_end_to_end_on_real_samples` | AC1, AC5 | Chạy kiểm thử toàn bộ 33 mẫu raw OCR qua pipeline `match_ocr_text` hoàn chỉnh, kiểm tra không có crash và log metadata hợp lệ |

---

## 6. Migration

Không có. Task này chỉ đo lường và kiểm thử độ chính xác trên pipeline hiện có, không thay đổi schema database.

---

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| `superproject` | `test/4.17-ocr-accuracy-test` |
| `backend` | `test/4.17-ocr-accuracy-test` |
| `docs` | `test/4.17-ocr-accuracy-test` |

---

## 8. Rủi ro

1. **Chênh lệch giữa môi trường In-memory và Postgres thật**:
   - *Rủi ro*: Thuật toán pg_trgm trên PostgreSQL có thể có khác biệt nhỏ về chỉ số tương đồng so với hàm Python `trigram_similarity`.
   - *Giảm thiểu*: Cả hai triển khai đều sử dụng chung ngưỡng `similarity_threshold = 0.3` và cùng thuật toán chuẩn hóa `normalize_ocr_text`. Script benchmark hỗ trợ chạy in-memory `FakeReader` đảm bảo tính tất định, nhanh chóng và không phụ thuộc Docker/Supabase local, đồng thời ghi rõ môi trường trong báo cáo.

2. **Hiểu lầm về chỉ tiêu định lượng Top-3 > 85%**:
   - *Rủi ro*: Người đọc có thể nhầm lẫn mốc 85% là tiêu chí DoD của backlog hoặc là độ chính xác trên toàn bộ thuốc thị trường.
   - *Giảm thiểu*: Báo cáo minh bạch tách bạch 2 góc nhìn: Góc nhìn 1 (Seed thật) đo trên 10 mẫu có trong seed và đo tỷ lệ an toàn trên 23 mẫu ngoài seed; Góc nhìn 2 (Chẩn đoán) đo trên 14 cặp từ điển đầy đủ để đánh giá thuật toán.

3. **Xung đột cấu trúc bảng `Test_Cases.xlsx`**:
   - *Rủi ro*: Khi merge test case vào file Excel tổng có thể làm sai lệch format hoặc hỏng công thức.
   - *Giảm thiểu*: Sử dụng script chuẩn của dự án `.agents/scripts/testcase_xlsx.py` với 3 bước nghiêm ngặt `validate` → `build` → `merge`.

---

## 9. Câu hỏi mở

Không có câu hỏi chặn. Tất cả định nghĩa mẫu số (10 in-seed, 23 safe fallback, 33 chẩn đoán) và giải pháp xử lý 16 duplicate đã được chốt đồng bộ.

---

## 10. Phát sinh

- **Xử lý Lỗi A (16 mẫu duplicate)**: Đã chọn Phương án (a) theo hướng dẫn của Reviewer: xóa 16 bản ghi duplicate khỏi `annotations.v1.csv` và `labels.xlsx`, tránh thổi phồng mẫu và sai lệch thống kê.
- **Xử lý Lỗi B (Mẫu IMG_049 Hapacol Extra)**: Đã bổ sung mẫu IMG_049 (`hapacol_extra_front_01.jpg`, Hapacol Extra: Paracetamol 500mg + Cafein 65mg) vào `manifest.v1.json`, cập nhật `total_images = 33` và nạp vào `annotations.v1.csv` và `labels.xlsx`.

---

## Bước tiếp theo

- Đang chờ: Reviewer xem xét bản kế hoạch kỹ thuật `03-plan.md` (33 mẫu độc lập).
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 4.17-ocr-accuracy-test requirement` và sau đó `python .agents/scripts/gate.py approve 4.17-ocr-accuracy-test plan` để chuyển sang giai đoạn `implement`.
- Cập nhật lần cuối: 2026-11-14 09:40, Antigravity
