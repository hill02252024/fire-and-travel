from datetime import date
from html import escape
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
DATA = json.loads((ROOT / "data/guides.json").read_text(encoding="utf-8"))
BASE_URL = SITE["baseUrl"].rstrip("/")
BASE_PATH = SITE["basePath"].rstrip("/") + "/"
TODAY = date.today().isoformat()
ANCHOR = re.compile(r'<a href="([^"]+)"(?:\s+target="([^"]*)")?(?:\s+rel="([^"]*)")?>([^<]*)</a>')


def inline_html(value):
    out = []
    start = 0
    for match in ANCHOR.finditer(value):
        out.append(escape(value[start:match.start()]))
        href, target, rel, label = match.groups()
        attrs = f' target="{escape(target, quote=True)}"' if target else ""
        if target == "_blank" and not rel:
            rel = "noopener noreferrer"
        attrs += f' rel="{escape(rel, quote=True)}"' if rel else ""
        out.append(f'<a href="{escape(href, quote=True)}"{attrs}>{escape(label)}</a>')
        start = match.end()
    out.append(escape(value[start:]))
    return "".join(out)


def json_ld(guide, canonical):
    return json.dumps({
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": guide["title"],
        "description": guide["description"],
        "datePublished": DATA["published"],
        "dateModified": DATA["published"],
        "inLanguage": "zh-HK",
        "author": {"@type": "Organization", "name": "財與遠方編輯部"},
        "publisher": {"@type": "Organization", "name": SITE["name"]},
        "mainEntityOfPage": canonical,
    }, ensure_ascii=False, separators=(",", ":"))


def render_section(section):
    content = [f'<section><h2>{escape(section["heading"])}</h2>']
    content.extend(f'<p>{inline_html(paragraph)}</p>' for paragraph in section.get("paragraphs", []))
    bullets = section.get("bullets", [])
    if bullets:
        content.append("<ul>")
        content.extend(f"<li>{inline_html(item)}</li>" for item in bullets)
        content.append("</ul>")
    content.append("</section>")
    return "".join(content)


def render_guide(guide):
    canonical = f'{BASE_URL}/guides/{guide["slug"]}.html'
    published = DATA["published"]
    publisher_id = SITE.get("adsensePublisher", "")
    adsense = (
        f'<meta name="google-adsense-account" content="{escape(publisher_id, quote=True)}">'
        f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={escape(publisher_id, quote=True)}" crossorigin="anonymous"></script>'
        if publisher_id else ""
    )
    sections = "".join(render_section(section) for section in guide["sections"])
    faqs = "".join(
        f'<section><h3>{escape(item["question"])}</h3><p>{escape(item["answer"])}</p></section>'
        for item in guide.get("faqs", [])
    )
    sources = "".join(
        f'<li><a href="{escape(source["url"], quote=True)}" target="_blank" rel="noopener noreferrer">{escape(source["title"])}</a></li>'
        for source in guide.get("sources", [])
    )
    related = "".join(
        f'<a class="text-link" href="{escape(item["url"], quote=True)}">{escape(item["title"])} →</a>'
        for item in guide.get("related", [])
    )
    return f'''<!doctype html>
<html lang="zh-HK"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1"><title>{escape(guide["title"])}｜財與遠方</title><meta name="description" content="{escape(guide["description"], quote=True)}"><link rel="canonical" href="{escape(canonical, quote=True)}"><meta property="og:type" content="article"><meta property="og:title" content="{escape(guide["title"], quote=True)}｜財與遠方"><meta property="og:description" content="{escape(guide["description"], quote=True)}"><meta property="og:url" content="{escape(canonical, quote=True)}">{adsense}<link rel="stylesheet" href="{BASE_PATH}assets/site.css"><script type="application/ld+json">{json_ld(guide, canonical)}</script></head><body><header class="site-header"><a class="brand" href="{BASE_PATH}"><span class="brand-mark">財</span><span>財與遠方</span></a><nav aria-label="主要導覽"><a href="{BASE_PATH}calculators/fire.html">財務自由試算</a><a href="{BASE_PATH}calculators/travel.html">旅行預算</a><a href="{BASE_PATH}guides/" aria-current="page">實用指南</a><a href="{BASE_PATH}news/">每週新聞</a></nav></header><main class="article"><p class="breadcrumb"><a href="{BASE_PATH}">首頁</a>　/　<a href="{BASE_PATH}guides/">實用指南</a>　/　{escape(guide["title"])}</p><p class="eyebrow">{escape(guide["eyebrow"])} · 更新於 {published}</p><h1>{escape(guide["title"])}</h1><p class="lead">{escape(guide["lead"])}</p><p class="fine-print">以下為一般教育資訊和情境示例，不是個人化投資或稅務建議。數字和規則會因產品、個人情況及法規而異，請以最新官方資料和產品文件為準。</p>{sections}<section><h2>常見問題</h2>{faqs}</section><section><h2>參考資料</h2><p>以下官方教育與監管資料供讀者進一步核對；引用不代表機構推薦任何投資產品。</p><ul>{sources}</ul></section><section class="callout"><h2>繼續規劃</h2><p>{related}</p><p><a href="{BASE_PATH}guides/">返回全部理財與投資指南 →</a></p></section></main><footer class="site-footer"><div><a class="brand" href="{BASE_PATH}"><span class="brand-mark">財</span><span>財與遠方</span></a><p>用數字規劃自由，用預算留住遠方。</p></div><nav aria-label="頁尾導覽"><a href="{BASE_PATH}about.html">關於本站</a><a href="{BASE_PATH}disclaimer.html">免責聲明</a><a href="{BASE_PATH}privacy.html">私隱政策</a><a href="{BASE_PATH}news/">每週新聞</a></nav><small>© 2026 財與遠方</small></footer></body></html>'''


def render_cards():
    cards = []
    for guide in DATA["guides"]:
        url = f'{BASE_PATH}guides/{guide["slug"]}.html'
        cards.append(
            f'<article class="card"><p class="eyebrow">{escape(guide["eyebrow"])}</p>'
            f'<h2><a href="{url}">{escape(guide["title"])}</a></h2>'
            f'<p>{escape(guide["lead"])}</p><a class="text-link" href="{url}">閱讀指南 →</a></article>'
        )
    return (
        '<section class="section-block" id="evergreen-guides"><div class="section-head">'
        '<div><p class="eyebrow">常青理財指南</p><h2>香港理財與投資：10 篇常青指南</h2></div>'
        '<p>從日常預算到投資風險，逐步建立自己的判斷框架。</p></div>'
                f'<div class="card-grid">{"".join(cards)}</div></section>'
    )


def main():
    for guide in DATA["guides"]:
        path = ROOT / "guides" / f'{guide["slug"]}.html'
        path.write_text(render_guide(guide), encoding="utf-8")
    index_path = ROOT / "guides/index.html"
    index = index_path.read_text(encoding="utf-8")
    section = render_cards()
    pattern = re.compile(r'<section class="section-block" id="evergreen-guides">.*?</section>')
    if pattern.search(index):
        index = pattern.sub(lambda _: section, index, count=1)
    else:
        marker = '<section class="callout">'
        if marker not in index:
            raise SystemExit("Could not find a safe insertion point in guides/index.html")
        index = index.replace(marker, section + marker, 1)
    index_path.write_text(index, encoding="utf-8")
    print(f'Generated {len(DATA["guides"])} evergreen guides and refreshed guides/index.html.')


if __name__ == "__main__":
    main()
