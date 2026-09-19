# Tách codebase Odoo 19 về domain Ứng dụng/Trang web

## 1. Nguyên tắc

- **Không sửa một byte nào của mã nguồn Odoo.** Tiêu chí PoF của cuộc thi cấm chỉnh sửa mã nguồn thư viện đính kèm; Odoo là nền lõi mở (open-core) nên mọi giá trị của đội nằm ở layer addon riêng (`dxos_*`) và cấu hình Dify.
- "Tách codebase" vì vậy nghĩa là **chọn lọc module sẽ phân phối/đóng gói** (keep-list), áp dụng lúc build hoặc lúc tạo bản làm việc — không phải fork rồi sửa code.
- Keep-list là nguồn sự thật duy nhất, sinh tự động bằng closure phụ thuộc: muốn thêm/bớt domain thì sửa seed rồi chạy lại script, không chọn tay từng module.

## 2. Phương pháp

Script `DXOS/tools/compute_closure.py` parse toàn bộ `__manifest__.py` ở hai gốc addon (`addons/` và `odoo/addons/`), dựng đồ thị `depends` và lấy closure bắc cầu từ tập seed:

| Seed | Domain |
|---|---|
| `website` | trình tạo trang web |
| `website_sale` + glob `website_sale_*` (14 module) | TMĐT |
| `website_blog` | blog |
| `website_forum` | diễn đàn |
| `im_livechat`, `website_livechat` | trò chuyện trực tiếp |
| `website_slides` + glob `website_slides_*` | học trực tuyến |
| `website_mail` | hạ tầng website (mail bridge) |
| `theme_default` | theme mặc định cho theme configurator của website (không module nào `depends` vào nó, giữ vì lý do runtime) |

Kết quả đã chạy và kiểm chứng trên repo này (nhánh 19.0, commit 7bbce824): **tổng 662 module, giữ 78, xóa 584**; mọi module giữ đều có `depends` nằm trọn trong tập giữ (không có phụ thuộc trốn thoát); không có module `test_*` nào lọt vào closure.

## 3. Tập giữ (78)

Danh sách đầy đủ: `DXOS/tools/keep_modules.txt`. Chia 3 nhóm:

**(a) Website-domain (28)**: website, website_blog, website_forum, website_links, website_livechat, website_mail, website_mass_mailing, website_partner, website_payment, website_profile, website_sale + 14 website_sale_*, website_slides, website_slides_forum, website_slides_survey.

**(b) Nền tảng/core (28)**: base, web, bus, mail, portal, portal_rating, rating, digest, resource, utm, http_routing, auth_signup, google_recaptcha, social_media, web_tour, link_tracker, html_builder, html_editor, contacts, onboarding, base_setup, analytic, gamification, survey, im_livechat, theme_default, base_geolocalize, google_address_autocomplete.

**(c) Module nghiệp vụ bị TMĐT kéo vào (22) — quyết định team phải chấp nhận**: sale, sales_team, sale_stock, sale_mrp, sale_gelato, sale_loyalty, account, account_payment, stock, stock_account, stock_delivery, delivery, delivery_mondialrelay, barcodes, barcodes_gs1_nomenclature, payment, payment_custom, loyalty, product, uom, mrp, mass_mailing.

Bản đồ kéo theo (vì sao nhóm (c) tồn tại): `sale`←website_sale; `account`←sale+website_payment; `stock`+`barcodes`←website_sale_stock/website_sale_collect; `delivery`←website_sale; `payment`←website_payment; `payment_custom`←website_sale_collect; `loyalty`←website_sale_loyalty; `mrp`←sale_mrp←website_sale_mrp; `sale_gelato`←website_sale_gelato; `delivery_mondialrelay`←website_sale_mondialrelay; `mass_mailing`←website_mass_mailing←website_sale_mass_mailing.

**Biến thể LEAN (quyết định số 1 của team)**: nếu không muốn Manufacturing/Gelato/Mondial Relay/Marketing trong codebase, bỏ 4 seed `website_sale_mrp`, `website_sale_gelato`, `website_sale_mondialrelay`, `website_sale_mass_mailing` rồi chạy lại script; ước lượng bớt được khoảng 10 module (mrp, sale_mrp, sale_gelato, delivery_mondialrelay, mass_mailing, website_mass_mailing và các cầu nối) — con số chính xác phải chốt bằng cách chạy lại `compute_closure.py`. Chức năng mất: sản xuất theo đơn web, print-on-demand Gelato, giao hàng Mondial Relay, newsletter mass mailing.

## 4. Tập xóa (584) — phân nhóm sơ bộ

Danh sách đầy đủ sinh tự động: chạy `compute_closure.py` ghi ra `delete_modules.txt`. Các họ lớn: localization `l10n_*` (~231, thêm lại dễ dàng nếu cần thị trường cụ thể), POS `pos_*` (~42), `test_*` (~40), HR (~28), payment providers `payment_*` (~22), CRM (~20), sale mở rộng (~22), Project (~18), spreadsheet/dashboard (~15), hạ tầng auth/storage (~25), hạ tầng truyền thông (~15), mrp mở rộng (~10), mass_mailing mở rộng (~9), purchase (~9), event (~6), lịch/tài khoản ngoài (~6), tồn kho mở rộng (~6), khác (~36).

Module `website_*` bị xóa và lý do (27): website_cf_turnstile (captcha Cloudflare, không ai phụ thuộc), website_crm + 4 module cầu CRM (CRM ngoài phạm vi), website_customer (portal khách hàng, closure không cần), website_event + 11 module con (Events ngoài phạm vi), website_google_map (snippet bản đồ, không phụ thuộc), website_hr_recruitment + _livechat (HR ngoài phạm vi), website_mail_group, website_mass_mailing_sms, website_project, website_sms, website_timesheet (các app nền đã xóa).

## 5. Trường hợp biên đã kiểm tra

- **payment_demo bị xóa theo closure nhưng khuyến nghị giữ lại** cho dev/test checkout (chỉ phụ thuộc `payment`, nhỏ); thêm vào seed là xong. `payment_custom` đã nằm trong tập giữ nên luồng thanh toán chuyển khoản vẫn chạy được ngay.
- Không có tham chiếu XML/data nào từ module giữ trỏ sang module xóa (đã grep các họ dễ đứt gãy nhất: website_event.*, website_crm.*, web_unsplash.*, website_mail_group.*, website_sms.*, website_google_map.*, mass_mailing_slides.*, hr_skills_slides.*, spreadsheet_dashboard.* — chỉ còn 2 chuỗi vô hại trong test/scss của chính `website`).
- `setup/`, `MANIFEST.in` không liệt kê từng addon nên không đứt gãy đóng gói; i18n của module nào đi theo module đó.
- Odoo 19 community **không có module AI nào** (không `ai`, `mail_ai`, `knowledge`, `llm`, `openai`); chỉ có cờ context `text_must_be_translated_for_openai` trong `addons/website/models/html_text_processor.py` và `website.py` chờ bản Enterprise cấp dịch vụ dịch AI — tức là toàn bộ lớp AI là chỗ trống cho DX-OS + Dify lấp vào.

## 6. Ba cách áp dụng keep-list

| Cách | Làm gì | Khi nào dùng |
|---|---|---|
| A. Trim lúc build (khuyến nghị) | Dockerfile COPY nguồn Odoo rồi chạy `DXOS/tools/trim_odoo.py` trong image; repo gốc giữ nguyên | Đóng gói DX-Lab, demo, nộp thi — thỏa "build từ source" và không fork |
| B. Bản làm việc đã trim | `git worktree add` nhánh mới rồi chạy `trim_odoo.py` ngay trong worktree, commit riêng | Đội muốn IDE/repo nhẹ khi dev; hủy bằng cách xóa worktree |
| C. Không trim khi dev | Giữ nguyên repo, chỉ install đúng module domain vào database dev | Nhanh nhất để bắt đầu; trim chỉ dùng lúc đóng gói |

Cả ba cách dùng chung một keep-list và một script `trim_odoo.py` (chỉ xóa nguyên thư mục module, có `--dry-run`); không cách nào sửa nội dung file Odoo.

## 7. Việc cần làm khi team duyệt

1. Chốt biến thể seed (FULL hay LEAN, có giữ payment_demo không) → chạy lại `compute_closure.py` chốt số liệu.
2. Chọn cách áp dụng (A/B/C) cho pha dev hiện tại.
3. Nếu chọn B: tạo worktree `dxos-clean`, chạy trim, commit với message mô tả keep-list (kèm dòng Co-Authored theo quy tắc repo).
4. Đưa keep-list vào CI: job kiểm tra mọi module trong keep-list tồn tại và depends thỏa mãn (chống trôi khi rebase upstream).
