---
task: adhoc-20261118-mobile-profile-flow-ui
stage: test
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-18 23:02 +0700
content_hash: sha256:4159e0b759b979a3
inputs:
  01-requirement.md: sha256:c338df6345d3cc26
  03-plan.md: sha256:0145eb93e75e6160
  04-impl-notes.md: sha256:e82aa19b16b30fc7
---

# adhoc-20261118-mobile-profile-flow-ui · Test

Task chỉ đổi UI Flutter (AC9: không đổi backend/contract/quyền). Bằng chứng chính là widget test trên checkout cô lập; test tích hợp backend chỉ để hồi quy quyền và chưa chạy được trên máy này.

## 1. Môi trường

- Code kiểm thử: `scratch/workspace/frontend`, nhánh `feat/adhoc-20261118-mobile-profile-flow-ui`, nền `81566509`, thay đổi task chưa commit (24 file tracked, +1062/−580).
- Baseline so sánh: `scratch/baseline-frontend` tại `81566509`, không có thay đổi.
- Gate test: `python .agents/scripts/gate.py adhoc-20261118-mobile-profile-flow-ui test` → exit 0 (chạy lại 2026-11-18, `evidence/test-gate.log` là lượt đầu).
- Môi trường integration kiểm lại 2026-11-18 22:56 (`evidence/test-environment-recheck.log`): không có `supabase` và `docker` trong PATH; `127.0.0.1:54322` từ chối kết nối; `backend/.venv` thiếu module `anthropic`. Không có Android/iOS/emulator (`evidence/test-devices.json`).
- Preview web: phiên trước chạy (`evidence/test-preview.log`), chỉ tới màn đăng nhập. Kiểm lại: không còn process dart/flutter, server đã dừng.

## 2. Kết quả theo tiêu chí chấp nhận

Chỉ tính 40 test case mới của task (`evidence/testcase-provenance.json`). Mã ca bỏ tiền tố `TC-`.

| AC | Test case | Kết quả |
|---|---|---|
| AC1 | PROFUI-15/16/19, CAREGIVER-37, LINKFOLLOW-36/39, INVITELINK-14, APPNAV-13; PROFUI-22/23, CAREGIVER-42, LINKAPPROVE-31, APPNAV-15 | pass widget; đối chiếu Figma/thiết bị Pending |
| AC2 | PROFUI-15/17, LINKFOLLOW-39, APPNAV-11/12; INVITELINK-16 | pass; INVITELINK-16 Pending |
| AC3 | LINKFOLLOW-36, INVITELINK-14/15; LINKFOLLOW-41 Fail; LINKFOLLOW-43, INVITELINK-16/19 Pending | pass một phần, 1 fail có sẵn ở baseline |
| AC4 | CAREGIVER-37/38, LINKFOLLOW-37/38/39, LINKAPPROVE-28/29; LINKFOLLOW-40 Fail; LINKFOLLOW-43, LINKAPPROVE-31 Pending | pass một phần, 1 fail có sẵn ở baseline |
| AC5 | CAREGIVER-38/39, LINKAPPROVE-28/29/30; LINKFOLLOW-42 Fail; PROFUI-24, CAREGIVER-40/41 Pending | pass widget; quyền phía server Pending |
| AC6 | PROFUI-15/16/17/18 | pass |
| AC7 | CAREGIVER-38, LINKFOLLOW-36/37, LINKAPPROVE-30; PROFUI-20/21, LINKFOLLOW-41/42, INVITELINK-17/18, APPNAV-14 Fail; PROFUI-24, CAREGIVER-40/41 Pending | 7 fail, đều có sẵn ở baseline |
| AC8 | PROFUI-16/19, LINKFOLLOW-38, LINKAPPROVE-28; PROFUI-22/23, CAREGIVER-42, LINKFOLLOW-43, INVITELINK-19, LINKAPPROVE-31, APPNAV-15 Pending | pass widget; thiết bị Pending |
| AC9 | PROFUI-18, APPNAV-12/13; PROFUI-24, CAREGIVER-40 Pending | pass; diff review ở giai đoạn review |
| AC10 | APPNAV-10/11/12/13; INVITELINK-17, APPNAV-14 Fail; PROFUI-22, APPNAV-15 Pending | pass điều hướng chính, 2 fail có sẵn ở baseline |

## 3. Kịch bản chất lượng đã phủ

| Kịch bản | Test | Kết quả |
|---|---|---|
| Truy cập chéo patient không liên kết/consent → 403 + `denied` | `backend/tests/integration/test_family_links_access.py` | skip: Supabase local không chạy (`evidence/test-rights-integration.log`, 9 skipped) |
| Rút consent/hủy liên kết → 403 ở request kế tiếp | `backend/tests/integration/test_family_links_immediate_effect.py` | skip, cùng lý do |
| Idempotent liều, chạy đua Worker, tương tác thuốc | — | không áp dụng: task không chạm |

Task không đổi backend, nên các kịch bản trên là hồi quy. Chưa có bằng chứng chạy thật; ca TC-PROFUI-24, TC-CAREGIVER-40/41 để Pending.

## 4. Toàn bộ bộ test

- Widget regression (phiên trước, nhóm profile/family_link/family/consent/AppShell): `01:31 +364 -8: Some tests failed.`, log `evidence/test-widget-regression.log`.
- Triage 8 fail, chạy trong phiên này, cùng 6 file test ở hai checkout:
  - Lệnh: `flutter test test/features/family/family_adherence_screen_test.dart test/features/family/family_link_code_stability_test.dart test/features/family_link/family_tab_screen_test.dart test/features/family_link/invite_link_flow_test.dart test/features/family_link/redeem_acceptance_test.dart test/features/profile/profile_app_lifecycle_test.dart` (trong `mobile/`).
  - Baseline `81566509`: `00:32 +21 -8: Some tests failed.`, `evidence/test-fail-triage-baseline.log`.
  - Nhánh task: `00:30 +21 -8: Some tests failed.`, `evidence/test-fail-triage-workspace.log`.
  - Cùng 8 test fail ở cả hai bản: lỗi có sẵn, task không thêm fail. Khớp `evidence/failure-comparison.json` của implement (82 fail toàn bộ, `only_current: []`).
- Backend integration: `pytest tests/integration` dừng collection, `1 warning, 11 errors in 7.53s` (thiếu `anthropic`), `evidence/test-backend-integration.log`; test quyền chọn riêng `9 skipped in 5.47s`, `evidence/test-rights-integration.log`.
- `scope.py --stage test`: chạy với `AGENTS_ROOT` trỏ vào `scratch/workspace` và `scratch/qa-workspace`; cả hai exit 0, "OK: mọi thay đổi nằm trong phạm vi." (`evidence/test-scope.log`). Giai đoạn test không sửa code sản phẩm.

## 5. Bộ test case Excel

- Spec: `testcases.json` · File task: `testcases.xlsx` · File tổng: bản QA cô lập `scratch/qa-workspace/docs/Team1_DTU/04_Quality_&_Testing/Test_Cases.xlsx` (docs nhánh `feat/adhoc-20261118-mobile-profile-flow-ui`, nền `6eab7ab8`). Chưa ghi vào `docs` gốc.
- Log: `evidence/testcase-xlsx.log`. `validate`, `build`, `merge` exit 0, không có CẢNH BÁO.
- Giữ nguyên ID và kết quả của 134 ca lịch sử; thêm 40 ca mới (21 Pass, 8 Fail, 11 Pending).

| Chức năng (mã) | Tổng | Pass | Fail | Pending |
|---|---|---|---|---|
| PROFUI | 24 | 18 | 2 | 4 |
| CAREGIVER | 42 | 38 | 0 | 4 |
| LINKFOLLOW | 43 | 36 | 3 | 4 |
| INVITELINK | 19 | 11 | 2 | 6 |
| LINKAPPROVE | 31 | 26 | 0 | 5 |
| APPNAV | 15 | 13 | 1 | 1 |
| **Tổng** | **174** | **142** | **8** | **24** |

- Test case `Pending` cần người chạy:
  - Thiết bị thật/Figma: PROFUI-14/22/23, CAREGIVER-42, LINKAPPROVE-31, APPNAV-15, INVITELINK-19.
  - Camera/QR: LINKFOLLOW-25/26/27/43.
  - Hai thiết bị + backend: CAREGIVER-28, LINKAPPROVE-26/27.
  - DB thật/Access Log: PROFUI-24, CAREGIVER-40/41.
  - Link mời: INVITELINK-09/11/12/13/16.
  - BVA chưa có test: LINKAPPROVE-BVA-10/11.
- Bug đã ghi vào Bug Report: 8 (bằng số ca Fail), xem mục 5b.

## 5b. Lỗi sản phẩm tìm thấy

Không có lỗi mới do task. 8 ca Fail dưới đây fail giống hệt trên baseline `81566509`, được ghi để không che lỗi. Cần triage ở task riêng.

| Ca | Mức | Test | Thực tế | Nghi vấn |
|---|---|---|---|---|
| PROFUI-20 | Low | `profile_app_lifecycle_test`: clears profile on logout | RenderFlex overflowed by 28 pixels ở Column màn đăng nhập | Layout login trong viewport test; test dừng trước khi kiểm cleanup |
| PROFUI-21 | Low | như trên, on 401 | Cùng overflow 28 px | Như PROFUI-20 |
| LINKFOLLOW-40 | Medium | `redeem_acceptance_test`: AC2 valid QR waits for explicit confirmation | Expected: true, Actual: false | Hành vi quét QR khác kỳ vọng test; cần chốt theo QD-04/QD-34 |
| LINKFOLLOW-41 | Low | `family_link_code_stability_test` mục 4 | Không thấy text "PATIENT10X" sau đăng nhập lại | Fixture bootstrap/login hoặc nạp lại mã |
| LINKFOLLOW-42 | Low | `family_adherence_screen_test`: logout removes health data | Overflow 28 px ở màn đăng nhập | Như PROFUI-20 |
| INVITELINK-17 | Medium | `invite_link_flow_test`: AC16 OTP rồi tới màn nhập mã | Assertion trong `pumpApp` | Fixture login/OTP |
| INVITELINK-18 | Low | `invite_link_flow_test`: đăng xuất xóa link mời | Assertion trong luồng đăng xuất | Fixture vòng đời auth |
| APPNAV-14 | Medium | `family_tab_screen_test`: unread count | Không tìm thấy ConsentScope/FamilyLinkScope phía trên widget | Harness test thiếu scope |

Ba ca logout/401 (PROFUI-20/21, LINKFOLLOW-42) chạm cleanup dữ liệu sức khỏe. Chưa có bằng chứng cleanup sai, nhưng cũng chưa chứng minh được là đúng. Nên ưu tiên triage.

## 6. Test không ổn định hoặc bị skip

- Không thấy flaky: 8 fail lặp lại giống nhau ở phiên trước và cả hai lượt chạy trong phiên này.
- Skip: 9 test integration quyền vì Supabase local không chạy. Không nới hay đánh dấu skip trong code.

## 7. Phát sinh

- Integration backend và test trên thiết bị cần máy có Supabase CLI + Docker và Android/iOS. Không chạy được ở môi trường hiện tại.
- File tổng chỉ được merge vào bản QA cô lập. Khi xong review, đưa sheet vào `docs` gốc theo `wf-git` (nhánh docs cùng tên).
- Lượt preview phiên trước dừng giữa chừng do hết lượt duyệt tự động; không dùng làm bằng chứng Pass.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt quyết định chấp nhận 8 Fail có sẵn ở baseline và các ca Pending, rồi chạy `python .agents/scripts/gate.py approve adhoc-20261118-mobile-profile-flow-ui test`. Nếu muốn chạy integration trước, cần máy có Supabase/Docker: `cd backend && supabase start && supabase db reset && pytest tests/integration`.
- Sau duyệt: giai đoạn review (`wf-review`). Sau đó commit/push frontend và docs theo `wf-git`, bump con trỏ, mở PR.
- Cập nhật lần cuối: 2026-11-18 23:05, Claude Code.
