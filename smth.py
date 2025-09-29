#!/usr/bin/env python3
"""
Extract usable Font Awesome icon class names from a local fontawesome-all.min.css file.

Outputs:
- icon_list.txt (default): one icon name per line (e.g., fa-yin-yang)
- brands_list.txt: only brand icons (fa-github, etc.)
- solids_list.txt: only non-brand (solid/regular style) base names

Assumptions:
- You are using the HTML5 UP template that @imports 'fontawesome-all.min.css'
- File is located at: assets/css/fontawesome-all.min.css (adjust via --css if needed)

Why this script?
Simply guessing icon names wastes time. This parses what’s REALLY in your build, avoiding invisible (missing) icons.

Usage:
    python extract_icons.py
    python extract_icons.py --css assets/css/fontawesome-all.min.css --prefix fa-

Optional:
    python extract_icons.py --markdown table.md
    python extract_icons.py --json icons.json --csv icons.csv

Author: (Mentor) – Adapt and extend as you learn.
"""

import re
import argparse
from pathlib import Path
import json
import csv
from typing import Set, List

ICON_SELECTOR_RE = re.compile(r"\.(fa-[a-z0-9-]+)::?before")
# Some builds include style prefixes like .fab, .fas, .far, .fal – catch them too:
STYLE_SELECTOR_RE = re.compile(r"\.(fa[brsl]?[a-z]?-[a-z0-9-]+)::?before")


def load_css(css_path: Path) -> str:
    if not css_path.exists():
        raise FileNotFoundError(f"CSS file not found: {css_path}")
    return css_path.read_text(encoding="utf-8", errors="ignore")


def extract_icon_classes(css_text: str) -> Set[str]:
    """
    Extract raw classes (.fa-something:before). We also look for style prefixed forms (.fab-, .fas-, etc.).
    Return a set of class names like 'fa-code', 'fa-github', 'fab-github' if present.
    """
    matches_primary = ICON_SELECTOR_RE.findall(css_text)
    matches_style = STYLE_SELECTOR_RE.findall(css_text)
    return set(matches_primary) | set(matches_style)


def normalize_icons(raw: Set[str]) -> List[str]:
    """
    Normalize to base usable tokens for this template.
    Strategy:
      - Keep only classes that start with 'fa-' (base icons)
      - For style-specific (fab-github, fas-user), also derive the base 'fa-github' if present in font.
    NOTE: In Font Awesome 5, 'fab' = brands, 'fas' = solid, 'far' = regular (subset).
    We'll produce a final deduplicated list preferring 'fa-*'.
    """
    base_icons = set()
    brand_icons = set()

    for cls in raw:
        if cls.startswith("fa-"):
            # Already a base form (e.g., fa-code)
            base_icons.add(cls)
        else:
            # Possibly prefixed, e.g., fab-github
            if cls.startswith("fab-"):
                brand_name = cls.replace("fab-", "fa-")
                brand_icons.add(brand_name)
            elif cls.startswith(("fas-", "far-", "fal-")):
                solid_name = cls.split("-", 1)[1]
                solid_full = f"fa-{solid_name}"
                base_icons.add(solid_full)

    # Merge inferred brand icon base names into base set too,
    # but we keep a separate brand set to output brand listing.
    full_base = base_icons | brand_icons
    return sorted(full_base), sorted(brand_icons), sorted(full_base - brand_icons)


def write_list(path: Path, items: List[str]) -> None:
    path.write_text("\n".join(items) + "\n", encoding="utf-8")


def write_markdown_table(path: Path, all_icons: List[str], columns: int = 4) -> None:
    lines = ["| Icon Class | Preview |", "|-----------|---------|"]
    for icon in all_icons:
        # Preview cell requires manual inspection in a live HTML environment; here we just show code inline.
        lines.append(f"| `{icon}` | `<span class=\"icon {icon}\"></span>` |")
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_json(path: Path, all_icons: List[str], brands: List[str], solids: List[str]) -> None:
    data = {
        "count_total": len(all_icons),
        "count_brands": len(brands),
        "count_non_brands": len(solids),
        "icons": all_icons,
        "brands": brands,
        "non_brands": solids,
    }
    path.write_text(json.dumps(data, indent=2), encoding="utf-8")


def write_csv(path: Path, all_icons: List[str], brands: List[str]) -> None:
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["icon_class", "is_brand"])
        brand_set = set(brands)
        for icon in all_icons:
            writer.writerow([icon, "yes" if icon in brand_set else "no"])


def main():
    parser = argparse.ArgumentParser(description="Extract usable Font Awesome icons from a local CSS bundle.")
    parser.add_argument("--css", default="assets/css/fontawesome-all.min.css", help="Path to fontawesome-all.min.css")
    parser.add_argument("--out", default="icon_list.txt", help="Primary output list file")
    parser.add_argument("--brands-out", default="brands_list.txt", help="Brands-only output file")
    parser.add_argument("--solids-out", default="solids_list.txt", help="Non-brands (solid/regular) output file")
    parser.add_argument("--markdown", default="", help="Optional markdown table output file")
    parser.add_argument("--json", default="", help="Optional JSON output file")
    parser.add_argument("--csv", default="", help="Optional CSV output file")
    args = parser.parse_args()

    css_path = Path(args.css)
    css_text = load_css(css_path)

    raw_classes = extract_icon_classes(css_text)
    all_icons, brand_icons, non_brand_icons = normalize_icons(raw_classes)

    write_list(Path(args.out), all_icons)
    write_list(Path(args.brands_out), brand_icons)
    write_list(Path(args.solids_out), non_brand_icons)

    if args.markdown:
        write_markdown_table(Path(args.markdown), all_icons)

    if args.json:
        write_json(Path(args.json), all_icons, brand_icons, non_brand_icons)

    if args.csv:
        write_csv(Path(args.csv), all_icons, brand_icons)

    print(f"Total icons: {len(all_icons)}")
    print(f"Brands: {len(brand_icons)} | Non-brands: {len(non_brand_icons)}")
    print(f"Wrote: {args.out}, {args.brands_out}, {args.solids_out}")
    if args.markdown:
        print(f"Wrote markdown table: {args.markdown}")
    if args.json:
        print(f"Wrote JSON: {args.json}")
    if args.csv:
        print(f"Wrote CSV: {args.csv}")

if __name__ == "__main__":
    main()