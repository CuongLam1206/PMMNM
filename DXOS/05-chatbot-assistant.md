# Thiết kế Chatbot AI Assistant cho DX-OS

Chatbot có **hai vai trò trong một bản thể**, đúng yêu cầu đề bài:
1. **Trợ lý hướng dẫn sử dụng hệ thống** — giải đáp "chức năng này là gì, thao tác ở đâu, làm thế nào" cho người dùng phần mềm (quản trị viên, nhân viên nội dung, bán hàng).
2. **Tư vấn viên nghiệp vụ** — hiểu quy trình doanh nghiệp đang chạy trên hệ thống (mô hình BPMN-lite, luật DMN-lite, log quyết định) để trả lời "tại sao hệ thống đề xuất sửa quy trình này mà không phải quy trình khác", "quy trình duyệt thủ công nằm ở bước nào, ai phụ trách".

## 1. Hai cửa vào, một não bộ

| Cửa vào | Đối tượng | Kênh | Ghi chú |
|---|---|---|---|
| Backend systray widget | Nhân viên/quản trị dùng Odoo | OWL component trong backend, mở từ thanh systray | Kèm ngữ cảnh màn hình hiện tại (model, action, view) gửi lên Dify làm context |
| Website widget | Khách truy cập website | Livechat widget có sẵn của Odoo | Dùng chung não nhưng kho tri thức và quyền khác nhau (chỉ tài liệu công khai + catalog) |

Cả hai gọi cùng một Dify chatflow; khác nhau ở `user`/`inputs` và bộ knowledge được bật (Dify hỗ trợ chọn dataset theo biến đầu vào qua node router).

## 2. Kiến trúc chatflow trong Dify

```
Người dùng hỏi
   │
   ▼
[Node phân loại câu hỏi] (question-classifier)
   ├─ A. Hướng dẫn sử dụng hệ thống
   │     ▼ [Knowledge: DX-OS docs + Odoo user docs + FAQ nội bộ]
   │       → trả lời kèm trích dẫn trang tài liệu + đường dẫn màn hình
   ├─ B. Nghiệp vụ & quy trình của doanh nghiệp
   │     ▼ [Tool: đọc mô hình quy trình]  [Knowledge: hồ sơ quy trình, biên bản duyệt]
   │       → trả lời dựa trên BPMN-lite/DMN-lite thật, kèm trích dẫn bước/quy tắc
   ├─ C. Tra cứu dữ liệu tác nghiệp (đơn hàng, khóa học, thread…)
   │     ▼ [Tool: Odoo read-only API] → trả lời có số liệu
   ├─ D. Yêu cầu hành động (tạo activity, nháp bài viết…)
   │     ▼ [Tool ghi có kiểm soát] → luôn tạo bản NHÁP / activity chờ duyệt, không tự commit
   └─ E. Ngoài phạm vi / cần con người
         ▼ chuyển livechat operator kèm tóm tắt hội thoại
```

Nguyên tắc grounding: mọi câu trả lời phải kèm nguồn (trang tài liệu, bước BPMN id, rule id, bản ghi Odoo). Không có nguồn thì nói "tôi không chắc" và đề xuất chuyển người — chống hallucination, và cũng là điểm cộng human-in-the-loop khi chấm thi.

## 3. Vai trò 2 hoạt động nhờ dữ liệu nào

Để trả lời được "tại sao sửa quy trình này", hệ thống phải **lưu vết suy luận của AI** ngay từ lúc phân tích:

- Model `dxos.process.definition` (BPMN-lite JSON) và `dxos.rule.definition` (DMN-lite) — xem tài liệu 03.
- Model `dxos.automation.proposal`: mỗi đề xuất tự động hóa lưu: quy trình nguồn, node/luật bị ảnh hưởng, đề xuất, **lý do AI đưa ra (rationale)**, dữ liệu dẫn chứng (số liệu [D] tại thời điểm phân tích), trạng thái duyệt (chờ/duyệt/từ chối + ghi chú người duyệt).
- Model `dxos.decision.log`: mỗi lần runtime DMN-lite ra quyết định trên dữ liệu thật đều ghi input → rule → output.

Khi user hỏi "tại sao bỏ bước duyệt thủ công ở bước X?", chatbot: tool đọc `dxos.automation.proposal` của quy trình đó → trích rationale + số liệu dẫn chứng + ai đã duyệt ngày nào → trả lời có trích dẫn. Khi hỏi "duyệt thủ công giờ ở đâu?", chatbot đọc mô hình BPMN-lite hiện hành (sau khi đã áp dụng thay đổi) → chỉ ra node user-task, người phụ trách (role), và màn hình Odoo tương ứng (activity/approval).

Đây là khác biệt cốt lõi so với chatbot RAG thông thường: **AI giải thích được quyết định của chính hệ thống**, vì mọi quyết định đều được lưu có cấu trúc chứ không nằm trong đầu model.

## 4. Kho tri thức (RAG)

| Dataset | Nguồn | Cập nhật |
|---|---|---|
| DX-OS docs | Tài liệu sản phẩm đội tự viết (module guide, FAQ) | Mỗi release, CI push lên Dify API |
| Odoo user docs (phần website domain) | Repo odoo/documentation hoặc bản tự tóm tắt | Cần kiểm tra giấy phép trước khi nạp (mục 6) |
| Hồ sơ quy trình doanh nghiệp | BPMN-lite JSON render thành văn bản mô tả + biên bản duyệt | Webhook khi definition thay đổi |
| Catalog & chính sách (cho cửa website) | product, page, chính sách bán hàng | Cron đồng bộ hằng ngày |

Kỹ thuật: chunk theo heading; hybrid retrieval + rerank (Dify hỗ trợ sẵn); citation bật sẵn; tiếng Việt dùng model embedding đa ngữ (kiểm chứng trong pha 1, ví dụ họ bge-multilingual / multilingual-e5 qua provider OpenAI-compatible tự host).

## 5. Ngữ cảnh màn hình (context-aware help)

Widget backend gửi kèm mỗi câu hỏi: `model`, `action/view id`, `record id` (nếu có), role user. Chatflow dùng biến này để:
- Ưu tiên tài liệu đúng màn hình ("bạn đang ở form sản phẩm…").
- Cho phép câu hỏi cụt: "nút này làm gì?" kèm selector element đang focus.
- Chặn tool ghi không đúng quyền của role.

## 6. Guardrails, đánh giá và giấy phép

- Guardrails: chặn prompt-injection từ nội dung web (nội dung trang được đánh dấu là data, không phải instruction); giới hạn tool ghi ở danh sách trắng; mọi tool ghi tạo bản nháp chờ duyệt.
- Bộ đánh giá: 50–100 câu hỏi thật chia 2 vai trò, chấm groundedness (có trích dẫn đúng không) và độ đúng thao tác; chạy mỗi lần đổi prompt (Dify có annotation/eval cơ bản, phần còn lại làm script gọi API).
- Giấy phép: nội dung RAG là dữ liệu/tài liệu, không phải mã nguồn nhúng — nhưng nếu nạp tài liệu odoo.com/documentation cần xác nhận giấy phép của repo đó trước khi phân phối; phương án an toàn nhất cho PoF là đội tự viết tài liệu DX-OS và chỉ trích dẫn link Odoo docs.

## 7. Bám vào hạ tầng livechat native của Odoo

Không xây kênh chat mới: dùng lại `im_livechat` + `website_livechat`.
- Chatbot script native (`chatbot.script.step`, 7 loại bước tại addons/im_livechat/models/chatbot_script_step.py:23-30) giữ các luồng tuần tự chắc chắn; nhánh `free_input_single/multi` là điểm chèn Dify (override `_process_answer` :305 hoặc controller `chatbot_trigger_step` addons/im_livechat/controllers/chatbot.py:41).
- Tin nhắn khách vào website đi qua override `message_post` tại addons/website_livechat/models/discuss_channel.py:93 — điểm chặn để bơm ngữ cảnh RAG/agent-assist.
- Khách vãng lai đã có `mail.guest` (addons/mail/models/discuss/mail_guest.py:16), không cần tự quản phiên.
- Nút chat nhúng sẵn qua template loader addons/website_livechat/views/website_livechat.xml:8; pha 1 có thể thay bằng embed.js của Dify (tài liệu 02) rồi chuyển sang widget native khi cần ngữ cảnh màn hình.
- Chuyển người: bước `forward_operator` native kèm tóm tắt LLM sinh trước khi chuyển.

## 8. Lộ trình

- Pha 1 (demo): cửa backend + classifier 2 nhánh A/B + dataset DX-OS docs + hồ sơ quy trình; trả lời có trích dẫn.
- Pha 2: tool tra cứu dữ liệu read-only, ngữ cảnh màn hình, cửa website dùng chung não.
- Pha 3: tool ghi có kiểm soát, đánh giá tự động, dịch đa ngôn ngữ.
