# HLR 最終交付清單

## 章節版本

| 章節 | Branch | Tag／Release |
| --- | --- | --- |
| 2 | `chapter/02-toolbox` | `book-v2-ch02-toolbox` |
| 3 | `chapter/03-blueprint` | `book-v2-ch03-blueprint` |
| 4 | `chapter/04-architecture` | `book-v2-ch04-architecture` |
| 5 | `chapter/05-backend` | `book-v2-ch05-backend` |
| 6 | `chapter/06-quality` | `book-v2-ch06-quality` |
| 7 | `chapter/07-frontend` | `book-v2-ch07-frontend` |
| 8 | `chapter/08-deployment` | `book-v2-ch08-deployment` |
| 9 | `chapter/09-operations` | `book-v2-ch09-operations` |
| 10 | `chapter/10-agent-ready` | `book-v2-ch10-agent-ready` |

所有 Release 位於 <https://github.com/eric861129/Habit-Life-RPG/releases>。已發布章節分支與 Tag 不得改寫。

## 正式環境

- Frontend：<https://victorious-dune-0ad92d11e.7.azurestaticapps.net>
- API：<https://hlr-eric861129-v2-api.azurewebsites.net>
- Docs：<https://hlr-eric861129-v2-api.azurewebsites.net/docs>
- Liveness：<https://hlr-eric861129-v2-api.azurewebsites.net/health/live>
- Readiness：<https://hlr-eric861129-v2-api.azurewebsites.net/health/ready>

Azure 實際資源必須維持 Static Web Apps `Free`、App Service `F1/Free`、SQL `freelimit + useFreeLimit=true + AutoPause`。

## 發版驗證

```bash
python scripts/final_verify.py
```

- [ ] Ruff、Pytest、OpenAPI parity 全部成功。
- [ ] Vitest 與 frontend production build 成功。
- [ ] 唯讀公開探測五個網址皆為 200。
- [ ] 完整 reader journey 驗證 register、login、Habit list、check-in、409、防具獎勵與 archive。
- [ ] 公開示範帳號可登入，繁體中文 Habit 未損壞。
- [ ] GitHub CI、backend deploy、frontend deploy、public health workflow 成功。
- [ ] Repository、branches、Tags、Releases 與正式網址可匿名開啟。
