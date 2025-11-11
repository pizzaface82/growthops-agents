from __future__ import annotations
import pandas as pd

def load_gsc_csv(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer)
    df = df.copy()
    df["ctr"] = df["ctr"].astype(float)
    df["position"] = df["position"].astype(float)
    return df

def load_ads_csv(path_or_buffer) -> pd.DataFrame:
    df = pd.read_csv(path_or_buffer)
    df = df.copy()
    for col in ["clicks","conversions"]:
        if col in df.columns: df[col] = df[col].astype(int)
    for col in ["cost","cpc"]:
        if col in df.columns: df[col] = df[col].astype(float)
    return df
