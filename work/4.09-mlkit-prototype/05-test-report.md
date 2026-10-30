---
task: 4.09-mlkit-prototype
stage: test
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 17:14 +0700
content_hash: sha256:635dcc9b4799485a
inputs:
  01-requirement.md: sha256:8a9ccb35212f46c2
  03-plan.md: sha256:6beeb0f93423efc9
  04-impl-notes.md: sha256:f9db3c1a907e8565
---

# 4.09 · Kiểm công cụ chấm và quyết định ML Kit từ pilot v1

Ngày lập kiểm chứng: 2026-10-29. Hồ sơ prototype, số liệu và **GO tiếp tục ML Kit từ pilot** đã sẵn sàng để người duyệt xem xét và chuyển review. Các kiểm thủ công chưa làm được ghi là giới hạn prototype. Không bắt buộc làm thêm benchmark có ngưỡng hoặc Tesseract theo scope mới.

## Điều chỉnh cách chốt task theo chỉ dẫn mới

- Người dùng phản hồi “task này đâu có cần test đâu ta”, rồi yêu cầu “tiếp tục làm cho tôi” sau khi thống nhất chốt 4.09 ở prototype Android, raw OCR, đo kết quả và quyết định hướng.
- Bằng chứng native pilot và 49 JSON đã có phục vụ kết luận prototype. Không yêu cầu quét lại toàn bộ ảnh, kiểm điện thoại thật hoặc chạy thêm bộ manual như một tính năng hoàn chỉnh để chốt pilot này.
- TC-OCRP-01..08 và TC-OCRD-47 giữ Pending vì chưa thực hiện đầy đủ theo các steps đó. Đây là thông tin giới hạn, không là việc mới giao người dùng hoặc điều kiện bổ sung chặn chốt hồ sơ pilot. Không đổi Pending thành Pass và không tuyên bố những hành vi này đã đạt.
- Những nội dung manual trong 01/03 đã approved được lưu nguyên như kế hoạch kiểm trước chỉ dẫn mới. Báo cáo draft này ghi rõ việc thu hẹp mức kiểm chứng được người dùng yêu cầu; không sửa lén artifact approved hoặc nới phép chấm exact.
- GO là quyết định kỹ thuật từ pilot, không phải bảo đảm matching đúng, chuẩn chất lượng production hay tự hoàn thành Definition of Done về PR/reviewer.

Báo cáo trước đồng bộ v1: `evidence/test-report-before-v1.md`. Các số 17 ảnh/15 chưa chạy/23 exact trong bản cũ không còn hiện hành.

## 1. Môi trường

- Gate test OK với 01/03/04 approved: `evidence/test-v1-gate.log`. Không sửa approved artifact/code sản phẩm.
- Windows, Python 3.13 chạy unit/CLI; bundled Python có openpyxl kiểm workbook và dựng testcase bằng script chính thức.
- Superproject `feat/datasets-ocr`; frontend `feat/mlkit-prototype-measurement` sạch; docs `codex/4.09-ocr-testcases` chỉ thay workbook tổng.
- Dùng 49 JSON native pilot-002 đã có, không chạy OCR mới/cài/xóa app/thao tác máy ảo. Pipeline ghi bản sao trong `scratch/test-v1-pipeline/`.
- Không API/backend/DB sức khỏe, không reset DB. iOS, camera 4.10, normalization/matching 4.12/4.13 ngoài scope.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test/bằng chứng | Kết quả |
|---|---|---|
| AC1 | 49 raw native lịch sử; TC-OCRP-01 | Có pilot Android emulator; testcase native chưa chạy mới, Pending |
| AC2 | Unit/hash/idempotence, HOST1, verify_v1 | Pass bảo toàn raw/metadata; share qua UI Pending TC-OCRP-02 |
| AC3 | Unit/fake lịch sử, unit no_text; TC-OCRP-03..05 | Có kiểm logic; native ảnh trắng/hỏng/hủy Pending |
| AC4 | Unit lifecycle lịch sử; TC-OCRP-06 | Native double tap/back/background/process death Pending |
| AC5 | 41 unit + HOST2 chấm49/49 | Pass công cụ; kiểm nhãn độc lập Pending TC-OCRD-47 |
| AC6 | HOST5/verify_v1 nguồn nguyên vẹn, prototype lịch sử | Không dùng nhãn sửa raw; offline/native không mutation thuốc Pending TC-OCRP-07 |
| AC7 | verify_v1 T8, TC-OCRD-49, HOST3 | Pass: engineering GO riêng; automatic not_decided; thiếu protocol không benchmark go |
| AC8 | Báo cáo/README/decision ghi đủ giới hạn/Pending | Pass minh bạch; GO không tự đủ Definition of Done |
| AC9 | Unit XLSX B2/shared-inline/ID trùng/formula/nhãn thiếu/path/JSON lỗi | Pass |
| AC10 | Unit strength/boundary/blank/multi-component, annotations | Pass phép chấm; xác minh bao bì độc lập Pending |
| AC11 | HOST1 + hash import-index + unit conflict/legacy/unmapped | Pass bảo toàn payload; không dựng JSON từ screenshot |
| AC12 | Unit earliest/timestamp/tie/deviceKind/OS, HOST2 | Pass chọn tất định, không chọn run đẹp/gộp emulator với điện thoại |
| AC13 | HOST2 CSV/JSON/Markdown, HOST4 no-data N/A, HOST5 | Pass tái hiện cục bộ; clone/publish 4.08 Pending |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Nhập lại không ghi đè payload | Unit + HOST1 | Pass |
| No-text/lỗi/missing hiện rõ | Unit + HOST2/HOST4 | Pass |
| Thiếu protocol không tự benchmark go | Unit + HOST3 | Pass |
| Quyết định người phụ trách tách automatic pilot | verify_v1 T8 | Pass |
| Không đổi nguồn trong phép đo | HOST5 + verify_v1 | Pass |
| Share/picker/offline/lifecycle/vỉ nghiêng native | TC-OCRP-01..08 | Pending |
| Patient/consent/dose/RLS | Không service/schema sức khỏe thay đổi | Không áp dụng |

## 4. Bộ kiểm tra và dữ liệu thật

Các kết quả dưới đây là bằng chứng của lượt kiểm trước ngày 2026-10-29; lượt chỉnh hồ sơ này không chạy lại unit/Flutter/OCR và không nhận là kết quả chạy mới.

- `python -m unittest discover -s datasets/scripts -p "test_*.py" -v`: **41 pass, 0 fail, 1.113s**; `evidence/test-v1-unit.log`.
- `python work/4.09-mlkit-prototype/scratch/test_v1_pipeline.py`: **5 host integration checks pass**; `evidence/test-v1-integration.log`. Import/re-import49 raw từ filesystem, chấm bản sao, missing-protocol pending, empty-raw49 not_run, hash nguồn không đổi. Không có ADB mới trong lượt này.
- Bundled Python `work/4.08-ocr-capture-evaluation/scratch/verify_v1.py`: kiểm snapshot/labels/ảnh/annotations/GO/report/raw hash đạt; `../4.08-ocr-capture-evaluation/evidence/test-v1-integrity.log`.
- Không chạy lại Flutter vì latest implement chỉ dữ liệu/quyết định, frontend không sửa. 13 Flutter unit/widget/native smoke ở evidence cũ không được tính là vừa chạy; unit/fake không thay kiểm native.
- Scope test exit1: “CHẶN: 230 file ngoài phạm vi”; `evidence/test-v1-scope.log`, phân loại mục7.

### Pilot-002 v1 hiện hành

- 49 ảnh/49 nhãn, 28 hộp/21 vỉ, 23 tên sản phẩm; **coverage49/49**, 0 lỗi dữ liệu. Bộ nhỏ/nguồn chưa rõ không đại diện mọi điều kiện.
- Sau rà nhãn theo ảnh: exact_name **27**, partial_name **5**, tokens_present_noncontiguous **2**, name_not_found **14**, no_text **1**; exact **27/49 = 55.1%**. Không cộng partial/prefix/token rời thành tên đúng hoặc matching đúng.
- Median **2615ms**, p95 **5267ms**, n=49 từ run emulator đã có; không suy tốc độ điện thoại thật.
- 49 JSON khớp import-index; dataset hash `588a56f54a5155250ce6c5fc633b60d05351f20561d46ba49ed482eab1b77e7f`.
- `datasets/results/pilot-002/decision.json`/`decision.md`: engineering_pilot GO theo xác nhận người dùng ngày2026-10-29, có lý do/giới hạn/hash truy vết. summary tự động vẫn not_decided. Nếu làm benchmark có ngưỡng sau này, phải chốt protocol trước đo; không áp ngưỡng sau khi xem điểm.

## 5. Bộ test case Excel

- Spec `testcases.json`; file task `testcases.xlsx`; file tổng theo người dùng `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Script chính thức validate/build/merge thành công, không cảnh báo đổi Pass/Fail cũ; `evidence/testcase-v1-xlsx.log`.
- Read-only sheet/ID/status khớp spec: `evidence/testcase-v1-verification.log`. Không render/recalculate bằng Excel native.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Prototype ML Kit Android (OCRP) | 8 | 0 | 0 | 8 |
| Nhập/đánh giá OCR dataset (OCRD) | 48 | 47 | 0 | 1 |
| Task4.09 | 56 | 47 | 0 | 9 |
| File tổng gồm4.08 | 64 | 53 | 0 | 11 |

47 Pass gồm41 unit Python,5 host checks,1 kiểm artifact quyết định. Không đồng nhất với số test Flutter. TC-OCRD-48 của benchmark bắt buộc cũ được bỏ theo scope approved mới, không dùng lại ID; TC-OCRD-49 mới kiểm engineering GO. Không bỏ testcase lỗi để làm xanh.

Các tình huống chưa kiểm đầy đủ, ghi nhận giới hạn prototype:

- TC-OCRP-01: OCR native trên Android đã chọn, ghi model/OS/metadata thực.
- TC-OCRP-02: share JSON bằng UI, đọc file ngoài app.
- TC-OCRP-03..05: ảnh trắng, file lỗi/quyền đọc, hủy picker rồi thử lại.
- TC-OCRP-06: double tap/back/background/process death/retry.
- TC-OCRP-07: offline, không gửi ảnh backend/cloud hoặc mutation thuốc.
- TC-OCRP-08: cùng vỉ thẳng và nghiêng hướng 1 giờ/7 giờ; ghi thực tế, không suy nguyên nhân/góc số.
- TC-OCRD-47: người khác kiểm 49 nhãn/strength từ ảnh, ghi người/ngày; cùng việc TC-PKGDATA-02.

Bug Report mới: 0Fail. Không đổi Pending thành Pass từ unit test.

## 5b. Lỗi sản phẩm tìm thấy

Không có lỗi chương trình mới trong41 unit/5 host đã chạy. Hạn chế OCR ảnh vỉ nghiêng người dùng báo vẫn giữ; chưa có đối chứng mới để kết luận nguyên nhân. OCR miss là kết quả đo, không tự coi là lỗi matching chưa xây.

## 6. Test không ổn định hoặc bị skip

Không che failure bằng retry/timeout/skip. Nhánh symlink trong unit path escape phụ thuộc quyềnOS; không khẳng định đã chạy nếuOS từ chối. Manual native/independent review để Pending; không nới exact để tăng tỷ lệ.

## 7. Phát sinh

- Lượt chỉnh hồ sơ theo chỉ dẫn mới: gate test OK (`evidence/test-scope-clarification-gate.log`); scope vẫn exit 1 với 230 file đã có (`evidence/test-scope-clarification.log`). Chỉ sửa báo cáo draft/handoff/evidence trong work; không sửa workbook tổng, dataset, code hoặc artifact approved. Không chạy lại test/OCR; số Pass/Pending giữ nguyên từ bằng chứng trước.
- Scope thấy226 file datasets,2 api_contract,1 .gitignore,1 workbook tổng docs. Datasets là baseline/implement hai task đã duyệt; .gitignore/api_contract là thay đổi riêng đã được cho giữ. Test stage chỉ ghi work và workbook docs theo wf-testcase.
- Thiếu testcase-book; dùng --into theo đường dẫn đã được người dùng xác nhận. Không sửa AGENTS/scope để báo sạch.
- Merge4.08 ban đầu tạo nhầm file tại04_Quality_And_Testing. Đã xác minh đó chỉ là file vừa tạo, xóa đúng file đó, merge vào file đúng; kiểm cuối đủ3 chức năng/64ID, không còn file nhầm.
- Frontend sạch; docs chỉ đổi workbook tổng. Không commit/push/stage/bump con trỏ hoặc sửa approved01/03/04.

## Bước tiếp theo

- Chờ người duyệt xem báo cáo và giới hạn, dùng `python .agents/scripts/gate.py approve 4.09-mlkit-prototype test`.
- Sau duyệt, lượt tiếp theo review prototype, raw, phép chấm, số liệu và quyết định GO; không yêu cầu người dùng chạy lại ảnh hoặc bộ manual mở rộng để bắt đầu review.
- Nếu review phát hiện nhãn hoặc công cụ sai, ghi bằng chứng và sửa theo quy trình tương ứng; không tự sửa labels/raw để tăng điểm.
- Chỉ commit/push khi người dùng yêu cầu; không commit scratch. Publish/PR/reviewer chưa thực hiện, không tự tuyên bố Definition of Done.
- Cập nhật:2026-10-29, Codex.
