"""
Stáhne oficiální CZ/SK XML strom kategorií Heureky a připraví lokální
referenční JSON/CSV pro validaci CATEGORYTEXT.

Vstup:
- config/heureka_category_mapping.json

Výstup:
- data/reference/heureka/heureka_cz_categories.xml
- data/reference/heureka/heureka_sk_categories.xml
- data/reference/heureka/heureka_cz_categories.json
- data/reference/heureka/heureka_sk_categories.json
- data/reference/heureka/heureka_*_categories.csv
"""
import csv
import json
import sys
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONFIG_PATH = ROOT / "config" / "heureka_category_mapping.json"
REFERENCE_DIR = ROOT / "data" / "reference" / "heureka"


def normalize_path(value: str) -> str:
    parts = [" ".join(part.split()) for part in value.split("|")]
    return " | ".join(part for part in parts if part)


def download(url: str, out: Path) -> None:
    req = urllib.request.Request(url, headers={"User-Agent": "Lakma-Sidolux-feed/1.0"})
    with urllib.request.urlopen(req, timeout=60) as resp:
        out.write_bytes(resp.read())


def parse_categories(xml_path: Path, market: str, source_url: str) -> list[dict]:
    root = ET.parse(xml_path).getroot()
    rows = []
    for category in root.iter("CATEGORY"):
        category_id = (category.findtext("CATEGORY_ID") or "").strip()
        name = " ".join((category.findtext("CATEGORY_NAME") or "").split())
        full = category.findtext("CATEGORY_FULLNAME")
        if not full:
            continue
        path = normalize_path(full)
        rows.append(
            {
                "market": market,
                "category_id": category_id,
                "name": name,
                "path": path,
                "depth": path.count("|") + 1,
                "source_url": source_url,
            }
        )
    rows.sort(key=lambda row: row["path"])
    return rows


def write_json(path: Path, payload: dict) -> None:
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")


def write_csv(path: Path, rows: list[dict]) -> None:
    fields = ["market", "category_id", "name", "path", "depth", "source_url"]
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fields, delimiter=";")
        writer.writeheader()
        writer.writerows(rows)


def main() -> None:
    sys.stdout.reconfigure(encoding="utf-8")
    config = json.loads(CONFIG_PATH.read_text(encoding="utf-8"))
    REFERENCE_DIR.mkdir(parents=True, exist_ok=True)

    generated_at = datetime.now().isoformat(timespec="seconds")
    for market, url in config["category_sources"].items():
        xml_path = REFERENCE_DIR / f"heureka_{market}_categories.xml"
        json_path = REFERENCE_DIR / f"heureka_{market}_categories.json"
        csv_path = REFERENCE_DIR / f"heureka_{market}_categories.csv"

        print(f"Stahuji {market.upper()}: {url}")
        download(url, xml_path)
        rows = parse_categories(xml_path, market.upper(), url)
        payload = {
            "market": market.upper(),
            "source_url": url,
            "generated_at": generated_at,
            "count": len(rows),
            "categories": rows,
        }
        write_json(json_path, payload)
        write_csv(csv_path, rows)
        print(f"  OK: {len(rows)} kategorií -> {json_path.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
