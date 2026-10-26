# 3.25 · Mô tả PR chuẩn bị bàn giao

Các đoạn dưới là bản soạn tại local, chưa có PR được mở. Người dùng yêu cầu hoàn tất phần hiện tại và chưa xử lý High ngày 26/10/2026. Mọi mô tả giữ R1/R3/R5 còn mở, không trình bày test đỏ thành Pass hoặc xác nhận sẵn sàng merge.

## api_contract

**Title:** `fix(contract): restore consent-scoped adherence history specification`

Hợp đồng main mất `/adherence` và bảy schema sau merge khiến bộ test không thể kiểm response lịch sử. Khôi phục đúng phần định nghĩa từ commit `382fb13`, giữ nguyên nội dung JSON của các endpoint/schema khác.

Validation: đối chiếu JSON nguồn và HEAD trong `work/3.25/evidence/review-refresh-audit.log`; các unit contract nằm trong lần kiểm backend 144 Pass/2 Fail. Hai Fail thuộc xác nhận sớm, không phải lỗi thiếu schema. Mô tả chỉ trả liều đã đến giờ vẫn còn xung đột ngoại lệ AC3; R1 được để lại cho 3.23 xử lý đồng bộ contract/domain/SQL. Không tuyên bố contract đã đáp ứng toàn AC3/AC8.

Base cần chọn trước PR: working tree ở `585e99c`; chỉ stage `openapi.json`, so lại staged diff. Các thay đổi chưa commit. Phụ thuộc: backend/test 3.25 dùng contract này; thêm liên kết PR thật khi tạo.

Refs: 3.25; phụ thuộc sản phẩm 3.23.

## backend

**Title:** `test(adherence): cover family history rates and confirmation boundaries`

Bổ sung oracle cho liều đã xác nhận hợp lệ được tính ngay, pending tại +120 phút, missed sau cửa sổ và hậu xác nhận muộn. Test tích hợp người thân kiểm cả date/medication, response theo contract, audit và GET không thay đổi dose log. Không sửa production domain/SQL trong task kiểm thử.

Validation gần nhất: unit/contract/PEP/route **144 Pass, 2 Fail**, `review-refresh-backend.log/xml`. Evidence integration trước đó: history/PEP **66 Pass, 2 Fail**, `test-p7-integration.log/xml`; toàn integration **1089 Pass, 20 Fail, 1 XPASS**. Hai history Fail là R1/BUG-3.25-01: liều 08:00 đã xác nhận 07:30 bị loại trước giờ dự kiến. Các Fail ngoài history được giữ theo báo cáo, không gán thành hồi quy task này.

Unit task ở commit `49f2f11`, integration còn working tree. Base main diff có acceptance redeem kế thừa từ task 3.15; chọn base/tách phạm vi trước PR, không đưa nhầm vào mô tả 3.25. Phụ thuộc contract khôi phục; liên kết PR contract và test E2E khi có URL thật.

Refs: 3.25. R1 được hoãn theo yêu cầu người dùng; cần task sản phẩm 3.23 sửa sau.

## frontend

**Title:** `fix(adherence): clear family history when the session is unavailable`

Lịch sử gia đình được xóa khi app vào nền hoặc khả năng đọc của phiên/mạng bị vô hiệu. Controller chặn load khi unavailable và bỏ response cũ; khi phiên/foreground/online sẵn sàng trở lại, màn đọc mới thay vì hiển thị dữ liệu cũ. Bổ sung unit/widget và helper test route đọc API local.

Validation gần nhất: ba file family history **17/17 Pass**, `review-refresh-mobile.jsonl`; kiểm offline/background/logout/đổi patient/403 và response muộn ở cấp widget/controller. Evidence Android có linked/revoke/cross_patient Pass ở các lượt riêng. Độ ổn định handshake lượt đầu vẫn chưa xác định nguyên nhân.

Giới hạn: **R3** chưa có native OS/offline/logout/cache bền/response muộn trên thiết bị; **R5** chưa tìm thấy entrypoint chọn bệnh nhân/mở route trong UI production. Harness bootstrap auth/medication/consent in-memory và dùng Navigator mở route nên không chứng minh toàn hành trình PB21. Toàn Flutter trước đó **770 Pass/1 Fail/1 Skip**, không tuyên bố full suite xanh.

Base task `b24ee68`; commit test `a147ed4`, fix `46275fa`; working tree sạch. Xác định commit nào đã có PR trước khi tạo để tránh PR trùng; không kéo toàn UI/demo trong diff main local cũ. Mô tả này phục vụ bàn giao fix privacy/test hiện có, không nhận là đã hoàn tất UI entrypoint của 3.24.

Refs: 3.25, 3.25-02; phần UI còn lại thuộc 3.24.

## tests

**Title:** `test(adherence): add isolated Android family history runner`

Thêm runner local cho ba scenario linked/revoke/cross_patient, chạy production history route qua API/PEP và đối chiếu audit PostgreSQL thật. Runner dùng package `vn.drugtime.adherence_e2e`, từ chối package tồn tại, giữ bearer trong app-private qua stdin, chỉ kết nối local, commit thu hồi trước refresh và cleanup app/reverse mapping/process riêng.

Validation mới nhất: host runner **19/19 Pass**, `review-refresh-runner.log/xml`; lint file task Pass. Evidence Android: linked Pass; revoke handshake Fail đầu, chạy riêng Pass và chạy cùng cross_patient Pass; tất cả log đỏ/xanh đều được giữ. Không có một invocation cả ba scenario cùng xanh.

Giới hạn R3/R5: route test chưa đi từ UI chọn patient, chưa thực thi native lifecycle/offline/logout hoặc chứng minh không cache bền. Không dùng 19 test host để gọi là Android E2E Pass. Chỉ ba file trong `e2e/mobile_adherence_history/`; baseline redeem/pyc của task 3.15 không phải delta mới 3.25. Chưa commit. Phụ thuộc frontend helper và contract/backend local.

Chạy lại khi cần: theo README của runner, dùng Supabase/DB local, Android package riêng và `--preflight` trước scenario. Không dùng app người dùng hoặc hệ thống deploy.

Refs: 3.25.

## docs

**Title:** `test(adherence): record PB21 cases and retest evidence`

Cập nhật sheet lịch sử tuân thủ người thân và Report/Bug Report của workbook tổng theo spec task. Giữ **53 case: 46 Pass, 1 Fail, 6 Pending**, một Bug Report `BUG-FADH-20` cho BUG-3.25-01; TC40/41 Pass theo widget retest, không nhận là đã kiểm OS thật. Giữ 20 sheet chức năng khác.

Validation: testcase validator exit 0; JSON/task/master khớp mọi field case; evidence và kết quả tổng được đối chiếu ở `review-refresh-testcase-validate.log`, `review-refresh-evidence.log`, `review-refresh-audit.log`. Layout/recalculation dùng evidence stage test; không chạy native Excel ở review. Không đổi kết quả chỉ vì quyết định hoãn High.

Workbook working tree so với commit `3077e2e`; chỉ stage đúng file `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`. Phụ thuộc evidence/test của các PR trên; thêm liên kết thật khi có.

Refs: 3.25.

## Superproject

**Title:** `docs: finalize task 3.25 test and review handoff`

Lưu artifact requirement/plan/implementation/test/review, test case task và evidence PB21; thêm mô tả PR và ghi nhận quyết định người dùng để R1/R3/R5 xử lý sau. Review có kết luận kỹ thuật Chưa đạt; hồ sơ và phạm vi thực hiện hiện tại đã hoàn tất. Giữ Fail/Pending và trách nhiệm 3.23/3.24/QA; không đánh dấu sản phẩm đã thỏa toàn Definition of Done.

Postman local gồm collection sáu GET, environment không có token, ví dụ và assertion từ contract. Evidence HTTP trước đó: **9 lượt/14 request/75 assertion/0 failure** với DB audit; không publish workspace hoặc gửi run events. Contract/Postman là phần ngoài plan cũ đã được báo trong 05; scope test vẫn exit 1 với 15 file, scope review exit 1 với 20 file working tree kế thừa. Không ghi scope Pass.

Verification hồ sơ: gate review được phép chạy; 01/03/04/05 giữ nguyên hash; review draft chờ người duyệt. Lượt hoàn tất chỉ sửa hồ sơ, không chạy lại test hoặc đổi code/workbook/collection. Tổng kiểm mới gần nhất: backend 144 Pass/2 Fail, Mobile 17/17 Pass, host runner 19/19 Pass.

Chỉ stage các artifact/evidence và Postman đã được kiểm. Không stage scratch, runtime token/environment hoặc gitlink chưa xác minh. Chưa có commit bump; nếu PR sau này cập nhật gitlink thì đổi title thành `chore: bump verified task 3.25 dependencies` và ghi SHA/URL thật sau khi từng commit đã push/merge. Không tạo liên kết giả ở bản soạn.

Refs: 3.25.

## Thứ tự phối hợp

1. Chọn base và tránh đưa commit redeem/UI demo kế thừa vào PR 3.25.
2. Contract khôi phục → backend/test sử dụng contract → frontend helper/fix → tests runner → docs workbook.
3. Lưu superproject artifact độc lập; chỉ bump submodule sau khi commit đích được xác minh trên remote, rồi cập nhật SHA sau squash merge nếu có.
4. Gắn liên kết giữa các PR thật trước khi gửi review. Người dùng hiện chỉ yêu cầu hoàn tất hồ sơ, chưa yêu cầu mở PR/push/merge.
5. R1/R3/R5 để xử lý sau theo quyết định người dùng; người duyệt phải thấy chúng cùng Fail/Pending khi quyết định nghiệm thu hoặc merge.
