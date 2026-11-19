---
task: 5.07-admin-request-queue-ui
stage: implement
owner: Ngọc Việt
started_at: 2026-11-19 14:36
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 14:53 +0700
content_hash: sha256:79a97af4212edd02
inputs:
  01-requirement.md: sha256:821055c7aa5e683a
  03-plan.md: sha256:85421c949dc367bb
---

# 5.07-admin-request-queue-ui · Implement

## 1. Tiến độ

| Bước | Trạng thái | Lệnh kiểm tra và kết quả | Log |
|---|---|---|---|
| P1 | xong | Stash WIP ở superproject và `frontend`, rồi `git switch -c feat/5.07-admin-request-queue-ui` từ `origin/main` (`frontend` tại `4baf32d0`). `git status` trong `frontend/admin` sạch trước khi sửa. | — |
| P2 | xong | `npm run test:deletion-queue` fail (RED): `ERR_MODULE_NOT_FOUND ... lib\deletion-requests\queue.ts` | `evidence/implement-P2.log` |
| P3 | xong | Test `formatRequestedAt` nằm trong cùng file test và fail cùng lượt RED của P2 | `evidence/implement-P2.log` |
| P4 | xong | `npm run test:deletion-queue`: 8 pass, 0 fail | `evidence/implement-unit.log` |
| P5 | xong | `npx tsc --noEmit`: exit 0 (chạy lại sau `next build`). Lần chạy đầu chỉ lỗi ở `.next/types` cũ của nhánh khác, không có lỗi trong code. | `evidence/implement-P5.log` |
| P6 | xong một phần | Component và style đã viết; build OK. Chưa render với API local (xem P8). | — |
| P7 | xong | Mục sidebar có trong `sidebarItems`; build OK. Trạng thái active chưa xem trên trình duyệt (xem P8). | — |
| P8 | xong một phần | `npm run lint`: exit 0. `npm run build`: exit 0, route `ƒ /dashboard/deletion-requests` (dynamic). **Chưa kiểm tay M1–M5** vì máy này không có `docker` và `supabase` CLI để chạy backend local (mục 6). | `evidence/implement-lint.log`, `evidence/implement-build.log` |
| P9 | xong | `scope.py --stage implement`: 11 file của task đều `[OK]`; 13 file `[NGOÀI]` là thay đổi sẵn có, không thuộc task (mục 6). | `evidence/implement-scope.log` |

## 2. File đã thay đổi

| Submodule | Nhánh | File |
|---|---|---|
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/lib/deletion-requests/queue.ts` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/lib/api/deletion-requests.ts` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/app/dashboard/deletion-requests/page.tsx` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/app/dashboard/deletion-requests/loading.tsx` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/components/deletion-requests/DeletionQueueTable.tsx` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/components/deletion-requests/RefreshButton.tsx` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/components/deletion-requests/QueueStatus.tsx` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/components/layout/Sidebar.tsx` (sửa) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/app/dashboard/dashboard-theme.css` (sửa, thêm khối `.deletion-queue*` ở cuối file) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/scripts/deletion-queue.test.mjs` (thêm) |
| frontend | `feat/5.07-admin-request-queue-ui` | `admin/package.json` (sửa, thêm script `test:deletion-queue`) |

Kết quả `python .agents/scripts/scope.py 5.07-admin-request-queue-ui --stage implement`: exit 1. Mọi file của task đều `[OK]`; 13 file `[NGOÀI]` không thuộc task (mục 6). Log: `evidence/implement-scope.log`

## 3. Kết quả test cuối

| Submodule | Lệnh | Kết quả (pass/fail/skip) | Log |
|---|---|---|---|
| frontend | `npm run test:deletion-queue` | 8 / 0 / 0 | `evidence/implement-final-frontend.log` |
| frontend | `npm run test:chart` (test có sẵn) | 12 / 0 / 0 | `evidence/implement-final-frontend.log` |
| frontend | `npm run lint` | exit 0 | `evidence/implement-lint.log` |
| frontend | `npm run build` | exit 0 | `evidence/implement-build.log` |
| backend | `pytest tests/integration/test_admin_deletion_requests_api.py` | chưa chạy (không có Supabase local) | — |

Truy vết quy tắc nghiệp vụ đã thực hiện:

| Quy tắc | AC | Đã làm | Bằng chứng |
|---|---|---|---|
| UC25/UC26: xem yêu cầu chờ, cũ trước | AC1 | Bảng giữ nguyên thứ tự backend trả về; giờ theo `Asia/Ho_Chi_Minh` | Unit `formatRequestedAt`; M1 chưa chạy |
| Contract 5.06: `skip`/`limit`, trang vượt cuối | AC2 | `parsePage`, `skipFor`, `pageCount`, `overflowTarget`, `redirect` | Unit 4 nhóm; M1, M2 chưa chạy |
| Contract 5.06: `401`/`403`/`503` | AC4, AC5 | `queueErrorView`; `QueueStatus` không render dòng hay tổng số khi lỗi | Unit `queueErrorView`; M3 chưa chạy |
| QA.01: tối đa 60 giây | AC7 | Trang `force-dynamic`, `apiFetch` dùng `no-store`, nút làm mới | M4 chưa chạy |
| Bất biến 1, 4 | AC5 | Chỉ gọi Backend API từ server; không lưu quyền hay dữ liệu ở trình duyệt | Đọc code; M3 chưa chạy |

## 3b. Bộ test case Excel (chỉ task size S)

Làm ở giai đoạn test.

## 4. Migration

Không có.

## 5. Ghi chú cho người review

- Trang là server component với `export const dynamic = "force-dynamic"`. Phân trang dùng `?page=N`; "Làm mới" và "Thử lại" gọi `router.refresh()`.
- Lỗi 401 không redirect thẳng về `/auth/login`: nếu cookie còn hạn, middleware sẽ đẩy về lại `/dashboard`. Thay vào đó trang hiện thông báo kèm `LogoutButton` có sẵn. `LogoutButton` chỉ là nút icon (`aria-label="Đăng xuất"`); file này ngoài phạm vi nên không đổi thành nút có chữ.
- `formatRequestedAt` dựng chuỗi từ `formatToParts` với locale `en-GB` và `hourCycle: "h23"` để không phụ thuộc dấu phân cách của ICU.
- `lib/deletion-requests/queue.ts` không import gì, để `node --test` import trực tiếp được (Node ≥ 22.18; máy chạy là v24.22.2).
- Bảng dùng `<table>`, `<caption>` ẩn và `<th scope="col">`; `user_id` có `overflow-wrap: anywhere` để không bị cắt (AC6).

## 6. Phát sinh

- Stash trước khi tạo nhánh (người dùng yêu cầu): superproject `stash@{0}` "wip before 5.07-admin-request-queue-ui (from feat/adhoc-20261118-mobile-profile-flow-ui)"; `frontend` `stash@{0}` "wip before 5.07-admin-request-queue-ui" (tạo khi đang detached HEAD). Lấy lại bằng `git stash pop` trên nhánh tương ứng.
- **M1–M5 và test tích hợp backend chưa chạy.** Máy này không có `docker` và `supabase` CLI, `frontend/admin` không có `.env.local` (`DRUGTIME_API_BASE_URL`). Không dùng `backend/.env` vì có thể trỏ tới DB dùng chung, và M1–M4 cần seed hoặc sửa dữ liệu. Cần người có môi trường local chạy M1–M5 theo mục 5 của `03-plan.md`, hoặc chạy ở giai đoạn test.
- `scope.py` báo 13 file `[NGOÀI]`, không file nào thuộc task: 10 file `.agents/skills/speckit-*/SKILL.md` (chưa track trong submodule `.agents`), `.specify/feature.json` (Spec Kit tạo lại sau khi stash), và 2 file backlog `.ods`/`.xlsx` (thay đổi sẵn có trong submodule `docs`). Không đụng tới vì là thay đổi của người dùng.
- Superproject đang ở nhánh `feat/5.07-admin-request-queue-ui` và theo dõi `origin/main` (do `switch -c ... origin/main`). Khi push lần đầu, dùng `git push -u origin feat/5.07-admin-request-queue-ui`.

## Bước tiếp theo

- Quyết định của người dùng (2026-11-19): dời kiểm tay M1–M5 và test tích hợp backend sang giai đoạn test (`05-test-report.md`), chạy trên môi trường có backend local.
- Đang chờ: người duyệt.
- Việc cần làm: chạy `python .agents/scripts/gate.py approve 5.07-admin-request-queue-ui implement`, rồi bắt đầu giai đoạn test (`wf-test`). Chưa commit; khi được yêu cầu thì commit `frontend` theo `wf-git` trước, rồi bump con trỏ ở superproject.
- Cập nhật lần cuối: 2026-11-19 14:45, Claude Code
