import json
from pathlib import Path
import shutil
import sys

SOURCE = Path(__file__).resolve().parents[1]
SITE = json.loads((SOURCE / "data/site.json").read_text(encoding="utf-8"))
PUBLISHED_FILES = ("index.html", "about.html", "disclaimer.html", "privacy.html", "404.html")
PUBLISHED_DIRS = ("assets", "calculators", "guides", "news")
EXCLUDED_NAMES = {"sitemap.xml", "sitemap-pages.xml", "robots.txt"}


def published_sources():
    files = [SOURCE / name for name in PUBLISHED_FILES if (SOURCE / name).is_file()]
    for directory in PUBLISHED_DIRS:
        root = SOURCE / directory
        if root.is_dir():
            files.extend(path for path in root.rglob("*") if path.is_file() and path.name not in EXCLUDED_NAMES)
    return sorted(files)


def main():
    if SITE.get("indexable", True):
        raise SystemExit("Refusing to mirror indexable content to the temporary subdirectory.")
    if SITE.get("adsEnabled", False):
        raise SystemExit("Refusing to mirror the temporary subdirectory with AdSense enabled.")
    if SITE.get("baseUrl", "").rstrip("/") != "https://todays-tasks.com/fire-and-travel":
        raise SystemExit("Temporary mirror is only allowed at todays-tasks.com/fire-and-travel.")
    if len(sys.argv) != 2:
        raise SystemExit("Usage: python3 scripts/sync_subdirectory.py /path/to/hill02252024.github.io")

    site_repo = Path(sys.argv[1]).resolve()
    if not (site_repo / ".git").exists():
        raise SystemExit("The destination must be the existing root website Git repository.")
    destination = site_repo / "fire-and-travel"
    manifest = site_repo / "scripts" / "fire-and-travel-manifest.json"
    previous = set()
    if manifest.exists():
        previous = set(json.loads(manifest.read_text(encoding="utf-8")).get("files", []))
    if destination.exists() and not previous:
        raise SystemExit("The destination already exists without a manifest; refusing to overwrite it.")

    source_files = published_sources()
    current = {source.relative_to(SOURCE).as_posix() for source in source_files}
    html_files = [source for source in source_files if source.suffix.lower() == ".html"]
    for page in html_files:
        text = page.read_text(encoding="utf-8")
        if '<meta name="robots" content="noindex,follow">' not in text and '<meta name="robots" content="noindex">' not in text:
            raise SystemExit(f"Refusing to publish an indexable page: {page.relative_to(SOURCE)}")
        if "adsbygoogle.js" in text:
            raise SystemExit(f"Refusing to publish AdSense code before the new domain is ready: {page.relative_to(SOURCE)}")

    for relative in sorted(current):
        target = destination / relative
        if target.exists() and relative not in previous:
            raise SystemExit(f"Refusing to overwrite unmanaged file: {target}")
    for relative in sorted(previous - current):
        stale = destination / relative
        if stale.is_file():
            stale.unlink()
    for source in source_files:
        relative = source.relative_to(SOURCE)
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, target)

    manifest.parent.mkdir(parents=True, exist_ok=True)
    manifest.write_text(json.dumps({"files": sorted(current)}, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(f"Synced {len(current)} static files to {destination}; all HTML pages are noindex.")


if __name__ == "__main__":
    main()
