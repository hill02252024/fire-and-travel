from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
SITE = json.loads((ROOT / "data/site.json").read_text(encoding="utf-8"))
BASE = SITE["basePath"]
if not BASE.endswith("/"):
    BASE += "/"
BASE_URL = SITE["baseUrl"].rstrip("/")
INDEXABLE = bool(SITE.get("indexable", True))


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.title = ""
        self.in_title = False
        self.h1_count = 0
        self.links = []
        self.canonical = ""
        self.robots = ""
        self.jsonld = []
        self.in_jsonld = False
        self._jsonld_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self.in_title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical = attrs.get("href", "")
        if tag == "meta" and attrs.get("name", "").lower() == "robots":
            self.robots = attrs.get("content", "").lower()
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self.in_jsonld = True
            self._jsonld_text = []

    def handle_endtag(self, tag):
        if tag == "title":
            self.in_title = False
        if tag == "script" and self.in_jsonld:
            self.jsonld.append("".join(self._jsonld_text))
            self.in_jsonld = False

    def handle_data(self, data):
        if self.in_title:
            self.title += data.strip()
        if self.in_jsonld:
            self._jsonld_text.append(data)


def canonical_for(path):
    relative = path.relative_to(ROOT).as_posix()
    if relative == "index.html":
        route = "/"
    elif relative.endswith("/index.html"):
        route = "/" + relative[:-len("index.html")]
    else:
        route = "/" + relative
    return BASE_URL + route


def local_file(url_path):
    path = url_path.split("?", 1)[0].split("#", 1)[0]
    if path.rstrip("/") == BASE.rstrip("/"):
        target = ROOT / "index.html"
    elif path.startswith(BASE):
        target = ROOT / path[len(BASE):]
    else:
        return None
    if target.is_dir() or not target.suffix:
        if target.with_suffix(".html").exists():
            target = target.with_suffix(".html")
        else:
            target = target / "index.html"
    try:
        resolved = target.resolve()
        if ROOT.resolve() not in resolved.parents and resolved != ROOT.resolve():
            return None
    except OSError:
        return None
    return target


def main():
    pages = sorted(p for p in ROOT.rglob("*.html") if p.name != "404.html")
    errors = []
    titles = {}
    canonicals = set()
    for path in pages:
        rel = path.relative_to(ROOT).as_posix()
        parser = PageParser()
        parser.feed(path.read_text(encoding="utf-8"))
        if not parser.title:
            errors.append(f"{rel}: missing title")
        elif parser.title in titles:
            errors.append(f"{rel}: duplicate title with {titles[parser.title]}")
        titles[parser.title] = rel
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected one H1, found {parser.h1_count}")
        expected_canonical = canonical_for(path)
        if parser.canonical != expected_canonical:
            errors.append(f"{rel}: canonical {parser.canonical!r}, expected {expected_canonical!r}")
        canonicals.add(expected_canonical)
        is_noindex = "noindex" in parser.robots
        if INDEXABLE and is_noindex:
            errors.append(f"{rel}: indexable page is marked noindex")
        if not INDEXABLE and not is_noindex:
            errors.append(f"{rel}: temporary page must be noindex")
        for raw in parser.jsonld:
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD: {exc}")
        for href in parser.links:
            target = local_file(href)
            if target and not target.is_file():
                errors.append(f"{rel}: broken internal link {href}")

    sitemap_path = ROOT / "sitemap.xml"
    if INDEXABLE:
        try:
            tree = ET.parse(sitemap_path)
            locs = [e.text for e in tree.findall(".//{*}loc") if e.text]
            for loc in locs:
                if not loc.startswith(BASE_URL + "/"):
                    errors.append(f"sitemap.xml: URL outside site base: {loc}")
            if len(locs) != len(set(locs)):
                errors.append("sitemap.xml: duplicate URLs")
            missing = canonicals - set(locs)
            if missing:
                errors.append(f"sitemap.xml: missing canonical pages: {', '.join(sorted(missing)[:5])}")
        except (OSError, ET.ParseError) as exc:
            errors.append(f"sitemap.xml: {exc}")
    elif sitemap_path.exists() or (ROOT / "sitemap-pages.xml").exists():
        errors.append("temporary noindex site must not publish a sitemap")

    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"PASS: {len(pages)} HTML pages, unique titles, one H1 each, canonicals, noindex mode, local links, and sitemap valid.")


if __name__ == "__main__":
    main()
