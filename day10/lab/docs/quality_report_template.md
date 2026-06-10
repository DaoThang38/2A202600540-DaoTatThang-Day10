# Quality report — Lab Day 10 (nhóm)

**run_id:** pipeline_20260610  
**Ngày:** 10/06/2026

---

## 1. Tóm tắt số liệu

| Chỉ số | Trước | Sau | Ghi chú |
|--------|-------|-----|---------|
| raw_records | 10 | 10 | Tập input (gồm cả record bẩn) |
| cleaned_records | 10 | 4 | Chỉ giữ lại 4 record đúng chuẩn |
| quarantine_records | 0 | 6 | Các record bị lọc (sai policy, outdated) |
| Expectation halt? | N/A | Không | Pass toàn bộ điều kiện validate |

---

## 2. Before / after retrieval (bắt buộc)

> Đính kèm hoặc dẫn link tới `artifacts/eval/before_after_eval.csv` (hoặc 2 file before/after).

**Câu hỏi then chốt:** refund window (`q_refund_window`)  
**Trước:** Hệ thống tìm thấy thông báo hoàn tiền 14 ngày (bản nháp/sai chuẩn).  
**Sau:** Tìm thấy chính xác thông báo 7 ngày làm việc (từ `policy_refund_v4`).

**Merit (khuyến nghị):** versioning HR — `q_leave_version` (`contains_expected`, `hits_forbidden`, cột `top1_doc_expected`)

**Trước:** Lấy chính sách HR năm 2025 (quy định 10 ngày phép).  
**Sau:** Lấy chính xác bản mới nhất 2026 (quy định 12 ngày phép), do bản 2025 đã bị đẩy vào quarantine.

---

## 3. Freshness & monitor

> Kết quả `freshness_check` (PASS/WARN/FAIL) và giải thích SLA bạn chọn.

**Kết quả:** PASS.
**Giải thích SLA:** Chúng tôi chọn SLA `MAX_DAYS = 3`. Tức là data không được phép trễ hơn 3 ngày so với ngày hiện tại (hoặc ngày xuất bản quy định). Điều này hợp lý với một Knowledge Base IT thường xuyên thay đổi quy định nội bộ hàng tuần.

---

## 4. Corruption inject (Sprint 3)

> Mô tả cố ý làm hỏng dữ liệu kiểu gì (duplicate / stale / sai format) và cách phát hiện.

Chúng tôi đã kiểm thử với file `policy_export_dirty.csv`, có chứa các lỗi cố ý:
1. Có 1 dòng rác với doc_id rỗng. -> Phát hiện và drop ở khâu clean doc_id.
2. Có 1 dòng hoàn tiền 14 ngày. -> Lọc dựa trên Regex.
3. Có 1 bản ghi chính sách HR 2025 (stale data). -> Lọc dựa trên logic check năm trong text.
4. Lỗi định dạng ngày (dd-mm-yyyy thay vì yyyy-mm-dd). -> Pandas parser bắt lỗi và gán NaT (Not a Time), sau đó drop các dòng không có effective_date hợp lệ.

---

## 5. Hạn chế & việc chưa làm

- Chưa triển khai Data Quality Dashboard trực quan để hiển thị báo cáo dễ nhìn hơn cho Stakeholder.
- Hiện tại quarantine chỉ ghi file CSV, lý tưởng nhất là bắn Notification Slack cho Admin vào kiểm duyệt định kỳ.
