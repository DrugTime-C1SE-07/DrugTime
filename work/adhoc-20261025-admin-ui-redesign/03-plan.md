---
task: adhoc-20261025-admin-ui-redesign
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-25 15:17 +0700
content_hash: sha256:a4322237aa7fbdfd
inputs:
  01-requirement.md: sha256:ffdb8e4c5877f6b5
---

# adhoc-20261025-admin-ui-redesign · Plan

## 1. Giải pháp

**Lớp theme riêng, có phạm vi, đặt chồng lên CSS hiện có.** Không sửa `app/globals.css`. Thêm một file CSS mới chỉ được import từ `app/dashboard/layout.tsx`. Mọi selector trong file mới đều bắt đầu bằng `.admin-theme`.

1. `app/dashboard/layout.tsx` (thay đổi TSX duy nhất của task):
   - Nạp Open Sans bằng `next/font/google` (subsets `latin`, `vietnamese`; weight 400/600/700; `variable: "--font-open-sans"`).
   - Bọc `ToastProvider` và các phần bên trong bằng `<div className={\`admin-theme ${openSans.variable}\`}>`. Phải bọc ở ngoài vì `.toast-container` là anh em của `.admin-shell` (`components/ui/Toast.tsx:118-125`). Bọc ngoài `ToastProvider` thì toast cũng nhận theme.
   - `import "./dashboard-theme.css"`.
   - Không đổi `SessionKeepAlive`, `readExpiry`, cookie, thứ tự component.
2. `app/dashboard/dashboard-theme.css` (mới), gồm các khối theo thứ tự:
   - **Token:** `.admin-theme { --color-primary …; --font-sans: var(--font-open-sans), …; --radius-card …; --shadow-card … }`. Gán lại các biến đang có (`--color-*`, `--radius-*`, `--shadow-*`, `--font-sans`, `--font-main`). Nhờ vậy 340 chỗ dùng `var(--…)` ngoài khối Login tự đổi theo. Thêm biến riêng có tiền tố `--dt-`: `--dt-bg-gradient`, `--dt-accent-gradient`, `--dt-chip-bg`, `--dt-frame-radius`.
   - **Khung:** `.admin-theme .admin-shell` có nền `--dt-bg-gradient`. `.admin-shell__content` là khung trắng, bo góc `--dt-frame-radius` (32px), có lề. `.admin-sidebar` là gradient xanh đậm, bo cong cạnh phải (`border-radius: 0 48px 48px 0`), chữ và icon trắng. Mục đang chọn là pill trắng, chữ màu primary.
   - **Topbar:** nền trong suốt trên khung trắng. Nút icon tròn xám nhạt. Avatar profile tròn nền primary.
   - **Card, panel:** `.dashboard-kpi`, `.dashboard-panel`, `.medication-stat`, `.medication-table-card`, card stats bên interaction: nền trắng, bỏ viền, bóng mềm, bo 20px. Card tiêu điểm `.dashboard-kpi-grid > .dashboard-kpi:first-child` dùng `--dt-accent-gradient`, chữ trắng (giống card "Solar Power" trong ảnh).
   - **Control:** nút chính (`.dashboard-action--primary` và các class tương đương) dùng gradient accent. Chip, select filter có nền `--dt-chip-bg` và bo tròn. Ô search xám nhạt bo góc giống thanh Search trong ảnh.
   - **Bảng, badge, phân trang:** header bảng nền xám rất nhạt, hover dòng xanh nhạt, trang đang chọn dùng gradient accent. Badge mức độ nghiêm trọng và trạng thái giữ màu ngữ nghĩa (Q4).
   - **Modal, drawer, toast:** bo 24px, header có vạch accent, backdrop xanh đậm mờ.
   - **Focus:** override `outline` trong `.admin-theme` bằng màu primary mới, tỷ lệ tương phản ≥ 3:1. Không bỏ focus ring nào.
   - **Responsive:** ở ≤ 900px bỏ lề khung, sidebar bỏ bo cong. Bảng giữ scroll ngang trong `.medication-table-scroll` hoặc khung tương ứng.
   - **Reduced motion:** transition mới chỉ dùng `color`, `background-color`, `box-shadow`, `opacity`, `transform`. Rule `prefers-reduced-motion` toàn cục ở `globals.css:4622` đã vô hiệu hóa chúng, không cần thêm.

**Bảng màu** (giữ tương phản AC5; chữ trắng chỉ đặt trên nền ≥ `#2563EB`, tỷ lệ 5.17:1):

| Token | Giá trị | Dùng cho |
|---|---|---|
| `--dt-bg-gradient` | `linear-gradient(135deg, #7CC4F0 0%, #5B8FE0 100%)` | Nền ngoài khung, giống ảnh; không có chữ trên đó |
| `--dt-accent-gradient` | `linear-gradient(135deg, #2563EB 0%, #1D4ED8 100%)` | Sidebar, card tiêu điểm, nút chính, trang đang chọn; có chữ trắng |
| `--color-primary` | `#2563EB` | Liên kết, icon, focus |
| `--color-primary-strong` | `#1D4ED8` | Hover |
| `--color-primary-soft` | `#EAF2FE` | Nền nhấn nhẹ |
| `--dt-chip-bg` | `#EEF1F5` | Chip, ô search, nút phụ (chip xám trong ảnh) |
| `--color-shell` | `#F4F8FE` | Nền phụ trong khung |
| `--color-text` / `--color-muted` | `#111827` / `#5B6472` | Chữ chính / phụ (≥ 4.5:1 trên trắng) |
| `--color-danger`, `--color-success`, `--severity-*` | Giữ giá trị hiện tại | Ngữ nghĩa trạng thái (Q4) |

**Lý do chọn cách này, các cách đã cân nhắc:**
- *Sửa trực tiếp `:root` và các khối trong `globals.css`:* bỏ, vì khối Login dùng 25 lần `var(--…)` nên Login sẽ đổi theo (vi phạm AC2). Thêm nữa diff trong file 4631 dòng rất khó review.
- *Sửa className hoặc markup trong từng component:* bỏ. Selector có sẵn đã đủ để style lại. Sửa TSX làm tăng rủi ro AC3 mà không thêm giá trị thị giác. Style inline có mã hex (`InteractionDetailModal.tsx:182,183,293`, `MedicationDetailModal.tsx:147,148,173`) chỉ là màu trung tính hoặc trạng thái, vẫn hợp tông mới nên giữ nguyên.
- *Tailwind hoặc CSS Modules:* bỏ, vì phải thêm dependency hoặc viết lại markup.
- Mọi selector đều có phạm vi `.admin-theme`. Vì vậy dù App Router giữ stylesheet khi điều hướng client từ `/dashboard` về `/auth/login`, Login vẫn không bị ảnh hưởng: trang Login không có `.admin-theme`.

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `frontend/admin/app/globals.css` (4631 dòng) | Token `:root` ở dòng 3–40. Khối Login ở dòng 1854–2351. Ngoài Login có 340 lần dùng `var(--…)`; màu hardcode chủ yếu là `#ffffff` (55), `#eff4ff`, cùng màu trạng thái cam/đỏ/xanh lá. Focus ring toàn cục ở dòng 4606–4613 dùng `rgba(0,97,148,.45)`. Reduced motion toàn cục ở dòng 4622. Media query ở 900px và 1200px. Font Be Vietnam Pro được nạp bằng `@import`. |
| `frontend/admin/app/dashboard/layout.tsx` | Cấu trúc `ToastProvider > .admin-shell > Sidebar + main(Topbar + body)`. Server component. |
| `frontend/admin/app/layout.tsx` | Chỉ import `globals.css`. Không dùng `next/font`. |
| `frontend/admin/components/ui/Toast.tsx:118-125` | `.toast-container` được render ngoài `.admin-shell`, nên scope phải bọc ngoài `ToastProvider`. |
| `frontend/admin/components/ui/Modal.tsx` | Không dùng portal. Class: `modal-backdrop`, `modal-dialog--{size}`, `modal-header`, `modal-body`, `modal-footer`. |
| `frontend/admin/components/layout/Sidebar.tsx`, `Topbar.tsx` | Class BEM `admin-sidebar__*`, `admin-topbar__*`. Mục đang chọn có `admin-sidebar__link--active` và `aria-current`. |
| `frontend/admin/components/dashboard/KpiCard.tsx` | `dashboard-kpi dashboard-kpi--{tone}`, với `__icon`, `__label`, `__pill`, `__metric`, `__footer`. |
| `grep style={{` trên `components/**` | 9 file có style inline. Phần lớn dùng `var(--…)` nên tự theo token mới. 6 chỗ có mã hex trung tính hoặc trạng thái, giữ nguyên. |
| `frontend/admin/middleware.ts` | `/dashboard/*` cần cookie phiên hợp lệ. Muốn chụp màn hình để kiểm AC thì phải đăng nhập được, tức cần backend chạy và tài khoản admin để test. |
| `frontend/admin/package.json` | Không có lệnh test. Lệnh kiểm tra gồm `npm run lint` và `npm run build`. |
| `.agents/scripts/scope.py` | Đường dẫn trong bảng tính từ gốc submodule. Cột Submodule là `frontend`, nên đường dẫn có dạng `admin/...`. |
| Baseline (`evidence/plan-baseline-lint.log`, `evidence/plan-baseline-build.log`) | `npm run lint`: exit 0, không lỗi. `npm run build`: exit 0, 11 route. Implement phải giữ được kết quả này. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule; được dùng glob, ví dụ `src/<module>/auth/**`. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `admin/app/dashboard/layout.tsx` | sửa | Nạp Open Sans (`next/font/google`), bọc `.admin-theme`, import file theme |
| frontend | `admin/app/dashboard/dashboard-theme.css` | thêm | Toàn bộ lớp theme có phạm vi `.admin-theme` |

Không có file test: admin chưa có bộ test tự động (xem mục 5).

## 4. Checklist

- [ ] P1 [frontend] Tạo nhánh `feat/adhoc-20261025-admin-ui-redesign` từ `origin/main` theo `wf-git`. Không đụng thay đổi có sẵn `D mobile/.env.example`. — file: (git) — AC: AC3 — xong khi: `git -C frontend branch --show-current` ra đúng tên nhánh, và `git -C frontend status` chỉ còn dòng `D mobile/.env.example` có từ trước.
- [ ] P2 [frontend] Chụp ảnh baseline của `/auth/login` ở 1440px và 375px trước khi sửa. — file: `work/.../evidence/` — AC: AC2 — xong khi: có `evidence/login-before-1440.png` và `evidence/login-before-375.png`.
- [ ] P3 [frontend] Sửa `layout.tsx`: thêm `next/font/google` Open Sans, wrapper `.admin-theme`, `import "./dashboard-theme.css"`. Tạo file CSS mới chỉ chứa khối token. — file: `admin/app/dashboard/layout.tsx`, `admin/app/dashboard/dashboard-theme.css` — AC: AC1, AC3 — xong khi: `npm run build` exit 0. DOM `/dashboard` có `.admin-theme` chứa cả `.admin-shell` và `.toast-container`. `getComputedStyle` của `body .admin-shell` cho `font-family` bắt đầu bằng Open Sans.
- [ ] P4 [frontend] Style khung: nền gradient, khung trắng bo 32px, sidebar gradient bo cong và pill cho mục đang chọn, khu tài khoản và logout, topbar. — file: `admin/app/dashboard/dashboard-theme.css` — AC: AC1, AC5 — xong khi: ảnh `/dashboard` ở 1440px thấy đủ các yếu tố trên. Chữ trắng trên sidebar có tỷ lệ ≥ 4.5:1 khi đo bằng DevTools.
- [ ] P5 [frontend] Style trang Tổng quan: KPI (card đầu tiên dùng gradient accent), panel sync, panel quality, bảng workers, tabs, breadcrumb, `dashboard-action`. — file: như P4 — AC: AC1, AC5 — xong khi: có ảnh `evidence/impl-dashboard-1440.png`, chữ trên card gradient đạt ≥ 4.5:1.
- [ ] P6 [frontend] Style trang Danh mục thuốc: header, stats, sync banner, search, filter chip/select, bảng, badge, actions, phân trang. Trang Quy tắc tương tác dùng các selector `interaction-*` và `frame3` tương ứng, cộng guideline card. — file: như P4 — AC: AC1, AC4, AC5 — xong khi: có ảnh hai trang ở 1440px. Badge chống chỉ định vẫn đỏ và có chữ.
- [ ] P7 [frontend] Style modal (`modal-*`), các modal chi tiết hoặc form, drawer hoặc editor modal của interaction, toast (`toast-item--*`), và `admin-page-placeholder`. — file: như P4 — AC: AC1, AC4 — xong khi: có ảnh modal form thuốc, modal chi tiết tương tác và một toast sau khi bấm nút Thông báo.
- [ ] P8 [frontend] Thêm focus ring trong phạm vi `.admin-theme` (outline màu primary mới, `outline-offset: 2px`) và media query ≤ 900px. — file: như P4 — AC: AC5, AC6, AC7 — xong khi: Tab qua sidebar và filter thấy rõ outline. Ở 768px và 375px, `document.documentElement.scrollWidth <= innerWidth`. Bật `prefers-reduced-motion` thì không còn chuyển động.
- [ ] P9 [frontend] Kiểm hành vi (AC4): tìm kiếm, lọc, đặt lại lọc, phân trang, thêm/sửa, xem chi tiết, duyệt nhanh, xóa mềm + hoàn tác, mở editor interaction. — file: không có — AC: AC4 — xong khi: ghi kết quả từng thao tác vào `04-impl-notes.md`, không có lỗi console mới.
- [ ] P10 [frontend] Chụp lại `/auth/login` ở 1440px và 375px rồi so với P2. Kiểm diff bằng `git -C frontend diff --stat`, phải chỉ có 2 file trong bảng mục 3. — file: không có — AC: AC2, AC3 — xong khi: ảnh trước và sau không khác (so pixel bằng script trong `work/.../scratch/`, hoặc so bằng mắt nếu không có công cụ), diff đúng 2 file.
- [ ] P11 [frontend] Chạy `npm run lint`, `npm run build`, `python .agents/scripts/scope.py adhoc-20261025-admin-ui-redesign --stage implement`, lưu log. — file: `work/.../evidence/` — AC: AC8 — xong khi: lint và build exit 0 như baseline. Scope không báo file mới ngoài phạm vi, trừ các file có sẵn đã ghi ở mục 10.

## 5. Test

### Unit

| Test dự kiến | AC | Submodule |
|---|---|---|
| `npm run lint` → `evidence/implement-lint.log` (exit 0 như baseline) | AC8 | frontend |
| `npm run build` → `evidence/implement-build.log` (exit 0, đủ 11 route như baseline) | AC8 | frontend |

Không viết unit test mới. Task không thêm logic nào, và admin chưa có test runner (`AGENTS.md`: "TODO(team): chưa có lệnh test"). Thêm runner chỉ để test CSS là ngoài phạm vi.

### Tích hợp

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| Duyệt thủ công bằng browser pane trên `npm run dev` + backend local, chụp ảnh 5 trang dashboard ở 1440px | AC1 | Ảnh lưu `evidence/impl-<trang>-1440.png` |
| So ảnh Login trước và sau + `git diff --stat` | AC2, AC3 | P2, P10 |
| Chạy tay chuỗi thao tác nghiệp vụ trên 2 bảng | AC4 | P9 |
| Đo tương phản bằng DevTools, Tab bàn phím | AC5 | P4, P5, P8 |
| Viewport 768/375: kiểm `scrollWidth` | AC6 | P8 |
| Giả lập `prefers-reduced-motion` | AC7 | P8 |

Không chạm vùng rủi ro nào nên không có kịch bản chất lượng tích hợp nào của `AGENTS.md` áp dụng. Không thêm test vào `tests`.

## 6. Migration

Không có.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/adhoc-20261025-admin-ui-redesign` (đã có, commit `17862a3`) |
| frontend | `feat/adhoc-20261025-admin-ui-redesign` (tạo ở P1 từ `origin/main`) |

## 8. Rủi ro

- **Cần đăng nhập mới chụp và kiểm được dashboard.** `middleware.ts` chặn `/dashboard` khi không có phiên. Giảm thiểu: chạy backend local (`supabase start` + API) với tài khoản admin trong seed, hoặc dùng phiên do người dùng tự đăng nhập trong browser pane. Xem Q1.
- **`next/font/google` cần mạng lúc build.** Build offline hoặc CI không có mạng sẽ lỗi. Phát hiện ở P3 và P11. Nếu team thấy không chấp nhận được thì đổi sang `@import` Google Fonts trong file theme, giống cách `globals.css` đang nạp Be Vietnam Pro (không cần mạng lúc build).
- **Màu sidebar và card tiêu điểm đậm hơn ảnh tham chiếu.** Ảnh dùng xanh nhạt `~#6FB6EE` với chữ trắng, chỉ đạt khoảng 2.5:1 nên trượt AC5. Plan dùng `#2563EB → #1D4ED8` để chữ trắng đạt ≥ 4.5:1. Gradient nhạt như ảnh chỉ dùng cho nền ngoài khung, nơi không có chữ.
- **Selector override có thể không thắng CSS cũ** khi rule cũ có specificity cao hơn (ví dụ `:has()`, chuỗi nhiều class, `!important`). Phát hiện bằng ảnh chụp ở từng bước. Xử lý bằng cách tăng specificity trong file theme, không sửa `globals.css`.
- **Stylesheet theme vẫn nạp sau khi logout bằng điều hướng client.** Không ảnh hưởng gì vì mọi selector cần `.admin-theme`. P10 kiểm Login sau khi đã vào dashboard rồi logout.
- **Chồng thay đổi với task khác trong `frontend`.** Thay đổi `D mobile/.env.example` đã có trước task này. P1 không stage file đó.

## 9. Câu hỏi mở

Q1 [không chặn] Kiểm AC1, AC4–AC7 bằng cách nào khi `/dashboard` cần đăng nhập?
- Ảnh hưởng: không đăng nhập được thì không có ảnh chụp làm bằng chứng, AC1 và AC4–AC7 chỉ còn bằng chứng là build thành công.
- Lựa chọn: Agent chạy backend local và đăng nhập bằng tài khoản admin trong seed của backend / Người dùng tự đăng nhập trong browser pane, agent dùng phiên đó.
- Giả định mặc định: agent thử chạy backend local và dùng tài khoản admin trong seed. Nếu không có seed admin thì dừng và nhờ người dùng đăng nhập trong browser pane. Agent không tự tạo tài khoản.

## 10. Phát sinh

- `scope.py` đang báo các file có sẵn ngoài phạm vi: `.claude/rules/**`, `AGENTS.md`, `docs/**`, `frontend/mobile/.env.example`, `graphify-out/**` (xem `evidence/requirement-scope.log`). Chúng không thuộc task này. Ở P11 scope sẽ vẫn liệt kê chúng; agent sẽ đối chiếu để chắc không có file mới nào lọt ra ngoài.
- `.gitignore` của superproject ignore `work/`, nên artifact phải commit bằng `git add -f`. Đề xuất team sửa trong một task riêng.

## Bước tiếp theo

- Đang chờ: người duyệt (và xác nhận giả định Q1).
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261025-admin-ui-redesign plan`; sau đó agent làm giai đoạn implement (`wf-implement`) từ P1.
- Cập nhật lần cuối: 2026-10-25, Claude Code
