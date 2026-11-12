# 財與遠方

香港繁體中文的財務自由、被動收入與旅行規劃網站；原始碼由 `hill02252024/fire-and-travel` 管理。

## 網站內容

- `/calculators/fire.html`：FIRE 年期情境試算器
- `/calculators/travel.html`：長途旅行現金流試算器
- `/guides/`：FIRE、被動收入、香港預算、應急金、複利、平均成本法、ETF、分散投資、投資費用、股息、強積金與投資防騙指南、美國 Payday Compass 出糧預算 App、亞洲打工仔適用限制；文章來源資料在 `data/guides.json`- `/brokers/`：IBKR、老虎證券、富途及 Webull 香港法團、牌照、官方費率、風險與本站邀請連結披露；資料在 `data/brokers.json`，由 `scripts/build_brokers.py` 產生
- `/news/`：每週新聞摘要；來源、原文連結和日期隨文章列出

計算器只在瀏覽器運算。所有投資數字都由使用者輸入，不預設或承諾投資回報。本站只提供一般教育資訊，不提供個人化投資建議。

## 本機檢查

```bash
python3 scripts/build_guides.py
python3 scripts/build_brokers.py
python3 scripts/build_news.py
python3 scripts/apply_publish_mode.py
python3 scripts/check_site.py
python3 -m unittest scripts/test_calculators.py
node --test scripts/calculators.test.mjs
```

正式網站由 `hill02252024/fire-and-travel` 的 `main` 分支提供，目標網域為 `https://fireandjourney.com/`。GitHub Pages 已設定網站自訂網域；GoDaddy DNS 仍待完成。Zo 的週六排程會更新此 repository、重建網站並測試後推送至 `main`。沒有足夠可靠新聞時跳過發布。排程不得更改 CNAME、網域或 GoDaddy DNS。

## 週更守則

每次最多整理五則本週重要消息，以繁體中文香港用語摘要，標清發布日期和原始來源；沒有足夠可靠且值得整理的消息時，略過該週，不建立空白新聞頁。優先監管機構、政府、央行、交易所及新聞機構的一手報道；不得把來源未證實的傳聞寫成事實，不得給出個人化買賣建議，不得複製大段原文。提交前須執行網站檢查並只提交與本週摘要相關的檔案。

## 網域與預覽

正式網站網域為 `https://fireandjourney.com/`；GitHub Pages 專案根目錄已用此網域作為 canonical，頁面可索引，並提供 `robots.txt` 和 `sitemap.xml`。GoDaddy DNS 尚待更新與傳播，Search Console 的網域驗證和 sitemap 提交也待 DNS 完成。

既有預覽 `https://todays-tasks.com/fire-and-travel/` 保留為 noindex 副本，不進入 Today’s Tasks 根站 sitemap；此副本不再是理財網站的正式 SEO 網址。網域與索引設定由 `data/site.json` 管理。
