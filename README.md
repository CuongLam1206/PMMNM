# PMNM — DX-OS cho OLP Phần mềm nguồn mở 2026

DX-OS kiến trúc Open-Core: Odoo 19 community (domain Ứng dụng/Trang web: trình tạo
trang web, TMĐT, blog, diễn đàn, trò chuyện trực tiếp, học trực tuyến) + Dify
(agentic AI), theo mô hình H-P-D-I của đề bài.

## Các nhánh

| Nhánh | Nội dung |
|---|---|
| `main` | Tích hợp của đội, chỉ nhận merge đã review |
| `cuongld/idea` | Hồ sơ nghiên cứu, kế hoạch triển khai, công cụ tách codebase (`DXOS/`) |
| `dxos-clean` | Codebase Odoo 19.0 đã trim còn 78 module website-domain; 1 commit snapshot, không kèm lịch sử upstream |

## Bắt đầu development

git clone -b dxos-clean https://github.com/CuongLam1206/PMMNM.git dxos

Addon mới của đội đặt ngoài repo này theo addons-path, hoặc nhánh riêng rẽ merge
vào main. Công cụ tái tạo bản trim từ upstream Odoo: `DXOS/tools/trim_odoo.py`
ở nhánh `cuongld/idea`.

## Giấy phép

Odoo giữ nguyên LGPL-3 upstream, không chỉnh sửa; phần DX-OS sẽ chốt giấy phép
OSI khi team duyệt kế hoạch (xem `DXOS/03-bpmn-dmn.md`).

