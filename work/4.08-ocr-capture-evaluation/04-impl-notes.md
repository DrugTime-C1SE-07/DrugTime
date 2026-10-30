---
task: 4.08-ocr-capture-evaluation
stage: implement
owner: Bao Nguyen
started_at: 2026-10-26 17:00
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 16:34 +0700
content_hash: sha256:544eece4a736ff20
inputs:
  01-requirement.md: sha256:2c4a08a77f82f9e0
  03-plan.md: sha256:981facafd3a1d985
---
# 4.08 · Implement bộ ảnh có nhãn v1


Ngày: 2026-10-29. Requirement/plan mới đã approved, gate implement OK. Không nghiên cứu engine/góc tối ưu; không chạy công cụ OCR cũ. Nội dung dưới áp dụng hiện tại, các mục sau phần Lịch sử không là điều kiện hoàn thành mới.

## Tiến độ theo plan mới

| Bước | Trạng thái | Bằng chứng |
|---|---|---|
| P1 baseline | Xong | scratch/review-v1/baseline.json; evidence/implement-label-review-baseline.log; superproject feat/datasets-ocr, frontend feat/mlkit-prototype-measurement sạch |
| P2 rà ảnh/nhãn/nguồn | Xong rà trực quan bằng AI, chưa review độc lập | Đã xem đủ 49 ảnh qua contact sheets; 23 dòng sửa theo ảnh, không theo raw. datasets/annotations.v1.csv; scratch/review-v1/label-changes.json và labels-before-review.xlsx; evidence/implement-label-review.log |
| P3 cấu trúc/hash | Xong | 49 ID/path/ảnh/nhãn khớp, 0 lỗi reader; 49 byte ảnh không đổi; evidence/implement-v1-integrity.log |
| P4 manifest | Xong | datasets/manifest.v1.json: version/hash/stats/verification/limitations; hash tái tính khớp, annotations có hash riêng; evidence/implement-v1-integrity.log |
| P5 README | Xong | datasets/README.md dẫn v1/pilot-002/decision và hạn chế; trạng thái local_only rõ |
| P6 bàn giao hồ sơ | Xong chuẩn bị, publish/clone/PR Pending | Scope/evidence và danh sách file sẵn; không tự commit/push hoặc tuyên bố nhóm đã pull được |

## File thay đổi và quyết định nhãn

- datasets/labels.xlsx: sửa 23 dòng có bằng chứng ảnh; không đổi ID/path/layout/style hoặc ảnh. Bisoheart khác A.T Bisoprolol; Atorvastatin nhiều nhà sản xuất không tự thêm A.T; Candesartan Krka/A.TCANDESARTAN HTZ/ACANTANHTZ là các tên riêng; Lifezine/Levocetirizin không đồng nhất với 1-AL. Ghi từng thay đổi trong label-changes.json.
- 1-AL hộp trắng không có hàm lượng đọc được: bỏ giá trị 5mg suy từ folder/ảnh khác. Tên/hàm lượng tách riêng. Trường thiếu giữ trống, đặc biệt nhãn nhiều thành phần không tự chọn một số mg.
- datasets/annotations.v1.csv: 49 dòng, verified_by ghi đúng “Codex visual inspection (AI, not independent human sign-off)”, ngày 2026-10-29. Watermark ghi như quan sát, không bịa URL nguồn; người chụp/thiết bị/điều kiện không biết ghi unknown. Không thấy patient identifier/secret khi xem 49 ảnh.
- datasets/manifest.v1.json: 49 ảnh, 23 nhãn sản phẩm, 28 hộp/21 vỉ; không trùng byte. 15 ảnh chụp cầm tay nguồn chưa rõ, 34 ảnh sản phẩm nguồn chưa rõ. Không coi khác byte là độc lập mẫu nguồn; giới hạn đại diện chưa kiểm.
- datasets/README.md: quy ước/phiên bản/tái hiện/giới hạn và quyết định 4.09. Không sửa scripts/frontend/engine hoặc dữ liệu .gitignore/api_contract/docs của người dùng.

## Kiểm chứng và AC

- Lệnh thực: bundled Python chạy scratch/review_dataset.py, finalize_dataset_v1.py, verify_v1.py. Logs: implement-label-review-baseline.log, implement-label-review.log, implement-v1-integrity.log. Các script tác vụ ở scratch, không yêu cầu thêm công cụ runtime cho dataset.
- AC1/T1: 49 ID duy nhất, mỗi ảnh một hàng, path có thật, reader 0 lỗi. AC2/AC3/T2: đọc ảnh và sửa tên/strength có chứng cứ, không dùng raw làm nhãn; đánh dấu nguồn rà là AI, không giả thành người khác ký duyệt.
- AC4/T3/T4: manifest/statistics/hash từ byte thật, nguồn chưa rõ ghi unknown, có limitations. Thử tamper snapshot bằng fixture của unit reader trong bộ 41 test vừa chạy ở work/4.09-mlkit-prototype/evidence/implement-v1-final-unit.log (41 pass, 1.482s); kiểm snapshot thật độc lập tại implement-v1-integrity.log.
- AC5: không thấy PHI/credential khi rà ảnh; phần chưa rõ không suy thành đáp án. Có thể cần reviewer đọc lại chữ cách điệu/tên dài, đã nêu trong annotations.
- AC6: README/local artifact sẵn; kiểm clone/pull và publish Pending vì chưa có yêu cầu commit/push. Không gọi task complete.
- Workbook fallback openpyxl do artifact-tool rendering không hoạt động ở lượt chỉnh cùng hội thoại; backup trước sửa. Read-back xác nhận chỉ ô tên/strength có trong change list đổi, style/ô còn lại không đổi. Chưa render/tính lại bằng Excel native; không tuyên bố đã kiểm Excel UI.

## Phát sinh/phạm vi

- scope.py --stage implement: “CHẶN: 226 file ngoài phạm vi”, evidence/implement-v1-scope.log. Bộ kiểm scope nhìn toàn repo: code/raw/pilot/report của 4.09, các ảnh/công cụ/baseline có sẵn được người dùng cho giữ, và tài liệu docs. Lượt này chỉ sửa 4 file được plan 4.08 cho phép; các thay đổi quyết định/report 4.09 có plan riêng cũng được người dùng duyệt trong cùng lượt. Không sửa phạm vi/approval để báo sạch giả, không xin lại quyền giữ thay đổi đã được cho phép.
- Không xóa nghiên cứu/evidence lịch sử; bỏ chúng khỏi điều kiện hoàn thành hiện hành theo requirement mới. Không commit/push hoặc đổi nhánh.

## Bước tiếp theo

- Chờ duyệt implement: python .agents/scripts/gate.py approve 4.08-ocr-capture-evaluation implement
- Sau duyệt, lượt sau wf-test xác minh độc lập dữ liệu/README/manifest, làm testcase và review. Publish/PR theo Definition of Done chỉ khi người dùng yêu cầu commit/push; chuẩn bị kết quả trước, chưa tự ghi đã chia sẻ.
- Cập nhật: 2026-10-29, Codex.


## Lịch sử triển khai trước 2026-10-29


# 4.08 · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `python -B work/4.08-ocr-capture-evaluation/run_ocr.py work/4.08-ocr-capture-evaluation/images/hapacol_extra_original.png`: thành công, 11 dòng, raw/TSV/stderr/metadata | evidence/implement-P1.log |
| P2 | xong | `python -B -m unittest discover -s work/4.08-ocr-capture-evaluation -p test_run_ocr.py -v`: 15/15 pass; bảng Unicode/wrap, CSV, lỗi/model thiếu và run riêng | evidence/implement-P2.log; evidence/implement-final-superproject.log |
| P3 | xong | CLI trên ảnh hapacol_650_extra_original.png thành công, 15 dòng; đọc lại CSV, kiểm tra độ rộng bảng và hash ảnh cả hai run | evidence/implement-P3.log; evidence/implement-export-verification.log |
| P4 | chưa làm | Cần ảnh chụp thật và nhãn đã xác minh | Chưa có |
| P5 | chưa làm | Cần bộ ảnh theo góc và đáp án | Chưa có |
| P6 | chưa làm | Cần kết quả đánh giá và holdout | Chưa có |
| P7 | xong | Đọc nhãn C2/Sheet1, shared/inline strings, thiếu/trùng hàng/sheet; hash nhãn không đổi | evidence/implement-P7-P9.log; evidence/implement-comparison-verification.log |
| P8 | xong | Trích ứng viên bằng geometry/regex; khử trùng/vùng độc lập; Levenshtein complete-link chỉ gom biến thể; test đổi nhãn không thay extraction | evidence/implement-final-superproject.log |
| P9 | xong | CLI tự đối chiếu nhãn, --labels/--sheet/--no-labels, comparison.csv/txt và fields.json; lỗi nhãn giữ raw và báo failed | evidence/implement-final-superproject.log |
| P10 | xong | 37 test pass, lint pass, 2 ảnh chạy thật, CSV/evidence/độ rộng bảng/hash nhãn xác minh | evidence/implement-P10-extra.log; evidence/implement-P10-650.log; evidence/implement-comparison-verification.log |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| superproject (cục bộ) | Không tạo/đổi nhánh | run_ocr.py; test_run_ocr.py; ocr_fields.py; test_ocr_fields.py; README.md; 04-impl-notes.md; results/**; evidence/** trong thư mục task |

Không sửa submodule, bộ cài hoặc labels.xlsx; không commit/push.

`python .agents/scripts/scope.py 4.08-ocr-capture-evaluation --stage implement`: OK, không có thay đổi ngoài work/ — log evidence/implement-scope.log. Do work/ không được Git theo dõi, scope ghi CHƯA SỬA cho một số file đã tạo; kiểm tra trực tiếp và log chạy công cụ xác nhận file thực tế tồn tại.

## 3. Kết quả test cuối

| Phạm vi | Lệnh | Kết quả | Log |
|---|---|---|---|
| Công cụ cục bộ | `python -B -m unittest discover -s work/4.08-ocr-capture-evaluation -p "test_*.py" -v` | 37 pass, 0 fail; gồm 15 test cũ | evidence/implement-final-superproject.log |
| Lint | `backend/.venv/Scripts/ruff.exe check --no-cache work/4.08-ocr-capture-evaluation/run_ocr.py work/4.08-ocr-capture-evaluation/ocr_fields.py work/4.08-ocr-capture-evaluation/test_ocr_fields.py work/4.08-ocr-capture-evaluation/test_run_ocr.py` | All checks passed; format các file Python bằng Ruff | evidence/implement-lint.log |
| Tesseract thật | CLI với hai ảnh web hiện có | 2 run thành công, 11 và 15 dòng | evidence/implement-P1.log; evidence/implement-P3.log |
| Export | Đọc CSV, kiểm tra line_count, độ rộng hiển thị mọi dòng bảng, hash ảnh so metadata | 2 run PASS | evidence/implement-export-verification.log |
| Đối chiếu nhãn thật | CLI hai ảnh, đọc lại 5 dòng comparison.csv/ảnh, evidence JSON, table width <=110 và hash labels trước/sau | 2 run PASS; không sửa labels.xlsx | evidence/implement-comparison-verification.log |

Lần test đầu gặp PermissionError khi tempfile dùng thư mục hệ thống trong sandbox; đã chuyển thư mục tạm test vào results/ và xác minh đường dẫn tuyệt đối trong results/ trước cleanup. Chạy lại thành công. Lint lần đầu phát hiện thứ tự import; đã sửa và chạy lại đạt.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

P1–P3 và P7–P10 hoàn thành (7/10 bước); P4–P6 chưa có đầu vào ảnh chụp thật. Chạy một lệnh cho mỗi ảnh, mặc định eng, PSM=3/OEM=3. Một lần nhận diện Tesseract sinh cả txt/tsv. Kết quả lưu riêng theo run, CSV UTF-8 BOM và bảng ASCII wrap theo độ rộng terminal. Confidence là trung bình điểm từ hợp lệ, không phải accuracy.

CLI tự dùng labels.xlsx cạnh script nếu tồn tại; mặc định hiển thị bảng đối chiếu. Dùng --no-labels để chỉ xem raw. Hàm extraction không nhận filename hoặc nhãn; Excel chỉ đưa vào comparator sau extraction. Không sửa chữ sai bằng đáp án. JSON giữ mọi ứng viên/evidence và chữ chưa phân loại, bảng chính giới hạn ba ứng viên/ô và ghi số còn lại; CSV giữ đầy đủ.

Grammar trích hàm lượng hiện chỉ hỗ trợ tên + số + đơn vị đơn giản; không chứng minh đúng ngữ nghĩa dược chất hoặc mọi tên ghép/tỷ lệ. Name geometry tạo giả thuyết, không phải xác nhận sản phẩm. Tên thiếu hoặc nhiều cách ghép được đánh dấu Thiếu/Cần xác minh. Levenshtein chỉ nhóm tên gần nhau, không tự sửa hoặc chấm Đúng. Trường có ứng viên mâu thuẫn được giữ và chấm bảo thủ.

Kết quả thực tế:
- results/20261026_170237_326044_e7dbb214/: Hapacol Extra, 11 dòng.
- results/20261026_170302_118668_b0b6bfd9/: Hapacol 650 Extra, 15 dòng.
- results/20261026_202111_787415_18dbc2ef/: đối chiếu Hapacol Extra; tên có ứng viên ghép nhưng Cần xác minh, hoạt chất/hàm lượng Sai vì có biến thể ccafein; hãng Sai, JAPAN GMP Thiếu.
- results/20261026_202112_443546_2d99d7eb/: đối chiếu Hapacol 650 Extra; hoạt chất/hàm lượng Đúng theo nhãn hiện tại, tên Thiếu, hãng Sai, JAPAN GMP Thiếu. Báo nhãn tên không gồm 650 để người dùng xác minh; không tự sửa.
- Hash labels.xlsx trước/sau hai lần chạy mới: 8a38c0dec1d03a0282698b935dd185f7f17375d2f15b35d94c5d3b9896dc51e5.

CSV phòng công thức bằng dấu nháy đơn trong ô có tiền tố nguy hiểm; raw.txt/words.tsv giữ nguyên. Kết quả hiển thị tiếng Việt tốt nhất với terminal/font monospace UTF-8; ký tự điều khiển được thay bằng khoảng trắng chỉ trong bảng hiển thị.

## 6. Phát sinh

Không có thay đổi phạm vi. P4–P6 cần ảnh chụp thật, metadata góc/ánh sáng và nhãn người dùng xác minh, hiện chưa có. Hai ảnh web không phải bằng chứng để chọn góc tốt nhất. Chưa tạo evaluation.csv/capture-rules.md hoặc số liệu accuracy giả.

Phản hồi tiếp theo của người dùng: nhiều dòng rác/lặp, tiếng Việt sai, tên Hapacol Extra chưa ghép được. Đã chạy lại hai ảnh với `--psm 11`, vẫn eng, không thay code hoặc model. Log: evidence/implement-psm11-extra.log và evidence/implement-psm11-650.log. Run mới có 20 và 37 dòng, xuất được HAPACOL/Extra rời nhau và vẫn nhiều dòng nhiễu. Đây không phải bằng chứng accuracy cao hơn; chưa có pipeline ghép tên sản phẩm. Máy vẫn thiếu vie. Rule lọc/gom theo trường hoặc ghép theo vị trí là mở rộng so với plan hiện chỉ xuất dòng OCR thô, phải đề xuất cập nhật plan trước khi thêm. Không tự sửa đáp án hoặc đổi tên thuốc dựa vào suy đoán.

Sau đó người dùng đã reopen và approve plan bổ sung P7–P10, triển khai như phần tiến độ trên. Chưa tự cài vie hoặc thay OCR engine. Test đầu vòng bổ sung dùng sai fixture Paracetamo1 (có chữ số nên phải bị bảo vệ khỏi fuzzy); đổi fixture thành biến thể ký tự Paracetamoi và giữ test số riêng. Chạy cuối 37 test đạt. Không có thay đổi file ngoài plan.

## Bước tiếp theo

- Cập nhật 2026-10-29: người dùng loại nghiên cứu Tesseract khỏi phạm vi. 4.08 theo bảng Sprint mới chỉ thu thập/gắn nhãn/bàn giao dataset. P4–P6 nghiên cứu engine bên dưới là lịch sử, không tiếp tục yêu cầu thực hiện để đóng bộ ảnh. Cần reopen requirement/plan approved để đồng bộ; nội dung thay thế cụ thể ở scope-correction.md. Không sửa artifact approved hoặc xóa bằng chứng lịch sử trong lượt này.

- Đang chờ: người dùng dùng bảng đối chiếu, xác minh nhãn tên ảnh 650 và cung cấp ảnh chụp thật/nhãn để làm P4.
- Việc cần làm: tiếp tục P4–P6 khi có bộ ảnh có góc/ánh sáng; chưa đề nghị duyệt implement vì phần nghiên cứu góc chụp chưa hoàn tất. Chưa chuyển test/review.
- Không commit/push work/.
- Cập nhật lần cuối: 2026-10-26 20:21, Codex.
