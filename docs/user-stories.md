# Habit Life RPG User Stories

版本：Chapter 3 Blueprint  
狀態：MVP 驗收標準  
對應書稿：第 3.2 節「使用者故事與驗收標準」

## 1. 文件目的

本文件把 `docs/PRD.md` 中的產品願景拆成可驗收的開發單位。第三章先聚焦在最重要的主循環：使用者完成 habit 後，透過 API 打卡並取得 RPG 數值回饋。

後續第 5 章實作後端、第 6 章撰寫 Pytest 時，應優先回到本文件確認「做到什麼程度才算完成」。

## 2. 共同前提

- 使用者已經有帳號與角色狀態。
- 使用者已經登入，API 能取得目前使用者身分。
- 系統中已存在至少一筆屬於該使用者的 habit。
- MVP 統一使用 `habit` / `habits` / `habit_id` 命名。
- 核心 API 為 `POST /api/v1/habits/{habit_id}/checkin`。

## 3. Story 1：基礎 habit 打卡 API

**身為** 冒險者，  
**我想要** 在完成一個 habit 後送出打卡請求，  
**以便於** 系統記錄我的努力，並回饋經驗值、金幣與角色成長。

### 3.1 驗收標準

#### AC 1：API 路徑

Given 使用者已登入  
When 前端送出 habit 打卡請求  
Then 後端必須提供以下 API：

```http
POST /api/v1/habits/{habit_id}/checkin
```

#### AC 2：成功打卡

Given 使用者已登入，且該 habit 屬於目前使用者  
And 該 habit 今天尚未打卡  
When 使用者呼叫 `POST /api/v1/habits/{habit_id}/checkin`  
Then 後端回傳 `200 OK`  
And 回傳 JSON 必須包含更新後的角色狀態。

最低回傳欄位：

```json
{
  "habit_id": 1,
  "checked_in": true,
  "current_exp": 120,
  "current_gold": 35,
  "current_level": 2,
  "leveled_up": false
}
```

#### AC 3：同日不可重複打卡

Given 使用者已登入，且該 habit 今天已完成打卡  
When 使用者再次呼叫 `POST /api/v1/habits/{habit_id}/checkin`  
Then 後端回傳 `400 Bad Request`  
And 回傳 JSON 必須包含可讀錯誤訊息。

範例：

```json
{
  "detail": "Habit already checked in today."
}
```

#### AC 4：不可打卡他人的 habit

Given 使用者已登入  
And `habit_id` 對應的 habit 不屬於目前使用者  
When 使用者呼叫 `POST /api/v1/habits/{habit_id}/checkin`  
Then 後端回傳 `403 Forbidden`  
And 不得更新任何角色數值。

範例：

```json
{
  "detail": "You do not have permission to check in this habit."
}
```

#### AC 5：不存在的 habit

Given 使用者已登入  
And `habit_id` 不存在  
When 使用者呼叫 `POST /api/v1/habits/{habit_id}/checkin`  
Then 後端回傳 `404 Not Found`  
And 不得更新任何角色數值。

範例：

```json
{
  "detail": "Habit not found."
}
```

#### AC 6：未登入不可打卡

Given 使用者未登入或 token 無效  
When 呼叫 `POST /api/v1/habits/{habit_id}/checkin`  
Then 後端回傳 `401 Unauthorized`  
And 不得更新任何 habit 或角色狀態。

## 4. Story 2：前端呈現打卡結果

**身為** 冒險者，  
**我想要** 在打卡後立即看到角色狀態更新，  
**以便於** 感受到 habit 轉換成 RPG 成長的回饋。

### 4.1 驗收標準

#### AC 1：打卡成功後更新畫面

Given 使用者在首頁看到 habit 清單  
When 使用者對某個 habit 完成打卡，且 API 回傳 `200 OK`  
Then 前端應更新以下資訊：

- 角色目前經驗值。
- 角色目前金幣。
- 角色目前等級。
- 該 habit 的今日打卡狀態。

#### AC 2：升級時顯示慶祝狀態

Given 使用者打卡後達到升級門檻  
When API 回傳 `leveled_up: true`  
Then 前端應顯示升級提示或慶祝狀態  
And 使用者可以回到首頁繼續操作。

#### AC 3：打卡失敗時顯示錯誤

Given 使用者打卡失敗  
When API 回傳 `400`、`401`、`403` 或 `404`  
Then 前端應顯示錯誤訊息  
And 不應把該 habit 標示為已打卡成功。

## 5. 測試提示

第 6 章撰寫測試時，至少應包含：

- 成功打卡會更新 `current_exp`。
- 成功打卡會更新 `current_gold`。
- 成功打卡可能讓 `current_level` 上升。
- 同日重複打卡回傳 `400 Bad Request`。
- 打卡他人的 habit 回傳 `403 Forbidden`。
- 未登入請求回傳 `401 Unauthorized`。
- 不存在的 habit 回傳 `404 Not Found`。

## 6. 本章邊界

第三章只定義故事與驗收標準，不建立 FastAPI router、資料庫模型、React 元件或測試檔。那些會在第 4 章之後依序展開。
