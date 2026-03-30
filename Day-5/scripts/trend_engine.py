"""
trend_engine.py — Content Trend Analysis Engine
Part of the 10x-content-intel plugin

Usage:
    python scripts/trend_engine.py <dataset-name>

Generates trend analysis charts and insights from cleaned content data.
"""

import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import seaborn as sns
import sys
from pathlib import Path
from datetime import datetime

# Style setup
sns.set_style("whitegrid")
PALETTE = sns.color_palette("muted")
PASTEL = sns.color_palette("pastel")

plt.rcParams.update({
    'figure.dpi': 120,
    'axes.titlesize': 14,
    'axes.titleweight': 'bold',
    'axes.labelsize': 12,
    'xtick.labelsize': 10,
    'ytick.labelsize': 10,
    'figure.facecolor': 'white',
    'axes.facecolor': 'white',
    'axes.edgecolor': '#cccccc',
    'grid.color': '#eeeeee',
})


def detect_columns(df: pd.DataFrame) -> dict:
    """Auto-detect key columns in the dataset."""
    col_map = {}
    cols_lower = {c.lower(): c for c in df.columns}

    # Type column (Movie vs TV Show)
    for key in ['type', 'content_type', 'media_type']:
        if key in cols_lower:
            col_map['type'] = cols_lower[key]
            break

    # Date column
    for key in ['date_added', 'release_date', 'added_date', 'date']:
        if key in cols_lower:
            col_map['date'] = cols_lower[key]
            break

    # Year column
    for key in ['release_year', 'year', 'release_year']:
        if key in cols_lower:
            col_map['year'] = cols_lower[key]
            break

    # Genre column
    for key in ['listed_in', 'genre', 'genres', 'category']:
        if key in cols_lower:
            col_map['genre'] = cols_lower[key]
            break

    # Duration column
    for key in ['duration', 'runtime', 'length']:
        if key in cols_lower:
            col_map['duration'] = cols_lower[key]
            break

    # Rating column
    for key in ['rating', 'content_rating', 'maturity_rating']:
        if key in cols_lower:
            col_map['rating'] = cols_lower[key]
            break

    return col_map


def chart_yearly_additions(df, col_map, out_dir):
    """Chart 1: Yearly content additions, stacked by type."""
    if 'year' not in col_map or 'type' not in col_map:
        return

    yearly = df.groupby([col_map['year'], col_map['type']]).size().unstack(fill_value=0)

    fig, ax = plt.subplots(figsize=(12, 6))
    yearly.plot(kind='bar', stacked=True, ax=ax, color=PALETTE[:len(yearly.columns)], edgecolor='white')
    ax.set_title('Content Added by Year (Movies vs TV Shows)')
    ax.set_xlabel('Release Year')
    ax.set_ylabel('Number of Titles')
    ax.legend(title='Type')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_dir / 'chart_01_yearly_additions.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("  Chart 1: Yearly additions — saved")


def chart_cumulative_growth(df, col_map, out_dir):
    """Chart 2: Cumulative content growth."""
    if 'date' not in col_map:
        return

    date_col = col_map['date']
    df_dated = df.dropna(subset=[date_col]).copy()
    df_dated[date_col] = pd.to_datetime(df_dated[date_col], errors='coerce')
    df_dated = df_dated.dropna(subset=[date_col]).sort_values(date_col)
    df_dated['cumulative'] = range(1, len(df_dated) + 1)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.plot(df_dated[date_col], df_dated['cumulative'], color=PALETTE[0], linewidth=2)
    ax.fill_between(df_dated[date_col], df_dated['cumulative'], alpha=0.15, color=PALETTE[0])
    ax.set_title('Cumulative Content Growth Over Time')
    ax.set_xlabel('Date')
    ax.set_ylabel('Total Titles in Library')
    plt.tight_layout()
    plt.savefig(out_dir / 'chart_02_cumulative_growth.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("  Chart 2: Cumulative growth — saved")


def chart_monthly_seasonality(df, col_map, out_dir):
    """Chart 3: Monthly addition patterns."""
    if 'date' not in col_map:
        return

    date_col = col_map['date']
    df_dated = df.dropna(subset=[date_col]).copy()
    df_dated[date_col] = pd.to_datetime(df_dated[date_col], errors='coerce')
    monthly = df_dated[date_col].dt.month_name().value_counts()
    month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                   'July', 'August', 'September', 'October', 'November', 'December']
    monthly = monthly.reindex(month_order).fillna(0)

    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(monthly.index, monthly.values, color=PALETTE[2], edgecolor='white')
    ax.set_title('Content Additions by Month (Seasonality)')
    ax.set_xlabel('Month')
    ax.set_ylabel('Number of Titles Added')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(out_dir / 'chart_03_monthly_seasonality.png', dpi=120, bbox_inches='tight')
    plt.close()
    print("  Chart 3: Monthly seasonality — saved")


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/trend_engine.py <dataset-name>")
        sys.exit(1)

    dataset = sys.argv[1]
    clean_path = Path(f"output/{dataset}/{dataset}_cleaned.csv")
    out_dir = Path(f"output/{dataset}/trends")

    if not clean_path.exists():
        print(f"Error: Cleaned data not found at {clean_path}")
        print("Run the :scan skill first to clean the data.")
        sys.exit(1)

    out_dir.mkdir(parents=True, exist_ok=True)

    df = pd.read_csv(clean_path)
    print(f"Loaded: {len(df):,} rows from {clean_path}")

    col_map = detect_columns(df)
    print(f"Detected columns: {col_map}")

    chart_yearly_additions(df, col_map, out_dir)
    chart_cumulative_growth(df, col_map, out_dir)
    chart_monthly_seasonality(df, col_map, out_dir)

    print(f"\nAll trend charts saved to {out_dir}")


if __name__ == "__main__":
    main()
