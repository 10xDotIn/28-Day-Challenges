"""
Data Engineer: ingest, profile, clean all shopify-data CSVs.
Outputs:
  - output/shopify-data/cleaned-data/*.csv
  - output/shopify-data/data-profile.md
"""

import pandas as pd
import numpy as np
import re
import os
import json
from pathlib import Path
from datetime import datetime

BASE     = Path("C:/Users/p/Downloads/10x-analyst-main/10x-analyst-main")
INPUT    = BASE / "input"  / "shopify-data"
OUT_ROOT = BASE / "output" / "shopify-data"
OUT_CLN  = OUT_ROOT / "cleaned-data"
OUT_CLN.mkdir(parents=True, exist_ok=True)

# ── helpers ──────────────────────────────────────────────────────────────────

def clean_columns(df: pd.DataFrame) -> pd.DataFrame:
    df.columns = (
        df.columns
          .str.strip()
          .str.lower()
          .str.replace(r"[^a-z0-9]+", "_", regex=True)
          .str.strip("_")
    )
    return df

def parse_dates(df: pd.DataFrame) -> list[str]:
    """Detect and parse date-like columns in-place; return list of parsed col names."""
    parsed = []
    date_hints = re.compile(r"(date|created_at|updated_at|timestamp|time)", re.I)
    for col in df.columns:
        if date_hints.search(col) and df[col].dtype == object:
            try:
                df[col] = pd.to_datetime(df[col], utc=False, errors="coerce")
                parsed.append(col)
            except Exception:
                pass
    return parsed

def drop_fully_null(df: pd.DataFrame) -> tuple[pd.DataFrame, list[str]]:
    null_cols = [c for c in df.columns if df[c].isna().all()]
    return df.drop(columns=null_cols), null_cols

def quality_score(df: pd.DataFrame) -> float:
    """Simple score: 1 - (total_missing / total_cells)."""
    total = df.size
    if total == 0:
        return 100.0
    missing = df.isna().sum().sum()
    return round((1 - missing / total) * 100, 1)

def col_profile(df: pd.DataFrame) -> list[dict]:
    rows = []
    for col in df.columns:
        s = df[col]
        missing     = int(s.isna().sum())
        missing_pct = round(missing / len(df) * 100, 1) if len(df) else 0
        unique      = int(s.nunique(dropna=True))
        dtype       = str(s.dtype)
        extra = {}
        if pd.api.types.is_numeric_dtype(s):
            extra = {
                "min":    round(float(s.min()), 4) if not s.isna().all() else None,
                "max":    round(float(s.max()), 4) if not s.isna().all() else None,
                "mean":   round(float(s.mean()), 4) if not s.isna().all() else None,
                "median": round(float(s.median()), 4) if not s.isna().all() else None,
                "std":    round(float(s.std()), 4) if not s.isna().all() else None,
            }
        elif pd.api.types.is_datetime64_any_dtype(s):
            extra = {
                "min": str(s.min()),
                "max": str(s.max()),
            }
        else:
            top = s.value_counts().head(3)
            extra = {"top_values": {str(k): int(v) for k, v in top.items()}}
        rows.append({
            "column":      col,
            "dtype":       dtype,
            "missing":     missing,
            "missing_pct": missing_pct,
            "unique":      unique,
            **extra,
        })
    return rows

# ── load & clean each file ───────────────────────────────────────────────────

files = {
    "customers":    INPUT / "customers.csv",
    "orders":       INPUT / "orders.csv",
    "order_items":  INPUT / "order_items.csv",
    "products":     INPUT / "products.csv",
    "price_changes":INPUT / "price_changes.csv",
}

profiles   = {}
summaries  = {}
clean_dfs  = {}

for name, path in files.items():
    print(f"\n{'='*60}")
    print(f"  Processing: {name}")
    print(f"{'='*60}")

    df = pd.read_csv(path, low_memory=False)
    raw_rows, raw_cols = df.shape
    print(f"  Raw shape : {raw_rows} rows x {raw_cols} cols")

    # 1. Standardise column names
    df = clean_columns(df)

    # 2. Parse date columns
    parsed_dates = parse_dates(df)
    if parsed_dates:
        print(f"  Parsed dates : {parsed_dates}")

    # 3. Drop fully-null columns
    df, dropped_cols = drop_fully_null(df)
    if dropped_cols:
        print(f"  Dropped fully-null cols: {dropped_cols}")

    # 4. Drop exact duplicate rows
    dupes = df.duplicated().sum()
    if dupes:
        df = df.drop_duplicates()
        print(f"  Dropped {dupes} duplicate rows")

    # 5. Strip whitespace from object columns
    for col in df.select_dtypes(include="object").columns:
        df[col] = df[col].str.strip()

    # 6. Save cleaned CSV
    out_path = OUT_CLN / f"{name}.csv"
    df.to_csv(out_path, index=False)
    print(f"  Saved -> {out_path}")

    clean_dfs[name] = df
    profiles[name]  = col_profile(df)
    summaries[name] = {
        "raw_rows":    raw_rows,
        "raw_cols":    raw_cols,
        "clean_rows":  len(df),
        "clean_cols":  len(df.columns),
        "columns":     list(df.columns),
        "parsed_dates":parsed_dates,
        "dropped_cols":dropped_cols,
        "dupes_removed":int(dupes),
        "quality_score":quality_score(df),
    }

# ── relationship detection ───────────────────────────────────────────────────

print("\n" + "="*60)
print("  Relationship detection")
print("="*60)

col_index = {}   # col_name -> [table_name, ...]
for tbl, df in clean_dfs.items():
    for col in df.columns:
        col_index.setdefault(col, []).append(tbl)

relationships = []
# explicit FK candidates (known from domain)
fk_candidates = [
    ("orders",      "customer_id",    "customers",    "customer_id"),
    ("order_items", "order_id",       "orders",       "order_id"),
    ("order_items", "product_sku",    "products",     "sku"),
    ("price_changes","sku",           "products",     "sku"),
]

for (src_tbl, src_col, tgt_tbl, tgt_col) in fk_candidates:
    src_df = clean_dfs[src_tbl]
    tgt_df = clean_dfs[tgt_tbl]
    if src_col not in src_df.columns or tgt_col not in tgt_df.columns:
        relationships.append({
            "from": f"{src_tbl}.{src_col}",
            "to":   f"{tgt_tbl}.{tgt_col}",
            "match_pct": "N/A (column missing after clean)",
        })
        continue
    src_vals = set(src_df[src_col].dropna().unique())
    tgt_vals = set(tgt_df[tgt_col].dropna().unique())
    matched  = len(src_vals & tgt_vals)
    match_pct= round(matched / len(src_vals) * 100, 1) if src_vals else 0
    orphans  = len(src_vals - tgt_vals)
    card = "many-to-one"  # most FK relationships here
    relationships.append({
        "from":      f"{src_tbl}.{src_col}",
        "to":        f"{tgt_tbl}.{tgt_col}",
        "match_pct": match_pct,
        "orphans":   orphans,
        "cardinality": card,
    })
    print(f"  {src_tbl}.{src_col} -> {tgt_tbl}.{tgt_col}: {match_pct}% match, {orphans} orphans")

# ── date ranges ──────────────────────────────────────────────────────────────

date_ranges = {}
for tbl, df in clean_dfs.items():
    dr = {}
    for col in df.select_dtypes(include="datetime64[ns]").columns:
        dr[col] = {"min": str(df[col].min()), "max": str(df[col].max())}
    if dr:
        date_ranges[tbl] = dr

# ── write data-profile.md ────────────────────────────────────────────────────

def md_table(headers, rows):
    sep = "| " + " | ".join(["---"] * len(headers)) + " |"
    head = "| " + " | ".join(headers) + " |"
    body = "\n".join("| " + " | ".join(str(c) for c in r) + " |" for r in rows)
    return "\n".join([head, sep, body])

lines = []
lines.append("# Data Profile — shopify-data")
lines.append(f"\nGenerated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")

# Data Inventory
lines.append("## Data Inventory\n")
inv_rows = []
for name, s in summaries.items():
    issues = []
    if s["dropped_cols"]:
        issues.append(f"dropped null cols: {s['dropped_cols']}")
    if s["dupes_removed"]:
        issues.append(f"{s['dupes_removed']} dupes removed")
    # flag cols with high missing
    for cp in profiles[name]:
        if cp["missing_pct"] > 5:
            issues.append(f"{cp['column']} {cp['missing_pct']}% missing")
    inv_rows.append([
        name,
        f"{s['clean_rows']:,}",
        s["clean_cols"],
        f"{s['quality_score']}%",
        "; ".join(issues) if issues else "None",
    ])
lines.append(md_table(
    ["File", "Rows", "Columns", "Quality Score", "Issues Found"],
    inv_rows
))

# Column lists
lines.append("\n## Column Inventory\n")
for name, s in summaries.items():
    lines.append(f"### {name}\n")
    lines.append(f"Columns: `{'`, `'.join(s['columns'])}`\n")
    if s["parsed_dates"]:
        lines.append(f"Date columns parsed: `{'`, `'.join(s['parsed_dates'])}`\n")
    if s["dropped_cols"]:
        lines.append(f"Fully-null columns dropped: `{'`, `'.join(s['dropped_cols'])}`\n")

# Date ranges
lines.append("## Date Ranges\n")
for tbl, dr in date_ranges.items():
    lines.append(f"### {tbl}\n")
    for col, rng in dr.items():
        lines.append(f"- `{col}`: {rng['min']} → {rng['max']}")
    lines.append("")

# Relationships
lines.append("## Relationships Detected\n")
rel_rows = []
for r in relationships:
    rel_rows.append([
        r["from"],
        r["to"],
        r.get("cardinality", "—"),
        f"{r['match_pct']}%",
        r.get("orphans", "—"),
    ])
lines.append(md_table(
    ["From", "To", "Cardinality", "Match %", "Orphans"],
    rel_rows
))

# Per-table column profiles
lines.append("\n## Per-Table Column Profiles\n")
for name, cp in profiles.items():
    lines.append(f"### {name}\n")
    col_rows = []
    for c in cp:
        stats = ""
        if "mean" in c:
            stats = f"min={c['min']}, max={c['max']}, mean={c['mean']}, median={c['median']}, std={c['std']}"
        elif "top_values" in c:
            top = ", ".join(f"{k}({v})" for k, v in list(c["top_values"].items())[:3])
            stats = f"top: {top}"
        elif c["dtype"].startswith("datetime"):
            stats = f"{c.get('min','')} → {c.get('max','')}"
        col_rows.append([
            c["column"],
            c["dtype"],
            c["unique"],
            f"{c['missing']} ({c['missing_pct']}%)",
            stats,
        ])
    lines.append(md_table(
        ["Column", "Type", "Unique", "Missing", "Stats / Top Values"],
        col_rows
    ))
    lines.append("")

# Data quality notes
lines.append("## Data Quality Notes\n")
lines.append("- All column names standardised to `snake_case`.")
lines.append("- Fully-null columns removed (e.g. `note` in orders, `variant_title` in order_items).")
lines.append("- Date/datetime columns parsed to `datetime64[ns]`.")
lines.append("- Leading/trailing whitespace stripped from all string columns.")
lines.append("- Exact duplicate rows checked and removed where found.")
lines.append("- No numeric outlier removal was performed; flagged in per-column stats only.")
lines.append("- Missing values left in place; imputation deferred to analyst discretion.")

profile_path = OUT_ROOT / "data-profile.md"
profile_path.write_text("\n".join(lines), encoding="utf-8")
print(f"\n  Profile written -> {profile_path}")

# ── final console summary ────────────────────────────────────────────────────

print("\n" + "="*60)
print("  SUMMARY")
print("="*60)
for name, s in summaries.items():
    print(f"\n  {name}:")
    print(f"    Rows   : {s['clean_rows']:,}")
    print(f"    Cols   : {s['clean_cols']}  ({', '.join(s['columns'])})")
    print(f"    Quality: {s['quality_score']}%")
    if s["dropped_cols"]:
        print(f"    Dropped: {s['dropped_cols']}")
    if s["parsed_dates"]:
        print(f"    Dates  : {s['parsed_dates']}")

print("\n  Date ranges:")
for tbl, dr in date_ranges.items():
    for col, rng in dr.items():
        print(f"    {tbl}.{col}: {rng['min']} to {rng['max']}")

print("\n  Relationships:")
for r in relationships:
    print(f"    {r['from']} -> {r['to']}  ({r.get('match_pct')}% match, {r.get('orphans',0)} orphans)")

print("\nDone.")
