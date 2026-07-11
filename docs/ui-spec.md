# Habit Life RPG UI Spec

## 1. 設計原則

介面要有 RPG 冒險日誌的性格，但首先是一個可重複使用的習慣工具。資訊必須安靜、清楚、可掃描，不使用大型行銷 Hero、玻璃擬態、裝飾光球或難以閱讀的遊戲字體。

- 背景使用近黑墨色，內容使用象牙白、苔綠、金色與磚紅形成多色但克制的系統。
- 卡片圓角不超過 8px，不把卡片放進另一張卡片。
- 指令使用 icon + text；編輯、封存與登出等熟悉工具可使用 lucide icon，並提供 tooltip 與 accessible name。
- 字體大小不隨 viewport 寬度縮放，letter spacing 固定為 0。
- 動態數值、按鈕 loading 文案與錯誤內容不得改變主要控制尺寸。

## 2. Responsive Layout

### mobile：390 × 844

- 單欄 Dashboard，左右 padding 16px。
- Header、Profile summary、Today progress、Habit list 與主要動作依序排列。
- 新增／編輯表單使用全螢幕 sheet 或自然文件流，不塞入窄小 modal。
- 觸控目標至少 44 × 44px，長名稱可換行但不得壓到操作按鈕。

### desktop：1440 × 1000

- 最大內容寬度 1120px，固定左右留白。
- Profile summary 與 Today progress 可形成兩欄；Habit 工作區維持主要閱讀寬度。
- 表單與清單可並排，但不得出現卡片套卡片。
- 版面在 loading、empty、error 與成功狀態間維持穩定。

## 3. 畫面

### Auth Screen

- 以 tabs 或 segmented control 切換 Login / Register。
- 帳號、密碼有永久可見 label，不以 placeholder 代替。
- 密碼可顯示／隱藏，icon button 有 tooltip。
- 表單錯誤顯示在欄位附近，總體 API error 使用 `role="alert"`。

### Dashboard

- Header 顯示產品名稱、目前使用者與 Logout。
- Profile summary 顯示 level、累積 EXP、gold 與下一級門檻。
- Today progress 顯示今天完成數／啟用 Habit 總數。
- Habit list 顯示名稱、分類、streak、今日狀態與主要 Check-in 動作。
- 建立 Habit 是清楚的主要命令；Edit 與 Archive 是次要工具。

### Habit Form

- 名稱必填，顯示 120 字限制。
- 描述、分類為選填。
- 儲存期間欄位與按鈕停用，按鈕寬度不因文字改變。
- Cancel 不清除已儲存資料。

## 4. Component States

| 元件 | loading | empty | success | error |
| --- | --- | --- | --- | --- |
| Auth | 停用提交並保留欄位 | 不適用 | 進入 Dashboard | 欄位或表單 alert |
| Dashboard | 穩定 skeleton | 建立第一個 Habit | 顯示最新摘要 | retry panel |
| Habit row | Check-in spinner | 不適用 | Done + reward feedback | 恢復可操作並顯示訊息 |
| Habit form | 固定尺寸 saving state | 空白初始值 | 關閉並刷新清單 | 保留輸入與錯誤 |

## 5. Accessibility

- keyboard 使用者能依合理順序完成登入、建立 Habit、打卡、編輯與登出。
- 所有可操作元件都有可見 focus 樣式，focus 不被 sticky header 或 dialog 遮住。
- icon-only button 必須有 `aria-label` 與 tooltip。
- 成功訊息使用禮貌的 live region；錯誤使用 `role="alert"`。
- 顏色不是唯一狀態線索；Done、Error 與 Level-up 都有文字或 icon。
- 對比符合 WCAG AA 的一般文字需求。

## 6. Content Language

主要介面使用繁體中文，技術欄位維持 Habit、EXP、gold、level。文案短而具體，不用畫面文字介紹產品功能或教學操作。

## 7. 不使用的視覺模式

- 不使用巨大 Hero、宣傳式價值主張或功能介紹卡。
- 不使用滿版漸層、紫藍單色系、米色單色系或裝飾性光暈。
- 不使用 canvas、3D 場景或遊戲引擎。
- 不以動畫掩蓋 loading；尊重 `prefers-reduced-motion`。
