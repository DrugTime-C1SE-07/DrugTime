# [High][3.24] Lịch sử người thân còn dữ liệu sức khỏe khi offline hoặc chạy nền

## Retest 25/10/2026 · Đã xác nhận fix ở unit/widget

- Frontend `46275fa7aa07df0abf2f5db0dde51882b99249a1` (`fix(adherence): clear family history when unavailable`), baseline trước sửa `a147ed4`.
- Chạy lại ba file family adherence: **17 Pass, 0 Fail, 0 Skip**, exit 0. Hai ca offline/background từng đỏ đã xanh; các assertion cũ giữ nguyên và có thêm kiểm response muộn, không GET khi paused, đọc mới khi online/resumed, denied không hiện dữ liệu cũ.
- Ca mới `AC6: unavailable history rejects late reads and reloads on return` cũng Pass. Các ca đổi patient/logout/401/403/network/read-only Pass.
- Toàn Flutter: **770 Pass/1 Fail/1 Skip**, exit 1; Fail badge `family_tab_screen_test.dart` có cùng lỗi thiếu ConsentScope/FamilyLinkScope trong log trước bản sửa, không phải lỗi mới phát hiện của fix này. Skip live repository cần fixture API/DB có sẵn; không đổi skip.
- `analyze` năm file bản sửa: **No issues found**, exit 0. Backend unit/contract history **113 Pass/2 Fail**; hai Fail thuộc BUG-3.25-01 độc lập.
- Evidence: `work/3.25/evidence/test-bug02-family-mobile.jsonl`, `test-bug02-mobile-full.jsonl`, `test-bug02-analyze.log`, `test-bug02-final-verify.log`. TC-FADH-40/41 chuyển **Pass** trong spec/task/master theo xác nhận của người dùng “Cập nhật thành Pass theo retest”.
- **Giới hạn:** chưa chạy Android lifecycle OS, hành trình Mobile → API → DB hoặc kiểm RAM/cache bền trên thiết bị. Fix đã xác minh ở widget; tiêu chí OS/E2E cuối issue còn Pending. Các phần dưới là mô tả và bằng chứng đỏ trước fix, giữ để truy vết.

## Phân loại

- **BUG-3.25-02**, phát hiện tại task 3.25 / PB21 / **AC6, QD-29**; task sản phẩm xử lý: **3.24**.
- **High**: dữ liệu sức khỏe còn trong cây widget sau sự kiện bắt buộc xóa dữ liệu phiên, chặn nghiệm thu quyền riêng tư PB21.
- Hai tình huống cùng thuộc một lỗi invalidation: TC-FADH-40/41, Bug Report BUG-FADH-40/41. Chưa có bằng chứng truy cập chéo patient hoặc rò rỉ dữ liệu thật.

## Môi trường và tái hiện

Lượt test ngày 25/10/2026: frontend `a147ed4`, widget test dùng production FamilyAdherenceScreen/DrugTimeApp, repository cấp dữ liệu local giả. Family đã đăng nhập, đã tải lịch sử patient P và thấy tên thuốc giả **Thuốc A**.

### A. Chạy nền

1. Mở FamilyAdherenceScreen, đợi tải lịch sử thành công.
2. Phát lifecycle `inactive → hidden → paused`.
3. Pump một frame; kiểm toàn cây widget bằng `find.text('Thuốc A', skipOffstage: false)`.

### B. Offline trong app

1. Khởi tạo DrugTimeApp với family session và connectivity monitor được app đăng ký.
2. Mở route AppRoutes.familyAdherence cho P; hoàn tất tải lịch sử hôm nay, xác minh tên thuốc đang hiện.
3. Emit `false` qua stream connectivity, pump và đợi widget ổn định.
4. Kiểm toàn cây widget như tình huống A.

## Thực tế / kỳ vọng

**Thực tế:** sau mỗi trigger vẫn tìm thấy **4 Text Thuốc A**. Hai ca fail tại assertion yêu cầu không còn dữ liệu; điều kiện tải dữ liệu trước trigger đã đạt.

**Kỳ vọng:** xóa ngay lịch sử sức khỏe khỏi state/RAM và giao diện khi offline hoặc chạy nền. Response tới muộn không khôi phục dữ liệu cũ. Khi được phép tải lại, gọi API để kiểm quyền mới.

## Nguyên nhân đã đối chiếu

- `mobile/lib/features/adherence/presentation/screens/family_adherence_screen.dart`: didChangeAppLifecycleState chỉ refresh khi resumed, chưa clear khi inactive/hidden/paused.
- `mobile/lib/app/app.dart`: callback familyConnectivity.onlineChanges chỉ clear FamilyAlertController, chưa clear family history.
- Controller lịch sử đã có generation/clear nhưng hai sự kiện trên chưa nối tới cơ chế đó.

## Bằng chứng / hồi quy

Nguồn local trong superproject: `work/3.25/05-test-report.md`, mục 6 và `04-impl-notes.md`, mục BUG-3.25-02.

`work/3.25/evidence/test-contract-mobile.jsonl`: **14 Pass/2 Fail** trong 16 ca family adherence. Hai test đỏ thuộc `mobile/test/features/family/family_adherence_screen_test.dart`:

- `AC6 QD-29: background removes family health data immediately`
- `AC6 QD-29: offline removes health data from the actual app`

Từ frontend/mobile:

```powershell
flutter test --no-pub test/features/family/family_adherence_screen_test.dart
```

Kết quả lấy từ evidence ngày 25/10, không chạy lại khi tạo issue. Chứng cứ hiện tại là widget test, chưa xác minh lifecycle OS trên Android thật. Evidence local chưa có URL GitHub.

Đổi patient, clear/response muộn ở controller, refresh 403/network/401 và logout đã có test Pass; không gộp những nhánh đó thành lỗi mới.

## Tiêu chí hoàn tất

- [x] Nối offline và lifecycle chạy nền tới clear/invalidation family history; dữ liệu biến mất ngay khi nhận trigger (unit/widget).
- [x] Request đang chạy/response tới muộn không khôi phục dữ liệu sau invalidation (unit/widget).
- [x] Hai test hiện đỏ chuyển xanh; các test đổi patient/logout/401/403/network/read-only vẫn Pass.
- [x] Online/foreground trở lại bắt đầu lần đọc mới, denied không hiện dữ liệu cũ (unit/widget; quyền API/DB thật giữ bằng chứng trước, chưa chạy lại).
- [ ] Kiểm thêm Android với lifecycle OS thật và hành trình Mobile → API → DB; lưu evidence, phân biệt đã chạy/Pending.
