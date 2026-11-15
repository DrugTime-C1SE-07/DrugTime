---
task: 5.13
stage: contract
status: approved
approved_by: Bao Nguyen
approved_at: 2026-11-10 13:05 +0700
content_hash: sha256:d57a06a4057ba520
inputs:
  01-requirement.md: sha256:eb0cc2ee1b9c43b1
---

# 5.13 · API contract

## 1. File đã sửa trong submodule contract

- `api_contract/openapi.json`: thêm `GET /family/patients`, schemas `LinkedPatient`, `LinkedPatientList`.
- `api_contract/README.md`: mô tả cách dùng danh sách và phân biệt với `/family/caregivers`.
- Nhánh contract và Backend: `feat/list-linked-patients`. Contract tạo nhánh từ HEAD sạch `61df460` đang có (giữ nguyên contract profile/phone); Backend đã ở nhánh người dùng tạo. Không commit/push, không chuyển nhánh superproject.
- Đầu vào hiện hành: `01-requirement.md` size L, approved lại bởi Bao Nguyen lúc `2026-11-10 13:03 +0700`, đã bao gồm migration và AC10–AC14. Không sửa artifact đã approved.

## 2. Thay đổi

| Endpoint | Thêm / sửa / xóa | Tương thích | Tóm tắt |
|---|---|---|---|
| `GET /family/patients` | Thêm | Không phá vỡ | Danh sách bệnh nhân mà caller hiện có quyền theo dõi, làm nguồn cho bộ chọn PB22. Chỉ trả ID và tên; kiểm quyền DB mỗi request; audit fail-closed. |

Thêm endpoint và hai schema mới; mọi định nghĩa API cũ giữ nguyên theo phép so sánh JSON với snapshot trước khi sửa. Không đổi version, response của `/family/caregivers`, hoặc các API theo `patient_id`.

## 3. Chi tiết từng endpoint

### `GET /family/patients`

- `operationId`: `listMyLinkedPatients`; tag `family`.
- Bearer là app session token của tài khoản cá nhân theo quy ước chung; không chấp nhận Supabase Auth token thay thế.
- Chủ danh sách lấy từ danh tính phiên. Không có role `family` độc lập bắt buộc trong token: một tài khoản có thể là người bệnh của quan hệ này và người thân ở quan hệ khác.
- Không có path/query parameter hoặc body. Query/body thừa (kể cả selectors ID, `limit`, `cursor`) trả 422 theo định dạng ValidationError đã có. Kiểm token trước quyền; validation cấu trúc có thể trả trước kiểm admin như endpoint family hiện hành.
- Mỗi bệnh nhân phải đủ: liên kết với caller `active`, `sharing_enabled=true`, consent của bệnh nhân `family_sharing` và `health_data` đang hiệu lực. Không dùng consent riêng của caller để quyết định quyền xem người khác. Không tự thêm caller vào kết quả.
- Pending/rejected/revoked, sharing tắt, thiếu một consent, hoặc liên kết của caller khác đều bị loại. Không trả lý do loại từng patient; không đổi cả response thành 403 chỉ vì có mục bị loại.
- Mỗi `patient_id` xuất hiện một lần. Không phân trang/cắt ngầm theo giả định đã duyệt trong requirement.
- Sort theo tên đã trim tăng dần theo mã Unicode, phân biệt hoa/thường và dấu; null cuối, ID UUID tăng dần khi bằng tên. Không hứa thứ tự ngôn ngữ tiếng Việt hoặc bỏ dấu.
- Tên null nếu không có hoặc chỉ có khoảng trắng, theo quy tắc projection tên hiện có trong `SqlUsers.display_names`. Không fallback sang email/điện thoại, không loại patient vì thiếu/trùng tên.

Schema response 200:

```json
{
  "items": [
    {
      "patient_id": "3f0c2a9e-7b1d-4e58-9c6a-2d4b8e1f0a73",
      "patient_full_name": "Nguyễn Văn An"
    }
  ]
}
```

- `items`: array bắt buộc; rỗng là `[]`.
- `patient_id`: string UUID bắt buộc, khóa kỹ thuật của patient cho request sau.
- `patient_full_name`: string không rỗng đã trim hoặc null; field luôn có mặt.
- Envelope và item đều `additionalProperties: false`. Không thêm link ID, email, điện thoại, ngày sinh, ảnh, thuốc, lịch, liều hoặc hồ sơ.

| HTTP | Schema | Hành vi / ví dụ |
|---|---|---|
| 200 | `LinkedPatientList` | Danh sách đầy đủ hoặc `{"items":[]}`. Có ví dụ tên trùng, tên null trong OpenAPI. |
| 401 | `ErrorDetail` | Thiếu/sai/hết hạn token hoặc tài khoản đã bị xóa. Ví dụ `{"detail":"Missing bearer token"}`; client không so khớp nội dung câu 401. |
| 403 | `ErrorDetail` | Admin: `{"detail":"khong_co_quyen"}`. Ghi denied bền vững mức request. Consent của patient khác chỉ tác động bộ lọc, không trả `consent_revoked`. |
| 422 | `ValidationError` | Query/body không được nhận. Ví dụ `detail:[{loc:["query","patient_id"],msg:"Extra inputs are not permitted",type:"extra_forbidden"}]`. |
| 503 | `ErrorDetail` | `{"detail":"service_unavailable"}` khi DB, kiểm quyền hoặc audit không khả dụng, gồm thất bại ghi denied. Không trả dữ liệu một phần. |

Không có 404 (không truy vấn patient cụ thể), 409 (GET không thay đổi liên kết) hoặc khóa idempotency. Retry GET vẫn kiểm quyền và ghi audit cho lần truy cập mới. Mọi response của endpoint có `Cache-Control: no-store` theo mẫu header hiện có của `/adherence`.

### Quyền, PEP và audit

- Dùng PEP hiện có, đọc lại quan hệ/consent từ DB mỗi request trước khi đọc tên để trả; không tự viết cơ chế quyền song song, không cache hoặc cấp quyền bằng JWT.
- Scope đề xuất cho đúng hành động: `danh_sach_benh_nhan_lien_ket`, consent purpose `health_data`, thêm `family_sharing` ở nhánh người thân. Không dùng scope thuốc/hồ sơ để ghi một lần xem danh sách quan hệ.
- Mỗi patient được trả cần một `access_logs` allowed với đúng actor và subject. Các allowed của cùng request nằm trong một transaction và phải bền vững trước response; lỗi audit giữa chừng làm cả request 503, rollback toàn bộ allowed của request, không trả danh sách hoặc commit allowed một phần. Denied đã ghi bền vững ở transaction riêng không bị rollback theo request.
- Patient bị lọc không tạo denied chỉ vì không đủ điều kiện; API không nhận request truy cập riêng patient đó.
- Danh sách rỗng ghi audit metadata mức request, không tạo access log với patient giả.
- Admin bị từ chối trước khi duyệt các bệnh nhân; ghi denied mức request ở transaction riêng, không mất khi rollback request. Không gán một bệnh nhân tùy ý làm subject.
- Audit metadata không chứa tên, hồ sơ, nội dung y tế, token hay thông tin liên lạc. Phương án lưu audit mức request phải dùng cơ chế audit sẵn có và được thiết kế trong plan.
- Đăng ký route vào registry enforcement/CI hiện có; metadata OpenAPI không tự cấp quyền.
- Không có mặt trong danh sách không làm lộ lý do; có mặt trong danh sách không cấp quyền cho request sau. API thuốc/lịch sử/tương tác vẫn kiểm quyền riêng. Task này không sửa Mobile hoặc cấp quyền chia sẻ.

## 4. Thay đổi phá vỡ và client bị ảnh hưởng

Không có. Client đang dùng `/family/caregivers` tiếp tục quản lý người giám sát của chính họ. Client của task 5.14 sẽ dùng endpoint mới; controller Mobile hiện có chưa có repository lấy danh sách này nên không đổi schema client đang sử dụng. Task 5.15 chịu trách nhiệm ngữ cảnh patient sau khi chọn.

## 5. Đối chiếu tiêu chí chấp nhận

| AC | Endpoint phục vụ |
|---|---|
| AC1 | 200 chỉ trả ID/tên của patient đủ active + sharing + hai consent; distinct patient_id. |
| AC2 | 200 items rỗng khi không có patient đủ quyền; audit request-level. |
| AC3 | Quyền DB mỗi request, cùng token vẫn loại patient ngay sau thay đổi liên kết/chia sẻ/một trong hai consent. |
| AC4 | 401 token không hợp lệ; 403 admin, không có dữ liệu danh sách. |
| AC5 | 503 khi audit không ghi bền vững; không trả danh sách một phần. |
| AC6 | Admin bị từ chối có denied bền vững trong transaction riêng; lỗi ghi denied thì 503. Không đánh đồng lọc danh sách với từ chối cả request. |
| AC7 | Loại pending/rejected/revoked, liên kết của người khác, sharing tắt và thiếu consent; liên kết lại chưa chia sẻ vẫn bị loại. |
| AC8 | Tên trùng vẫn là hai UUID riêng; strict response projection chỉ hai field. |
| AC9 | Thiếu health_data bị loại ngay cả khi vẫn active, sharing bật và family_sharing còn hiệu lực. |
| AC10 | Mỗi patient được trả có một allowed đúng actor/subject/scope `danh_sach_benh_nhan_lien_ket`, không có tên/nội dung y tế trong audit. |
| AC11 | Empty-list ghi metadata mức request, admin 403 ghi denied transaction riêng; không có subject giả. Audit bắt buộc lỗi trả 503. |
| AC12 | Tiền đề schema để triển khai scope/audit mới: migration mới, kiểm reset sạch và giữ audit cũ khi nâng cấp. Đây là tiêu chí DB cho plan/implement/test, không thêm endpoint hay field response. |
| AC13 | Giữ grant tối thiểu và revoke/trigger append-only trên các bảng audit. Đây là tiêu chí DB cho plan/implement/test, không thay đổi quyền client gọi API. |
| AC14 | OpenAPI ghi rõ allowed trong cùng transaction, audit lỗi rollback toàn bộ allowed; không tạo denied chỉ vì lọc ứng viên không đủ quyền. |

## 6. Kiểm tra đã chạy

| Lệnh | Kết quả | Log |
|---|---|---|
| `python -X utf8 work/5.13/scratch/validate_contract.py` | PASS parse JSON/khóa duy nhất; 450 local refs resolve; 55 operationId không trùng; schema Draft 2020-12 và 6 ví dụ response hợp lệ (UUID có format check); kiểm field bắt buộc, cấm field ngoài response và cache headers. So baseline: chỉ thêm một endpoint và hai schema. | `evidence/contract-validate.log` |
| `git -C api_contract diff --check` | PASS, exit 0. | `evidence/contract-diff-check.log` |
| `python .agents/scripts/scope.py 5.13 --stage contract` (có quyền đọc Git submodule) | Exit 1: hai file contract trong phạm vi; ba file Firebase untracked có từ trước trong Frontend bị đánh dấu ngoài phạm vi. Không nhận kết quả chạy sandbox ban đầu vì Git bị từ chối khiến script bỏ sót thay đổi. | `evidence/contract-scope.log` |
| `python .agents/scripts/gate.py 5.13 contract` | PASS, requirement size L đã được duyệt lại, cổng contract mở trên đầu vào mới. | `evidence/contract-gate.log` |

Không chạy test Backend/DB vì chưa implement. Không có lệnh validate OpenAPI toàn phần được quy định trong AGENTS/README; môi trường hiện tại không có `openapi_spec_validator`. Các kiểm tra trên không thay thế validate đầy đủ OpenAPI meta-schema.

## 7. Câu hỏi mở

Không còn câu hỏi nghiệp vụ hoặc schema chặn contract. Requirement size L đã bao gồm migration, audit request-level và AC10–AC14; đã đối chiếu lại bản draft với approval mới. Scope toàn workspace còn baseline Firebase ở mục 8, không coi đây là scope pass.

## 8. Phát sinh

1. `backend/supabase/migrations/20260927082912_rebuild_schema_v11.sql:24` định nghĩa enum `access_data_scope` chỉ có năm giá trị thuốc/hồ sơ/lịch sử/tương tác/món ăn. Không có giá trị mô tả danh sách quan hệ. `access_logs.data_scope` dùng enum này, nên scope mới cần migration mới; không thể chỉ thêm Enum Python. Audit mức request cũng cần đối chiếu các ràng buộc operation/subject của `family_link_audit_events` trước khi chọn nơi lưu.
2. Đã xử lý phát sinh requirement: người dùng reopen và duyệt lại bản size L ngày 2026-11-10 lúc 13:03 +0700. Phạm vi hiện bao gồm migration mở rộng scope và các operation/ràng buộc audit cần thiết; AC10–AC14 kiểm audit đúng hành động, request-level, DB sạch/nâng cấp, append-only/grant và tính nguyên tử của allowed. Không cần reopen requirement thêm cho phát sinh này; chi tiết file migration và nơi lưu request-level audit thuộc plan.
3. `backend/tests/architecture/test_module_dependencies.py` cho phép access → family/consent/identity, nhưng không family → access. Plan cần bố trí use case/composition theo ranh giới hiện có; không thêm vòng phụ thuộc. Nếu cần quan hệ mới phải cập nhật C4 trước, đưa ra ngoài phạm vi để duyệt theo AGENTS.
4. Đã đối chiếu `wf-db-migration`: migration mới thay vì sửa migration đã áp dụng, không mở quyền client, giữ access_logs append-only, kiểm DB sạch ở các giai đoạn được phép. Giai đoạn contract chưa sửa code Backend/migration hay tài liệu docs.
5. Scope scan toàn workspace bị chặn bởi `frontend/mobile/android/app/google-services.json`, `frontend/mobile/firebase.json`, `frontend/mobile/lib/firebase_options.dart`. Ba file untracked này đã xuất hiện trong output status Frontend ở lượt kiểm tra code trước khi bắt đầu giai đoạn contract. Agent không tạo, sửa, đọc nội dung, stage hoặc xóa các file này; đây không phải thay đổi của 5.13. Người dùng cần xử lý hoặc xác nhận baseline riêng trước khi coi scope toàn workspace đã sạch; không tự sửa chúng để làm scope pass.

## Bước tiếp theo

- Đang chờ: người duyệt xem bản contract đã đối chiếu requirement size L mới.
- Lệnh người duyệt: `python .agents/scripts/gate.py approve 5.13 contract`.
- Sau approval contract: dùng gate xác định bước plan, lập `03-plan.md` gồm migration, PEP/scope, audit request-level/per-patient, registry CI và test cho AC1–AC14. Không triển khai Backend trong lượt contract này.
- Scope chưa đạt trên toàn workspace do ba file Firebase có từ trước; phần diff do agent tạo chỉ gồm hai file contract và artifact/evidence trong `work/5.13/`.
- Chưa commit/push. File code Backend không thay đổi trong giai đoạn này.
- Cập nhật lần cuối: 2026-11-10, Codex.
