from __future__ import annotations

import argparse
from pathlib import Path
import sys

from apps.keyword_intel_agent.src.loaders import load_gsc_csv, load_ads_csv
from apps.keyword_intel_agent.src.metrics import compute_overlap_segments, roi_signals
from apps.keyword_intel_agent.src.ai import fallback_rules


def build_markdown(gsc_path: str, ads_path: str) -> str:
    """
    Build the markdown recommendations for SEO ↔ SEM keyword intelligence.
    """
    gsc = load_gsc_csv(gsc_path)
    ads = load_ads_csv(ads_path)

    # Use the exact-match path (simpler & already proven working in the app)
    seg = compute_overlap_segments(gsc, ads, fuzzy=False, threshold=85)
    overlap = roi_signals(seg["overlap"])
    organic_only = seg["organic_only"]
    paid_only = seg["paid_only"]

    md = fallback_rules(overlap, organic_only, paid_only)
    return md


def main() -> None:
    parser = argparse.ArgumentParser(description="SEO ↔ SEM Keyword Intelligence CLI")
    parser.add_argument(
        "--gsc",
        required=True,
        help="Path to GSC CSV (page, query, clicks, impressions, ctr, position)",
    )
    parser.add_argument(
        "--ads",
        required=True,
        help="Path to Ads CSV (campaign, adgroup, keyword, clicks, cost, cpc, conversions)",
    )
    parser.add_argument(
        "--out",
        default="out/recommendations.md",
        help="Path to write markdown recommendations file.",
    )
    args = parser.parse_args()

    md = build_markdown(args.gsc, args.ads)

    # 1) Ensure output directory exists and write file as UTF-8
    out_path = Path(args.out)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(md, encoding="utf-8")

    # 2) Print markdown to stdout as UTF-8 bytes to avoid Windows cp1252 issues
    #    n8n's Execute Command will capture this as stdout.
    sys.stdout.buffer.write(md.encode("utf-8", errors="ignore"))
    sys.stdout.buffer.write(b"\n")
    sys.stdout.flush()


if __name__ == "__main__":
    main()