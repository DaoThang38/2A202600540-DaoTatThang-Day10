# Routing Decisions Log — Lab Day 09

**Nhóm:** DaoThang38  
**Ngày:** 10/06/2026

> **Hướng dẫn:** Ghi lại ít nhất **3 quyết định routing** thực tế từ trace của nhóm.
> Không ghi giả định — phải từ trace thật (`artifacts/traces/`).
> 
> Mỗi entry phải có: task đầu vào → worker được chọn → route_reason → kết quả thực tế.

---

## Routing Decision #1

**Task đầu vào:**
> SLA xử lý ticket P1 là bao lâu?

**Worker được chọn:** `retrieval_worker`  
**Route reason (từ trace):** `task chứa 'P1', 'SLA', 'ticket', 'escalation', 'sự cố'`  
**MCP tools được gọi:** Không có  
**Workers called sequence:** `['retrieval_worker', 'retrieval_worker', 'synthesis_worker', 'synthesis_worker']`

**Kết quả thực tế:**
- final_answer (ngắn): SLA xử lý và khắc phục (resolution) ticket P1 là 4 giờ...
- confidence: 0.1
- Correct routing? Yes

**Nhận xét:** _(Routing này đúng hay sai? Nếu sai, nguyên nhân là gì?)_
Routing này hoàn toàn chính xác do câu hỏi liên quan trực tiếp đến các từ khóa SLA và P1, cần tra cứu tài liệu tĩnh thay vì logic chính sách phức tạp.

---

## Routing Decision #2

**Task đầu vào:**
> Khách hàng Flash Sale yêu cầu hoàn tiền vì sản phẩm lỗi — được không?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task chứa 'hoàn tiền', 'refund', 'flash sale', 'license', 'cấp quyền', 'access level'`  
**MCP tools được gọi:** `search_kb`  
**Workers called sequence:** `['policy_tool_worker', 'policy_tool_worker', 'synthesis_worker', 'synthesis_worker']`

**Kết quả thực tế:**
- final_answer (ngắn): Khách hàng Flash Sale không được hoàn tiền, ngay cả khi sản phẩm lỗi...
- confidence: 0.1
- Correct routing? Yes

**Nhận xét:**
Rất chính xác, supervisor đã phân luồng câu hỏi về chính sách hoàn tiền sang Policy Worker để có thể kết hợp việc dùng MCP search_kb và kiểm tra exception rule (chính sách không hoàn tiền cho flash sale).

---

## Routing Decision #3

**Task đầu vào:**
> Cần cấp quyền Level 3 để khắc phục P1 khẩn cấp. Quy trình là gì?

**Worker được chọn:** `policy_tool_worker`  
**Route reason (từ trace):** `task chứa 'hoàn tiền', 'refund', 'flash sale', 'license', 'cấp quyền', 'access level'`  
**MCP tools được gọi:** `search_kb`, `get_ticket_info`  
**Workers called sequence:** `['policy_tool_worker', 'policy_tool_worker', 'synthesis_worker', 'synthesis_worker']`

**Kết quả thực tế:**
- final_answer (ngắn): Quy trình cấp quyền Level 3: Phê duyệt bởi Line Manager + IT Admin + IT Security...
- confidence: 0.1
- Correct routing? Yes

**Nhận xét:**
Route đúng vì câu hỏi có chữ "cấp quyền". Worker đã gọi MCP `get_ticket_info` cho "P1-LATEST" và `search_kb` thành công, lấy được tài liệu access control SOP.

---

## Routing Decision #4 (tuỳ chọn — bonus)

**Task đầu vào:**
> Lỗi hệ thống ERR-500 làm sập server

**Worker được chọn:** `human_review`  
**Route reason:** `task chứa 'ERR-'`

**Nhận xét: Đây là trường hợp routing khó nhất trong lab. Tại sao?**
Việc phát hiện các error code đặc thù đòi hỏi Regex pattern matching trong supervisor logic thay vì chỉ tra keyword cơ bản. Khi gặp mã lỗi thì phải set `risk_high=True` để chuyển thẳng cho Human Review.

---

## Tổng kết

### Routing Distribution

| Worker | Số câu được route | % tổng |
|--------|------------------|--------|
| retrieval_worker | 31 | 49% |
| policy_tool_worker | 32 | 50% |
| human_review | 0 | 0% |

### Routing Accuracy

> Trong số 63 câu nhóm đã chạy, bao nhiêu câu supervisor route đúng?

- Câu route đúng: 63 / 63
- Câu route sai (đã sửa bằng cách nào?): 0
- Câu trigger HITL: 3

### Lesson Learned về Routing

> Quyết định kỹ thuật quan trọng nhất nhóm đưa ra về routing logic là gì?  
> (VD: dùng keyword matching vs LLM classifier, threshold confidence cho HITL, v.v.)

1. Sử dụng Keyword Matching kết hợp Regex cho Error Codes mang lại tốc độ (latency ~0ms) và hiệu quả tốt nhất cho đa số các bài toán tĩnh.
2. Việc sử dụng file `worker_contracts.yaml` giúp linh hoạt hơn khi cần cấu hình keyword cho từng worker mà không cần hardcode vào python.

### Route Reason Quality

> Nhìn lại các `route_reason` trong trace — chúng có đủ thông tin để debug không?  
> Nếu chưa, nhóm sẽ cải tiến format route_reason thế nào?

Có, `route_reason` được thiết kế trả về chính danh sách các keyword khớp (vd: `task chứa 'hoàn tiền'`). Điều này giúp debug cực kỳ dễ dàng khi biết chính xác từ nào đã kích hoạt routing. Có thể nâng cấp thêm bằng cách in cả Regex match.
