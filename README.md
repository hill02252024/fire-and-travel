# 財與遠方

香港繁體中文的財務自由、被動收入與旅行規劃網站，部署於 GitHub Pages。Repository: `hill02252024/fire-and-travel`。

## 網站內容

- `/calculators/fire.html`：FIRE 年期情境試算器
- `/calculators/travel.html`：長途旅行現金流試算器
- `/guides/`：FIRE、被動收入、香港預算、應急金、複利、平均成本法、ETF、分散投資、投資費用、股息、強積金與投資防騙指南；文章來源資料在 `data/guides.json`
- `/news/`：每週新聞摘要；來源、原文連結和日期隨文章列出

計算器只在瀏覽器運算。所有投資數字都由使用者輸入，不預設或承諾投資回報。本站只提供一般教育資訊，不提供個人化投資建議。

## 本機檢查

```bash
python3 scripts/build_guides.py
python3 scripts/build_news.py
python3 scripts/check_site.py
python3 -m unittest scripts/test_calculators.py
node --test scripts/calculators.test.mjs
```

GitHub Pages 直接從 `main` 分支根目錄發布，不需要 GitHub Actions 工作流程權限。每週新聞由 Zo 的週六排程更新 `data/news.json`，並在提交前重新產生新聞頁、更新 sitemap、執行檢查；沒有足夠可靠新聞時應跳過發布。

## 週更守則

每次最多整理三則本週重要消息，以繁體中文香港用語摘要，標清發布日期和原始來源。優先監管機構、政府、央行、交易所及新聞機構的一手報道；不得把來源未證實的傳聞寫成事實，不得給出個人化買賣建議，不得複製大段原文。提交前須執行網站檢查並只提交與本週摘要相關的檔案。

## 發布網址

GitHub 帳戶的根 Pages 網站已綁定 `todays-tasks.com`。因此這個專案網站會以子路徑發布：`https://todays-tasks.com/fire-and-travel/`。如日後要用獨立網域，需另行設定 DNS 和 Pages 網域，不要移除現有根網站的網域設定。
