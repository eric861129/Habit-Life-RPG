# Azure Static Web Apps 前端部署

HLR React 前端使用 Static Web Apps Free。免費方案不含 SLA，適合個人學習與書籍示範；超過免費配額時會停止服務，不會自動轉成 Standard 計費。

## 建置設定

- App location：`frontend`
- Build command：`npm run build`
- Output location：`dist`
- API root：GitHub Environment variable `HLR_BACKEND_URL`
- SPA fallback：`frontend/staticwebapp.config.json`

`.github/workflows/deploy-frontend.yml` 會先執行 `npm ci`、Vitest 與 production build，全數成功才上傳。Static Web Apps deployment token 儲存於 `azure-demo` Environment Secret，不出現在 workflow 或終端輸出。

## 驗收

1. 首頁回應 HTTP 200，並包含 `Habit Life RPG`。
2. React 路由重新整理後仍回到 `index.html`。
3. 前端建置檔只包含公開 HTTPS API 網址，不包含 token 或 secret。
4. 註冊、建立 Habit 與 Check-in 在公開網址完整成功。
