---
task: adhoc-20261025-admin-ui-redesign
title: Thiết kế lại giao diện Admin Web theo phong cách smart-home-management (trừ Login)
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-25 15:05 +0700
content_hash: sha256:ffdb8e4c5877f6b5
---

# adhoc-20261025-admin-ui-redesign · Thiết kế lại giao diện Admin Web (trừ Login)

## 1. Mục tiêu

Quản trị viên dùng Admin Web (`frontend/admin`) thấy một giao diện mới, đồng nhất, theo phong cách của ảnh tham chiếu `D:\smart-home-management\4198319.jpg`: nền gradient xanh dương nhạt, khung nội dung trắng bo góc lớn, sidebar xanh bo cong, thẻ (card) trắng đổ bóng nhẹ, điểm nhấn gradient xanh, font Open Sans. Chỉ đổi phần trình bày; mọi hành vi, dữ liệu hiển thị, lời gọi service/API giữ nguyên.

## 2. Phạm vi

### Trong phạm vi

- Khung chung khu `/dashboard/*`: `Sidebar`, `Topbar`, `admin-shell` (nền, khung bo góc, lưới).
- Trang Tổng quan `/dashboard`: `DashboardHeader`, `KpiCard`, `SyncStatusPanel`, `DataQualityPanel`, `WorkersTable`.
- Trang Danh mục thuốc `/dashboard/medications`: header, stats grid, sync banner, filters, table, form, detail modal.
- Trang Quy tắc tương tác `/dashboard/interactions`: header, stats grid, guideline card, filters, table, drawer, form, detail modal.
- Trang placeholder `/dashboard/ocr-review`, `/dashboard/scraper-logs` (chỉ style khung `admin-page-placeholder`).
- Thành phần UI dùng chung: `Modal`, `Toast`, nút, input, select, badge, phân trang, trạng thái hover/focus/disabled.
- Token thiết kế mới (màu, bo góc, bóng, font) áp dụng **trong phạm vi khu dashboard**, không rò sang trang Login.

### Ngoài phạm vi

- Trang và thành phần Login: `app/auth/login/page.tsx`, `components/auth/LoginForm.tsx`, khối CSS `.admin-login-*` (dòng ~1854–2351 của `globals.css`), route `app/api/session/*`, `SessionKeepAlive`. Giao diện Login phải giữ nguyên từng pixel.
- `LogoutButton`: chỉ được đổi style qua CSS của nơi đặt nó (sidebar/topbar), không sửa file.
- Mọi logic: state, handler, hook, props, điều kiện render, gọi API/service, dữ liệu mẫu (ví dụ "14,850", "Sync: 2 phút trước"), văn bản tiếng Việt hiện có.
- Thêm tính năng mới thấy trong ảnh tham chiếu nhưng không có trong app (ô Search toàn cục, lời chào "Hi, …", widget thời tiết/ngày, biểu đồ). Không bịa dữ liệu để lấp bố cục.
- Dark mode (hiện app không có).
- Backend, `api_contract`, `tests`, `docs`, mobile, landing.
- Thêm dependency npm.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `D:\smart-home-management\4198319.jpg` | Phong cách: nền gradient xanh `~#7AC3EE → #5B8FE0`, khung trắng bo góc ~48px, sidebar xanh bo cong phía phải, chữ menu trắng chữ thường + icon đặc; card tiêu điểm nền gradient xanh chữ trắng; card thường nền trắng bóng mềm; chip/nút xám nhạt `#E5E7EB`, trạng thái chọn = gradient xanh; tiêu đề đậm đen; thanh Search xám bo góc; icon chuông/thư xám; avatar tròn xanh. |
| `D:\smart-home-management\Fonts.txt` | Font duy nhất: Open Sans. |
| `frontend/admin/package.json` | Next.js 14, React 18, `lucide-react`; không có Tailwind; không có lệnh test. |
| `frontend/admin/app/globals.css` (4021+ dòng) | Toàn bộ style ở một file. Token `:root` (dòng 3–40): primary `#006194`, font "Be Vietnam Pro", `--radius-card: 16px`. Khối Login dùng 25 lần `var(--…)` → đổi token ở `:root` sẽ làm đổi Login; token mới phải đặt trong scope `.admin-shell`. |
| `frontend/admin/app/layout.tsx`, `app/dashboard/layout.tsx` | Root layout chỉ import `globals.css`; dashboard layout bọc `ToastProvider > .admin-shell > Sidebar + main(Topbar + body)`. Không có `next/font`. |
| `frontend/admin/components/layout/Sidebar.tsx`, `Topbar.tsx` | Sidebar: brand, trạng thái hệ thống, 5 mục nav (lucide), khối tài khoản + logout. Topbar: sync label, nút trợ giúp/thông báo (gọi `showToast`), profile, logout. |
| `frontend/admin/components/ui/Modal.tsx` | Không dùng portal → modal nằm trong `.admin-shell`, nhận token scope được. Toast container cần kiểm khi plan (do `ToastProvider` bọc ngoài `.admin-shell`). |
| `frontend/admin/app/dashboard/page.tsx` | KPI dùng dữ liệu tĩnh, prop `tone`. |
| 9 component dùng `style={{…}}` inline (Medication*/Interaction*/DataQualityPanel/LoginForm) | Một số màu nằm inline trong TSX; plan phải quyết định đổi các style inline thuần trình bày hay giữ. |
| `work/admin-dashboard-prototype/01-requirement.md` | Task trước đã dựng UI 2 bảng PB04/PB05; task này chỉ đổi lớp trình bày lên trên nó. |
| Skill `ui-ux-pro-max` (`--design-system`, density 7) | Gợi ý tự động ra dark glassmorphism + Fira — **không dùng** vì trái phong cách tham chiếu người dùng chỉ định; chỉ lấy checklist: tương phản 4.5:1, focus ring rõ, `cursor:pointer`, transition 150–300ms, `prefers-reduced-motion`, responsive 375/768/1024/1440. |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Chỉ `frontend/admin`: CSS và markup trình bày. |
| `backend` | Không | Không đổi API hay logic. |
| `api_contract` | Không | Không đổi hình dạng API. |
| `tests` | Không | Không có E2E cho admin. |
| `docs` | Không | Không ghi artifact vào docs. |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: thay đổi thuần giao diện, không thêm/sửa endpoint, field hay mã lỗi.
- Endpoint liên quan: chỉ dùng những gì admin đang gọi (`app/api/session/*` phía Next, giữ nguyên).

## 6. Vùng rủi ro và bất biến bị chạm

- Không chạm vùng rủi ro nào trong `AGENTS.md`. Không đọc/ghi dữ liệu sức khỏe, không đổi phân quyền, không có migration, không import giữa module backend.
- Bất biến 1 (client không gọi Supabase trực tiếp): giữ nguyên, task không thêm lời gọi mạng nào.
- Rủi ro riêng của task (không thuộc bảng AGENTS.md): (a) đổi token lan sang Login; (b) vô tình đổi logic khi sửa TSX. Xử lý bằng AC2, AC3.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given đã đăng nhập, When mở lần lượt `/dashboard`, `/dashboard/medications`, `/dashboard/interactions`, `/dashboard/ocr-review`, `/dashboard/scraper-logs` ở 1440px, Then mỗi trang có: nền gradient xanh, khung nội dung trắng bo góc lớn, sidebar xanh bo cong với mục đang chọn nổi bật, card trắng bóng mềm, font Open Sans; ảnh chụp lưu ở `evidence/`. | manual (so sánh thị giác với ảnh tham chiếu, không có test UI tự động) |
| AC2 | Given bản trước và sau task, When mở `/auth/login`, Then giao diện Login không thay đổi (ảnh chụp trước/sau trùng khớp; `git diff` không chạm `LoginForm.tsx`, `app/auth/**` và khối `.admin-login-*`). | manual + kiểm diff |
| AC3 | Given `git diff` của `frontend/admin`, When rà từng file `.tsx` bị sửa, Then chỉ đổi `className`, thẻ bao bọc thuần trình bày, `style` inline thuần trình bày, hoặc thuộc tính a11y; không đổi state, hook, handler, props, dữ liệu, chuỗi văn bản, import service. | manual (review diff) |
| AC4 | Given trang Danh mục thuốc và Quy tắc tương tác, When thực hiện tìm kiếm, lọc, đặt lại lọc, phân trang, mở form thêm/sửa, xem chi tiết, duyệt nhanh, xóa mềm + hoàn tác, mở drawer, Then mọi thao tác chạy như trước và Toast hiện với style mới. | manual |
| AC5 | Given bất kỳ trang dashboard nào, When điều hướng bằng bàn phím (Tab), Then mọi phần tử tương tác có focus ring nhìn rõ; chữ thường trên nền trắng và chữ trắng trên nền xanh/gradient đạt tương phản ≥ 4.5:1 (chữ lớn ≥ 3:1). | manual (DevTools contrast) |
| AC6 | Given cửa sổ 768px và 375px, When mở các trang dashboard, Then không có cuộn ngang toàn trang (bảng được cuộn ngang trong khung riêng), sidebar vẫn dùng được. | manual |
| AC7 | Given `prefers-reduced-motion: reduce`, When hover/mở modal, Then không còn animation chuyển động (chỉ đổi màu/opacity). | manual |
| AC8 | Given mã sau thay đổi, When chạy `npm run lint` và `npm run build` trong `frontend/admin`, Then cả hai thành công (lỗi đối chiếu với baseline trước task); log ở `evidence/`. | unit (lint/build) |

## 8. Câu hỏi mở

Không có (Q1–Q4 đã được người dùng xác nhận theo giả định mặc định ngày 2026-10-25, chuyển sang mục 9).

## 9. Giả định

- (Q1, người dùng xác nhận) Font khu dashboard là Open Sans, nạp qua `next/font/google` ở `app/dashboard/layout.tsx`, chỉ áp dụng trong `.admin-shell`; Login giữ font cũ.
- (Q2, người dùng xác nhận) Được sửa markup TSX ở mức trình bày (`className`, thẻ bao bọc, style inline thuần màu sắc, thuộc tính a11y), ràng buộc bởi AC3.
- (Q3, người dùng xác nhận) Không thêm phần tử không có trong app (ô Search, lời chào, widget ngày/thời tiết, biểu đồ); chỉ lấy ngôn ngữ thị giác của ảnh.
- (Q4, người dùng xác nhận) Giữ ngữ nghĩa màu mức độ nghiêm trọng và trạng thái (đỏ/xanh lá/cam), chỉ chỉnh tông cho hài hòa; badge luôn có chữ.
- Nhánh task: `feat/adhoc-20261025-admin-ui-redesign` ở superproject và `frontend` (theo `wf-git`); superproject hiện đang ở `feat/3.24-adherence-family-view`, `frontend` ở `main` — chưa tạo nhánh trong giai đoạn này.
- Ảnh tham chiếu chỉ là nguồn phong cách; bố cục thông tin của từng trang giữ như hiện tại.
- Văn bản giao diện giữ tiếng Việt như hiện có (không đổi sang chữ thường kiểu "home", "result" của ảnh).

## 10. Phát sinh

- `frontend/mobile/.env.example` đang ở trạng thái bị xóa (`D`) trong working tree của `frontend`, không do task này. Không đụng tới; cần lưu ý khi commit để không kéo theo.
- Superproject có thay đổi chưa commit ở `AGENTS.md`, `api_contract`, `backend`, `docs`, `frontend` từ việc khác.
- `scope.py --stage requirement` báo 38 file "ngoài phạm vi" (`.claude/rules/**`, `AGENTS.md`, 4 file trong `docs/`, `frontend/mobile/.env.example`, `graphify-out/**`). Tất cả là thay đổi có sẵn trước task này; task này chỉ ghi vào `work/adhoc-20261025-admin-ui-redesign/`. Log: `evidence/requirement-scope.log`. Nên tạo nhánh task sạch (hoặc commit/stash các thay đổi đó ở nhánh của chúng) trước giai đoạn implement.

## 11. Size

- `size`: M
- Lý do: không chạm vùng rủi ro, `contract_change: no`, một submodule; nhưng sửa CSS lớn (file 4000+ dòng) và nhiều component (> 3 file, > 50 dòng) nên không phải S.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261025-admin-ui-redesign requirement`; sau đó agent làm giai đoạn plan (`wf-plan`).
- Cập nhật lần cuối: 2026-10-25, Claude Code
