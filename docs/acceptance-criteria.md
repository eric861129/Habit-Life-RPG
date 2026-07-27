# Habit Life RPG 驗收標準

版本：2026-07-27 第二輪文件驅動變更

## AC-PRIORITY-01 建立預設值

Given 已登入會員開啟新增習慣表單  
When 只填名稱並儲存  
Then API建立 `priority=medium` 的Habit，畫面顯示「中」標籤。

## AC-PRIORITY-02 選擇高或低優先級

Given 已登入會員開啟新增或編輯表單  
When 選擇高、中或低優先級並儲存  
Then Request送出對應的 `high`、`medium` 或 `low`，回應與重新載入後保持一致。

## AC-PRIORITY-03 拒絕不合法值

Given 呼叫端送出不在允許清單中的優先級  
When API驗證Request  
Then 回傳 `422 Unprocessable Entity`，且不建立或修改Habit。

## AC-PRIORITY-04 今日清單排序

Given 會員擁有高、中、低優先級的啟用Habit  
When 呼叫 `GET /api/v1/habits`  
Then 依高、中、低排序；同一優先級依Habit `id` 遞增。

## AC-PRIORITY-05 交付證據

Given 功能完成  
When 執行後端、OpenAPI契約、前端元件測試與正式建置  
Then 所有檢查通過，變更紀錄列出文件、測試、程式與驗收結果。
