# 3.25 · Các PR đã xuất bản

Người dùng yêu cầu commit, push và mở PR ngày 26/10/2026. Các PR ở trạng thái draft; R1/R3/R5 hoãn xử lý, Fail/Pending giữ nguyên.

## DrugTime-api_contract

https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15

**fix(contract): restore consent-scoped adherence history specification**

Khôi phục GET /adherence và bảy schema từ commit 382fb13 vì bản contract main bị thiếu phần lịch sử. JSON của các endpoint/schema khác giữ nguyên.

Đối chiếu hash với manifest review đã duyệt: không đổi. Evidence unit/contract/PEP gần nhất: 144 Pass, 2 Fail; hai Fail thuộc xác nhận sớm AC3. Mô tả chỉ trả liều đã đến as_of còn xung đột ngoại lệ xác nhận sớm, để task 3.23 xử lý đồng bộ domain/SQL/contract. Không chạy lại test sản phẩm trong lượt commit/push/PR.

Ba phát hiện review High R1/R3/R5 đang hoãn theo chỉ đạo người dùng. Duyệt báo cáo không thay Fail/Pending thành Pass và chưa xác nhận DoD; PR draft để bàn giao, chưa sẵn sàng merge.

Các PR liên quan:

- [DrugTime-api_contract](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15)
- [DrugTime-backend](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41)
- [DrugTime-frontend](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45)
- [DrugTime-test](https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2)
- [DrugTime-docs](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19)
- [DrugTime](https://github.com/DrugTime-C1SE-07/DrugTime/pull/43)

Nguồn evidence: [hồ sơ task 3.25](https://github.com/DrugTime-C1SE-07/DrugTime/tree/test/3.25-family-adherence-history-tests/work/3.25).

Refs: 3.25.

## DrugTime-backend

https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41

**test(adherence): cover family history rates and confirmation boundaries**

Bổ sung unit và integration oracle cho tỷ lệ lịch sử người thân, liều xác nhận hợp lệ, pending tại +120 phút, missed sau cửa sổ và biên xác nhận. Kiểm cả nhóm date/medication, contract, audit và GET không đổi dose log. Không sửa domain/SQL.

Evidence đã duyệt: unit/contract/PEP 144 Pass, 2 Fail; integration history/PEP 66 Pass, 2 Fail. Hai Fail mỗi bộ là AC3 xác nhận sớm, giữ regression đỏ theo BUG-3.25-01 (issue #40). Toàn integration trước: 1089 Pass, 20 Fail, 1 XPASS; không tuyên bố suite xanh. Không chạy lại test sản phẩm trong lượt xuất bản.

PR đặt trên nhánh 3.15 để loại acceptance redeem kế thừa khỏi diff 3.25. Cần đưa base 3.15 vào main, retarget và kiểm diff trước merge; không merge riêng nhánh 3.25 xuống base khi chưa quyết định thứ tự.

Ba phát hiện review High R1/R3/R5 đang hoãn theo chỉ đạo người dùng. Duyệt báo cáo không thay Fail/Pending thành Pass và chưa xác nhận DoD; PR draft để bàn giao, chưa sẵn sàng merge.

Các PR liên quan:

- [DrugTime-api_contract](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15)
- [DrugTime-backend](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41)
- [DrugTime-frontend](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45)
- [DrugTime-test](https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2)
- [DrugTime-docs](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19)
- [DrugTime](https://github.com/DrugTime-C1SE-07/DrugTime/pull/43)

Nguồn evidence: [hồ sơ task 3.25](https://github.com/DrugTime-C1SE-07/DrugTime/tree/test/3.25-family-adherence-history-tests/work/3.25).

Refs: 3.25.

## DrugTime-frontend

https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45

**fix(adherence): clear family history when the session is unavailable**

Xóa lịch sử gia đình khi app vào nền hoặc phiên/mạng không cho phép đọc. Controller chặn load khi unavailable và bỏ response cũ; foreground/online/phiên hợp lệ trở lại yêu cầu đọc mới. Thêm unit/widget và helper Android route. Hai commit a147ed4 và 46275fa dựa trên b24ee68, không đưa UI/demo kế thừa vào diff.

Evidence đã duyệt: targeted family history 17/17 Pass. Android linked/revoke/cross_patient có Pass ở các lượt riêng; handshake revoke lượt đầu Fail được giữ. Full Flutter trước: 770 Pass, 1 Fail, 1 Skip. Không chạy lại test trong lượt xuất bản.

R3 còn thiếu native OS/offline/logout/cache bền/response muộn trên thiết bị. R5 chưa có entrypoint chọn patient/mở lịch sử trong UI production; harness pushNamed trực tiếp nên chưa chứng minh full PB21. BUG-3.25-02/issue #44 chỉ có bằng chứng fix ở widget/controller và route; không tự đóng issue.

Ba phát hiện review High R1/R3/R5 đang hoãn theo chỉ đạo người dùng. Duyệt báo cáo không thay Fail/Pending thành Pass và chưa xác nhận DoD; PR draft để bàn giao, chưa sẵn sàng merge.

Các PR liên quan:

- [DrugTime-api_contract](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15)
- [DrugTime-backend](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41)
- [DrugTime-frontend](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45)
- [DrugTime-test](https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2)
- [DrugTime-docs](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19)
- [DrugTime](https://github.com/DrugTime-C1SE-07/DrugTime/pull/43)

Nguồn evidence: [hồ sơ task 3.25](https://github.com/DrugTime-C1SE-07/DrugTime/tree/test/3.25-family-adherence-history-tests/work/3.25).

Refs: 3.25.

## DrugTime-test

https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2

**test(adherence): add isolated Android family history runner**

Thêm runner local cho linked/revoke/cross_patient với production history route, API/PEP và audit PostgreSQL thật. Package riêng vn.drugtime.adherence_e2e, chặn package đã tồn tại, bearer qua stdin vào app-private, chỉ local và cleanup riêng tài nguyên runner.

Evidence đã duyệt: host runner 19/19 Pass; Android linked Pass, revoke Fail đầu rồi Pass riêng và Pass cùng cross_patient. Không có một invocation cả ba scenario cùng xanh. Host unit không chứng minh Android E2E. R3/R5 vẫn thiếu lifecycle/offline/logout/cache bền và hành trình chọn patient thật. Không chạy lại test trong lượt xuất bản.

PR đặt trên nhánh 3.15 vì runner tái sử dụng e2e/mobile_redeem/run_e2e.py ở base đó. Diff chỉ thêm ba file mobile_adherence_history, không thêm pyc hoặc thay redeem. Cần merge base 3.15 rồi retarget/kiểm diff trước merge 3.25.

Ba phát hiện review High R1/R3/R5 đang hoãn theo chỉ đạo người dùng. Duyệt báo cáo không thay Fail/Pending thành Pass và chưa xác nhận DoD; PR draft để bàn giao, chưa sẵn sàng merge.

Các PR liên quan:

- [DrugTime-api_contract](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15)
- [DrugTime-backend](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41)
- [DrugTime-frontend](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45)
- [DrugTime-test](https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2)
- [DrugTime-docs](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19)
- [DrugTime](https://github.com/DrugTime-C1SE-07/DrugTime/pull/43)

Nguồn evidence: [hồ sơ task 3.25](https://github.com/DrugTime-C1SE-07/DrugTime/tree/test/3.25-family-adherence-history-tests/work/3.25).

Refs: 3.25.

## DrugTime-docs

https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19

**test(adherence): record PB21 cases and retest evidence**

Lưu bộ ca PB21 và cập nhật retest trong Test_Cases.xlsx: 53 ca, 46 Pass, 1 Fail, 6 Pending; một bug BUG-FADH-20 ánh xạ BUG-3.25-01. TC40/41 Pass theo widget, không nhận là đã kiểm OS thật. Giữ 20 sheet chức năng khác so baseline trước retest.

Evidence đã duyệt: validator exit 0, JSON/task/master khớp metadata và kết quả; log review-refresh-testcase-validate, review-refresh-evidence, review-refresh-audit. Không chạy lại Excel hoặc test sản phẩm trong lượt xuất bản.

Base là nhánh 3.15 chứa workbook kế thừa; diff từ base gồm commit PB21 3077e2e và retest 1809e2f. Cần merge base rồi retarget và đối chiếu workbook với các PR docs #17/#18 trước merge để không ghi đè cập nhật song song.

Ba phát hiện review High R1/R3/R5 đang hoãn theo chỉ đạo người dùng. Duyệt báo cáo không thay Fail/Pending thành Pass và chưa xác nhận DoD; PR draft để bàn giao, chưa sẵn sàng merge.

Các PR liên quan:

- [DrugTime-api_contract](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15)
- [DrugTime-backend](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41)
- [DrugTime-frontend](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45)
- [DrugTime-test](https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2)
- [DrugTime-docs](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19)
- [DrugTime](https://github.com/DrugTime-C1SE-07/DrugTime/pull/43)

Nguồn evidence: [hồ sơ task 3.25](https://github.com/DrugTime-C1SE-07/DrugTime/tree/test/3.25-family-adherence-history-tests/work/3.25).

Refs: 3.25.

## DrugTime

https://github.com/DrugTime-C1SE-07/DrugTime/pull/43

**chore: publish task 3.25 evidence and verified submodule pointers**

Lưu hồ sơ task 3.25, evidence, testcase JSON/XLSX, Postman local và bump năm submodule tới commit đã push, kiểm SHA remote. Tất cả giai đoạn, gồm review, được gate xác nhận approved. Giữ nguyên nội dung artifact đã duyệt.

Postman có sáu GET, environment không token, ví dụ và assertion; evidence cũ 9 lượt/14 request/75 assertion/0 failure. Không publish Postman workspace hoặc gửi run events.

Lượt xuất bản kiểm gate, staged whitespace, hash 105 file khớp review, và mẫu credential trong hồ sơ/evidence không có phát hiện. Không chạy lại test sản phẩm. Kết quả đã duyệt vẫn là backend 144 Pass/2 Fail, mobile targeted 17/17 Pass, host runner 19/19 Pass; workbook 46 Pass/1 Fail/6 Pending. Scope trước vẫn exit 1 như review giải thích, không đổi thành Pass.

Backend/tests/docs là PR phụ thuộc nhánh 3.15. Thứ tự: xử lý base 3.15 → contract → backend → frontend → tests → docs → superproject. Nếu squash/rebase merge làm SHA thay đổi, cập nhật gitlink tới SHA đã merge trước khi merge superproject.

Ba phát hiện review High R1/R3/R5 đang hoãn theo chỉ đạo người dùng. Duyệt báo cáo không thay Fail/Pending thành Pass và chưa xác nhận DoD; PR draft để bàn giao, chưa sẵn sàng merge.

Các PR liên quan:

- [DrugTime-api_contract](https://github.com/DrugTime-C1SE-07/DrugTime-api_contract/pull/15)
- [DrugTime-backend](https://github.com/DrugTime-C1SE-07/DrugTime-backend/pull/41)
- [DrugTime-frontend](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/45)
- [DrugTime-test](https://github.com/DrugTime-C1SE-07/DrugTime-test/pull/2)
- [DrugTime-docs](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/19)
- [DrugTime](https://github.com/DrugTime-C1SE-07/DrugTime/pull/43)

Nguồn evidence: [hồ sơ task 3.25](https://github.com/DrugTime-C1SE-07/DrugTime/tree/test/3.25-family-adherence-history-tests/work/3.25).

Refs: 3.25.
