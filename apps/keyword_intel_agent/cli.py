from __future__ import annotations
import argparse, os, pandas as pd
from apps.keyword_intel_agent.src.loaders import load_gsc_csv, load_ads_csv
from apps.keyword_intel_agent.src.metrics import add_kw_norm_cols, compute_overlap_segments, roi_signals
from apps.keyword_intel_agent.src.ai import fallback_rules

def run(gsc_path: str, ads_path: str, out_path: str):
    gsc = load_gsc_csv(gsc_path)
    ads = load_ads_csv(ads_path)
    gsc, ads = add_kw_norm_cols(gsc, ads)
    seg = compute_overlap_segments(gsc, ads, fuzzy=True, threshold=90)
    overlap = roi_signals(seg["overlap"]) if not seg["overlap"].empty else seg["overlap"]
    md = fallback_rules(overlap, seg["organic_only"], seg["paid_only"])
    os.makedirs(os.path.dirname(out_path) or ".", exist_ok=True)
    with open(out_path, "w", encoding="utf-8") as f:
        f.write(md)
    print(f"✅ Wrote recommendations to {out_path}")

if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--gsc", required=True)
    ap.add_argument("--ads", required=True)
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    run(args.gsc, args.ads, args.out)
