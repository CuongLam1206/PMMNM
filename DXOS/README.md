# DX-OS trên Odoo 19 + Dify — Hồ sơ nghiên cứu & kế hoạch triển khai

Hồ sơ này phục vụ review nội bộ đội thi và gửi team đánh giá trước khi code.
Bối cảnh: cuộc thi Phần mềm nguồn mở OLP 2026, chủ đề DX-OS/DX-Lab kiến trúc Open-Core,
mô hình H-P-D-I (xem `Quick-guide-to-DXOS.md` ở gốc repo).
Phạm vi sản phẩm: domain Ứng dụng/Trang web của Odoo — trình tạo trang web, TMĐT, blog,
diễn đàn, trò chuyện trực tiếp, học trực tuyến — khai thác Agentic AI triệt để qua Dify.

## Mục lục

| Tài liệu | Nội dung | Trạng thái |
|---|---|---|
| [01-tach-codebase.md](01-tach-codebase.md) | Danh sách giữ/bỏ module Odoo (78/584), cách tách codebase sạch, phương án build | đã có số liệu kiểm chứng |
| [02-phan-tich-dify.md](02-phan-tich-dify.md) | Phân tích Dify 1.17.1: kiến trúc, node workflow, RAG, API, giấy phép, công thức tích hợp | đã phân tích từ clone |
| [03-bpmn-dmn.md](03-bpmn-dmn.md) | Odoo có BPMN không; thiết kế BPMN-lite + DMN-lite (builder, form, rule engine, runtime) | đã khảo sát + thiết kế |
| [04-ai-usecases-website-domain.md](04-ai-usecases-website-domain.md) | Ý tưởng AI cho từng domain + ma trận ưu tiên + phụ lục điểm bám kỹ thuật | đầy đủ |
| [05-chatbot-assistant.md](05-chatbot-assistant.md) | Chatbot hai vai trò: trợ lý sử dụng hệ thống + tư vấn viên nghiệp vụ | đầy đủ |
| [06-ke-hoach-trien-khai.md](06-ke-hoach-trien-khai.md) | Kế hoạch triển khai tổng thể: kiến trúc, workstream, milestone, rủi ro | đầy đủ, chờ team chốt 6 quyết định |

## Cách đọc nhanh cho người review

1. Đọc `06` trước để thấy bức tranh và các quyết định cần chốt.
2. Đọc `04` để xem AI sẽ làm gì ở từng domain và đội định demo gì (mục P0).
3. Đọc `05` và `03` cho hai "nhân vật chính" của sản phẩm: chatbot nghiệp vụ và BPMN-lite/DMN-lite.
4. `01` và `02` là phụ lục kỹ thuật cho người sẽ trực tiếp build.

## Nguyên tắc bất biến (rút từ tiêu chí PoF của cuộc thi)

- Không chỉnh sửa mã nguồn Odoo/Dify/thư viện đính kèm; mọi giá trị thêm mới nằm ở layer addon `dxos_*` và cấu hình Dify xuất dạng file.
- Odoo giữ nguyên khả năng build từ source; phần "tách codebase" là curated keep-list áp dụng lúc build/đóng gói, không phải fork sửa code.
- Repo công khai, README + Changelog + bug tracker (GitHub issues), license OSI-approved cho toàn bộ code đội viết.
- Mọi hành động tự hành của AI đều có human-in-the-loop và log giải thích được.
