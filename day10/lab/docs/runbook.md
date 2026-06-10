# Runbook — Lab Day 10 (incident tối giản)

---

## Symptom

> User / agent thấy gì? (VD: trả lời “14 ngày” thay vì 7 ngày)

- **Agent LLM** trả lời các câu hỏi liên quan đến chính sách với nội dung lỗi thời hoặc sai lệch (Ví dụ: "Được hoàn tiền trong 14 ngày" thay vì 7 ngày; "Nhân viên dưới 3 năm được nghỉ 10 ngày phép" thay vì 12 ngày).
- LLM từ chối trả lời vì không truy xuất được document nào.

---

## Detection

> Metric nào báo? (freshness, expectation fail, eval `hits_forbidden`)

- **Freshness Check:** Cảnh báo báo đỏ (FAIL) khi Data pipeline phát hiện dữ liệu export có ngày `exported_at` trễ hơn SLA quy định (vd: 3 ngày).
- **Evaluation `hits_forbidden`:** Script `eval_retrieval.py` báo cáo tỷ lệ `hits_forbidden` tăng cao (ví dụ LLM lấy nhầm `hr_policy_2025` thay vì bản 2026).
- Cảnh báo log `duplicate_chunk_text > 0` và số lượng record lọt vào thư mục `quarantine` tăng vọt bất thường.

---

## Diagnosis

| Bước | Việc làm | Kết quả mong đợi |
|------|----------|------------------|
| 1 | Kiểm tra `artifacts/manifests/*.json` | Xác định xem ngày chạy pipeline gần nhất là bao giờ, số lượng input record có khớp với DB hay không, có record nào bị chặn không. |
| 2 | Mở `artifacts/quarantine/*.csv` | Xem các record bị chặn thuộc lỗi gì (lỗi date, lỗi trùng, lỗi policy rác). Nếu đó là file policy mới cần thiết, nó báo hiệu rule cleaning đang quá khắt khe. |
| 3 | Chạy `python eval_retrieval.py` | Kiểm tra xem ChromaDB đã nhúng đúng các văn bản mới nhất chưa hay vẫn lôi ra rác. Cột top1_doc_matches phải báo True. |

---

## Mitigation

> Rerun pipeline, rollback embed, tạm banner “data stale”, …

1. Tạm dừng kết nối Agent tới ChromaDB (hoặc gắn cờ cảnh báo trên UI "Dữ liệu có thể đang được cập nhật").
2. Update lại regex và luật trong `cleaning_rules.py` nếu format dữ liệu nguồn bị thay đổi mà không báo trước.
3. Chạy lại `python main.py` để wipe và rebuild ChromaDB với bộ rules chuẩn.

---

## Prevention

> Thêm expectation, alert, owner — nối sang Day 11 nếu có guardrail.

- Cập nhật chặt chẽ file `contracts/data_contract.yaml` để làm source of truth về định dạng Schema cho Data Team.
- Thiết lập cảnh báo Slack/Email tự động khi số lượng record vào quarantine > 5% tổng số file chạy.
