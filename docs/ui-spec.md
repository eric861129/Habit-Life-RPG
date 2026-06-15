# Habit Life RPG UI Spec

版本：Chapter 3 Blueprint  
狀態：MVP 介面規格  
對應書稿：第 3.4 節「線框圖與 UI Spec」

## 1. 文件目的

本文件定義 `Habit Life RPG` MVP 的第一版視覺骨架。第三章只建立靜態原型與 UI 規則，讓讀者在進入後端章節前，先看見產品大致長什麼樣子。

正式 React + Vite 前端會在第 7 章依照本規格重建，不直接沿用第三章的靜態 HTML。

## 2. 設計方向

`Habit Life RPG` 的視覺語言應該讓使用者感覺自己正在打開一個復古像素 RPG 的任務選單，而不是一般待辦清單。畫面可以使用 `Quest`、`Hero`、`Guild Rank`、`Reward` 等 RPG 呈現語彙，但資料欄位、API、測試與程式碼命名仍維持 `habit` / `habits` / `habit_id`。

核心感受：

- 復古像素 RPG 選單感，帶有任務板、角色面板與戰利品回饋感。
- 使用低飽和 16-bit 色盤，避免 Cyberpunk 霓虹、玻璃擬態或現代發光 UI。
- 苔綠色代表可執行行動，金色代表 reward、rank、gold。
- 使用硬邊框、像素角標、實心陰影與方塊進度條，營造老式遊戲選單語彙。
- 資訊層級清楚，優先呈現 Hero Status 與今日 Quest Log。
- 元件密度適中，能支援手機版為主的閱讀與操作。

## 3. 色彩系統

| Token | 色碼 | 用途 |
| :--- | :--- | :--- |
| `--color-primary` | `#171923` | App 背景與主要深色區域 |
| `--color-accent` | `#7FB069` | 主要行動、可打卡狀態、進度條 |
| `--color-surface` | `#262A35` | Hero 面板、Quest 卡片、底部導覽 |
| `--color-surface-muted` | `#34343F` | 次要容器與 reward chip |
| `--color-text` | `#F3E6C8` | 主要文字，偏羊皮紙色 |
| `--color-muted` | `#B8AA88` | 次要文字、說明文字 |
| `--color-gold` | `#D6A84F` | 金幣、rank 與獎勵 |
| `--color-danger` | `#B85C50` | 錯誤、HP 風險、失敗狀態 |
| `--color-border` | `#6F6047` | 像素面板邊框 |

## 4. 間距與尺寸

- 基礎間距使用 8px 倍數：`8 / 16 / 24 / 32`。
- 卡片圓角以 0px 或 4px 為主，維持像素遊戲硬邊感。
- 主要操作按鈕高度至少 44px，方便手機點擊。
- 手機版主要內容寬度使用全寬，左右保留 16px padding。
- 桌面版原型以手機 app shell 置中展示，最大寬度 420px。
- RPG 裝飾只能用像素邊框、角標、rank 標籤、reward chip 與方塊進度條，不加入複雜背景圖或難以維護的美術素材。

## 5. 字體

- 英文與數字優先使用 monospace，中文使用系統字體 fallback，避免載入外部字型。
- 不使用 viewport width 動態縮放字體。
- 字級建議：
  - App title：22px / 700。
  - Section heading：16px / 700。
  - Habit title：15px / 700。
  - Body：14px / 400。
  - Metadata：12px / 600。

## 6. 主要畫面區塊

### 6.0 Game Studio 取向

第三章不導入 Phaser、Three.js 或遊戲引擎。本章採用 `Game UI Frontend` 的思路，把畫面先設計成復古像素 RPG 的 DOM UI：

- 玩家動詞：完成 habit、打卡領獎、累積 EXP、避免 HP 扣減。
- 核心循環：看見 Hero Status -> 選擇 Quest -> 打卡 -> 領取 reward -> 檢查是否升級。
- UI 表層：用 Quest Log、Guild Rank、Reward chip、Level gate、像素邊框與方塊進度條呈現遊戲感。
- 工程邊界：UI 可顯示 Quest，但 API、資料表與測試仍使用 habit 命名。
- 本章只做 DOM 靜態原型，不做 canvas playfield、角色動畫或戰鬥系統。

### 6.1 App Header

顯示產品名稱與今日狀態。

內容：

- `Habit Life RPG`
- 今日日期或短句。
- 小型 rank 標記，例如 `Rank D`。

### 6.2 Hero Status

畫面最上方的核心資訊區。

必要資訊：

- 角色名稱與職業稱號。
- 等級。
- Guild Rank。
- Streak。
- HP。
- EXP 進度。
- 金幣。

這個區塊要像 RPG character sheet 的簡化版，讓使用者先看見自己的成長狀態，再進入 habit 操作。

### 6.3 Quest Log

畫面中段顯示今日可打卡 habit。UI 可稱為 Quest Log，但底層仍是 habit 清單。每個 habit item 應該像一張任務捲軸，而不是現代卡片。

每個 habit item 至少包含：

- habit 名稱。
- RPG 化類型或簡短描述，例如 `Mind quest`、`Body quest`。
- Quest 序號或 rank，例如 `Quest 01`、`Rank C`。
- 獎勵資訊，例如 `+40 EXP`、`+8 gold`。
- 當日狀態，例如 `Ready`、`Done`、`Locked`。
- 主要打卡按鈕。

任務捲軸呈現規則：

- 使用羊皮紙底色與深色墨字。
- 左右可有卷軸端或像素化紙張邊界。
- reward chip 像蓋章或任務報酬標籤。
- 仍需保留 `habit` 的產品語義，不把資料模型改名為 quest。

### 6.4 回饋提示

第三章靜態原型應展示一個成功或升級狀態，讓讀者看見 RPG 化的成就感。

建議內容：

- `Level gate unlocked`
- `120 / 400 EXP`
- 復古方塊進度條。
- reward 或 rank 提示。

### 6.5 Bottom Navigation

底部導覽先展示三個 MVP 入口：

- Home
- Quests
- Hero

第三章只展示視覺骨架，不需要任何切換邏輯。

## 7. 元件狀態

| 元件 | 狀態 | 呈現 |
| :--- | :--- | :--- |
| Check-in button | Ready | Accent 背景，文字可用 `打卡領獎` |
| Check-in button | Done | 深色背景與 muted 文字 |
| Habit item | Ready | 任務捲軸、rank 標籤、reward chip |
| Habit item | Done | 已完成捲軸狀態，保留 reward 但降低強調 |
| Error toast | Planned | 第 7 章接 API 後再實作 |
| Level up panel | Static preview | 第三章先用 RPG reward panel 展示 |

## 8. 靜態原型

第三章原型位置：

```text
prototype/static/index.html
```

限制：

- 只使用 HTML/CSS。
- 不使用 JavaScript。
- 不接後端 API。
- 不引入 React、Vite 或 Tailwind。
- 只展示 MVP 視覺骨架。

## 9. 後續章節接續點

- 第 4 章：把 UI 狀態與 API 契約對齊。
- 第 5 章：完成 `POST /api/v1/habits/{habit_id}/checkin`。
- 第 6 章：用測試確認成功、重複打卡、權限錯誤等狀態。
- 第 7 章：用 React + Vite + Tailwind 重建正式前端。
