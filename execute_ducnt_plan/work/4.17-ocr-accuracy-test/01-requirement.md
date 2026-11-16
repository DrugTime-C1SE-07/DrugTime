---
task: 4.17-ocr-accuracy-test
title: Test OCR accuracy across multiple packaging samples (PB31)
type: feature
stage: requirement
size: M
contract_change: no
affected: [backend, docs]
status: approved
approved_by: Duc1445
approved_at: 2026-11-14 10:33 +0700
content_hash: sha256:95d4f73b8f3d2a81
---

# 4.17 · Test: OCR accuracy across multiple packaging samples (PB31)

## 1. Mục tiêu

Kiểm thử và đo lường định lượng độ chính xác nhận diện & đối sánh thuốc (Top-1, Top-3 accuracy) cùng độ trễ xử lý (median, p95, average latency) trên tập **33 mẫu ảnh bao bì thuốc thực nghiệm độc lập** tại Việt Nam (sau khi tinh lọc loại bỏ 16 mẫu duplicate và bổ sung mẫu thực IMG_049 Hapacol Extra theo yêu cầu Reviewer), đối chiếu với mục tiêu kỹ thuật nội bộ do kế hoạch thực nghiệm đề xuất (Top-3 > 85% trên tập chẩn đoán 33 mẫu) và hành vi an toàn theo PB31 (trả về trạng thái `no_match` hoặc `low_confidence` với `preselected_id = null` khi thuốc ngoài danh mục để kích hoạt tìm kiếm thủ công, không tự ý chọn sẵn thuốc sai), xuất báo cáo chi tiết và cập nhật kết quả vào bộ test case tổng của dự án.

> [!NOTE]
> **Giới hạn tập dữ liệu**: Bộ 33 mẫu là tập mẫu thực nghiệm độc lập đã được tinh lọc (loại bỏ hiện tượng copy-paste trùng lặp mẫu ảnh), tuy nhiên vẫn là tập mẫu thực nghiệm nội bộ, chưa phải tập đại diện lâm sàng cho mọi điều kiện ánh sáng, góc chụp và chủng loại bao bì thực tế trên thị trường. Kết quả đo lường là benchmark thực nghiệm nội bộ trên tập mẫu này, không suy rộng thành độ chính xác sản phẩm tổng quát.

## 2. Phạm vi

### Trong phạm vi

- Thu thập và đối soát toàn bộ 33 mẫu OCR thô với bảng nhãn chuẩn (`datasets/labels.xlsx` — 33 dòng nhãn, 14 cặp tên–hàm lượng, 14 tên sản phẩm khác nhau).
- Phân biệt rõ hai tầng đánh giá:
  1. **Tầng ML Kit Raw Recognition**: Baseline nhận diện OCR text thô trên thiết bị di động, **không phải** độ chính xác matching của backend.
  2. **Tầng Backend Matching Pipeline (`normalize_ocr_text` → `lookup_ocr_candidates` → `score_ocr_matches`)**: Chạy đối sánh 33 raw text qua pipeline backend với 2 góc nhìn tách bạch và mẫu số riêng biệt:
     - **Góc nhìn 1 — Báo cáo chính thức trên Seed thực tế (`10_knowledge_base.sql`)**: 
       + Đối với **10 mẫu** có hoạt chất & hàm lượng tương ứng trong seed (nhóm A1: Atorvastatin 10mg [6 mẫu], Efferalgan 500mg [4 mẫu]), mẫu số cố định = 10, đo Top-1 và Top-3 khớp hoạt chất/hàm lượng và khớp tên thương phẩm.
       + Đối với **23 mẫu** còn lại (thuốc khác hàm lượng hoặc ngoài seed: nhóm A2 [4 mẫu], A3 [12 mẫu], A4 [7 mẫu]), mẫu số cố định = 23, kiểm tra Tỷ lệ an toàn (Safety Fallback Rate): hệ thống phải trả về trạng thái `no_match` (mở tìm kiếm thủ công với `suggested_query`) hoặc `low_confidence` với `preselected_id = null`. Tuyệt đối **không** được trả về `status = "matched"` (gán sẵn sai thuốc). Tỷ lệ an toàn **tách riêng biệt, không tính gộp** vào Top-3 Accuracy.
     - **Góc nhìn 2 — Báo cáo chẩn đoán thuật toán (Diagnostic Benchmark trên Catalog 14 cặp đầy đủ)**: Chạy trên catalog giả lập chứa đầy đủ cả 14 cặp sản phẩm/hàm lượng từ nhãn dataset với mẫu số = 33 (100% mẫu có ground truth trong từ điển). Đo lường năng lực cốt lõi của thuật toán chuẩn hóa chuỗi và fuzzy matching khi có ground-truth, đối chiếu với mục tiêu kỹ thuật nội bộ đề xuất (Top-3 > 85%). Báo cáo minh bạch đây là phép đo chẩn đoán kỹ thuật, **không** dùng làm bằng chứng DoD hay thay thế catalog thật vì đã đưa nhãn ground-truth vào danh mục.
- Đo lường phân vị độ trễ (average, median, p95 matching latency ms).
- Viết bộ test đánh giá độ chính xác và lưu báo cáo chi tiết vào `work/4.17-ocr-accuracy-test/evidence/accuracy_report.log`.
- Lập kế hoạch kỹ thuật (`03-plan.md`), báo cáo kiểm thử (`05-test-report.md`), và cập nhật test case thực nghiệm vào `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (`wf-testcase`).

### Ngoài phạm vi

- Không thay đổi thuật toán lõi hoặc UI của mobile app (`frontend/mobile` chỉ gọi `POST /catalog/medications/match`).
- Không thay đổi API contract `/catalog/medications/match`.
- Không tự ý nạp thêm các biệt dược mới vào migration hay seed chính thức `10_knowledge_base.sql` trong task này (nếu cần bổ sung catalog thật, sẽ ghi nhận vào Bug Report / Phát sinh để PO/team quản lý danh mục xem xét).

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `Product-and-Sprint-backlog-DrugTime.xlsx` (Sprint 4 Backlog) | Task 4.17 thuộc PB31: "Test: OCR accuracy across multiple packaging samples", estimate 6h, owner Duc, trạng thái hiện tại `Not started` (chờ đồng bộ backlog chính thức). PB31 chỉ yêu cầu quét bao bì trên thiết bị, khi confidence thấp hoặc không khớp thì chuyển sang manual search fallback; **không có tiêu chí phần trăm định lượng cứng** trong backlog. |
| `PLAN_TIEN_DO_DUCNT.md:193-223` | Tracker tiến độ nội bộ: đề xuất mục tiêu kỹ thuật Top-3 > 85% để đánh giá thuật toán trên tập chẩn đoán, đo latency benchmark, lưu `accuracy_report.log`, lập `05-test-report.md` và cập nhật `Test_Cases.xlsx`. |
| `api_contract/openapi.json:2160-2240` | Hợp đồng API `/catalog/medications/match` quy định 3 giá trị `status` chuẩn của `OcrMatchResult`: (1) `matched` (`preselected_id` có giá trị); (2) `low_confidence` (`preselected_id = null`, trả danh sách gợi ý + `suggested_query`); (3) `no_match` (`items` rỗng, `preselected_id = null`, app mở tìm thủ công với `suggested_query`). Khi thiếu hàm lượng nhưng catalog chỉ có 1 hàm lượng, cho phép `matched` kèm `reasons = ["strength_unverified"]`. |
| `backend/src/drugtime/modules/catalog/domain/ocr_match.py:17` & `score_ocr_matches.py:419` | `OcrMatchStatus(StrEnum)` trong domain backend định nghĩa 3 giá trị: `MATCHED`, `LOW_CONFIDENCE`, `NO_MATCH`. Logic tính điểm hỗ trợ `strength_unverified` khi tên thuốc đủ điểm tin cậy và không bị xung đột hàm lượng. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md:68` | Quyết định QD-39: Mọi kết quả OCR và nhập tay phải được người dùng kiểm tra lại tên thuốc, hàm lượng, đơn vị, liều trước khi tạo lịch. Thuốc chưa có trong danh mục → không gán thuốc gần giống để vượt chặn. |
| `datasets/labels.xlsx` & `datasets/annotations.v1.csv` | Đã tinh lọc chuẩn hóa thành 33 mẫu độc lập (sau khi loại 16 duplicate IMG_033–IMG_048 và bổ sung IMG_049 Hapacol Extra), gồm 14 cặp (tên - hàm lượng); có **13 mẫu** mang giá trị `strength = None`. |
| `datasets/manifest.v1.json` | Quản lý 33 ảnh mẫu vật lý (kèm `hapacol_extra_front_01.jpg`), 100% hash SHA256 đã khớp với file vật lý trên đĩa. |
| `backend/supabase/seeds/10_knowledge_base.sql` | Danh mục thuốc seed hiện tại gồm 59 thuốc mẫu (tên thương phẩm kèm hàm lượng như `Lipitor 10 mg`, `Glucophage 500 mg`, `Agi-Tyfedol 500`, `Concor 5 mg`, `Clarityne 10 mg`...). |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `backend` | Có | Chạy đánh giá và bộ test matching pipeline trên 33 mẫu raw OCR; lưu evidence log. |
| `docs` | Có | Cập nhật sheet test case và kết quả kiểm thử accuracy PB31 vào `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`. |
| `frontend` | Không | Mobile (`ocr_api_repository.dart`) chỉ gọi API matching, không chứa logic ranking Top-1/Top-3. |
| `api_contract` | Không | Giữ nguyên contract `/catalog/medications/match`. |
| `tests` | Không | Không sửa E2E suite ở repo `tests`. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: Chỉ sử dụng và kiểm thử độ chính xác của endpoint/pipeline `/catalog/medications/match` hiện có; không thay đổi request/response hay status code.
- Endpoint liên quan (chỉ dùng): `POST /catalog/medications/match`.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm dữ liệu sức khỏe bệnh nhân, phân quyền người thân, `access_logs`, schema migration hay secret.
- Bất biến liên quan PB31 (R-01) & QD-39: Khi độ tin cậy thấp hoặc thuốc không có trong danh mục, pipeline **phải** trả về `status = "no_match"` hoặc `status = "low_confidence"` với `preselected_id = null`, tuyệt đối không tự ý chọn sẵn một thuốc sai (`preselected_id` khác null).

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | **Given** 33 mẫu raw OCR đối chiếu với `datasets/labels.xlsx`, **When** chạy pipeline matching OCR của backend, **Then** xuất được bảng tổng hợp kết quả từng mẫu gồm Image ID, Loại bao bì (hộp/vỉ), Expected Drug, Top-1 match, Top-3 matches, `status` (`matched` / `low_confidence` / `no_match`), `preselected_id`, `top_score` và thời gian xử lý (`elapsed_ms`). | integration |
| AC2 | **Given** 10 mẫu bao bì thuộc nhóm A1 (có hoạt chất & hàm lượng tương ứng trong seed `10_knowledge_base.sql`), **When** chạy matching pipeline trên seed thật, **Then** đo lường Top-1 và Top-3 với mẫu số = 10 theo cả hai tiêu chí: (1) Khớp hoạt chất & hàm lượng và (2) Khớp chính xác tên sản phẩm/thương phẩm. | integration |
| AC3 | **Given** 23 mẫu bao bì thuộc nhóm A2, A3, A4 (thuốc khác hàm lượng hoặc ngoài danh mục seed), **When** chạy matching pipeline trên seed thật, **Then** kiểm tra mục tiêu an toàn kỹ thuật do task đề xuất (Safety Fallback Target): đo lường tỷ lệ các mẫu trả về `status = "no_match"` hoặc `status = "low_confidence"` với `preselected_id = null` (không tự ý chọn sẵn thuốc sai), hướng tới đạt 100% (23/23 mẫu) trên tập kiểm thử này. Ghi nhận rõ đây là chỉ tiêu kiểm thử kỹ thuật nội bộ của task, không phải ngưỡng tỷ lệ % quy định trong backlog PB31. Chỉ số này tách biệt, không tính gộp vào Top-3 accuracy. | integration |
| AC4 | **Given** toàn bộ 33 mẫu bao bì chạy trên Catalog Chẩn đoán 14 cặp nhãn đầy đủ, **When** đo lường độ chính xác thuật toán với mẫu số = 33, **Then** xuất kết quả Top-1 và Top-3 Strict Product Accuracy và Active Ingredient Accuracy; so sánh với mục tiêu kỹ thuật nội bộ đề xuất **Top-3 > 85%** mà không suy diễn thành DoD chính thức khi chưa có phê duyệt của PO. | integration |
| AC5 | **Given** toàn bộ output đo lường và bảng phân tích lỗi chi tiết từng mẫu, **When** hoàn tất kiểm thử, **Then** lưu log gốc tại `work/4.17-ocr-accuracy-test/evidence/accuracy_report.log` và lập báo cáo chi tiết `work/4.17-ocr-accuracy-test/05-test-report.md`. | integration |
| AC6 | **Given** kết quả kiểm thử trong phiên làm việc, **When** chạy `wf-testcase`, **Then** cập nhật `work/4.17-ocr-accuracy-test/testcases.json`, `testcases.xlsx` và gộp vào `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (`validate/build/merge` exit 0). | manual / integration |

## 8. Bảng Crosswalk Nhãn – Seed và Quy tắc Định nghĩa "Match đúng"

### 8.1. Bảng Crosswalk chi tiết 14 cặp (Nhãn bao bì – Hoạt chất – Seed)

> [!NOTE]
> **Nguồn gốc Ground Truth Dược lý học**:
> Bảng `datasets/labels.xlsx` và `annotations.v1.csv` lưu trữ các trường `drug_name`, `strength`, và `active_ingredient`. Các hoạt chất chính trong cột *Hoạt chất chính (Medical Ground Truth)* dưới đây được tra cứu và xác thực độc lập từ **Dược thư Quốc gia Việt Nam (Bộ Y tế) và Tờ Hướng dẫn Sử dụng (SmPC) chính thức của các biệt dược lưu hành tại Việt Nam** (đã được ghi nhận chi tiết nguồn tham chiếu trong script `verify_crosswalk.py`).

| STT | Tên trên nhãn (`drug_name`) | Hàm lượng (`strength`) | Số mẫu | Hoạt chất chính (Medical Ground Truth) | Thuốc tương ứng trong seed `10_knowledge_base.sql` | Phân loại ánh xạ (Nhóm đánh giá) |
|:---:|---|---|:---:|---|---|---|
| 1 | `Atorvastatin` | `10mg` | 5 | Atorvastatin | `Lipitor 10 mg` (Atorvastatin 10 mg) | **A1**: Trùng hoạt chất & hàm lượng |
| 2 | `A.TATORVASTATIN` | `10mg` | 1 | Atorvastatin | `Lipitor 10 mg` (Atorvastatin 10 mg) | **A1**: Trùng hoạt chất & hàm lượng |
| 3 | `Efferalgan` | `500mg` | 4 | Paracetamol | `Agi-Tyfedol 500` (Paracetamol 500 mg) | **A1**: Trùng hoạt chất & hàm lượng |
| 4 | `A.TBisoprolol` | `2.5mg` | 3 | Bisoprolol fumarat | `Concor 5 mg` (Bisoprolol fumarat 5 mg) | **A2**: Trùng hoạt chất, khác hàm lượng |
| 5 | `Bisoheart` | `2.5mg` | 1 | Bisoprolol fumarat | `Concor 5 mg` (Bisoprolol fumarat 5 mg) | **A2**: Trùng hoạt chất, khác hàm lượng |
| 6 | `A.TCANDESARTAN HTZ` | `32mg + 25mg` | 1 | Candesartan cilexetil + Hydrochlorothiazide | Không có (chỉ có đơn chất HCTZ: `Thiazifar 25 mg`) | **A3**: Thuốc phối hợp chưa có trong seed |
| 7 | `ACANTANHTZ` | `8mg + 12.5mg` | 1 | Candesartan cilexetil + Hydrochlorothiazide | Không có (chỉ có ARB+HCTZ khác: `Losartan/HCTZ`) | **A3**: Thuốc phối hợp chưa có trong seed |
| 8 | `Decolgen Forte` | `None` | 5 | Paracetamol + Phenylephrin + Clorpheniramin | Không có (chỉ có đơn chất `Agi-Tyfedol 500`, `Phenylephrin 10 mg`) | **A3**: Thuốc phối hợp chưa có trong seed |
| 9 | `Tiffy Dey` | `None` | 4 | Paracetamol + Phenylephrin + Clorpheniramin | Không có (chỉ có đơn chất `Agi-Tyfedol 500`, `Phenylephrin 10 mg`) | **A3**: Thuốc phối hợp chưa có trong seed |
| 10 | `Hapacol Extra` | `500mg + 65mg` | 1 | Paracetamol + Cafein | Không có (chỉ có đơn chất `Agi-Tyfedol 500`) | **A3**: Thuốc phối hợp chưa có trong seed |
| 11 | `Candesartan Krka` | `16mg` | 1 | Candesartan cilexetil | Không có (seed chỉ có ARB khác: Losartan, Valsartan) | **A4**: Hoạt chất ngoài danh mục seed |
| 12 | `Cilapress` | `5mg` | 1 | Cilnidipine | Không có (seed chỉ có chẹn canxi khác: Amlodipin, Felodipin) | **A4**: Hoạt chất ngoài danh mục seed |
| 13 | `Cildip` | `5mg` | 1 | Cilnidipine | Không có (seed chỉ có chẹn canxi khác: Amlodipin, Felodipin) | **A4**: Hoạt chất ngoài danh mục seed |
| 14 | `Strepsils Original` | `None` | 4 | 2,4-Dichlorobenzyl alcohol + Amylmetacresol | Không có (viên ngậm sát trùng họng ngoài danh mục) | **A4**: Hoạt chất ngoài danh mục seed |

*Tổng cộng*: 14 cặp tên–hàm lượng = **33 mẫu** (A1: 10 mẫu, A2: 4 mẫu, A3: 12 mẫu, A4: 7 mẫu).

---

### 8.2. Định nghĩa Mẫu số và Công thức Tính Accuracy

Để đảm bảo tính khoa học và minh bạch, các chỉ số được định nghĩa với mẫu số và tập dữ liệu hoàn toàn tách bạch:

1. **Bộ chỉ số 1 — Đánh giá Matching trên Seed thực tế (`10_knowledge_base.sql`)**:
   - **Tập đánh giá In-Seed Matching ($S_{seed\_match}$ = Nhóm A1)**: Mẫu số cố định là **10 mẫu**.
     - $\text{Top-1 Active Ingredient Accuracy} = \frac{\text{Số mẫu nhóm A1 có ứng viên Top 1 khớp đúng hoạt chất \& hàm lượng}}{10}$
     - $\text{Top-3 Active Ingredient Accuracy} = \frac{\text{Số mẫu nhóm A1 có ít nhất một ứng viên trong Top 3 khớp đúng hoạt chất \& hàm lượng}}{10}$
     - $\text{Top-1 / Top-3 Strict Brand Accuracy} = \frac{\text{Số mẫu nhóm A1 khớp chính xác tên thương phẩm (medication.name)}}{10}$
   - **Tập đánh giá An toàn Out-of-Seed / Different Strength ($S_{seed\_safe}$ = Nhóm A2 + A3 + A4)**: Mẫu số cố định là **23 mẫu** ($4 + 12 + 7$).
     - $\text{Safety Fallback Rate} = \frac{\text{Số mẫu có } status \in \{\text{"no\_match"}, \text{"low\_confidence"}\} \text{ VÀ } preselected\_id \text{ là None}}{23}$
     - **Chỉ tiêu kiểm thử an toàn đề xuất**: Đo lường khả năng fallback an toàn trên 23 mẫu ngoài seed / khác hàm lượng, với mục tiêu không tự ý gán `status = "matched"` với một `preselected_id` sai. Ghi chú rõ: Đây là tiêu chuẩn kiểm thử kỹ thuật nội bộ do task đề ra trên tập dữ liệu này nhằm kiểm chứng yêu cầu PB31 (chuyển fallback tìm thủ công), **không phải là chỉ số phần trăm định lượng quy định trong Product Backlog PB31**. Tỷ lệ an toàn này **tuyệt đối không được tính gộp** vào tỷ lệ Top-3 accuracy.

2. **Bộ chỉ số 2 — Đánh giá Chẩn đoán Thuật toán (Diagnostic Benchmark trên 14 cặp Catalog đầy đủ)**:
   - **Tập đánh giá Chẩn đoán ($S_{diagnostic}$)**: Mẫu số cố định là **33 mẫu** (toàn bộ 33 ảnh đều có ground truth tương ứng trong danh mục chẩn đoán).
     - $\text{Top-1 Diagnostic Accuracy} = \frac{\text{Số mẫu gợi ý đúng sản phẩm ground truth ở vị trí Top 1}}{33}$
     - $\text{Top-3 Diagnostic Accuracy} = \frac{\text{Số mẫu có sản phẩm ground truth nằm trong Top 3 ứng viên}}{33}$
     - $\text{MRR (Mean Reciprocal Rank)} = \frac{1}{33} \sum_{i=1}^{33} \frac{1}{\text{rank}_i}$ (với $\text{rank}_i$ là thứ hạng của ground truth, nếu không nằm trong kết quả thì $\frac{1}{\text{rank}_i} = 0$).
   - **Phạm vi của mục tiêu nội bộ Top-3 > 85%**: Ngưỡng này **chỉ áp dụng duy nhất** cho chỉ số $\text{Top-3 Diagnostic Accuracy}$ trên tập 33 mẫu chẩn đoán, nhằm đánh giá năng lực của normalizer + fuzzy matcher khi dữ liệu đầu vào có đầy đủ trong catalog.

---

### 8.3. Quy tắc xử lý dạng bào chế, thuốc phối hợp và mẫu thiếu hàm lượng

1. **Dạng bào chế (Dosage Form)**:
   - Không coi là lỗi matching nếu OCR chỉ đọc được tên và hàm lượng mà không đọc được dạng bào chế (ví dụ: viên sủi Efferalgan 500mg đối chiếu với viên nén Agi-Tyfedol 500mg), miễn là hoạt chất và hàm lượng khớp đúng.
2. **Thuốc phối hợp đa thành phần (Combination Drugs)**:
   - Với các thuốc phối hợp như `Decolgen Forte`, `Tiffy Dey`, `A.TCANDESARTAN HTZ`, `Hapacol Extra`, thuật toán phải nhận diện đúng tên biệt dược phối hợp hoặc nhận diện đúng cặp hoạt chất chính. Việc chỉ nhận diện được 1 thành phần đơn lẻ mà bỏ sót dạng phối hợp sẽ được ghi nhận và phân tích trong báo cáo lỗi.
3. **Mẫu thiếu hàm lượng trên bao bì (`strength = None`)**:
   - Có chính xác **13 mẫu** mang giá trị `strength = None` trong nhãn (gồm: 5 mẫu `Decolgen Forte`, 4 mẫu `Strepsils Original`, 4 mẫu `Tiffy Dey`).
   - *Hành vi API và Hợp đồng*:
     - Nếu văn bản OCR không bóc tách được hàm lượng:
       + Trường hợp tên thuốc chỉ có duy nhất 1 hàm lượng trong catalog: Contract và mã nguồn cho phép trả về `status = "matched"` kèm `reasons = ["strength_unverified"]` và `preselected_id` được gán sẵn.
       + Trường hợp tên thuốc có nhiều hàm lượng trong catalog: Hệ thống trả về `status = "low_confidence"` kèm `reasons = ["multiple_strengths"]` và `preselected_id = null`.
   - *Nguyên tắc QD-39*: Bất kể API trả về `matched` hay `low_confidence`, người dùng **luôn phải kiểm tra và xác nhận thủ công** trước khi tạo lịch (QD-39). Khi có cờ `strength_unverified`, client phải hiển thị cảnh báo nhắc người dùng đối chiếu lại hàm lượng in trên bao bì.

---

### 8.4. Xử lý Lỗi Dữ liệu Reviewer Phát hiện (Lỗi A & Lỗi B)

Nhằm đảm bảo tính trung thực học thuật (AGENTS.md §5) và độ chính xác của tập dữ liệu thực nghiệm theo yêu cầu của Reviewer:

1. **Xử lý Lỗi A — Loại bỏ 16 mẫu duplicate (Chọn Phương án a)**:
   - Qua rà soát chi tiết, 16 mẫu (tương ứng IMG_033 đến IMG_048) là các bản ghi copy-paste trùng lặp điều kiện chụp và file ảnh với các mẫu ban đầu. Việc giữ lại các mẫu này làm sai lệch thống kê (thổi phồng mẫu).
   - Quyết định lựa chọn **Phương án (a)**: Xóa toàn bộ 16 mẫu trùng lặp khỏi `annotations.v1.csv` và `labels.xlsx`. Giữ lại 32 mẫu độc lập ban đầu và bổ sung mẫu mới thật sự IMG_049 (`hapacol_extra_front_01.jpg`), chốt tập dữ liệu benchmark chính thức gồm **33 mẫu độc lập**.
   - *Lý do chọn (a) thay vì (b)*: Phương án (b) yêu cầu chụp 16 ảnh mới trong điều kiện khác nhau là bất khả thi trong phiên làm việc hiện tại, và việc tự ý tạo ảnh giả sẽ vi phạm nghiêm trọng tính trung thực của bằng chứng.
2. **Xử lý Lỗi B — Chuẩn hóa IMG_049 vào `manifest.v1.json`**:
   - Mẫu IMG_049 (`hapacol_extra_front_01.jpg`, Hapacol Extra: Paracetamol 500mg + Cafein 65mg) đã được bổ sung đầy đủ vào `datasets/manifest.v1.json` với trường `sample_id = "IMG_049"`, cập nhật `total_images = 33` và kiểm chứng mã băm SHA256 tương ứng.
   - Thư mục vật lý `datasets/images/hapacol_extra/box/` đã được thiết lập và file raw OCR tương ứng đã được tích hợp vào `datasets/results/pilot-002/raw/`.

## 9. Câu hỏi mở

Q1 [đã giải quyết]: Cách tiếp cận đo lường giữa catalog seed thật (`10_knowledge_base.sql`) và danh mục chẩn đoán:
- **Kết luận**: Đã phân định rõ ràng mục đích, phạm vi và công thức tính toán:
  1. *Báo cáo chính thức trên Seed*: Đánh giá matching trên 10 mẫu có cùng hoạt chất/hàm lượng (nhóm A1); đánh giá Tỷ lệ an toàn (Safety Fallback Rate) trên 23 mẫu ngoài seed (nhóm A2, A3, A4) với yêu cầu kiểm tra `preselected_id = null`.
  2. *Báo cáo chẩn đoán*: Đánh giá năng lực thuật toán matching trên toàn bộ 33 mẫu với danh mục 14 ground-truth đầy đủ. Ngưỡng kỹ thuật nội bộ Top-3 > 85% chỉ áp dụng cho tập này.

## 10. Giả định

- Task 4.14 đã hoàn tất bộ unit test chuẩn hóa OCR (`test_ocr_real_output.py`), Task 4.17 kế thừa tập dữ liệu 33 ảnh & raw JSON đã tinh lọc.
- Nếu môi trường hiện tại chưa khởi động Postgres local (`supabase start`), có thể đo bằng matching pipeline kết hợp in-memory repository nạp đúng schema & dữ liệu từ `10_knowledge_base.sql` hoặc kiểm tra kết nối Postgres local ở giai đoạn `plan`; ghi nhận rõ môi trường thực thi trong `05-test-report.md`.
- Cả hai mốc chỉ tiêu định lượng (mục tiêu Top-3 > 85% trên 33 mẫu chẩn đoán, và mục tiêu an toàn 23/23 trên tập ngoài seed) đều là các **chỉ tiêu kỹ thuật tham chiếu nội bộ do task đề xuất**, không phải là các ngưỡng phần trăm cứng trong Backlog PB31 chính thức.
- Bảng tiến độ trong `PLAN_TIEN_DO_DUCNT.md` là tracker nội bộ theo dõi tiến độ kỹ thuật của nhánh; file workbook backlog chính thức `Product-and-Sprint-backlog-DrugTime.xlsx` sẽ được đồng bộ theo quy trình chung của team.

## 11. Phát sinh

- Đã phát hiện và xử lý dứt điểm 2 lỗi dữ liệu do Reviewer chỉ ra (Lỗi A: 16 mẫu duplicate; Lỗi B: thiếu IMG_049 Hapacol Extra trong manifest). Tập dữ liệu được tinh lọc chuẩn hóa về đúng 33 mẫu độc lập thực tế.

## 12. Size

- `size`: M
- Lý do: Liên quan 2 submodule (`backend`, `docs`), cần chạy benchmark matching pipeline trên toàn bộ 33 mẫu raw OCR, sinh báo cáo `03-plan.md`, `05-test-report.md`, `accuracy_report.log` và cập nhật workbook `Test_Cases.xlsx`.

## Bước tiếp theo

- Đang chờ: Reviewer xem xét bản phân tích yêu cầu đã cập nhật số liệu 33 mẫu thực nghiệm độc lập và giải pháp cho Lỗi A/B.
- Việc cần làm: Người dùng chạy `python .agents/scripts/gate.py approve 4.17-ocr-accuracy-test requirement` để phê duyệt lại requirement.
- Cập nhật lần cuối: 2026-11-14 09:40, Antigravity
