# 4.16 · Đóng gói và mở PR

Cập nhật ngày 28/10/2026 theo yêu cầu người dùng commit, push và mở PR. Các artifact 01/03/04/05/06 đã approved được giữ nguyên; gate kiểm lại vẫn xác nhận toàn bộ approval hợp lệ.

## Kết quả

- Frontend: [PR #49](https://github.com/DrugTime-C1SE-07/DrugTime-frontend/pull/49), nhánh `feat/4.16-selection-confirmation-screen`, HEAD `49b345a0fa30291e4d974591b9d1b06d2b4690cc` đã push. Commit chức năng `e4eb451`, sau đó merge main `d0f3527` không có xung đột. Diff PR chỉ có 13 file đúng phạm vi; hash nội dung khớp bản đã review.
- Docs: [PR #24](https://github.com/DrugTime-C1SE-07/DrugTime-docs/pull/24), cùng tên nhánh, HEAD `73590c1e04a9b84f2b43907bec602cfc49afc75d` đã push. Commit workbook `da3f624`, sau đó merge main `1e42083` và giải quyết xung đột Excel.
- Superproject lấy main mới nhất `a6d2f88` làm nền, ghi artifact/evidence task và chỉ cập nhật con trỏ frontend/docs tới hai SHA đã xác nhận trên remote. PR tổng để draft trong khi hai PR submodule đang chờ review/merge.

## Kiểm chứng trong lượt đóng gói

- Suite medication sau khi merge main: **172 Pass / 0 Fail**, lệnh `flutter test --no-pub test/features/medication --reporter expanded`, log `evidence/git-package-medication.log`. Không chạy lại full Flutter suite hoặc kiểm thiết bị trong lượt này; số liệu full-suite và Android ở 04/05/06 là bằng chứng các phiên trước.
- Kiểm 13 hash frontend, index ban đầu rỗng và quét mẫu credential trong artifact/evidence dự kiến publish: `evidence/git-package-preflight.log`. Không phát hiện mẫu credential đã kiểm; không suy thành chứng nhận quét toàn repo.
- Scope implement: 14 file task đúng phạm vi; exit 1 do `backend/src/drugtime/modules/catalog/fetchers.py` ngoài task đã có từ trước. Giữ nguyên theo quyết định đã ghi ở 05/06, không stage vào commit 4.16. Log `evidence/git-package-scope.log`.
- Xung đột workbook: lấy workbook docs/main mới nhất làm nền trong scratch, dùng `.agents/scripts/testcase_xlsx.py merge` gộp spec 4.16, kiểm **23 sheet chức năng khác giữ nguyên** value/formula/style/validation và các bug không thuộc MEDPICK; sheet MEDPICK khớp workbook task đã review. Log `evidence/git-workbook-merge.log`, `evidence/git-workbook-verify.log`.
- Cảnh báo merge TC-MEDPICK-28: main cũ là Pass, spec mới là Fail. Giữ Fail theo báo cáo test/review đã được duyệt và quyết định người dùng ở `evidence/test-layout-risk-acceptance.log`; không nâng kết quả thành Pass.
- Report được tính lại trong artifact-tool và render trước/sau, không xuất lại XLSX bằng tool khác. Ảnh `evidence/git-workbook-before-*.png`, `evidence/git-workbook-after-*.png`; log cùng tiền tố. Không kiểm recalculation trong native Excel.
- Gate sau đóng gói vẫn toàn bộ approved: `evidence/git-package-gate.log`. Không tự ghi approval hoặc sửa artifact đã được duyệt.
- `git diff --cached --check` báo khoảng trắng cuối dòng trong raw evidence log; giữ nguyên output bằng chứng. Kiểm diff bỏ thư mục evidence sạch; code frontend cũng đã qua diff-check ở review.

## Bước tiếp theo

- Người khác review PR frontend/docs; giữ ngoại lệ layout Medium của TC-28/51: MEDPICK **50 Pass / 2 Fail / 0 Pending**, AC10/AC11 chưa đạt đầy đủ ở màn nhỏ/chữ lớn/bàn phím mở.
- Merge frontend và docs trước. Nếu squash/rebase merge đổi SHA, cập nhật con trỏ trong PR tổng tới SHA thực tế đã merge và có trên remote trước khi đánh dấu PR tổng ready/merge.
- PR tổng cần review độc lập theo Definition of Done. Lượt này chỉ commit/push/mở PR, không merge PR.
- Scratch và thay đổi/con trỏ api_contract/backend/tests ngoài task không nằm trong commit 4.16.
