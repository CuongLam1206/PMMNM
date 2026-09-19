# BPMN/DMN trong Odoo 19: khảo sát và thiết kế BPMN-lite + DMN-lite cho DX-OS

## 1. Kết luận khảo sát: Odoo community 19 KHÔNG có BPMN/DMN

Bằng chứng tại repo `/home/cuong/odoo` (nhánh 19.0):
- Grep không hit code nào cho `bpmn`, `dmn`, `decision table`, `process model`, `workflow builder`, `bpmn-js` (vài hit `dmn` là false-positive i18n/PDF test).
- Không có model/engine `workflow` nào trong toàn bộ addon (từ khóa "workflow" chỉ xuất hiện như文案 marketing của mail gateway).
- Các app thiên về quy trình của bản Enterprise (`studio`, `knowledge`, `documents`, `sign`, `planning`, `approvals`) **không tồn tại trong cây community** (kiểm tra bằng git refs và GitHub API tại ref 19.0/18.0).

Thứ gần nhất mà native community có, và vì sao không phải BPMN:

| Công cụ native | Làm được gì | Thiếu gì so với BPMN |
|---|---|---|
| `mail.activity.plan` (Activity Plans) | chuỗi bước activity có thứ tự, hạn chổi tương đối, người phụ trách theo rule, liên kết bước kế tiếp | không canvas, không gateway/điều kiện, không song song, không instance quy trình toàn cục |
| `base_automation` (Automated Actions) | luật ECA trên 1 model: trigger on_create/write/unlink/time/message/**on_webhook** (`/web/hook/<uuid>`, auth public) → server actions (write/create/copy/code/webhook/email/SMS/activity) | luật một nhịp, không token/trạng thái quy trình, không chuỗi bước người dùng |
| `ir.cron` | hẹn giờ chạy server action | chỉ là timer |
| mail gateway (fetchmail) | mail đến → tạo bản ghi → chạy action | event-to-action, không mô hình hóa luồng |
| kanban stages của project/sale/… | trạng thái trực quan theo model | không phải mô hình quy trình riêng, không điều kiện chuyển trạng thái do user vẽ |

Hệ sinh thái: OCA không có repo BPMN nào (`OCA/workflow` 404); `base_tier_validation` (OCA/server-ux) là framework duyệt tuyến tính cấu hình bằng form, không trực quan. Module thương mại (AG Approval Workflow 19.0, MT-Workflow2) có designer trực quan nhưng giấy phép đóng/không công bố — loại vì rủi ro lock-in và vi phạm tinh thần open-core. Kết nối Camunda/Flowable/Activiti đều là tích hợp REST tự viết, thêm gánh nặng vận hành JVM — loại làm mặc định.

**Hệ quả cho keep-list**: không có module BPMN native nào để giữ; khoảng trống này chính là chỗ DX-OS điền vào. Các khối native ở bảng trên được GIỮ và dùng làm runtime (chúng đều nằm trong closure hoặc core).

## 2. Thiết kế DX-OS: BPMN-lite + DMN-lite

Đúng deal của đề bài: BPMN-lite trả lời "công việc tiếp theo là gì?", DMN-lite trả lời "dữ liệu hiện tại thì quyết định gì?". Bốn thành phần:

### 2.1 Visual Process Builder
- Module `dxos_bpmn`, widget OWL nhúng **bpmn-js (giấy phép MIT**, họ bpmn.io; tương thích khi nhúng vào module LGPL-3 như Odoo) render canvas trong backend.
- Nguồn sự thật là **BPMN-lite JSON** (nodes/edges/điều kiện gateway kiểu domain Odoo) — dễ cho LLM đọc/ sinh hơn XML; xuất/nhập BPMN 2.0 XML chỉ là interoperability option.
- Model `dxos.process.definition`: name, version chain (mỗi lần publish tạo revision), json graph, xml export, model Odoo đích (model mà quy trình chạy trên, ví dụ `blog.post`, `sale.order`), trạng thái draft/published.
- Palette giới hạn ở tập node BPMN-lite: start, end, user-task, service-task, exclusive-gateway, parallel-gateway, timer-event, decision-task (gọi DMN-lite), ai-task (gọi Dify). Không cố nhái toàn bộ BPMN 2.0.

### 2.2 Form Builder
- Mỗi user-task trỏ tới một trong hai: (a) view/form Odoo có sẵn của model đích, hoặc (b) `dxos.form.definition` — schema form JSON (fields kiểu char/selection/m2o/monetary…) render động bằng OWL cho các bước không thuộc model nào (ví dụ bước "thu thập ý kiến quản lý").
- Tận dụng web editor có sẵn của Odoo cho (a); chỉ xây dynamic form renderer cho (b) — giữ phạm vi nhỏ.

### 2.3 Rule Engine (DMN-lite)
- Model `dxos.dmn.table` + `dxos.dmn.rule`: cột input (field của model đích hoặc biến quy trình, toán tử =, !=, >, <, in, contains, regex), cột output (giá trị hoặc biến gán), hit policy FIRST/ANY theo thứ tự ưu tiên.
- Editor dạng bảng trong backend (không cần dmn-js ngay; dmn-js MIT là phương án nâng cấp UI sau).
- Mọi lần evaluate ghi `dxos.decision.log`: bảng, rule trúng, input snapshot, output, bản ghi đích, thời gian — đây là nguyên liệu để chatbot trả lời "tại sao hệ thống quyết định vậy".

### 2.4 Workflow Runtime
- `dxos.process.instance` (1 instance per bản ghi model đích) + `dxos.instance.node` (token đang ở node nào, trạng thái, người phụ trách, hạn chốt).
- Ánh xạ node → primitive Odoo native: user-task → `mail.activity` (hoặc approval record tự xây nếu cần đa mức duyệt); service-task → `ir.actions.server`; decision-task → evaluate DMN-lite; timer → `ir.cron._trigger(at=...)`; ai-task → gọi Dify qua `dxos_core`.
- Chuyển tiếp cạnh: điều kiện là domain Odoo hoặc output của DMN-lite; parallel gateway sinh nhiều token; join chờ đủ token.
- Human-in-the-loop mặc định: node có cờ `requires_approval` thì action chỉ chạy sau khi người được gán bấm duyệt trong chatter/widget.

## 3. Seam AI: Dify phân tích quy trình, đề xuất automation, user duyệt

Luồng đúng như deal đề bài:
1. Controller `dxos_bpmn` serialize `process.definition` JSON + decision tables + metadata model/field + số liệu thực thi (thời gian trung bình mỗi node, tỷ lệ tắc ở node, số lần decision log rẽ nhánh X) → POST sang Dify workflow `/v1/workflows/run`.
2. Dify workflow (LLM nodes + knowledge base best-practices) trả JSON danh sách đề xuất: node nào bỏ được/gộp được, chỗ nào gắn service-task/ai-task, rule DMN mới đề xuất, kèm **rationale** và số liệu dẫn chứng.
3. Odoo lưu vào `dxos.automation.proposal` (trạng thái pending/approved/rejected + ghi chú người duyệt) → wizard duyệt hiển thị diff mô hình trước/sau.
4. Khi duyệt: generator áp dụng lên revision mới của definition và/hoặc sinh bản ghi `base.automation`/`ir.actions.server`/activity plan tương ứng.
5. Chiều ngược lại miễn phí: Dify gọi vào Odoo qua route webhook của `base_automation` (`/web/hook/<uuid>`) hoặc controller read-only của `dxos_core` khi cần dữ liệu tươi.

Chính các record proposal + decision log này nuôi vai trò "tư vấn viên nghiệp vụ" của chatbot (tài liệu 05): mọi "tại sao" đều tra được nguồn có cấu trúc.

## 4. Giấy phép và PoF

- bpmn-js/dmn-js: MIT — nhúng vào addon LGPL-3 được, giữ nguyên notice; không sửa mã nguồn thư viện (PoF) — chỉ wrap bằng OWL component và asset bundle.
- Module `dxos_bpmn`, `dxos_dmn` do đội viết: chọn LGPL-3 (đồng bộ Odoo) hoặc MIT; ghi LICENSE từng tệp + bản toàn văn trong repo (PoF).
- Không nhúng Camunda Modeler (sản phẩm desktop, giấy phép riêng).

## 5. Phạm vi pha 1 (demo được)

Builder vẽ được 6 loại node core + lưu/publish revision; runtime chạy tuyến tính có gateway exclusive dùng DMN-lite; decision log; 1 luồng demo đầy đủ: vẽ quy trình duyệt nội dung blog → AI đề xuất bỏ bước trùng (có rationale) → duyệt → runtime áp dụng → chatbot giải thích được quyết định. Parallel gateway, timer, form builder động: pha 2.
