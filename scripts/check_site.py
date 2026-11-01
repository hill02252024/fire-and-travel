from html.parser import HTMLParser
from pathlib import Path
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[1]
BASE = "/fire-and-travel/"
BASE_URL = "https://todays-tasks.com/fire-and-travel"


class PageParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.title = ""
        self.description = ""
        self.canonical = ""
        self.h1_count = 0
        self.links = []
        self.jsonld = []
        self._title = False
        self._jsonld = False
        self._jsonld_text = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "title":
            self._title = True
        if tag == "h1":
            self.h1_count += 1
        if tag == "meta" and attrs.get("name", "").lower() == "description":
            self.description = attrs.get("content", "")
        if tag == "link" and attrs.get("rel", "").lower() == "canonical":
            self.canonical = attrs.get("href", "")
        if tag == "a" and attrs.get("href"):
            self.links.append(attrs["href"])
        if tag == "script" and attrs.get("type") == "application/ld+json":
            self._jsonld = True
            self._jsonld_text = []

    def handle_endtag(self, tag):
        if tag == "title":
            self._title = False
        if tag == "script" and self._jsonld:
            self.jsonld.append("".join(self._jsonld_text))
            self._jsonld = False

    def handle_data(self, data):
        if self._title:
            self.title += data
        if self._jsonld:
            self._jsonld_text.append(data)


def local_file(url_path):
    path = url_path.split("?", 1)[0].split("#", 1)[0]
    if path == BASE or path == BASE[:-1]:
        return ROOT / "index.html"
    if not path.startswith(BASE):
        return None
    relative = path[len(BASE):]
    if not relative:
        return ROOT / "index.html"
    target = ROOT / relative
    if target.is_dir() or relative.endswith("/"):
        target = target / "index.html"
    elif not target.suffix:
        if target.with_suffix(".html").exists():
            target = target.with_suffix(".html")
        else:
            target = target / "index.html"
    return target


def main():
    errors = []
    pages = sorted(p for p in ROOT.rglob("*.html") if p.name != "404.html")
    titles = {}
    for path in pages:
        parser = PageParser()
        content = path.read_text(encoding="utf-8")
        parser.feed(content)
        rel = path.relative_to(ROOT).as_posix()
        if not parser.title.strip():
            errors.append(f"{rel}: missing title")
        if not parser.description.strip():
            errors.append(f"{rel}: missing meta description")
        if parser.h1_count != 1:
            errors.append(f"{rel}: expected one h1, found {parser.h1_count}")
        if not parser.canonical.startswith(BASE_URL):
            errors.append(f"{rel}: canonical outside site base: {parser.canonical}")
        if parser.title in titles:
            errors.append(f"{rel}: duplicate title with {titles[parser.title]}")
        titles[parser.title] = rel
        for raw in parser.jsonld:
            try:
                json.loads(raw)
            except json.JSONDecodeError as exc:
                errors.append(f"{rel}: invalid JSON-LD: {exc}")
        for href in parser.links:
            target = local_file(href)
            if target and not target.is_file():
                errors.append(f"{rel}: broken internal link {href}")
    try:
        tree = ET.parse(ROOT / "sitemap.xml")
        locs = [e.text for e in tree.findall(".//{*}loc")]
        for loc in locs:
            if not loc.startswith(BASE_URL + "/"):
                errors.append(f"sitemap.xml: URL outside site base: {loc}")
        if len(locs) != len(set(locs)):
            errors.append("sitemap.xml: duplicate URLs")
    except (OSError, ET.ParseError) as exc:
        errors.append(f"sitemap.xml: {exc}")
    if errors:
        print("\n".join(errors))
        sys.exit(1)
    print(f"PASS: {len(pages)} HTML pages, unique titles, one H1 each, local links and sitemap valid.")


if __name__ == "__main__":
    main()
