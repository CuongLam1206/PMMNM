# Kế hoạch triển khai DX-OS (bản để team review)

Trạng thái: bản nháp tổng hợp, các phụ lục kỹ thuật nằm ở tài liệu 01–03.
Chưa code sản phẩm — hồ sơ này để team đánh giá và chốt quyết định trước khi bước vào pha build.

## 1. Mục tiêu và phạm vi

Mục tiêu cuộc thi: DX-Lab mô phỏng H-P-D-I trên nền open-core, chấm 50 điểm PoF (loại trừ)
+ 50 điểm hackathon/showcase. Sản phẩm của đội:

- Nền lõi mở: **Odoo 19 community** (domain Ứng dụng/Trang web) + **Dify** (agentic AI platform), cả hai OSI-approved, giữ nguyên mã nguồn gốc.
- Layer giá trị của đội (open-core): bộ addon `dxos_*` trên Odoo + cấu hình Dify xuất thành file (DSL workflow) + tài liệu.
- Phạm vi domain: trình tạo trang web, TMĐT, blog, diễn đàn, trò chuyện trực tiếp, học trực tuyến.
- Hai nhân vật chính khi demo: **Chatbot AI Assistant** (trợ lý sử dụng + tư vấn nghiệp vụ, tài liệu 05) và **BPMN-lite/DMN-lite** (user mô hình hóa quy trình, AI đề xuất tự động hóa, user duyệt, tài liệu 03).

Ngoài phạm vi (nói rõ để team không lan man): các app CRM/HR/Sản xuất/POS…, không gian [H] SSO/storage chỉ dùng mức tối thiểu có sẵn (res.users, portal), không gian [D] dùng báo cáo Odoo + một analytics copilot đọc-only.

## 2. Kiến trúc tổng thể

```
┌──────────────────────────── DX-Lab (docker compose) ───────────────────────────┐
│                                                                                │
│  ┌─────────────── Odoo 19 (build đã trim theo keep-list, tài liệu 01) ───────┐ │
│  │  addons gốc giữ nguyên  +  addons-path bổ sung: ./dxos-addons            │ │
│  │    dxos_core      : connector Odoo↔Dify, queue, log AI, guardrails       │ │
│  │    dxos_bpmn      : BPMN-lite builder (bpmn-js) + runtime                │ │
│  │    dxos_dmn       : DMN-lite decision tables + rule engine + decision log│ │
│  │    dxos_assistant : chatbot widget backend + website, ngữ cảnh màn hình  │ │
│  │    dxos_web_ai    : AI features cho website builder + TMĐT               │ │
│  │    dxos_community : AI features cho blog + diễn đàn                      │ │
│  │    dxos_learn_ai  : AI features cho e-learning + livechat assist         │ │
│  └───────────────────────────────┬───────────────────────────────────────────┘ │
│                                  │ REST (workflows/run, chat-messages)         │
│                                  ▼                                             │
│  ┌────────────── Dify self-host (api, worker, web, plugin daemon) ───────────┐ │
│  │  chatflow trợ lý | workflow sinh nội dung | agent phân tích BPMN          │ │
│  │  datasets: DX-OS docs, hồ sơ quy trình, catalog | tools gọi ngược Odoo    │ │
│  └───────────────┬───────────────────────────────────────────────────────────┘ │
│                  ▼                                                             │
│   Postgres (Odoo) · Postgres+Redis+VectorDB (Dify) · LLM provider              │
│   (OpenAI-compatible self-host hoặc API, chốt ở mục 7)                         │
└────────────────────────────────────────────────────────────────────────────────┘
```

Chiều gọi: Odoo→Dify cho mọi thứ chạy server-side (nút bấm, cron, runtime BPMN).
Dify→Odoo qua tool HTTP gọi controller `dxos_core` (auth bearer/API-key, chỉ đọc hoặc ghi nháp).
Không cho Dify chạm thẳng database.

Ánh xạ H-P-D-I: [H] = người dùng Odoo + human-in-the-loop duyệt đề xuất; [P] = BPMN-lite runtime
+ automated actions Odoo; [D] = dữ liệu domain chuẩn hóa trong Odoo + decision log; [I] = Dify agents.
Đúng trình tự tuyến tính của đề bài: AI chỉ tự hành trên quy trình/dữ liệu đã chuẩn hóa.

## 3. Workstream và phân công (3 thí sinh + 1 giảng viên)

| WS | Nội dung chính | Đầu ra kiểm chứng được | Phụ trách đề xuất |
|---|---|---|---|
| WS0 Compliance & repo | repo công khai, LICENSE từng tệp, README/Changelog/issues, docker build từ source | checklist PoF xanh | cả đội, 1 người giữ |
| WS1 Nền & codebase trim | keep-list (tài liệu 01), Dockerfile trim, compose Odoo+Dify, CI cơ bản | `docker compose up` chạy cả hai | SV1 (backend/Odoo) |
| WS2 Connector + Chatbot | dxos_core, dxos_assistant, datasets, eval set | chatbot trả lời có trích dẫn 2 vai trò | SV2 (AI/Dify) |
| WS3 BPMN-lite/DMN-lite | dxos_bpmn, dxos_dmn, agent phân tích quy trình, luồng đề xuất-duyệt | demo vẽ quy trình → AI đề xuất → duyệt → runtime chạy | SV1 + SV2 |
| WS4 AI domain P0 | các feature P0 trong tài liệu 04 theo từng module | mỗi domain 1 demo 60 giây | SV3 (frontend/UX) + hỗ trợ |
| WS5 Demo & cộng đồng | kịch bản showcase, tài liệu người dùng, roadmap cộng đồng, blog post | slide + script demo | SV3 + giảng viên |

Giảng viên: review kiến trúc hằng tuần, giữ phạm vi, luyện demo.

## 4. Milestone

- **M0 (tuần 1)**: repo public + PoF checklist bản đầu; compose Odoo trim + Dify up; Dify hello-world workflow gọi được từ Odoo button.
- **M1 (tuần 2)**: dxos_core hoàn chỉnh (auth, log, queue, guardrails); chatbot v0 nhánh hướng dẫn sử dụng; BPMN-lite builder vẽ + lưu được JSON.
- **M2 (tuần 3)**: chatbot nhánh nghiệp vụ đọc được proposal/decision log; agent phân tích BPMN trả đề xuất có rationale; luồng duyệt đề xuất chạy end-to-end.
- **M3 (tuần 4)**: đủ feature P0 của 6 domain; eval set chatbot đạt ngưỡng; decision log phủ các luồng demo.
- **M4 (tuần 5)**: đóng băng tính năng; polish UX; kịch bản showcase diễn thử 2 lần; hồ sơ PoF rà lần cuối (license scan toàn repo).
- Buffer tuần 6 cho phát sinh trước hạn nộp.

## 5. Kịch bản demo dự kiến (xương sống showcase)

1. Chủ doanh nghiệp kể bài toán bằng một câu → AI sinh trang đích nháp (website builder).
2. Nhân viên nhập sản phẩm → AI viết mô tả + SEO; khách hỏi trên website → support bot RAG trả lời, kẹt thì chuyển livechat kèm tóm tắt.
3. Quản lý vẽ quy trình duyệt nội dung bằng BPMN-lite → AI phân tích dữ liệu diễn đàn/blog đề xuất bỏ bước duyệt trùng, kèm lý do và số liệu → quản lý duyệt → runtime áp dụng.
4. Nhân viên hỏi chatbot "tại sao bỏ bước duyệt đó?" → chatbot trích rationale + biên bản duyệt để trả lời.
5. Học viên vào khóa học → AI sinh quiz từ slide; gia sư RAG trả lời câu hỏi trong phạm vi khóa.

Mỗi bước đều chiếu được log AI và điểm human-in-the-loop — đúng tinh thần [I] của đề bài.

## 6. Rủi ro và giảm thiểu

| Rủi ro | Giảm thiểu |
|---|---|
| Closure phụ thuộc của website_sale kéo nhiều module kế toán/kho vào keep-list | chấp nhận và giải thích trong tài liệu 01; trim chỉ bỏ app không liên quan, không cố cắt dependency |
| Dify nặng (nhiều service) khi demo trên máy yếu | compose profile tối giản; vector DB chọn loại nhẹ; tài liệu yêu cầu phần mềm tối thiểu |
| Chất lượng LLM tiếng Việt | chốt provider sớm, eval set ngay M1; prompt tiếng Việt có few-shot |
| Vi phạm PoF do license tài liệu RAG hoặc thư viện JS nhúng | WS0 scan license trước khi nạp/nhúng; bpmn-js/dmn-js kiểm tra giấy phép ở tài liệu 03 |
| Lan man phạm vi (CRM, HR…) | phạm vi khóa ở mục 1; mọi ý tưởng mới vào backlog P2 |
| Odoo upgrade/rebase khó nếu fork sửa code | không fork sửa code; trim lúc build; addon tách repo-thư mục riêng |

## 7. Các quyết định team cần chốt khi review

1. Phương án trim: Docker build-time trim (khuyến nghị) hay nhánh repo đã xóa sẵn (có sẵn công cụ, tài liệu 01).
2. LLM provider: self-host OpenAI-compatible (tự chủ, demo offline) hay API thương mại (chất lượng cao, cần mạng + key).
3. Repo layout: monorepo (odoo fork-clean + dxos-addons + dify-config) hay 3 repo riêng; khuyến nghị monorepo cho chấm thi "build từ source" một lệnh.
4. Mức tự hành tối đa của AI ở demo: chỉ tạo bản nháp (khuyến nghị) hay cho phép 1 luồng tự commit có giám sát.
5. Vector DB và model embedding đa ngữ cho tiếng Việt.
6. Kịch bản demo chính thức chọn 3 trong 5 bước ở mục 5.

## 8. Việc cần làm ngay sau khi review duyệt

1. Chạy script trim tạo codebase sạch (tài liệu 01) trên nhánh riêng.
2. Dựng compose Odoo+Dify, tạo workspace Dify, import DSL workflow đầu tiên.
3. Khởi tạo dxos-addons skeleton + CI license scan.
4. Viết 20 câu hỏi eval đầu tiên cho chatbot từ tài liệu thật của đội.
