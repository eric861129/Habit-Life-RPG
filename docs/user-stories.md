# Habit Life RPG User Stories

本文件使用穩定識別碼，後續 API、測試與書稿都引用相同編號。

## AUTH-01 建立帳號

身為 Guest，我想建立帳號，以便保存自己的成長資料。

Given 帳號名稱尚未被使用且密碼符合規則  
When Guest 送出註冊表單  
Then 系統建立帳號、回傳 Access Token，並導向 Dashboard。

Given 帳號名稱已存在  
When Guest 再次使用相同名稱註冊  
Then 系統回傳 `409 Conflict`，且不建立第二個帳號。

## AUTH-02 登入與登出

身為 Member，我想安全登入與登出，以便在共用裝置保護資料。

Given 帳號與密碼正確  
When Guest 登入  
Then 系統回傳 Access Token 並載入本人資料。

Given Member 已登入  
When Member 選擇登出  
Then 前端移除 Token，回到登入畫面，且不再呼叫受保護 API。

## HABIT-01 查看今日習慣

身為 Member，我想查看自己的啟用 Habit，以便知道今天要完成什麼。

Given Member 已登入且有啟用 Habit  
When Dashboard 載入  
Then 只顯示本人的啟用 Habit 與今日打卡狀態。

Given Member 尚未建立 Habit  
When Dashboard 載入  
Then 顯示 empty state 與清楚的建立入口。

## HABIT-02 建立習慣

身為 Member，我想建立 Habit，以便定義自己的每日行動。

Given Member 已登入且名稱符合限制  
When Member 儲存新 Habit  
Then 系統建立屬於該 Member 的啟用 Habit，並立即顯示在今日任務。

## HABIT-03 修改習慣

身為 Member，我想修改 Habit 名稱、描述與分類，以便讓目標保持清楚。

Given Habit 屬於目前 Member  
When Member 儲存有效修改  
Then 系統回傳更新後資料且不改變既有 Check-in 歷史。

## HABIT-04 封存與恢復

身為 Member，我想封存暫停的 Habit，以便今日畫面只保留正在進行的目標。

Given Habit 屬於目前 Member  
When Member 封存 Habit  
Then Habit 不再出現在今日任務，歷史 Check-in 仍可保留。

## CHECKIN-01 每日成功打卡

身為 Member，我想為完成的 Habit 打卡，以便取得角色成長回饋。

Given Habit 屬於目前 Member、未封存且今天尚未打卡  
When Member 送出 Check-in  
Then 系統建立紀錄、回傳 `201 Created`，增加 `40 EXP` 與 `8 gold`。

## CHECKIN-02 阻止重複獎勵

身為 Member，我不應因重複點擊而得到多次獎勵。

Given 同一 Habit 今天已成功打卡  
When Member 再次送出 Check-in  
Then 系統回傳 `409 Conflict`，Check-in、EXP、gold 與 level 均不改變。

## CHECKIN-03 計算連續天數

身為 Member，我想看見連續天數，以便理解自己的持續成果。

Given 同一 Habit 昨天曾成功打卡  
When Member 今天成功打卡  
Then Habit streak 增加一。

Given 同一 Habit 的最近打卡早於昨天  
When Member 今天成功打卡  
Then Habit streak 重設為一。

## CHECKIN-04 保護資料所有權

身為 Member，我只能操作自己的 Habit。

Given Habit 不存在或不屬於目前 Member  
When Member 嘗試讀取、修改、封存或打卡  
Then 系統回傳 `404 Not Found`，且不洩漏他人資料。

## DASHBOARD-01 顯示角色摘要

身為 Member，我想看到 level、EXP、gold 與今日進度，以便立即理解目前狀態。

Given Member 已登入  
When Dashboard 載入完成  
Then 顯示最新 Profile 與今天已完成／總 Habit 數。

## DASHBOARD-02 處理系統狀態

身為 Member，我想在網路較慢或失敗時得到清楚回饋，以便知道下一步。

Given 請求仍在進行  
When 畫面等待資料  
Then 顯示不造成版面跳動的 loading state。

Given API 回傳 `401 Unauthorized`  
When 前端收到錯誤  
Then 清除失效 Token、顯示 session 訊息並回到 Login。

Given API 或網路暫時失敗  
When 前端無法完成操作  
Then 顯示可讀 error state 與 retry 動作，不假裝成功。
