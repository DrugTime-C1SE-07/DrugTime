---
task: 4.08-ocr-capture-evaluation
stage: test
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 16:53 +0700
content_hash: sha256:38974180712acae4
inputs:
  01-requirement.md: sha256:2c4a08a77f82f9e0
  03-plan.md: sha256:981facafd3a1d985
  04-impl-notes.md: sha256:544eece4a736ff20
---

# 4.08 · Kiểm bộ ảnh bao bì có nhãn v1

Ngày lập kiểm chứng: 2026-10-29. Hồ sơ bộ ảnh/nhãn v1 đã sẵn sàng để người duyệt xem xét và chuyển review. Kiểm cấu trúc/hash/tài liệu có bằng chứng; dữ liệu còn cục bộ, chưa công bố qua remote. Không có yêu cầu nghiên cứu Tesseract trong phạm vi hiện hành.

## Điều chỉnh cách chốt task theo chỉ dẫn mới

- Người dùng phản hồi “task này đâu có cần test đâu ta”, rồi yêu cầu “tiếp tục làm cho tôi” sau khi thống nhất chốt đúng phạm vi bộ ảnh và prototype. Không yêu cầu người dùng làm thêm bộ kiểm thủ công hoặc rà lại toàn bộ 49 ảnh để chốt hồ sơ.
- 4.08 bàn giao bộ ảnh có nhãn, nguồn/giới hạn, phiên bản/hash và README. Việc AI đã đối chiếu ảnh được ghi đúng là AI review; không giả chữ ký hoặc một lượt kiểm của người khác.
- TC-PKGDATA-02 giữ Pending như thông tin về kiểm độc lập chưa thực hiện, không là yêu cầu bổ sung chặn chốt phiên bản mẫu hiện tại. TC-PKGDATA-08 thuộc bàn giao sau khi có yêu cầu commit/push; chưa push không đồng nghĩa thiếu phần tạo bộ ảnh cục bộ.
- Các hàng Pending trong bảng dưới ghi mức kiểm chứng thực tế, không phải danh sách bắt người dùng làm thêm. Chưa xác nhận production readiness hoặc Definition of Done về PR/reviewer.
- Không sửa 01/03/04 đã approved. Đây là ghi nhận chỉ dẫn mới và cách chấp nhận giới hạn trong báo cáo draft, không đổi kết quả test hoặc nhãn.

## 1. Môi trường

- Gate test OK với requirement/plan/implement đã approved: `evidence/test-v1-gate.log`.
- Windows, Python 3.13 và bundled Python có openpyxl. Superproject `feat/datasets-ocr`; docs `codex/4.09-ocr-testcases`; frontend `feat/mlkit-prototype-measurement` sạch.
- Dataset v1: 49 ảnh, 28 hộp/21 vỉ, 23 tên sản phẩm; hash `588a56f54a5155250ce6c5fc633b60d05351f20561d46ba49ed482eab1b77e7f`.
- Test stage chỉ đọc nguồn và kiểm fixture/bản sao work; không sửa ảnh/nhãn/raw hoặc code sản phẩm. Không API/DB sức khỏe, không reset DB.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Test/bằng chứng | Kết quả |
|---|---|---|
| AC1 | verify_v1 T1, reader/validation unit, TC-PKGDATA-01 | Pass: 49 ID duy nhất, đủ hàng/đường dẫn, 0 lỗi cấu trúc |
| AC2 | annotations và nhật ký 23 hàng sửa theo ảnh; TC-PKGDATA-02/03 | Có review AI; người kiểm độc lập Pending |
| AC3 | Workbook preservation, annotations, 1-AL không suy 5mg; TC-PKGDATA-02/03 | Pass kiểm dữ liệu đã ghi; xác minh trực quan độc lập Pending |
| AC4 | verify_v1 T4, snapshot fixture, README; TC-PKGDATA-04..07 | Pass hash/count/nguồn chưa rõ/giới hạn; không coi các view là nguồn độc lập |
| AC5 | annotations ghi AI reviewer và unknown; TC-PKGDATA-02/05 | Pass trung thực metadata; người khác rà PHI/secret/nhãn Pending |
| AC6 | README có hướng dẫn/local-only; TC-PKGDATA-07/08 | Pass chuẩn bị cục bộ; commit/push/clone/pull chưa thực hiện |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Không bỏ hàng sai ID/path âm thầm | Unit công cụ dataset + verify_v1 | Pass |
| Đổi byte ảnh làm đổi snapshot hash | test_snapshot_tracks_actual_image_bytes trên fixture | Pass |
| Không bịa nguồn/thiết bị/người kiểm | verify_v1 T2/T3 + annotations | Pass; reviewer là AI, không giả human sign-off |
| Không đổi style/ô workbook ngoài nhật ký | So backup/changes | Pass |
| Patient/consent/dose/RLS | Không thay đổi service/schema sức khỏe | Không áp dụng |

## 4. Các kiểm tra đã chạy

Các kết quả dưới đây là bằng chứng của lượt kiểm trước ngày 2026-10-29; lượt chỉnh hồ sơ này không chạy lại unit/OCR và không nhận là kết quả chạy mới.

- Bundled Python `work/4.08-ocr-capture-evaluation/scratch/verify_v1.py`: các khẳng định đạt, hash/count khớp, 49 ảnh/raw không đổi; `evidence/test-v1-integrity.log`.
- `python -m unittest discover -s datasets/scripts -p "test_*.py" -v`: 41 pass, 0 fail, 1.113s; bộ dùng chung với 4.09, không tính thêm lượt chạy. Log `../4.09-mlkit-prototype/evidence/test-v1-unit.log`.
- README/spec: `evidence/test-v1-readme-spec.log`. Không chạy lại OCR hoặc clone từ remote.
- Scope test exit 1: “CHẶN: 230 file ngoài phạm vi”; `evidence/test-v1-scope.log`. Không báo scope sạch.

## 5. Bộ test case Excel

- Spec `testcases.json`; file task `testcases.xlsx`; file tổng người dùng chỉ định: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`.
- Script chính thức validate/build/merge --into thành công, không cảnh báo đổi Pass/Fail cũ; `evidence/testcase-v1-xlsx.log`.
- Kiểm read-only sheet/ID/status khớp: `../4.09-mlkit-prototype/evidence/testcase-v1-verification.log`. Chưa render/recalculate bằng Excel native.

| Chức năng | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Packaging Dataset (PKGDATA) | 8 | 6 | 0 | 2 |

- TC-PKGDATA-02: người khác rà 49 ảnh/nhãn/strength/PHI, ghi người/ngày thật.
- TC-PKGDATA-08: sau yêu cầu publish, kiểm clone/pull đủ ảnh/nhãn/hash trên checkout khác.
- Bug Report mới: 0 Fail.

## 5b. Lỗi sản phẩm tìm thấy

Không có lỗi chương trình mới trong kiểm tra đã chạy. Nguồn/điều kiện chưa biết ghi unknown; AI review không thay xác minh độc lập.

## 6. Test không ổn định hoặc bị skip

Không failure bị che bằng retry/skip. Manual chưa thực hiện để Pending. Bộ nhỏ không chứng minh đại diện mọi điều kiện; không đặt quota ảnh mới ngoài scope.

## 7. Phát sinh

- Lượt chỉnh hồ sơ theo chỉ dẫn mới: gate test OK (`evidence/test-scope-clarification-gate.log`); scope vẫn exit 1 với 230 file đã có (`evidence/test-scope-clarification.log`). Lượt này chỉ sửa hai báo cáo draft và handoff/evidence trong work; không sửa workbook tổng, dataset, code hoặc artifact approved. Không chạy lại test/OCR.
- Scope toàn repo gồm 226 file datasets, 2 api_contract, 1 .gitignore, 1 workbook tổng docs. Datasets là baseline và implement của hai task đã duyệt; .gitignore/api_contract là thay đổi riêng đã được người dùng yêu cầu giữ. Không sửa các file nguồn này ở test stage.
- Chưa khai báo testcase-book; dùng --into đúng file docs đã được người dùng xác nhận. Không sửa AGENTS/scope để làm xanh.
- Merge đầu tiên gõ nhầm `04_Quality_And_Testing`, tạo workbook mới 8 case. Đã kiểm sheet/count rồi xóa đúng file vừa tạo; gộp lại vào `04_Quality_&_Testing` và kiểm đủ các chức năng OCR cũ. File nhầm không còn.
- Không commit/push/bump con trỏ hoặc đổi nhánh. Giữ nguyên artifact approved.

## Bước tiếp theo

- Chờ người duyệt xem báo cáo với giới hạn đã ghi, dùng `python .agents/scripts/gate.py approve 4.08-ocr-capture-evaluation test`.
- Sau duyệt, lượt tiếp theo review hồ sơ/dữ liệu đúng phạm vi 4.08; không yêu cầu bộ kiểm Android hoặc kiểm nhãn độc lập bổ sung để bắt đầu review.
- Khi người dùng yêu cầu commit/push, publish datasets và artifact/evidence đúng phạm vi, không commit scratch. Kiểm clone/pull tại bước bàn giao đó; chưa tuyên bố đã chia sẻ từ remote.
- Chưa tự approve hoặc tuyên bố hoàn tất Definition of Done về PR/reviewer.
- Cập nhật: 2026-10-29, Codex.
