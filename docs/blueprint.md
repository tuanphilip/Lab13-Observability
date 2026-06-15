# Day 13 Observability Lab Report

> **Instruction**: Fill in all sections below. This report is designed to be parsed by an automated grading assistant. Ensure all tags (e.g., `[GROUP_NAME]`) are preserved.

## 1. Team Metadata
- Họ tên: Vũ Tuấn Phương
- MSSV: 2A202600772
- [REPO_URL]: https://github.com/tuanphilip/Lab13-Observability
- Role: Logging, PII, Tracing, SLOs & Alerts, Dashboard, Demo, Report

---

## 2. Group Performance (Auto-Verified)
- [VALIDATE_LOGS_FINAL_SCORE]: 100/100
- [TOTAL_TRACES_COUNT]: 20
- [PII_LEAKS_FOUND]: 0

---

## 3. Technical Evidence (Group)

### 3.1 Logging & Tracing
- [EVIDENCE_CORRELATION_ID_SCREENSHOT]: 
![alt text](images/dashboard_main.png)
- [EVIDENCE_PII_REDACTION_SCREENSHOT]:
![alt text](images/dashboard_main.png)
- [EVIDENCE_TRACE_WATERFALL_SCREENSHOT]: docs/images/trace_waterfall.png
- [TRACE_WATERFALL_EXPLANATION]: RAG retrieval step was slow because it simulated a 2.5-second time sleep.

### 3.2 Dashboard & SLOs
- [DASHBOARD_6_PANELS_SCREENSHOT]: ![alt text](images/dashboard_main.png)docs/images/dashboard_main.png
- [SLO_TABLE]:
| SLI | Target | Window | Current Value |
|---|---:|---|---:|
| Latency P95 | < 3000ms | 28d | 150ms |
| Error Rate | < 2% | 28d | 0% |
| Cost Budget | < $2.5/day | 1d | $0.0213 |

### 3.3 Alerts & Runbook
- [ALERT_RULES_SCREENSHOT]: docs/images/dashboard_main.png
- [SAMPLE_RUNBOOK_LINK]: docs/alerts.md#L1

---

## 4. Incident Response (Group)
- [SCENARIO_NAME]: rag_slow
- [SYMPTOMS_OBSERVED]: P95 latency spiked from ~150ms to 2651ms.
- [ROOT_CAUSE_PROVED_BY]: Log record showing latency_ms=2651 due to sleep injected in app/mock_rag.py when rag_slow state is enabled.
- [FIX_ACTION]: Optimize vector database indexes or toggle the incident off.
- [PREVENTIVE_MEASURE]: Add circuit breaker and fallback response when RAG latency exceeds threshold.

---

## 5. Individual Contributions & Evidence

### Vũ Tuấn Phương (2A202600772)
- [TASKS_COMPLETED]: 
  - Triển khai middleware gán và truyền nhận Correlation ID (`x-request-id` và `x-response-time-ms`) qua FastAPI Middleware.
  - Làm giàu log tự động trong API endpoint `/chat` sử dụng structlog contextvars.
  - Xây dựng Regex và đăng ký bộ xử lý PII Scrubber để lọc các thông tin cá nhân khỏi log.
  - Tích hợp Langfuse Tracing cho model generate và retrieve.
  - Xây dựng dashboard HTML 6 panels tương tác thời gian thực tại endpoint `/dashboard` tích hợp điều khiển incident và trigger load test.
  - Cấu hình SLOs (`slo.yaml`), alert rules (`alert_rules.yaml`) và viết Runbook hướng dẫn ứng cứu sự cố (`docs/alerts.md`).
- [EVIDENCE_LINK]: (Hãy điền link commit/PR trên github của bạn ở đây)

---

## 6. Bonus Items (Optional)
- [BONUS_COST_OPTIMIZATION]: (Description + Evidence)
- [BONUS_AUDIT_LOGS]: (Description + Evidence)
- [BONUS_CUSTOM_METRIC]: (Description + Evidence)
