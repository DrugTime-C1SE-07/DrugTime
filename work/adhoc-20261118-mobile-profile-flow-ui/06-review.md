---
task: adhoc-20261118-mobile-profile-flow-ui
stage: review
status: approved
approved_by: Ngọc Việt
approved_at: 2026-11-18 23:11 +0700
content_hash: sha256:048b7c4c5557b016
inputs:
  01-requirement.md: sha256:c338df6345d3cc26
  03-plan.md: sha256:0145eb93e75e6160
  04-impl-notes.md: sha256:e82aa19b16b30fc7
  05-test-report.md: sha256:4159e0b759b979a3
---

# adhoc-20261118-mobile-profile-flow-ui · Review

## 1. Kết luận

Đạt, kèm lưu ý.

Không có lỗi Critical hay High. Có 3 lưu ý Medium nên sửa trước khi mở PR, nhất là việc rebase lên `origin/main` mới. Có thêm 5 lưu ý Low.

Review do Claude Code thực hiện, cùng phiên đã viết lại `05-test-report.md`. Skill khuyên nên review ở phiên mới hoặc trên tool khác; lần này chưa làm được như vậy.

## 2. Phạm vi đã review

| Submodule | Lệnh diff |
|---|---|
| `frontend` (checkout cô lập `scratch/workspace/frontend`, nhánh `feat/adhoc-20261118-mobile-profile-flow-ui`) | `git diff HEAD -- mobile` cộng 7 file mới chưa track. Nền `81566509` = `main` của bản clone. Code chưa commit. |
| `backend`, `api_contract`, `tests` | Không bị chạm |
| `docs` | Chỉ có `Test_Cases.xlsx` đã merge trong `scratch/qa-workspace/docs`, sinh từ `testcases.json` |

Đã đọc toàn bộ diff `lib/`: 19 file sửa và 5 file mới (+1062/−580 tính cả test). Diff test đọc theo các assertion bị xóa hoặc đổi và các test mới.

Kết quả `scope.py --stage implement` với `AGENTS_ROOT=scratch/workspace`: "OK: mọi thay đổi nằm trong phạm vi.", exit 0 (`evidence/review-scope-validate.log`).

## 3. Kết quả theo danh sách

| Mục | Kết quả |
|---|---|
| Đúng yêu cầu | Phần lớn đạt. Diff chỉ đổi presentation và route. Điều khiển chưa có backend đều hiện "Chưa khả dụng" và `onPressed`/`onChanged: null`, đạt AC2. Callback consent, sharing, revoke, approve/reject, QR/share giữ nguyên (AC3–AC5). Có 3 màn mới và 4 route mới, có test điều hướng (AC10). Lệch: M2 (AC10), L1 (AC1, câu chữ). |
| Phạm vi | Đạt. `scope.py` exit 0; không có file ngoài bảng. |
| Contract | Không áp dụng. Không đổi request/response hay repository. |
| Bất biến kiến trúc | Đạt. Không có Supabase key hay truy cập trực tiếp; file mới không gọi mạng. Không đổi PEP/consent/access log, không cache quyền ở app. Bất biến 5–7 không bị chạm. |
| Bảo mật | Không thấy vấn đề: không có secret, không log dữ liệu nhạy cảm. Link mời và mã QR vẫn chỉ hiện khi có consent `family_sharing`. |
| Xử lý lỗi | Giữ nhánh lỗi/thử lại cũ (caregivers, share link, privacy). Lưu ý M1: có đường crash khi tên rỗng. |
| Hiệu năng | Không có vấn đề. Chỉ là widget tĩnh, không thêm vòng tải dữ liệu. |
| Chất lượng test | Đạt. 14 file UI/regression pass 147/147 trong phiên review (`evidence/review-focused-tests.log`). Assertion bị xóa đều thuộc hai loại: đổi định dạng, hoặc đổi kỳ vọng UI đã duyệt ở requirement (cao 48 px, field "Chưa khả dụng" thay cho ẩn field). Không có skip. Chưa có test cho tên người giám sát rỗng (M1). |
| Dễ đọc và nhất quán | Có lệch nhỏ: hard-code màu canvas ở nhiều nơi, điều kiện thừa, 1 lint info mới (L2–L4). |
| Đối chiếu 04/05 với log trong `evidence/` | Khớp. 04: 147/0 (`implement-focused-pass.log` `+147: All tests passed!`), toàn suite 82 fail trùng baseline (`failure-comparison.json`). 05: 8 fail trùng baseline (`test-fail-triage-*.log`, cả hai `+21 -8`). Analyze phiên này 5 issue, giống `implement-analyze-delivery.log`; 4 issue ở `app_shell.dart` có sẵn ở baseline (baseline cũng báo 4 issue). `testcase_xlsx.py validate` exit 0, 8 Fail = 8 dòng bug. Integration backend và thiết bị chưa chạy, đã ghi rõ ở 05 và được duyệt. |

## 4. Phát hiện

| Mức | Vị trí | Vấn đề | Đề xuất |
|---|---|---|---|
| Medium | `mobile/lib/features/family_link/presentation/screens/caregivers_screen.dart:259` | Avatar chữ cái đầu dùng `familyDisplayName(caregiver.familyName).characters.first`. `familyName` là `String?` và `familyDisplayName` chỉ đổi `null` sang tên mặc định. Nếu backend trả `""`, `.first` ném `StateError` và màn Người giám sát lỗi dựng. Code trước task không có đường này. | Dùng `characters.firstOrNull ?? '?'`, hoặc xử lý chuỗi rỗng trong `familyDisplayName`. Thêm 1 widget test với `familyName: ''`. |
| Medium | `mobile/lib/features/consent/presentation/screens/privacy_settings_screen.dart:126` | Mục mới "Ai có thể xem hồ sơ của tôi" mở `AppRoutes.caregivers` nhưng bỏ qua kết quả trả về. Khi chưa có người giám sát, nút "Mở tab Người thân" chỉ pop về màn Quyền riêng tư, không mở tab Người thân như khi đi từ Hồ sơ (`profile_screen.dart:86-91`). Lệch AC10 nhưng không phải dead-end. | Dùng chung luồng `_openCaregivers` của Hồ sơ, hoặc pop tiếp với cùng kết quả để AppShell chuyển tab. Thêm test điều hướng. |
| Medium | `mobile/lib/app/app_shell.dart`, `mobile/test/app/app_shell_test.dart` | Nhánh task dựng trên `81566509`; `origin/main` của frontend đã tới `c761218c` (PR #78 home living banner). PR này cũng sửa vùng nav bar của `app_shell.dart` (dòng 223–330) và test của nó, cạnh chỗ task sửa (dòng 187, 267–273). Nhiều khả năng sẽ xung đột khi mở PR. | Trước khi commit/PR: rebase hoặc merge `origin/main` vào nhánh task, giải xung đột `app_shell.dart`, chạy lại 14 file test và toàn suite, so lại với baseline mới. |
| Low | `mobile/lib/features/profile/presentation/screens/reminder_sound_screen.dart:32` | Nhãn âm thanh "Âm cha hữu ơi" không có trong Figma; frame `sound-row` của Figma là "Vui vẻ" (`evidence/figma-settings-health-states.json`). | Đổi thành "Vui vẻ". |
| Low | `mobile/lib/features/profile/presentation/screens/medical_profile_screen.dart:149`, `:201` | Điều kiện thừa `compact ? 48 : 48`. | Thay bằng `48`. |
| Low | `medical_profile_screen.dart:31,34`, `profile_screen.dart:18`, `shared/widgets/profile_flow_widgets.dart` (`profileFlowCanvas = 0xFFF7F9F8`) | Màu nền canvas hard-code hai giá trị khác nhau (`F5F7F6` và `F7F9F8`) ở nhiều nơi, không qua `AppColors`. Ngoài ra còn nhiều màu icon hard-code trong `profile_screen.dart` và `invite_caregiver_screen.dart`. | Gom về token trong `app_theme.dart` khi làm design token. Không chặn PR. |
| Low | `mobile/test/features/family_link/share_invite_link_screen_test.dart:77` | Lint info mới `curly_braces_in_flow_control_structures`. | Bọc `if` bằng `{}`. |
| Low | `mobile/lib/features/family_link/presentation/screens/scan_link_qr_screen.dart:254` | Khi đèn flash không khả dụng, `_TorchButton` trả `SizedBox.shrink()`, làm tiêu đề "Quét mã QR" lệch tâm. Nhánh `camera == null` thì có giữ chỗ 48 px. | Trả `SizedBox(width: 48)`. |

Không có phát hiện Critical/High. Trước khi merge vẫn cần người chạy các ca Pending trên thiết bị và DB thật (xem `05-test-report.md` mục 5). Ba ca cleanup khi đăng xuất/401 (TC-PROFUI-20/21, TC-LINKFOLLOW-42) fail sẵn ở baseline; nên mở task riêng để chứng minh lại cleanup dữ liệu sức khỏe.

## 5. Mô tả PR

Thứ tự merge theo `wf-git`: frontend → docs → superproject. Sau squash merge, cập nhật con trỏ tới SHA đã merge trước khi merge PR superproject.

### PR frontend: `feat/adhoc-20261118-mobile-profile-flow-ui` → `main`

```
feat(mobile): profile & caregiver flow UI from Figma S08

Refs: adhoc-20261118-mobile-profile-flow-ui

Summary
- Restyle S08 profile, personal/medical profile, caregivers, privacy, family link code,
  share link, QR scanner, enter code, consent confirmation, link result and approve sheet.
- New screens: invite caregiver hub, notification preferences, reminder sound, settings
  (routes /profile/invite, /profile/notifications, /profile/notifications/sound, /profile/settings).
- Features without backend support are shown as "Chưa khả dụng" and are disabled (no requests, no fake saves).
- No change to data, state, repositories, API calls or consent/sharing callbacks.

Tests
- 14 UI/regression files: 147/147 pass.
- Full mobile suite: 82 failures, identical to baseline 81566509 (no new failures).
- Pending manual: device/Figma visual checks, camera QR, two-device link approve/reject, DB access log.

Risk
- app_shell.dart touched (profile canvas + nav bar inset); rebased on main <sha>.

Links: docs PR <link>, superproject PR <link>.
```

### PR docs: `feat/adhoc-20261118-mobile-profile-flow-ui` → `main`

```
docs(testing): update profile/caregiver test cases

Refs: adhoc-20261118-mobile-profile-flow-ui

- Test_Cases.xlsx: PROFUI, CAREGIVER, LINKFOLLOW, INVITELINK, LINKAPPROVE, APPNAV updated;
  134 historical cases kept, 40 new (21 Pass, 8 Fail pre-existing on baseline, 11 Pending).
- Report and Bug Report sheets rebuilt by testcase_xlsx.py merge.

Links: frontend PR <link>, superproject PR <link>.
```

### PR superproject: `fix/…` hoặc `feat/adhoc-20261118-mobile-profile-flow-ui` → `main`

```
chore: bump frontend and docs for profile flow UI (adhoc-20261118-mobile-profile-flow-ui)

- Bump frontend to <merged sha>, docs to <merged sha>.
- Add work/adhoc-20261118-mobile-profile-flow-ui artifacts and evidence.

Merge after frontend and docs PRs.
```

## 6. Ghi chú cho quy trình

- `.claude/skills/` là thư mục tự tạo (doctor báo lỗi), nên Claude Code không nạp được skill `wf-*`; agent phải đọc thẳng `.agents/skills/*/SKILL.md`. Cần chạy `doctor.py --fix` sau khi chuyển skill speckit.
- Checkout cô lập trong `scratch/` không tự cập nhật theo `origin/main`. Skill `wf-git` hoặc `wf-review` nên có bước kiểm "nhánh task còn dựng trên nhánh gốc mới nhất" trước khi viết mô tả PR.
- Ca Fail có sẵn ở baseline đang được ghi vào Bug Report của task. Nên có quy ước riêng (ví dụ cột "pre-existing") để không lẫn với lỗi do task gây ra.

## Bước tiếp theo

- Đang chờ: người duyệt.
- Việc cần làm: người duyệt quyết định sửa 3 lưu ý Medium trước hay ghi nhận. Sửa code cần `python .agents/scripts/gate.py reopen adhoc-20261118-mobile-profile-flow-ui implement`. Nếu chấp nhận: `python .agents/scripts/gate.py approve adhoc-20261118-mobile-profile-flow-ui review`.
- Sau duyệt: theo `wf-git`, đưa code từ checkout cô lập vào `frontend` gốc trên nhánh `feat/adhoc-20261118-mobile-profile-flow-ui` dựng từ `origin/main` mới; tương tự với `docs`. Commit, push, bump con trỏ và mở PR theo mục 5, chỉ khi người dùng yêu cầu.
- Cập nhật lần cuối: 2026-11-18, Claude Code.
