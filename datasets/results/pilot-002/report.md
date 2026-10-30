# Báo cáo OCR

Chế độ: pilot; quyết định: **not_decided**.

Nhãn: 49/49 hợp lệ; raw: 49 file.

| Thiết bị | Đúng/đã chạy | Accuracy | Coverage | Median / p95 ms |
|---|---|---|---|---|
| android/sdk_gphone16k_x86_64/17/emulator | 27/49 | 55.1% | 49/49 | 2615 / 5267 |

Tên chỉ đạt khi đúng cả cụm; đủ token nhưng tách xa là chẩn đoán phụ.
Hàm lượng chấm riêng; nhiều thành phần chưa có quy tắc thì chưa chấm.
JSON raw không bị sửa. Xem per_image.csv cho từng ảnh/run và summary.json cho nhóm chi tiết.

## Trạng thái các run được chọn để chấm

- exact_name: 27
- name_not_found: 14
- no_text: 1
- partial_name: 5
- tokens_present_noncontiguous: 2

## Từng ảnh theo run được chọn

| Image ID | Tên kỳ vọng | Kết quả | Run ID |
|---|---|---|---|
| atorvastatin_10_box_001 | A.TATORVASTATIN | name_not_found | 06f91517-adb5-4f5d-906f-f68c1e5d2cdf |
| metformin_500_blister_002 | Metformin | exact_name | 07a91d95-ea4b-4cfa-b360-a2b42c0d39de |
| candesartan_htz_32_25_blister_001 | Candesartan Krka | exact_name | 10f8e81e-003f-4009-8bc5-f91f15cf37d9 |
| levocetirizine_5_box_001 | 1-AL | name_not_found | 1c687834-2fb4-401c-8a07-ecf580d32a3c |
| tiffy_dey_box_001 | Tiffy Dey | name_not_found | 2684aa88-a381-43ac-a331-9cd50c541444 |
| decolgen_forte_blister_002 | Decolgen Forte | tokens_present_noncontiguous | 2c8f2b8e-9dde-4436-a6cf-9b6d5246d13c |
| bisoprolol_2_point_5_box_002 | A.TBisoprolol | partial_name | 2da6ca63-2bff-4b87-95f3-959067784a05 |
| efferalgan_blister_002 | Efferalgan | name_not_found | 35596a5b-074c-416d-a2c5-e3f748adb9aa |
| tiffy_dey_blister_002 | Tiffy Dey | name_not_found | 36aab102-d3ae-4fd6-9902-2870f087a5a2 |
| metformin_500_box_003 | Metformin | exact_name | 37336c67-2a7d-49ff-819c-e7324e8c254b |
| candesartan_htz_32_25_box_001 | A.TCANDESARTAN HTZ | partial_name | 3e2b29bd-ee6f-44b2-8470-7b9a9bf0bcb0 |
| decolgen_forte_blister_001 | Decolgen Forte | partial_name | 4505fc7c-5241-4a40-bffb-14ffaa685fff |
| strepsils_blister_002 | Strepsils Original | exact_name | 5b7c3812-6896-4ebf-9e77-d904bacbceb3 |
| metformin_500_box_001 | Metformin | exact_name | 64533465-627b-4e4c-b57a-9e97e71cd0e0 |
| efferalgan_blister_001 | Efferalgan | exact_name | 6799276d-9660-4172-823d-698ab37150a8 |
| atorvastatin_10_blister_002 | Atorvastatin | exact_name | 6c38adb0-5fee-4b4e-b70f-9d91f42e1422 |
| atorvastatin_10_blister_001 | Atorvastatin | exact_name | 7134a04f-fc31-41fb-bd01-227c95a2b108 |
| levocetirizine_5_box_002 | 1-AL | exact_name | 72147707-9021-4f94-a171-c1946e4a33d1 |
| strepsils_blister_001 | Strepsils Original | exact_name | 7da78f76-0b14-4a57-9642-1b5bd7c902f7 |
| decolgen_forte_box_002 | Decolgen Forte | name_not_found | 8d81e335-9dc0-4df6-9051-c73abf139f27 |
| efferalgan_box_002 | Efferalgan | exact_name | 9045e139-e68d-4a56-beee-23f36e3f954f |
| cilnidipine_5_box_002 | Clidipine | name_not_found | 923f520b-99a8-4cbc-ac18-8fc06167a683 |
| candesartan_htz_32_25_box_002 | ACANTANHTZ | exact_name | 976ae91d-b79d-48a9-9444-3468c964a30a |
| decolgen_forte_blister_003 | Decolgen Forte | tokens_present_noncontiguous | 99eaa534-e48b-44f1-8bd6-f72a4d4be482 |
| levocetirizine_5_box_003 | Lifezine | exact_name | 9d81f31b-7e89-4365-954a-0347c7c03fae |
| bisoprolol_2_point_5_box_001 | A.TBisoprolol | name_not_found | 9df3f601-b3bb-4a4e-a5a4-3a7c7b132d4f |
| strepsils_box_001 | Strepsils Original | exact_name | a2a4ae32-c9e2-4703-8cee-0722430c6dee |
| bisoprolol_2_point_5_blister_001 | Bisoheart | no_text | be5bdeed-37c9-4208-bcf9-9e4634ed4f30 |
| loratadine_table_10_box_003 | Nó-lapin | partial_name | bf779f5c-16d3-417a-8c4b-6aedada08cd9 |
| metformin_500_box_002 | Metformin | exact_name | bfeb4070-46cc-4f72-82dc-59dd0e70fa15 |
| loratadine_table_10_box_001 | LoratadineSPM | name_not_found | c3ba9109-e0ef-4f08-8ede-e0401a6ee537 |
| cilnidipine_5_box_001 | Cilnidipine | exact_name | d1b6702a-cc87-4373-b4b1-f1952e71c5be |
| strepsils_box_002 | Strepsils Original | name_not_found | ddd2955d-a5b0-4be5-85df-3b1716da4e63 |
| cilnidipine_5_blister_001 | Cildip | exact_name | df88d05f-f180-4a73-85b9-ebc4eca02622 |
| tiffy_dey_blister_001 | Tiffy Dey | name_not_found | e0c21b32-8f62-4360-86df-f4ca7c2ac41e |
| efferalgan_box_001 | Efferalgan | exact_name | e10ce562-a06d-4e03-8991-a48310cb03f7 |
| atorvastatin_10_box_002 | Atorvastatin | exact_name | e37b994a-67d7-459e-b067-0d75b4863a73 |
| loratadine_table_10_box_002 | ALOR | name_not_found | e43d4c3a-5e6e-42b7-8771-e3b88bf56306 |
| decolgen_forte_blister_004 | Decolgen Forte | exact_name | e70fc2a4-737d-4ab4-beb6-80d0fda31a0d |
| metformin_500_blister_001 | Metformin | exact_name | e7a80d6a-3cbe-4890-b07a-cfc29bc7e9a1 |
| tiffy_dey_box_002 | Tiffy Dey | name_not_found | ef381c48-a299-40c4-86a6-0f5541d79dca |
| levocetirizine_5_box_004 | Levocetirizin | exact_name | f06d9227-c843-4c16-9ae2-c8c923bedf35 |
| atorvastatin_10_box_003 | Atorvastatin | exact_name | f23251be-4b45-407b-a928-a88dd3d02008 |
| cilnidipine_5_box_003 | CILPOL | exact_name | f2a05f89-d16b-4da0-9fe5-9e1023f45dd6 |
| cilnidipine_5_blister_002 | Cilapress | exact_name | f2dbbcff-0e27-47c4-87b7-4edaac90ec94 |
| bisoprolol_2_point_5_blister_002 | A.TBisoprolol | partial_name | f52a04a9-6103-4dd4-a644-2f22c8031217 |
| decolgen_forte_box_001 | Decolgen Forte | exact_name | f7a16f0e-9c18-4731-ad45-1c546e8acbd0 |
| atorvastatin_10_blister_003 | Atorvastatin | name_not_found | fea2622e-6a3e-4533-8dee-cd46826917a9 |
| levocetirizine_5_blister_001 | 1-AL | exact_name | ff0c4cb4-8066-4586-a00b-53f5ffb3cbba |

## Nhóm sản phẩm và bao bì

| Nhóm / thiết bị | Đúng/đã chạy | Đã chạy/tổng nhãn |
|---|---|---|
| android/sdk_gphone16k_x86_64/17/emulator / product=atorvastatin_10 | 4/6 | 6/6 |
| android/sdk_gphone16k_x86_64/17/emulator / product=bisoprolol_2.5 | 0/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / product=candesartan_htz_32_25 | 2/3 | 3/3 |
| android/sdk_gphone16k_x86_64/17/emulator / product=cilnidipine_5 | 4/5 | 5/5 |
| android/sdk_gphone16k_x86_64/17/emulator / product=decolgen_forte | 2/6 | 6/6 |
| android/sdk_gphone16k_x86_64/17/emulator / product=efferalgan | 3/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / product=levocetirizine_5 | 4/5 | 5/5 |
| android/sdk_gphone16k_x86_64/17/emulator / product=loratadine_tablet_10 | 0/3 | 3/3 |
| android/sdk_gphone16k_x86_64/17/emulator / product=metformin_500 | 5/5 | 5/5 |
| android/sdk_gphone16k_x86_64/17/emulator / product=strepsils | 3/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / product=tiffy_dey | 0/4 | 4/4 |
| android/sdk_gphone16k_x86_64/17/emulator / package_type=blister | 12/21 | 21/21 |
| android/sdk_gphone16k_x86_64/17/emulator / package_type=box | 15/28 | 28/28 |

## Tất cả hàng xuất (gồm run thừa/không ánh xạ/chưa chạy)

- exact_name: 27
- name_not_found: 14
- no_text: 1
- partial_name: 5
- tokens_present_noncontiguous: 2

## Lỗi dữ liệu

- Không có.

## Giới hạn

- OCR occurrence is not catalog matching accuracy.
- Pilot samples are not automatically a representative benchmark.
- Unknown deviceKind is not evidence of a physical device.
