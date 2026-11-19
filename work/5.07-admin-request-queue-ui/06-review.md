---
task: 5.07-admin-request-queue-ui
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-19 15:28 +0700
content_hash: sha256:0efedd4f16f39e9d
inputs:
  01-requirement.md: sha256:821055c7aa5e683a
  03-plan.md: sha256:85421c949dc367bb
  04-impl-notes.md: sha256:79a97af4212edd02
  05-test-report.md: sha256:cb7c4abe5a130e7d
---

# 5.07-admin-request-queue-ui · Review

## 1. Kết luận

**Đạt, kèm lưu ý.** Không có phát hiện Critical hay High. Có 2 phát hiện Medium và 3 phát hiện Low (mục 4).

Lưu ý về tính độc lập: review này do cùng tool và cùng phiên đã implement thực hiện (Claude Code). Thứ tự đọc vẫn theo skill: diff trước, `04`/`05` sau. Người review PR theo Definition of Done nên xem kỹ phát hiện M1.

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| frontend | `git -C frontend diff origin/main` (3 file sửa) và đọc trọn 8 file mới chưa track. Code chưa commit nên không dùng được `main...HEAD`. Base: `origin/main` `4baf32d0` |
| docs | `git -C docs diff --stat`: `Test_Cases.xlsx` (merge bộ test case). File backlog `.xlsx` bị xóa là thay đổi sẵn có của người dùng, không thuộc task |

Kết quả `scope.py --stage implement`: 11 file của task đều `[OK]`; 13 file `[NGOÀI]` không thuộc task (speckit, `.specify/feature.json`, backlog). Đã ghi ở `04` mục 6. Log: `evidence/implement-scope.log`.

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | AC1–AC6 và AC8 có code đáp ứng.<br>AC5, nhánh 401: hiện thông báo kèm `LogoutButton`, không chuyển thẳng về đăng nhập. Lệch câu chữ AC nhưng đã thống nhất trong `03` mục 1 (L1).<br>AC7 và trạng thái đang tải của AC4 chưa được chứng minh (M2). |
| Phạm vi | Đúng bảng "File sẽ thay đổi". Không có file thừa. |
| Contract | Gọi `GET /admin/deletion-requests?skip&limit` với `method: "GET"`. Kiểu `{items,total}` và bốn trường khớp contract 5.06. 401/403/422/503 đều được ánh xạ: `queue.ts:71-75`. |
| Bất biến kiến trúc | 1: chỉ gọi Backend API từ server; không key, không Supabase.<br>4: `force-dynamic`, `apiFetch` dùng `no-store`, không lưu quyền. Riêng router cache phía client, xem M1.<br>7: `Asia/Ho_Chi_Minh` ở `queue.ts:51-59`. |
| Bảo mật | Không có secret. Token chỉ đọc từ cookie httpOnly phía server. Không render HTML thô; React escape. Khi lỗi không hiển thị dữ liệu: `page.tsx:31-37`. |
| Xử lý lỗi | `ApiError` hiện màn lỗi. Lỗi khác ném lên error boundary, không bị nuốt: `page.tsx:32`. `detail` của backend không hiện ra UI. |
| Hiệu năng | Mỗi lượt tải một request, có phân trang 20. Không có vấn đề. |
| Chất lượng test | 8 unit test có nhánh lỗi và giá trị biên: `parsePage` không hợp lệ, `overflowTarget` (3,30,0)→2, `queueErrorView` 422/500/503. Thiếu test cho thứ tự khi trùng `requested_at` (L2). |
| Dễ đọc và nhất quán | Theo pattern có sẵn (`medications-header`, `dashboard-action`, `medication-table-card`). Không có code chết hay `console.log`. Comment ngắn, đúng chỗ. |
| Đối chiếu 04/05 với log trong `evidence/` | Số liệu khớp:<br>- unit 8/0/0: `implement-final-frontend.log`, `test-unit.log`<br>- `test:chart` 12/0<br>- build có `ƒ /dashboard/deletion-requests`<br>- lint exit 0<br>Kiểm tay có `test-manual-mock.log` và `test-mock-api-requests.json`.<br>`testcase_xlsx.py validate`: 15 test case, 12 Pass / 0 Fail / 3 Pending, khớp `05`.<br>Mục 5 và 7 của `05` vẫn ghi "chưa merge", trong khi file tổng đã merge (L3). |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Medium (M1) | `app/dashboard/deletion-requests/page.tsx:61-73`; `package.json` `next ^14.2.0` | Next 14 giữ payload trang động trong router cache phía client khoảng 30 giây. Bấm `Link` ("Trang trước", mục sidebar) hoặc Back tới trang đã xem trong 30 giây có thể hiện dữ liệu cũ mà không gọi API.<br>Hậu quả:<br>- AC2 ("quay lại trang 1 thì gọi `skip=0`") có thể không gọi lại API.<br>- AC5 ("kể cả dữ liệu đã tải trước đó") có thể vẫn thấy dòng cũ ngay sau khi bị gỡ quyền.<br>Chưa tái hiện: kiểm tay chỉ dùng `navigate` (tải trang đầy đủ) và `router.refresh()`. "Làm mới" và "Thử lại" không bị ảnh hưởng. | Kiểm tay: trang 1, sang trang 2, rồi bấm "Trang trước", xem API có nhận `skip=0` không. Nếu không:<br>- đặt `experimental.staleTimes.dynamic: 0` trong `next.config` (ngoài phạm vi, cần reopen plan);<br>- hoặc chấp nhận và ghi rõ, vì backend vẫn kiểm quyền ở mỗi lượt gọi và dữ liệu cũ là dữ liệu admin đó đã thấy. |
| Medium (M2) | `05` mục 2 | AC7 (60 giây), trạng thái đang tải (AC4) và test tích hợp backend `test_admin_deletion_requests_api.py` chưa chạy. Mọi kiểm tay đều trên API giả, nên chưa có bằng chứng UI chạy đúng với backend thật. | Trước khi merge, người có Supabase local chạy TC-DELQUEUE-09, 13, 15 và cập nhật file tổng. |
| Low (L1) | `components/deletion-requests/QueueStatus.tsx:29-35` | AC5 ghi "401 đưa về luồng đăng nhập có sẵn"; code hiện thông báo kèm nút icon "Đăng xuất". Đây là thiết kế đã duyệt trong `03`, nhưng nút chỉ có icon nên không rõ hành động. | Task sau: cho `LogoutButton` nhận nhãn chữ ("Đăng nhập lại"). |
| Low (L2) | `scripts/deletion-queue.test.mjs` | Given của AC1 nói hai mục cùng `requested_at` khác `id`. Không có test hay kiểm tay nào dùng dữ liệu trùng giờ. UI chỉ giữ nguyên thứ tự backend trả về, nên rủi ro thấp. | Khi chạy TC-DELQUEUE-15, xác nhận test backend phủ thứ tự `id` khi trùng giờ. |
| Low (L3) | `05-test-report.md` mục 5, 7 | Ghi "chưa merge" nhưng `Test_Cases.xlsx` đã merge trên nhánh `docs` `feat/5.07-admin-request-queue-ui`. `05` đã duyệt và người dùng chọn giữ nguyên. | Ghi chú trong PR `docs`; hoặc reopen test để sửa câu chữ. |

Ngoài ra, `?page=` cực lớn (ví dụ 21 chữ số) làm `skip` thành `1e+21`, backend trả 422 và trang hiện "Không tải được hàng chờ". Không lộ dữ liệu, chỉ xảy ra khi tự gõ URL. Không xếp thành phát hiện.

## 5. Mô tả PR

Thứ tự merge theo `wf-git`: frontend → docs → superproject. Không đổi contract, backend hay vùng test tích hợp.

### PR 1 — `frontend` (`feat/5.07-admin-request-queue-ui` → `main`)

**feat(admin): deletion request queue page (5.07)**

Trang Admin Web `/dashboard/deletion-requests`, chỉ đọc. Liệt kê yêu cầu xóa dữ liệu đang chờ duyệt qua `GET /admin/deletion-requests` (contract 5.06).

- Server component `force-dynamic`. Gọi API từ server bằng cookie phiên, `no-store`.
- Bảng bốn cột (mã yêu cầu, mã người gửi, thời điểm gửi theo giờ VN, trạng thái), tổng số, phân trang 20 dòng (`?page=N`). Trang vượt cuối tự chuyển về trang cuối.
- "Làm mới" và "Thử lại" dùng `router.refresh()`. Có trạng thái đang tải, rỗng, lỗi 503, 403 không có quyền, 401 hết phiên (kèm nút Đăng xuất). Khi lỗi không hiển thị dữ liệu.
- Mục sidebar "Yêu cầu xóa dữ liệu".

Test:
- `npm run test:deletion-queue`: 8 pass.
- `npm run lint`, `npm run build`: exit 0.
- Kiểm tay AC1–AC6 trên API giả: `work/5.07-admin-request-queue-ui/evidence/test-manual-mock.log`.

Cần kiểm thêm với backend thật:
1. `cd backend && supabase start && supabase db reset`. Đặt `DRUGTIME_API_BASE_URL` trong `frontend/admin/.env.local`, rồi `npm run dev`.
2. Seed yêu cầu `cho_duyet`, đăng nhập admin, mở trang. Bấm "Làm mới" trong 60 giây sau khi chèn yêu cầu mới (AC7).
3. Sang trang 2, bấm "Trang trước", xác nhận API nhận `skip=0` (phát hiện M1).

Rủi ro: router cache phía client của Next 14 (M1).

Liên quan: PR `docs` (bộ test case), PR superproject (bump con trỏ).

### PR 2 — `docs` (`feat/5.07-admin-request-queue-ui` → `main`)

**docs(testing): add DELQUEUE test cases (5.07)**

Thêm sheet "Hàng chờ yêu cầu xóa" (DELQUEUE) vào `Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx`: 15 test case, 12 Pass, 0 Fail, 3 Pending (TC-DELQUEUE-09, 13, 15 cần Supabase local). Dựng lại sheet `Report`.

Chỉ stage `Test_Cases.xlsx`. Không commit thay đổi file backlog đang có trong working tree.

### PR 3 — superproject (`feat/5.07-admin-request-queue-ui` → `main`)

**chore: bump frontend, docs (5.07-admin-request-queue-ui)**

Bump con trỏ `frontend` và `docs` tới commit đã merge của PR 1 và PR 2. Kèm artifact `work/5.07-admin-request-queue-ui/` (01–06, evidence, `testcases.json`/`.xlsx`); không commit `scratch/`. Merge sau cùng. Nếu PR submodule được squash, cập nhật con trỏ theo `wf-git` trước khi merge.

## 6. Ghi chú cho quy trình

- Review chạy cùng phiên và cùng tool với implement, trái khuyến nghị "nên chạy trong phiên mới, trên tool khác".
- Máy không có Docker và Supabase CLI. Kiểm tay giao diện phải dùng API giả trong `scratch/`. Nên có hướng dẫn chung cho việc kiểm UI admin khi không có backend local, ví dụ một mock theo OpenAPI.
- `scope.py --stage test` báo các file implement chưa commit là `[NGOÀI]`. Nên coi file của bảng implement đã duyệt là hợp lệ ở giai đoạn test, hoặc nhắc commit trước giai đoạn test.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm:
  - Duyệt: `python .agents/scripts/gate.py approve 5.07-admin-request-queue-ui review`.
  - Chạy TC-DELQUEUE-09, 13, 15 và kiểm M1 trên môi trường có Supabase local.
  - Khi người dùng yêu cầu: commit, push và mở PR theo mục 5 (`wf-git`).
- Cập nhật lần cuối: 2026-11-19 15:20, Claude Code
