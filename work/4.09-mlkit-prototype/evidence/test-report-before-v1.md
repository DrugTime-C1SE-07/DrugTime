---
task: 4.09-mlkit-prototype
stage: test
status: draft
---

# 4.09 · Test công cụ dataset và hồi quy prototype Android

## Cập nhật hiện hành · 2026-10-29

- Người dùng yêu cầu hoàn tất 4.08/4.09 theo bảng Sprint mới và bỏ nghiên cứu Tesseract khỏi phạm vi; không yêu cầu làm thêm engine đó. Nội dung thay thế ở ../4.08-ocr-capture-evaluation/scope-correction.md; requirement/plan approved cần reopen trước khi sửa.
- **Pilot-002 đã có đủ 49/49 ảnh**. Lượt này chạy lại chấm vào scratch/pilot-002-current, không sửa raw/ảnh/nhãn: 0 data error, exact=23, partial=10, token rời=4, name_not_found=11, no_text=1; median=2615 ms, p95=5267 ms trên emulator. Log evidence/test-pilot002-current.log. Hợp lệ về cấu trúc không đồng nghĩa nhãn đã được xác minh độc lập.
- Người dùng đã quyết định **GO tiếp tục ML Kit** trong chat ngày 2026-10-29. Lý do người dùng: có trường hợp sai nhãn hoặc raw đọc được phần tên có thể hữu ích cho bước sau. Đây là quyết định hướng kỹ thuật từ pilot; chưa chứng minh partial matching đúng, chưa đạt ngưỡng đặt trước, không sửa decision=not_decided do evaluator sinh.
- Cần đồng bộ AC7 và phạm vi 4.08 qua reopen; rà nhãn, lưu phiên bản/số liệu/quyết định của người phụ trách, hoàn tất native manual/review. Không tự đánh dấu task complete hoặc sửa artifact approved.
- Các mục dưới đây là snapshot ngày 2026-10-28: số “15 ảnh chưa chạy” tại thời điểm đó không còn là trạng thái hiện hành. 41 Python/13 Flutter/5 host là evidence lần trước, không báo là vừa chạy lại lượt này.

Ngày kiểm: 2026-10-28. Công cụ dataset đã kiểm đạt trong phạm vi đã chạy. **Task và test stage chưa hoàn tất**: 15/17 ảnh chưa có run, các thao tác native chưa kiểm mới, chưa xác minh độc lập toàn bộ nhãn hoặc frozen benchmark/go-no-go. Không đề nghị duyệt test lúc này. Báo cáo trước vòng dataset lưu tại evidence/test-report-before-dataset.md.

## 1. Môi trường

- Gate test OK, requirement/plan/implement approved; không sửa 01/03/04 hoặc code sản phẩm. Log evidence/test-dataset-gate.log.
- Superproject feat/datasets-ocr, frontend feat/mlkit-prototype-measurement. Docs ban đầu main sạch, tạo nhánh codex/4.09-ocr-testcases trước khi gộp file tổng. Không commit/push hoặc stage/bump con trỏ.
- Python 3.13 tại máy người dùng chạy 41 test và CLI; bundled Python có openpyxl chạy script testcase_xlsx.py chính thức. Không cài thêm package.
- Android emulator-5554 online, sdk_gphone16k_x86_64, Android 17. Chỉ đọc JSON/hash qua ADB; không khởi động/dừng máy ảo, gỡ/cài app hoặc chạy OCR lại trên thiết bị người dùng.
- Các lệnh pipeline ghi vào work/4.09-mlkit-prototype/scratch/dataset-test-20261028, không ghi dữ liệu sản phẩm trong datasets. Test fixture Python dùng TEMP, Flutter dùng fake/filesystem/widget.
- Không API/DB/backend hoặc endpoint sức khỏe trong task; không reset DB, không áp dụng các kịch bản patient/consent/dose/RLS. Không kiểm iOS/camera UI của 4.10.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test/bằng chứng phiên này | Kết quả |
|---|---|---|
| AC1 | Đọc JSON native có sẵn từ Android; Flutter fake/widget 13 pass | Một phần: có raw native lịch sử, chưa chạy OCR mới/điện thoại bắt buộc; TC-OCRP-01 Pending |
| AC2 | 13 test prototype, Python import/hash/idempotence và pipeline ADB→raw bản sao | Pass tự động cho byte/raw/metadata/lưu; native share sheet ngoài app vẫn Pending TC-OCRP-02 |
| AC3 | Fake prototype phân biệt no_text/input_error/engine_error/cancel; Python no_text vào mẫu số | Pass unit, native blank/hỏng/cancel chưa chạy lại; TC-OCRP-03..05 Pending |
| AC4 | Prototype unit/controller kiểm thao tác lặp/dispose/close/lỗi | Pass unit; back/background/process death native chưa kiểm lại, TC-OCRP-06 Pending |
| AC5 | 41 unit + pipeline raw thật, chọn 2 ảnh/17, exact 1/2, raw lặp/unmapped hiện rõ | Pass công cụ; bộ ảnh/nhãn đầy đủ và điều kiện benchmark chưa đủ |
| AC6 | Hash source trước/sau pipeline nguyên vẹn; code import chỉ ADB/filesystem; unit prototype | Không có mutation thuốc hoặc nhãn vào engine trong luồng kiểm; offline runtime chưa chạy mới, TC-OCRP-07 Pending |
| AC7 | Fixture frozen go/no-go/pending, hash byte thật sai/config/coverage/timestamp sai đều pending; real-data thiếu protocol pending | Pass logic; benchmark Android thật còn Pending TC-OCRD-48, không có kết luận go/no-go |
| AC8 | Pilot not_decided, no-data N/A và báo cáo chỉ rõ phần thiếu | Pass việc báo trạng thái; chưa đóng task |
| AC9 | Shared/inline XLSX header B2, duplicate/formula/nhãn/ảnh thiếu/path escape/JSON lỗi | Pass tự động, không sửa workbook/ảnh |
| AC10 | Single strength/boundary, blank và multi-component chưa chấm | Pass unit; xác minh nhãn thật độc lập Pending TC-OCRD-47 |
| AC11 | Native import bản sao, hash raw cũ/mới, conflict/legacy/mapping ambiguity, SHA-256 provenance | Pass tự động và import từ app; không dựng raw từ screenshot |
| AC12 | Earliest lỗi không thay run đẹp, timestamp/tie/deviceKind/OS; pipeline giữ retry | Pass tự động; không gộp máy ảo/điện thoại |
| AC13 | CLI xuất CSV/JSON/Markdown, 17 ảnh không raw vẫn not_run, exit1 unmapped hiện rõ | Pass tái hiện trên bản sao dữ liệu thật; không cần backend hoặc sửa nhãn |

Đạt công cụ không có nghĩa ML Kit đọc đúng toàn bộ ảnh hoặc matching chọn đúng thuốc. Các unit test không thay thao tác native hoặc phép đo chất lượng thực.

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Kiểm trong phiên này | Kết quả |
|---|---|---|
| Raw bất biến, nhập lại không overwrite | 41 unit liên quan và pipeline bản sao | Pass |
| Run lỗi/no_text/missing không che khỏi báo cáo | Unit + CLI real-data/no-data | Pass |
| Lựa chọn run tất định, không lấy lần đẹp nhất | Unit + hai run vỉ thật và CSV selected | Pass |
| Metadata/ảnh không gán nhầm | Hash nguồn/provenance/mapping; unmapped giữ rõ | Pass cho kiểm đã chạy |
| Thiếu protocol/nhãn/hash/config/coverage không tự go | Unit và real-data mode benchmark | Pass logic; chưa có benchmark thật |
| Chia sẻ native, permission/gallery, lifecycle/offline | Chưa thao tác mới trên UI native | Pending |
| Cross-patient/consent/idempotent dose/schema | Không có service/DB/health endpoint thay đổi | Không áp dụng |

## 4. Toàn bộ bộ kiểm tra phù hợp với thay đổi

- `python -m unittest discover -s datasets/scripts -p "test_*.py" -v`: **41 pass, 0 fail, 1.027s**, evidence/test-dataset-unit.log.
- `python work/4.09-mlkit-prototype/scratch/test_dataset_pipeline.py`: **5 kiểm tra tích hợp host pass**, evidence/test-integration.log. Đi qua ADB thật→JSON gốc→import→CLI evaluate→CSV/JSON/Markdown; kiểm re-import, thống kê/mapping, benchmark thiếu protocol, no-data đủ 17 ảnh và hash nguồn bất biến. Chỉ dùng bản sao scratch.
- `flutter test test/features/ocr_prototype` từ frontend/mobile: **13 pass, 0 fail**, log kết thúc 00:05 +13 All tests passed; evidence/test-ocr-prototype-unit-widget.log. Không cài lại app lên máy ảo. Không chạy lại 546 test toàn app vì đợt mới không sửa frontend; bộ liên quan OCR đã chạy toàn bộ trong phiên này.
- Tổng lượt kiểm tự động: 41 Python + 13 Flutter + 5 host. Số test case Excel là cách tổ chức kiểm tra khác, không đồng nhất với tổng test tự động.
- Không có bộ service-integration áp dụng trong vùng tests/backend. Không reset DB hoặc mở rộng kiểm backend không liên quan.
- `scope.py --stage test` báo nguyên văn “CHẶN: 50 file ngoài phạm vi”, evidence/test-dataset-scope.log. Phân loại ở mục 7, không báo scope toàn repo sạch.

### Dữ liệu thật được đối chiếu

- 17 nhãn/17 ảnh còn nguyên byte; 6 legacy raw và 4 raw mới giữ ở datasets. Vòng test đọc lại/import vào scratch, không tạo raw giả hoặc thay payload.
- 4 raw mới: 3 run ánh xạ vào 2 ảnh bằng SHA-256, 1 raw có ảnh không khớp dataset (c6da86d5-1496-4f70-9fb2-720ae357221c) giữ unmapped. Ảnh vỉ có 2 run, chọn run sớm bf2e373a…; run screenshot 71e2ac39… được giữ là retry, không chọn theo điểm.
- Run screenshot khớp decolgen_forte_blister_002, không phải hộp gửi kèm; hộp decolgen_forte_box_001 là run f5ce68db… Theo phép chấm hiện tại: hộp exact, vỉ đủ token nhưng tách xa; exact=1/2, coverage=2/17, 15 not_run.
- CLI pilot real-data trả 1 vì unmapped, vẫn xuất báo cáo; đây là hành vi mong đợi và đã được kiểm, không phải test fail. decision=not_decided. Mode benchmark thiếu protocol trả pending (vẫn mã 1 vì data error hiện có).
- Metadata lịch sử có osVersion=d/nativeSdkVersion=dd giữ nguyên; ADB observed_device ghi riêng. Cần metadata thực trước benchmark; quan sát lúc nhập không chứng minh metadata tại thời điểm OCR hoàn toàn chính xác.

## 5. Bộ test case Excel

Dùng skill wf-testcase và script chính thức, không tự sửa format bằng code khác.

- Spec: testcases.json.
- File task: testcases.xlsx.
- File tổng người dùng xác nhận “ở trong docs”: docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx.
- Script `validate`, `build`, `merge --into docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` đều exit 0; không có cảnh báo ghi đè kết quả cũ. Log evidence/testcase-xlsx.log.
- Repo chưa khai báo vai trò testcase-book; dùng --into theo đường dẫn đã xác nhận, không tự sửa AGENTS.md. File tổng trước đó chỉ có sheet rỗng; script chính thức tạo OCR Prototype, OCR Dataset, Report và bỏ placeholder rỗng, không có test case cũ bị mất.
- Kiểm file task/master read-only: IDs và counts khớp, 56 ID duy nhất, sheet Report có 2 chart; evidence/testcase-xlsx-verification.log. Không chạy recalculation hoặc render bằng Excel native trong phiên này; không khẳng định đã kiểm hiển thị/tính lại trên Excel.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Prototype ML Kit Android (OCRP) | 8 | 0 | 0 | 8 |
| Nhập và đánh giá OCR dataset (OCRD) | 48 | 46 | 0 | 2 |
| Tổng | 56 | 46 | 0 | 10 |

46 Pass lấy từ 41 unit Python và 5 host checks vừa chạy; 13 test Flutter là evidence bổ sung cho AC3/4, không biến 8 ca native manual thành Pass.

Các Pending cần thực hiện:

- TC-OCRP-01: OCR native trên thiết bị bắt buộc, metadata thực.
- TC-OCRP-02: share JSON qua giao diện hệ điều hành và đọc ngoài app.
- TC-OCRP-03..05: ảnh trắng, file lỗi/quyền đọc, hủy picker native.
- TC-OCRP-06: double tap/back/background/process death/retry native.
- TC-OCRP-07: OCR offline và kiểm không gửi ảnh/mutation thuốc.
- TC-OCRP-08: đối chứng ảnh vỉ nghiêng hướng 1 giờ/7 giờ.
- TC-OCRD-47: người kiểm xác minh nhãn/strength của 17 ảnh.
- TC-OCRD-48: benchmark chính thức đủ dữ liệu/protocol/Q1.

Bug Report mới: 0 test case Fail, không tự dựng bug hoặc nâng lỗi OCR pilot thành bug thuật toán matching.

## 5b. Lỗi sản phẩm và hạn chế đã ghi nhận

- Không tìm thấy lỗi chương trình mới trong 41 unit, 13 Flutter và 5 host checks đã chạy. Không sửa code sản phẩm hoặc nới khẳng định test.
- OCR-TILT-01 từ người dùng báo trước: ảnh vỉ nghiêng hướng 1 giờ/7 giờ đọc chưa đạt. Chưa có cặp đối chứng kiểm trong phiên này; không quy ra góc số hoặc kết luận nguyên nhân chỉ do nghiêng. TC-OCRP-08 Pending; giữ giới hạn chất lượng này trong báo cáo.
- Raw thật ảnh vỉ có token tên tách xa, không đạt exact, nhưng 4.09 chưa có ngưỡng chính thức nên đây là kết quả phép đo, không bằng chứng công cụ chấm bị lỗi. Không dùng fuzzy để nâng điểm.
- 1 run unmapped và metadata nhập thử là thiếu dữ liệu, cần người thử đối chiếu; không tự đoán/ghi đè raw.

## 6. Test không ổn định hoặc bị skip

- Không có unit/host failure mới và không tăng retry/skip để che lỗi. Các ca native/benchmark chưa chạy ghi Pending rõ ràng.
- Unit path escape có nhánh kiểm symlink chỉ khi Windows cho phép tạo symlink; các kiểm ../path tuyệt đối/Windows drive luôn chạy. Không suy rằng nhánh symlink đã chạy nếu OS từ chối privilege.
- Test Excel native render/recalculate chưa thực hiện; kiểm cấu trúc và trạng thái bằng openpyxl read-only.

## 7. Phát sinh và phạm vi

- Scope test báo 50 file ngoài phạm vi: các thay đổi datasets của implement đã approved và baseline đã được người dùng cho giữ, cộng file tổng docs được chỉ định trong lượt này. Chỉ sửa work artifact/scratch/evidence và file tổng docs qua script wf-testcase; không sửa scripts/ảnh/nhãn/raw/frontend ở test stage.
- Vì testcase-book chưa khai báo, scope.py không nhận file tổng như vùng test hợp lệ; đã dùng --into sau khi hỏi và được người dùng chỉ định docs. Không tự sửa scope.py/AGENTS để báo sạch.
- Docs nhánh codex/4.09-ocr-testcases, chỉ Test_Cases.xlsx thay đổi; frontend sạch. Không commit/push/stage con trỏ, không đổi nhánh dataset hoặc ML Kit.
- Nhánh đề xuất chưa được tạo trong repo khác và không có task/thread mới. Các artifact approved giữ nguyên.

## Bước tiếp theo

- **Chưa đề nghị duyệt 05 hoặc chuyển review**, vì còn 10 test case Pending, 15 ảnh chưa chạy và chưa có benchmark/go-no-go.
- Người thử tiếp tục quét 15 ảnh theo đúng image_id, nhập metadata thực; giữ mọi run và raw. Sau đó nhập/chấm vào session phù hợp theo datasets/README.md; không chọn lần tốt nhất hoặc tự đổi ngưỡng.
- Xác minh run chưa ánh xạ và labels/strength; chạy các ca native còn thiếu trên thiết bị đã chốt, ghi evidence rồi cập nhật kết quả manual/spec/file tổng. Không tự đổi Pending thành Pass từ unit test.
- Q1: nhóm chốt bộ ảnh/thiết bị/ngưỡng/protocol trước lần đo chính thức. Khi đủ và report hoàn chỉnh mới dùng lệnh duyệt: python .agents/scripts/gate.py approve 4.09-mlkit-prototype test.
- Cập nhật: 2026-10-28, Codex.
