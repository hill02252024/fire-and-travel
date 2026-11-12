from datetime import date
from html import escape
import json
from pathlib import Path
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "data/brokers.json").read_text(encoding="utf-8"))
BASE_URL = SITE["baseUrl"].rstrip("/")
BASE_PATH = SITE["basePath"].rstrip("/") + "/"
UPDATED = DATA["updated"]


def safe_https(url):
    parsed = urlparse(url)
    return parsed.scheme == "https" and bool(parsed.netloc)


def site_header(active="brokers"):
    links = [
        ("財務自由試算", "calculators/fire.html", "fire"),
        ("旅行預算", "calculators/travel.html", "travel"),
        ("實用指南", "guides/", "guides"),
        ("券商介紹", "brokers/", "brokers"),
        ("每週新聞", "news/", "news"),
    ]
    nav = "".join(
        f'<a href="{BASE_PATH}{path}"' + (f' aria-current="page"' if key == active else "") + f'>{escape(label)}</a>'
        for label, path, key in links
    )
    return f'<header class="site-header"><a class="brand" href="{BASE_PATH}"><span class="brand-mark">財</span><span>{escape(SITE["name"])}</span></a><nav aria-label="主要導覽">{nav}</nav></header>'


def site_footer():
    return f'<footer class="site-footer"><div><a class="brand" href="{BASE_PATH}"><span class="brand-mark">財</span><span>{escape(SITE["name"])}</span></a><p>用數字規劃自由，用預算留住遠方。</p></div><nav aria-label="頁尾導覽"><a href="{BASE_PATH}about.html">關於本站</a><a href="{BASE_PATH}disclaimer.html">免責聲明</a><a href="{BASE_PATH}privacy.html">私隱政策</a><a href="{BASE_PATH}news/">每週新聞</a></nav><small>© {date.today().year} {escape(SITE["name"])}</small></footer>'


def list_items(items):
    return "<ul>" + "".join(f"<li>{escape(item)}</li>" for item in items) + "</ul>"


def source_list(sources):
    return "<ul>" + "".join(
        f'<li><a href="{escape(source["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(source["title"])}</a></li>'
        for source in sources
    ) + "</ul>"


def sections(title, items):
    return f'<section><h2>{escape(title)}</h2>{list_items(items)}</section>'


def article_schema(broker, canonical):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": broker["title"],
        "description": broker["description"],
        "datePublished": UPDATED,
        "dateModified": UPDATED,
        "inLanguage": "zh-HK",
        "author": {"@type": "Organization", "name": "財與遠方編輯部"},
        "publisher": {"@type": "Organization", "name": SITE["name"]},
        "mainEntityOfPage": canonical,
    }, ensure_ascii=False, separators=(",", ":"))


def referral_disclosure(broker):
    if broker["referralUrl"]:
        return "透過本站邀請連結開戶或符合券商活動條件時，本站可能獲得推薦獎勵；不保證你或本站一定符合資格。優惠、費用及條款由券商決定，請先看官方細則。這不是開戶或買賣建議。"
    return "本站目前沒有 IBKR 邀請連結。以下按鈕只連到 IBKR 官方網站，不會為本站帶來邀請獎勵；取得你的專屬連結後才會更新。"


def profile_cta(broker):
    url = broker["referralUrl"] or broker["officialUrl"]
    rel = "sponsored nofollow noopener noreferrer" if broker["referralUrl"] else "noopener noreferrer"
    return f'<section class="callout"><p class="eyebrow">開戶連結</p><h2>{escape(broker["ctaLabel"])}</h2><p>{escape(referral_disclosure(broker))}</p><p><a class="button button-primary" href="{escape(url, quote=True)}" target="_blank" rel="{rel}">{escape(broker["ctaLabel"])} →</a></p></section>'


def render_profile(broker):
    canonical = f'{BASE_URL}/brokers/{broker["slug"]}.html'
    background = "".join(f"<p>{escape(text)}</p>" for text in broker["background"])
    regulatory = "".join(f"<p>{escape(text)}</p>" for text in broker["regulatory"])
    fees = list_items(broker["fees"])
    sources = source_list(broker["sources"])
    return f'''<!doctype html>
<html lang="zh-HK"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(broker["title"])}｜財與遠方</title><meta name="description" content="{escape(broker["description"], quote=True)}"><link rel="canonical" href="{escape(canonical, quote=True)}"><meta property="og:type" content="article"><meta property="og:title" content="{escape(broker["title"], quote=True)}｜財與遠方"><meta property="og:description" content="{escape(broker["description"], quote=True)}"><meta property="og:url" content="{escape(canonical, quote=True)}"><link rel="stylesheet" href="{BASE_PATH}assets/site.css"><script type="application/ld+json">{article_schema(broker, canonical)}</script></head><body>{site_header()}<main class="article"><p class="breadcrumb"><a href="{BASE_PATH}">首頁</a>　/　<a href="{BASE_PATH}brokers/">券商介紹</a>　/　{escape(broker["name"])}</p><p class="eyebrow">券商資料整理 · 更新於 {UPDATED}</p><h1>{escape(broker["title"])}</h1><p class="lead">{escape(broker["lead"])}</p><div class="callout"><strong>本站邀請連結披露</strong><p>{escape(referral_disclosure(broker))}</p></div><section><h2>公司背景與香港法團</h2><p><strong>香港服務法團：</strong>{escape(broker["entity"])}</p><p><strong>牌照資料：</strong>{escape(broker["license"])}</p>{background}</section><section><h2>牌照、安全與投資者保障</h2>{regulatory}<p>持牌不等於零風險。開戶前請核對完整法團名稱、客戶協議、資金及證券託管安排、閒置現金處理、證券借貸授權，以及各市場的保障範圍。</p></section><section><h2>佣金與其他常見費用</h2><p>以下是官方費率頁的代表性股票收費，並非所有帳戶、產品或優惠的完整價格。收費會更改；落單前請以券商當刻顯示的預計費用和最新費表為準。</p>{fees}<p>除券商佣金和平台費外，可能還有印花稅、交易所／監管／結算費、匯兌差價、存取款、託管、公司行動、行情訂閱、孖展利息或產品費。選券商時，請用自己的市場、交易額和頻率計算總成本。</p></section>{sections("主要優點", broker["advantages"])}{sections("需要留意的限制", broker["limitations"])}{profile_cta(broker)}<section><h2>官方資料與自行核對</h2><p>以下連結用來核對法團、牌照、費率及監管資料；監管機構並沒有因此推薦該券商或其產品。</p>{sources}</section><section class="callout"><h2>開戶前快速檢查</h2><ul><li>帳戶由哪個法團提供？它的牌照目前是否有效？</li><li>你選的是哪個市場、費率計劃和產品？</li><li>佣金、平台費、法定徵費、匯兌和提款費加起來是多少？</li><li>優惠的期限、存款／交易要求和提取限制是甚麼？</li><li>自己是否理解孖展、期權、證券借貸和海外稅務風險？</li></ul><p><a href="{BASE_PATH}brokers/">返回券商資料總覽 →</a></p></section><p class="fine-print">本文只作一般教育資訊，不是投資、法律或稅務建議，不對任何券商作安全保證或個人化推薦。最後核對日期：{UPDATED}。</p></main>{site_footer()}</body></html>'''


def render_index():
    canonical = f"{BASE_URL}/brokers/"
    cards = []
    for broker in DATA["brokers"]:
        url = f'{BASE_PATH}brokers/{broker["slug"]}.html'
        cards.append(
            f'<article class="card"><p class="eyebrow">{escape(broker["entity"])}</p>'
            f'<h2><a href="{url}">{escape(broker["name"])}</a></h2>'
            f'<p>{escape(broker["lead"])}</p><a class="text-link" href="{url}">閱讀背景、牌照、費率和限制 →</a></article>'
        )
    source_note = "券商介紹採用官方資料，列出法團、牌照、費用和限制。本站可能透過部分邀請連結取得推薦獎勵；所有獎勵及優惠以券商條款為準。內容不代表推薦任何券商或投資產品。"
    return f'''<!doctype html>
<html lang="zh-HK"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>香港券商介紹：IBKR、老虎、富途、Webull｜財與遠方</title><meta name="description" content="比較 IBKR、老虎證券、富途與 Webull 香港法團背景、SFC 牌照、佣金、平台費、投資者保障及主要限制。"><link rel="canonical" href="{escape(canonical, quote=True)}"><meta property="og:type" content="website"><meta property="og:title" content="香港券商介紹：IBKR、老虎、富途、Webull｜財與遠方"><meta property="og:description" content="先核對法團、牌照和總費用，再了解各券商的平台優點與限制。"><meta property="og:url" content="{escape(canonical, quote=True)}"><link rel="stylesheet" href="{BASE_PATH}assets/site.css"></head><body>{site_header()}<main><section class="page-heading"><p class="breadcrumb"><a href="{BASE_PATH}">首頁</a>　/　券商介紹</p><p class="eyebrow">香港券商資料 · 更新於 {UPDATED}</p><h1>先看法團與總費用，再比較交易平台</h1><p class="lead">這裡整理 IBKR、老虎證券、富途與 Webull 的香港服務法團、牌照、股票費率、優點和限制，方便你自行核對；不替你作開戶或買賣決定。</p></section><section class="callout"><h2>推薦連結披露</h2><p>{escape(source_note)}</p></section><section class="callout"><h2>比較時先看這四件事</h2><ul><li>確認開戶協議中的香港法團和 SFC CE 編號，而不是只看品牌名稱。</li><li>將佣金、平台費、交易所／監管徵費、印花稅、匯兌和提款費一起計算。</li><li>「持牌」和投資者賠償基金都不是本金保證；賠償只按法定範圍和條件處理。</li><li>開戶優惠與邀請獎勵會變；以券商官方條款為準，切勿為領取獎賞而超出自己的需要交易。</li></ul></section><section class="section-block"><div class="section-head"><div><p class="eyebrow">券商資料</p><h2>四家平台</h2></div><p>本站沒有按排名推薦；請依你要交易的市場、費用和風險承受能力自行比較。</p></div><div class="card-grid">{"".join(cards)}</div></section><section class="callout"><h2>香港監管與賠償資料</h2><p><a href="https://apps.sfc.hk/publicregWeb/searchByBa" target="_blank" rel="noopener noreferrer">SFC 持牌人公眾紀錄冊</a>可用來核對法團和受規管活動。<a href="https://www.hkicc.org.hk/investor/fund_limit_c1_e.htm" target="_blank" rel="noopener noreferrer">投資者賠償基金</a>只涵蓋法定條件下的合資格申索，不賠一般投資損失。</p></section></main>{site_footer()}</body></html>'''


def update_navigation_and_home():
    nav_anchor = f'href="{BASE_PATH}news/">每週新聞</a>'
    nav_link = f'<a href="{BASE_PATH}brokers/">券商介紹</a>{nav_anchor}'
    for path in ROOT.rglob("*.html"):
        if path.name == "404.html" or "brokers" in path.relative_to(ROOT).parts:
            continue
        text = path.read_text(encoding="utf-8")
        if f'href="{BASE_PATH}brokers/"' not in text and nav_anchor in text:
            path.write_text(text.replace(nav_anchor, nav_link, 1), encoding="utf-8")
    home = ROOT / "index.html"
    text = home.read_text(encoding="utf-8")
    if 'id="broker-directory"' not in text:
        marker = '<section class="news-callout">'
        section = f'<section class="news-callout" id="broker-directory"><div><p class="eyebrow">開戶前先比較，不急着下單</p><h2>香港券商介紹與費用整理</h2><p>查看 IBKR、老虎證券、富途和 Webull 的香港法團、SFC 牌照、佣金與限制。部分頁面含本站邀請連結，並已清楚披露。</p></div><a class="button button-secondary" href="{BASE_PATH}brokers/">看四家券商資料 →</a></section>'
        if marker not in text:
            raise SystemExit("Could not find a safe insertion point in index.html")
        home.write_text(text.replace(marker, section + marker, 1), encoding="utf-8")


def validate_data():
    brokers = DATA.get("brokers", [])
    if len(brokers) != 4:
        raise ValueError("data/brokers.json 必須剛好有四家券商")
    slugs = set()
    for broker in brokers:
        for key in ("slug", "name", "title", "description", "lead", "entity", "license", "officialUrl", "ctaLabel"):
            if not broker.get(key):
                raise ValueError(f'券商資料缺少欄位：{key}')
        if broker["slug"] in slugs:
            raise ValueError(f'券商 slug 重複：{broker["slug"]}')
        slugs.add(broker["slug"])
        if not safe_https(broker["officialUrl"]):
            raise ValueError(f'官方網站必須使用 HTTPS：{broker["officialUrl"]}')
        if broker["referralUrl"] and not safe_https(broker["referralUrl"]):
            raise ValueError(f'邀請連結必須使用 HTTPS：{broker["referralUrl"]}')
        if not broker.get("sources"):
            raise ValueError(f'{broker["name"]} 必須列出參考資料')
        for source in broker["sources"]:
            if not safe_https(source["url"]):
                raise ValueError(f'參考資料必須使用 HTTPS：{source["url"]}')


def main():
    validate_data()
    out = ROOT / "brokers"
    out.mkdir(exist_ok=True)
    for broker in DATA["brokers"]:
        (out / f'{broker["slug"]}.html').write_text(render_profile(broker), encoding="utf-8")
    (out / "index.html").write_text(render_index(), encoding="utf-8")
    update_navigation_and_home()
    print(f'Generated {len(DATA["brokers"])} broker profiles and brokers/index.html.')


if __name__ == "__main__":
    main()
