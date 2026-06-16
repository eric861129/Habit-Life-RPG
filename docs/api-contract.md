# Habit Life RPG API Contract

版本：Chapter 4 Foundation  
狀態：API 溝通契約  
對應書稿：第 4.3 節「API 規格與溝通契約」

## 1. 文件目的

本文件用讀者可讀的方式解釋 `docs/openapi.yaml`。OpenAPI YAML 是機器可讀的契約，本文件則說明前端、後端、測試與 AI 建築團隊應如何理解這份契約。

第四章只建立契約，不建立 FastAPI route、資料庫連線或前端 API client。

## 2. 契約原則

- 所有 API 走 `/api/v1` 版本路徑。
- 所有資料交換使用 JSON。
- 進入 API、資料表、測試與程式碼後，一律使用 `habit` / `habits` / `habit_id`。
- UI 可以把 habit 包裝成 Quest，但 API 契約不使用 Quest 命名。
- 角色數值由後端結算，前端只呈現 response。
- 錯誤格式統一為 `{ "detail": "..." }`。

## 3. Endpoint 清單

| 方法 | 路徑 | 說明 | 使用章節 |
| :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/user/profile` | 取得目前玩家狀態 | 第 5 章後端、第 7 章 Hero Status |
| `GET` | `/api/v1/habits` | 取得目前使用者的 habits | 第 5 章後端、第 7 章 Quest Log |
| `POST` | `/api/v1/habits/{habit_id}/checkin` | 對單一 habit 打卡並領取獎勵 | 第 5 章主線 API |

## 4. 打卡成功回應

`POST /api/v1/habits/{habit_id}/checkin` 成功時回傳：

```json
{
  "habit_id": 1,
  "checked_in": true,
  "current_exp": 160,
  "current_gold": 43,
  "current_level": 2,
  "leveled_up": false
}
```

欄位意義：

| 欄位 | 型別 | 說明 |
| :--- | :--- | :--- |
| `habit_id` | integer | 被打卡的 habit |
| `checked_in` | boolean | 後端是否接受本次打卡 |
| `current_exp` | integer | 打卡後的玩家經驗值 |
| `current_gold` | integer | 打卡後的玩家金幣 |
| `current_level` | integer | 打卡後的玩家等級 |
| `leveled_up` | boolean | 本次打卡是否造成升級 |

## 5. 錯誤回應

所有錯誤 response 使用同一種外型：

```json
{
  "detail": "Habit already checked in today."
}
```

| 狀態碼 | 情境 | 前端行為 |
| :--- | :--- | :--- |
| `400 Bad Request` | 同一個 habit 今天已經打卡 | 顯示重複打卡訊息，不更新成功狀態 |
| `401 Unauthorized` | 使用者未登入或 token 無效 | 導向登入頁或要求重新登入 |
| `403 Forbidden` | habit 不屬於目前使用者 | 顯示權限錯誤，不更新角色數值 |
| `404 Not Found` | habit 不存在 | 顯示資料不存在，不更新角色數值 |

## 6. Profile Response

`GET /api/v1/user/profile` 回傳目前玩家狀態：

```json
{
  "id": 1,
  "username": "arthur",
  "level": 2,
  "exp": 120,
  "gold": 35,
  "hp": 86
}
```

前端第 7 章會用這些欄位渲染 Hero Status。

## 7. Habit List Response

`GET /api/v1/habits` 回傳目前使用者的 habit 清單：

```json
[
  {
    "id": 1,
    "title": "晨間 20 分鐘閱讀",
    "category": "Mind",
    "last_check_in": null,
    "checked_in_today": false
  }
]
```

前端可以把這份資料呈現成 Quest Log，但底層命名仍是 habit。

## 8. 與測試的關係

第 6 章撰寫 Pytest 時，至少要驗證：

- 成功打卡回傳 `200 OK` 與完整成功欄位。
- 同日重複打卡回傳 `400 Bad Request`。
- 未登入回傳 `401 Unauthorized`。
- 非本人 habit 回傳 `403 Forbidden`。
- 不存在的 habit 回傳 `404 Not Found`。
- 錯誤 response 都包含 `detail`。

## 9. 第四章邊界

本文件不是程式碼，也不是測試。它是後續實作的契約來源。

第 5 章後端實作時，FastAPI 的實際 response 必須與 `docs/openapi.yaml` 保持一致。
