---
task: 4.09-mlkit-prototype
stage: implement
owner: Bao Nguyen
started_at: 2026-10-27
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 17:11 +0700
content_hash: sha256:f9db3c1a907e8565
inputs:
  01-requirement.md: sha256:8a9ccb35212f46c2
  03-plan.md: sha256:6beeb0f93423efc9
---
# 4.09 · Implement số liệu và quyết định hướng ML Kit từ pilot

## Cập nhật mới nhất · Hướng dẫn không phụ thuộc máy cá nhân

- Người dùng báo README dùng chung có đường dẫn máy cá nhân và đã reopen implement. Gate OK: `evidence/implement-portable-readme-gate.log`. Phạm vi sửa đúng `datasets/README.md` trong plan đã duyệt; không sửa requirement/plan hoặc hồ sơ approved khác.
- Đã sửa đủ 3 vị trí: thư mục gốc repo mô tả theo cấu trúc, ADB gọi qua `PATH` bằng `--adb adb`, thư mục JSON xuất dùng `--source ./ocr-export`. Thêm cách kiểm `adb devices`, thay serial phù hợp và vị trí folder export tương đối.
- Không đổi raw, nhãn, ảnh, script, số liệu/hash quyết định hoặc code frontend. Không chạy lại OCR/Flutter/unit suite vì chỉ sửa hướng dẫn; không yêu cầu người dùng test lại ảnh.
- Kiểm văn bản: không còn đường dẫn Windows tuyệt đối/tên tài khoản riêng trong README; kiểm parser `--help` và đối chiếu 225 hash nguồn/kết quả dataset ngoài README không đổi. Output: `evidence/implement-portable-readme-verification.log`; baseline `evidence/implement-portable-readme-baseline.log`.
- Scope exit 1: “CHẶN: 224 file ngoài phạm vi”, `evidence/implement-portable-readme-scope.log`; là baseline/thay đổi task liên quan đã có và đã được yêu cầu giữ. Lượt này chỉ sửa README trong plan và hồ sơ work; không xóa baseline để báo scope sạch.
- Không commit, push, stage, bump con trỏ hoặc mở PR theo chỉ dẫn người dùng. Phần triển khai/số liệu bên dưới là hồ sơ các lượt trước, không nhận là test vừa chạy lại.


Ngày: 2026-10-29. Requirement/plan mới đã approved, implement đã reopen và gate OK. Giữ nguyên ML Kit/frontend/evaluator/raw; chỉ chốt dữ liệu/report/decision theo phạm vi mới. Không đòi nghiên cứu OCR cũ hoặc matching hoàn tất mới được bàn giao 4.09.

## Tiến độ theo plan mới

| Bước | Trạng thái | Bằng chứng |
|---|---|---|
| P1 baseline/kế thừa | Xong | Kiểm nhánh và dữ liệu; giữ 04/evidence lịch sử phía dưới; code không đổi |
| P2 raw/nhãn/hash/coverage | Xong cho pilot, hạn chế manual rõ | 49 raw và 49 nhãn nối được, 0 data error; nhãn theo v1 4.08, review AI ghi trung thực; native chưa kiểm mới giữ Pending |
| P3 chấm lại | Xong | evidence/implement-pilot002-final-score.log; per_image.csv, summary.json, report.md; không OCR lại |
| P4 coverage native/unit/manual | Xong đối chiếu, native manual Pending | Có raw native emulator; unit/fake và host evidence từ vòng trước; chưa có bằng chứng mới native share/gallery/offline/lifecycle trên thiết bị bắt buộc, không dùng GO để miễn kiểm |
| P5 quyết định GO | Xong | decision.json/decision.md; evidence/implement-pilot-decision-verification.log; decided_at giữ ngày xác nhận 2026-10-29 |
| P6 README/bàn giao | Xong chuẩn bị | README dẫn manifest/annotations và pilot-002/decision; dữ liệu local, review/publish Pending |
| P7 kiểm cuối/04 | Xong kiểm công cụ và toàn vẹn | 41 unit pass (1.482s), evidence/implement-v1-final-unit.log; kiểm snapshot/report/raw/decision tại work/4.08-ocr-capture-evaluation/evidence/implement-v1-integrity.log; scope có baseline đã cho giữ |

## File và số liệu hiện hành

- Đúng 6 file phạm vi plan: datasets/README.md, results/pilot-002/{per_image.csv,summary.json,report.md,decision.json,decision.md}. Labels/annotations/manifest đổi trong phạm vi task 4.08, ở 4.09 chỉ đọc. Không sửa code, scripts, raw/provenance/mapping hoặc app Android.
- Theo nhãn đã rà từ ảnh: exact 27/49 (55,1%), partial 5, đủ token rời 2, name_not_found 14, no_text 1; coverage 49/49, data errors=0. Không cộng partial/token rời thành matching đúng và không quy tất cả name_not_found cho lỗi nhãn. Median 2615 ms/p95 5267 ms trên emulator; không đại diện điện thoại thật.
- Bộ dữ liệu v1: 588a56f54a5155250ce6c5fc633b60d05351f20561d46ba49ed482eab1b77e7f. Snapshot nhãn/ảnh của report khớp manifest; các nhãn sau hiệu chỉnh thay điểm cũ 23/49 nhưng không thay raw hoặc nới phép chấm.
- GO do người phụ trách xác nhận trong chat; decision_type=engineering_pilot, ngày 2026-10-29, có nguồn xác nhận/lý do/hashreport/hashraw/limitations và task nhận bàn giao. Không giả chữ ký reviewer; automatic_pilot_decision vẫn not_decided. Không đạt benchmark đặt trước hoặc top-1/top-N matching bằng quyết định này.
- AC7/AC8 mới: quyết định hướng và bằng chứng số liệu được ghi rõ, không đóng task thiếu kiểm chứng/review/PR. CLI mode benchmark vẫn nguyên yêu cầu frozen nếu nhóm muốn làm phép đo đó.

## Lệnh và bằng chứng trong lượt này

- `python datasets/scripts/evaluate_ocr.py --labels datasets/labels.xlsx --runs datasets/results/pilot-002/raw --output datasets/results/pilot-002`: thực sự chạy, exit0, 49/49 và 0 data error; implement-pilot002-final-score.log.
- `python work/4.09-mlkit-prototype/scratch/finalize_pilot_decision.py`: tạo quyết định từ xác nhận đã có, không tạo raw; implement-pilot-decision-verification.log.
- `python -m unittest discover -s datasets/scripts -p "test_*.py" -v`: 41 pass, 0 fail, 1.482s; implement-v1-final-unit.log. Test snapshot tamper/CLI và selection/strength/no_text/duplicate/phiên bản vẫn đạt. Đây là test công cụ/fixture, không 41 ảnh thật mới.
- Verify v1 của 4.08: 49 raw hashes khớp import-index và quyết định, 49 ảnh không đổi, report/snapshot/hash quyết định khớp, style/ô workbook không liên quan không đổi. T8 decision proof đạt: manual GO và automatic not_decided tồn tại riêng, ngày đúng xác nhận, có giới hạn/missing.
- Không chạy lại 13 Flutter/5 host hoặc native smoke vì không đổi code và không có nghi vấn mới; các bằng chứng cũ giữ đúng nguồn. Không báo những test đó là lần chạy mới. Native manual còn thiếu đã ghi rõ; không cài/gỡ app hoặc thay emulator.

## Phát sinh/phạm vi

- Scope implement báo “CHẶN: 224 file ngoài phạm vi”, evidence/implement-decision-scope.log. Gồm baseline/ảnh/raw/code/file tổng đã có, cộng nhãn/annotations/manifest được triển khai theo plan 4.08 cũng approved trong lượt này. Không có thay đổi sản phẩm ngoài hai plan; không xóa hoặc xin lại quyền giữ dữ liệu đã được người dùng cho phép, không báo scope toàn repo sạch.
- Rà nhãn là Codex visual inspection, không giả thành human sign-off độc lập; metadata/sources thiếu vẫn unknown. Khi nhãn/report đổi lần nữa phải cập nhật hash/chứng cứ trong decision, không dùng decision gắn snapshot cũ.
- Chưa có commit/push hoặc review/PR approval. Không coi quyết định GO miễn Definition of Done hoặc các kiểm native còn thiếu.

## Bước tiếp theo

- Chờ duyệt implement: python .agents/scripts/gate.py approve 4.09-mlkit-prototype implement
- Sau duyệt, chỉ đối chiếu thay đổi README với bằng chứng có sẵn khi cập nhật trạng thái test/review; không quét lại ảnh, không bổ sung bộ manual hoặc chạy lại unit/Flutter chỉ vì sửa đường dẫn hướng dẫn.
- Giữ nguyên kết luận GO và giới hạn prototype đã được chấp nhận trong báo cáo test. Không sửa các artifact approved khác hoặc tự coi approval cũ vẫn hợp lệ sau thay đổi đầu vào; gate quyết định trạng thái.
- Giữ toàn bộ kết quả cục bộ theo yêu cầu, không commit/push hoặc mở PR; giữ nguyên hai nhánh hiện tại.
- Cập nhật: 2026-10-29, Codex.


## Lịch sử triển khai trước 2026-10-29


# 4.09 · Implement prototype OCR Android

## Vòng datasets · 2026-10-28 · hoàn tất implement theo plan mới

Requirement/plan cập nhật đã approved; gate implement OK. Áp dụng AC1–AC13 và 7 bước mới trong plan; phần bên dưới tiêu đề này giữ lịch sử prototype trước đó. Owner theo Git: Bao Nguyen. Không sửa ảnh, workbook hoặc frontend.

| Bước mới | Trạng thái | Bằng chứng |
|---|---|---|
| P1 baseline | xong | evidence/implement-dataset-gate.log; implement-dataset-baseline.json; hash cuối khớp |
| P2 reader/validation/mapping | xong | implement-dataset-final-unit.log: header B2/shared/inline, duplicate/formula/thiếu ảnh/nhãn, path escape, JSON/mapping |
| P3 import/legacy | xong | implement-dataset-legacy.log: 6 raw cũ; implement-dataset-adb-import.log: 4 raw mới, 5 legacy trên app bỏ trùng |
| P4 scoring/selection/timing | xong | implement-dataset-final-unit.log: exact/token/strength, earliest, device/timing |
| P5 CLI/report/benchmark gating | xong | implement-dataset-final-unit.log, implement-dataset-final-pilot.log; pilot not_decided |
| P6 README/protocol draft | xong | datasets/README.md; datasets/results/benchmark-protocol.example.json draft/null |
| P7 kiểm cuối/pilot | xong cho đợt công cụ | 41 unit pass; implement-dataset-final-verification.log và implement-dataset-scope.log; manual/benchmark chính thức vẫn pending |

### File, hành vi và kết quả hiện tại

- 7 file cố định theo plan: datasets/README.md, scripts/ocr_dataset.py, import_android_runs.py, evaluate_ocr.py và 3 file test. Kết quả trong datasets/results/{legacy-pilot,pilot-001}, protocol template draft. Không sửa frontend, workbook hoặc ảnh.
- AC2/AC6/AC11/AC13: JSON nguyên byte/hash, từ chối conflict, provenance riêng. AC5/AC9/AC10/AC12: XLSX hiện tại, exact/token phụ, strength nhiều thành phần chưa chấm, earliest không chọn run đẹp, lỗi/coverage hiện đủ. AC7/AC8: pilot not_decided; benchmark thiếu frozen/hash/verified/config/coverage => pending; không gán ngưỡng.
- Pilot mới 4 raw: 3 raw khớp duy nhất 2 ảnh qua hash, 1 run chưa có ảnh khớp (c6da86d5-1496-4f70-9fb2-720ae357221c) giữ unmapped. Exact 1/2 ảnh đã chạy, coverage 2/17; 15 ảnh not_run. Một ảnh vỉ đủ token tách xa không tính exact; run lặp vẫn giữ trong CSV, chọn bf2e373a… sớm hơn theo timestamp.
- Run screenshot 71e2ac39… thực tế khớp decolgen_forte_blister_002, không phải ảnh hộp gửi kèm. Run hộp decolgen_forte_box_001 là f5ce68db… Chứng cứ SHA-256 trong run-map.csv/import-index.json và datasets/results/pilot-001/notes.md. Không sửa imageId=1 trong raw.
- ADB quan sát lúc nhập: Android sdk_gphone16k_x86_64/17/emulator. Metadata gốc có osVersion=d/SDK=dd vẫn giữ nguyên, chưa đủ dùng benchmark chính thức. Quan sát lúc nhập không chứng minh metadata thời điểm quét hoàn toàn chính xác.

### Kiểm chứng mới, giới hạn và phạm vi

- `python -m unittest discover -s datasets/scripts -p "test_*.py" -v`: lần đầu sandbox lỗi quyền TEMP (implement-dataset-unit.log); chạy ngoài sandbox 39 pass (implement-dataset-unit-native.log). Sau thêm kiểm raw hash/manifest: **41 pass, 0 fail**, 0.968s (implement-dataset-final-unit.log). Fixture test không phải 41 ảnh OCR thật.
- Lệnh import source work/results/runs và ADB emulator-5554 thực sự chạy; logs legacy/ad-import nêu ở bảng (tên đầy đủ implement-dataset-adb-import.log). Không chạy OCR lại hoặc thay app.
- CLI evaluate theo README đã xuất CSV/JSON/Markdown, có 1 data error unmapped nên trả mã 1 theo thiết kế (implement-dataset-final-pilot.log). Đây là thiếu dữ liệu, không phải unit test fail. Chưa kết luận go/no-go.
- Hash trước/sau: 17 ảnh và labels.xlsx không đổi; 6 legacy JSON khớp byte nguồn; 4 raw mới khớp import-index; frontend git status sạch (implement-dataset-final-verification.log). Không đổi nhánh/pointer/commit/push.
- Ruff không có trong Python hiện tại; không cài dependency hoặc báo lint pass. Không có lệnh lint riêng cho Python công cụ superproject trong AGENTS; tests import/compile các module. Không chạy lại Flutter do không sửa frontend.
- Scope báo nguyên văn “CHẶN: 21 file ngoài phạm vi”: .gitignore, api_contract/README.md, api_contract/openapi.json, 17 ảnh và labels.xlsx có sẵn; log implement-dataset-scope.log. README nay thuộc plan nên giảm từ 22 baseline còn 21. Người dùng đã cho giữ/tạo/điền các file nền này; vòng này không sửa chúng, không xin lại quyền giữ hoặc mở scope sửa nhãn/ảnh. Không có thay đổi mới ngoài plan, không báo scope toàn repo sạch.
- Work raw cũ giữ để link/evidence lịch sử truy vết; bản dùng chung hiện ở datasets/. Raw chưa ánh xạ/metadata nhập thử phải đối chiếu, không đoán nhãn hoặc nới chấm.

### Bước tiếp theo của vòng datasets

Chờ duyệt implement: `python .agents/scripts/gate.py approve 4.09-mlkit-prototype implement`. Sau duyệt, lượt tiếp theo wf-test kiểm phần còn thiếu và testcase Excel; người thử tiếp tục 15 ảnh bằng đúng image_id, đối chiếu run unmapped và metadata thật. Q1/benchmark vẫn pending. Không tự chuyển giai đoạn; không commit/push. Các mục dưới là lịch sử prototype ngày 2026-10-27, không phải lần chạy mới của vòng datasets.

## 1. Tiến độ

Phạm vi mới theo chỉ dẫn trực tiếp của người dùng ngày 2026-10-27: **chỉ Android, không cần iOS**. 01 và 03 đã được duyệt lại cho Android; gate implement OK trong lượt tiếp tục này. Không có yêu cầu kiểm thử iOS trong scope mới. Đã gỡ toàn bộ thay đổi iOS do task tạo; `git diff -- mobile/ios` rỗng. Chưa đóng task hoặc kết luận go/no-go.

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong cho Android | Flutter 3.47.4/Dart 3.13.3; pub get thành công; minSdk 24; APK debug build thành công | evidence/implement-P1-pub.log; evidence/implement-android-only-build.log |
| P2 | xong code/unit | Gallery tĩnh, recover picker, validate ảnh, ML Kit Latin; fake phân biệt text/no_text/input_error/engine_error/cancel/unsupported | evidence/implement-android-only-tests.log |
| P3 | xong code/unit | Lưu ảnh nguyên byte và JSON UTF-8 riêng run; round trip raw, không overwrite, lỗi lưu/retry/export | evidence/implement-android-only-tests.log |
| P4 | xong code/unit | Khóa tác vụ, không thay run chưa lưu; dispose không notify; chờ engine trước close | evidence/implement-android-only-tests.log |
| P5 | xong code/widget | Entrypoint riêng, form metadata, raw/history, share JSON có origin; Android only, không mutation thuốc | evidence/implement-android-only-tests.log |
| P6 | xong công cụ/template | Evaluator và 13 unittest pass bằng fixture giả; protocol còn draft/Q1; chưa benchmark thật | evidence/implement-P6.log |
| P7 | xong tự động/native smoke trên máy ảo; manual/benchmark pending | Full suite 546 pass trong lượt tiếp tục; analyzer sạch; APK prototype build và mở được; 2 ca native offline pass trên AVD Android 17; đã nhận 1 raw JSON thật | evidence/implement-resume-final-frontend.log; evidence/implement-resume-final-analyze.log; evidence/implement-native-emulator.log; evidence/implement-native-export-driver.log; evidence/implement-resume-final-apk.log; evidence/implement-native-export.log; evidence/implement-android-prototype.png |

## 2. File đã thay đổi

Nhánh superproject và frontend: feat/4.09-mlkit-prototype. Chưa commit/push.

| Submodule | File |
|---|---|
| frontend | mobile/pubspec.yaml, mobile/pubspec.lock |
| frontend | mobile/android/app/build.gradle.kts |
| frontend | mobile/lib/main_ocr_prototype.dart |
| frontend | mobile/lib/features/ocr_prototype/ocr_models.dart, ocr_store.dart, ocr_native.dart, ocr_controller.dart, ocr_screen.dart |
| frontend | mobile/test/features/ocr_prototype/ocr_controller_test.dart, ocr_screen_test.dart, native_export_driver.dart |
| frontend | mobile/integration_test/ocr_prototype_test.dart |
| superproject work | 04-impl-notes.md, benchmark-protocol.md, benchmark_manifest.example.json, scripts/evaluate_ocr.py, scripts/test_evaluate_ocr.py, results/README.md, results/native-smoke-index.json, results/runs/15f29db3-510a-4f8f-a041-9d1ccfdf322c.json, evidence/ |

Không còn thay đổi mobile/ios. Native integration test đã chạy trên máy ảo Android, chưa chạy điện thoại thật. Hiện có 13 file frontend thuộc phạm vi plan (driver mới nằm trong glob test đã duyệt). APK mới: frontend/mobile/build/app/outputs/flutter-apk/app-debug.apk; file build ignored, không commit.

Scope toàn repo vẫn exit 1 vì 136 file ngoài plan thuộc thay đổi riêng: .gitignore, tools/tesseract/**, api_contract/README.md, api_contract/openapi.json. Người dùng đã xác nhận “Giữ nguyên, tiếp tục riêng 4.09”; không sửa/stash/commit chúng. Mọi file frontend thuộc 4.09 được scope liệt kê [OK]. Không tuyên bố scope toàn repo sạch; log evidence/implement-resume-scope.log. File session Kotlin tạm từng xuất hiện trong lúc build nhưng đã tự biến mất khi build hoàn tất; scope cuối chỉ còn 136 file nền đã được cho giữ.

## 3. Kết quả kiểm tra

| Lệnh | Kết quả | Log |
|---|---|---|
| flutter pub get | Thành công; pin google_mlkit_text_recognition 0.17.1, image_picker 1.2.4, path_provider 2.1.6 | evidence/implement-P1-pub.log |
| flutter test | 546 pass trong lượt tiếp tục sau duyệt plan Android | evidence/implement-resume-final-frontend.log |
| flutter test test/features/ocr_prototype | 13 pass sau Android-only | evidence/implement-android-only-tests.log |
| flutter analyze | No issues found trong lượt tiếp tục; analyzer riêng native test/driver cũng sạch | evidence/implement-resume-final-analyze.log; evidence/implement-resume-native-analyze.log |
| dart format trên các file mới | Hoàn tất | evidence/implement-format.log |
| flutter build apk --debug -t lib/main_ocr_prototype.dart | Build cuối thành công, 34.0 giây Gradle; APK entrypoint prototype, không phải test harness | evidence/implement-resume-final-apk.log; evidence/implement-final-apk-sha256.log |
| python -m unittest discover -s work/4.09-mlkit-prototype/scripts -p test_*.py -v | 13 pass trong lượt tiếp tục; fixture giả, không phải accuracy thật | evidence/implement-resume-P6.log |
| adb devices -l / emulator -list-avds | Không có điện thoại thật; có AVD Pixel_9_Pro_XL | evidence/implement-resume-devices.log; evidence/implement-resume-avds.log |
| flutter test integration_test/ocr_prototype_test.dart -d emulator-5556 --dart-define-from-file=.../scratch/native-defines.json | 2 ca native pass: controller/store/export JSON với ảnh có chữ; blank/hỏng | evidence/implement-native-emulator.log |
| flutter drive --driver=test/features/ocr_prototype/native_export_driver.dart --target=integration_test/ocr_prototype_test.dart -d emulator-5556 --dart-define-from-file=... | Pass; host callback đã ghi nguyên payload JSON thực | evidence/implement-native-export-driver.log; evidence/implement-native-export.log |
| Cài và mở APK prototype cuối trên AVD | Status ok, đã xem screenshot, màn prototype hiển thị rõ không overflow | evidence/implement-android-prototype.png |

Lần full test đầu có 545 pass/1 fail ở test chưa scroll tới export; đã sửa test và lần full suite sau có 546 pass. Lần analyze đầu toàn mobile có 5 info curly braces trong file mới; đã sửa, lần cuối sạch. Lần build Android đầu có lỗi cache Kotlin C:/D:, cơ chế fallback vẫn build thành công; bản build lại Android-only thành công, không nâng toolchain hoặc sửa Gradle ngoài plan.

## 3b. Bộ test case Excel

Task M: thực hiện ở giai đoạn test; chưa dựng Excel.

## 4. Migration

Không có API/backend/schema/health endpoint mới.

## 5. Ghi chú cho người review

- AC1: ML Kit native đã chạy offline trên máy ảo Pixel_9_Pro_XL / sdk_gphone16k_x86_64, Android 17. Wi-Fi/mobile data đã tắt; log chọn module OCR local. Đây là smoke trên emulator, chưa phải kiểm chứng điện thoại thật hoặc benchmark.
- AC2: raw Unicode/newline giữ nguyên; JSON schemaVersion=1 chứa runId/imageId/status/elapsedMs và metadata. Bản lưu nằm application-support/ocr_runs trên thiết bị. Export JSON qua share sheet; không tự share ảnh. imagePath chỉ là đường dẫn tương đối trong app; dùng imageId lấy ảnh nguồn 4.08.
- AC3/AC4: unit/widget chứng minh phân loại trạng thái, cancel, phục hồi lựa chọn không tự OCR, retry, chặn double tap, không notify sau dispose và close sau tác vụ. Ca native đã kiểm ảnh trắng/hỏng và lưu/đọc raw. Gallery, share sheet, native lifecycle và permission còn pending; fixture picker không thay bằng chứng gallery thật.
- AC5/AC7/AC8: template protocol/evaluator sẵn; draft/thiếu dữ liệu/config/nhãn/thiết bị => pending, không go. Chọn n run sớm nhất theo timestamp/runId cho mỗi image/device/cold-warm; không chọn lại run tốt hơn. Không dùng điểm fixture làm benchmark.
- AC6: không HTTP/backend/cloud OCR hoặc medication repository trong feature. Engine chỉ nhận đường dẫn ảnh; nhãn chỉ ở evaluator offline. Không xử lý đơn thuốc/tạo thuốc.
- Đã đọc lại Proposal_v5 FR01, phạm vi on-device và blister-pack/manual-confirmation; evidence/implement-resume-business.log. Phạm vi nền tảng được người dùng đổi trực tiếp sang Android; nội dung nghiệp vụ còn lại giữ nguyên.
- Giao diện dùng theme mobile hiện có; không thêm route vào app chính. Chạy: `cd frontend/mobile` rồi `flutter run -t lib/main_ocr_prototype.dart -d <android-device>`.
- Metadata device/OS/revision/nativeSdkVersion do người thử nhập và xác nhận. Android plugin khai báo com.google.mlkit:text-recognition:16.0.1; model version nội bộ ghi not_exposed. Cần đối chiếu build evidence trước benchmark.
- Hướng dẫn nhận raw cho 4.14 và đề xuất bàn giao results/runs/*.json nằm trong benchmark-protocol.md. Đã có 1 raw ML Kit thực tế từ ảnh pilot trên máy ảo, tại results/runs/15f29db3-510a-4f8f-a041-9d1ccfdf322c.json (375 ký tự; 3715 ms của riêng run này). Không dùng thời gian emulator này làm ngưỡng; không tạo kết quả giả. Source/hash/giới hạn ở results/native-smoke-index.json và results/README.md.

## 6. Phát sinh và quyết định

1. Người dùng cho giữ thay đổi sẵn có pubspec.lock (xóa ffi_leak_tracker) làm baseline; không phục hồi bản cũ.
2. Người dùng cho giữ 136 file ngoài task; không mở rộng scope sửa các file đó.
3. Người dùng yêu cầu bỏ iOS: đã gỡ Podfile mới, phần nâng deployment target/photo usage/MinimumOSVersion do task thêm và đổi platform guard/text sang Android-only. Đã reopen, cập nhật và duyệt lại 01; 03 đã cập nhật và approved lại; đã tiếp tục implement theo gate.
4. Không có điện thoại Android kết nối; đã dùng AVD read-only để kiểm native offline và raw JSON. APK build/native emulator không chứng minh permission/gallery/share sheet/lifecycle trên điện thoại thật. Q1 (ngưỡng, thiết bị và protocol) và dataset 4.08 vẫn chặn benchmark/go-no-go.
5. Không sửa file ngoài bảng plan; không có commit/push hoặc tự duyệt.

## 7. Evidence native và raw bàn giao

- Dùng AVD có sẵn Pixel_9_Pro_XL tại emulator-5556, WHPX khả dụng, -read-only -no-snapshot -no-window. Không thay dữ liệu AVD gốc; đã đóng máy ảo sau kiểm tra, log evidence/implement-emulator-cleanup.log.
- Ảnh pilot 4.08: hapacol_extra_original.png, nội dung thực WebP dù đuôi .png; giữ nguyên byte. SHA-256: 839db054f22fbb2d55de40384f11f80906087914d1420e9153c5cd7842582add. Không đọc labels.xlsx làm input OCR.
- Fixture truyền vào sandbox app và so hash trước chạy. Trên Windows, không truyền cả base64 ảnh vào dart-defines vì vượt giới hạn độ dài lệnh. Dùng OCR_IMAGE_PATH và base64 qua stdin adb để bảo toàn byte, không thay đổi ảnh.
- flutter test có thể dọn test app sau chạy; để thu raw, dùng integrationDriver.reportData + host callback nhận nguyên chuỗi JSON gốc. Driver nằm trong glob test đã duyệt, từ chối overwrite run khác. OCR_RESULTS_DIR trỏ tới results của task.
- Native test dùng picker fixture, controller/ML Kit/FileOcrStore thật; không thao tác gallery/share sheet của hệ điều hành. File host là raw export đã kiểm round-trip, không giả lập bấm Chia sẻ.
- Bản APK cuối đã build lại -t lib/main_ocr_prototype.dart sau native test để không bàn giao harness. SHA-256: 64187cea3cb24b145f255393fe9cfb0f351c7718f48bc9fbd80ba1ba5e3ef3fc.
- Ảnh pilot/máy ảo không đại diện bộ 4.08 chụp thật; không có accuracy hoặc kết luận go/no-go. Không tạo điểm benchmark từ fixture unit test.

## Bước tiếp theo (lịch sử prototype 2026-10-27)

- Đang chờ: người duyệt implement. Phần code P1–P6 xong; P7 đã xong kiểm tự động/native smoke, còn manual và benchmark pending được ghi rõ.
- Lệnh duyệt: `python .agents/scripts/gate.py approve 4.09-mlkit-prototype implement`.
- Sau duyệt, lượt tiếp theo wf-test: kiểm gallery/permission/share sheet/lifecycle/restart, thiết bị Android đã chốt; testcase Excel theo wf-testcase. Chốt Q1 và bộ 4.08 đã xác minh trước đợt B, không đóng 4.09 hoặc tự kết luận go khi thiếu evidence.
- Bàn giao raw cho 4.14: results/README.md và runs/<runId>.json; source/hash/loại pilot nằm trong native-smoke-index.json. Không dùng imagePath như URL ảnh.
- Chưa commit/push. Đề xuất commit work và code khi người dùng yêu cầu; chỉ stage file thuộc task, không .gitignore/tools/api_contract hoặc scratch/__pycache__. Commit/push frontend trước khi bump con trỏ.
- Lệnh artifact dự kiến: `git add -- work/4.09-mlkit-prototype/04-impl-notes.md work/4.09-mlkit-prototype/benchmark-protocol.md work/4.09-mlkit-prototype/benchmark_manifest.example.json work/4.09-mlkit-prototype/scripts/evaluate_ocr.py work/4.09-mlkit-prototype/scripts/test_evaluate_ocr.py work/4.09-mlkit-prototype/results work/4.09-mlkit-prototype/evidence` rồi `git commit -m "docs(ocr): record Android prototype implementation"`. Chưa chạy.
- Cập nhật: 2026-10-27, Codex.

## Tự kiểm bàn giao implement (lịch sử prototype 2026-10-27)

- Gate implement OK; requirement/plan vẫn approved, không tự duyệt 04.
- 13 file frontend của task nằm trong plan; scope toàn repo exit 1 chỉ do 136 file nền đã được người dùng cho giữ, không có file nguồn mới ngoài phạm vi. Kiểm tra đối chiếu: evidence/implement-final-artifact-check.log.
- Full Flutter test, evaluator test, native smoke, analyzer và APK đã thực sự chạy trong lượt tiếp tục này, log ở bảng kiểm tra. Manual/benchmark còn pending được ghi rõ; không tuyên bố hoàn thành task.
- Raw JSON từ ML Kit thật trên emulator có source/hash; máy ảo riêng đã đóng; không commit/push.
