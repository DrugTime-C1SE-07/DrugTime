---
task: 4.17-ocr-accuracy-test
stage: test
status: draft
---

# 4.17 · Test Report: OCR accuracy across multiple packaging samples (PB31)

> [!IMPORTANT]
> **THÔNG BÁO VỀ CHẾ ĐỘ THỰC THI (MOCK MODE)**:
> Toàn bộ kết quả trong báo cáo này được thực hiện ở **MOCK mode** (sử dụng in-memory `FakeCatalogReader` nạp schema & dữ liệu từ seed `10_knowledge_base.sql` và kết quả OCR thô decoupled từ `datasets/results/pilot-002/raw/*.json`).
> **Kết quả 100% là do mock pipeline đối sánh, chưa phải là kiểm thử trên ảnh chụp camera vật lý thời gian thực hay OCR engine trực tiếp trên thiết bị di động.**

## 1. Môi trường

- **Chế độ kiểm thử**: MOCK mode (In-memory Catalog Reader mô phỏng SQL adapter với accent-folding substring matching và trigram fuzzy matching).
- **Dữ liệu hạt giống**: `backend/supabase/seeds/10_knowledge_base.sql` (59 bản ghi thuốc chuẩn).
- **Tập mẫu thực nghiệm**: 33 mẫu bao bì độc lập (`datasets/results/pilot-002/raw/*.json`, `datasets/labels.xlsx`).
- **Lệnh chạy**:
  ```powershell
  python 04-implementation/run_accuracy_test.py --mock
  ```
- **Bằng chứng log**: [accuracy_report.log](file:///E:/DrugTIme_main/execute_ducnt_plan/work/4.17-ocr-accuracy-test/evidence/accuracy_report.log) (AGENTS.md §5).

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Nội dung tiêu chí | Kết quả kiểm chứng thực tế | Đánh giá |
|---|---|---|---|
| **AC1** | Tập 33 mẫu độc lập, bảng nhãn chuẩn xác 14 cặp, xuất bảng chi tiết | Xuất đủ 33 dòng với đầy đủ Image ID, Nhóm, Status Seed, Preselected ID, Status Diag, T1, T3, Score, Độ trễ ms | **Pass** |
| **AC2** | Góc nhìn 1: Đo lường đối sánh 10 mẫu có hoạt chất trong seed (Nhóm A1). Top-1 Active Ingredient Accuracy >= 70% | 7/10 mẫu đạt (70.0%), 100% `preselected_id = null` | **Pass** |
| **AC3** | Góc nhìn 1: Đo lường an toàn 23 mẫu ngoài seed (Nhóm A2..A4). 100% kích hoạt fallback an toàn theo PB31 và QD-39 (`preselected_id = null`) | 23/23 mẫu (100.0%) trả về `NO_MATCH` hoặc `LOW_CONFIDENCE` với `preselected_id = null` | **Pass** |
| **AC4** | Góc nhìn 2: Đo lường chẩn đoán thuật toán trên 14 cặp Ground Truth (Top-1/Top-3 >= 70%) & Độ trễ Median < 50ms | Top-1: 24/33 (72.7%), Top-3: 24/33 (72.7%), MRR = 0.727; Median latency: 6.75 ms (< 50ms) | **Pass** |
| **AC5** | Tuân thủ QD-33: Chỉ log metadata (status, top_score, candidate_count, reasons, elapsed_ms), không log rawText OCR thô | Không leak rawText trong log hệ thống, chỉ lưu metadata đo lường | **Pass** |
| **AC6** | Biên soạn và đồng bộ 6 test cases vào workbook tổng của dự án `Test_Cases.xlsx` | 6/6 test cases Pass | **Pass** |

## 3. Kịch bản chất lượng đã phủ

- **An toàn phân loại và không gán thuốc sai (QD-39 & PB31)**: Với 23 mẫu thuốc khác hàm lượng (A2) hoặc ngoài danh mục seed (A3, A4), hệ thống luôn trả về `status` là `no_match` hoặc `low_confidence` với `preselected_id = null`, bắt buộc người dùng tìm kiếm thủ công, tuyệt đối không tự ý chọn sẵn thuốc sai.
- **Bảo mật và Quyền riêng tư (QD-33)**: Chuỗi ký tự OCR thô trích xuất từ bao bì không bao giờ bị ghi vào log hệ thống hoặc lưu trữ vĩnh viễn; chỉ log metadata kỹ thuật.
- **Phản hồi tức thì (Latency Constraint)**: Độ trễ xử lý matching trung vị đạt **6.75 ms** (< 50 ms budget), P95 đạt **21.02 ms** (< 100 ms budget).

## 4. Bảng kết quả chi tiết từng mẫu (Trích xuất từ accuracy_report.log)

| Image ID | Tên thuốc nhãn | Nhóm | Trạng thái Seed | Preselected | Trạng thái Diag | T1 | T3 | Score | Độ trễ (ms) |
|---|---|---|---|---|---|---|---|---|---|
| `decolgen_forte_box_001` | Decolgen Forte | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.521 | 6.38 |
| `decolgen_forte_box_002` | Decolgen Forte | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 2.64 |
| `decolgen_forte_blister_001` | Decolgen Forte | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 10.71 |
| `decolgen_forte_blister_002` | Decolgen Forte | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.510 | 12.09 |
| `decolgen_forte_blister_003` | Decolgen Forte | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.512 | 10.95 |
| `efferalgan_box_001` | Efferalgan | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.958 | 6.95 |
| `efferalgan_box_002` | Efferalgan | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.975 | 3.71 |
| `efferalgan_blister_001` | Efferalgan | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.959 | 13.33 |
| `efferalgan_blister_002` | Efferalgan | A1 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.653 | 7.73 |
| `strepsils_box_001` | Strepsils Original | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.525 | 2.16 |
| `strepsils_box_002` | Strepsils Original | A4 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 1.48 |
| `strepsils_blister_001` | Strepsils Original | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.550 | 0.84 |
| `strepsils_blister_002` | Strepsils Original | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.519 | 10.56 |
| `tiffy_dey_box_001` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 9.11 |
| `tiffy_dey_box_002` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 1.75 |
| `tiffy_dey_blister_001` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 22.62 |
| `tiffy_dey_blister_002` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 2.78 |
| `atorvastatin_10_blister_001` | Atorvastatin | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.968 | 13.78 |
| `atorvastatin_10_blister_002` | Atorvastatin | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.772 | 19.33 |
| `atorvastatin_10_blister_003` | Atorvastatin | A1 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 2.19 |
| `atorvastatin_10_box_001` | A.TATORVASTATIN | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.971 | 4.38 |
| `atorvastatin_10_box_002` | Atorvastatin | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.965 | 5.67 |
| `atorvastatin_10_box_003` | Atorvastatin | A1 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.965 | 6.75 |
| `bisoprolol_2_point_5_blister_001` | Bisoheart | A2 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 0.03 |
| `bisoprolol_2_point_5_blister_002` | A.TBisoprolol | A2 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.753 | 8.30 |
| `bisoprolol_2_point_5_box_001` | A.TBisoprolol | A2 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.585 | 3.33 |
| `bisoprolol_2_point_5_box_002` | A.TBisoprolol | A2 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.521 | 3.38 |
| `candesartan_htz_32_25_blister_001` | Candesartan Krka | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.975 | 9.02 |
| `candesartan_htz_32_25_box_001` | A.TCANDESARTAN HTZ | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.642 | 5.01 |
| `candesartan_htz_32_25_box_002` | ACANTANHTZ | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.971 | 3.70 |
| `cilnidipine_5_blister_001` | Cildip | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.960 | 21.02 |
| `cilnidipine_5_blister_002` | Cilapress | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.957 | 8.79 |
| `hapacol_extra_front_01` | Hapacol Extra | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.993 | 8.83 |

## 5. Phân tích kết quả theo Condition Tags

Dựa trên dữ liệu điều kiện chụp thực nghiệm trích xuất từ `datasets/annotations.v1.csv`:

| Tiêu chí phân loại điều kiện | Số lượng mẫu | Số mẫu Top-1 đạt | Tỷ lệ chính xác (%) | Nhận xét phân tích kỹ thuật |
|---|---|---|---|---|
| **Hộp thuốc (`box`)** | 16 | 12 | **75.0%** | Bề mặt in phẳng, tương phản cao, ít biến dạng quang học. |
| **Vỉ thuốc (`blister`)** | 17 | 12 | **70.6%** | Bề mặt nhôm/nhựa gồ ghề, dễ bị phản xạ ánh sáng làm mờ chữ. |
| **Chụp thẳng góc (`non-oblique`)** | 21 | 17 | **81.0%** | Hình ảnh trực diện, tỷ lệ ký tự chuẩn, OCR trích xuất chính xác. |
| **Chụp góc nghiêng (`oblique view`)** | 12 | 7 | **58.3%** | Bị biến dạng phối cảnh (perspective distortion), ký tự bị co giãn hoặc đứt nét. |
| **Ảnh sản phẩm phẳng (`product image`)** | 17 | 15 | **88.2%** | Điều kiện tối ưu, nền đơn sắc, tỷ lệ nhận diện cao nhất. |
| **Ảnh cầm tay (`hand-held`)** | 16 | 9 | **56.2%** | Bị rung tay, ngón tay che một phần viền và nền có texture phức tạp. |

### Phân tích chi tiết 9 ca không khớp trong benchmark chẩn đoán

1. `bisoprolol_2_point_5_blister_001`: Ảnh vỉ quá mờ/tối, OCR engine trả về chuỗi rỗng `""`. Hệ thống xử lý an toàn với `status = NO_MATCH`.
2. `strepsils_box_002`: Chụp nghiêng góc mạnh, chữ bị méo khiến OCR đọc thành `ESrepsils` -> trượt ngưỡng fuzzy matching.
3. `decolgen_forte_box_002`: Chữ in nghệ thuật trên hộp khiến OCR đọc nhầm chữ `n` thành `r` (`Decolger`).
4. `decolgen_forte_blister_001`: Mực in trên vỉ nhôm bị bong tróc một phần, thiếu token tên thuốc.
5. `tiffy_dey_box_001, 002` & `tiffy_dey_blister_001, 002` (4 mẫu): Font chữ cách điệu trên bao bì Tiffy Dey khiến OCR đọc dính thành `TIFFYoEY` hoặc thiếu khoảng trắng.
6. `atorvastatin_10_blister_003`: Mặt nhôm vỉ thuốc phản quang làm lóa sáng toàn bộ dòng tên biệt dược và hoạt chất.

## 6. Giới hạn thực nghiệm & Kết luận (Limitations & Verdict)

### Giới hạn thực nghiệm (Limitations)

1. **Chưa có ảnh thật trực tiếp trong pipeline runtime**: Toàn bộ quá trình kiểm thử sử dụng dữ liệu văn bản thô (rawText JSON) được trích xuất sẵn từ đợt chạy thực nghiệm pilot-002, chưa kết nối trực tiếp với luồng chụp ảnh từ camera vật lý của thiết bị di động trong phiên test này.
2. **Chưa có Real OCR Engine trên thiết bị**: Kiểm thử thực hiện decoupled trên backend matching logic, chưa tích hợp Google ML Kit Text Recognition chạy on-device realtime trên app Flutter.
3. **Môi trường Database Mock**: Đánh giá dựa trên `FakeCatalogReader` in-memory nạp dữ liệu từ seed SQL chuẩn, chưa kiểm thử độ trễ mạng thực tế qua kết nối PostgreSQL/Docker.

### Kết luận kiểm thử (Verdict)

> **VERDICT**: **PASS (mock mode) – chờ ảnh thật để chạy real mode**

Hệ thống matching backend đáp ứng xuất sắc các bất biến an toàn cốt lõi của PB31 và QD-39:
- Đạt **100% (23/23 mẫu) kích hoạt fallback an toàn** chuyển sang tìm kiếm thủ công khi thuốc ngoài danh mục, không bao giờ tự ý gán sai thuốc (`preselected_id = null`).
- Đạt **70.0% độ chính xác nhận diện hoạt chất** trên tập có trong Seed (Nhóm A1).
- Năng lực thuật toán chẩn đoán đạt **72.7% Top-1/Top-3** trên 14 cặp từ điển, độ trễ phản hồi tức thì **6.75 ms**.

---

## Bước tiếp theo

- Đang chờ: Reviewer xem xét báo cáo kiểm thử `05-test-report.md`.
- Việc cần làm: Người dùng / Reviewer chạy lệnh phê duyệt trong terminal riêng:
  ```powershell
  python .agents/scripts/gate.py approve 4.17-ocr-accuracy-test test
  ```
  *(Gõ `4.17-ocr-accuracy-test` khi console yêu cầu xác nhận)*
- Cập nhật lần cuối: 2026-11-16 13:17, Antigravity
