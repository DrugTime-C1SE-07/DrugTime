---
task: 5.07-admin-request-queue-ui
title: Admin dashboard - Hàng chờ yêu cầu xóa dữ liệu
type: feature
stage: requirement
size: M
contract_change: no
affected: [frontend]
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 14:27 +0700
content_hash: sha256:821055c7aa5e683a
---

# 5.07-admin-request-queue-ui · Hàng chờ yêu cầu xóa dữ liệu trên Admin Dashboard

## 1. Mục tiêu

Quản trị viên mở một trang trên Admin Dashboard để xem các yêu cầu xóa dữ liệu còn chờ duyệt, yêu cầu cũ nhất xếp trước, và làm mới được để thấy trạng thái hiện hành. Đặc tả kịch bản chi tiết: [spec.md](spec.md).

## 2. Phạm vi

### Trong phạm vi

- Mục "Yêu cầu xóa dữ liệu" trên sidebar (`frontend/admin/components/layout/Sidebar.tsx`) và trang mới dưới `frontend/admin/app/dashboard/`.
- Bảng chỉ đọc gồm bốn trường của contract: `id`, `user_id`, `requested_at` (hiển thị theo `Asia/Ho_Chi_Minh`), `status`. Hiển thị tổng số.
- Phân trang theo `skip`/`limit` (20 mục mỗi trang), về trang hợp lệ khi trang hiện tại vượt cuối.
- Nút làm mới thủ công.
- Các trạng thái: đang tải, rỗng, lỗi kèm thử lại, hết phiên (401), sai vai trò (403).
- Gọi API qua lớp có sẵn `frontend/admin/lib/api/client.ts` (`apiFetch`, phía server, token trong cookie httpOnly).

### Ngoài phạm vi

- Gửi yêu cầu xóa, rút đồng ý (luồng mobile, `POST /deletion-requests` còn TODO ở backend).
- Duyệt, từ chối, kích hoạt hay thực thi xóa (`POST /admin/deletion-requests/{id}/approve` còn TODO).
- Xem hồ sơ người gửi, tra cứu theo `user_id`, lọc, tìm kiếm, sắp xếp khác thứ tự backend.
- Tự động làm mới định kỳ (polling, push).
- Sửa backend, contract, migration.

## 3. Bối cảnh & nguồn đã đọc

| Nguồn (đường dẫn) | Điều rút ra |
|---|---|
| `docs/Team1_DTU/01_Proposal_&_Planning/Product-and-Sprint-backlog-DrugTime.ods` | Task gốc 5.07, PB35 (bản replan ghi 5.17). Dùng mã gốc, cùng quy ước với 5.06. |
| `work/5.06-admin-queue-api/01-requirement.md` | Nguồn nghiệp vụ UC25, UC26, QA.01 cho hàng chờ; 5.06 đã xong cả 6 giai đoạn. |
| `work/5.06-admin-queue-api/02-contract.md` (approved) | `GET /admin/deletion-requests`: `skip` ≥ 0 (mặc định 0), `limit` 1–100 (mặc định 20); `200 {items, total}`, `Cache-Control: no-store`; chỉ `cho_duyet`; sắp `requested_at` rồi `id` tăng dần; trang vượt cuối trả `items` rỗng + `total` hiện hành; `401`, `403 {"detail":"admin_only"}`, `422`, `503 {"detail":"service_unavailable"}`. |
| `backend/src/drugtime/modules/consent/adapters/inbound/http.py` (dòng 141, 173) | Endpoint đọc đã có. `POST /deletion-requests` và approve vẫn TODO. |
| `backend/tests/integration/test_admin_deletion_requests_api.py` | Hành vi API (lọc, thứ tự, phân trang, 401/403/503) đã có test tích hợp phía backend. |
| `frontend/admin/app/dashboard/` | Có trang medications, interactions, scraper-logs, ocr-review. Chưa có trang hàng chờ. |
| `frontend/admin/components/layout/Sidebar.tsx` | Danh mục điều hướng khai báo cứng; cần thêm một mục. |
| `frontend/admin/lib/api/client.ts` | `apiFetch` gọi từ server, ném `ApiError(status, code)`; dùng lại, không tạo client mới. |
| `frontend/admin/package.json` | Không có test runner chung. Có tiền lệ `node --test scripts/chart-geometry.test.mjs` cho logic thuần. |
| `docs/Team1_DTU/02_Requirements/drugtime_quyet_dinh_theo_chuc_nang.md` | Không có quyết định riêng về hàng chờ xóa dữ liệu (đã tìm "xóa dữ liệu", "deletion", "UC25", "UC26", "PB35"). |

### Quyết định nghiệp vụ áp dụng

| Nguồn và trạng thái | Quy tắc | AC |
|---|---|---|
| UC25, UC26 qua 5.06 (approved) | Admin xem danh sách yêu cầu xóa đang chờ, cũ trước. | AC1 |
| QA.01 qua 5.06 (approved) | Yêu cầu đã ghi nhận xuất hiện trong hàng chờ trong tối đa 60 giây. | AC7 |
| Contract 5.06 (approved) | Bốn trường, chỉ `cho_duyet`, thứ tự `requested_at` rồi `id`, phân trang offset, quyền Admin kiểm ở mỗi lượt gọi. | AC1, AC2, AC5 |
| Bất biến 4 và 7 trong `AGENTS.md` | Không cache quyết định phân quyền ở app; giờ theo `Asia/Ho_Chi_Minh`. | AC1, AC5 |
| `drugtime_quyet_dinh_theo_chuc_nang.md` | Không áp dụng: không có mục nào cho hàng chờ Admin. | — |

## 4. Submodule bị ảnh hưởng

| Submodule | Ảnh hưởng? | Lý do |
|---|---|---|
| `frontend` | Có | Trang mới, mục sidebar, hàm gọi API và logic phân trang trong `frontend/admin`. |
| `backend` | Không | Endpoint đọc đã có từ 5.06. |
| `api_contract` | Không | Chỉ dùng endpoint có sẵn. |
| `tests` | Không | Chưa có hạ tầng E2E cho Admin Web (xem Q1). |
| `docs` | Không | Chỉ tham chiếu; bộ test case Excel cập nhật ở giai đoạn test (`wf-testcase`). |

## 5. Thay đổi API contract

- `contract_change`: no
- Lý do: client chỉ dùng endpoint đã có, không đổi đường dẫn, tham số, field hay mã lỗi.
- Endpoint liên quan: chỉ dùng `GET /admin/deletion-requests?skip=&limit=`.

## 6. Vùng rủi ro và bất biến bị chạm

- Bất biến 1: Admin Web chỉ gọi Backend API; không thêm Supabase key hay truy cập trực tiếp.
- Bất biến 4: quyết định quyền đọc từ backend mỗi lượt; không lưu cờ "là admin" hay dữ liệu hàng chờ ở trình duyệt (`localStorage`, cache fetch).
- Bất biến 7: giờ hiển thị theo `Asia/Ho_Chi_Minh`.
- `user_id` là định danh cá nhân: chỉ hiển thị cho Admin, không ghi vào log trình duyệt hay URL.
- Vùng "Dữ liệu sức khỏe" và "Phân quyền người thân": không chạm. Endpoint chỉ trả metadata yêu cầu, không đọc lịch uống, liều hay hồ sơ y tế.

## 7. Tiêu chí chấp nhận

| ID | Given / When / Then | Mức test |
|---|---|---|
| AC1 | Given backend trả hai mục `cho_duyet` có cùng `requested_at` và khác `id`, When Admin mở trang hàng chờ, Then bảng hiển thị đủ bốn trường, giờ dạng `dd/MM/yyyy HH:mm` theo `Asia/Ho_Chi_Minh`, giữ đúng thứ tự backend trả về, và hiển thị `total`. | unit (định dạng giờ, ánh xạ dòng) + manual (trang thật với API local) |
| AC2 | Given `total` = 45 và 20 mục mỗi trang, When Admin sang trang 3 rồi quay lại trang 1, Then gọi API với `skip` = 40 rồi `skip` = 0, `limit` = 20, có 3 trang. Given đang ở trang 3 mà lượt tải mới trả `items` rỗng và `total` = 30, Then về trang 2 và tải lại. | unit |
| AC3 | Given một mục đã rời hàng chờ và một mục mới được tạo sau lần tải trước, When Admin bấm làm mới, Then danh sách và `total` phản ánh trạng thái hiện hành, không dùng kết quả cũ. | manual (dữ liệu seed trong DB local) |
| AC4 | Given lượt tải đang chạy, trả rỗng, hoặc trả `503`/lỗi mạng, When trang hiển thị, Then lần lượt thấy trạng thái đang tải, thông báo "Không có yêu cầu chờ duyệt", và thông báo lỗi có nút thử lại; khi API phục hồi, bấm thử lại hiển thị danh sách. | unit (ánh xạ kết quả/lỗi sang trạng thái) + manual |
| AC5 | Given API trả `401` (phiên hết hạn) hoặc `403 admin_only`, When mở hoặc làm mới trang, Then `401` đưa về luồng đăng nhập có sẵn, `403` hiển thị thông báo không có quyền; cả hai không hiển thị dòng nào hay `total`, kể cả dữ liệu đã tải trước đó. | unit (ánh xạ lỗi) + manual |
| AC6 | Given chỉ dùng bàn phím, When điều hướng tới mục sidebar, chuyển trang, làm mới, thử lại, Then mọi nút đều focus và kích hoạt được; `user_id` (UUID 36 ký tự) hiển thị đầy đủ, không bị cắt. | manual (trình duyệt) |
| AC7 | Given một yêu cầu `cho_duyet` được chèn vào DB, When Admin làm mới trong vòng 60 giây, Then yêu cầu xuất hiện. | manual (chèn dữ liệu seed vì `POST /deletion-requests` chưa có; xem Q3) |
| AC8 | Given trang đã build, When chạy `npm run lint` và `npm run build` trong `frontend/admin`, Then không có lỗi. | unit (lint/build) |

## 8. Câu hỏi mở

```
Q1 [không chặn] Kiểm thử UI ở mức nào khi Admin Web chưa có test runner?
- Ảnh hưởng: mức test của AC1–AC5 và việc có thêm dependency hay không.
- Lựa chọn: A) logic thuần (phân trang, định dạng giờ, ánh xạ lỗi) tách thành module, test bằng `node --test` như `test:chart`, phần còn lại kiểm tay trên API local / B) thêm Vitest + Testing Library hoặc Playwright.
- Giả định mặc định: A. Hành vi API đã có test tích hợp ở backend từ 5.06. Nếu nhánh `feat/adhoc-20261028-admin-live-api` (có `tests/unit/*.test.ts` + `tsconfig.test.json`) được merge vào `main` của `frontend` trước, dùng hạ tầng đó thay cho `node --test` trên `.mjs`.

Q2 [không chặn] Kích thước trang và cách làm mới?
- Ảnh hưởng: AC2, AC3.
- Lựa chọn: A) 20 mục mỗi trang (mặc định contract), làm mới thủ công / B) cỡ trang khác hoặc tự làm mới định kỳ.
- Giả định mặc định: A.

Q3 [không chặn] AC7 (mốc 60 giây của QA.01) kiểm bằng gì khi `POST /deletion-requests` chưa có?
- Ảnh hưởng: AC7 có kiểm đầy đủ trong task này hay chuyển sang task làm luồng gửi yêu cầu.
- Lựa chọn: A) chèn dữ liệu seed vào DB local rồi làm mới; kiểm đầu-cuối khi có luồng gửi / B) chờ luồng gửi xong mới đóng task.
- Giả định mặc định: A.
```

## 9. Giả định

- UI chỉ đọc; không có nút duyệt/từ chối, kể cả dạng vô hiệu.
- Dữ liệu tải ở server component hoặc route handler qua `apiFetch` với `cache: "no-store"`, theo cách các trang dashboard hiện có đang làm.
- Nhãn sidebar: "Yêu cầu xóa dữ liệu"; đường dẫn `/dashboard/deletion-requests`.

## 10. Phát sinh

- Draft trước (2026-11-17) ghi `scope.py` báo 1.268 file ngoài task do workspace đang ở nhánh `feat/adhoc-20261118-mobile-profile-flow-ui` với nhiều thay đổi chưa commit. Cần nhánh `feat/5.07-admin-request-queue-ui` riêng (skill `wf-git`) trước khi implement.
- `.specify/feature.json` (Spec Kit) nằm ngoài `work/`; không thuộc artifact quy trình.
- `python .agents/scripts/scope.py 5.07-admin-request-queue-ui --stage requirement` (2026-11-19): exit 1, 1.659 file ngoài phạm vi, không file nào do task này sửa. Gồm `graphify-out/` (1.538), `.claude/rules` (28), `my-project/` (30), `.specify/` (18), `.agents/skills/speckit-*` (10), `frontend/admin/.test-build/` (13), backlog `.ods`/`.xlsx` trong `docs` (2). [Log](evidence/requirement-scope.log). Cần dọn hoặc `.gitignore` các mục này, hoặc làm task trên nhánh sạch.
- Hạ tầng unit test của Admin Web (`tests/unit`, `tsconfig.test.json`) chỉ có trên nhánh chưa merge `feat/adhoc-20261028-admin-live-api` của `frontend` (commit `85ff2ab3`). Liên quan Q1.
- Gate requirement: OK. [Log](evidence/requirement-gate.log)

## 11. Size

- `size`: M
- Lý do: một submodule (`frontend`), không đổi contract, không migration; nhưng màn hình mới có nhiều trạng thái (tải, rỗng, lỗi, 401, 403, phân trang) và hiển thị định danh cá nhân, vượt mức khoảng 3 file / 50 dòng của size S.

## Bước tiếp theo

- Đang chờ: người duyệt (Q1–Q3 không chặn, sẽ theo giả định mặc định nếu không có ý kiến khác).
- Việc cần làm: xem file này và [checklist yêu cầu](checklists/requirements.md), rồi chạy `python .agents/scripts/gate.py approve 5.07-admin-request-queue-ui requirement`. Giai đoạn kế tiếp: plan (`wf-plan`).
- Cập nhật lần cuối: 2026-11-19, Claude Code
