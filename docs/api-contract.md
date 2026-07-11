# Habit Life RPG API Contract

- Base path：`/api/v1`
- Authentication：`Authorization: Bearer <access-token>`
- Content type：`application/json`
- 正式機器契約：`docs/openapi.yaml`

## 狀態碼

| 狀態碼 | 用途 |
| --- | --- |
| `200` | 讀取或修改成功 |
| `201` | 註冊、建立 Habit 或建立 Check-in 成功 |
| `204` | 封存成功且無回應內容 |
| `401` | Token 缺少、失效或登入失敗 |
| `404` | 資源不存在或不屬於目前使用者 |
| `409` | 帳號重複或同日重複 Check-in |
| `422` | Request schema 驗證失敗 |

獎勵、streak 與 level 由 `POST /api/v1/habits/{habit_id}/checkins` 的後端交易計算。
