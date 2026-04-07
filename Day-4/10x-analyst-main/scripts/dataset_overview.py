import pandas as pd
import re
import sys
import io

# Force UTF-8 output on Windows so unicode characters print cleanly
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding="utf-8")

FILES = [
    ("customers",     "input/shopify-data/customers.csv"),
    ("orders",        "input/shopify-data/orders.csv"),
    ("order_items",   "input/shopify-data/order_items.csv"),
    ("products",      "input/shopify-data/products.csv"),
    ("price_changes", "input/shopify-data/price_changes.csv"),
]

DATE_KEYWORDS = ("date", "time", "created", "updated", "at", "on")
NUMERIC_SKIP  = ("id", "zip", "postal", "phone", "code")


def clean_columns(df):
    df.columns = (
        df.columns
        .str.strip()
        .str.lower()
        .str.replace(r"[^a-z0-9]+", "_", regex=True)
        .str.strip("_")
    )
    return df


DATE_ANTI_KEYWORDS = ("channel", "type", "category", "name", "status")

def is_date_col(col):
    if any(kw in col for kw in DATE_ANTI_KEYWORDS):
        return False
    return any(kw in col for kw in DATE_KEYWORDS)


def is_numeric_skip(col):
    return any(kw in col for kw in NUMERIC_SKIP)


def parse_dates(df):
    date_cols = []
    for col in df.columns:
        if is_date_col(col) and df[col].dtype == object:
            try:
                df[col] = pd.to_datetime(df[col], infer_datetime_format=True, errors="coerce")
                if df[col].notna().sum() > 0:
                    date_cols.append(col)
            except Exception:
                pass
        elif is_date_col(col) and pd.api.types.is_datetime64_any_dtype(df[col]):
            date_cols.append(col)
    return df, date_cols


def overview(name, path):
    print("=" * 64)
    print(f"  FILE : {path}")
    print(f"  TABLE: {name}")
    print("=" * 64)

    try:
        df = pd.read_csv(path, low_memory=False)
    except Exception as e:
        print(f"  ERROR loading file: {e}\n")
        return

    df = clean_columns(df)
    df, date_cols = parse_dates(df)

    rows, cols = df.shape
    print(f"\n  Rows: {rows:,}   Columns: {cols}")

    # --- Column names and dtypes ---
    print("\n  Columns & Data Types:")
    print(f"  {'Column':<35} {'Dtype':<15} {'Null %':>7}")
    print("  " + "-" * 60)
    for col in df.columns:
        null_pct = df[col].isna().mean() * 100
        print(f"  {col:<35} {str(df[col].dtype):<15} {null_pct:>6.1f}%")

    # --- Date ranges ---
    if date_cols:
        print("\n  Date Ranges:")
        for col in date_cols:
            s = df[col].dropna()
            if len(s):
                print(f"    {col}: {s.min().date()} to {s.max().date()} ({len(s):,} non-null)")

    # --- Key numeric stats ---
    num_cols = [
        c for c in df.select_dtypes(include="number").columns
        if not is_numeric_skip(c)
    ]
    if num_cols:
        print("\n  Numeric Column Stats (excl. ID/code fields):")
        print(f"  {'Column':<35} {'Min':>12} {'Max':>12} {'Mean':>12} {'Median':>12}")
        print("  " + "-" * 87)
        for col in num_cols:
            s = df[col].dropna()
            if len(s) == 0:
                continue
            print(
                f"  {col:<35} "
                f"{s.min():>12,.2f} "
                f"{s.max():>12,.2f} "
                f"{s.mean():>12,.2f} "
                f"{s.median():>12,.2f}"
            )

    print()


def main():
    base = "C:/Users/p/Downloads/10x-analyst-main/10x-analyst-main"
    for name, rel_path in FILES:
        full_path = f"{base}/{rel_path}"
        overview(name, full_path)


if __name__ == "__main__":
    main()
