# 第二輪：文件驅動的Habit優先級變更

## 編輯需求

> 使用者的今日習慣變多後，希望先看見最重要的項目。請加入高、中、低優先級，並讓清單依優先級排序。

## 施工順序

1. 更新PRD、使用者故事、驗收標準、資料庫綱要、API契約、OpenAPI與UI Spec。
2. 新增後端與前端測試，確認因尚未實作 `priority` 而失敗。
3. 新增migration、模型、schema、排序與前端欄位。
4. 執行指定測試、完整測試、lint、OpenAPI檢查與前端build。
5. 記錄提交、tag、已知限制與交接方式。

## 文件影響範圍

| 文件 | 這次決策 |
| --- | --- |
| `docs/PRD.md` | 優先級納入MVP規則 |
| `docs/user-stories.md` | 新增HABIT-05 |
| `docs/acceptance-criteria.md` | 新增AC-PRIORITY-01～05 |
| `docs/database-schema.md` | `habits.priority`，預設 `medium` |
| `docs/api-contract.md` | 欄位、錯誤與排序契約 |
| `docs/openapi.yaml` | Create、Update、Read schema |
| `docs/ui-spec.md` | 表單選項、清單標籤與閱讀順序 |

## Red證據

- 後端：`KeyError: 'priority'`，API回應與migration都尚未提供欄位。
- 前端：`Unable to find a label with the text of: 優先級`，表單尚未提供選項。

以上失敗都直接對應尚未實作的新需求，不是套件、路徑或環境錯誤。
