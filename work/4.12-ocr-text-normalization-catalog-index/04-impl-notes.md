---
task: 4.12-ocr-text-normalization-catalog-index
stage: implement
owner: phucnguyenngoc
started_at: 2026-10-30
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-30 13:37 +0700
content_hash: sha256:524fa01907d961a8
inputs:
  01-requirement.md: sha256:af09eb8e3be07716
  03-plan.md: sha256:1561587391291ad5
---

# 4.12 · Implement giữ dòng OCR, gom cụm và tra cứu catalog bằng DB index

Đã hoàn thành P1–P8 theo 01/03 mới được duyệt ngày 30/10/2026. Lịch sử implement trước đổi phạm vi lưu nguyên tại `evidence/implement-refresh-before.md`; kết quả cũ không được dùng nghiệm thu AC mới. P9–P11 thuộc giai đoạn test, chưa thực hiện trong lượt này.

## 1. Tiến độ

Mọi đường dẫn log bên dưới tính từ thư mục task. Lệnh backend dùng `backend/.venv/Scripts/python.exe`; workflow dùng `C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe` vì alias WindowsApps không chạy. Output thô lưu bằng `2>&1 | Tee-Object`.

| Bước | Trạng thái | Kiểm chứng trong lượt này | Log |
|---|---|---|---|
| P1 | xong | DTO frozen/tuple: nguồn dòng, strength, cụm, candidate/nguồn, normalized document trong lookup; unit giữ ID/raw/null và cấm gán lại | `evidence/implement-refresh-targeted-final.log` |
| P2 | xong | LF/CRLF/CR/trống cuối/offset; clean NFC còn dấu, key bỏ dấu; whitelist và eligibility có reason; không xóa số tên/mở rộng Met. | cùng log P1 |
| P3 | xong | Detector cũ được tái dùng theo từng dòng/nhóm; Decimal canonical, hợp lệ/chưa hiểu độc lập, mỗi canonical tối đa một phiếu mỗi line; giữ thiểu số/hòa/xung đột | cùng log P1 |
| P4 | xong | Complete-link, signature hàm lượng, chặn số khác nhau và cầu nối thiếu strength; đại diện theo hỗ trợ; ratio cache trong một lượt | cùng log P1 |
| P5 | xong, giới hạn tập nhỏ | Người dùng xác nhận 4 đáp án cặp dòng từ 2 raw; thử 5 ngưỡng và chốt 0.86; regression thật + synthetic; xử lý 49 raw kiểm bảo toàn nguồn, không coi là accuracy | `evidence/implement-refresh-cluster-calibration.log/.json`, log P1 |
| P6 | xong code/unit | CLI tạo migration alias GIN; 3 nhánh SELECT parameterized, literal escape, active only, probe 201 distinct ID/nguồn; alias giữ đủ hit theo ID; DB thật chờ P9 | `evidence/implement-refresh-migration-new.log`, log P1 |
| P7 | xong | Facade/application lookup dùng chung; dedup query trong lượt, giữ mọi cụm/nguồn; lỗi nhánh/iterator truyền lên; không snapshot xuyên lượt; builder cũ đã xóa | log P1, `evidence/implement-refresh-audit-final.log` |
| P8 | xong với lỗi nền/phạm vi kế thừa được ghi rõ | 213 targeted pass; full unit/architecture 1518 pass/30 fail nền; 5 test U12 thêm sau collection full đã pass ở targeted cuối; lint 31 nền/0 mới; audit hash/phạm vi | các log ở mục 3 và 6 |

## 2. File đã thay đổi

Backend trên nhánh `feat/4.12-ocr-text-normalization-catalog-index`, không detached. Tiếp tục các thay đổi task cũ được plan ghi nhận; không stash/reset/stage/commit/push. Có 12 file mới/sửa hiện trong git status và xóa builder từng là file untracked của vòng cũ.

| Nhóm | File tính từ gốc backend |
|---|---|
| DTO | `src/drugtime/modules/catalog/domain/catalog_index.py` |
| Normalize/parser | `src/drugtime/modules/catalog/application/normalize_ocr.py` |
| Gom cụm mới | `src/drugtime/modules/catalog/application/cluster_ocr_lines.py` |
| Lookup mới | `src/drugtime/modules/catalog/application/lookup_ocr_candidates.py` |
| Builder cũ đã xóa | `src/drugtime/modules/catalog/application/build_catalog_index.py` |
| SQL adapter | `src/drugtime/modules/catalog/adapters/outbound/sql_catalog.py` |
| Facade/export DTO | `src/drugtime/modules/catalog/api.py` |
| Migration mới | `supabase/migrations/20261030025813_catalog_ingredient_alias_search.sql` |
| Unit | `tests/unit/test_catalog_ocr_normalization.py`, `test_catalog_ocr_clusters.py`, `test_catalog_index.py`, `test_catalog_sync.py` |
| Fixture | `tests/fixtures/catalog_ocr_clustering.json` |

Không sửa source ngoài bảng 03. Search/CRUD HTTP cũ giữ nguyên diff; ingest chỉ đổi tên AC của regression sẵn có sang AC20. Toàn bộ source catalog không còn CatalogIndex/IndexedMedication/build_catalog_index/load_catalog_index/list_for_index. Integration cũ vẫn gọi facade cũ, cần thay ở P9 theo plan; chưa gọi đó là regression DB đã được nghiệm thu.

## 3. Kết quả kiểm chứng

Lệnh pytest/ruff chạy tại `backend` trừ lệnh scratch chạy từ gốc. Log `implement-refresh-*` mới, không ghi đè log lịch sử trước vòng này.

| Lệnh | Kết quả thực thi | Log |
|---|---|---|
| Workflow Python + `gate.py 4.12-ocr-text-normalization-catalog-index implement` | exit0, được bắt đầu | `evidence/implement-refresh-gate.log` |
| `python -m pytest -p no:cacheprovider tests/unit/test_catalog_ocr_normalization.py tests/unit/test_catalog_ocr_clusters.py tests/unit/test_catalog_index.py tests/unit/test_catalog_sync.py tests/unit/test_catalog_search.py tests/unit/test_catalog_crud.py tests/architecture --junitxml=... --tb=short` | cuối: **213 passed**, 1 warning, không skip | `evidence/implement-refresh-targeted-final.log/.xml` |
| `python -m pytest -p no:cacheprovider tests/unit tests/architecture --junitxml=... --tb=short` | **1518 passed, 30 failed**, 8 warnings, không skip; collection 1548 trước khi thêm 5 test U12 cuối | `evidence/implement-refresh-unit-final.log/.xml` |
| `python work/.../scratch/run_baseline_refresh.py` | source HEAD `2439aa66` được xuất vào scratch, cùng dependencies/contract hiện tại: **86 passed, 30 failed**; 30 nodeid trùng full hiện tại, 0 lỗi mới | `evidence/implement-refresh-unit-baseline.log` |
| `python -m ruff check --no-cache .` (được script baseline gọi và đối chiếu từng finding với source HEAD) | **31 lỗi có sẵn, 0 lỗi mới**; không gọi toàn repo lint pass | `evidence/implement-refresh-lint-baseline-final.log` |
| `python -m ruff check --no-cache` trên 9 file source/unit mới sửa trừ SQL adapter | All checks passed; SQL adapter còn đúng 2 E501 baseline ở CRUD cũ, không sửa lan | `evidence/implement-refresh-lint-changed-final.log` |
| `python -m ruff format --no-cache` trên 9 file trên; SQL chỉ sửa import mới | Đã format; không format lan CRUD/search cũ | `evidence/implement-refresh-format-final.log`, `...-sql-imports.log` |
| `python work/.../scratch/calibrate_refresh.py` | exit0: hash/source line của 4 cặp đúng; 49/49 raw tái ghép dòng đúng, không nhân thành viên; chọn T=0.86 | `evidence/implement-refresh-cluster-calibration.log/.json` |
| Workflow Python + `scope.py 4.12-ocr-text-normalization-catalog-index --stage implement` | **exit1**, 1 NGOÀI là integration test cũ; xem mục 6, không gọi scope pass | `evidence/implement-refresh-scope.log` |
| `python work/.../scratch/audit_refresh_final.py` | exit0: 6 hash bảo vệ không đổi; không migration cũ bị sửa; không source builder cũ; 30 fail trùng baseline; tất cả path backend thuộc plan | `evidence/implement-refresh-audit-final.log` |

Lần P1–P4 đầu có 1 test đại diện fail vì test đặt threshold0.70 trong khi ratio thực của dòng dài thấp hơn. Sửa riêng threshold kiểm thử thành0.65 để kiểm nhánh đại diện đã nhập cụm, không nới ngưỡng production. Log đầu giữ tại `implement-refresh-P1-P4.log`; các lần cuối pass. Các lỗi UTF-8/cwd của script chỉnh sửa đã sửa trước khi ghi tiếp; không dùng lệnh lỗi làm bằng chứng pass.

30 lỗi nền: 24 ca contract thiếu path/khác semantics trong checkout api_contract hiện tại, 6 ca profile invalid-auth mong401 nhưng nhận422. Đã tái hiện trên source HEAD trong chính lượt này; không sửa contract/auth hoặc expected ngoài phạm vi để làm xanh. Các warning là Starlette TestClient deprecation và JWT key ngắn trong fixture auth hiện hữu.

## 3b. Bộ test case Excel

Task L: làm ở P11/giai đoạn test. Workbook/spec/report lịch sử không được coi là phủ 23 AC mới. Không dựng/merge workbook trong lượt implement.

## 4. Migration

Tạo bằng Supabase CLI2.120.0, một file mới `20261030025813_catalog_ingredient_alias_search.sql`: BEGIN → CREATE INDEX `ingredient_aliases_search_idx` trên `public.catalog_search_key(alias_text) extensions.gin_trgm_ops` → COMMIT.

Tái dùng function/index tên/hoạt chất và các index liên kết hiện có; không đổi bảng/cột/constraint/enum/function/data/grant/RLS. Không mở quyền client/API/worker mới. GIN transactional có thể chặn writer và tăng disk: triển khai cần cửa sổ bảo trì. Chưa chạy DB reset/upgrade/EXPLAIN/ACL/freshness trên DB thật; thuộc P9 theo 03. AC16/AC17/AC19 phần DB chưa được nghiệm thu. Không sửa migration cũ; audit git xác nhận.

## 5. Quy tắc nghiệp vụ, ngưỡng và giới hạn

Đã đọc lại 01/03 và tài liệu `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`: quy ước trạng thái, mục2/3/14/16; nguồn3.1, baseline `QD-2026-10-03-v1`. ✅ là chốt baseline, chưa xác nhận triển khai/chữ ký Mentor; BQ-042 vẫn mở. Không phát hiện mâu thuẫn buộc đổi requirement/contract. Không patient endpoint, không thêm quan hệ import liên module, không đổi engine tương tác.

| Quy tắc / trạng thái nguồn | AC / bước | Bằng chứng và giới hạn |
|---|---|---|
| Giữ dòng/clean-key/whitelist/eligibility theo 01 mới | AC1–AC3, AC7, AC8, AC15 / P1,P2 | Unit nguồn LF/CRLF/CR/NFC/NFD/đ/offset/trống/số tên/Met./SĐK toàn mẫu; không sửa ký tự hoặc nối dòng |
| QD-38 ✅, BQ-042 ❓; grammar mục7a | AC3–AC6, AC12–AC14 / P1,P3,P4 | Unit đơn/nồng độ/phối hợp/%/0/âm/O.5/l0/5OO/unsupported; nhóm hỏng không lấy phần đầu; hợp lệ độc lập vẫn giữ bên cạnh phần chưa hiểu; không quy đổi |
| QD-39 ✅: người dùng kiểm tra, không tự chọn/che bất định | AC9–AC14, AC17, AC21 / P4,P6,P7 | Signature/complete-link, thiếu strength không nối xung đột; count theo line, đại diện hỗ trợ, giữ mọi giá trị/nguồn; DTO không confidence/chọn thuốc |
| QD-36 ✅: giữ ID, ngừng chọn mới thuốc gỡ; freshness | AC17–AC19 / P6,P7 | Unit raw/null/ID cùng tên, active predicate, nguồn alias, limit/truncated, 2 caller/UoW, lỗi không fallback; DB thật P9 |
| QD-39 ✅: chính sách OCR lưu/xóa; task này chỉ bộ nhớ | AC21 / P2,P4,P7 | Guard I/O/log/writer; không endpoint/ảnh/OCR/LLM mới, chỉ query bound; không nghiệm thu cơ chế lưu/xóa OCR |
| QD-45 ✅: API/backlog chuẩn | AC20, AC22 / P7,P8 | Facade chung trả normalized document + candidate/nguồn, regression ingest/search/CRUD/architecture pass; không HTTP mới; integration search P10 |
| Raw/đáp án chủ dữ liệu xác nhận trong chat30/10 | AC10, AC11, AC23 / P5 | 4 cặp từ2 run, 4 document synthetic, thử5 ngưỡng; fixture provenance/expected cố định; regression U12 pass |

**Chọn ngưỡng:** người dùng xác nhận gom `Metformin 500mg` với `FMetformin 500mg`, gom `Candesarton Krka 16 mg` với `Candesartan Krka 16 mg`; giữ riêng `formin 500mg` với tên đầy đủ, giữ riêng dòng hoạt chất `Candesartan cilexetil` với tên `Candesartan Krka 16 mg`. Fixture lưu nguồn file/hash/run/image ID/line ID; selected text là chữ bao bì, không có định danh patient. Không dùng nhãn tên thuốc của workbook làm nhãn cụm.

| T | Cặp raw đúng /4 | Case synthetic đúng /4 | Ca sai |
|---|---|---|---|
| 0.80 | 3 | 4 | gom nhầm fragment formin theo đáp án đã xác nhận |
| 0.83 | 4 | 4 | không |
| **0.86** | **4** | **4** | **không trong tập kiểm** |
| 0.89 | 4 | 2 | mất gom typo synthetic |
| 0.92 | 4 | 2 | mất gom typo synthetic |

Chọn không gom sai trước, rồi tối đa ca đúng, hòa lấy T lớn hơn: **0.86**. Đại diện: eligible → hỗ trợ exact-key → tổng ratio → độ dài → line ID; thứ tự cụm count giảm/line ID đầu/key. Mảnh có dấu chấm chỉ nhập khi có neo eligible, tiền tố≥3 và≥65%, vẫn đạt T; substring không đủ. Bốn cặp chỉ là calibration nhỏ có nhãn, không là accuracy matching hoặc xác minh dược. 49 raw đã xử lý chỉ chứng minh bảo toàn nguồn/không nhân thành viên, chưa có nhãn đầy đủ cho mọi dòng.

Retrieval là literal containment bỏ dấu, không hứa fuzzy recall catalog cho mọi typo. Mọi khóa eligible của mọi cụm được query, đại diện trước; dedup chỉ trong lượt. 200 distinct ID cho mỗi khóa/nguồn, probe201, truncated riêng; không global cap/top-N UI. Alias chỉ qua liên kết hoạt chất sẵn có. Giao dịch đọc mới phản ánh commit theo DB, không snapshot/cache; consumer phải đối chiếu trạng thái ID khi xác nhận ở task tích hợp.

## 6. Phát sinh và phạm vi kế thừa

- Scope raw exit1 báo `backend/tests/integration/test_catalog_index.py`: file task cũ chưa commit, nằm trong03 nhưng bị loại khỏi stage implement. Hash trước/sau chứng minh không sửa trong lượt này. Workbook docs cũng có thay đổi cũ nhưng không bị sửa thêm. Không sửa/reset các file đó, gate hoặc scope để che trạng thái.
- Scope ghi CHƯA SỬA cho builder vì file vòng cũ chưa từng tracked; đã xóa trên filesystem nên không có git deletion. Audit xác nhận path không tồn tại và source không còn interface cũ.
- Snapshot `implement-refresh-protected-before.json` bảo vệ01/03/05/06/integration/workbook; audit cuối **6/6 giữ nguyên hash**. Chỉ source/test/migration trong bảng03 cùng04/evidence/scratch của task được sửa. Tất cả backend status path thuộc plan; delta implement không có path ngoài kế hoạch.
- Sandbox ban đầu chặn ghi evidence; retry require_escalated được auto-review cho phép. Không thay quyền/cấu hình máy; không có hành động bị auto-review từ chối còn chặn.
- Raw đã có ở datasets. Người dùng làm rõ raw chưa gom và gom thuộc task này; đã thực hiện thuật toán, tạo nhãn kiểm thử đề xuất và nhận xác nhận cả4. AC23 không còn Pending do thiếu nhãn, nhưng giới hạn tập nhỏ nêu ở mục5.
- Toàn suite/lint còn lỗi nền đã thực thi đối chiếu; không gọi toàn repo xanh. P9–P11 và review mới còn chưa làm. Không thay05/06 đã approved nhưng cũ, không dùng các kết luận lịch sử để nghiệm thu task mới.

## Bước tiếp theo

- Đã xong **8/8 bước implement**, chờ người duyệt đọc04/diff/evidence. Không còn câu hỏi nghiệp vụ chặn trong phạm vi này.
- Theo cổng duyệt AGENTS.md và wf-implement bước8, người duyệt tự chạy (agent không approve):

```powershell
& 'C:/Users/admin/AppData/Local/Python/pythoncore-3.14-64/python.exe' .agents/scripts/gate.py approve 4.12-ocr-text-normalization-catalog-index implement
```

- Sau duyệt, lượt riêng dùng wf-next/gate. 05 cũ còn approved nhưng input đã đổi: cần người dùng reopen test nếu gate yêu cầu. P9 viết lại integration cũ theo facade mới, reset/upgrade DB local/index/ACL/freshness/alias/error/budget; P10 integration search/full suite; P11 workbook/Bug/Test Report. Không tiếp tục stage test trong lượt này.
- Chưa commit/push. Đề xuất lưu12 file backend mới/sửa và artifact/evidence khi người dùng yêu cầu; không stage scratch. Integration/workbook cũ chỉ xử lý ở giai đoạn test; superproject chỉ bump SHA submodule đã push theo wf-git. Các gitlink api_contract/backend/docs/frontend/tests khác từ trước, không can thiệp.
- Cập nhật lần cuối: 2026-10-30, Codex.
