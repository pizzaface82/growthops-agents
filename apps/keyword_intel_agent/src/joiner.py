from __future__ import annotations
import pandas as pd

def tidy_columns_for_display(df: pd.DataFrame) -> pd.DataFrame:
    preferred = [
        "page","query","keyword","kw_norm",
        "clicks_gsc","impressions","ctr","position",
        "clicks_ads","cost","cpc","conversions",
        "expected_ctr","ctr_gap","organic_potential",
        "high_cpc_flag","reduce_bid_flag","priority"
    ]
    cols = [c for c in preferred if c in df.columns]
    cols += [c for c in df.columns if c not in cols]
    return df[cols]
