---
task: adhoc-20261025-admin-ui-redesign
stage: implement
owner: Ngọc Việt
started_at: 2026-10-25 15:18
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-25 16:02 +0700
content_hash: sha256:5a954b91ef7e6181
inputs:
  01-requirement.md: sha256:ffdb8e4c5877f6b5
  03-plan.md: sha256:a4322237aa7fbdfd
---

# adhoc-20261025-admin-ui-redesign · Implement

## 1. Tiến độ

Chụp ảnh và kiểm hành vi dùng Chrome headless qua CDP (`scratch/cdp-shot.mjs`, kèm các file job `scratch/jobs-*.json`). Script đặt một cookie phiên **test** (JWT không ký, chỉ có `exp`) trên `localhost:3100`. Cách làm này được người dùng chọn ngày 2026-10-25 vì Docker tắt và backend không có seed admin, xem mục 5. Trước khi chụp, dev server `next dev -p 3100` đã chạy.

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | `git -C frontend switch -c feat/adhoc-20261025-admin-ui-redesign origin/main` → đúng nhánh; `status` chỉ còn `D mobile/.env.example` có sẵn. `git diff 4c78045a HEAD -- admin` rỗng nên baseline lint/build của plan vẫn hợp lệ. | `evidence/implement-P1.log` |
| P2 | xong | `scratch/shot.sh` (Chrome CLI headless) chụp `/auth/login` ở 1440×900 và 375×812. Chụp lặp lại cho 0 pixel khác (`scratch/imgdiff.py`), nên cách chụp tất định. | `evidence/implement-P2.log`, `evidence/login-before-{1440,375}.png` |
| P3 | xong | `layout.tsx`: Open Sans qua `next/font/google`, wrapper `.admin-theme`, import CSS. Kiểm trong trình duyệt: `.admin-theme` chứa cả `.admin-shell` và `.toast-container`; `font-family` của h1 là `__Open_Sans_…`. | (kiểm bằng browser pane, kết quả ghi ở đây) |
| P4 | xong | Khung gradient, khung trắng bo 36px, sidebar gradient bo cong `28px 72px 72px 28px`, pill trắng cho mục active, topbar chip tròn. Ảnh 1440 không có tràn ngang. | `evidence/implement-P4-P6-shots.log`, `evidence/impl-dashboard-1440.png`, `evidence/impl-dashboard-scrolled-1440.png` |
| P5 | xong | KPI đầu tiên dùng gradient accent chữ trắng; tabs, thống kê, quality, workers dùng nền `--color-shell`. | `evidence/impl-dashboard-1440.png` |
| P6 | xong | Trang thuốc và tương tác: card, search/filter dạng chip, bảng, phân trang, badge giữ màu ngữ nghĩa (chống chỉ định vẫn đỏ, có chữ). Sửa thêm `.interactions-header__actions` (trước đây không có CSS nên 2 nút xếp dọc), xem mục 5. | `evidence/impl-medications-1440.png`, `evidence/impl-interactions-1440.png`, `evidence/impl-ocr-review-1440.png`, `evidence/impl-scraper-logs-1440.png` |
| P7 | xong | Modal form thuốc, chi tiết thuốc, form/hiệu chỉnh/xóa tương tác, toast (nút Thông báo). Backdrop phủ cả sidebar, sau khi sửa lỗi stacking (mục 5). `InteractionDetailModal` không được trang nào dùng nên không chụp được. | `evidence/implement-P7-shots.log`, `evidence/impl-modal-*.png`, `evidence/impl-toast-1440.png` |
| P8 | xong | **Responsive**: 8 ảnh ở 768/375, `scrollWidth - innerWidth = 0` ở mọi trang. **Tương phản**: 12/12 cặp đạt (`scratch/contrast.py`), cộng lớp phủ tối 22% trên 3 nền xanh đều ≥ 6.7:1. **Focus**: bấm Tab thật qua CDP, `:focus-visible` = true, link sidebar có outline trắng 2px, nút có outline 3px `#2563eb`, select hiện focus qua viền và vòng sáng của `.filter-select:focus-within`. **Reduced motion**: `transition-duration` 0.18s/0.2s khi tắt, `1e-05s` khi bật `reduce`. | `evidence/implement-P8-responsive.log`, `evidence/implement-P8-contrast.log`, `evidence/implement-P8-focus.log`, `evidence/implement-P8-focus-motion.log`, `evidence/impl-*-{768,375}.png`, `evidence/impl-focus-*.png` |
| P9 | xong | Kịch bản hành vi chạy trong trang (`scratch/behavior-medications.js`, `scratch/behavior-interactions.js`). Thuốc **15/15 PASS**: tìm kiếm, xóa từ khóa, lọc chất lượng, đặt lại, trang sau/trang đầu, mở/hủy form thêm, form sửa, modal chi tiết, duyệt nhanh + toast, xóa mềm + hoàn tác. Tương tác **12/12 PASS**: tìm kiếm, lọc mức độ, đặt lại, trang sau, form thêm, form hiệu chỉnh, hộp xác nhận xóa mềm và hủy. `consoleErrors: []` ở cả hai. | `evidence/implement-P9-medications.log`, `evidence/implement-P9-interactions.log` |
| P10 | xong | So pixel Login trước và sau bằng cùng công cụ Chrome CLI: 1440 → `diff_pixels=0`, 375 → `diff_pixels=0`. Thêm một kiểm: vào dashboard, bấm Đăng xuất, về `/auth/login`; ảnh lúc đó giống hệt Login mở trực tiếp (`diff_pixels=0`), nên stylesheet theme còn nạp sau khi điều hướng client cũng không ảnh hưởng Login. `git -C frontend diff --stat` chỉ có `layout.tsx`, file CSS mới là untracked, cộng thay đổi `mobile/.env.example` có sẵn. | `evidence/implement-P10-login-diff.log`, `evidence/login-after-*.png`, `evidence/login-cdp-*.png` |
| P11 | xong | `npm run lint` exit 0. `npm run build` exit 0, đủ 11 route; `/auth/login` vẫn 7.41 kB như baseline. `scope.py --stage implement`: 2 file của task `[OK]`; 37 file `[NGOÀI]` trùng với danh sách có sẵn từ `requirement-scope.log` (bớt `Test_Cases.xlsx`, file này giờ được tính `[OK]` theo vai trò testcase-book). Không có file mới ngoài phạm vi. Chạy lại sau vòng tinh chỉnh (P12): kết quả như trên. | `evidence/implement-final-frontend-lint.log`, `evidence/implement-final-frontend-build.log`, `evidence/implement-scope.log` |
| P12 | xong | **Vòng tinh chỉnh sau reopen (2026-10-25)**: người dùng thấy trang Tổng quan "to quá cỡ". Thêm khối "Thang cỡ trang Tổng quan" vào `dashboard-theme.css`, đưa về cùng mật độ với hai trang bảng. Đo bằng `scratch/measure-dashboard.js` ở 1440px, trước → sau: H1 42→26px; số KPI 58→36px; card KPI cao 248→166px; footer KPI 68→43px; pill 35→25px; H2 24→18px; tab 16→13px (cao 36→30); ô thống kê 85→65px; vòng chất lượng 188→150px (chữ 42→30px); mục chất lượng 83→53px; bảng workers: header 58→40px, dòng 88→56px; badge trạng thái 46→26px; lưới chính 639→470px. Ở ≤ 900px, H1 24px thay cho 32px của `globals.css`. Ảnh 1440/768/375: `overflowX = 0`, `consoleErrors: []`. Login so với baseline: 1440 và 375 đều `diff_pixels=0`. Lint, build và scope chạy lại đều như P11. | `evidence/adjust-measure-before.log`, `evidence/adjust-measure-after.log`, `evidence/adjust-dashboard-shots.log`, `evidence/adjust-login-diff.log`, `evidence/impl-dashboard-{1440,scrolled-1440,768,375}.png` |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/adhoc-20261025-admin-ui-redesign` | `admin/app/dashboard/layout.tsx` (sửa) |
| frontend | `feat/adhoc-20261025-admin-ui-redesign` | `admin/app/dashboard/dashboard-theme.css` (thêm, 974 dòng) |

Kết quả `python .agents/scripts/scope.py adhoc-20261025-admin-ui-redesign --stage implement`: 2 file của task `[OK]`. Script vẫn exit 1 vì 37 file có sẵn từ trước task (`.claude/rules/**`, `AGENTS.md`, 3 file `docs/**`, `frontend/mobile/.env.example`, `graphify-out/**`), xem mục 6. Log: `evidence/implement-scope.log`.

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `cd frontend/admin && npm run lint` | pass (exit 0, 0 lỗi; baseline cũng 0) | `evidence/implement-final-frontend-lint.log` |
| frontend | `cd frontend/admin && npm run build` | pass (exit 0, 11 route như baseline) | `evidence/implement-final-frontend-build.log` |
| frontend | Kịch bản hành vi CDP | 27/27 pass, 0 lỗi console | `evidence/implement-P9-*.log` |
| frontend | So pixel Login | 3/3 cặp `diff_pixels=0` | `evidence/implement-P10-login-diff.log` |

Admin chưa có test runner (`AGENTS.md`: TODO(team)). Theo plan, không có unit test mới vì task không thêm logic.

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test (task size M).

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- **Q1 của plan, đổi cách kiểm:** người dùng xác nhận giả định mặc định ngày 2026-10-25. Khi chạy thực tế thì không làm được: Docker không chạy nên không bật được Supabase và backend, và `backend/supabase` không có file seed nào có admin. Người dùng cũng không tự đăng nhập được vì form Login cần backend. Agent hỏi và người dùng chọn phương án "cookie test local": JWT không ký, chỉ có `exp`, đặt trên `localhost:3100`. Cách này chạy được vì `middleware.ts` chỉ đọc `exp` và các trang dashboard hiện chỉ dùng dữ liệu tĩnh. Token chỉ tồn tại trong trình duyệt test và script `scratch/`, không có trong code app.
- **Lỗi đã gặp và sửa trong P7 (stacking):** ban đầu `.admin-shell__content` có `z-index: 1`, tạo stacking context riêng nên modal (z-index 1000) bị sidebar (z-index 20) đè lên. Cách sửa: `.admin-shell { isolation: isolate }`, khung trắng `::before` dùng `z-index: -1`, bỏ z-index của content. Đã kiểm lại bằng chuỗi computed style và ảnh `impl-modal-*`.
- **Tương phản (P8):** chữ phụ `#e0eaff` trên `#2563eb` chỉ đạt 4.28:1 và focus ring rgba 55% chỉ đạt 2.56:1. Đã đổi sang `#f5f8ff` (4.86:1) và outline primary đặc (5.17:1). Các mảng nền trắng trong suốt (0.14–0.2) trên nền xanh làm chữ trắng tụt khoảng 4:1, nên đổi thành lớp phủ tối `--dt-on-accent-surface: rgba(15,23,80,.22)` (≥ 6.7:1).
- **Ngoài phần style "theo ảnh", có thêm 2 chỉnh layout trong file theme**, vẫn nằm trong file đã duyệt:
  - (a) `.interactions-header__actions` không có CSS trong `globals.css` nên 2 nút xếp dọc; theme xếp lại thành hàng ngang.
  - (b) ở ≤ 900px, layout cũ để sidebar `position: fixed` rộng 260px, nên trên 375px phần nội dung chỉ còn khoảng 115px. Theme chuyển sidebar thành thanh trên cùng, nav cuộn ngang. Cả hai sửa lỗi layout có sẵn, không đổi markup.
- **Giới hạn còn lại:** ở 375px, nav sidebar cuộn ngang nên mục đang chọn có thể nằm ngoài vùng nhìn thấy (vd. "Quy tắc tương tác"). Vẫn dùng được nhưng chưa tự cuộn tới mục active, vì muốn vậy phải thêm JS, ngoài phạm vi "chỉ giao diện". Nhãn trong 4 thẻ stats của trang thuốc và tương tác vẫn xuống dòng ở 1440px; hiện tượng này có từ layout cũ, theme không đổi grid đó.
- `dashboard-theme.css` dài 974 dòng, vượt ngưỡng mềm 800 dòng của quy ước code. Tôi giữ một file vì plan đã duyệt chỉ cho phép đúng file này. File chia theo khối có tiêu đề (token, khung, sidebar, topbar, thang cỡ Tổng quan, bảng, modal, responsive). Nếu reviewer muốn tách (vd. `dashboard-theme.overview.css`) thì cần reopen plan để thêm file vào bảng phạm vi.
- Dev server khi đang HMR từng log `Module not found: './dashboard-theme.css'`, trong khoảng vài giây giữa lúc sửa `layout.tsx` và lúc tạo file CSS. Các lần chạy CDP sau đó trên trình duyệt sạch đều có `consoleErrors: []`.
- Cấu hình chạy preview nằm ở `D:\Captone\.claude\launch.json`, ngoài repo.

## 6. Phát sinh

- 37 file `[NGOÀI]` của `scope.py` là thay đổi có sẵn trước task, không do task này tạo (đã ghi ở `01` mục 10 và `03` mục 10). Cần commit hoặc tách chúng ở nhánh của chúng trước khi mở PR, để PR `frontend` không kéo theo `D mobile/.env.example`.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt xem ảnh trong `evidence/` rồi chạy `python .agents/scripts/gate.py approve adhoc-20261025-admin-ui-redesign implement`; sau đó agent làm giai đoạn test (`wf-test`). Chưa commit code trong `frontend` và artifact `04`.
- Cập nhật lần cuối: 2026-10-25 16:05, Claude Code (sau vòng tinh chỉnh P12)
