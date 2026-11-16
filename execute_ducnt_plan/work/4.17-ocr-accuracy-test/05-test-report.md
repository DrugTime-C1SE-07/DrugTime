---
task: 4.17-ocr-accuracy-test
stage: test
status: approved
approved_by: Duc1445
approved_at: 2026-11-16 14:45 +0700
content_hash: sha256:6acf81f997930b3f
inputs:
  01-requirement.md: sha256:95d4f73b8f3d2a81
  03-plan.md: sha256:91a7c5f2ee7e1d5d
  04-impl-notes.md: sha256:f858084690ba58c3
---

# 4.17 · Test Report: OCR accuracy across multiple packaging samples (PB31)

> [!IMPORTANT]
> **THÔNG BÁO VỀ CHẾ ĐỘ THỰC THI (MOCK MODE)**:
> Toàn bộ kết quả trong báo cáo này được thực hiện ở **MOCK mode** (sử dụng in-memory `FakeCatalogReader` nạp schema & dữ liệu từ seed `10_knowledge_base.sql` và kết quả OCR thô decoupled từ `datasets/results/pilot-002/raw/*.json`).
> **Kết quả 100% là do mock pipeline đối sánh, chưa phải là kiểm thử trên ảnh chụp camera vật lý thời gian thực hay OCR engine trực tiếp trên thiết bị di động.**

## 1. Môi trường kiểm thử

- **Chế độ kiểm thử**: MOCK mode (In-memory Catalog Reader mô phỏng SQL adapter với accent-folding substring matching và trigram fuzzy matching).
- **Dữ liệu hạt giống**: `backend/supabase/seeds/10_knowledge_base.sql` (59 bản ghi thuốc chuẩn).
- **Tập mẫu thực nghiệm**: 33 mẫu bao bì độc lập (`datasets/results/pilot-002/raw/*.json`, `datasets/labels.xlsx`).
- **Lệnh thực thi kiểm thử**:
  - Mock benchmark: `python 04-implementation/run_accuracy_test.py --mock`
  - Unit tests: `python -m pytest 04-implementation/test_metrics.py -v`
- **Bằng chứng log thực tế**:
  - [mock-accuracy-test.log](file:///E:/DrugTIme_main/execute_ducnt_plan/work/4.17-ocr-accuracy-test/evidence/mock-accuracy-test.log) (Log output của mock test)
  - [unit-test-metrics.log](file:///E:/DrugTIme_main/execute_ducnt_plan/work/4.17-ocr-accuracy-test/evidence/unit-test-metrics.log) (5/5 unit tests passed)
  - [accuracy_report.log](file:///E:/DrugTIme_main/execute_ducnt_plan/work/4.17-ocr-accuracy-test/evidence/accuracy_report.log) (Bảng tổng hợp chi tiết)

## 2. Bảng 4 chỉ số đo lường cốt lõi (4 Core Metrics)

| STT | Chỉ số đo lường | Tập mẫu & Mẫu số | Kết quả đo thực tế | Chỉ tiêu đề xuất | Đánh giá |
|:---:|---|---|---|---|---|
| **1** | **In-Seed Active Ingredient Accuracy** | Nhóm A1 ($N = 10$ mẫu: Efferalgan 500mg, Atorvastatin 10mg) | **7/10 mẫu đạt (70.0%)**<br>(100% `preselected_id = null`) | $\ge 70.0\%$ | **PASS** |
| **2** | **Safety Fallback Rate (PB31 / QD-39)** | Nhóm A2, A3, A4 ($N = 23$ mẫu: ngoài seed / khác hàm lượng) | **23/23 mẫu đạt (100.0%)**<br>(100% trả về `NO_MATCH` hoặc `LOW_CONFIDENCE` với `preselected_id = null`) | $100\%$ | **PASS** |
| **3** | **Diagnostic Algorithm Accuracy & MRR** | Toàn bộ $N = 33$ mẫu (đối chiếu danh mục 14 cặp Ground Truth) | **Top-1: 24/33 (72.7%)**<br>**Top-3: 24/33 (72.7%)**<br>**MRR: 0.727** | $\ge 70.0\%$ | **PASS** |
| **4** | **Độ trễ xử lý matching (Latency Budget)** | Phân vị độ trễ trên $N = 33$ mẫu | **Median (p50): 6.72 ms**<br>**Average: 6.65 ms**<br>**P95: 14.07 ms** | Median $< 50\text{ ms}$<br>P95 $< 100\text{ ms}$ | **PASS** |

## 3. Phân tích kết quả theo Condition Tags

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

## 4. Bảng kết quả chi tiết từng mẫu (Trích xuất từ accuracy_report.log)

| Image ID | Tên thuốc nhãn | Nhóm | Trạng thái Seed | Preselected | Trạng thái Diag | T1 | T3 | Score | Độ trễ (ms) |
|---|---|---|---|---|---|---|---|---|---|
| `decolgen_forte_box_001` | Decolgen Forte | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.521 | 4.56 |
| `decolgen_forte_box_002` | Decolgen Forte | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 2.42 |
| `decolgen_forte_blister_001` | Decolgen Forte | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 6.72 |
| `decolgen_forte_blister_002` | Decolgen Forte | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.510 | 11.45 |
| `decolgen_forte_blister_003` | Decolgen Forte | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.512 | 10.60 |
| `efferalgan_box_001` | Efferalgan | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.958 | 7.35 |
| `efferalgan_box_002` | Efferalgan | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.975 | 3.47 |
| `efferalgan_blister_001` | Efferalgan | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.959 | 13.01 |
| `efferalgan_blister_002` | Efferalgan | A1 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.653 | 7.70 |
| `strepsils_box_001` | Strepsils Original | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.525 | 2.16 |
| `strepsils_box_002` | Strepsils Original | A4 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 1.42 |
| `strepsils_blister_001` | Strepsils Original | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.550 | 0.83 |
| `strepsils_blister_002` | Strepsils Original | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.519 | 10.55 |
| `tiffy_dey_box_001` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 7.88 |
| `tiffy_dey_box_002` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 1.20 |
| `tiffy_dey_blister_001` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 13.83 |
| `tiffy_dey_blister_002` | Tiffy Dey | A3 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 2.62 |
| `atorvastatin_10_blister_001` | Atorvastatin | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.968 | 10.51 |
| `atorvastatin_10_blister_002` | Atorvastatin | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.772 | 14.07 |
| `atorvastatin_10_blister_003` | Atorvastatin | A1 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 1.93 |
| `atorvastatin_10_box_001` | A.TATORVASTATIN | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.971 | 4.03 |
| `atorvastatin_10_box_002` | Atorvastatin | A1 | `LOW_CONFIDENCE` | null | `LOW_CONFIDENCE` | Y | Y | 0.965 | 5.04 |
| `atorvastatin_10_box_003` | Atorvastatin | A1 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.965 | 5.23 |
| `bisoprolol_2_point_5_blister_001` | Bisoheart | A2 | `NO_MATCH` | null | `NO_MATCH` | N | N | None | 0.02 |
| `bisoprolol_2_point_5_blister_002` | A.TBisoprolol | A2 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.753 | 7.65 |
| `bisoprolol_2_point_5_box_001` | A.TBisoprolol | A2 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.585 | 2.95 |
| `bisoprolol_2_point_5_box_002` | A.TBisoprolol | A2 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.521 | 3.16 |
| `candesartan_htz_32_25_blister_001` | Candesartan Krka | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.975 | 10.48 |
| `candesartan_htz_32_25_box_001` | A.TCANDESARTAN HTZ | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.642 | 5.59 |
| `candesartan_htz_32_25_box_002` | ACANTANHTZ | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.971 | 6.85 |
| `cilnidipine_5_blister_001` | Cildip | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.960 | 18.80 |
| `cilnidipine_5_blister_002` | Cilapress | A4 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.957 | 8.10 |
| `hapacol_extra_front_01` | Hapacol Extra | A3 | `NO_MATCH` | null | `LOW_CONFIDENCE` | Y | Y | 0.993 | 7.25 |

## 5. Giới hạn thực nghiệm & Kết luận (Limitations & Verdict)

### Giới hạn thực nghiệm (Limitations)

1. **Chưa có ảnh thật trực tiếp trong pipeline runtime**: Toàn bộ quá trình kiểm thử sử dụng dữ liệu văn bản thô (rawText JSON) được trích xuất sẵn từ đợt chạy thực nghiệm pilot-002, chưa kết nối trực tiếp với luồng chụp ảnh từ camera vật lý của thiết bị di động trong phiên test này.
2. **Chưa có Real OCR Engine trên thiết bị**: Kiểm thử thực hiện decoupled trên backend matching logic, chưa tích hợp Google ML Kit Text Recognition chạy on-device realtime trên app Flutter.
3. **Môi trường Database Mock**: Đánh giá dựa trên `FakeCatalogReader` in-memory nạp dữ liệu từ seed SQL chuẩn, chưa kiểm thử độ trễ mạng thực tế qua kết nối PostgreSQL/Docker.

### Kết luận kiểm thử (Verdict)

> **VERDICT**: **PASS (mock mode) – chờ ảnh thật để chạy real mode**

Hệ thống matching backend đáp ứng các bất biến an toàn cốt lõi của PB31 và QD-39:
- Đạt **100% (23/23 mẫu) kích hoạt fallback an toàn** chuyển sang tìm kiếm thủ công khi thuốc ngoài danh mục, không bao giờ tự ý gán sai thuốc (`preselected_id = null`).
- Đạt **70.0% độ chính xác nhận diện hoạt chất** trên tập có trong Seed (Nhóm A1).
- Năng lực thuật toán chẩn đoán đạt **72.7% Top-1/Top-3** trên 14 cặp từ điển, độ trễ phản hồi tức thì trung vị **6.72 ms** (< 50 ms budget).

---

## Bước tiếp theo

- Đang chờ: Reviewer xem xét báo cáo kiểm thử `05-test-report.md`.
- Việc cần làm: Người dùng / Reviewer chạy lệnh phê duyệt trong terminal riêng:
  ```powershell
  python .agents/scripts/gate.py approve 4.17-ocr-accuracy-test test
  ```
  *(Gõ `4.17-ocr-accuracy-test` khi console yêu cầu xác nhận)*
- Cập nhật lần cuối: 2026-11-16 13:35, Antigravity
