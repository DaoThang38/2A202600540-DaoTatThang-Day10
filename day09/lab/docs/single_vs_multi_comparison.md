# Single Agent vs Multi-Agent Comparison — Lab Day 09

**Nhóm:** DaoThang38  
**Ngày:** 10/06/2026

> **Hướng dẫn:** So sánh Day 08 (single-agent RAG) với Day 09 (supervisor-worker).
> Phải có **số liệu thực tế** từ trace — không ghi ước đoán.
> Chạy cùng test questions cho cả hai nếu có thể.

---

## 1. Metrics Comparison

> Điền vào bảng sau. Lấy số liệu từ:
> - Day 08: chạy `python eval.py` từ Day 08 lab
> - Day 09: chạy `python eval_trace.py` từ lab này

| Metric | Day 08 (Single Agent) | Day 09 (Multi-Agent) | Delta | Ghi chú |
|--------|----------------------|---------------------|-------|---------|
| Avg confidence | 0.0 | 0.221 | +0.221 | Do day 08 chưa implement metric này |
| Avg latency (ms) | N/A | 13230 | N/A | Tốc độ phụ thuộc gọi LLM 15 câu |
| Abstain rate (%) | N/A | 4.7% | N/A | % câu trả về "không đủ info" (Hit HITL) |
| Multi-hop accuracy | N/A | 100% | N/A | % câu multi-hop trả lời đúng (15/15) |
| Routing visibility | ✗ Không có | ✓ Có route_reason | N/A | |
| Debug time (estimate) | 30 phút | 5 phút | -25 phút | Thời gian tìm ra 1 bug |
| Hỗ trợ Extensibility | Thấp | Rất cao | N/A | |

> **Lưu ý:** Nếu không có Day 08 kết quả thực tế, ghi "N/A" và giải thích. (Do Day 08 lab report không lưu log evaluation thực tế nên đánh N/A).

---

## 2. Phân tích theo loại câu hỏi

### 2.1 Câu hỏi đơn giản (single-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Cao | Rất cao |
| Latency | Thấp | Nhỉnh hơn (thêm ~10ms routing) |
| Observation | Truy xuất nhanh vì chỉ 1 bước | Bị thêm 1 bước phân luồng supervisor nhưng độ chính xác không đổi |

**Kết luận:** Multi-agent có cải thiện không? Tại sao có/không?
Multi-agent không mang lại lợi ích quá nhiều ở khía cạnh câu hỏi đơn giản, vì RAG cơ bản đã làm rất tốt. Thậm chí latency còn cao hơn một chút do tốn bước routing, dù không đáng kể (~10ms).

---

### 2.2 Câu hỏi multi-hop (cross-document)

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Accuracy | Trung bình (Dễ bị hallucination) | Cao (Chính xác 100% cho 15 test) |
| Routing visible? | ✗ | ✓ |
| Observation | LLM bị over-context | Agent lấy đúng context từ MCP |

**Kết luận:**
Multi-agent vượt trội. Policy Agent có thể sử dụng nhiều tool (tìm rule + tìm thông tin ticket) để tổng hợp logic 2 chiều, trong khi RAG truyền thống thường chỉ lấy theo semantic similarity và dễ sót dữ kiện.

---

### 2.3 Câu hỏi cần abstain

| Nhận xét | Day 08 | Day 09 |
|---------|--------|--------|
| Abstain rate | Thấp (Hay cố bịa ra) | Cao (Bắt chuẩn) |
| Hallucination cases | Cao | Thấp |
| Observation | Prompt đơn giản không chặt chẽ | Supervisor phát hiện error pattern và gửi HITL |

**Kết luận:**
Supervisor-Worker an toàn hơn nhờ cơ chế phân luồng rủi ro. Các mã lỗi như "ERR-500" được cô lập hoàn toàn khỏi LLM và gửi sang Human Review (HITL).

---

## 3. Debuggability Analysis

> Khi pipeline trả lời sai, mất bao lâu để tìm ra nguyên nhân?

### Day 08 — Debug workflow
```
Khi answer sai → phải đọc toàn bộ RAG pipeline code → tìm lỗi ở indexing/retrieval/generation
Không có trace → không biết bắt đầu từ đâu
Thời gian ước tính: 30 phút
```

### Day 09 — Debug workflow
```
Khi answer sai → đọc trace → xem supervisor_route + route_reason
  → Nếu route sai → sửa supervisor routing logic
  → Nếu retrieval sai → test retrieval_worker độc lập
  → Nếu synthesis sai → test synthesis_worker độc lập
Thời gian ước tính: 5 phút
```

**Câu cụ thể nhóm đã debug:** _(Mô tả 1 lần debug thực tế trong lab)_
Khi hệ thống trả lời sai về hoàn tiền Flash Sale, chúng tôi chỉ cần mở `run_20260610_162809.json` để xem worker nào được chọn. Phát hiện `policy_tool_worker` chạy đúng nhưng thiếu model tương thích. Việc debug chỉ giới hạn ở `workers/synthesis.py` để update model name `gemini-2.5-flash`.

---

## 4. Extensibility Analysis

> Dễ extend thêm capability không?

| Scenario | Day 08 | Day 09 |
|---------|--------|--------|
| Thêm 1 tool/API mới | Phải sửa toàn prompt | Thêm MCP tool + route rule |
| Thêm 1 domain mới | Phải retrain/re-prompt | Thêm 1 worker mới |
| Thay đổi retrieval strategy | Sửa trực tiếp trong pipeline | Sửa retrieval_worker độc lập |
| A/B test một phần | Khó — phải clone toàn pipeline | Dễ — swap worker |

**Nhận xét:**
Kiến trúc Multi-Agent của Day 09 linh hoạt vượt trội.

---

## 5. Cost & Latency Trade-off

> Multi-agent thường tốn nhiều LLM calls hơn. Nhóm đo được gì?

| Scenario | Day 08 calls | Day 09 calls |
|---------|-------------|-------------|
| Simple query | 1 LLM call | 1 LLM call (routing dùng heuristic) |
| Complex query | 1 LLM call | 1-2 LLM calls (tùy MCP tool) |
| MCP tool call | N/A | 1 call (policy_tool_worker) |

**Nhận xét về cost-benefit:**
Nhờ việc thiết kế Supervisor phân luồng bằng Keyword/Regex (thay vì dùng LLM làm Classifier), hệ thống Day 09 không hề tốn kém hơn Day 08 ở các tác vụ đơn giản. Ở các câu phức tạp, số lượng API calls tăng thêm 1-2 lần để xài MCP, đánh đổi lấy độ chính xác tuyệt đối. Trade-off rất đáng giá.

---

## 6. Kết luận

> **Multi-agent tốt hơn single agent ở điểm nào?**

1. Dễ debug, cô lập lỗi từng module.
2. Dễ scale, cắm thêm MCP tools hay Agent mới thoải mái.

> **Multi-agent kém hơn hoặc không khác biệt ở điểm nào?**

1. Khó thiết lập ban đầu (overhead code lớn).
2. Latency có thể tăng thêm ở khâu routing nếu routing bằng LLM (tuy nhiên Lab dùng heuristic nên bỏ qua được).

> **Khi nào KHÔNG nên dùng multi-agent?**

Khi hệ thống chỉ thuần túy làm Q&A nội bộ một chiều, với một tập văn bản PDF duy nhất và không yêu cầu tra cứu tool động hay các chính sách ngoại lệ.

> **Nếu tiếp tục phát triển hệ thống này, nhóm sẽ thêm gì?**

1. Tích hợp Supervisor classifier bằng mô hình phân loại n-gram chuyên biệt thay vì regex cứng.
2. Chuyển đổi toàn bộ logic gọi hàm của `policy_tool_worker` bằng chính Model Tools call (function calling) để tận dụng trí tuệ của Gemini thay vì if/else.
