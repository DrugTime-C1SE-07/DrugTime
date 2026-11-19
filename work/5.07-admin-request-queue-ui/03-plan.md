---
task: 5.07-admin-request-queue-ui
stage: plan
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 14:31 +0700
content_hash: sha256:85421c949dc367bb
inputs:
  01-requirement.md: sha256:821055c7aa5e683a
---

# 5.07-admin-request-queue-ui · Plan

## 1. Giải pháp

**Luồng dữ liệu.** Trang `/dashboard/deletion-requests` là **server component**. Mỗi lần render, trang đọc `?page=N`, gọi `GET /admin/deletion-requests?skip=(N-1)*20&limit=20` qua `apiFetchWithSession` (token lấy từ cookie httpOnly, `cache: "no-store"`) rồi trả HTML. Trình duyệt không giữ token, không giữ cờ quyền, không cache dữ liệu hàng chờ (bất biến 1 và 4).

**Thành phần.**

- `lib/deletion-requests/queue.ts`: hàm thuần, không import `next/*`, để test bằng `node --test` (Node ≥ 22.18 import trực tiếp `.ts`, tiền lệ `scripts/chart-geometry.test.mjs`):
  - `PAGE_SIZE = 20`; `parsePage(raw)` trả số nguyên ≥ 1 (giá trị sai hoặc thiếu thì về 1); `skipFor(page)`; `pageCount(total)` (tối thiểu 1).
  - `overflowTarget(page, total, itemCount)`: trả số trang hợp lệ cuối cùng khi `itemCount === 0 && total > 0 && page > pageCount(total)`, ngược lại `null`.
  - `formatRequestedAt(iso)`: `dd/MM/yyyy HH:mm` theo `Asia/Ho_Chi_Minh` qua `Intl.DateTimeFormat`.
  - `queueErrorView(status)`: `401` thành `session_expired`, `403` thành `forbidden`, còn lại (gồm `422`, `503`, lỗi mạng) thành `unavailable`.
  - Kiểu `DeletionRequest { id: number; user_id: string; requested_at: string; status: "cho_duyet" }`, `DeletionQueuePage { items; total }`.
- `lib/api/deletion-requests.ts`: `fetchDeletionQueue(page)` gọi `apiFetchWithSession` với `method: "GET"`.
- `app/dashboard/deletion-requests/page.tsx`: gọi `fetchDeletionQueue`.
  - Thành công: nếu `overflowTarget` khác `null` thì `redirect("?page=<target>")`; nếu không thì render bảng, tổng số và phân trang (các `<Link>` Trước/Sau và "Trang X / Y").
  - `ApiError`: render khối trạng thái theo `queueErrorView`, **không** render bảng hay tổng số.
- `app/dashboard/deletion-requests/loading.tsx`: trạng thái đang tải khi điều hướng vào trang hoặc chuyển trang.
- `components/deletion-requests/DeletionQueueTable.tsx`: bảng bốn cột. `user_id` dùng font mono, `overflow-wrap: anywhere`, không cắt.
- `components/deletion-requests/RefreshButton.tsx` (client): `router.refresh()` trong `useTransition`, hiện "Đang tải…" và `aria-busy` khi đang chạy. Nút này dùng cho cả "Làm mới" và "Thử lại".
- `components/deletion-requests/QueueStatus.tsx`: các khối rỗng, `unavailable` (kèm `RefreshButton`), `forbidden` và `session_expired` (kèm `LogoutButton` có sẵn để xóa cookie và về `/auth/login`).
- `Sidebar.tsx`: thêm mục "Yêu cầu xóa dữ liệu" (icon `Trash2` của `lucide-react`, đã cài).

**Vì sao chọn server component thay vì client component cộng route handler proxy.** Đây là cách ít code nhất: không thêm route `app/api/**`. Không có phản hồi cũ đến muộn ghi đè dữ liệu (AC5), vì mỗi lần refresh trả về một cây mới từ server. Phân trang bằng URL nên dùng được với bàn phím và nút Back.

**Xử lý 401.** Không `redirect("/auth/login")` từ trang. Khi backend trả 401 mà cookie chưa tới hạn, middleware sẽ đẩy `/auth/login` về lại `/dashboard`, tạo vòng lặp. Trang hiện thông báo kèm `LogoutButton`; nút này gọi `/api/session/logout` để xóa cookie rồi điều hướng tới trang đăng nhập.

### Quyết định nghiệp vụ áp dụng

Đã đối chiếu lại `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` (bản trong checkout hiện tại) với các từ khóa "xóa dữ liệu", "deletion", "UC25", "UC26", "PB35". Không có quyết định nào cho hàng chờ Admin. Nguồn nghiệp vụ là 5.06 (approved), giữ nguyên như mục 3 của `01`.

| Quy tắc (nguồn) | AC | Bước | Test |
|---|---|---|---|
| UC25/UC26: Admin xem yêu cầu chờ, cũ trước (5.06 `01`) | AC1 | P3, P4, P5 | `formatRequestedAt …`, kiểm tay M1 |
| QA.01: yêu cầu xuất hiện ≤ 60 giây (5.06 `01`) | AC7 | P5, P8 | kiểm tay M4 |
| Contract 5.06: `skip`/`limit`, trang vượt cuối trả rỗng + `total` | AC2 | P2, P5 | `skipFor …`, `pageCount …`, `overflowTarget …` |
| Contract 5.06: `401`, `403 admin_only`, `503` | AC4, AC5 | P2, P5 | `queueErrorView …`, kiểm tay M3 |
| Bất biến 4, 7 trong `AGENTS.md` | AC1, AC5 | P3, P5 | `formatRequestedAt …`, kiểm tay M3 |

## 2. Khảo sát

| File đã đọc | Điều rút ra |
|---|---|
| `work/5.07-admin-request-queue-ui/01-requirement.md` (approved) | 8 AC; Q1–Q3 theo mặc định: `node --test` cho logic thuần, 20 mục mỗi trang, làm mới thủ công, AC7 kiểm bằng dữ liệu seed. |
| `work/5.06-admin-queue-api/02-contract.md` (approved) | Hình dạng response và mã lỗi (đã tóm ở `01` mục 3). |
| `frontend/admin/lib/api/client.ts` | `apiFetchWithSession` ném `ApiError(401)` khi thiếu cookie; `apiFetch` ánh xạ lỗi mạng thành `ApiError(503)`; mặc định `method: "POST"` nên phải truyền `GET`. |
| `frontend/admin/middleware.ts` | Chỉ kiểm có phiên và hạn phiên; quyền admin do backend quyết. Không redirect về login khi cookie còn hạn. |
| `frontend/admin/app/dashboard/layout.tsx` | Shell có sẵn (Sidebar, Topbar, Toast, SessionKeepAlive); trang con chỉ render nội dung. |
| `frontend/admin/components/layout/Sidebar.tsx` | Mảng `sidebarItems` khai báo cứng, icon `lucide-react`. |
| `frontend/admin/components/auth/LogoutButton.tsx` | Gọi `POST /api/session/logout` rồi `window.location.assign("/auth/login")`; dùng lại cho trường hợp 401. |
| `frontend/admin/app/api/session/refresh/route.ts` | Mẫu ánh xạ lỗi sang mã cho trình duyệt; không cần route mới. |
| `frontend/admin/app/dashboard/scraper-logs/page.tsx`, `medications/page.tsx` | Trên `main` chưa trang nào đọc API thật (medications dùng mock). Trang này là trang đầu tiên gọi API thật qua server component. |
| `frontend/admin/lib/api/*.ts` (trừ `client.ts`) | Các file đều rỗng (0 dòng); không có helper gọi danh sách nào để dùng lại. |
| `frontend/admin/scripts/chart-geometry.test.mjs`, `package.json` | `node --test` import trực tiếp `.ts`; script `test:chart`. Node local là v24.22.2. |
| `frontend/admin/app/dashboard/dashboard-theme.css` | Mọi selector nằm dưới `.admin-theme`; thêm style cho trang mới vào đây. |

## 3. File sẽ thay đổi (ranh giới phạm vi)

<!-- scope.py đọc bảng này. Đường dẫn tính từ gốc submodule; được dùng glob, ví dụ `src/<module>/auth/**`. -->

| Submodule | Đường dẫn | Thêm / sửa / xóa | Mục đích |
|---|---|---|---|
| frontend | `admin/lib/deletion-requests/queue.ts` | thêm | Hàm thuần: phân trang, trang vượt cuối, định dạng giờ, ánh xạ lỗi; kiểu dữ liệu |
| frontend | `admin/lib/api/deletion-requests.ts` | thêm | `fetchDeletionQueue(page)` qua `apiFetchWithSession` |
| frontend | `admin/app/dashboard/deletion-requests/page.tsx` | thêm | Server component của trang hàng chờ |
| frontend | `admin/app/dashboard/deletion-requests/loading.tsx` | thêm | Trạng thái đang tải |
| frontend | `admin/components/deletion-requests/**` | thêm | `DeletionQueueTable`, `RefreshButton`, `QueueStatus` |
| frontend | `admin/components/layout/Sidebar.tsx` | sửa | Thêm mục "Yêu cầu xóa dữ liệu" |
| frontend | `admin/app/dashboard/dashboard-theme.css` | sửa | Style bảng, phân trang, khối trạng thái |
| frontend | `admin/scripts/deletion-queue.test.mjs` | thêm | Unit test cho `queue.ts` |
| frontend | `admin/package.json` | sửa | Script `test:deletion-queue` |

## 4. Checklist

- [ ] P1 [frontend] Tạo nhánh `feat/5.07-admin-request-queue-ui` từ `origin/main` trong `frontend` và superproject theo `wf-git` — file: không — AC: — — xong khi: `git -C frontend branch --show-current` in tên nhánh, `git status` sạch trong `frontend/admin`
- [ ] P2 [frontend] Viết test RED cho `parsePage`, `skipFor`, `pageCount`, `overflowTarget`, `queueErrorView` — file: `admin/scripts/deletion-queue.test.mjs`, `admin/package.json` — AC: AC2, AC4, AC5 — xong khi: `npm run test:deletion-queue` fail vì chưa có module
- [ ] P3 [frontend] Viết test RED cho `formatRequestedAt` (UTC 17:30 ra 00:30 ngày hôm sau theo giờ VN; chuỗi có offset `+07:00`) — file: `admin/scripts/deletion-queue.test.mjs` — AC: AC1 — xong khi: test fail
- [ ] P4 [frontend] Cài đặt `queue.ts` cho tới khi P2 và P3 pass — file: `admin/lib/deletion-requests/queue.ts` — AC: AC1, AC2, AC4, AC5 — xong khi: `npm run test:deletion-queue` pass, log lưu ở `evidence/implement-unit.log`
- [ ] P5 [frontend] `fetchDeletionQueue` cùng trang server component: thành công, trang vượt cuối thì `redirect`, `ApiError` thì render khối trạng thái không kèm dữ liệu; `loading.tsx` — file: `admin/lib/api/deletion-requests.ts`, `admin/app/dashboard/deletion-requests/page.tsx`, `admin/app/dashboard/deletion-requests/loading.tsx` — AC: AC1, AC2, AC4, AC5, AC7 — xong khi: `npx tsc --noEmit` không lỗi
- [ ] P6 [frontend] Các component `DeletionQueueTable`, `RefreshButton`, `QueueStatus` và style — file: `admin/components/deletion-requests/**`, `admin/app/dashboard/dashboard-theme.css` — AC: AC1, AC3, AC4, AC5, AC6 — xong khi: trang render được với API local
- [ ] P7 [frontend] Thêm mục sidebar — file: `admin/components/layout/Sidebar.tsx` — AC: AC6 — xong khi: mục hiện ra và ở trạng thái active tại `/dashboard/deletion-requests`
- [ ] P8 [frontend] Lint, build, kiểm tay M1–M5 trên API local (backend `supabase db reset` cộng dữ liệu seed) — file: không — AC: AC1, AC3–AC8 — xong khi: `npm run lint` và `npm run build` không lỗi (log ở `evidence/implement-lint.log`, `evidence/implement-build.log`), kết quả M1–M5 ghi trong `04-impl-notes.md`
- [ ] P9 [frontend] `scope.py --stage implement` chỉ báo file trong bảng mục 3 — file: không — AC: — — xong khi: không còn file nào của task bị báo ngoài phạm vi

## 5. Test

### Unit

Chạy bằng `cd frontend/admin && npm run test:deletion-queue`, file `admin/scripts/deletion-queue.test.mjs`.

| Test dự kiến | AC | Submodule |
|---|---|---|
| `parsePage`: `undefined`, `"0"`, `"-1"`, `"abc"`, `"2.5"` cho ra 1; `"3"` cho ra 3 | AC2 | frontend |
| `skipFor`: trang 1 cho 0, trang 3 cho 40 | AC2 | frontend |
| `pageCount`: total 0 cho 1, 20 cho 1, 21 cho 2, 45 cho 3 | AC2 | frontend |
| `overflowTarget`: (3, 30, 0) cho 2; (3, 45, 5) cho `null`; (2, 0, 0) cho `null`; (1, 0, 0) cho `null` | AC2 | frontend |
| `formatRequestedAt`: `2026-11-18T17:30:00Z` ra `19/11/2026 00:30`; `2026-11-19T08:05:00+07:00` ra `19/11/2026 08:05` | AC1 | frontend |
| `queueErrorView`: 401 ra `session_expired`; 403 ra `forbidden`; 422, 500, 503 ra `unavailable` | AC4, AC5 | frontend |

### Tích hợp

Admin Web chưa có hạ tầng E2E (Q1 của `01`, đã duyệt theo mặc định). Hành vi API đã có test tích hợp ở `backend/tests/integration/test_admin_deletion_requests_api.py` từ 5.06. Task này không sửa backend nên không có test tích hợp mới; chạy lại file đó một lần để xác nhận endpoint vẫn đúng.

Phần giao diện kiểm tay trên trình duyệt với backend local, kết quả ghi vào `04-impl-notes.md`:

| Test dự kiến | AC / kịch bản chất lượng | Ghi chú |
|---|---|---|
| `pytest tests/integration/test_admin_deletion_requests_api.py` | AC1, AC2, AC5 (phía API) | Chạy lại, không sửa |
| M1: seed 45 yêu cầu `cho_duyet`, gồm 2 yêu cầu trùng `requested_at`, cùng vài trạng thái khác. Mở trang: 20 dòng, đúng thứ tự, giờ VN, total 45, sang trang 3 rồi về trang 1 | AC1, AC2 | |
| M2: đang ở trang 3, chuyển 20 dòng sang trạng thái khác, bấm "Làm mới": về trang 2 | AC2, AC3 | |
| M3: tắt backend thì thấy lỗi và nút "Thử lại", bật lại rồi thử lại thì thấy danh sách. Đăng nhập tài khoản không phải admin (hoặc gỡ quyền admin trong DB) rồi làm mới: thông báo không có quyền, không có dòng hay total. Thu hồi phiên ở backend rồi làm mới: thông báo hết phiên, bấm đăng nhập lại về `/auth/login` | AC4, AC5 | Rút quyền có hiệu lực ở request kế tiếp |
| M4: chèn 1 yêu cầu `cho_duyet` mới, bấm làm mới trong vòng 60 giây: yêu cầu xuất hiện | AC7 | Dữ liệu seed, vì `POST /deletion-requests` chưa có |
| M5: chỉ dùng bàn phím (Tab, Enter): sidebar, phân trang, làm mới, thử lại; `user_id` hiển thị đủ 36 ký tự | AC6 | |

## 6. Migration

Không có. Task không đổi schema.

## 7. Nhánh git

| Submodule | Nhánh |
|---|---|
| superproject | `feat/5.07-admin-request-queue-ui` |
| frontend | `feat/5.07-admin-request-queue-ui` |

## 8. Rủi ro

- **Workspace bẩn.** `scope.py` đang báo 1.659 file ngoài phạm vi, phần lớn do `graphify-out/`, `my-project/`, `.specify/` và `frontend/admin/.test-build/`, và superproject đang đứng ở nhánh task khác. Giảm thiểu: P1 tạo nhánh mới từ `origin/main`; các thư mục trên phải được người dùng dọn hoặc đưa vào `.gitignore` trước P9, nếu không scope check sẽ không sạch (xem mục 10).
- **Xung đột với nhánh chưa merge `feat/adhoc-20261028-admin-live-api`.** Nhánh đó sửa `Sidebar.tsx`, `layout.tsx` và thêm `tests/unit`. Nếu nó merge trước, `Sidebar.tsx` có thể xung đột. Phát hiện bằng `git merge-tree` khi mở PR; xung đột chỉ ở một mục trong mảng nên dễ gộp.
- **Định dạng giờ khác nhau giữa Node và trình duyệt.** Chuỗi `Intl` với locale `vi-VN` có thể khác dấu phân cách giữa các phiên bản ICU. Giảm thiểu: dựng chuỗi từ `formatToParts` thay vì dùng `format()`; có test unit cho đầu ra cố định.
- **Vòng lặp chuyển hướng khi gặp 401.** Đã tránh bằng `LogoutButton` (xem mục 1). M3 kiểm trực tiếp.
- **Lộ `user_id`.** Trang chỉ render ở server sau khi backend xác nhận quyền admin. Không ghi `user_id` vào `console` hay URL; phân trang chỉ mang `page`.

## 9. Câu hỏi mở

Không có. Q1–Q3 của `01` đã duyệt theo mặc định.

## 10. Phát sinh

- Mục "Phát sinh" của `01` vẫn còn hiệu lực: 1.659 file ngoài phạm vi, chưa có file nào của task. Cần người dùng quyết dọn hay đưa vào `.gitignore` các mục `graphify-out/`, `my-project/`, `.specify/`, `frontend/admin/.test-build/` trước giai đoạn implement.
- Ngoài ra còn các thay đổi chưa commit thuộc task khác: `.gitignore`, `AGENTS.md`, `Test_Plan.md`, `.claude/launch.json` và `frontend/mobile/lib/app/app_preview_session.dart`. Cần commit hoặc stash các file này trên nhánh của chúng trước P1.
- `python .agents/scripts/scope.py 5.07-admin-request-queue-ui --stage plan` (2026-11-19): exit 1, 1.659 file ngoài phạm vi; task này chỉ ghi vào `work/`. [Log](evidence/plan-scope.log)
- Gate plan: OK. [Log](evidence/plan-gate.log)

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: xem plan rồi chạy `python .agents/scripts/gate.py approve 5.07-admin-request-queue-ui plan`. Giai đoạn kế tiếp là implement (`wf-implement`), bắt đầu từ P1.
- Cập nhật lần cuối: 2026-11-19, Claude Code
