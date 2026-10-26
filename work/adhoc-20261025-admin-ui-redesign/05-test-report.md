---
task: adhoc-20261025-admin-ui-redesign
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-10-26 15:05 +0700
content_hash: sha256:0dd681f4b50afc97
inputs:
  01-requirement.md: sha256:ffdb8e4c5877f6b5
  03-plan.md: sha256:a4322237aa7fbdfd
  04-impl-notes.md: sha256:c11493562de82dc7
---

# adhoc-20261025-admin-ui-redesign · Test

## 1. Môi trường

- Code dưới test: `frontend` nhánh `feat/adhoc-20261025-admin-ui-redesign`, commit `122e3577` (trên `24c36415`). Kiểm bằng `git -C frontend diff --quiet -- admin`: working tree của `admin` trùng HEAD.
- Service: `next dev -p 3100` (Admin Web). Không cần backend vì các trang dashboard dùng dữ liệu tĩnh của frontend. Phiên đăng nhập là cookie **test** (JWT không ký, chỉ có `exp`) đặt trên `localhost`, theo cách người dùng chọn ở implement (xem `04` mục 5).
- Công cụ: Chrome headless qua CDP (`scratch/cdp-shot.mjs` + `scratch/jobs-*.json`); so pixel Login bằng Chrome CLI (`scratch/shot.sh` + `scratch/imgdiff.py`); tương phản bằng `scratch/contrast.py`; hành vi bằng `scratch/behavior-medications.js`, `scratch/behavior-interactions.js`.
- Nhánh của vùng test tích hợp: không dùng. Task không chạm `tests`, `backend/tests/integration` hay `backend/tests/interaction_scenarios`.

## 2. Kết quả theo tiêu chí chấp nhận

Theo `01`, không AC nào ở mức `integration`; AC1–AC7 là `manual`, AC8 là lint/build. Giai đoạn này chạy lại toàn bộ bộ kiểm tự động trên code đã commit.

| AC | Test | Kết quả |
|---|---|---|
| AC1 (giao diện mới ở 5 trang) | Ảnh 1440 cả 5 trang + trang đã cuộn (`test-pages.log`, `test-pages-scrolled.log`); một vùng cuộn, sidebar/topbar cố định (`test-scroll-structure.log`); bảng vừa card ở 1440 (`test-table-width.log`) | pass: overflowX ≤ 0; `innerVerticalScrollers: []`; topbar/sidebar top 0 trước và sau khi cuộn; 0 lỗi console |
| AC2 (Login không đổi) | So pixel `/auth/login` với baseline ở 1440 và 375; Login sau khi Đăng xuất từ dashboard so với Login mở trực tiếp (`test-login-diff.log`, `test-login-logout.log`) | pass: 3/3 `diff_pixels=0` |
| AC3 (chỉ đổi trình bày) | `git diff origin/main..HEAD` của `frontend` (`test-diff.log`) | pass: đúng 2 file `dashboard-theme.css`, `layout.tsx`; không file nào trong `components`, `app/auth`, `lib`, `globals.css` bị đổi |
| AC4 (nghiệp vụ chạy như trước) | Kịch bản thuốc 15 bước, tương tác 12 bước (`test-behavior-*.log`); modal khóa cuộn trang nền (`test-modal-scroll-lock.log`); modal và toast nhận theme (`test-overlays*.log`) | pass: 15/15, 12/12, 0 lỗi console; lăn chuột: không modal thì scrollY 268, có modal thì 0 |
| AC5 (focus, tương phản) | Tab thật qua CDP (`test-focus.log`); topbar không che focus (`test-focus-not-obscured.log`); 12 cặp màu (`test-contrast.log`) | pass: `:focus-visible` đúng 5/5; nút focus top 141 > đáy topbar 68; 12/12 cặp đạt |
| AC6 (768/375 không cuộn ngang) | 8 ảnh responsive (`test-responsive.log`); bảng ở 1280 (`test-table-width.log`) | pass: overflowX = 0 ở cả 8; bảng 958 = 958 ở 1280 |
| AC7 (reduced motion) | `transition-duration` khi bật/tắt `reduce` (`test-focus-motion.log`) | pass: 1e-05s khi bật; 0.18s/0.2s khi tắt |
| AC8 (lint, build) | `npm run lint`, `npm run build` (`test-admin-lint.log`, `test-admin-build.log`) | pass: exit 0; 11 route; `/auth/login` 7.41 kB như baseline |

## 3. Kịch bản chất lượng đã phủ

Task không chạm vùng rủi ro nào trong `AGENTS.md` (`01` mục 6), nên không kịch bản chất lượng tích hợp nào áp dụng (403/`access_logs`, rút consent, `client_uuid`, Worker chạy đua, golden scenarios tương tác thuốc).

| Kịch bản | Test | Kết quả |
|---|---|---|
| Không áp dụng | — | — |

## 4. Toàn bộ bộ test tích hợp

- Lệnh theo `AGENTS.md`: `cd backend && supabase start && supabase db reset && pytest tests/integration`
- Kết quả: **chưa chạy**. Docker daemon không chạy trên máy này (`docker info` lỗi), nên `supabase start` không khởi động được. Task không sửa file nào ở `backend`, `api_contract` hay `tests`, nên bộ test tích hợp không có thay đổi nào để phát hiện; nhưng theo quy trình, mục này để mở cho tới khi chạy được.
- Bộ kiểm của task (thay cho test tích hợp, chạy trong phiên này trên commit `122e3577`): 37 lượt chạy CDP, 0 lỗi console, 27/27 bước hành vi, 3/3 so pixel Login, 12/12 cặp tương phản, lint và build exit 0. Log: `evidence/test-*.log`.
- `scope.py --stage test`: exit 1 (log: `evidence/test-scope.log`). So với danh sách có sẵn từ `requirement-scope.log`, khác biệt là: thêm `frontend/admin/app/dashboard/dashboard-theme.css` và `layout.tsx` (đó là commit `24c36415`, `122e3577` của giai đoạn implement đã duyệt; script tính commit trên nhánh task; giai đoạn test không sửa chúng), và `Test_Cases.xlsx` giờ là `[OK]`. Còn lại là các thay đổi có sẵn từ trước task (mục 7).

## 5. Bộ test case Excel

- Spec: `testcases.json` · File task: `testcases.xlsx` · File tổng: `docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (**chưa gộp**, xem bên dưới)
- Log: `evidence/testcase-xlsx.log` (`validate` exit 0, `build` exit 0)

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| Giao diện Admin Web (ADMINUI) | 27 | 25 | 0 | 2 |

- Kỹ thuật: EP theo độ rộng viewport (3 lớp: ≥1281, 901–1280, ≤900); bảng quyết định "trang nào nhận theme" (R1 Login, R2 dashboard); chuyển trạng thái đóng → mở modal (khóa cuộn); đoán lỗi (CSS còn nạp sau khi đăng xuất bằng điều hướng client; topbar dính che focus).
- Test case `Pending` cần người chạy:
  - `TC-ADMINUI-26`: đăng nhập bằng tài khoản admin thật qua backend (Supabase cloud theo `backend/.env`) rồi duyệt 5 trang và đăng xuất.
  - `TC-ADMINUI-27`: kiểm layout và thanh cuộn trên Firefox và Safari (agent chỉ kiểm trên Chrome).
- Bug đã ghi vào Bug Report: không có.
- **Chưa chạy `merge` vào file tổng**: trong submodule `docs`, `Test_Cases.xlsx` đang ở trạng thái xung đột merge (`UU`) trên nhánh `main`, kèm thay đổi đã stage của người khác (backlog, schema, tài liệu yêu cầu). Theo `wf-git`, agent không ghi vào file đang có thay đổi chưa xong của người khác. Cần người dùng quyết định trước (mục "Bước tiếp theo").

## 5b. Lỗi sản phẩm tìm thấy

Không có.

## 6. Test không ổn định hoặc bị skip

- Không có test nào cho kết quả khác nhau giữa các lần chạy. Ảnh chụp Login lặp lại cho 0 pixel khác (implement P2), kịch bản hành vi cho cùng kết quả ở P9, P13 và giai đoạn test.
- Bị bỏ qua có lý do: bộ test tích hợp backend (mục 4) vì Docker không chạy.

## 7. Phát sinh

- `docs`: `Test_Cases.xlsx` đang xung đột merge (`UU`), cùng 3 file khác đã stage (`Product-and-Sprint-backlog-DrugTime.xlsx`, `drugtime_quyet_dinh_theo_chuc_nang.md`, `drugtime_schema_v11.sql`). Không thuộc task này; chặn bước `merge` test case.
- Các thay đổi chưa commit có sẵn ở superproject (`.agents`, `AGENTS.md`, con trỏ `api_contract`/`backend`/`docs`, `.claude/`, `graphify-out/`) và `frontend/mobile/.env.example` vẫn nằm ngoài task, như đã ghi ở `01`, `03`, `04`.
- Con trỏ submodule `frontend` ở superproject chưa bump lên `122e3577` (chưa push, theo `wf-git`).

## Bước tiếp theo

- Đang chờ: người dùng (quyết định gộp test case), rồi người duyệt.
- Việc cần làm:
  1. Người dùng xử lý xung đột merge `Test_Cases.xlsx` trong `docs` (hoặc cho biết nhánh `docs` nên dùng). Sau đó agent chạy `python .agents/scripts/testcase_xlsx.py merge adhoc-20261025-admin-ui-redesign` và cập nhật mục 5.
  2. Tùy chọn: bật Docker để agent chạy `pytest tests/integration`; chạy tay `TC-ADMINUI-26`, `TC-ADMINUI-27`.
  3. Người duyệt chạy `python .agents/scripts/gate.py approve adhoc-20261025-admin-ui-redesign test`; sau đó agent làm giai đoạn review (`wf-review`).
- Cập nhật lần cuối: 2026-10-26 15:00, Claude Code
