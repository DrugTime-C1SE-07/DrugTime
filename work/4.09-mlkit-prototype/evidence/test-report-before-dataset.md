---
task: 4.09-mlkit-prototype
stage: test
status: draft
---

# 4.09 · Test Android — đang thu thập bằng chứng

Báo cáo nháp đang làm, chưa đủ điều kiện duyệt test hoặc kết luận go/no-go. Vòng hiện tại ghi nhận pilot người dùng báo và lấy raw từ ứng dụng; không chạy lại automation hoặc benchmark.

## 1. Môi trường

- Implement và plan Android-only đã approved; gate test OK, evidence/test-gate.log. Không sửa 01/03/04 đã duyệt.
- Máy ảo người dùng: emulator-5554, sdk_gphone16k_x86_64, Android 17; kết nối ADB hiện ở trạng thái device. Không đóng/reboot hoặc thay dữ liệu máy ảo của người dùng.
- Không API/DB/backend integration trong scope; không reset DB. Không chạm kịch bản patient/consent/dose/RLS.
- Nguồn ảnh người dùng mô tả: ảnh mạng tĩnh, gồm vỉ thuốc và hộp thuốc; đánh giá định tính cả hai nhận diện khá ổn.

## 2. Kết quả theo tiêu chí chấp nhận

| AC | Bằng chứng hiện có | Trạng thái |
|---|---|---|
| AC1 | Người dùng đã mở prototype Android và thử hai ảnh; app trên emulator lưu 5 run có status=text. Năm run không tự đồng nhất với hai ảnh người dùng vừa mô tả. | Một phần: pilot định tính, chưa benchmark/điện thoại thật |
| AC2 | Đã lấy nguyên JSON của 5 run qua adb run-as, không sửa raw/metadata; runId riêng và hash ảnh/file được ghi trong results/user-pilot-index.json. | Một phần: đọc file được; chưa chứng minh bấm native share sheet |
| AC3 | Các run hiện lấy đều text; blank/hỏng/cancel không được người dùng báo đã kiểm trong vòng này. Log native/fake của implement chỉ là nguồn kế thừa. | Pending kiểm chứng vòng test |
| AC4 | Chưa có báo cáo thao tác lặp/back/background/restart hoặc engine lỗi của người dùng. | Pending |
| AC5 | Chưa có bộ 4.08 chụp thật/nhãn xác minh/protocol frozen; mã ảnh nhập tay hiện trùng. | Pending |
| AC6 | Theo nguồn implement: on-device, không ghi thuốc. Vòng này không thay code hoặc dùng nhãn để sửa raw. Chưa chạy lại kiểm tra mạng trong lượt người dùng thử. | Kế thừa evidence implement, chưa xác minh toàn bộ vòng test |
| AC7 | Không có ngưỡng/benchmark đủ đại diện. | Pending, không go/no-go |
| AC8 | Ghi đúng pilot và nguồn từng bằng chứng; không suy status=text là nhận diện đúng hoặc tính accuracy=100%. | Đã áp dụng cho báo cáo này |

### Nhận xét trực tiếp của người dùng

Người dùng báo đã test hai ảnh mạng tĩnh (vỉ thuốc, hộp thuốc) và cả hai cho kết quả khá ổn. Đây là nhận xét định tính, không phải nhãn đã xác minh, không có tử/mẫu accuracy theo tên/hoạt chất. Chưa xác định hai ảnh vừa báo tương ứng runId nào trong năm run có sẵn; không tự chọn hai run tốt nhất.

## 3. Kịch bản chất lượng đã phủ

Không có QA cross-patient/consent/dose/interaction/schema áp dụng vì task chỉ prototype OCR bao bì cục bộ. Native permission/gallery/share/lifecycle và chất lượng nhận diện vẫn phải kiểm theo plan.

## 4. Automation và toàn bộ bộ test

- Vòng ghi nhận này chưa chạy automation hoặc benchmark. Không coi log ở implement là lần chạy test mới.
- Evidence kế thừa từ 04 approved: 546 test Flutter, 13 evaluator test, native smoke trên AVD riêng và analyzer/build. Cần đối chiếu/chạy bộ phù hợp khi thực hiện vòng test đầy đủ theo wf-test.
- Lệnh lấy dữ liệu: adb -s emulator-5554 exec-out run-as vn.drugtime.drugtime_mobile ls/base64/sha256sum trong files/ocr_runs; script chỉ ghi nguyên payload JSON vào results/runs, từ chối overwrite nội dung khác.
- Log import thực tế: evidence/test-user-pilot-import.log; 5 run, 5 hash byte ảnh khác nhau, tất cả status=text. Số hash byte khác nhau không chứng minh có 5 cảnh chụp/loại bao bì khác nhau.
- Scope sẽ lưu vào evidence/test-scope.log; repo có code implement đã approved và 136 thay đổi riêng được người dùng cho giữ. Vòng này chỉ ghi work/4.09-mlkit-prototype; không sửa frontend.

## 5. Bộ test case Excel

Chưa thực hiện trong vòng ghi nhận pilot này; làm theo wf-testcase trước khi hoàn tất giai đoạn test. Chưa có số Pass/Fail chính thức cho workbook; các mục chưa chạy phải Pending.

## 5b. Lỗi sản phẩm tìm thấy

### OCR-TILT-01 · Vỉ thuốc nghiêng 1 giờ / 7 giờ

- Nguồn: người dùng báo trực tiếp sau khi thử prototype Android; ca manual được người dùng đánh giá không đạt.
- Đầu vào: ảnh vỉ thuốc có hướng chữ/bao bì nghiêng theo mô tả 1 giờ và 7 giờ; chưa có góc độ chuẩn hoặc ảnh đối chứng ánh xạ runId. Không tự quy ra góc số.
- Kỳ vọng kiểm: trên cùng ảnh, nhận diện phần chữ cần đọc; cần xác minh vùng chữ nhìn thấy và nhãn trước chấm định lượng.
- Thực tế người dùng báo: không đọc được ở hướng nghiêng. Chưa biết status=no_text hay status=text nhưng raw thiếu/sai; không dùng status=text để phủ nhận lỗi nhận diện.
- Kiểm tra thực hiện: tìm run mới trong files/ocr_runs trên emulator-5554; không có run mới ngoài 5 run đã lấy. Chưa xác định run nào của ảnh nghiêng; evidence/test-user-tilt-import.log.
- Nguyên nhân gốc: chưa xác minh. Code hiện dùng InputImage.fromFilePath + recognizer Latin, không có preprocessing/deskew; đây là bối cảnh kỹ thuật, không phải bằng chứng đủ để kết luận lỗi do góc.
- Bước chẩn đoán tiếp: giữ nguyên ảnh gốc; chạy bản có dòng chữ được căn ngang và bản nghiêng, mã ảnh riêng, lưu raw/runId; đối chiếu cùng vùng chữ để tách ảnh hưởng của góc với kích thước chữ/ánh sáng.
- Phạm vi: camera/crop/preprocessing thuộc 4.10, ngoài 4.09 theo requirement. Không thêm tự xoay/deskew vào code sản phẩm ở giai đoạn test. Nếu cần thay đổi sản phẩm hoặc AC, ghi đề xuất và dùng gate reopen theo quy trình; chưa sửa code.
- Ảnh hưởng AC1/AC5/AC7: hạn chế pilot phải báo rõ; chưa đạt điều kiện kết luận go/no-go cho ảnh nghiêng.

Mọi run người dùng nhập imageId=1 là vấn đề truy vết bộ dữ liệu, chưa kết luận là lỗi app vì imageId là trường người thử nhập.

## 6. Test không ổn định hoặc bị skip

Chưa chạy bộ test trong vòng ghi nhận này, không có thống kê skip mới. Các ca chưa thực hiện ghi Pending, không ghi Pass dựa trên status=text.

## 7. Phát sinh và raw bàn giao

- 5 run mới từ máy ảo người dùng đã lưu tại results/runs, thêm vào raw native smoke có từ implement. Index tách riêng results/user-pilot-index.json; không sửa results/native-smoke-index.json.
- Tất cả run mới mang imageId=1 nhưng có hash ảnh khác nhau. Dùng runId + inputImageSha256 để giữ độc lập, không dùng imageId=1 suy cùng một ảnh. Cần mã ảnh riêng ở lần chạy tiếp và manifest ánh xạ trước benchmark.
- Metadata gốc do người thử nhập được giữ nguyên; model/OS thực đọc qua adb nằm ở index, không ghi đè metadata.
- Xuất qua adb là lấy dữ liệu app, không phải test thành công native share sheet.
- Chưa có commit/push; không sửa artifact approved hoặc code sản phẩm.

## Bước tiếp theo

- Cập nhật 2026-10-28: người dùng yêu cầu đưa raw/script/báo cáo dùng chung sang datasets/ và chấm theo labels.xlsx (image_id, relative_path, drug_name, strength). Đề xuất cụ thể: [dataset-evaluation-change.md](dataset-evaluation-change.md). Plan approved hiện giới hạn ở work/ và requirement vẫn chấm hoạt chất, nên cần reopen đầu vào trước khi sửa evaluator; chưa triển khai hoặc sửa artifact approved.

- Tiếp tục giai đoạn test, chưa đề nghị duyệt 05.
- Ưu tiên đối chiếu OCR-TILT-01: cùng ảnh gốc và bản căn ngang, mã riêng, raw/runId và vùng chữ kỳ vọng; ghi đúng ảnh nghiêng không đạt, không gộp vào hai ảnh pilot nhận xét tốt.
- Người thử dùng mã ảnh riêng cho mỗi ảnh, xác định runId tương ứng vỉ/hộp nếu cần đối chiếu định tính; không suy từ raw hoặc chọn kết quả tốt nhất.
- Kiểm thêm ảnh không chữ/hỏng, cancel, double tap, back/background/restart và Xuất JSON qua share sheet, đọc trên máy khác.
- Agent hoàn thiện test report và testcases Excel theo wf-test/wf-testcase khi chạy vòng kiểm thử đầy đủ. Q1 (ngưỡng/model Android) và dữ liệu 4.08 đã xác minh phải chốt trước benchmark.
- Bàn giao 4.14: results/README.md, results/user-pilot-index.json và các file JSON được chỉ mục; chưa có accuracy/go-no-go.
- Cập nhật: 2026-10-27, Codex.

## Kiểm tra phạm vi vòng ghi nhận

- `scope.py --stage test` exit 1: “CHẶN: 149 file ngoài phạm vi”; evidence/test-scope.log. Gồm 13 file frontend của implement đã approved và 136 file nền mà người dùng đã cho giữ từ trước. Vòng ghi nhận này không sửa các file đó, chỉ thêm artifact/raw/evidence trong work/4.09-mlkit-prototype. Không báo scope toàn repo sạch và không đề nghị duyệt 05 khi báo cáo còn nháp.
