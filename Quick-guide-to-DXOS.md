# Giới thiệu mô hình DX-OS và chủ đề cuộc thi Phần mềm nguồn mở OLP 2026

## 1. Bài toán Chuyển đổi số và sự ra đời của kiến trúc DX-OS

Chuyển đổi số (CĐS) được tài liệu xác định là yêu cầu bắt buộc đối với tổ chức trong nền kinh tế số. Tuy nhiên, nhiều chương trình CĐS vẫn mắc vào “ảo tưởng công nghệ”: đầu tư nhiều phần mềm nhưng nhân sự vẫn làm việc thủ công, dữ liệu bị phân tán trong các “ốc đảo thông tin”.

Giáo trình **“Xây dựng Hệ điều hành Doanh nghiệp số: Từ Tư duy đến Hành động (DX-OS in Action)”** đưa ra một phương pháp luận trong đó chuyển đổi số về bản chất là quá trình chuyển giao quyền kiểm soát từ thao tác thủ công của con người sang các thuật toán tự động.

Phương pháp được mô hình hóa bằng cấu trúc **H-P-D-I**, gồm 4 không gian chức năng.

### 1.1. Cấu trúc 4 không gian của Hệ điều hành DX-OS

#### [H] Không gian Nhân sự — Kiến tạo môi trường làm việc số tích hợp

Đây là phân tầng vận hành cơ sở của hệ thống. Mục tiêu là tạo ra môi trường làm việc số khép kín, giảm sự phụ thuộc vào trí nhớ, thói quen và thao tác thủ công của nhân sự.

Các thành phần được đề cập:

- Quản trị định danh tập trung (**SSO**).
- Tiêu chuẩn hóa lưu trữ dữ liệu tệp tin vật lý theo phương pháp **P.A.R.A**.
- Cổng thông tin nội bộ để kiểm soát độ chính xác của luồng thông tin ngay từ đầu vào.

#### [P] Không gian Quy trình — Tự động hóa luồng công việc

Không gian [P] tiếp nhận quyền điều khiển từ con người thông qua các cấu trúc thuật toán.

Chức năng cốt lõi:

- Tự động hóa quy trình dựa trên **kiến trúc hướng sự kiện**.
- Xử lý các bước chuyển giao thông tin giữa các bộ phận mà không cần thao tác thủ công.
- Áp dụng các ràng buộc kỹ thuật **Poka-yoke** để hạn chế thao tác không hợp lệ.
- Bảo đảm tính toàn vẹn của dữ liệu ngay từ điểm chạm đầu vào.

#### [D] Không gian Dữ liệu — Ra quyết định dựa trên sự thật

Khi không gian [P] vận hành ổn định, hệ thống tự động tạo ra các tập dữ liệu phẳng có cấu trúc.

Không gian [D] chịu trách nhiệm:

- Thu thập dữ liệu.
- Làm sạch dữ liệu.
- Đồng bộ hóa dữ liệu.
- Hình thành **nguồn cơ sở dữ liệu sự thật duy nhất**.
- Triệt tiêu hiện tượng “ốc đảo thông tin”.
- Cung cấp **Dashboard thời gian thực** để cấp quản lý giám sát và điều hành dựa trên số liệu định lượng.

#### [I] Không gian Trí tuệ Nhân tạo — Tiến đến doanh nghiệp tự hành

Đây là trạng thái kiến trúc cao nhất, hướng tới mô hình **doanh nghiệp AI-Native**.

AI được tích hợp trực tiếp vào hệ thống dưới dạng các **tác tử tự hành (Agentic AI)**.

Hệ thống có khả năng:

1. Tự phân tích dữ liệu từ không gian [D].
2. Tự nhận diện sự kiện từ không gian [P].
3. Tự động thực thi các lệnh hành động đã được cấu hình.
4. Không yêu cầu tín hiệu điều khiển hoặc thao tác nhấp chuột từ con người.

### 1.2. Sự tiến hóa tuyến tính và nguyên lý Human-in-the-loop

Tài liệu nhấn mạnh rằng quá trình nâng cấp hệ thống phải diễn ra theo trình tự tuyến tính:

**[H] → [P] → [D] → [I]**

Không thể đạt được năng lực tự động hóa ở [I] nếu chưa:

- Chuẩn hóa dữ liệu tại [D].
- Thiết lập các ràng buộc kỹ thuật tại [P].

Việc đưa AI vào một quy trình chưa chuẩn hóa có thể dẫn đến:

- Lỗi logic dữ liệu đầu vào.
- Hiện tượng **Garbage In, Garbage Out (GIGO)**.
- Ảo giác dữ liệu.

Theo nguyên lý **Human-in-the-loop**, khi năng lực xử lý của máy móc tại [P], [D], [I] tăng lên thì tỷ lệ thao tác thủ công của con người ([H]) giảm xuống, từ mức 100% xuống khoảng 10–20%.

Vai trò của nhân sự chuyển dần sang:

- Thiết kế luồng thuật toán.
- Kiểm soát chất lượng hệ thống.
- Giám sát các rào chắn đạo đức.
- Phê duyệt các trường hợp ngoại lệ.

---

## 2. Chủ đề Cuộc thi Phần mềm Nguồn mở OLP 2026: Xây dựng DX-Lab

Hội Tin học Việt Nam và Câu lạc bộ VFOSSA công bố chủ đề cuộc thi OLP Phần mềm Nguồn mở 2026 là:

> **Xây dựng Hệ điều hành Doanh nghiệp số (DX-OS) dựa trên kiến trúc Open-Core.**

Mục tiêu là hướng dẫn sinh viên chuyên và không chuyên CNTT sử dụng các nền tảng mã nguồn mở để thiết kế và xây dựng một **Trạm thực hành số (DX-Lab)**.

DX-Lab phải mô phỏng 4 không gian kiến trúc **H-P-D-I** và giải quyết các bài toán vận hành của doanh nghiệp.

### 2.1. Khai thác hệ sinh thái công nghệ OLP các năm trước

Các đội thi được định hướng kết hợp các nền tảng mã nguồn mở đã được khai thác trong các kỳ OLP trước để xây dựng một hệ thống vận hành hoàn chỉnh.

#### OLP 2024 — Low-code/No-code

Khai thác các nền tảng phát triển dùng ít mã nguồn (**LCDP**) để:

- Xây dựng biểu mẫu nhập liệu.
- Thiết lập cơ sở dữ liệu quan hệ.
- Tạo rào chắn kỹ thuật tại không gian [P].

#### OLP 2025 — Dữ liệu mở liên kết

Tận dụng các mô hình **Linked Open Data (LOD)** để:

- Chuẩn hóa cấu trúc siêu dữ liệu.
- Hình thành nguồn sự thật duy nhất cho không gian [D].

#### OLP 2023 — Mô hình Ngôn ngữ Lớn

Triển khai:

- **LLM**.
- **RAG**.
- Tác tử thông minh.

Mục tiêu là tự động hóa quy trình ra quyết định tại không gian [I].

### 2.2. Quy hoạch công cụ theo bản đồ công nghệ DX-OS

Các đội thi cần chủ động nghiên cứu và lựa chọn các giải pháp phần mềm lõi mở (**Open-Core**) để hình thành hệ sinh thái DX-Lab.

| Không gian | Nhóm công cụ cần nghiên cứu |
|---|---|
| **[H] Nhân sự** | SSO, Cloud Storage, Wiki/CMS, hệ thống truyền thông tức thời |
| **[P] Quy trình** | Low-code, iPaaS, Workflow Automation, API integration |
| **[D] Dữ liệu** | CSDL quan hệ/phi quan hệ, BI nguồn mở, Dashboard, trực quan hóa dữ liệu |
| **[I] AI** | Machine Learning, Vector Database, LLM Frameworks, RAG, Agentic AI |

### 2.3. Phạm vi khai thác DX-Lab

DX-Lab phục vụ 3 nhóm tác nhân chính:

1. **Ban lãnh đạo, quản lý SME và cơ quan Nhà nước**
   - Chẩn đoán thực trạng tổ chức.
   - Đo lường các hạn chế vận hành.
   - Tối ưu hóa ROI đầu tư hạ tầng công nghệ.

2. **Chuyên gia công nghệ và tư vấn viên**
   - Đóng gói và chia sẻ tri thức chuyên môn.
   - Kết nối đối tác kỹ thuật.
   - Xây dựng năng lực tham gia mạng lưới tư vấn viên chuyển đổi số cấp quốc gia.

3. **Sinh viên và giảng viên khối ngành kỹ thuật, kinh tế số**
   - Tiếp cận môi trường thực nghiệm giả lập.
   - Thực hành trên cơ sở dữ liệu thực tế của doanh nghiệp.
   - Chuyển hóa lý thuyết thành năng lực ứng dụng thực chiến.

---

## 3. Chuẩn bị cho cuộc thi PMNM - OLP 2026

Cuộc thi Phần mềm nguồn mở OLP 2026 dành cho sinh viên chuyên hoặc không chuyên CNTT trên toàn quốc.

- Mỗi đội tối đa **3 thí sinh**.
- Đội thi có sự dẫn dắt của **1 giảng viên**.
- Tổng điểm: **100 điểm**.
  - **50 điểm**: Tiêu chí loại trừ (**PoF - Point of Failure**).
  - **50 điểm**: Hackathon và trình diễn (**Showcase**).

### 3.1. Tiêu chí loại trừ (PoF - Point of Failure)

#### 1. Cấp phép hợp lệ

Sản phẩm phải:

- Sử dụng giấy phép **OSI-approved**.
- Có thông tin giấy phép rõ ràng trong từng tệp mã.
- Có bản sao toàn văn giấy phép.

Vi phạm có thể bị trừ điểm nặng.

#### 2. Hệ thống quản lý mã nguồn

Bắt buộc:

- Sử dụng hệ thống quản lý mã nguồn công khai trên Internet.
- Có web viewer.
- Cho phép truy cập mở.

#### 3. Cài đặt từ mã nguồn (Building From Source)

Sản phẩm phải cho phép:

- Biên dịch từ mã nguồn.
- Cài đặt từ mã nguồn.

Cần có hướng dẫn rõ ràng.

Tài liệu khuyến khích sử dụng **container hóa**, chẳng hạn như Docker, để đóng gói hệ thống DX-Lab.

#### 4. Quản lý thư viện và tài liệu

Yêu cầu:

- Không chỉnh sửa mã nguồn của các thư viện đính kèm.
- Có **README** rõ ràng.
- Có **Changelog**.
- Có hệ thống ghi nhận lỗi (**Bug tracker**).

### 3.2. Kỹ năng giải quyết vấn đề và trình diễn sản phẩm

Phần thi chung kết gồm hackathon và showcase, tập trung vào 3 khía cạnh:

#### Tư duy kiến trúc

Đội thi cần:

- Lắp ghép các phần mềm mã nguồn mở một cách logic.
- Tạo ra giải pháp kỹ thuật có tính nguyên gốc.
- Giải quyết đúng bài toán nghiệp vụ DX-OS.

#### Mức độ hoàn thiện và thân thiện

DX-Lab cần:

- Chạy thực tế ổn định, mượt mà.
- Có tiện ích thân thiện với người dùng cuối.
- Phục vụ được cả nhân viên và quản lý.

#### Khả năng thu hút cộng đồng

Đội thi cần thể hiện:

- Tầm nhìn phát triển bền vững.
- Khả năng phát triển sản phẩm trong cộng đồng nguồn mở.
- Phong cách trình diễn thuyết phục.

---

## 4. Tóm tắt kiến trúc DX-OS

```text
                 DX-OS
                   │
          ┌────────┴────────┐
          │     H-P-D-I     │
          └────────┬────────┘
                   │
       ┌───────────┼───────────┐
       │           │           │
      [H]         [P]         [D]         [I]
   Nhân sự      Quy trình    Dữ liệu       AI
       │           │           │           │
      SSO       Workflow       BI        Agentic AI
   Storage       iPaaS       Database       RAG
    Wiki       Low-code    Dashboard      Vector DB
       │           │           │           │
       └───────────┴───────────┴───────────┘
                       │
                    DX-Lab
                       │
             Doanh nghiệp tự hành
```

### Nguyên tắc cốt lõi

> **Chuẩn hóa [H] → Tự động hóa [P] → Chuẩn hóa dữ liệu [D] → Tự hành bằng AI [I]**

AI không phải điểm bắt đầu của chuyển đổi số. Theo tài liệu, AI chỉ phát huy hiệu quả khi quy trình và dữ liệu phía trước đã được chuẩn hóa.

---

## 5. Checklist chuẩn bị OLP PMNM 2026

### Kiến trúc

- [ ] Hiểu rõ H-P-D-I.
- [ ] Xác định bài toán nghiệp vụ doanh nghiệp.
- [ ] Thiết kế luồng dữ liệu xuyên suốt H → P → D → I.
- [ ] Xác định vai trò Human-in-the-loop.

### Open Source

- [ ] Kiểm tra giấy phép OSI-approved.
- [ ] Công khai repository.
- [ ] Có web viewer.
- [ ] Có thể build từ source.
- [ ] Có README.
- [ ] Có Changelog.
- [ ] Có Bug tracker.
- [ ] Không sửa mã nguồn thư viện bên thứ ba.

### DX-Lab

- [ ] H: SSO + Storage + Wiki/CMS + Communication.
- [ ] P: Low-code + iPaaS + Workflow + API.
- [ ] D: Database + BI + Dashboard.
- [ ] I: LLM + RAG + Vector DB + Agentic AI.
- [ ] Đóng gói bằng container khi phù hợp.
- [ ] Có demo thực tế.
- [ ] Có UX thân thiện.
- [ ] Có câu chuyện phát triển cộng đồng.

---

## 6. Tài liệu tham khảo

Tài liệu gốc giới thiệu giáo trình:

**Xây dựng Hệ điều hành Doanh nghiệp số (DX-OS)**

https://opendigitransform.gitbook.io/dx-os
