---
task: 4.16-selection-confirmation-screen
stage: review
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-28 10:56 +0700
content_hash: sha256:88dac76d9b46812b
inputs:
  01-requirement.md: sha256:68d21d09eefdb715
  03-plan.md: sha256:5eee2adbfe7e1076
  04-impl-notes.md: sha256:4d2fac667536668a
  05-test-report.md: sha256:6f3c7c38451a6df1
---

# 4.16 · Review chọn và xác nhận thuốc

## 1. Kết luận

**Đạt, kèm lưu ý — trong phạm vi UI/mock được duyệt và ngoại lệ layout đã được người dùng chấp nhận.**

Không phát hiện Critical/High trong diff task. Có **1 Medium, 0 Low**: vùng xem lại thuốc quá thấp ở màn nhỏ/chữ lớn khi bàn phím mở. Đây là cùng nguyên nhân của TC-MEDPICK-28/51, không đếm thành hai lỗi sản phẩm. Người dùng đã chấp nhận hoãn sửa ngày 28/10/2026; TC-28/51 vẫn Fail và AC10/AC11 chưa đạt đầy đủ ở cấu hình này. Không nâng kết quả hai case thành Pass.

Kết luận cho phép trình người review PR xem xét cùng ngoại lệ; không thay thế ít nhất một người khác approve PR theo Definition of Done. Không kết luận toàn suite xanh, không nghiệm thu OCR/matching 4.13 hoặc search mới 4.15, không khẳng định đã chạy binary release.

## 2. Phạm vi đã review

Gate review được phép bắt đầu: `evidence/review-gate.log`. Requirement, plan, implement và test đều có approval hợp lệ khi bắt đầu phiên.

| Submodule | Base và lệnh kiểm | Phạm vi thực tế |
|---|---|---|
| frontend | `origin/main = HEAD = ccdc3adff1dda6e6664a63d02e7d9e09c7ceb212`; `git -C frontend diff origin/main...HEAD`; `git -C frontend diff origin/main -- mobile`; `git -C frontend ls-files --others --exclude-standard mobile` | Triple-dot diff rỗng vì chưa commit. Đã đọc toàn bộ working diff của 6 file sửa và toàn văn 7 file mới, không bỏ sót untracked. Tổng 13 file đúng bảng 03. Bản chụp nội dung: `evidence/review-frontend-diff.txt`. |
| docs | `origin/main = HEAD = ce9ec72b93bbfe04efdc777389179b2d38e09210`; `git -C docs diff origin/main...HEAD`; đọc workbook hiện tại và bản `git show HEAD:Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` bằng openpyxl chỉ đọc | Chỉ workbook tổng thay đổi. Đối chiếu 52 dòng MEDPICK với spec và workbook task; kiểm hai dòng Bug Report. 20 sheet khác giữ nguyên value/formula/style/number format và merged cells so với docs HEAD. Không ghi lại workbook. |
| backend, api_contract, tests, superproject | Đọc trạng thái Git để phân biệt baseline/ngoài task; không đưa các commit/con trỏ cũ vào diff task | File backend `catalog/fetchers.py` đã có ngoài task; không review/đóng gói thay đổi đó như sản phẩm 4.16. Không thay contract, schema hay E2E repo. |

`scope.py 4.16-selection-confirmation-screen --stage implement`: **exit 1**, log `evidence/review-scope-implement.log`. 13 frontend file và workbook docs đều `[OK]`; chỉ `backend/src/drugtime/modules/catalog/fetchers.py` là `[NGOÀI]`. Mục 4 của 05 đã ghi quyết định người dùng “Giữ nguyên và ghi rõ khi bàn giao”; giữ nguyên và loại khỏi PR task, không xin lại quyết định đã có. Không gọi scope là Pass hoặc sửa scope script để che kết quả.

`evidence/review-git-status.log`: frontend/docs/superproject trên `feat/4.16-selection-confirmation-screen`; backend trên `feat-3.26`. Các con trỏ api_contract/backend/docs/frontend/tests khác base đã có từ trước. Không stage, commit, push hoặc bump chúng trong review.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC9 được đáp ứng trong phạm vi UI/mock: hai nguồn dùng chung panel; giữ thứ tự và object/id; chạm chỉ chọn, confirm khóa lặp; hủy/Back giữ form; OCR rỗng tìm tay trả về caller; tìm rỗng focus cùng ô; thay list/query xóa chọn; metadata thiếu hiển thị trung thực; demo không lưu hoặc đổi nguồn production. AC10/AC11 có ngoại lệ M1 bên dưới, không ghi đạt toàn bộ. |
| Phạm vi | 13 file frontend đúng plan; workbook đúng vai trò testcase-book. Scope exit 1 chỉ do file backend ngoài task được cho phép giữ nguyên từ trước. Phiên review chỉ ghi 06, scratch và evidence trong work của task. |
| Contract | Không đổi API/DTO/field/mã lỗi. `CatalogSearch` chỉ là kiểu hàm UI; caller production vẫn dùng `MedicationController.searchCatalog`. Không phát minh OCR contract hoặc đưa fixture vào mapper/repository production. |
| Bất biến kiến trúc | Nút xác nhận chỉ trả `DrugCatalogItem`, không gọi lưu thuốc/lịch. Form giữ `_save`/client_uuid và kiểm tra liều/giờ hiện có. Không truy cập Supabase trực tiếp, không đổi PEP/consent/log, Worker/liều, interaction engine, timezone hay import giữa module backend. wf-health-endpoint/wf-db-migration không áp dụng vì không thêm/sửa endpoint/service dữ liệu sức khỏe hoặc schema. |
| Bảo mật | Không thấy secret, ảnh/văn bản OCR thật, dữ liệu bệnh nhân thật hoặc debug print mới trong diff. Fixture được đánh dấu tổng hợp; không thêm storage. Route demo có `preview && kDebugMode`, entry chỉ debug/preview; không dùng badge để thay repository hoặc quyết định phân quyền. Đây là review diff/evidence liên quan, không phải chứng nhận quét mọi secret trong repo. |
| Xử lý lỗi | Debounce 300ms và generation giữ chống response về muộn; query trống/quá 100 rune/loading/lỗi/401 phân biệt được. Retry chỉ với lỗi cho phép; dispose hủy timer/controller/focus. Panel kiểm lại object còn trong list trước confirm; host kiểm mounted/current route, chặn trả lặp. Giữ cơ chế MedicationFailure sẵn có, không bổ sung nuốt lỗi. |
| Hiệu năng | Không thêm HTTP/DB call khi chọn/confirm; không thêm N+1 hay truy vấn. Tập kết quả hiện tại nhỏ, panel không xếp hạng lại. Chưa benchmark danh sách ngoài phạm vi/giới hạn hiện tại. |
| Chất lượng test | Đã đọc toàn bộ diff 6 file sửa và 3 test mới. Assertions kiểm identity/latest selection, stale result, double confirm, hủy giữ form, spy lưu bằng 0, HTTP guard và route gate. Suite medication chạy lại phiên review: **172 pass, 0 fail**. Matrix keyboard 220 dp chưa đại diện inset Android 325.5 dp; log thiết bị đã bắt M1, không dùng widget Pass để phủ nhận lỗi. |
| Dễ đọc và nhất quán | Panel sở hữu state cục bộ, screen/sheet dùng chung; dùng theme token hiện có, typed result và dependency injection nhỏ. Không thêm domain abstraction hoặc công nghệ mới. Không thấy code chết/TODO/debug print mới trong diff. |
| Đối chiếu 04/05 với log | Số liệu và giới hạn cuối khớp evidence: medication 172 pass; toàn suite lịch sử 830 pass/1 skip/2 fail; baseline family 10 pass/2 fail; analyze sạch; catalog 43 pass; Android normal Pass và màn nhỏ Fail 21.34 < 35 dp. TalkBack Pass là xác nhận của người dùng; không tự nhận agent thao tác. Hash 13 file khớp đầu stage test. 05 có phần lịch sử cũ; dùng mục 9 và frontmatter/gate cho trạng thái hiện tại. |

### Bằng chứng thực thi trong phiên review

| Lệnh | Kết quả | Log |
|---|---|---|
| `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/gate.py 4.16-selection-confirmation-screen review` | Exit 0, được bắt đầu review | `evidence/review-gate.log` |
| `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/scope.py 4.16-selection-confirmation-screen --stage implement` | Exit 1, một file backend ngoài task; 14 file task đúng phạm vi | `evidence/review-scope-implement.log` |
| `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/testcase_xlsx.py validate 4.16-selection-confirmation-screen` | Exit 0, 52 case: 50 Pass / 2 Fail / 0 Pending | `evidence/review-testcase-validate.log` |
| Từ `frontend/mobile`: `flutter test --no-pub test/features/medication --reporter expanded` | Exit 0; **172 pass**, 23 giây theo reporter | `evidence/review-medication.log` |
| `backend/.venv/Scripts/python.exe -X utf8 work/4.16-selection-confirmation-screen/scratch/review_verify.py` | Exit 0; hash 13 file, AC1–AC11 có case, 52 case có actual và evidence tồn tại, hai workbook khớp spec, hai Bug Report Medium, 20 sheet khác giữ nguyên, các tổng kết log lịch sử khớp | `evidence/review-evidence-verification.log` |
| `git -C frontend diff --check` | Exit 0 | `evidence/review-diff-check.log` |

Flutter CLI dùng `C:/Users/admin/flutter/bin/cache/dart-sdk/bin/dart.exe C:/Users/admin/flutter/bin/cache/flutter_tools.snapshot`. Không chạy lại toàn suite, analyze, API/DB hay thiết bị trong review vì code 13 file không thay đổi so với bằng chứng test. Đã đọc/đối chiếu kết quả các lần chạy trước, không coi là lần chạy mới. Không đổi status testcase, actual, workbook hoặc artifact đã approved.

### Truy vết AC và kết quả cuối

| AC | Test case chính | Kết luận review |
|---|---|---|
| AC1 | TC-30/46 | Hai nguồn cùng panel; Pass trong phạm vi mock. |
| AC2 | TC-31 | Giữ thứ tự và danh tính/cùng tên khác hàm lượng; Pass. |
| AC3 | TC-32/33/34/49 | Chọn chưa trả, confirm đúng một lần, không tự lưu; Pass. |
| AC4 | TC-34/35/36/48 | Đổi chọn, hủy/Back và giữ form; Pass. |
| AC5 | TC-37/39 | OCR rỗng → tìm tay → confirm về caller; Pass. |
| AC6 | TC-38/39 | Tìm rỗng sửa cùng ô, không tạo vòng lặp sheet/thuốc; Pass. |
| AC7 | TC-40/41 | Thay list/query và response cũ không phục hồi lựa chọn; Pass. |
| AC8 | TC-42 | Không bịa metadata hoặc đơn vị/strength; Pass. |
| AC9 | TC-46/47/48/49 | Offline/spy lưu/route production; Pass trong phạm vi mock, không có chứng cứ chạy release. |
| AC10 | TC-43/44/45/50/51 | Widget/normal Pass; Android nhỏ/chữ lớn Fail, M1 được chấp nhận hoãn sửa. |
| AC11 | TC-50/51/52 | Normal và kiểm tay/TalkBack Pass theo nguồn tương ứng; cấu hình nhỏ/chữ lớn vẫn Fail, cùng M1. |

Tiền tố đầy đủ của các case là `TC-MEDPICK-`. TC-25/26/27/29 là hồi quy API/DB thật được chạy bổ sung ở stage test, không mở rộng sản phẩm task thành tích hợp OCR mới. `test-pending-device-response.json` ghi đủ 5 query, id chọn 153, id đã gỡ 154, add_calls=0 và số meds/schedules/prescriptions giữ 0/0/0. Bộ Excel có 2 dòng bug cho 2 case Fail nhưng chỉ 1 nguyên nhân layout.

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| **Medium — M1, đã chấp nhận hoãn sửa** | `frontend/mobile/lib/features/medication/presentation/widgets/drug_catalog_sheet.dart:126`; vùng `Expanded` ở dòng 167; CTA cố định tại `drug_selection_panel.dart:152`; matrix `drug_catalog_sheet_test.dart:243` | Sau khi host dành chỗ keyboard, sheet tiếp tục lấy 92% chiều cao còn lại và giữ header/CTA ngoài vùng cuộn. Tại 360×616 dp, font 1.5, keyboard 325.5 dp, list/review chỉ còn **21.34 dp**, thấp hơn một dòng metadata **35 dp**. Vùng xem lại bị cắt dù nút confirm đã bật. Cùng lỗi trong BUG-MEDPICK-28/51. | Task sửa sau cần bố trí lại phần header/CTA và vùng cuộn để đọc được metadata, thêm regression với inset thực tế và assert độ cao/khả năng đọc, chạy lại TC-28/51 trên Android. Trong thời gian hoãn sửa, cách tránh là đóng bàn phím hoặc giảm cỡ chữ; giữ hai case Fail và ngoại lệ trong PR. |

M1 đối chiếu trực tiếp với code và `test-android-large-regression-v2.log`, `test-pending-TC28-android-confirmed.log`: chọn đã có nhưng viewport không đủ đọc, không có chứng cứ sai object/id hoặc tự lưu. Phân loại Medium theo thang dự án vì có cách tránh; không tự nâng thành High chỉ vì một phần AC layout chưa đạt. Ngoại lệ đã được nêu rõ trước khi test được người duyệt approve: `evidence/test-layout-risk-acceptance.log`, frontmatter 05 (28/10/2026 10:40 +0700). Kết luận này dựa trên chấp nhận rủi ro cụ thể đó, không phải quy tắc cho qua mọi AC fail.

Hai lỗi family trong toàn suite là giới hạn baseline, không phải phát hiện mới của diff: `alert entry displays server unread count and removes it after clear` và lifecycle ổn định link code (không thấy PATIENT10X). `test-full-flutter.log` và `implement-baseline-family.log` cùng ghi nhận hai lỗi. Không che fail/skip hoặc sửa ngoài phạm vi.

## 5. Mô tả PR

Chỉ soạn nội dung để người dùng review; **chưa mở PR** và chưa có URL PR để liên kết. Khi tạo các PR, bổ sung liên kết hai chiều frontend ↔ docs ↔ superproject. Không tạo PR backend/contract/tests cho task này.

### Frontend

**Title:** `feat(medication): require explicit catalog selection confirmation`

**Body:**

Task 4.16 bổ sung bước chọn, xem lại và xác nhận thuốc dùng chung cho đầu vào OCR/mock và tìm danh mục. Trước đây chạm một kết quả đã trả thuốc về form; sau thay đổi, chạm chỉ chọn tạm và chỉ “Xác nhận thuốc” mới trả đúng catalog item. Hủy giữ nguyên form. No-result có đường tìm thủ công, dữ liệu thiếu được thể hiện trung thực. Thêm demo tổng hợp chỉ debug/preview; tìm kiếm production tiếp tục dùng controller/repository hiện có.

Validation: suite medication chạy lại ở review **172 pass** (`review-medication.log`), hash 13 file khớp test stage, diff-check sạch. Evidence trước: analyze sạch; full Flutter **830 pass / 1 skip / 2 fail có sẵn ở family**, đã đối chiếu baseline main. MEDPICK **50 Pass / 2 Fail / 0 Pending**; TC-28/51 là cùng một lỗi layout Medium đã được người dùng chấp nhận hoãn sửa, chưa khắc phục. AC1–AC9 đạt trong phạm vi mock; AC10/AC11 có ngoại lệ màn nhỏ/chữ lớn/keyboard.

Kiểm tay: chạy debug với `--dart-define=DRUGTIME_PREVIEW=true`; Thêm thuốc mới → “Mẫu · Xem thử chọn và xác nhận thuốc”. Đi bốn preset OCR/tìm kiếm có/rỗng; chọn/đổi/xem lại/confirm; thử Hủy/Back. Từ rỗng, chọn “Tìm kiếm thủ công”, nhập `Paracetamol`, chọn rồi xác nhận về caller; bản production chỉ đổi form sau confirm và chỉ lưu ở nút Lưu thuốc. Kiểm tên dài/cuộn/TalkBack. Lỗi đã biết: 360×616 dp, font 1.5 và keyboard 325.5 dp làm review còn 21.34 dp; đóng keyboard/giảm chữ để tránh. Không gọi đây là đã sửa hoặc release/OCR 4.13/search 4.15 được nghiệm thu.

Related PRs: bổ sung URL docs và superproject khi được yêu cầu tạo PR. Merge frontend và docs trước, rồi superproject.

### Docs

**Title:** `test(medication): update selection confirmation cases and known layout issue`

**Body:**

Task 4.16 cập nhật sheet MEDPICK và Report của `Test_Cases.xlsx`: giữ ID cũ, bổ sung case chọn/xác nhận/no-result, kết quả cuối **52 case: 50 Pass / 2 Fail / 0 Pending**. BUG-MEDPICK-28/51 cùng một nguyên nhân layout Medium, có ghi quyết định chấp nhận hoãn sửa; TalkBack Pass theo người dùng kiểm tay. 20 sheet chức năng không liên quan giữ nguyên so với docs HEAD.

Validation: `testcase_xlsx.py validate` exit 0; script review chỉ đọc đối chiếu cả workbook tổng/task với spec, actual/status/comments và hai dòng Bug Report. Build/merge/render evidence ở stage test; không sửa workbook trong review, chưa kiểm recalculation bằng native Excel. Related PRs: bổ sung URL frontend/superproject khi mở PR. Không đưa tài liệu/code ngoài task vào PR này.

### Superproject

**Title:** `chore: record task 4.16 review and merged submodule revisions`

**Body:**

Ghi artifact/evidence task 4.16 và cập nhật con trỏ frontend/docs sau khi các PR tương ứng được duyệt, merge và commit đích có trên remote. Task cung cấp UI chọn/xác nhận dùng chung và no-result trên mock; giữ ngoại lệ layout Medium được chấp nhận, MEDPICK 50 Pass/2 Fail, suite medication review 172 pass và giới hạn full-suite family có sẵn.

Kiểm lại gate/scope, commit artifact/spec/workbook/evidence cùng task; không stage scratch hoặc file backend fetchers ngoài task. `work/` đang bị ignore nên cần stage tường minh khi được yêu cầu commit. Không bump các con trỏ api_contract/backend/tests đang khác base chỉ vì chúng xuất hiện trong status. Related PRs: thêm URL frontend/docs trước khi mở/hoàn tất PR superproject. Nếu squash merge đổi SHA, dùng SHA đã merge trên main; chỉ bump tới commit đã push/kiểm chứng trên remote.

Thứ tự: frontend + docs → xác nhận SHA sau merge trên remote → superproject. Không có thay đổi contract/backend/integration-test cần merge cho task này.

## 6. Ghi chú cho quy trình

- Phiên này đã đọc 04/05 khi khảo sát tiến độ trước khi đọc đầy đủ wf-review; không đạt trình tự “chưa đọc phần tự thuật” của skill. Đã giảm rủi ro bị dẫn dắt bằng đọc toàn bộ diff/new file, kiểm lại yêu cầu/plan, chạy suite medication, đối chiếu trực tiếp workbook với base và log thô. Không gọi đây là review của một người khác; người review PR vẫn phải độc lập theo Definition of Done.
- Không chỉ dùng `origin/main...HEAD`: task chưa commit nên lệnh đó rỗng và không chứa bảy file untracked. Đã đọc working diff và toàn văn file mới; lưu bản chụp review để người tiếp tục đối chiếu.
- Nội dung 04/05 giữ các câu “draft/chờ duyệt” từ lúc kết thúc stage, trong khi frontmatter và gate hiện đã approved. Không sửa artifact đã duyệt; dùng gate/frontmatter và phần cập nhật cuối để xác định trạng thái. Các con số 45/1/6 ở phần lịch sử 05 không phải kết quả cuối 50/2/0.
- Sandbox chặn ghi `review-gate.log` lần đầu; đã chạy lại với escalation và có log gate hợp lệ trước review. Các lệnh ghi evidence/Flutter cache cần escalation; không đổi quyền/cấu hình máy hoặc sửa nguồn ngoài work.

## Bước tiếp theo

- Đang chờ: người duyệt review. Không có câu hỏi mở mới chặn review; ngoại lệ Medium được giữ như quyết định đã có.
- Đọc kết luận, M1 và mô tả PR, rồi tự chạy: `backend/.venv/Scripts/python.exe -X utf8 .agents/scripts/gate.py approve 4.16-selection-confirmation-screen review` nếu đồng ý. Agent không chạy approve hoặc ghi approval thay người duyệt.
- Sau khi review được duyệt, khi người dùng yêu cầu commit/push/mở PR thì dùng wf-git; commit/push frontend và docs trước, artifact/evidence và con trỏ đúng SHA sau. Chưa tạo commit/PR, chưa merge, chưa hoàn thành Definition of Done của PR.
- Lỗi M1 được hoãn sửa; chỉ mở lại implement/test nếu người dùng yêu cầu sửa sau này. Không đổi hai testcase Fail trước khi regression thực sự pass.
- Cập nhật lần cuối: 2026-10-28, Codex.
