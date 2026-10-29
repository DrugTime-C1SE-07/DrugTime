# Kết luận hướng ML Kit · GO

Ngày quyết định: **2026-10-29**. Người quyết định: người phụ trách PB31, xác nhận trực tiếp trong chat.

**GO để tiếp tục ML Kit Android sang chuẩn hóa/matching.** Đây là quyết định hướng kỹ thuật dựa trên pilot; không phải xác nhận đạt ngưỡng benchmark đặt trước, matching đúng hoặc đủ điều kiện phát hành.

Bộ dữ liệu v1: 588a56f54a5155250ce6c5fc633b60d05351f20561d46ba49ed482eab1b77e7f. 49 ảnh/49 raw, nhãn đã rà trực quan theo bao bì, chưa có xác minh độc lập của người khác.

Tên exact: **27/49 (55.1%)**; coverage 49/49.
Median 2615 ms; p95 5267 ms trên emulator, không đại diện điện thoại thật.

- exact_name: 27
- name_not_found: 14
- no_text: 1
- partial_name: 5
- tokens_present_noncontiguous: 2

Không cộng partial/token rời thành số matching đúng; không kết luận mọi name_not_found do nhãn sai. Raw/ảnh giữ nguyên. summary.json của CLI vẫn not_decided, quyết định thủ công ghi riêng tại đây và decision.json.

## Giới hạn và công việc bàn giao

- GO is a human engineering direction decision from a pilot, not a predefined-threshold benchmark pass.
- OCR partial/noncontiguous text has not been proven to match the correct catalog product.
- 49 images are not a representative test of all medication packaging/capture conditions.
- Only an Android emulator is represented; timing does not establish physical-phone performance.
- Labels were visually reviewed by an AI assistant; independent human review remains outstanding.
- Native share/gallery/error/offline/lifecycle manual checks are not waived by GO.
- Publication/PR/reviewer approval still pending; no commit or push performed.

Dùng raw/ cho 4.12–4.14; dùng run-map.csv/import-index.json để nối đúng ảnh. imagePath là sandbox Android, không phải URL ảnh. Các task sau vẫn phải đo matching trên danh mục thực.
