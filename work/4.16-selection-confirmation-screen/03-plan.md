---
task: 4.16-selection-confirmation-screen
stage: plan
status: approved
approved_by: phucnguyenngoc
approved_at: 2026-10-26 20:18 +0700
content_hash: sha256:5eee2adbfe7e1076
inputs:
  01-requirement.md: sha256:68d21d09eefdb715
---

# 4.16 · Plan chọn, xác nhận thuốc và không có kết quả

## 1. Giải pháp

### Luồng và thành phần

Giữ `DrugCatalogItem` hiện có làm đầu vào/đầu ra nội bộ UI. Không tạo DTO/API OCR, điểm confidence hoặc repository mới cho production.

1. `DrugSelectionPanel` là vùng chọn/xem lại dùng chung: nhận danh sách ứng viên, nguồn OCR/tìm kiếm, callback xác nhận và callback tìm thủ công. Hiển thị thứ tự đầu vào; mỗi dòng có tên, hoạt chất, hàm lượng, dạng bào chế, đơn vị khi có. Chỉ chọn một dòng, dùng radio/selected semantics và viền + dấu chọn; không biểu thị chỉ bằng màu.
2. Chạm dòng chỉ cập nhật lựa chọn cục bộ. Vùng “Thông tin thuốc đã chọn” hiển thị dữ liệu chỉ đọc và nhắc kiểm tra; nút “Xác nhận thuốc” chỉ bật khi mục vẫn thuộc danh sách hiện tại. Người dùng đổi bằng cách chạm dòng khác. Xác nhận trả đúng đối tượng hiện hành, không dựng lại đối tượng từ chuỗi hiển thị.
3. Khi danh sách đầu vào được thay thế, xóa lựa chọn, kể cả ID cũ xuất hiện với metadata mới; cần chọn lại. Trong sheet, bắt đầu query/loading/error cũng hủy lựa chọn. Trước gọi callback xác nhận phải kiểm tra lại lựa chọn hiện hành và chặn double tap; mỗi lần mở chỉ trả một kết quả.
4. `DrugSelectionScreen` bọc panel trong màn toàn màn hình cho nguồn OCR/mock và nơi cần trình bày tập ứng viên sẵn có. Hàm mở màn trả `Future<DrugCatalogItem?>`; nhận hàm tìm danh mục được truyền tường minh. Không phụ thuộc vào ảnh/văn bản OCR hoặc module lưu lịch. Back/Hủy trả null. Khi tìm thủ công trả null, quay lại màn gốc; khi xác nhận trong tìm thủ công, chuyển đúng kết quả qua màn gốc về caller một lần.
5. `DrugCatalogSheet` tiếp tục sở hữu ô tìm, debounce 300ms, giới hạn 100 Unicode rune, generation chống kết quả về muộn, loading/error/retry và nguồn `_controller.searchCatalog`. Thay danh sách chọn-trả-ngay bằng panel chung. Cho phép truyền hàm tìm và hàm kiểm tra “Đang dùng” vào helper/widget; chỉ đọc `MedicationScope` khi chưa được truyền dependency đó. Demo truyền đủ dependency nên không cần repository/mạng thật; caller hiện tại không truyền vẫn dùng controller cũ.
6. No-result của panel có “Không tìm thấy thuốc phù hợp”, hướng dẫn và nút “Tìm kiếm thủ công”. Từ màn OCR mở sheet với hàm tìm được truyền. Trong sheet tìm thủ công, nút chỉ focus/chọn nội dung ô tìm hiện có để sửa từ khóa, không mở sheet lồng thêm. Không có nút xác nhận khả dụng khi rỗng.
7. `DrugSelectionDemoScreen` cung cấp bốn preset chính: OCR có kết quả/rỗng, tìm kiếm có kết quả/rỗng; thêm mẫu thiếu dữ liệu, tên dài và danh sách dài. Cả hai nguồn mở cùng `DrugSelectionScreen` và tìm thủ công dùng cùng `DrugCatalogSheet`. Fixture tổng hợp trong bộ nhớ, không ảnh/người bệnh, không network/storage; kết quả chỉ hiện tại demo, không gọi thêm thuốc/lưu lịch.
8. Route demo `/medications/selection-demo` chỉ mở khi `preview && kDebugMode`; route production phải từ chối, kể cả gọi trực tiếp. Từ `AddMedicationScreen` chỉ có liên kết xem demo trong preview; nguồn production vẫn qua `_pickDrug → showDrugCatalogSheet → confirmed item`. Giữ nguyên form nếu hủy; chỉ cập nhật `_drug` sau xác nhận, giữ bước nhập/kiểm tra liều, tần suất, giờ và Lưu thuốc như cũ.

Không thêm state controller/domain abstraction riêng: trạng thái chọn chỉ sống trong panel và không lưu bền vững. Hai host (screen/sheet) tái sử dụng panel để không lặp quy tắc chọn–xem lại–xác nhận. Không thay màn tìm danh mục production bằng dữ liệu mock.

### Đối chiếu Figma và quyết định UI

Đã đọc trực tiếp bằng Reqwise Figma MCP: file **Prototype_DrugTime**, page **Page 1**; đã xem screenshot S07c. Không tạo/sửa canvas.

| Nguồn Figma | Dữ kiện | Áp dụng cho 4.16 |
|---|---|---|
| `S07c · Xác nhận thông tin quét`, `51:5431` | Khung 375×812, header “Xác nhận thông tin”, vùng xem lại, lời nhắc kiểm tra, CTA “Tiếp tục thiết lập lịch uống” về S07. Nền #FCFCFC, CTA #01554F, field #E7F3F1, radius 12. | Giữ trình tự xem lại → xác nhận → form lịch, màu và góc bo theo theme. Dùng “Xác nhận thuốc” để phân biệt thao tác chọn danh mục với lưu lịch. |
| Cùng frame, `51:5470`, `51:5480`, `51:5489`, `51:5498` | Có ảnh/Chụp lại, bút sửa tên/hàm lượng, hạn sử dụng và số lượng. | Chỉ tham khảo hình thức; không thêm những chức năng/field ngoài requirement. Danh tính/hàm lượng chỉ đọc; đổi bằng chọn lại ứng viên hợp lệ. Không thông báo đã nhận diện ảnh khi đang dùng tìm kiếm/mock chưa có ảnh thật. |
| `S07 · Thêm thuốc mới`, `33:4419` | Picker danh mục, hàm lượng tự điền, lượng dùng/tần suất/giờ và Lưu thuốc tách biệt. | Caller sở hữu form sử dụng; xác nhận danh mục không tự lưu. |
| `S06a · Danh mục thuốc (tra cứu)`, `140:2` | Metadata là frame tra cứu; tên không chứng minh đây là màn xác nhận riêng. | Giữ picker hiện có của Flutter; không tự chuyển chức năng của màn quản lý thuốc sang màn chọn. |

Trong cây cấp một của Page 1 (46 phần tử) và nhóm S07 (4 frame), chưa thấy frame riêng cho danh sách ứng viên/no-result. Đây là phần UI đề xuất theo AC, không tuyên bố đã có thiết kế Figma tương ứng. Không cần đổi nghiệp vụ/AC để triển khai phần còn thiếu.

Độ đo Figma là tham khảo: tái sử dụng `AppColors`, `AppSpacing`, `AppRadius`, `AppTextStyles` và `AppSizes` hiện có; không tạo theme mới. Chữ tối thiểu 14, vùng chạm tối thiểu 48, CTA tối thiểu 56 theo theme; nội dung cuộn được, không khóa chiều cao theo frame 812. SafeArea và keyboard inset do Flutter quản lý; không vẽ status/home indicator thủ công. Vùng xem lại cùng danh sách nằm trong vùng cuộn; thanh xác nhận nằm ngoài vùng cuộn nhưng phải thu xếp được trên màn nhỏ/phóng chữ, nút có thể tăng chiều cao/wrap.

Audit S07c phát hiện 2 lỗi của cùng node home indicator thừa `51:5517` (vượt bounds và bị clip), và 1 gợi ý gom 7 cỡ chữ. Không sao chép các lỗi này vào Flutter; không sửa Figma ngoài yêu cầu. Bằng chứng và phạm vi đọc tại `evidence/plan-figma-notes.md`. Audit cấu trúc không xác minh đúng nghiệp vụ.

### Dữ liệu thiếu và tính nhất quán

- Các chuỗi tùy chọn rỗng/whitespace hiển thị “Chưa có thông tin” tại vùng xem lại; không hiển thị null, không điền giá trị y tế giả. Hàng danh sách có thể lược trường thiếu nhưng vùng xem lại phải cho thấy trường nào thiếu.
- `DrugCatalogItem.unit` hiện mặc định “viên”. UI chỉ hiển thị giá trị được truyền; fixture thiếu đơn vị phải truyền `unit: ''` tường minh, không sửa default entity/mapper trong task này. Chưa chứng minh đơn vị từ nguồn thật luôn được xác minh; đây là giới hạn đầu vào, không thực hiện chuyển đổi.
- Không chỉnh sửa tên/hàm lượng độc lập với ID; không tự chọn mục đầu, xếp hạng, tính score, hoặc xác nhận mục cũ sau refresh.
- Form trước đó chỉ nhận dữ liệu sau xác nhận; hủy/Back/dismiss sheet không sửa form và không gọi lưu.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/4.16-selection-confirmation-screen/01-requirement.md` | Approved; size M, contract_change no; AC1–AC11, mock trước/tích hợp thật sau 4.13/4.15. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md`, quy ước trạng thái và mục 2, 3, 14, 16 | QD-38/39/45 giữ trạng thái ✅: chốt baseline `QD-2026-10-03-v1`, chưa coi là đã triển khai hoặc Mentor ký. Quy đổi, ảnh thật, bản nháp/yêu cầu bổ sung ở ngoài task theo 01; không dùng plan mở rộng các phần này. |
| `frontend/mobile/lib/features/medication/domain/entities/medication.dart` | Tái sử dụng `DrugCatalogItem`; chuỗi bắt buộc có thể rỗng, unit có default, không thêm DTO matching. |
| `frontend/mobile/lib/features/medication/presentation/widgets/drug_catalog_sheet.dart` | Debounce/generation/error đã có; onTap đang pop ngay. Chuyển điểm pop sang confirm; bổ sung dependency injection cho mock và focus no-result. |
| `frontend/mobile/lib/features/medication/presentation/screens/add_medication_screen.dart` | `_pickDrug` đã return khi null; form riêng và Lưu thuốc riêng. Chỉ thêm entry demo có gate preview, không đổi nghiệp vụ lưu. |
| `frontend/mobile/lib/features/medication/presentation/state/medication_controller.dart` | `searchCatalog` và `isInUse` có sẵn; giữ controller/repository production. |
| `frontend/mobile/lib/features/medication/data/repositories/in_memory_medication_repository.dart` | Có nguồn mẫu, nhưng fixture mới riêng cho các tình huống 4.16 để không sửa seed dùng chung. |
| `frontend/mobile/lib/app/router.dart` | Có tham số `preview`; chưa có route chọn/OCR. Thêm duy nhất route demo, screen chung được mở bằng typed helper. |
| `frontend/mobile/lib/app/app_preview_session.dart`; `frontend/mobile/lib/app/adherence_demo_app.dart`; `frontend/mobile/lib/core/preview/app_preview_scope.dart`; `frontend/mobile/lib/core/config/app_config.dart` | Preview dùng dependency bộ nhớ, có scope/badge; AppConfig chỉ cho debug bật preview. Scope chỉ là ngữ cảnh trình bày, không dùng làm quyết định chọn repository hay phân quyền. Route demo vẫn phải có gate riêng. |
| `frontend/mobile/lib/app/theme/app_theme.dart` | Token đã có, tối thiểu chữ 14 và vùng chạm 48/CTA 56; không cần sửa theme. |
| `frontend/mobile/test/features/medication/drug_catalog_sheet_test.dart` | Có Completer để test request về muộn/error/dispose; giữ các case debounce/generation, bổ sung confirmation/no-result. |
| `frontend/mobile/test/features/medication/medication_lookup_widget_test.dart`; `frontend/mobile/test/features/medication/medication_screens_test.dart` | Có test trạng thái tìm và helper chọn thuốc; điều chỉnh thao tác để xác nhận rõ rồi mới kiểm form/lưu. Giữ assertions nghiệp vụ trước đó. |
| `.agents/templates/03-plan.md`; `.agents/scripts/scope.py`; `.agents/skills/wf-plan/SKILL.md`; `.agents/skills/wf-git/SKILL.md` | Bảng file là phạm vi cho implement. Giai đoạn test chỉ chạy lại widget suite và nghiệm thu, không dời việc viết Flutter test ra giai đoạn test. |

### Quyết định nghiệp vụ áp dụng

| Quy tắc / mục nguồn, trạng thái | AC | Checklist | Test |
|---|---|---|---|
| QD-39, mục 3: OCR/nhập tay phải kiểm tra trước tạo lịch, ✅ | AC1, AC3, AC4, AC9 | P1, P2, P3, P5 | T1, T3–T5, T14, T15 |
| QD-39, mục 3: chỉ thuốc danh mục, không gán gần giống, ✅ | AC2, AC5–AC7 | P1–P4 | T2, T6–T9, T16 |
| QD-39, mục 3: không Admin duyệt OCR, ✅ | AC6 | P3, P4 | T7, T8, T16 |
| QD-39, mục 3: vòng đời ảnh/văn bản, ✅ | AC9 | P4 | T13, T16; task này không tạo ảnh/văn bản thật hay storage, không nghiệm thu xóa/mã hóa OCR thật |
| QD-38, mục 2: tách hàm lượng/lượng dùng, không tự quy đổi, ✅ | AC2, AC8, AC9 | P1, P4, P5 | T2, T10, T14, T15 |
| QD-45, mục 14/16: contract/backlog chuẩn, ✅ | AC9 | P3, P4, P6 | T13, T16; không phát sinh endpoint/schema; tích hợp sau phải đối chiếu contract được duyệt |

Không thay endpoint dữ liệu sức khỏe/PEP, consent, lịch/liều, schema hay dependency module backend; không cần wf-health-endpoint/wf-db-migration. Không có API engineering hoặc Postman artifact trong phạm vi UI mock này.

## 3. File sẽ thay đổi (ranh giới phạm vi)

Đường dẫn tính từ gốc submodule. 13 file frontend: 7 thêm mới, 6 sửa. Workbook docs chỉ cập nhật ở cuối giai đoạn test theo wf-testcase; không sửa docs ở plan/implement.

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `mobile/lib/features/medication/presentation/widgets/drug_selection_panel.dart` | Thêm | Panel, enum nguồn, chọn/xem lại/xác nhận/no-result dùng chung. |
| frontend | `mobile/lib/features/medication/presentation/screens/drug_selection_screen.dart` | Thêm | Host typed result và điều phối tìm thủ công về caller ban đầu. |
| frontend | `mobile/lib/features/medication/presentation/widgets/drug_catalog_sheet.dart` | Sửa | Dùng panel, confirm thay onTap pop; injected search, focus no-result và reset lựa chọn. |
| frontend | `mobile/lib/features/medication/data/models/drug_selection_demo_fixtures.dart` | Thêm | Fixture tổng hợp, lookup bộ nhớ, tập rỗng/thiếu/dài cho demo. |
| frontend | `mobile/lib/features/medication/presentation/screens/drug_selection_demo_screen.dart` | Thêm | Launcher bốn preset và kết quả demo chỉ trong phiên. |
| frontend | `mobile/lib/app/router.dart` | Sửa | Khai báo route demo, gate preview/debug và từ chối ở production. |
| frontend | `mobile/lib/features/medication/presentation/screens/add_medication_screen.dart` | Sửa | Entry xem thử chỉ trong preview; giữ typed selection và form hiện tại. |
| frontend | `mobile/test/features/medication/drug_selection_panel_test.dart` | Thêm | Test chọn, đổi, thiếu dữ liệu, refresh, accessibility/bố cục. |
| frontend | `mobile/test/features/medication/drug_selection_flow_test.dart` | Thêm | Test hai nguồn, confirm/cancel/Back và manual-search trả về caller. |
| frontend | `mobile/test/features/medication/drug_selection_demo_test.dart` | Thêm | Test preset, route gate và không network/lưu từ demo. |
| frontend | `mobile/test/features/medication/drug_catalog_sheet_test.dart` | Sửa | Phủ confirm/no-result, bảo toàn debounce/generation/error. |
| frontend | `mobile/test/features/medication/medication_lookup_widget_test.dart` | Sửa | Điều chỉnh tương tác chọn/nhãn cần thiết, giữ hồi quy tìm kiếm. |
| frontend | `mobile/test/features/medication/medication_screens_test.dart` | Sửa | Helper chờ xác nhận, form không đổi khi hủy và chỉ lưu khi bấm Lưu. |
| docs | `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` | Sửa (giai đoạn test) | Merge test case vào workbook theo vai trò testcase-book trong AGENTS.md. |

Artifact `03`, `04`, `05`, spec `testcases.json`, workbook task và evidence nằm trong `work/4.16-selection-confirmation-screen/`; không ghi task vào docs. Không sửa entity, mapper, repository/controller production, API contract, .agents hay theme. Nếu cần thêm file ngoài bảng thì ghi Phát sinh và xin mở rộng phạm vi trước khi sửa.

## 4. Checklist

- [ ] P1 [frontend] Tạo panel với dữ liệu chỉ đọc, thứ tự đầu vào, chọn một/đổi chọn/xem lại, reset khi danh sách đổi, confirm một lần và no-result callback — file: `mobile/lib/features/medication/presentation/widgets/drug_selection_panel.dart`, `mobile/test/features/medication/drug_selection_panel_test.dart` — AC: AC1–AC4, AC7, AC8, AC10 — xong khi T1–T4, T9–T12 pass, trước confirm callback chưa được gọi, không có overflow/semantics thiếu nhãn.
- [ ] P2 [frontend] Tạo screen/typed helper, Back/Hủy và chuyển kết quả tìm thủ công về caller một lần; unmounted/dispose không pop sai route — file: `mobile/lib/features/medication/presentation/screens/drug_selection_screen.dart`, `mobile/test/features/medication/drug_selection_flow_test.dart` — AC: AC1, AC3–AC6, AC9 — xong khi T5, T6, T8 pass cho cả hai nguồn, hủy sheet vẫn có đường quay lại/hủy màn gốc.
- [ ] P3 [frontend] Nhúng panel vào sheet, thêm dependency injection và TextEditingController/FocusNode; giữ debounce/generation/error/retry/limit, no-result focus lại field, hủy lựa chọn ngay khi query đổi — file: `mobile/lib/features/medication/presentation/widgets/drug_catalog_sheet.dart`, `mobile/test/features/medication/drug_catalog_sheet_test.dart`, `mobile/test/features/medication/medication_lookup_widget_test.dart` — AC: AC1–AC8, AC10 — xong khi T7, T8, T10–T12, T17–T20 pass, tap dòng không đóng sheet.
- [ ] P4 [frontend] Thêm fixture và demo bốn preset; route chỉ preview/debug, dữ liệu mock không thay repository production; entry preview và kết quả hiển thị có nhãn Mẫu — file: `mobile/lib/features/medication/data/models/drug_selection_demo_fixtures.dart`, `mobile/lib/features/medication/presentation/screens/drug_selection_demo_screen.dart`, `mobile/lib/app/router.dart`, `mobile/lib/features/medication/presentation/screens/add_medication_screen.dart`, `mobile/test/features/medication/drug_selection_demo_test.dart` — AC: AC1, AC5, AC6, AC8, AC9 — xong khi T13, T16 pass; mở từng preset bằng app preview được, không fake chức năng camera/OCR/lưu lịch.
- [ ] P5 [frontend] Cập nhật helper test form để phải bấm Xác nhận thuốc, thêm spy kiểm không lưu từ chọn và giữ form khi hủy — file: `mobile/test/features/medication/medication_screens_test.dart`, `mobile/test/features/medication/medication_lookup_widget_test.dart` — AC: AC3, AC4, AC9 — xong khi T14, T15 pass, chỉ nút Lưu thuốc mới gọi lưu, các kiểm tra liều/giờ và cảnh báo đã dùng giữ đúng.
- [ ] P6 [frontend + work] Chạy format/analyze, test medication rồi toàn suite; lưu output và kiểm scope implement, cập nhật `04-impl-notes.md` từng P, không ghi pass cho bước chưa chạy — file: các Dart file ở bảng, artifact/evidence của task — AC: AC1–AC10 — xong khi lệnh phù hợp đều có log, lỗi tồn tại trước phân biệt được, không file ngoài phạm vi.
- [ ] P7 [work + docs, giai đoạn test sau duyệt 04] Chạy lại suite và kiểm Android theo T21/T22; đối chiếu màn với S07c trong giới hạn đã nêu, lập Excel theo wf-testcase (validate/build/merge), ghi `05-test-report.md` — file: artifact/evidence task, `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` — AC: AC1–AC11 — xong khi từng AC có kết quả/evidence, AC11 chỉ Pass sau thao tác thiết bị thực tế, Pending ghi rõ; không coi test mock là tích hợp backend/OCR thật.

## 5. Test

Tất cả test tự động dưới đây là unit/widget/flow với fake trong Flutter, không phải integration xuyên service. Viết trong implement (P1–P5). Giai đoạn test chạy lại và nghiệm thu thủ công.

### Unit/widget/flow

| ID / tên dự kiến | AC | File trong frontend |
|---|---|---|
| T1 `same_panel_for_ocr_and_search` | AC1 | `mobile/test/features/medication/drug_selection_flow_test.dart` |
| T2 `preserves_candidate_order_and_identity_with_similar_names` | AC2 | `mobile/test/features/medication/drug_selection_panel_test.dart` |
| T3 `tap_only_selects_confirm_returns_current_item_once` | AC3 | `mobile/test/features/medication/drug_selection_panel_test.dart` |
| T4 `changing_selection_returns_only_latest_item` | AC4 | `mobile/test/features/medication/drug_selection_panel_test.dart` |
| T5 `cancel_and_system_back_return_null` | AC4 | `mobile/test/features/medication/drug_selection_flow_test.dart` |
| T6 `ocr_empty_manual_search_confirmation_reaches_original_caller` | AC5 | `mobile/test/features/medication/drug_selection_flow_test.dart` |
| T7 `search_empty_action_focuses_editable_query_without_new_route` | AC6 | `mobile/test/features/medication/drug_catalog_sheet_test.dart` |
| T8 `cancel_manual_search_and_repeated_no_result_allow_retry_or_exit` | AC5, AC6 | `mobile/test/features/medication/drug_selection_flow_test.dart` |
| T9 `replacement_empty_or_same_id_changed_data_clears_selection` | AC7 | `mobile/test/features/medication/drug_selection_panel_test.dart` |
| T10 `missing_optional_fields_show_unknown_without_fabrication` | AC8 | `mobile/test/features/medication/drug_selection_panel_test.dart` |
| T11 `long_list_long_names_small_view_and_text_scale_remain_usable` | AC10 | `mobile/test/features/medication/drug_selection_panel_test.dart` |
| T12 `keyboard_and_semantics_keep_selection_and_confirm_accessible` | AC10 | `mobile/test/features/medication/drug_catalog_sheet_test.dart` |
| T13 `four_demo_presets_run_offline_without_save_or_external_dependencies` | AC1, AC5, AC6, AC9 | `mobile/test/features/medication/drug_selection_demo_test.dart` |
| T14 `form_changes_only_after_confirm_and_stays_intact_on_cancel` | AC3, AC4, AC9 | `mobile/test/features/medication/medication_screens_test.dart` |
| T15 `selection_never_saves_and_existing_schedule_validation_still_applies` | AC9 | `mobile/test/features/medication/medication_screens_test.dart` |
| T16 `demo_route_requires_preview_and_debug_with_no_production_mock_fallback` | AC6, AC9 | `mobile/test/features/medication/drug_selection_demo_test.dart` |
| T17 `debounce_299_300ms_and_trimmed_query_unchanged` (giữ case hiện có) | AC9 | `mobile/test/features/medication/drug_catalog_sheet_test.dart` |
| T18 `stale_A_B_A_success_or_error_never_restores_old_selection` | AC7 | `mobile/test/features/medication/drug_catalog_sheet_test.dart` |
| T19 `clear_dispose_error_retry_and_unauthorized_remain_distinct` | AC6, AC7, AC9 | `mobile/test/features/medication/drug_catalog_sheet_test.dart` |
| T20 `query_unicode_limits_99_100_101_and_whitespace` | AC6, AC9 | `mobile/test/features/medication/drug_catalog_sheet_test.dart` |

T11/T12 dùng ít nhất 320×568 và 375×812, text scale 1.0/1.5/2.0, inset bàn phím giả lập, danh sách dài và tên nhiều dòng. Assert thao tác chọn/xem lại/confirm thực hiện được, `tester.takeException()` rỗng và semantics có nhãn/selected/enabled; không chỉ snapshot màu.

T13/T15 dùng fake/spy cho tìm và lưu, chặn HTTP ngoài dự kiến; fake tìm trả fixture, spy lưu phải bằng 0 trong toàn bộ demo/chọn/tìm lại/xác nhận/hủy. T16 kiểm cả route preview hợp lệ và route production từ chối khi caller truyền trực tiếp; kiểm cấu hình release/debug theo cơ chế gate được viết, không coi preview badge là gate.

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Không thêm integration xuyên backend/PostgreSQL/OCR | Không AC nào ở mức integration | Không endpoint/schema/PEP/consent/liều/module boundary thay đổi. Không phát sinh cross-patient, race liều hoặc interaction scenario mới cho task này. Không tạo integration giả bằng cách đổi tên widget test. |

### Thủ công

| ID | Cách kiểm | AC / evidence |
|---|---|---|
| T21 | Android device/emulator: từ entry preview chạy OCR có kết quả/rỗng, search có kết quả/rỗng; chọn/đổi/xem lại/confirm; Back ở màn gốc và sheet; không kết quả → gõ lại → chọn → confirm về caller. Đối chiếu chữ Việt, phân biệt chọn/xác nhận, mục đang chọn và chạm/cuộn/keyboard. | AC11; log phiên bản app, thiết bị, bước thực tế và kết quả tại `evidence/test-manual-selection.log`. |
| T22 | Android màn nhỏ/phóng chữ: mở bàn phím, tên dài, danh sách dài, cuộn tới ứng viên cuối/xem lại/confirm; đọc bằng TalkBack nếu sẵn có, ghi rõ phần chưa kiểm. | AC10, AC11; cùng log, ảnh nếu có. |

Nếu chưa có thiết bị/emulator thì T21/T22 và AC11 là Pending, chưa đủ nghiệm thu thủ công; không suy ra từ widget test.

### Lệnh kiểm dự kiến

Trong `frontend/mobile`, lưu toàn bộ output vào evidence task:

- `dart format --output=none --set-exit-if-changed <các file Dart đã sửa>` sau khi format.
- `flutter analyze`.
- `flutter test test/features/medication`.
- `flutter test` sau khi suite mục tiêu pass, nhằm phát hiện route/preview hoặc caller khác bị ảnh hưởng.
- `flutter run --dart-define=DRUGTIME_PREVIEW=true -d <android-device-id>` cho T21/T22; ID lấy từ `flutter devices`, không tự đoán.
- Ở gốc: `python .agents/scripts/scope.py 4.16-selection-confirmation-screen --stage implement` / `--stage test` đúng thời điểm.

Giai đoạn test dùng wf-testcase: đọc workbook tổng để giữ mã/ID case đã có; mọi case chưa chạy là Pending; `validate`, `build`, `merge` và lưu `evidence/testcase-xlsx.log`. Không tự sửa .xlsx ngoài script. Xung đột kết quả tester cập nhật tay phải hỏi theo skill. Chưa chạy các lệnh Flutter/Excel trong giai đoạn plan này.

## 6. Migration

Không có. Không sửa schema, API contract hoặc backend.

## 7. Nhánh git

Áp dụng wf-git, chưa tạo/chuyển nhánh trong plan. Trạng thái đã đọc: superproject và frontend đều trên `test/3.25-family-adherence-history-tests`; frontend không có file chưa commit trong output status, superproject có con trỏ backend/docs/frontend khác baseline. Không quy các con trỏ đó cho task 4.16.

| Submodule | Nhánh |
|---|---|
| superproject | `feat/4.16-selection-confirmation-screen` |
| frontend | `feat/4.16-selection-confirmation-screen` |
| docs (cuối giai đoạn test) | `feat/4.16-selection-confirmation-screen` |

Trước implement: kiểm lại status/branch/base và nhánh task sẵn có; chọn base main chứa dependency cần thiết, không kéo commit 3.25 chưa merge vào task 4.16. Nếu code cần thiết chỉ có ở nhánh khác, báo dependency trước khi chuyển; không reset/stash thay đổi của người khác. Chuẩn bị nhánh docs trước merge workbook. Chỉ commit/push khi người dùng yêu cầu, submodule trước rồi con trỏ superproject sau; không bump tới commit chưa push.

## 8. Rủi ro

- Thiết kế Figma cũ cho sửa field OCR, trong khi requirement cần giữ đúng catalog ID: dùng field chỉ đọc và đổi lựa chọn, ghi rõ phần UI bổ sung; không biến OCR text thành thuốc hợp lệ.
- Chọn cũ tồn tại sau query/refresh: reset theo phiên dữ liệu, kiểm lại trước confirm, T9/T18 chặn metadata cũ cùng ID và request về muộn.
- Hai tầng route tìm thủ công trả kết quả hai lần hoặc pop nhầm khi unmounted: typed result, kiểm mounted và khóa confirm, T3/T5/T6/T8.
- Scope/keyboard: panel trong sheet có chiều cao hạn chế; ListView/summary cuộn, SafeArea và inset, T11/T12/T22. Không sao chép indicator bị clip hay chữ 11.5 từ Figma.
- Default unit của entity có thể che dữ liệu thiếu: fixture truyền rỗng tường minh, UI không suy luận. Việc xác minh/chuẩn hóa đầu vào thật thuộc tích hợp sau.
- Demo lọt vào production: gate route preview + debug, không dựa vào badge/scope để đổi nguồn; T13/T16 và kiểm nguồn production vẫn qua controller.
- Chưa có tích hợp thật 4.13/4.15: kết quả task chỉ chứng minh UI mock và hồi quy picker hiện tại. Không gọi đây là nghiệm thu OCR/search backend.
- Chưa có bằng chứng Android: AC11 vẫn cần thực thi khi test. Widget test không chứng minh đầy đủ bàn phím/chạm thiết bị.

## 9. Câu hỏi mở

Không có câu hỏi chặn plan. Bố cục chọn/xem lại trong cùng panel là lựa chọn UI được 01 cho phép; no-result được mô tả theo AC vì chưa thấy frame riêng. Nếu cần sửa field OCR/hạn sử dụng/ảnh thật giống toàn bộ S07c, phải mở lại requirement; không đưa vào implement theo plan này.

## 10. Phát sinh

- `python` mặc định là WindowsApps không chạy được; đã dùng `C:/Users/admin/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe -X utf8`, không đổi cấu hình máy.
- Kết nối Reqwise ban đầu trả NOT_CONNECTED; sau khi người dùng mở plugin đã đọc canvas và screenshot thành công.
- Git status cảnh báo quyền đọc global ignore và .pytest_cache; không thay cấu hình Git/quyền thư mục. Scope script đã chạy riêng và không phát hiện file ngoài work.
- Tee-Object không ghi được log mới trong sandbox; dùng apply_patch lưu nguyên output lệnh đã chạy trong phiên vào evidence, không bỏ kiểm tra hoặc yêu cầu đổi quyền.

## Bằng chứng kiểm tra

- `evidence/plan-gate.log`: gate plan cho phép bắt đầu.
- `evidence/plan-scope-baseline.log`: scope trước ghi plan, không có file ngoài work.
- `evidence/plan-scope.log`: scope sau ghi plan, không có file ngoài work.
- `evidence/plan-figma-notes.md`: dữ kiện Figma, phạm vi đã đọc, vấn đề audit và cách áp dụng.
- Đây là kết quả gate/scope/đọc thiết kế, không phải kết quả Flutter test.

## Bước tiếp theo

- Đang chờ: người duyệt plan.
- Đọc plan và các khác biệt Figma/phạm vi ở mục 1; tự chạy `python .agents/scripts/gate.py approve 4.16-selection-confirmation-screen plan` trong terminal. Nếu Python alias chưa hoạt động, thay bằng runtime bundled nêu trên.
- Sau duyệt, lượt tiếp theo dùng wf-next → wf-implement, bắt đầu kiểm gate/nhánh và P1. Chưa sửa code frontend trong lượt plan này.
- Có thể commit `work/4.16-selection-confirmation-screen/` cùng evidence khi người dùng yêu cầu; chưa commit/push.
- Cập nhật lần cuối: 2026-10-26, Codex.
