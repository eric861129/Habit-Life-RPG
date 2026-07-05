# 第 9 章導覽：維運合規

對應書稿：第 9 章「永續經營」  
Git tag：`ch09-ops`  
本章定位：補齊產品上線後的 Runbook、監控、告警與隱私合規文件。

## 本章交付物

- `docs/ops/runbook.md`
- `docs/ops/monitoring-checklist.md`
- `docs/ops/alerting-spec.md`
- `docs/ops/privacy-policy-draft.md`
- `docs/ops/data-minimization-checklist.md`

## 驗證方式

```bash
python -m pytest -q
cd frontend
npm run build
```

## 本章完成檢查

- [x] Runbook 已建立。
- [x] Azure Monitor 監控清單已建立。
- [x] HTTP 5xx 與可用性告警規格已建立。
- [x] 隱私權政策草案已建立。
- [x] 資料最小化清單已建立。
