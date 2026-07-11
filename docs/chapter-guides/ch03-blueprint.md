# 第 3 章：藍圖繪製

`chapter/03-blueprint` 是 `chapter/02-toolbox` 的累進版本。它只增加可驗收的產品文件，不提前加入後端或 React 成品。

## 本章成果

- `docs/PRD.md`：完整書本 MVP、規則、邊界與完成定義。
- `docs/user-stories.md`：AUTH、HABIT、CHECKIN、DASHBOARD 驗收案例。
- `docs/ux-flow.md`：成功、loading、empty、error、401、404 與 duplicate 流程。
- `docs/ui-spec.md`：mobile、desktop、元件狀態與可及性規格。

## 固定產品規則

- 一個 Habit 每個應用程式曆日最多成功打卡一次。
- 成功打卡固定增加 `40 EXP` 與 `8 gold`。
- 升級門檻是 `level × 200`。
- 連續日期增加 streak，中斷後重設為一。
- 後端是獎勵與資料所有權的唯一權威。

## 驗證

```bash
python -m pytest tests/test_environment_contract.py tests/test_blueprint_contract.py -q
```

所有文件契約通過後，下一個累進版本 `chapter/04-architecture` 才能把產品語言翻成資料庫與 API 契約。
