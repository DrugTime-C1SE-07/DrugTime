---
task: 4.09-mlkit-prototype
stage: plan
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 16:27 +0700
content_hash: sha256:6beeb0f93423efc9
inputs:
  01-requirement.md: sha256:8a9ccb35212f46c2
---

# 4.09 · Plan dataset dùng chung và đánh giá ML Kit

## 1. Giải pháp

Requirement approved lại ngày 2026-10-29, AC1–AC13, gồm AC7/AC8 mới cho quyết định hướng từ pilot. Giữ prototype Android hiện có: ảnh tĩnh → ML Kit Latin → raw/status/timing → lưu nội bộ Android → export JSON. Không sửa frontend, dependency, camera/preprocessing hoặc normalization/matching sản phẩm trong đợt này. Công cụ máy tính đọc trực tiếp labels.xlsx và raw, xuất báo cáo trong datasets/. Work giữ hồ sơ duyệt/evidence.

```text
datasets/
  README.md
  labels.xlsx                         # chỉ đọc
  images/                             # chỉ đọc
  scripts/
    ocr_dataset.py
    import_android_runs.py
    evaluate_ocr.py
    test_ocr_dataset.py
    test_import_android_runs.py
    test_evaluate_ocr.py
  results/
    legacy-pilot/
      raw/                            # 6 run lịch sử nguyên byte
      provenance/                     # index cũ, nguồn, SHA-256
    pilot-001/
      raw/                            # runId.json
      run-map.csv                     # mapping xác minh nếu cần
      import-index.json
      per_image.csv
      summary.json
      report.md
    benchmark-protocol.example.json   # draft, không tự điền ngưỡng
```

### Nhập dữ liệu

- CLI import nhận --source <directory> hoặc --adb <path> --serial <serial>, và --output <session-directory>. Không tự chọn thiết bị, khởi động/dừng emulator, gỡ app hoặc chạy OCR lại.
- ADB dùng subprocess danh sách đối số, không shell. Chỉ đọc run-as vn.drugtime.drugtime_mobile files/ocr_runs. Đọc base64 rồi giải mã giữ nguyên byte, kiểm schemaVersion=1/runId/path trước khi ghi độc quyền raw/runId.json. Cùng ID cùng byte thì skip; khác byte báo conflict, không overwrite; lỗi JSON/đọc phải được báo.
- Đọc hash ảnh sandbox khi imagePath an toàn. So với SHA-256 ảnh dataset để ghi chứng cứ ánh xạ riêng trong import-index. Không sửa imageId/rawText/metadata. Hash trùng nhiều ảnh => ambiguous; không đoán ảnh bằng tên thuốc trong raw.
- Sao chép 6 raw cũ cùng hai index cũ vào legacy-pilot, ghi hash và nguồn, giữ bản work/ để link/evidence cũ còn đúng. Không gộp legacy vào pilot mới mặc định. Screenshot không thay JSON thật, không dựng raw/timing/metadata từ màn hình.
- Driver Flutter hiện ghi OCR_RESULTS_DIR/runs, giữ tương thích: xuất trung gian rồi import --source vào raw/. Android không ghi trực tiếp vào D:\DrugTime.

### Đọc và ánh xạ

- ocr_dataset.py dùng standard library zipfile/ElementTree đọc XLSX chỉ đọc, hỗ trợ shared/inline strings, sheet relationships, header lệch hàng/cột (hiện B2:E2). Tìm duy nhất sheet chứa image_id,relative_path,drug_name,strength; sheet/header mơ hồ hoặc công thức nhãn báo lỗi, không lấy cache làm đáp án.
- Kiểm ID trùng, nhãn thiếu, ảnh thiếu, path tuyệt đối hoặc thoát dataset qua .. hoặc symlink; ghi row number/nguyên nhân. Không sửa workbook/ảnh, không đưa nhãn vào nhận diện.
- Ghép imageId đúng image_id. ID khác kể cả có đuôi chỉ nhận qua sidecar run-map.csv có run_id,image_id,verified_by,reason và chứng cứ; không suy từ filename UUID/raw. Không rõ => unmapped.
- Chọn run sớm nhất createdAt có timezone hợp lệ rồi runId cho mỗi ảnh/thiết bị. Device key gồm platform/model/OS/deviceKind; không gộp emulator và điện thoại. Run lỗi/no_text sớm vẫn được chọn. Schema/timestamp/meta hỏng => invalid_run; giữ và báo mọi run thừa/không chọn.

### Chấm và báo cáo

- Tên: NFC/casefold/thu gọn whitespace; exact_name khi đủ cụm đúng thứ tự và ranh giới từ. Không bỏ dấu, fuzzy, sửa ký tự hoặc dùng nhãn ghép raw.
- Sau exact, Counter token đủ số lần xuất hiện nhưng không thành cụm => tokens_present_noncontiguous; có một phần => partial_name; không token đúng => name_not_found. No_text/input_error/engine_error/not_run/unmapped/invalid_run tách riêng. Token phụ không được nâng thành exact hay matching thành công.
- Screenshot Decolgen có từ Decolgen và FORTE tách xa chỉ là bối cảnh; chấm sau lấy JSON/ảnh đúng, không coi UUID hiển thị là OCR khi chưa kiểm payload.
- Tử số exact_name; mẫu số ảnh nhãn tên hợp lệ có run được chọn hợp lệ, bao gồm no_text và engine/input_error. Coverage = đã chạy hợp lệ/tổng ảnh nhãn tên hợp lệ. Công bố tổng hàng và invalid_label/invalid_run/unmapped/not_run để không che thiếu dữ liệu. Điểm theo thiết bị và nhóm sản phẩm/box/blister từ path; không tự suy góc/ánh sáng, không cộng thiết bị thành điểm ảnh thiếu định nghĩa. Mẫu số 0 => null/N/A.
- Strength phụ: trống => unscored; nhãn đơn số + đơn vị chấm occurrence, cho phép khoảng trắng số/đơn vị (500mg = 500 mg) và ranh giới số để không khớp 1500 mg. Đây không chứng minh đúng thành phần/sản phẩm. Nhãn ghép nhiều thành phần/hàm lượng => requires_component_protocol, chưa chấm; không lấy một số mg để đạt cả chuỗi.
- Timing là số hữu hạn >=0, không bool, status text/no_text; median/p95 nearest-rank/n theo thiết bị. Lỗi/timing thiếu không thay 0; không suy cold/warm từ latency.
- per_image.csv có nhãn kỳ vọng, strength, imageId/runId/raw path/device/selected/status/classification/timing/lỗi. Run thừa/unmapped hiện riêng, không cộng điểm ảnh. CSV UTF-8 BOM, bảo vệ formula injection cho =,+,-,@ ở dữ liệu; raw JSON giữ nguyên.
- summary.json có counts/coverage/scores/groups/timing/errors/rules/selection/decision; report.md ghi tử/mẫu, giới hạn và mục chưa có. Không có raw vẫn xuất đủ not_run cho mọi ảnh nhãn. Raw ghi độc quyền; báo cáo generated được cập nhật. Không tạo workbook báo cáo mới.

### Quyết định hướng từ pilot

Người dùng đã chọn GO ngày 2026-10-29. Ghi riêng decision.json/decision.md với decision=go, decision_type=engineering_pilot, decided_by là người dùng xác nhận trong chat (không giả chữ ký reviewer), decided_at ghi ngày xác nhận, rationale, dataset_version/hash, report/raw references và limitations. Số liệu cũ trước sửa nhãn có thể dẫn làm lịch sử, không thay kết quả chấm theo snapshot chốt. Không tự sửa decided_at sang thời điểm chạy script.

Decision JSON phải nói rõ không phải automatic benchmark pass hoặc top-1/top-N matching. partial/token rời chưa có kết quả matching; name_not_found phải đối chiếu chứ không tự quy mọi lỗi cho nhãn. Native share/lifecycle còn thiếu phải ghi thật. summary.json của CLI vẫn not_decided ở mode pilot, không sửa evaluator hoặc payload để làm GO.

T8 bổ sung (kiểm artifact ở work/scratch, không viết test sản phẩm mới): đối chiếu decision JSON/Markdown với xác nhận người dùng, số liệu/hash/report hiện hành, phân biệt manual engineering go với automated not_decided, có giới hạn/missing rõ. Phủ AC7/AC8/AC13.

### Benchmark chính thức có ngưỡng (nếu nhóm thực hiện)

Pilot không cần ngưỡng, decision luôn not_decided. Benchmark dùng --mode benchmark --protocol <json> --manifest <json>. Manifest snapshot nhãn/hash ảnh thực/verification; protocol version/status=frozen/frozenAt, dataset hash, model/OS/config, điều kiện, số ảnh tối thiểu, repetitions cold/warm và ngưỡng exact tên/latency. Điều kiện/phase ghi thực tế ở sidecar, không sửa raw hoặc suy từ timing.

Hash phải tính byte thực, không chỉ so chuỗi khai báo. Thiếu verification/coverage/config/thiết bị/lần lặp, hash sai hoặc run trước frozenAt => pending. Khi đủ mới áp ngưỡng chốt trước; strength phụ không tự thành gate. Kế thừa ý tưởng earliest-createdAt/runId của evaluator cũ, bỏ tiêu chí hoạt chất. Q1 chỉ chặn benchmark chính thức có ngưỡng, không chặn bàn giao pilot hoặc quyết định hướng của người phụ trách.

## 2. Khảo sát

| Nguồn đã đọc | Kết luận |
|---|---|
| 01-requirement.md approved lại 2026-10-29 | AC1–AC13, tên chính/hàm lượng phụ, datasets dùng chung |
| dataset-evaluation-change.md; screenshot/ảnh người dùng | Raw nguyên vẹn, không dựng JSON từ màn hình |
| datasets/labels.xlsx, images; evidence/requirement-dataset-source.log | Baseline cũ 17 ảnh; hiện pilot-002 có 49 ảnh/49 nhãn, vẫn header B2:E2; phải dùng snapshot 4.08 mới và không mặc nhiên verified/đại diện |
| work/4.09-mlkit-prototype/scripts/evaluate_ocr.py, test_evaluate_ocr.py, benchmark-protocol.md | Cũ chấm tên/hoạt chất, protocol draft chặn mọi lần chạy; giữ lịch sử, công cụ mới theo AC hiện tại |
| work/4.09-mlkit-prototype/results/runs, README.md, hai index | 6 raw lịch sử, ID cũ chưa tự nối với ảnh mới |
| frontend/mobile/lib/features/ocr_prototype/ocr_models.dart, ocr_store.dart, ocr_native.dart, ocr_controller.dart; test/features/ocr_prototype/native_export_driver.dart | schemaVersion=1, imagePath trong app, driver dùng OCR_RESULTS_DIR/runs; không cần sửa app |
| 04-impl-notes.md, 05-test-report.md | Native smoke emulator/evidence cũ, manual/benchmark chưa đủ; không báo pass mới |
| Proposal_v5.docx §6.2/6.3, FR01, §8.1/lộ trình; đọc lại tại evidence/plan-dataset-source.log | On-device, manual confirmation, không OCR đơn thuốc |
| Bảng Sprint mới trong chat/requirement | 4.12 normalization, 4.13 matching, 4.17 accuracy toàn luồng; không dùng backlog repo cũ |
| .agents/scripts/scope.py; nhánh Git hiện tại | Hỗ trợ cột superproject; nhánh hiện tại phù hợp yêu cầu người dùng |

### Quyết định nghiệp vụ áp dụng

| Quy tắc/nguồn | AC | Bước | Test |
|---|---|---|---|
| Requirement Android-only, prototype độc lập, lỗi/lifecycle | AC1–AC4, AC6, AC8 | P1, P7 | T1, N1–N4 |
| Proposal FR01/§8.1 on-device, §6.3 không đơn thuốc, xác nhận thủ công | AC1, AC6 | P1, P7 | T1, N1, N4 |
| Requirement raw nguyên vẹn/dùng chung/lịch sử | AC2, AC6, AC11, AC13 | P2, P3, P6 | T2, T3, N2 |
| Requirement XLSX hiện tại, báo lỗi/coverage | AC5, AC9, AC13 | P2, P4, P5 | T2, T4, T6 |
| Requirement tên exact/token phụ, strength độc lập | AC5, AC10 | P4, P5 | T4, T6 |
| Requirement chọn run cố định, tách thiết bị | AC5, AC12 | P4, P5 | T5, T6 |
| Requirement AC7/AC8 mới: quyết định hướng của người phụ trách độc lập với quyết định tự động; benchmark có ngưỡng vẫn frozen | AC7, AC8 | P5, P6, P7 | T7, T8, N5 |

## 3. File sẽ thay đổi

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| superproject | datasets/README.md | sửa | Dẫn bản dữ liệu 4.08, pilot-002 và quyết định hướng |
| superproject | datasets/results/pilot-002/per_image.csv | tái tạo | Chấm raw đã có theo nhãn 4.08 chốt, giữ missing/errors |
| superproject | datasets/results/pilot-002/summary.json | tái tạo | Số liệu/hash; pilot tự động vẫn not_decided |
| superproject | datasets/results/pilot-002/report.md | tái tạo | Báo cáo đo lường cùng giới hạn |
| superproject | datasets/results/pilot-002/decision.json | thêm | GO kỹ thuật do người phụ trách xác nhận, chứng cứ và giới hạn |
| superproject | datasets/results/pilot-002/decision.md | thêm | Kết luận đọc được và bàn giao 4.11–4.14/4.17 |

6 file dữ liệu/hướng dẫn trong superproject. labels.xlsx/images/annotations/manifest chỉ đọc ở 4.09; nếu cần sửa nhãn làm trong scope 4.08 rồi chấm lại. Scripts/import/ML Kit/frontend giữ nguyên: capability đã có, không cần xây lại hoặc mở phạm vi refactor. Raw/provenance/mapping chỉ đọc, không xóa legacy hoặc pilot-001. Artifact/evidence/taskcase trong work, file tổng docs chỉ do wf-testcase ở test stage như người dùng đã cho phép.

## 4. Checklist

- [ ] P1 [work] Kiểm Git/hash và kế thừa 04/evidence, đối chiếu snapshot 4.08 — AC: AC1–AC4, AC6, AC8, AC11 — xong khi: biết code/capability có sẵn, không làm lại prototype; giữ nguyên raw/ảnh và thay đổi riêng.
- [ ] P2 [work] Đọc 49 raw, mapping/provenance và labels/annotations/manifest 4.08 đã chốt; kiểm metadata/coverage — AC: AC2, AC5, AC9, AC10, AC11, AC12 — xong khi: từng raw nối đúng ảnh, duplicate/metadata thiếu/nhãn chưa verified báo rõ; không đoán tên hoặc sửa raw.
- [ ] P3 [superproject/work] Chấm lại raw pilot-002 bằng công cụ hiện có sau khi nhãn 4.08 được chốt; đối chiếu tử/mẫu/groups/timing — file: datasets/results/pilot-002/per_image.csv, summary.json, report.md — AC: AC5, AC9, AC10, AC12, AC13 — xong khi: log tái hiện, hash nguồn trước/sau không đổi, missing/error không bị che. Không nâng partial/token rời thành exact.
- [ ] P4 [work] Đối chiếu native/fake/unit/manual còn thiếu theo AC1–AC4/AC6 và tổng hợp coverage thực tế — AC: AC1–AC4, AC6, AC8 — xong khi: có evidence cho phần đã kiểm, phần chưa kiểm ghi pending, không dùng GO để miễn kiểm. Nếu phát hiện bug code ngoài scope, báo và reopen plan trước sửa.
- [ ] P5 [superproject] Lưu quyết định GO do người phụ trách xác nhận trong chat và giới hạn pilot — file: datasets/results/pilot-002/decision.json, decision.md — AC: AC7, AC8 — xong khi: decision_type=engineering_pilot, người/ngày/lý do/chứng cứ/report hash rõ; không đổi summary tự động thành go hoặc tuyên bố matching/benchmark đạt ngưỡng.
- [ ] P6 [superproject/work] Cập nhật README/hướng dẫn, bàn giao dữ liệu cho task sau và ghi 04 — file: datasets/README.md, work/4.09-mlkit-prototype — AC: AC2, AC6–AC8, AC11, AC13 — xong khi: tên/link/phiên bản đúng, không còn yêu cầu làm nghiên cứu engine cũ, không tự commit/push hoặc đóng task thiếu manual/review.
- [ ] P7 [work] Chạy các kiểm tra phù hợp, scope/hash và chốt impl-notes — AC: AC1–AC13 — xong khi: dẫn đúng lần chạy, không lặp toàn bộ suite/build/OCR nếu không có thay đổi hoặc nghi vấn mới; đủ để người duyệt rà 04 theo plan mới. Test stage sau cập nhật testcase/report; không chuyển giai đoạn cùng lượt.

P2/P3/P5 chốt dữ liệu cuối sau P2–P4 của 4.08. Không tuyên bố đã verified toàn bộ nhãn trước khi bước xác minh dữ liệu hoàn tất.

## 5. Test

| Test và nơi chứa | AC |
|---|---|
| T1 kế thừa mobile/test/features/ocr_prototype/{ocr_controller_test.dart,ocr_screen_test.dart}; không viết lại đợt này | AC1–AC4, AC6 |
| T2 datasets/scripts/test_ocr_dataset.py: shared/inline strings, header B2, sheet/header mơ hồ, duplicate ID, nhãn/ảnh thiếu, path escape/symlink, formula label, JSON/schema hỏng | AC2, AC5, AC9, AC11, AC13 |
| T3 datasets/scripts/test_import_android_runs.py: byte/newline/Unicode/hash, trùng cùng/khác payload, invalid ID/path, mock ADB base64 lỗi, hash ambiguous, không sửa metadata | AC2, AC6, AC11, AC13 |
| T4 datasets/scripts/test_ocr_dataset.py: exact newline/case/NFC/boundary, ký tự sai, token thiếu/tách/đảo/lặp; strength 500mg/500 mg/1500 mg/trống/nhiều thành phần | AC5, AC10 |
| T5 datasets/scripts/test_ocr_dataset.py: earliest lỗi không thay run đẹp, timezone/tie/meta, OS/deviceKind tách, duplicate conflict; timing NaN/bool/negative/zero/missing; mẫu số 0 | AC5, AC9, AC12 |
| T6 datasets/scripts/test_evaluate_ocr.py: CLI temporary XLSX/raw, not_run/error/coverage/groups, selected/extras/unmapped, CSV escaping, hash source không đổi | AC5, AC9, AC12, AC13 |
| T7 datasets/scripts/test_evaluate_ocr.py: pilot not_decided; protocol draft/hash thật sai/run trước freeze/config/coverage/repetitions thiếu => pending; fixture đủ thì go/no-go đúng ngưỡng | AC7, AC8 |

Fixture giả chỉ ở temporary directory của test, không vào raw thật. Dataset thực để kiểm CLI/coverage, không khẳng định accuracy theo mong muốn. Không có service-integration hoặc endpoint sức khỏe mới, không reset DB.

| Native/manual | Nội dung | AC |
|---|---|---|
| N1 | ML Kit thật text/blank/hỏng/offline, model/OS/SDK/ảnh rõ | AC1, AC3, AC6 |
| N2 | Share đọc ngoài app, import datasets, restart giữ run | AC2, AC11, AC13 |
| N3 | Cancel/double tap/back/background/process death/retry | AC3, AC4 |
| N4 | Adapter/offline không cloud/backend/nhãn vào OCR/mutation thuốc | AC6 |
| N5 | Review quyết định hướng pilot: người/ngày/lý do/số liệu/giới hạn; nếu làm benchmark có ngưỡng thì kiểm frozen riêng | AC5, AC7, AC8 |

Test stage tiếp tục mục còn thiếu và testcase Excel theo workflow. Evidence cũ ghi nguồn, không báo pass mới; manual chưa chạy giữ Pending.

Lệnh dự kiến từ D:\DrugTime:

```powershell
python -m unittest discover -s datasets/scripts -p "test_*.py"
python datasets/scripts/import_android_runs.py --source work/4.09-mlkit-prototype/results/runs --output datasets/results/legacy-pilot
python datasets/scripts/import_android_runs.py --adb "C:/Users/QuangBao/AppData/Local/Android/sdk/platform-tools/adb.exe" --serial emulator-5554 --output datasets/results/pilot-001
python datasets/scripts/evaluate_ocr.py --labels datasets/labels.xlsx --runs datasets/results/pilot-002/raw --output datasets/results/pilot-002
```

Nếu run-as không hỗ trợ, dùng native export và --source; không root/đổi quyền. Mỗi đợt output riêng, report generated cập nhật còn raw không overwrite. Log vào evidence đúng giai đoạn.

## 6. Migration

Không API/DB/schema/health endpoint mới; không cần wf-db-migration/wf-health-endpoint. File migration chỉ copy/SHA-256 và giữ nguồn; không xóa raw cũ hoặc đổi nhãn/ảnh.

## 7. Nhánh git

| Repo | Nhánh hiện tại |
|---|---|
| superproject | feat/datasets-ocr |
| frontend | feat/mlkit-prototype-measurement |

Giữ hai nhánh theo yêu cầu người dùng; truyền task ID 4.09-mlkit-prototype rõ cho gate/scope. Theo wf-git: không tự đổi nhánh/commit/push/stage con trỏ frontend, không stash/reset thay đổi riêng.

## 8. Rủi ro

- Nhãn nhập tay chưa chắc verified; không suy đáp án từ OCR; giữ hash nguồn.
- Token tách xa không phải exact hoặc bằng chứng matching thành công.
- ID sai ghép nhầm; mapping cần chứng cứ; legacy tách biệt.
- Hiện 49 ảnh có nhiều tên sản phẩm/điều kiện, không mặc nhiên đại diện; emulator không thay điện thoại; quyết định hướng từ pilot không chứng minh đạt ngưỡng hay matching đúng.
- Hàm lượng nhiều thành phần chưa có protocol thì chưa chấm, không tự chọn số mg.
- Metadata nhập tay có thể sai, ghi provenance riêng thay vì sửa payload; phase ghi thực tế; hash benchmark tính byte thực.

## 9. Câu hỏi mở

Không có câu hỏi chặn quyết định hướng: người dùng đã chọn GO trong chat 2026-10-29. Q1 chỉ dành cho benchmark có ngưỡng nếu nhóm thực hiện; không chặn việc ghi quyết định này. Native manual, xác minh nhãn và review vẫn phải có bằng chứng; không tự miễn hoặc đổi Pending thành Pass.

## 10. Phát sinh

- Requirement mới đã approved, plan này tách GO kỹ thuật khỏi summary tự động/benchmark ngưỡng, không thay cách chấm để tạo go giả. 04 approved cũ sẽ hết hiệu lực theo đầu vào mới; sau duyệt plan phải rà soát/đồng bộ 04, không tự sửa metadata hoặc coi việc duyệt cũ vẫn đủ.
- Không sửa requirement, code/data hoặc chạy OCR/test/build trong lượt plan. Kế thừa 41 Python/13 Flutter/5 host đã kiểm ở lần trước, không gọi đó là test vừa chạy.
- Scope ngoài work gồm dataset/raw mới của người dùng và code/file tổng/baseline đã có; ghi đúng log, không xóa hoặc xin lại quyền giữ những thay đổi người dùng đã cho phép.

## Bước tiếp theo

- Chờ duyệt: python .agents/scripts/gate.py approve 4.09-mlkit-prototype plan
- Sau duyệt dùng wf-implement đồng bộ 04 theo P1–P7 mới, chốt số liệu/decision sau snapshot nhãn 4.08. Không xây lại prototype, không đợi nghiên cứu engine cũ hoặc matching 4.13.
- Cập nhật: 2026-10-29, Codex.

## Tự kiểm plan

- Plan-only: không sửa code/datasets/raw/requirement hoặc chạy test/build/OCR trong lượt này.
- Gate và scope tại evidence/plan-decision-gate.log, evidence/plan-decision-scope.log; bảng truy vết phủ AC1–AC13. Scope toàn repo có baseline đã được cho giữ, không báo sạch giả.
- Kết quả thực: gate plan OK; scope báo “CHẶN: 226 file ngoài phạm vi”, gồm dataset/code/file tổng/baseline đã có và được yêu cầu giữ từ trước, không có thay đổi sản phẩm do lượt plan. Không xin lại quyền giữ hoặc sửa chúng để scope sạch. Parser kiểm được 6 dòng phạm vi, không có frontend/scripts; evidence/plan-decision-check.log.
- 04-impl-notes đã approved nhưng approval cũ do đầu vào đổi. Sau duyệt plan, người dùng cần chạy `python .agents/scripts/gate.py reopen 4.09-mlkit-prototype implement` trước khi agent đồng bộ 04. Không tự sửa artifact approved hoặc approval metadata.
