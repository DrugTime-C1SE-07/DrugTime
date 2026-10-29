---
task: 4.09-mlkit-prototype
title: Prototype ML Kit và đánh giá go/no-go OCR
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 16:19 +0700
content_hash: sha256:8a9ccb35212f46c2
---

# 4.09 · Prototype ML Kit và đánh giá go/no-go OCR

## 1. Mục tiêu

Prototype Flutter trên Android nhận ảnh tĩnh, gọi ML Kit trên thiết bị, xem và lưu text OCR thô cùng thời gian xử lý. Dùng ảnh và nhãn trong datasets/ để đo khả năng đọc đúng tên thuốc; hàm lượng là chỉ số phụ độc lập khi có đáp án đọc được trên ảnh. Kết quả pilot phục vụ bàn giao cho chuẩn hóa/matching và quyết định hướng GO/no-go do người phụ trách xác nhận, kèm số liệu/giới hạn. Benchmark có ngưỡng là phép đo riêng, chỉ kết luận đạt ngưỡng khi đã chốt protocol trước lần đo chính thức. Prototype chạy được chưa có nghĩa hoàn thành task.

## 2. Phạm vi

### Trong phạm vi

- Nền tảng task 4.09 chỉ Android theo xác nhận người dùng; báo cáo pilot/quyết định hướng phải ghi rõ thiết bị đã và chưa kiểm. Chỉ benchmark chính thức có ngưỡng mới yêu cầu thiết bị được chốt trong protocol trước lần đo.
- Đợt A: nhận ảnh tĩnh người thử cung cấp, xem ảnh và raw text; lưu kết quả độc lập mỗi lần chạy, có mã ảnh/run ID, engine/phiên bản, thiết bị/OS, cấu hình, thời gian và trạng thái.
- Xuất kết quả đọc được ngoài app, đưa bản JSON gốc vào datasets/results/ để các task 4.12–4.14 và 4.17 dùng lại; giữ nguyên chữ nhận diện, không ghi đè lần chạy cũ. App vẫn lưu nội bộ trên Android; bản trong repo được lấy qua export/import trên máy tính, không ghi trực tiếp vào đường dẫn Windows từ Android.
- Phân biệt có chữ, không có chữ, lỗi đầu vào, lỗi engine; hủy chọn ảnh không phải lỗi OCR.
- Pilot: đọc trực tiếp datasets/labels.xlsx theo các cột image_id, relative_path, drug_name, strength, không cần người thử điền thêm manifest trùng thông tin để chấm ban đầu. Báo số ảnh đã chạy/chưa chạy và lỗi dữ liệu. Header hiện ở B2, không giả định luôn bắt đầu A1.
- Bàn giao pilot: dùng bộ ảnh/nhãn 4.08, ghi phiên bản/hash và trạng thái xác minh; báo exact tên, hàm lượng phụ, tử/mẫu, nhóm ảnh và timing theo thiết bị. Ghi quyết định hướng GO/no-go do người phụ trách xác nhận, cùng lý do và giới hạn; không yêu cầu matching hoàn tất.
- Nếu nhóm làm benchmark chính thức có ngưỡng: dùng bộ ảnh/nhãn đã xác minh và cố định, protocol/hash/thiết bị/độ phủ/lần lặp và ngưỡng chốt trước lần đo. Đây là đầu ra riêng, không điều kiện chặn quyết định hướng từ pilot theo AC7 mới.
- Công cụ nhập/chấm và hướng dẫn dùng chung nằm trong datasets/scripts/ và datasets/README.md; raw/báo cáo trong datasets/results/. Hồ sơ duyệt/evidence quy trình vẫn nằm trong work/4.09-mlkit-prototype. Chỉ sửa code/công cụ sau khi tới implement được duyệt.
- Chuyển dữ liệu lịch sử từ work/ sang khu legacy-pilot của datasets/ bằng bản sao nguyên byte và kiểm hash; giữ bản cũ để bằng chứng đã ghi còn truy vết. Tách các run chưa nối được với ảnh/nhãn hiện tại, không gộp chúng vào điểm pilot mới.

### Ngoài phạm vi

- Cấu hình, build, kiểm thử hoặc đánh giá go/no-go trên iOS; không yêu cầu máy Mac/Xcode hoặc thiết bị iOS để hoàn thành 4.09. Phạm vi nền tảng chung của sản phẩm trong proposal không thay đổi.
- Thu thập đủ bộ 4.08, sửa nhãn hoặc công cụ công cụ OCR nghiên cứu cũ của task đó.
- Camera, quyền camera, capture, crop, preprocessing của 4.10.
- Pipeline gọi OCR sang matching thuộc 4.11; normalization/index sản phẩm thuộc 4.12; fuzzy matching/scoring/top-N thuộc 4.13; chọn/xác nhận thuốc và tự điền thông tin không triển khai ở 4.09.
- Chấm hoạt chất, sửa chính tả OCR theo nhãn hoặc dùng fuzzy matching để nâng điểm OCR. Việc chuẩn hóa tối thiểu phục vụ so sánh không triển khai normalization sản phẩm của 4.12.
- OCR đơn thuốc, LLM, OCR cloud, huấn luyện engine; backend/DB/API mới; commit/push.

## Cập nhật phạm vi 2026-10-29

- Người dùng đã reopen requirement/plan sau khi yêu cầu bỏ nghiên cứu OCR cũ. 4.08 chỉ bộ ảnh có nhãn; 4.09 dùng ML Kit Android. Tài liệu nguồn là bảng Sprint mới và chỉ dẫn trong chat, không dùng backlog repo cũ.
- Người dùng quyết định GO tiếp tục ML Kit. Ghi riêng quyết định này, không coi partial/token rời là matching đúng hoặc suy mọi name_not_found do nhãn sai.
- Pilot-002 hiện có 49/49 ảnh: exact 23, partial 10, token rời 4, name_not_found 11, no_text 1, median 2615ms/p95 5267ms trên emulator. Evidence test-pilot002-current.log từ lượt trước. Chưa coi mọi nhãn đã verified độc lập, không chạy OCR/test/build mới trong lượt sửa requirement.
- Các nhắc nghiên cứu OCR/dataset chưa đủ trong bảng khảo sát hoặc evidence trước 2026-10-29 bên dưới là lịch sử; không là yêu cầu làm thêm công cụ cũ hoặc trạng thái thiếu 15 ảnh hiện tại.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn | Điều rút ra |
|---|---|
| Yêu cầu trực tiếp ngày 2026-10-28; work/4.09-mlkit-prototype/dataset-evaluation-change.md | Đưa công cụ/raw/báo cáo dùng chung vào datasets/, đọc format XLSX hiện tại; tên thuốc là mục tiêu chính, hàm lượng phụ; người dùng đã reopen 01/03/04. |
| datasets/labels.xlsx; datasets/images/; evidence/requirement-dataset-source.log | Vòng này đọc thực tế 17 dòng nhãn và 17 ảnh JPG. Sheet1 có header B2:E2: image_id, relative_path, drug_name, strength. Số lượng không chứng minh nhãn đã được xác minh hay bộ ảnh đủ đại diện. Không sửa workbook ở requirement. |
| work/4.09-mlkit-prototype/scripts/evaluate_ocr.py; results/README.md; 03-plan.md | Evaluator hiện còn đòi tên/hoạt chất, frozen protocol và manifest riêng; raw nằm trong work/. Cần cập nhật sang đánh giá pilot theo format mới trước khi chạy chấm; chưa sửa code. |
| Screenshot run 71e2ac39-c00b-45b4-a5ea-f604fda06de5 và datasets/images/decolgen_forte/box/decolgen_forte_box_001.jpg do người dùng gửi | Phần raw nhìn thấy có Decolgen và FORTE nhưng tách xa; cần tách lỗi bố cục/thứ tự khỏi exact. Screenshot không thay JSON gốc hoặc bằng chứng elapsedMs. |
| Xác nhận trực tiếp của người dùng ngày 2026-10-27: “không cần trên ios, chỉ tren android thôi” | Giới hạn task 4.09 ở Android; người dùng đã reopen requirement/plan để cập nhật, giữ các yêu cầu OCR/raw/benchmark khác. |
| Description 4.08–4.11 và xác nhận của người dùng trong chat | 4.09 giữ ML Kit; làm prototype trước và benchmark sau. Đây là phạm vi hiện hành. |
| AGENTS.md; .agents/skills/wf-next/SKILL.md; .agents/skills/wf-requirement/SKILL.md | Requirement cần duyệt trước plan/implement; không tự duyệt. |
| frontend/mobile/pubspec.yaml | Dart >=3.5.0 <4.0.0; hiện đã có google_mlkit_text_recognition 0.17.1, image_picker 1.2.4 và path_provider 2.1.6 từ vòng implement trước reopen. |
| frontend/mobile/lib/features/ocr_prototype/ocr_native.dart; ocr_screen.dart | Đọc lại trong vòng sửa: platform guard chỉ Android; màn thử nghiệm riêng. Không coi code/build là bằng chứng native OCR đạt AC1. |
| work/4.09-mlkit-prototype/04-impl-notes.md; 05-test-report.md; results/README.md | Lịch sử đã có test native emulator và 6 raw JSON, chưa có benchmark hoàn chỉnh/go-no-go hoặc chứng minh điện thoại thật. Vòng requirement hiện tại không chạy lại OCR/test/build. |
| frontend/mobile/lib/app/router.dart | Có route thuốc và QR; chưa có route prototype OCR. |
| frontend/mobile/lib/features/medication/presentation/screens/add_medication_screen.dart | Quét vỏ thuốc mới là toast đang phát triển. |
| frontend/mobile/lib/features/medication/data/repositories/remote_medication_repository.dart | Search gọi GET /catalog/medications; prototype không cần endpoint này. |
| work/4.08-ocr-capture-evaluation/01-requirement.md; README.md; 04-impl-notes.md | Có nghiên cứu công cụ OCR nghiên cứu cũ và hai ảnh web pilot; phần ảnh chụp thật/benchmark chưa hoàn thành. Không suy ra 4.09 đổi engine. |
| docs/Team1_DTU/01_Proposal_&_Planning/Proposal_v5.docx, §6.2, §6.3, FR01, §8.1 và lộ trình | Quét vỉ thuốc on-device, có xác nhận thủ công; đơn thuốc ngoài Phase 1. Lộ trình cũ đặt luồng sản phẩm ở Sprint 5; người dùng hiện yêu cầu prototype Sprint 4. |

### Quyết định nghiệp vụ áp dụng

| Nguồn/baseline | Quy tắc/trạng thái | AC |
|---|---|---|
| Chỉ dẫn trực tiếp ngày 2026-10-28 về datasets và format nhãn hiện tại | Tên thuốc chính; hàm lượng phụ; không chấm hoạt chất; giữ raw và dùng lại trong task sau. Phạm vi người dùng yêu cầu, đang ghi lại để duyệt requirement. | AC2, AC5, AC7–AC13 |
| Chỉ dẫn nền tảng mới của người dùng ngày 2026-10-27; Proposal_v5 phần Mobile App/Expected Outcomes | Chốt riêng 4.09 chỉ Android; iOS ngoài task này. Proposal vẫn mô tả sản phẩm Android/iOS, không sửa proposal hoặc suy thành bỏ iOS toàn dự án. | AC1, AC5, AC7, AC8 |
| Bảng Sprint 4 mới do người dùng cung cấp trong chat, ưu tiên hơn backlog cũ trong repo | 4.08 ảnh/nhãn; 4.09 ML Kit và quyết định hướng; 4.12 normalization/index; 4.13 matching; 4.14 unit test bằng raw; 4.17 đo top-1/top-N toàn luồng. Không dùng accuracy OCR làm accuracy matching. File Downloads từng cung cấp hiện không còn tại đường dẫn khi đọc lại; không thay bằng backlog cũ. | AC1–AC13 |
| Proposal_v5.docx §6.2, FR01, §8.1 | Xử lý vỉ thuốc trên thiết bị, không gửi ảnh tới backend/OCR cloud. Quy tắc trong proposal. | AC1, AC6 |
| Proposal_v5.docx §6.3 | OCR đơn thuốc ngoài Phase 1. | AC6 |
| Proposal_v5.docx lộ trình blister-pack scan with manual confirmation | OCR không phải quyết định chọn thuốc; prototype không tạo/cập nhật thuốc. | AC6 |
| Lộ trình proposal so với description hiện tại | Làm prototype Sprint 4 theo yêu cầu trực tiếp, không sửa proposal hoặc tuyên bố xong luồng sản phẩm. | AC8 |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| frontend | Có ở implement | Flutter prototype, plugin native và test trên Android; không sửa cấu hình iOS. |
| backend | Không | Không có API mới. |
| api_contract | Không | Không đổi hành vi HTTP. |
| tests | Không | Test thuộc frontend/mobile, không cần E2E service. |
| docs | Không | Chỉ đọc proposal. |
| .agents | Không | Chỉ dùng quy trình. |

Superproject: có thay đổi công cụ, dữ liệu dùng chung và hướng dẫn trong datasets/ ở giai đoạn implement; datasets/ là thư mục thường, không phải submodule mới. affected vẫn ghi frontend vì trường này liệt kê submodule. Không commit/push khi chưa được yêu cầu.

## 5. Thay đổi API contract

- contract_change: no. Không thêm/sửa/xóa endpoint, field, mã lỗi hoặc xác thực.
- Endpoint bối cảnh: GET /catalog/medications; không gọi trong prototype.
- Định dạng export cục bộ sẽ chốt ở plan, không phải contract API backend.

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm dữ liệu patient, lịch uống, consent, interaction engine, schema hoặc ranh giới backend.
- OCR sai tên/hàm lượng có thể gây hiểu nhầm: chỉ hiển thị kết quả thử, không tự xác nhận/lưu thuốc.
- Dùng ảnh bao bì không có dữ liệu cá nhân; xử lý/lưu cục bộ; không ghi token/credential.
- Nhãn chỉ dùng để chấm, không sửa raw hoặc làm đầu vào nhận diện.
- Confidence nếu có không phải accuracy; không dựng confidence giả.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given ảnh tĩnh hợp lệ trên thiết bị Android đã cấu hình hỗ trợ, When chạy ML Kit thật, Then thấy ảnh, raw text, thời gian và trạng thái không cần backend; ghi model/OS Android đã và chưa kiểm. Không yêu cầu kiểm chứng iOS. | manual: runtime native |
| AC2 | Given kết quả có chữ, When xuất và đọc lại, Then raw giữ nguyên và đủ run ID/mã ảnh/engine/phiên bản/thiết bị/OS/cấu hình/thời gian/trạng thái; chạy lại không ghi đè kết quả. | unit lưu/đọc; manual export thiết bị |
| AC3 | Given ảnh không chữ, tệp lỗi/không truy cập được hoặc hủy chọn, When xử lý, Then phân biệt no-text/lỗi đầu vào/hủy; không crash và thử ảnh khác được. | unit fake; manual native |
| AC4 | Given OCR đang chạy hoặc engine lỗi, When thao tác lặp/rời màn hình/lỗi xảy ra, Then không chồng kết quả sai ảnh, không cập nhật màn đã đóng, kết thúc trạng thái rõ và giải phóng tài nguyên. | unit fake; manual lifecycle |
| AC5 | Given bộ ảnh và labels.xlsx có nhãn tên hợp lệ, When chấm JSON ML Kit, Then ghép đúng imageId/image_id; tên chỉ đạt exact khi cả cụm xuất hiện đúng thứ tự, ranh giới từ sau NFC/casefold/thu gọn whitespace. Tách đủ token nhưng không liền cụm, thiếu/sai tên, no_text/lỗi, chưa chạy và không ánh xạ; không dùng fuzzy hoặc sửa chữ. Báo tử/mẫu exact trên ảnh có nhãn đã chạy, coverage trên toàn bộ nhãn hợp lệ, latency median/p95/n theo thiết bị và nhóm sản phẩm/bao bì; không tự suy điều kiện chụp. | unit phép tính; manual nhãn |
| AC6 | Given prototype và ảnh bao bì, When nhận diện/xuất, Then không gửi ảnh tới OCR cloud/backend, không dùng nhãn sửa raw, không tạo/cập nhật thuốc và không làm OCR đơn thuốc. | unit/kiểm tra mã; manual luồng |
| AC7 | Given báo cáo pilot Android có raw truy vết, số liệu và giới hạn, When người phụ trách quyết định hướng GO/no-go, Then ghi người/ngày/lý do quyết định và phân biệt với benchmark đạt ngưỡng hoặc accuracy matching. Pilot tự động vẫn not_decided; quyết định kỹ thuật ghi riêng. Nếu làm benchmark có ngưỡng, protocol vẫn phải chốt trước lần đo chính thức, không áp ngưỡng sau khi đã xem điểm. | unit không tạo go giả; manual review/quyết định |
| AC8 | Given mới có pilot hoặc thiếu kiểm chứng native/lifecycle/export/nhãn bắt buộc, When bàn giao, Then ghi rõ mức sẵn sàng, số liệu/điều kiện đã kiểm và phần pending; GO về hướng kỹ thuật không tự chứng minh đạt benchmark, matching đúng hoặc đủ Definition of Done. | manual |
| AC9 | Given workbook đúng các cột hiện tại nhưng có hàng/cột trống trước header, When chấm pilot, Then đọc được mà không sửa workbook; ID trùng, nhãn thiếu, đường dẫn sai/thoát dataset, ảnh thiếu hoặc JSON hỏng được báo cụ thể, không làm mất âm thầm các hàng khỏi mẫu số/coverage. | unit |
| AC10 | Given run có strength được xác minh nhìn thấy trên ảnh, When đánh giá hàm lượng, Then báo độc lập với tên; nhãn trống là unscored. Nhãn nhiều thành phần phải có quy tắc thành phần–hàm lượng rõ trước khi chấm; chưa có thì ghi chưa chấm, không coi tìm thấy một số mg là đúng toàn bộ. Không dùng tên/nhãn để suy hàm lượng không nhìn thấy. | unit; manual xác minh nhãn |
| AC11 | Given raw lịch sử hoặc JSON xuất/import mới, When đưa vào datasets/results/, Then giữ nguyên byte/payload, kiểm hash bản sao, giữ nguồn và bản cũ; cùng runId khác nội dung bị từ chối ghi đè. ID chưa ánh xạ để riêng; screenshot không được dựng thành raw native giả. | unit nhập/bảo toàn; manual JSON native |
| AC12 | Given nhiều lần chạy hoặc nhiều thiết bị cho cùng ảnh, When chấm, Then giữ mọi run và chọn trước quy tắc run sớm nhất theo createdAt hợp lệ/runId cho mỗi ảnh/thiết bị ở pilot; không thay bằng run tốt hơn, không gộp emulator với điện thoại thật. Benchmark chính thức dùng quy tắc/lần lặp trong protocol frozen. | unit |
| AC13 | Given người khác có dataset và raw, When chạy công cụ theo README, Then nhận bảng từng ảnh, tổng hợp máy đọc được và báo cáo dễ đọc, có nhãn kỳ vọng/trạng thái/đường dẫn raw/runId, coverage và lỗi dữ liệu. Không cần backend hoặc thay file nhãn để chạy pilot; hồ sơ duyệt vẫn ở work/. | unit đầu ra công cụ; manual tái hiện |

## 8. Câu hỏi mở

Không có câu hỏi chặn quyết định hướng: người dùng đã chọn GO tiếp tục ML Kit ngày 2026-10-29. Đây là quyết định từ pilot, không phải đạt ngưỡng đặt trước.

Q1 [không chặn bàn giao pilot/quyết định hướng; chỉ chặn benchmark chính thức có ngưỡng] Nếu nhóm thực hiện benchmark có ngưỡng, cần chốt thiết bị/OS, độ phủ, lần lặp, ngưỡng tên/timing và protocol trước lần đo. Không tự biến điểm pilot thành bằng chứng đạt ngưỡng hoặc sửa script để sinh go giả. Yêu cầu native/manual/nhãn và review còn thiếu vẫn phải kiểm, không được miễn chỉ vì đã GO.

## 9. Giả định

- Người dùng đã chốt ML Kit cho 4.09; không yêu cầu sửa/reopen 4.08.
- Bộ hiện có 17 ảnh tại thời điểm khảo sát, đủ bắt đầu pilot nhưng chưa được xác nhận đại diện benchmark. Raw cũ không tự nhập chung bộ mới; không dùng nhãn làm từ điển sửa chữ.
- 4.09 chỉ hỗ trợ/kiểm thử Android theo yêu cầu mới. Phiên bản package, yêu cầu build và model/OS Android khả dụng cần ghi trong plan/protocol; build APK hoặc test trên web/Windows không chứng minh OCR native trên Android chạy được. iOS không phải điều kiện chặn task.
- 12h là estimate backlog, không phải thời gian đã làm hoặc cam kết accuracy.

## 10. Phát sinh

- 4.08 có nghiên cứu công cụ OCR nghiên cứu cũ mở rộng nhưng 4.09 giữ ML Kit theo xác nhận người dùng.
- Bản benchmark có ngưỡng (nếu nhóm thực hiện) cần dữ liệu/protocol đủ trước đo; không tiếp tục coi việc thiếu benchmark frozen là chặn quyết định GO từ pilot của người phụ trách.
- Vòng implement trước đã có code/package, APK, native smoke trên emulator và raw; chưa có benchmark đầy đủ/điện thoại thật/go-no-go. Không chạy test/build ứng dụng trong vòng sửa requirement này.
- Ngày 2026-10-28: người dùng đã reopen requirement/plan/implement sau khi yêu cầu chuyển dữ liệu/công cụ sang datasets và chấm theo format hiện tại. Vòng này chỉ sửa requirement; plan và implementation phải đồng bộ ở các lượt sau. Không sửa code, datasets hoặc raw ở requirement.
- File sprint4-tasks (1).md trong Downloads không còn ở đường dẫn đã cung cấp khi thử đọc lại; sử dụng bảng task mới và phân công người dùng đã gửi trong chat, không tra backlog repo cũ để ghi đè phạm vi.
- Scope requirement vòng này báo 22 file ngoài phạm vi: .gitignore, api_contract/README.md, api_contract/openapi.json và 19 file datasets có sẵn trước lượt sửa này (17 ảnh, workbook, README). Người dùng đã cho giữ thay đổi riêng, đã yêu cầu tạo/điền dataset và hiện yêu cầu tích hợp dataset; không xin lại quyền giữ các file đó. Vòng này không sửa chúng; plan kế tiếp phải liệt kê rõ phần datasets sẽ thay đổi. Không tuyên bố scope toàn repo sạch.

## 11. Size

- size: M. Một submodule frontend và công cụ/dữ liệu ở superproject; prototype native, export, nhập/chấm XLSX, xử lý lỗi/test và benchmark vượt tiêu chí S. Không đổi contract.

## Bước tiếp theo

- Chờ duyệt: python .agents/scripts/gate.py approve 4.09-mlkit-prototype requirement
- Sau duyệt, lượt kế tiếp đồng bộ plan: tách quyết định GO của người phụ trách khỏi decision tự động của pilot và benchmark có ngưỡng; dùng dữ liệu 49/49 ảnh đã có, không quét lại chỉ vì đổi hồ sơ hoặc sửa nhãn.
- Không đợi nghiên cứu OCR cũ hoặc matching 4.13 để bàn giao 4.09. Không miễn native manual, xác minh nhãn, review hoặc điều kiện Definition of Done.
- Cập nhật: 2026-10-29, Codex.

## Kiểm tra giai đoạn requirement (vòng sửa Android-only)

Mục dưới là lịch sử ngày 2026-10-27, không phải kết quả kiểm tra hiện tại.

- `python .agents/scripts/gate.py 4.09-mlkit-prototype requirement`: OK; evidence/requirement-android-only-gate.log.
- Đọc lại nguồn proposal v5 và chỉ dẫn nền tảng mới; evidence/requirement-android-only-source.log. Chỉ dẫn mới giới hạn task 4.09, không thay nền tảng sản phẩm chung trong proposal.
- Scope vòng sửa: exit 1, “CHẶN: 148 file ngoài phạm vi”; xem evidence/requirement-android-only-scope.log. Đây là 12 file frontend của vòng implement trước reopen cùng 136 file thay đổi riêng đã được người dùng cho giữ. Repo có code implement 4.09 từ trước reopen và thay đổi riêng mà người dùng đã cho giữ; không tuyên bố scope toàn repo sạch. Vòng này chỉ sửa artifact trong work/4.09-mlkit-prototype và thêm log.
- Không chạy test app, build hoặc benchmark trong vòng sửa requirement; các bằng chứng implement trước đó chỉ được dẫn lại, không coi là lần chạy mới.

## Kiểm tra giai đoạn requirement (vòng datasets, 2026-10-28)

- Gate requirement OK; log: evidence/requirement-dataset-gate.log. 01/03/04 đều draft khi bắt đầu; chỉ sửa 01 trong lượt này.
- Đọc workbook bằng bundled Python ở chế độ read-only: 17 nhãn/17 ảnh; log: evidence/requirement-dataset-source.log. Không xác nhận nội dung mọi nhãn trong lượt này.
- scope.py báo “CHẶN: 22 file ngoài phạm vi”; log đầy đủ: evidence/requirement-dataset-scope.log. Phân loại baseline và yêu cầu hiện có tại mục Phát sinh; không bỏ qua hoặc xóa thay đổi để làm scope sạch.
- Không sửa frontend, datasets, script, raw, plan hoặc impl-notes; không chạy OCR/test/build/benchmark, chưa chuyển dữ liệu và chưa có go/no-go.

## Kiểm tra requirement sau quyết định hướng · 2026-10-29

- Gate requirement OK, log evidence/requirement-decision-gate.log. Chỉ cập nhật requirement/evidence; không sửa plan/implement approved, code/datasets/raw hoặc nhánh Git.
- Scope báo nguyên văn “CHẶN: 226 file ngoài phạm vi”, log evidence/requirement-decision-scope.log: .gitignore (1), api_contract (2), datasets (222), docs (1). Các thay đổi đã có trước lượt này theo yêu cầu giữ/tạo/điền dataset và file tổng của người dùng; không xin lại quyền giữ, không xóa để làm scope sạch.
- 04-impl-notes vẫn approved nhưng approval đã cũ vì requirement thay đổi. Sau khi duyệt requirement/plan mới, cần rà soát và duyệt lại implement theo gate; không tự đổi metadata hoặc đánh dấu xong.
- Không chạy OCR/test/build trong vòng requirement; giữ nguyên raw. Không còn yêu cầu nghiên cứu engine cũ; không tự xóa bằng chứng lịch sử.
