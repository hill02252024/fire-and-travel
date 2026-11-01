from datetime import date, datetime
from html import escape
from pathlib import Path
import json
import re
import subprocess
from urllib.parse import urlparse

ROOT = Path(__file__).resolve().parents[1]
CONFIG = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
BASE_URL = CONFIG["baseUrl"].rstrip("/")
BASE_PATH = CONFIG["basePath"].rstrip("/") + "/"
BRAND = CONFIG["name"]
PUB = CONFIG["adsensePublisher"]
NEWS_FILE = ROOT / "data/news.json"


def safe_url(value):
    parsed = urlparse(value)
    return parsed.scheme == "https" and bool(parsed.netloc)


def last_modified(relative_path):
    try:
        pending = subprocess.check_output(
            ["git", "status", "--porcelain", "--untracked-files=all", "--", relative_path],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if pending:
            return date.today().isoformat()
        value = subprocess.check_output(
            ["git", "log", "-1", "--format=%cs", "--", relative_path],
            cwd=ROOT,
            text=True,
            stderr=subprocess.DEVNULL,
        ).strip()
        if value:
            return value
    except (OSError, subprocess.CalledProcessError):
        pass
    return date.today().isoformat()


def page_head(title, description, canonical, page_type="website", article_json=None):
    social = f'<meta property="og:type" content="{escape(page_type)}"><meta property="og:title" content="{escape(title)}"><meta property="og:description" content="{escape(description)}"><meta property="og:url" content="{escape(canonical)}">'
    schema = ""
    if article_json:
        schema = '<script type="application/ld+json">' + json.dumps(article_json, ensure_ascii=False, separators=(",", ":")) + "</script>"
    return f'''<!doctype html>
<html lang="zh-HK"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(title)}</title><meta name="description" content="{escape(description)}"><link rel="canonical" href="{escape(canonical)}">{social}<meta name="google-adsense-account" content="{PUB}"><script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={PUB}" crossorigin="anonymous"></script>{schema}<link rel="stylesheet" href="{BASE_PATH}assets/site.css"></head>'''


def site_header(active="news"):
    links = [
        ("財務自由試算", "calculators/fire.html", "fire"),
        ("旅行預算", "calculators/travel.html", "travel"),
        ("實用指南", "guides/", "guides"),
        ("每週新聞", "news/", "news"),
    ]
    nav = "".join(
        f'<a href="{BASE_PATH}{path}"' + (f' aria-current="page"' if key == active else "") + f'>{escape(label)}</a>'
        for label, path, key in links
    )
    return f'<header class="site-header"><a class="brand" href="{BASE_PATH}"><span class="brand-mark">財</span><span>{escape(BRAND)}</span></a><nav aria-label="主要導覽">{nav}</nav></header>'


def site_footer():
    return f'''<footer class="site-footer"><div><a class="brand" href="{BASE_PATH}"><span class="brand-mark">財</span><span>{escape(BRAND)}</span></a><p>用數字規劃自由，用預算留住遠方。</p></div><nav aria-label="頁尾導覽"><a href="{BASE_PATH}about.html">關於本站</a><a href="{BASE_PATH}disclaimer.html">免責聲明</a><a href="{BASE_PATH}privacy.html">私隱政策</a></nav><small>© {date.today().year} {escape(BRAND)}</small></footer>'''


def news_card(entry):
    published = escape(entry["date"])
    headline = escape(entry["title"])
    slug = escape(entry["date"])
    story_count = len(entry["items"])
    return f'''<article class="article-card"><p class="eyebrow">WEEKLY BRIEF · {published} · {story_count} 則</p><h2><a href="{BASE_PATH}news/{slug}.html">{headline}</a></h2><p>{escape(entry.get("summary", "本週香港與全球財務、退休和旅行消息整理。"))}</p><a class="text-link" href="{BASE_PATH}news/{slug}.html">閱讀摘要 →</a></article>'''


def build_news_article(entry):
    article_date = date.fromisoformat(entry["date"])
    title = f'{entry["title"]}｜財與遠方'
    canonical = f'{BASE_URL}/news/{article_date.isoformat()}.html'
    description = entry.get("summary", "香港與全球財務、退休和旅行每週新聞摘要，附原始來源和發布日期。")[:300]
    schema = {
        "@context": "https://schema.org",
        "@type": "NewsArticle",
        "headline": entry["title"],
        "datePublished": article_date.isoformat(),
        "dateModified": article_date.isoformat(),
        "inLanguage": "zh-HK",
        "author": {"@type": "Organization", "name": f"{BRAND}自動新聞摘要"},
        "publisher": {"@type": "Organization", "name": BRAND},
        "mainEntityOfPage": canonical,
    }
    cards = []
    for number, item in enumerate(entry["items"], start=1):
        source_url = item["url"]
        if not safe_url(source_url):
            raise ValueError(f'新聞來源必須是 HTTPS 網址：{source_url}')
        cards.append(
            f'''<section class="news-card"><p class="eyebrow">消息 {number} · 原文發布：{escape(item["published"])}</p><h2>{escape(item["headline"])}</h2><p><strong>發生了甚麼：</strong>{escape(item["what"])}</p><p><strong>為甚麼值得留意：</strong>{escape(item["why"])}</p><p>來源：<a href="{escape(source_url, quote=True)}" target="_blank" rel="noopener noreferrer">{escape(item["source"])}</a></p></section>'''
        )
    body = "".join(cards)
    return f'''{page_head(title, description, canonical, "article", schema)}<body>{site_header()}<main class="article-page"><p class="breadcrumb"><a href="{BASE_PATH}">首頁</a>　/　<a href="{BASE_PATH}news/">每週新聞</a>　/　{article_date.isoformat()}</p><p class="eyebrow">每週焦點 · 自動整理：{article_date.isoformat()}</p><h1>{escape(entry["title"])}</h1><p class="lead">{escape(entry.get("summary", "本週財務、退休和旅行消息摘要。"))}</p>{body}<div class="article-callout">本文只作新聞導讀，不是個人化投資、稅務或旅遊建議。消息可能更新，請以原始來源為準；本站不提供買入或賣出指示。</div></main>{site_footer()}</body></html>'''


def validate_entry(entry):
    if not re.fullmatch(r"20\d\d-\d\d-\d\d", str(entry.get("date", ""))):
        raise ValueError("每則每週摘要必須有 YYYY-MM-DD 日期")
    date.fromisoformat(entry["date"])
    if not entry.get("title") or not entry.get("summary"):
        raise ValueError("每週摘要必須有 title 和 summary")
    items = entry.get("items")
    if not isinstance(items, list) or not 1 <= len(items) <= 3:
        raise ValueError("每週摘要必須有 1 至 3 則消息")
    for item in items:
        for field in ("headline", "source", "url", "published", "what", "why"):
            if not item.get(field):
                raise ValueError(f"新聞項目缺少必要欄位：{field}")
        date.fromisoformat(item["published"])
        if not safe_url(item["url"]):
            raise ValueError(f'新聞來源必須是 HTTPS 網址：{item["url"]}')


def build_sitemap():
    files = sorted(
        p for p in ROOT.rglob("*.html")
        if ".git" not in p.parts and p.name != "404.html"
    )
    entries = []
    for path in files:
        relative = path.relative_to(ROOT)
        if relative.as_posix() == "index.html":
            url = BASE_URL + "/"
        elif relative.name == "index.html":
            url = BASE_URL + "/" + relative.parent.as_posix().rstrip("/") + "/"
        else:
            url = BASE_URL + "/" + relative.as_posix()
        entries.append((url, last_modified(relative.as_posix())))
    rows = "\n".join(
        f"  <url><loc>{escape(url)}</loc><lastmod>{modified}</lastmod></url>"
        for url, modified in entries
    )
    (ROOT / "sitemap.xml").write_text(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
        + rows + "\n</urlset>\n",
        encoding="utf-8",
    )


def main():
    entries = json.loads(NEWS_FILE.read_text(encoding="utf-8"))
    if not isinstance(entries, list):
        raise ValueError("data/news.json 必須是陣列")
    seen = set()
    for entry in entries:
        validate_entry(entry)
        if entry["date"] in seen:
            raise ValueError(f'每週日期重複：{entry["date"]}')
        seen.add(entry["date"])
    entries.sort(key=lambda item: item["date"], reverse=True)
    (ROOT / "news").mkdir(exist_ok=True)
    for entry in entries:
        article = build_news_article(entry)
        (ROOT / "news" / f'{entry["date"]}.html').write_text(article + "\n", encoding="utf-8")
    cards = "".join(news_card(entry) for entry in entries)
    if not cards:
        cards = '<article class="article-card"><p class="eyebrow">首篇摘要將於星期六更新</p><h2>本週新聞尚未發布</h2><p>自動編輯會先核對來源和日期，再決定是否更新。本站不會為了維持更新頻率而編造新聞。</p></article>'
    title = "財務與旅行每週新聞摘要｜財與遠方"
    description = "每週整理香港及全球與個人理財、退休規劃和旅行相關的重要消息，附發布日期和原始來源連結。"
    canonical = BASE_URL + "/news/"
    page = f'''{page_head(title, description, canonical)}<body>{site_header()}<main><section class="page-heading"><p class="breadcrumb"><a href="{BASE_PATH}">首頁</a>　/　每週新聞</p><p class="eyebrow">每星期六 · 香港理財與旅行新聞</p><h1>財務與旅行每週新聞</h1><p class="lead">摘要香港及全球與個人理財、退休和旅行相關的重要消息。每篇標示發布日期、原文來源和自動整理；新聞不等於投資建議。</p></section><section class="content-panel"><h2>發布原則</h2><ul><li>優先引用監管機構、政府、交易所或原始發布者。</li><li>只摘要可核對的消息，附原文連結和日期，不複製大段內容。</li><li>每週最多三則；沒有可靠、值得整理的新消息時就略過。</li><li>不根據短期新聞預測價格，不提供買入或賣出指示。</li></ul></section><section class="article-list" id="news-list">{cards}</section><div class="article-callout">新聞整理只作資訊導讀。請閱讀原始公告，並自行核對金融產品、稅務和旅行規定。</div></main>{site_footer()}</body></html>'''
    (ROOT / "news" / "index.html").write_text(page + "\n", encoding="utf-8")
    build_sitemap()
    print(f"Generated {len(entries)} weekly briefs and sitemap.")


if __name__ == "__main__":
    main()
