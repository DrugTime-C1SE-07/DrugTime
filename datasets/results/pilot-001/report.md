# Báo cáo OCR

Chế độ: pilot; quyết định: **not_decided**.

Nhãn: 17/17 hợp lệ; raw: 21 file.

| Thiết bị | Đúng/đã chạy | Accuracy | Coverage | Median / p95 ms |
|---|---|---|---|---|
| android/sdk_gphone16k_x86_64/17/emulator | 7/16 | 43.8% | 16/17 | 2762.5 / 15690 |

Tên chỉ đạt khi đúng cả cụm; đủ token nhưng tách xa là chẩn đoán phụ.
Hàm lượng chấm riêng; nhiều thành phần chưa có quy tắc thì chưa chấm.
JSON raw không bị sửa. Xem per_image.csv cho từng ảnh/run và summary.json cho nhóm chi tiết.

## Trạng thái các run được chọn để chấm

- exact_name: 7
- name_not_found: 7
- partial_name: 1
- tokens_present_noncontiguous: 1

## Từng ảnh theo run được chọn

| Image ID | Tên kỳ vọng | Kết quả | Run ID |
|---|---|---|---|
| efferalgan_box_002 | Efferalgan | exact_name | 0a64fa73-2f85-4874-9f4f-e219d4082c79 |
| strepsils_box_001 | Strepsils Original | exact_name | 331bf632-ef84-4936-938b-6b9a8c4de6b9 |
| tiffy_dey_box_001 | Tiffy Dey | name_not_found | 4406e44d-afda-4455-8ede-96f7e32a5357 |
| efferalgan_blister_002 | Efferalgan | name_not_found | 50bffbf2-d004-4e32-952a-dcb44b7e0c4e |
| efferalgan_blister_001 | Efferalgan | exact_name | 57cbedaf-a76d-4afd-aa7f-30017e37f949 |
| strepsils_box_002 | Strepsils Original | name_not_found | 771badfa-1e6a-4a38-95e7-6fd1fbce623d |
| tiffy_dey_blister_001 | Tiffy Dey | name_not_found | 81f82429-b3f5-464b-97f9-4beb00bf92e2 |
| decolgen_forte_box_002 | Decolgen Forte | name_not_found | 8454aea4-1990-4a2b-ae23-4872983aa75d |
| efferalgan_box_001 | Efferalgan | exact_name | 84d7b04c-4674-45a8-9a3f-aaca303120ac |
| strepsils_blister_002 | Strepsils Original | exact_name | b13325d8-d293-4ca2-9817-99ea58301f91 |
| tiffy_dey_box_002 | Tiffy Dey | name_not_found | ba4984d2-1833-49fe-ab08-f8295e05dee7 |
| decolgen_forte_blister_002 | Decolgen Forte | tokens_present_noncontiguous | bf2e373a-4ec0-49c7-9fc3-ad3e9063f55a |
| tiffy_dey_blister_002 | Tiffy Dey | name_not_found | cbea4918-6597-4eb1-9bb8-3e930c5aa3c5 |
| strepsils_blister_001 | Strepsils Original | exact_name | e312bc09-4530-484e-b1ad-7d6e4632755b |
| decolgen_forte_blister_001 | Decolgen Forte | partial_name | e6a6edae-8532-445b-9d2a-81ce280d4a49 |
| decolgen_forte_box_001 | Decolgen Forte | exact_name | f5ce68db-9f3b-4d8b-b297-aaf550df7e4b |
| decolgen_forte_blister_003 | Decolgen Forte | not_run |  |

## Nhóm sản phẩm và bao bì

| Nhóm / thiết bị | Đúng/đã chạy | Đã chạy/tổng nhãn |
|---|---|---|
| android/sdk_gphone16k_x86_64/17/emulator / product=decolgen_forte | 1/4 | 4/5 |
| android/sdk_gphone16k_x86_64/17/emulator / product=efferalgan | 3/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / product=strepsils | 3/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / product=tiffy_dey | 0/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / package_type=blister | 3/8 | 8/9 |
| android/sdk_gphone16k_x86_64/17/emulator / package_type=box | 4/8 | 8/8 |

## Tất cả hàng xuất (gồm run thừa/không ánh xạ/chưa chạy)

- exact_name: 8
- name_not_found: 8
- not_run: 1
- partial_name: 1
- tokens_present_noncontiguous: 3
- unmapped: 1

## Lỗi dữ liệu

- c6da86d5-1496-4f70-9fb2-720ae357221c: imageId/mapping has no valid label

## Giới hạn

- OCR occurrence is not catalog matching accuracy.
- Pilot samples are not automatically a representative benchmark.
- Unknown deviceKind is not evidence of a physical device.
