# 第二輪案例：會員驗證垂直切片

> 分支：`chapter/r2-capstone`
>
> 起點：`book-v2-ch07-frontend`
>
> 完成 tag：`book-v2-r2-auth-slice`（本機待發布）

## 目的

第一輪專案已經具備註冊、登入、密碼雜湊、JWT 與受保護 API。第二輪不重寫整套驗證，而是補上初學者最容易漏掉的「Token 有期限」契約，讓後端回應、OpenAPI、瀏覽器 session 與失效畫面形成完整垂直切片。

讀者可以依序驗收：

1. `POST /api/v1/auth/register` 建立帳號，回傳 `201`。
2. 資料庫只保留 Argon2 密碼雜湊，不保留明文。
3. `POST /api/v1/auth/login` 回傳 Token、`bearer` 與 `expires_in`。
4. 帶 Bearer Token 呼叫 `GET /api/v1/user/profile`，回傳 `200`。
5. 未帶、無效或過期 Token，回傳 `401`。
6. 前端依 `expires_in` 計算絕對到期時間；到期或伺服器回 `401` 時清除 session 並要求重新登入。

## 契約變更

```yaml
TokenResponse:
  required: [access_token, token_type, expires_in]
  properties:
    access_token: {type: string}
    token_type: {type: string, const: bearer}
    expires_in:
      type: integer
      minimum: 1
      description: Access token lifetime in seconds.
```

範例回應：

```json
{
  "access_token": "eyJ...示範值",
  "token_type": "bearer",
  "expires_in": 3600
}
```

## Red 證據

先更新 OpenAPI 與測試，再執行：

```powershell
python -m pytest tests/test_auth_api.py::test_login_returns_token_lifetime_in_seconds -q
```

第一次執行得到：

```text
FAILED tests/test_auth_api.py::test_login_returns_token_lifetime_in_seconds
KeyError: 'expires_in'
1 failed
```

這個失敗符合需求：登入成功，但回應尚未提供 Token 存活秒數。它不是安裝失敗或測試寫錯目標。

## Green 與 Refactor

後端修改：

- `TokenResponse` 加入正整數 `expires_in`。
- `access_token_lifetime_seconds()` 將設定中的分鐘換算成秒。
- `build_token_response()` 統一註冊與登入回應，避免兩個路由各自組裝。

前端修改：

- `sessionStorage` 儲存 `{token, expiresAt}`，不再永久放在 `localStorage`。
- `restore()` 在到期邊界清除資料並回報 `expired: true`。
- API 回 `401` 時仍清除 session；伺服器驗證結果是最終依據。
- 關閉瀏覽器分頁會結束這份教學 session。

## 安全邊界

`sessionStorage` 仍可被同一頁面的 JavaScript 存取，因此仍可能受 XSS 影響。本案例只是讓初學者看清楚 Token 期限與失效旅程，不代表所有正式產品都應採用這個方案。

正式環境應依威脅模型評估 HttpOnly、Secure、SameSite Cookie 或其他儲存方式，也要搭配 CSP、輸入輸出處理、短效 Token、撤銷策略與伺服器端驗證。

JWT 的簽章用來保護完整性，不代表 payload 自動加密。不要把密碼、金鑰或不必要個資放入 payload。

## 驗收命令

```powershell
python -m pytest -q
python -m ruff check backend tests scripts
python scripts/verify_openapi.py
Set-Location frontend
npm test -- --run
npm run build
```

最低可觀察結果：

- auth tests 與 OpenAPI parity 通過。
- session 測試涵蓋寫入、未到期還原與到期清除。
- App 測試涵蓋登入成功、客戶端到期，以及伺服器 `401`。
- TypeScript build 成功。

## 復原

這是獨立教學分支，不修改既有 `main` 或 `book-v2-ch*` tags。需要回到第一輪第 7 章成果時，可切回：

```powershell
git switch --detach book-v2-ch07-frontend
```

比較第二輪會員驗證差異：

```powershell
git diff book-v2-ch07-frontend..book-v2-r2-auth-slice
```
