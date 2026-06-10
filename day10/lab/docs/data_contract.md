# Data contract — Lab Day 10

> Bắt đầu từ `contracts/data_contract.yaml` — mở rộng và đồng bộ file này.

---

## 1. Nguồn dữ liệu (source map)

| Nguồn | Phương thức ingest | Failure mode chính | Metric / alert |
|-------|-------------------|-------------------|----------------|
| `policy_refund_v4` | Đọc file tĩnh từ CSV export | Sai cửa sổ hoàn tiền (14 ngày thay vì 7 ngày) | Cảnh báo `stale_refund_window > 0` (drop record) |
| `sla_p1_2026` | Đọc file tĩnh từ CSV export | Trùng lặp chunk (duplicate chunk_text) | Cảnh báo `duplicate_chunk_text > 0` (quarantine) |
| `it_helpdesk_faq` | Đọc file tĩnh từ CSV export | Lỗi format ngày tháng (không chuẩn ISO) | Cảnh báo `invalid_effective_date_format > 0` (drop) |
| `hr_leave_policy` | Đọc file tĩnh từ CSV export | Lỗi dữ liệu cũ (stale version 2025, 10 ngày phép) | Cảnh báo `stale_hr_policy_effective_date > 0` (drop/quarantine) |
| `access_control_sop`| Đọc file tĩnh từ CSV export | Bị sót khỏi ALLOWED_DOC_IDS ban đầu | Cảnh báo `unknown_doc_id` nếu sót nguồn mới (drop) |

---

## 2. Schema cleaned

| Cột | Kiểu | Bắt buộc | Ghi chú |
|-----|------|----------|---------|
| chunk_id | string | Có | Tạo ID duy nhất (uuid) từ nội dung để tránh duplicate |
| doc_id | string | Có | Phân loại nguồn tài liệu (Chỉ chấp nhận từ ALLOWED_DOC_IDS) |
| chunk_text | string | Có | Văn bản sau khi clean rác |
| effective_date | date | Có | Ngày hiệu lực (phải chuẩn định dạng YYYY-MM-DD) |
| exported_at | datetime | Có | Ngày xuất dữ liệu raw |

---

## 3. Quy tắc quarantine vs drop

> Record bị flag đi đâu? Ai approve merge lại?

- **Drop**: Dành cho các lỗi nghiêm trọng về cấu trúc (thiếu `chunk_id`, `chunk_text` null), lỗi ngày tháng sai chuẩn, hoặc các tài liệu đã cũ rích (version 2025). Hệ thống sẽ vứt bỏ hoàn toàn không lưu trữ để tiết kiệm dung lượng.
- **Quarantine**: Dành cho các record có nghi ngờ (VD: duplicate `chunk_text`, doc_id lạ). Dữ liệu này sẽ được lưu vào thư mục `artifacts/quarantine/` để Data Engineer hoặc QA review bằng tay. Nếu hợp lệ sẽ được merge lại vào đường ống sau.

---

## 4. Phiên bản & canonical

> Source of truth cho policy refund: file nào / version nào?

`policy_refund_v4` là phiên bản có hiệu lực. Các phiên bản cũ hơn (v1, v2, v3) hoặc có nội dung hoàn tiền 14 ngày (thay vì 7 ngày) sẽ bị chặn lại ở lớp `cleaning_rules.py` do vi phạm source of truth.
