# 財與遠方

香港繁體中文的財務自由、被動收入與旅行規劃網站；原始碼由 `hill02252024/fire-and-travel` 管理。

## 網站內容

- `/calculators/fire.html`：FIRE 年期情境試算器
- `/calculators/travel.html`：長途旅行現金流試算器
- `/guides/`：FIRE、被動收入、香港預算、應急金、複利、平均成本法、ETF、分散投資、投資費用、股息、強積金與投資防騙指南、美國 Payday Compass 出糧預算 App、亞洲打工仔適用限制；文章來源資料在 `data/guides.json`
- `/news/`：每週新聞摘要；來源、原文連結和日期隨文章列出

計算器只在瀏覽器運算。所有投資數字都由使用者輸入，不預設或承諾投資回報。本站只提供一般教育資訊，不提供個人化投資建議。

## 本機檢查

```bash
python3 scripts/build_guides.py
python3 scripts/build_news.py
python3 scripts/apply_publish_mode.py
python3 scripts/check_site.py
python3 -m unittest scripts/test_calculators.py
node --test scripts/calculators.test.mjs
```

原始碼保存在 `hill02252024/fire-and-travel`；暫時公開副本由 Zo 的週六排程同步至 `hill02252024/hill02252024.github.io` repository 的 `fire-and-travel/` 子目錄。排程更新 `data/news.json`、重建頁面、套用暫時 `noindex`、執行檢查和測試，再只更新根站的子目錄，不碰首頁、其他頁面或 CNAME。沒有足夠可靠新聞時跳過發布。

## 週更守則

每次最多整理五則本週重要消息，以繁體中文香港用語摘要，標清發布日期和原始來源；沒有足夠可靠且值得整理的消息時，略過該週，不建立空白新聞頁。優先監管機構、政府、央行、交易所及新聞機構的一手報道；不得把來源未證實的傳聞寫成事實，不得給出個人化買賣建議，不得複製大段原文。提交前須執行網站檢查並只提交與本週摘要相關的檔案。

## 暫時預覽與正式網域

暫時公開預覽於 `https://todays-tasks.com/fire-and-travel/`，內容由本 repository 同步至既有 GitHub Pages 根站的獨立子目錄；不改首頁、其他路徑或 CNAME。暫時副本所有頁面均標記 `noindex,follow`，不載入 AdSense，也不進入根站 sitemap，避免未來換網域前把理財內容併入既有網站搜尋索引。

Canonical 目標及 GitHub Pages 專案路徑仍由 `data/site.json` 管理。取得新網域後，更新 `baseUrl`、`basePath` 與 `indexable`，重新生成頁面，再停止同步至 `hill02252024.github.io` 根站。
