# Phân tích Dify 1.17.1 và cách áp dụng Agentic AI cho DX-OS

Nguồn: clone tại `/home/cuong/dify` (branch mới nhất, `web/package.json` = 1.17.1), phân tích source `api/`, `web/`, `docker/`. Bản 1.17 là dòng refactor: graph engine nằm ở gói pip `graphon` (0.7.0), repo chỉ còn lớp adapter `api/core/workflow/`.

## 1. Giấy phép — điểm phải xử lý trước tiên

LICENSE của Dify là **Apache 2.0 sửa đổi** với 2 điều kiện thêm:
1. Được dùng thương mại, kể cả làm backend cho ứng dụng khác — nhưng **không được vận hành môi trường multi-tenant** (mỗi workspace Dify = một tenant) khi chưa có phép bằng văn bản;
2. Không được xóa logo/copyright trong frontend (console/web app) của Dify.

Hệ quả cho DX-OS và PoF:
- Dùng Dify làm AI backend cho sản phẩm: **được phép**.
- DX-Lab triển khai một workspace duy nhất: **không chạm điều kiện multi-tenant**. Nếu sau này bán SaaS mỗi khách một workspace → phải xin license thương mại.
- Giấy phép sửa đổi này không còn là Apache-2.0 thuần (OSI), nên **repo sản phẩm không vendoring mã nguồn Dify**: repo chỉ giữ file cấu hình/DSL export (workflow, chatflow) và docker-compose tham chiếu image upstream; bản thân Dify được build/run từ source upstream theo đúng hướng dẫn của họ (thỏa "build từ source" mà không phân phối lại mã sửa đổi).
- Giữ nguyên logo Dify ở console khi demo.

## 2. Kiến trúc tự host

Nhóm service trong `docker/`: api (Flask) + worker (Celery) + worker beat + web (Next.js) + plugin daemon + code-execution sandbox + SSRF proxy + nginx + PostgreSQL + Redis + vector DB (chọn 1 trong ~15 lựa chọn: pgvector, qdrant, weaviate, milvus, chroma, elasticsearch…). Khuyến nghị DX-Lab: **pgvector** (nhẹ, cùng họ Postgres, đỡ một service) trừ khi cần quy mô lớn.

Loại app: chat, chatflow (chat + workflow), agent, workflow, text-generator. Workflow và chatflow là hai thứ DX-OS dùng nhiều nhất.

## 3. Engine workflow: danh sách node (đủ dùng cho mọi ý tưởng ở tài liệu 04)

| Nhóm | Node |
|---|---|
| Vào/ra | `start`, `end`, `answer`, trigger: `trigger-webhook`, `trigger-schedule`, `trigger-plugin` |
| AI | `llm`, `agent` (v1), `agent-v2` (agent chiến lược mới), `question-classifier`, `parameter-extractor` |
| RAG | `knowledge-retrieval`, `knowledge-index`, `datasource` |
| Tích hợp | `tool` (plugin/built-in), `http-request`, `code` (Python/JS sandbox) |
| Điều khiển | `if-else`, `iteration` (+start/end), `loop` (+start/end), `list-operator`, `variable-assigner`, `variable-aggregator`, `template-transform` (Jinja2) |
| Con người | `human-input` — tạm dừng run, render form/action, resume, có timeout (human-in-the-loop native) |

Biến: cú pháp selector `{{#node_id.key#}}`; scope hệ thống `sys.*`, `env.*`, `conversation.*`; memory hội thoại lấy từ bảng messages theo conversation_id (TokenBufferMemory, cấu hình cửa sổ/token trên node LLM).

Sự kiện stream (SSE): workflow_started / node_started / node_finished / text_chunk / llm chunk / iteration_* / loop_* / **human_input_required / human_input_form_filled / human_input_form_timeout** / workflow_paused / workflow_finished / error / ping… Có endpoint replay/resume `GET /v1/workflow/<run_id>/events` — hữu ích khi trình diễn tiến độ agent chạy dài.

Agent: chiến lược function-calling và chain-of-thought (ReAct) bản classic; bản 1.17 thêm hệ chiến lược dạng plugin và node `agent-v2` (gắn tool, binding strategy). Max iteration mặc định 10.

## 4. Mặt API cho hệ thống ngoài (đúng thứ Odoo sẽ gọi)

Auth: header `Authorization: Bearer app-<24 ký tự>` (API key kiểu app, tạo trong console, tối đa 10 key/app; key dataset riêng cho API knowledge).

| Endpoint | Dùng cho |
|---|---|
| `POST /v1/workflows/run` | Odoo gọi workflow (blocking hoặc streaming); payload `inputs`, `files`, `user` (bắt buộc, ánh xạ EndUser), `response_mode` |
| `POST /v1/workflows/<workflow_id>/run` | chạy đúng một phiên bản workflow đã publish |
| `GET /v1/workflows/run/<run_id>` | tra trạng thái/kết quả (`status`, `outputs`, `error`, `total_steps`, `total_tokens`) |
| `POST /v1/workflows/tasks/<task_id>/stop`, `GET /v1/workflows/logs` | dừng, tra lịch sử |
| `POST /v1/chat-messages` | chatbot: `query`, `conversation_id` (rỗng = hội thoại mới), `inputs`, `files`, `user` |
| `POST /v1/chat-messages/<task_id>/stop` | dừng trả lời đang stream |
| `GET /v1/conversations`, `DELETE`, `POST .../name`, `GET/PUT .../variables` | quản lý hội thoại và biến hội thoại (nhớ trạng thái giữa các phiên) |
| `GET /v1/messages`, `POST /v1/messages/<id>/feedbacks`, `GET .../suggested` | lịch sử, thumbs up/down (nuôi eval set), câu gợi ý |
| `POST /v1/files/upload` | upload ảnh/PDF (vision, tài liệu slide) trước khi gọi workflow |
| `GET /v1/parameters`, `/v1/info`, `/v1/meta` | cấu hình app cho widget |
| `GET /v1/workflow/<run_id>/events` | SSE replay/resume cho run dài |

Response blocking của workflow: `task_id`, `workflow_run_id`, `data{status ∈ succeeded|failed|stopped|partial-succeeded|paused, outputs, error, elapsed_time, total_tokens, total_steps}`; khi có node `human-input` thì status `paused` kèm `paused_nodes` — tức là **duyệt của con người có thể nằm ngay trong run Dify** nếu muốn.

Embed web: script `embed.min.js` + `window.difyChatbotConfig = {token, baseUrl, inputs, ...}` tạo bubble + iframe chat; trang share standalone `/chatbot/<token>`. Đây là cách nhanh nhất gắn chatbot lên website Odoo (phase 1), trước khi làm widget OWL native.

Giới hạn cần biết: concurrency theo app (`max_active_requests`, vượt trả 429); multi-tenant theo workspace, cô lập end-user theo tham chiếu `user` → EndUser; file upload mặc định 15MB.

## 5. Áp dụng vào DX-OS: công thức tích hợp

Chiều Odoo → Dify (chính): module `dxos_core` giữ base URL + API key theo từng app Dify (mỗi mục đích một app: assistant, bpmn-analyst, content-gen, quiz-gen…), gọi blocking cho hành động ngắn (sinh SEO, phân loại) và streaming/resume cho run dài (phân tích quy trình, agent duyệt trang). Mọi call ghi `dxos.ai.log` (app, inputs tóm tắt, run_id, outputs, latency, token) — vừa phục vụ chatbot nghiệp vụ vừa phục vụ demo "minh bạch AI".

Chiều Dify → Odoo (tool): tool HTTP trong Dify gọi controller read-only/ghi-nháp của `dxos_core` (auth `bearer` bằng API key Odoo `res.users.apikeys`, hoặc route webhook `base_automation` `/web/hook/<uuid>` cho luồng event). Không cấp cho Dify truy cập DB.

Ghép cho từng nhân vật:
- **Chatbot assistant (tài liệu 05)**: app chatflow; node question-classifier rẽ nhánh RAG; dataset docs + hồ sơ quy trình; tool đọc proposal/decision log; embed lên website bằng embed.js, backend gọi trực tiếp API kèm ngữ cảnh màn hình.
- **Phân tích BPMN-lite (tài liệu 03)**: app workflow nhận `inputs.process_json` + số liệu thực thi; chuỗi node: parameter-extractor (chuẩn hóa) → knowledge-retrieval (best-practices) → llm (đề xuất) → parameter-extractor (ép JSON schema proposal) → end. Odoo lưu proposal kèm rationale; duyệt nằm ở Odoo (single source of truth), không dùng human-input của Dify cho bước này để không phân tán trạng thái.
- **Feature domain (tài liệu 04)**: workflow sinh nội dung dùng llm + vision (ảnh sản phẩm) + parameter-extractor trả JSON đúng schema Odoo; agent-v2 + tool fetch cho QA trang; trigger-schedule hoặc ir.cron Odoo cho batch (phân tích review, phát hiện bài cũ).
- **Livechat hybrid**: bước free-text của `chatbot.script` gọi `/v1/chat-messages` với conversation_id ánh xạ phiên livechat; hết ý thì `forward_operator` kèm tóm tắt do LLM sinh.

## 6. Hạn chế và rủi ro

- Giấy phép sửa đổi (mục 1) — đã có phương án xử lý.
- Bản 1.17 đổi kiến trúc (graphon tách ngoài): bám version bằng cách pin tag image và export DSL thành file trong repo; test lại DSL khi nâng cấp.
- Footprint tự host không nhỏ (api+worker+web+db+redis+vector+sandbox): tài liệu yêu cầu máy demo tối thiểu và profile compose tối giản.
- Chất lượng tiếng Việt phụ thuộc model: chọn provider OpenAI-compatible tự host hoặc API thương mại ngay từ M0, đo bằng eval set.
- Không có connector Odoo chính thức → `dxos_core` là code của đội (đúng chỗ cần thể hiện năng lực tại hackathon).

## 7. Dùng gì ở pha nào

Pha 1: chatflow assistant + embed.js; workflow sinh nội dung/quiz/SEO (blocking); 1 workflow phân tích BPMN; dataset docs.
Pha 2: tool Dify→Odoo, conversation variables, feedback/eval, agent-v2 QA trang, trigger-schedule batch.
Pha 3: human-input node cho phê duyệt trong run dài, plugin tool riêng đóng gói dxos, multi-app routing.
