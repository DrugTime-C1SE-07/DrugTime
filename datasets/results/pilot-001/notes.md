# Ghi nhận pilot 2026-10-28

- Nhập thật từ emulator-5554 qua run-as/base64, chỉ đọc app; hash ảnh đối chiếu với datasets/images. JSON giữ nguyên byte, metadata nhập tay giữ nguyên. Thiết bị/OS thực đọc lúc import lưu riêng trong import-index.json.
- 4 raw mới được giữ tại raw/, 5 raw trên app đã có trong legacy-pilot nên không nhập trùng vào đợt mới. Legacy còn 1 native smoke từ AVD riêng, tổng 6 raw.
- 3 trong 4 raw mới khớp duy nhất 2 ảnh dataset. Một ảnh vỉ được chạy hai lần; báo cáo chọn run sớm nhất, không chọn theo điểm. Run c6da86d5-1496-4f70-9fb2-720ae357221c có hash ảnh không khớp ảnh hiện có: giữ unmapped và không đoán từ text.
- Run 71e2ac39-c00b-45b4-a5ea-f604fda06de5 trong screenshot người dùng gửi khớp decolgen_forte_blister_002, không phải decolgen_forte_box_001 gửi kèm. Chứng cứ hash: 0ad9abf2f3ba66699a7505ebc1438c7dca1631b5cf574aec6ef8b170a3eadcf3. Đây là xác minh đầu vào, không sửa raw imageId=1.
- Run hộp decolgen_forte_box_001 là f5ce68db-9f3b-4d8b-b297-aaf550df7e4b, hash d5049169d63b43483520d37019ac3bf3e16ae9d8bc8a0b435315134023021115.
- Tại lúc tạo báo cáo: 17 nhãn hợp lệ về cấu trúc, 2 ảnh có run chọn hợp lệ, 1 ảnh exact và 1 ảnh đủ token tách xa. Coverage 2/17; 15 ảnh chưa chạy. Đây là pilot, không go/no-go và không tuyên bố toàn bộ nhãn đã được người khác xác minh.
- Metadata cũ có giá trị nhập thử (osVersion=d, nativeSdkVersion=dd), không đủ cho benchmark chính thức. Cần nhập metadata thực ở đợt đo sau. Thông tin ADB quan sát lúc import giúp tách máy ảo, không thay đổi metadata ghi nhận lúc chạy.

Đọc report.md/per_image.csv/summary.json để xem báo cáo tái tạo; notes này là ghi nhận mốc thời gian, không thay báo cáo mới khi thêm run.
