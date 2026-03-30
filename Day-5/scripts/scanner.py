"""
scanner.py — Content Library Scanner & Profiler
Part of the 10x-content-intel plugin

Usage:
    python scripts/scanner.py <dataset-name>

Scans input/<dataset>/ for data files, profiles them, and outputs a report.
"""

import pandas as pd
import sys
import os
from pathlib import Path
from datetime import datetime


def scan_directory(input_dir: Path) -> list:
    """Find all data files in the input directory."""
    extensions = ['*.csv', '*.xlsx', '*.xls', '*.json']
    files = []
    for ext in extensions:
        files.extend(input_dir.glob(ext))
    return sorted(files)


def load_file(filepath: Path) -> pd.DataFrame:
    """Load a data file into a DataFrame."""
    suffix = filepath.suffix.lower()
    if suffix == '.csv':
        return pd.read_csv(filepath)
    elif suffix in ['.xlsx', '.xls']:
        return pd.read_excel(filepath)
    elif suffix == '.json':
        return pd.read_json(filepath)
    else:
        raise ValueError(f"Unsupported file type: {suffix}")


def profile_dataframe(df: pd.DataFrame, filename: str) -> dict:
    """Generate a comprehensive profile of a DataFrame."""
    profile = {
        'filename': filename,
        'rows': len(df),
        'columns': len(df.columns),
        'memory_mb': df.memory_usage(deep=True).sum() / 1024 / 1024,
        'duplicates': df.duplicated().sum(),
        'column_details': []
    }

    for col in df.columns:
        col_info = {
            'name': col,
            'dtype': str(df[col].dtype),
            'non_null': df[col].notna().sum(),
            'null_count': df[col].isna().sum(),
            'null_pct': round(df[col].isna().mean() * 100, 1),
            'unique': df[col].nunique(),
            'sample_values': str(df[col].dropna().head(3).tolist())
        }
        profile['column_details'].append(col_info)

    return profile


def clean_dataframe(df: pd.DataFrame) -> tuple:
    """Clean the DataFrame and return (cleaned_df, actions_taken)."""
    actions = []
    original_shape = df.shape

    # Remove exact duplicates
    dupes = df.duplicated().sum()
    if dupes > 0:
        df = df.drop_duplicates()
        actions.append(f"Removed {dupes} duplicate rows")

    # Standardize column names
    original_cols = df.columns.tolist()
    df.columns = df.columns.str.strip().str.lower().str.replace(' ', '_').str.replace('-', '_')
    renamed = [(o, n) for o, n in zip(original_cols, df.columns) if o != n]
    if renamed:
        actions.append(f"Standardized {len(renamed)} column names")

    # Strip whitespace from string columns
    str_cols = df.select_dtypes(include='object').columns
    for col in str_cols:
        df[col] = df[col].str.strip() if df[col].dtype == 'object' else df[col]
    if len(str_cols) > 0:
        actions.append(f"Stripped whitespace from {len(str_cols)} text columns")

    # Parse date columns (heuristic: look for 'date' in column name)
    for col in df.columns:
        if 'date' in col.lower():
            try:
                df[col] = pd.to_datetime(df[col], errors='coerce')
                actions.append(f"Parsed '{col}' as datetime")
            except Exception:
                pass

    # Handle missing values
    for col in df.columns:
        null_count = df[col].isna().sum()
        if null_count > 0:
            if df[col].dtype == 'object':
                df[col] = df[col].fillna('Unknown')
                actions.append(f"Filled {null_count} nulls in '{col}' with 'Unknown'")
            elif pd.api.types.is_numeric_dtype(df[col]):
                median_val = df[col].median()
                df[col] = df[col].fillna(median_val)
                actions.append(f"Filled {null_count} nulls in '{col}' with median ({median_val:.1f})")

    return df, actions


def generate_report(profile: dict, actions: list, output_dir: Path) -> str:
    """Generate a markdown scan report."""
    report = f"""# Scan Report — {profile['filename']}
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

## Dataset Overview
| Metric | Value |
|--------|-------|
| Rows | {profile['rows']:,} |
| Columns | {profile['columns']} |
| Memory | {profile['memory_mb']:.1f} MB |
| Duplicates Found | {profile['duplicates']} |

## Column Inventory
| Column | Type | Non-Null | Null % | Unique | Sample Values |
|--------|------|----------|--------|--------|---------------|
"""
    for col in profile['column_details']:
        report += f"| {col['name']} | {col['dtype']} | {col['non_null']:,} | {col['null_pct']}% | {col['unique']:,} | {col['sample_values'][:50]} |\n"

    report += f"\n## Cleaning Actions Taken\n"
    for i, action in enumerate(actions, 1):
        report += f"{i}. {action}\n"

    report += f"\n## Output Files\n"
    report += f"- Cleaned dataset: `{output_dir.name}_cleaned.csv`\n"
    report += f"- This report: `scan_report.md`\n"

    return report


def main():
    if len(sys.argv) < 2:
        print("Usage: python scripts/scanner.py <dataset-name>")
        sys.exit(1)

    dataset = sys.argv[1]
    input_dir = Path(f"input/{dataset}")
    output_dir = Path(f"output/{dataset}")

    if not input_dir.exists():
        print(f"Error: Input directory '{input_dir}' not found")
        sys.exit(1)

    output_dir.mkdir(parents=True, exist_ok=True)

    # Find and load data files
    files = scan_directory(input_dir)
    if not files:
        print(f"No data files found in {input_dir}")
        sys.exit(1)

    print(f"Found {len(files)} data file(s) in {input_dir}")

    for filepath in files:
        print(f"\nProcessing: {filepath.name}")

        # Load
        df = load_file(filepath)
        print(f"  Loaded: {df.shape[0]:,} rows x {df.shape[1]} columns")

        # Profile
        profile = profile_dataframe(df, filepath.name)

        # Clean
        df_cleaned, actions = clean_dataframe(df)
        print(f"  Cleaned: {len(actions)} actions taken")

        # Save cleaned data
        clean_path = output_dir / f"{dataset}_cleaned.csv"
        df_cleaned.to_csv(clean_path, index=False)
        print(f"  Saved: {clean_path}")

        # Generate report
        report = generate_report(profile, actions, output_dir)
        report_path = output_dir / "scan_report.md"
        report_path.write_text(report, encoding='utf-8')
        print(f"  Report: {report_path}")


if __name__ == "__main__":
    main()
