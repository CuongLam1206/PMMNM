# Ý tưởng áp dụng Agentic AI cho từng domain của Ứng dụng Trang web

Phạm vi: 6 domain mà DX-OS khai thác trên Odoo 19 — Trình tạo trang web, TMĐT, Blog, Diễn đàn, Trò chuyện trực tiếp, Học trực tuyến.
Mỗi ý tưởng ghi rõ: giá trị nghiệp vụ, cách hiện thực bằng Dify (workflow / agent / RAG / tool), và độ ưu tiên cho hackathon (P0 = phải demo, P1 = nên có, P2 = tầm nhìn).

Nguyên tắc xuyên suốt (theo đúng tinh thần đề bài DX-OS):
- AI đứng ở không gian [I], chỉ tự hành trên nền quy trình [P] và dữ liệu [D] đã chuẩn hóa trong Odoo.
- Mọi hành động có tác dụng phụ (đăng bài, đổi giá, ẩn nội dung, gửi mail) đều đi qua **human-in-the-loop**: AI đề xuất → người duyệt → hệ thống thực thi.
- Mỗi lời gọi AI đều được ghi log (input, output, lý do) để chatbot nghiệp vụ có thể trả lời "tại sao hệ thống làm vậy" sau này.

---

## 1. Trình tạo trang web (website builder)

Hiện trạng Odoo: `website`, `website.page`, editor WYSIWYG + snippet, theme, SEO fields có sẵn trên page/view.

| # | Ý tưởng | Hiện thực bằng Dify | Ưu tiên |
|---|---------|---------------------|---------|
| 1 | **Sinh nội dung theo snippet**: nút "AI viết" trong editor sinh/rewrite tiêu đề, đoạn văn, CTA theo giọng thương hiệu, đa ngôn ngữ Việt/Anh | Chatflow + system prompt thương hiệu; gọi từ Odoo editor qua REST `/v1/chat-messages`, chèn kết quả vào snippet | P0 |
| 2 | **Sinh trang đích từ một câu mô tả**: user gõ "trang giới thiệu tiệm bánh ở Đà Lạt" → AI trả cấu trúc trang (danh sách snippet + nội dung từng khối) → Odoo render bản nháp để user sửa | Workflow: LLM phân tích ý định → LLM sinh JSON schema của page (snippet order + nội dung) → node code validate JSON → Odoo tạo `website.page` nháp | P0 |
| 3 | **SEO assistant**: sinh title, meta description, OG tag, alt text ảnh (model vision) cho từng page; chấm điểm SEO và gợi ý sửa | Workflow nhận HTML rút gọn + từ khóa → trả JSON fields; button "Chấm điểm SEO" trong page properties | P1 |
| 4 | **QA agent cho trang**: agent tự duyệt page (tool HTTP fetch) phát hiện link hỏng, ảnh thiếu alt, heading lệch cấp, chữ trùng nền | Agent node với tool `fetch_page`; chạy theo cron hoặc nút "Kiểm tra trang" | P2 |
| 5 | **Gợi ý bố cục & phong cách**: từ mô tả thương hiệu sinh palette màu/font áp vào theme variables | Workflow trả JSON CSS variables; áp qua record theme | P2 |

Điểm demo ăn tiền: ý tưởng 2 — gõ một câu, nhận một trang web hoàn chỉnh bản nháp, sửa bằng editor thật của Odoo.

## 2. Thương mại điện tử (website_sale)

Hiện trạng: `product.template`, giỏ/checkout controller của `website_sale`, payment acquirer, wishlist/comparison, `website_sale_stock`.

| # | Ý tưởng | Hiện thực bằng Dify | Ưu tiên |
|---|---------|---------------------|---------|
| 1 | **Sinh mô tả sản phẩm + SEO** từ thuộc tính + ảnh (vision): mô tả dài, bullet đặc trưng, meta, tên thân thiện URL | Workflow vision+LLM; nút "AI viết mô tả" trên form sản phẩm và bulk action cho danh sách sản phẩm | P0 |
| 2 | **Tìm kiếm ngữ nghĩa & "mua theo ý định"**: nhúng vector catalog sản phẩm; khách gõ "quà tặng dưới 300k cho mẹ" → trả sản phẩm đúng ngữ cảnh kèm lời giải thích | Knowledge base Dify index catalog (tên + mô tả + thuộc tính); chatflow trả JSON product ids → Odoo render grid | P1 |
| 3 | **Support bot trước chuyển giao**: bot trả lời câu hỏi sản phẩm/chính sách từ RAG catalog + tài liệu; hết khả năng thì chuyển operator kèm tóm tắt hội thoại | Chatflow RAG + node "forward to operator" của livechat; tóm tắt sinh bởi LLM trước khi chuyển | P0 |
| 4 | **Phân tích đánh giá**: sentiment + khía cạnh (giá, chất lượng, giao hàng) từ review → dashboard sản phẩm và gợi ý cải thiện mô tả | Workflow batch theo cron; kết quả ghi vào field phân tích trên sản phẩm | P2 |
| 5 | **Gợi ý thay thế khi hết hàng / upsell giỏ hàng**: rule DMN-lite (tồn kho, giá trị giỏ) chọn tình huống, AI viết lời mời kèm vào email/trang giỏ | DMN-lite quyết định trigger → workflow sinh copy → human duyệt với mail hàng loạt | P2 |
| 6 | **Cờ bất thường đơn hàng** (địa chỉ vô lý, số lượng đột biến): AI chấm điểm rủi ro, đơn điểm cao chuyển trạng thái chờ duyệt | Workflow nhận JSON đơn → trả score + lý do; Odoo tạo activity duyệt cho nhân viên | P2 |

## 3. Blog (website_blog)

Hiện trạng: `blog.blog`, `blog.post`, tag, trạng thái nháp/xuất bản, SEO fields.

| # | Ý tưởng | Hiện thực bằng Dify | Ưu tiên |
|---|---------|---------------------|---------|
| 1 | **Kho đề tài từ dữ liệu thật**: đào câu hỏi chưa được trả lời ở diễn đàn + từ khóa tìm kiếm nội bộ → danh sách đề tài bài viết kèm độ hấp dẫn ước tính | Workflow nhận export câu hỏi diễn đàn (tool gọi Odoo) → LLM cụm hóa + chấm điểm → danh sách đề tài | P1 |
| 2 | **Dàn ý + bản nháp theo giọng thương hiệu**: từ đề tài sinh outline SEO rồi viết nháp, chèn gợi ý liên kết nội bộ tới sản phẩm/trang | Workflow 2 tầng (outline → draft), tool `search_internal_links` truy vấn Odoo | P0 |
| 3 | **Tóm tắt & dịch**: tóm tắt bài dài thành thẻ meta/social; dịch bài sang ngôn ngữ website khác giữ nguyên định dạng | Workflow; ghi vào bản dịch của `website.page`/post | P1 |
| 4 | **Làm mới bài cũ**: phát hiện bài tụt hạng (theo analytics hoặc tuổi bài) → đề xuất cập nhật đoạn cụ thể | Cron + workflow so sánh nội dung với chủ đề hiện tại → đề xuất diff, người duyệt | P2 |
| 5 | **Kiểm duyệt bình luận**: phân loại spam/độc hại với ngưỡng tin cậy: cao thì tự ẩn, trung bình thì vào hàng đợi duyệt | Workflow phân loại trả score; DMN-lite chọn hành động theo ngưỡng | P1 |

## 4. Diễn đàn (website_forum)

Hiện trạng: `forum.forum`, `forum.post`, tag, điểm uy tín/badge, trường kiểm duyệt, `website_slides_forum` nối e-learning.

| # | Ý tưởng | Hiện thực bằng Dify | Ưu tiên |
|---|---------|---------------------|---------|
| 1 | **Chặn trùng lặp lúc gõ câu hỏi**: tìm ngữ nghĩa các thread đã có → gợi ý "câu hỏi này đã được trả lời" kèm link, giảm tải diễn đàn | Knowledge base index toàn bộ thread; chatflow trả top-k lúc user gõ (debounce) | P0 |
| 2 | **Gợi ý câu trả lời cho người trả lời/moderator**: RAG trên tài liệu sản phẩm + các câu trả lời hay đã duyệt → bản nháp trả lời, đăng bằng một click | Chatflow RAG; nút "AI nháp trả lời" trên form trả lời | P0 |
| 3 | **Tự gắn tag & phân loại chủ đề** khi tạo thread | Workflow phân loại trả JSON tags; áp tự động (không tác dụng phụ nặng nên không cần duyệt) | P1 |
| 4 | **Kiểm duyệt hai ngưỡng** như blog: độc hại/spam điểm cao tự ẩn + ghi log, điểm trung bình vào hàng đợi | Workflow + DMN-lite ngưỡng | P1 |
| 5 | **Đóng vòng tri thức**: thread đã giải quyết được thăng cấp thành bài KB/blog tự động (AI viết lại thành văn phong tài liệu) → nạp vào RAG của chatbot | Workflow rewrite + tạo bản nháp `blog.post`/KB chờ duyệt; sau duyệt index vào Dify | P1 |

Ý tưởng 5 là "câu chuyện cộng đồng" đẹp cho showcase: tri thức sinh ra từ diễn đàn quay lại nuôi trợ lý AI.

## 5. Trò chuyện trực tiếp (im_livechat / website_livechat)

Hiện trạng: kênh livechat, **chatbot script có sẵn** (`chatbot.script`, `chatbot.script.step` với các bước câu hỏi/văn bản/chuyển operator), canned responses, khách vãng lai (guest), kênh Discuss.

| # | Ý tưởng | Hiện thực bằng Dify | Ưu tiên |
|---|---------|---------------------|---------|
| 1 | **Chatbot hybrid**: giữ script tuần tự cho luồng chắc chắn (đặt hàng, bảo hành), khi script hụt ý thì fallback sang Dify chatflow RAG thay vì trả lời cứng | Override bước "free text": gọi Dify `/v1/chat-messages` với conversation id ánh xạ phiên livechat | P0 |
| 2 | **Trợ lý cho operator**: khung gợi ý trả lời thời gian thực (RAG tài liệu + tool đọc đơn hàng của khách đang chat), phát hiện cảm xúc/ý định | Chatflow stream; UI side-panel trong Discuss; operator bấm để chèn | P1 |
| 3 | **Tóm tắt + gắn nhãn sau phiên**: hết phiên, AI tóm tắt, gán tag chủ đề, tạo activity follow-up cho người phụ trách | Workflow trigger khi kênh đóng; ghi `mail.activity` | P1 |
| 4 | **Mời chat chủ động có kiểm soát**: DMN-lite quyết định khi nào mời (thời gian trên trang, giá trị giỏ, trang đang xem); AI cá nhân hóa câu mở đầu | DMN-lite trigger → workflow sinh câu mời → gửi qua livechat | P2 |
| 5 | **Phiên dịch thời gian thực** cho operator khách nước ngoài | Workflow dịch hai chiều, chèn bản dịch vào side-panel | P2 |

## 6. Học trực tuyến (website_slides)

Hiện trạng: `slide.channel`, `slide.slide` (pdf/video/article/quiz), `slide.question`/`slide.answer`, chứng chỉ, tiến độ `slide.channel.partner`, diễn đàn kèm kênh.

| # | Ý tưởng | Hiện thực bằng Dify | Ưu tiên |
|---|---------|---------------------|---------|
| 1 | **Sinh quiz từ nội dung slide**: từ PDF/article/video transcript sinh câu hỏi nhiều lựa chọn kèm giải thích từng phương án nhiễu | Workflow nhận nội dung slide → JSON câu hỏi → tạo bản nháp `slide.question` chờ duyệt | P0 |
| 2 | **Dàn ý + nội dung khóa học**: từ chủ đề + đối tượng sinh outline kênh và nháp slide article từng bài | Workflow 2 tầng; tạo bản nháp channel/slides | P1 |
| 3 | **Gia sư trong khóa học**: chatbot RAG scoped vào nội dung kênh, trả lời câu hỏi học viên ngay trang slide, không trả lời ngoài phạm vi khóa học | Chatflow với knowledge base = nội dung kênh; nhúng widget trang slide | P0 |
| 4 | **Lộ trình cá nhân hóa**: phân tích lỗi quiz + tiến độ → gợi ý slide ôn lại / kênh kế tiếp, kèm tin nhắn nhắc học khi có nguy cơ bỏ dở | Cron phân tích tiến độ → workflow sinh khuyến nghị → activity/mail nhắc | P1 |
| 5 | **Chấm câu trả lời tự luận + feedback**: câu hỏi dạng tự luận được AI chấm theo rubric và feedback cụ thể | Workflow chấm điểm trả JSON score + feedback; điểm cao/thấp bất thường chuyển người chấm | P2 |
| 6 | **Sinh chứng chỉ & câu hỏi ôn chứng chỉ** từ toàn bộ kênh | Workflow tổng hợp → bank câu hỏi ôn | P2 |

## 7. Ý tưởng liên domain (nền tảng DX-OS)

- **Content pipeline agent**: khoảng trống tri thức ở diễn đàn → nháp bài blog → SEO → chờ duyệt → xuất bản → index lại vào RAG. Một workflow Dify dài có node human-in-the-loop (duyệt trong Odoo).
- **Analytics copilot [D]**: hỏi bằng ngôn ngữ tự nhiên về dữ liệu domain (số phiên chat, tỷ lệ giải quyết diễn đàn, tiến độ học) → AI sinh truy vấn read-only trên Odoo → biểu đồ. Chỉ đọc, không cần duyệt.
- **BPMN-lite ↔ AI**: các quy trình vận hành website (duyệt nội dung, xử lý đơn, kiểm duyệt) được mô hình hóa bằng BPMN-lite; Dify phân tích mô hình + dữ liệu thực thi và đề xuất điểm tự động hóa — chính là các ý tưởng P0/P1 ở trên được "gắn địa chỉ" trong quy trình. Xem tài liệu 03 và 06.

## 8. Ma trận ưu tiên cho hackathon

P0 (demo chính): sinh trang từ câu mô tả; sinh mô tả sản phẩm; support bot RAG; chặn trùng diễn đàn + nháp trả lời; sinh quiz; gia sư khóa học; chatbot hybrid livechat; chatbot trợ lý hệ thống (tài liệu 05); BPMN-lite builder + AI đề xuất automation.
P1: SEO assistant, tìm kiếm ngữ nghĩa, trợ lý operator, tóm tắt phiên, kiểm duyệt hai ngưỡng, đóng vòng tri thức, lộ trình học, kho đề tài blog.
P2: phần còn lại — đưa vào roadmap "tầm nhìn cộng đồng" khi trình bày.

Cách chọn này tối ưu cho tiêu chí chấm: demo trực tiếp được ngay trên màn hình Odoo thật, có human-in-the-loop rõ ràng, và kể được câu chuyện H→P→D→I của đề bài.

---

## Phụ lục A. Điểm bám kỹ thuật đã xác minh trên repo (Odoo 19.0)

Đường dẫn dạng `addons/<module>/<file>.py:dòng`. Dùng khi ước lượng công sức từng ý tưởng.

**Trình tạo trang web**: `website` model tại website/models/website.py:99; `website.page` (inherits `ir.ui.view`) website_page.py:24; phục vụ trang qua ir_http.py:298 → website_page.py:371; controller website/controllers/main.py — save_xml :781, seo_suggest :810, tạo trang /website/add :672, server-action /website/action :1201; editor JS client_actions/website_preview/website_builder_action.js (nền html_builder). Hook: override create/write của page (website_page.py:164), thêm jsonrpc route theo mẫu seo_suggest.

**TMĐT**: product.template mở rộng tại website_sale/models/product_template.py:34 (website_description :64, description_ecommerce :72, _default_website_meta :818, _search_get_detail :873); controller website_sale/controllers/main.py — shop :285, product :559, _get_shop_domain :158, _prepare_product_values :808; giỏ tại controllers/cart.py; thanh toán provider-agnostic ở addons/payment/controllers/portal.py:258, xác nhận đơn sau `done` tại sale/models/payment_transaction.py (_post_process). Hook: _get_shop_domain cho search ngữ nghĩa, _prepare_product_values để bơm nội dung AI.

**Blog**: website_blog/models/website_blog.py — BlogPost :161, content :189, teaser :190, _compute_teaser :206, create/write :253-273, _default_website_meta :317; controller controllers/main.py blog :178, blog_post :227; nội dung sửa inline qua template website_blog_templates.xml:234-254. Hook: override create/write và _compute_teaser để bơm AI summary/SEO.

**Diễn đàn**: website_forum/models/forum_post.py — state :36-41 (active/pending/close/offensive/flagged), is_correct :71, quyền can_* :116-163, create :310-337 (trả karma); forum_forum.py ngưỡng karma :98-133; controller controllers/website_forum.py — post_create :412-437, hàng đợi duyệt :529, flag :622; karma/badge ở addons/gamification. Hook: post_create cho dedup + nháp trả lời; validate/_flag cho kiểm duyệt hai ngưỡng.

**Trò chuyện trực tiếp**: module `im_livechat`; chatbot.script.step có 7 loại bước (text, question_selection, question_email, question_phone, forward_operator, free_input_single, free_input_multi) tại models/chatbot_script_step.py:23-30, xử lý _process_answer :305 / _process_step :344; controller controllers/chatbot.py chatbot_trigger_step :41; website_livechat/models/discuss_channel.py:93 override message_post (điểm chặn tin nhắn khách); khách vãng lai mail.guest tại mail/models/discuss/mail_guest.py:16; embed loader website_livechat/views/website_livechat.xml:8 + route /im_livechat/loader/<id>. Hook chính cho chatbot hybrid: nhánh free_input → gọi Dify trước khi fallback.

**Học trực tuyến**: website_slides/models/slide_channel.py:19 (visibility :136, prerequisite_channel_ids :193); slide_slide.py — slide_category :88, html_content :108, question_ids :77; quiz models slide_question.py:8 và :62; chấm quiz tại controllers/main.py:1265-1314 (điểm ngưỡng, match đáp án); tiến độ slide_channel_partner.py (member_status :13-18); chứng chỉ qua website_slides_survey (survey.survey certification=True). Hook: controller quiz submit cho chấm tự luận AI; question_ids cho quiz sinh tự động.

**Xuyên suốt**: RPC mới REST `POST /json/2/<model>/<method>` auth bearer tại addons/rpc/controllers/json2.py:49 (JSON-RPC /jsonrpc vẫn còn, XML-RPC đã báo loại bỏ ở bản 22); API key Odoo `res.users.apikeys` (base/models/res_users.py:1519) xác thực bearer tại base/models/ir_http.py:212 — đây là auth cho tool Dify gọi Odoo; ir.cron._trigger (base/models/ir_cron.py:735) cho job AI hẹn giờ; bus `_sendone` (addons/bus/models/bus.py:111) đẩy kết quả AI lên trình duyệt realtime; base_automation on_webhook `/web/hook/<uuid>` (controllers/main.py:6) cho event từ Dify; ir.actions.server state code/webhook làm hook no-code.
