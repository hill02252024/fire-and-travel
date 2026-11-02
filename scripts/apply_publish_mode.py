import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
BASE_URL = SITE["baseUrl"].rstrip("/")
BASE_PATH = SITE["basePath"]
PREVIOUS_URL = SITE.get("previousBaseUrl", "").rstrip("/")
PREVIOUS_PATH = SITE.get("previousBasePath", "")
INDEXABLE = bool(SITE.get("indexable", True))
ROBOTS_RE = re.compile(r'<meta\s+name=["\']robots["\'][^>]*>', re.IGNORECASE)
CANONICAL_RE = re.compile(r'(<link\s+rel=["\']canonical["\']\s+href=["\'])[^"\']*(["\'])', re.IGNORECASE)
OG_URL_RE = re.compile(r'(<meta\s+property=["\']og:url["\']\s+content=["\'])[^"\']*(["\'])', re.IGNORECASE)


def canonical_for(path: Path) -> str:
    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        route = "/"
    elif relative.endswith("/index.html"):
        route = "/" + relative[: -len("index.html")]
    else:
        route = "/" + relative
    return BASE_URL + route


def update_page(path: Path) -> None:
    text = path.read_text(encoding="utf-8")
    if PREVIOUS_URL and PREVIOUS_URL != BASE_URL:
        text = text.replace(PREVIOUS_URL, BASE_URL)
    if PREVIOUS_PATH and PREVIOUS_PATH != BASE_PATH:
        text = text.replace(PREVIOUS_PATH, BASE_PATH)

    if path.name != "404.html":
        canonical = canonical_for(path)
        if CANONICAL_RE.search(text):
            text = CANONICAL_RE.sub(lambda match: match.group(1) + canonical + match.group(2), text, count=1)
        else:
            text = text.replace("</head>", f'<link rel="canonical" href="{canonical}"></head>', 1)
        if OG_URL_RE.search(text):
            text = OG_URL_RE.sub(lambda match: match.group(1) + canonical + match.group(2), text, count=1)

    if INDEXABLE and path.name != "404.html":
        text = ROBOTS_RE.sub("", text)
    else:
        tag = '<meta name="robots" content="noindex,follow">'
        if ROBOTS_RE.search(text):
            text = ROBOTS_RE.sub(tag, text, count=1)
        else:
            text = text.replace("</head>", tag + "</head>", 1)

    path.write_text(text, encoding="utf-8")


def main() -> None:
    pages = sorted(ROOT.rglob("*.html"))
    pages = [path for path in pages if not any(part.startswith(".") for part in path.relative_to(ROOT).parts)]
    for page in pages:
        update_page(page)
    sitemap = ROOT / "sitemap.xml"
    if not INDEXABLE and sitemap.exists():
        sitemap.unlink()
    print(f"Applied {'indexable' if INDEXABLE else 'temporary noindex'} publishing mode to {len(pages)} HTML pages.")


if __name__ == "__main__":
    main()
