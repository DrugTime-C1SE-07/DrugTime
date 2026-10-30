---
task: 4.09-mlkit-prototype
stage: review
status: approved
approved_by: Bao Nguyen
approved_at: 2026-10-29 17:14 +0700
content_hash: sha256:e0919214bceec11c
inputs:
  01-requirement.md: sha256:8a9ccb35212f46c2
  03-plan.md: sha256:6beeb0f93423efc9
  04-impl-notes.md: sha256:f9db3c1a907e8565
  05-test-report.md: sha256:635dcc9b4799485a
---

# 4.09 · Review prototype và kết luận hướng ML Kit

## 1. Kết luận

**Đạt, kèm lưu ý** trong phạm vi prototype Android, đo pilot và engineering GO. Không phát hiện Critical/High/Medium trong phần đã review. Có 1 Low L01 về diễn đạt README, cùng phát hiện được ghi ở review 4.08, không tính thành hai lỗi độc lập.

Kết luận dựa trên phạm vi người dùng vừa chốt và 05-test-report.md đã approved ngày 2026-10-29 16:53 +0700. Các kiểm manual chưa thực hiện giữ là giới hạn, không yêu cầu người dùng chạy thêm hoặc quét lại 49 ảnh. Không kết luận matching đúng, đạt benchmark ngưỡng đặt trước, sẵn sàng production hoặc đã đủ PR/reviewer của Definition of Done.

## 2. Phạm vi đã review

| Repo/phần | Lệnh hoặc cách đọc |
|---|---|
| Frontend | `git -C frontend diff main...HEAD`: 13 file, 1188 insertions/11 deletions; lưu `evidence/review-frontend-diff.log`, đọc lại các phần source/UI/store/lock riêng để tránh output bị cắt |
| Superproject | datasets untracked: đọc toàn bộ 6 Python files, README, dữ liệu thực; đối chiếu snapshot/49 raw/mapping/import-index/CSV/summary/decision |
| Docs | `git -C docs diff --stat`: chỉ Test_Cases.xlsx; đọc workbook ở chế độ read-only, so với spec/file task |
| Quy trình | 01 AC1–AC13, 03 file/checklist, 04/05 và raw log; 05 approved ghi chỉ dẫn mới về mức kiểm prototype |

Commit frontend hiện tại `281f9ff` có trong remote-tracking `origin/feat/mlkit-prototype-measurement` theo dữ liệu Git cục bộ; không fetch hay tuyên bố kiểm remote mới. Frontend không có uncommitted diff. Diff iOS rỗng. Docs nhánh `codex/4.09-ocr-testcases`, workbook chưa commit.

Scope implement: exit 1, **“CHẶN: 224 file ngoài phạm vi”**, `evidence/review-scope.log`. 6 file latest plan đều [OK]; ngoài phạm vi có labels/annotations/manifest của 4.08, baseline ảnh/raw/công cụ và .gitignore/api_contract/docs đã được người dùng cho giữ. Không sửa source/code/approved artifact trong review, không sửa scope hoặc xóa baseline để làm xanh. Gate review OK: `evidence/review-gate.log`.

Đây là review trong cùng hội thoại với implement, không thay một người khác approve PR theo Definition of Done.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1: native ML Kit adapter Android và pilot raw; AC2/11: run riêng, UTF-8/raw bytes/hash và import conflict; AC3/4: phân biệt lỗi/cancel, busy/generation/dispose và test fake; manual ngoài evidence giữ giới hạn theo 05 approved. AC5/9/10/12/13: reader B2, exact/token phụ, strength riêng, earliest run/device, CSV/JSON/Markdown. AC6: không API/cloud/catalog mutation trong prototype. AC7/8: engineering GO riêng với số liệu/hash/giới hạn, không tự sinh benchmark go |
| Phạm vi | Entrypoint prototype riêng, không nối route thêm thuốc/camera/DB/matching. Latest implement chỉ report/decision; code prototype và scripts kế thừa được đọc trong review này |
| Contract | Không endpoint/request/response backend đổi; JSON local schemaVersion=1, không dùng làm API contract |
| Bất biến kiến trúc | Không Supabase key/client direct DB, PEP/consent/dose/schema/interaction không bị tác động. Timestamp ghi +07:00 và timezone Asia/Ho_Chi_Minh |
| Bảo mật | Không thấy secret trong code diff; ID/path được ràng buộc, dataset path kiểm cả symlink, ADB subprocess dùng argv; CSV chống giá trị bắt đầu dấu công thức. Ảnh/raw chỉ cục bộ, exporter chia sẻ JSON theo thao tác tester |
| Xử lý lỗi | Picker/cancel/input/engine/save/export có trạng thái; không cho run mới khi kết quả chưa lưu. Import không overwrite raw conflict; malformed/unmapped/invalid/not_run hiện rõ. Khả năng native chưa kiểm đủ không bị đổi thành Pass |
| Hiệu năng | Đọc tuần tự phù hợp bộ pilot; timing chỉ engine theo từng thiết bị, median/p95 nearest-rank. Lịch sử UI load toàn bộ là giới hạn công cụ thử, chưa tối ưu thành tính năng sản phẩm |
| Chất lượng test | Đã đọc cả 3 Python test files và Flutter unit/widget/native fixture. Có đường lỗi/hash conflict/no_text/missing/selection/tamper; symlink có nhánh phụ thuộc quyền OS, native fixture có skip nếu thiếu input, đều không nhận là đã chạy đầy đủ |
| Dễ đọc/nhất quán | Adapter/controller/store tách biệt, dependency pinned; Android minSdk24 và lock yêu cầu Flutter>=3.47/Dart>=3.13 phải dùng khi tái hiện. README có Low L01 |
| Đối chiếu 04/05 với evidence | 41 unit (1.113s) và 5 host logs trước khớp; 13 Flutter trước có log +13. Lượt này validate testcase và kiểm hash/tái tính số liệu, không chạy lại unit/Flutter/native hoặc báo là test mới |

### Đối chiếu số liệu và nguồn

- `evidence/review-v1-crosscheck.log`: 49 ảnh/nhãn/annotations khớp; annotations SHA-256 và snapshot tính từ byte thật khớp manifest.
- Tái tính trong bộ nhớ từ raw hiện tại: exact27, partial5, token rời2, name_not_found14, no_text1; **27/49 = 55.1%**, coverage49/49, 0 lỗi dữ liệu; scores/selected_counts/snapshot khớp summary và CSV.
- 49 raw SHA-256 khớp cả decision và import-index; hash report/summary khớp decision. Không sửa raw hoặc nguồn để đạt số liệu.
- Engineering decision=go riêng, automatic pilot=not_decided. Không cộng partial hoặc chuỗi tên ngắn thành accuracy matching. Median2615/p95 5267ms, n49 từ emulator, không suy tốc độ điện thoại.
- `testcase_xlsx.py validate` exit0: `evidence/review-testcase-validation.log`. 56 case riêng:47 Pass/0 Fail/9 Pending; master64 case:53 Pass/0 Fail/11 Pending, khớp spec và workbook riêng. Các actual Pass có nguồn log; Pending không được giả thành Pass. Không phát hiện test Fail bị bỏ khỏi báo cáo.

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Low · L01, dùng chung 4.08 | datasets/README.md:11; datasets/README.md:17 | Cách nói cũ về “Còn cần ... native/manual” và “chưa ... kết luận go/no-go” có thể khiến người nhận hiểu rằng chưa chốt GO hoặc phải kiểm mở rộng trước bàn giao. Trong khi 05 approved mới ghi rõ giới hạn được chấp nhận và engineering GO đã có | Khi cập nhật tài liệu bàn giao, tách chưa kiểm khỏi điều kiện chốt prototype; ghi đã GO kỹ thuật và chưa có benchmark frozen. Hiện dùng 05 approved và decision.json làm nguồn trạng thái. Không thay số liệu/hash hoặc đổi Pending thành Pass |

Không có Critical/High cần reopen implement. Không sửa code hoặc file dữ liệu trong review. Các nhóm `product` trong công cụ là nhóm folder như plan; khi cần accuracy theo thương hiệu, dùng drug_name từ labels/CSV, không coi folder cùng hoạt chất là cùng sản phẩm.

## 5. Mô tả PR

Đã soạn, chưa mở PR:

- `pr-description-frontend.md`: prototype Android từ nhánh feat/mlkit-prototype-measurement.
- `pr-description-docs.md`: workbook chung Packaging Dataset/OCR Prototype/OCR Dataset.
- `pr-description-superproject.md`: datasets dùng chung 4.08/4.09 và artifact/evidence; con trỏ chỉ bump tới commit đã push hoặc SHA đã merge.

Thứ tự đề xuất khi được yêu cầu: frontend (nếu chưa merge) → docs → superproject. Không có API contract/backend PR cho scope này. Nếu squash/rebase merge đổi SHA, cập nhật con trỏ trước merge PR superproject. Không stage các con trỏ .agents/backend/api_contract hoặc .gitignore ngoài task.

## 6. Ghi chú cho quy trình

- Phạm vi kiểm được người dùng thu hẹp và duyệt trong 05; không tự yêu cầu native manual/điện thoại thật/benchmark ngưỡng mới chỉ để chốt prototype.
- Review cùng hội thoại có nguy cơ thiên lệch vì đã biết tự thuật implement; đã đối chiếu source/diff/hash/log thay vì nhận mô tả là bằng chứng. Vẫn cần một người khác approve PR.
- Latest plan không còn liệt kê lại code prototype đã commit; review đọc cả diff main...HEAD để không bỏ phần code kế thừa. Datasets untracked được đọc trực tiếp, không bỏ qua vì git diff không hiện.
- Không sửa approved artifact hay metadata để làm gate thông qua; không mở PR/merge khi chưa được yêu cầu.

## Bước tiếp theo

- Chờ người duyệt đọc kết luận/lưu ý và chạy `python .agents/scripts/gate.py approve 4.09-mlkit-prototype review`.
- Sau duyệt, sẵn sàng commit/push/mở PR khi người dùng yêu cầu; giữ hai nhánh superproject/frontend hiện tại. Không giao thêm việc quét ảnh hoặc manual mở rộng.
- Cập nhật: 2026-10-29, Codex.
