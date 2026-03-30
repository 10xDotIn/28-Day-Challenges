---
name: scan
description: "Quick scan & profile of a content library dataset — ingests, cleans, and generates a data inventory report"
argument-hint: "<dataset-folder-name>"
risk: "safe"
user-invocable: true
allowed-tools:
  - Read
  - Write
  - Edit
  - Bash
  - Glob
  - Grep
model: claude-sonnet-4-6
context: fork
agent: general-purpose
---

# Scan — Content Library Quick Profile

You are executing the `:scan` skill for the **10x-content-intel** plugin.

## What This Skill Does

Performs a quick scan and profile of a content library dataset. This is the foundational step — understand the data before analyzing it.

## Instructions

### Step 1: Locate the Data
- Look in `input/{argument}/` for data files (CSV, Excel, JSON)
- If no argument provided, scan all subdirectories in `input/`
- Read the agent instructions from `agents/content-profiler.md`

### Step 2: Ingest & Profile
Run the following Python script:

```python
import pandas as pd
import os
from pathlib import Path

# Find the dataset
dataset_name = "{argument}"
input_dir = Path(f"input/{dataset_name}")
output_dir = Path(f"output/{dataset_name}")
output_dir.mkdir(parents=True, exist_ok=True)

# Load all data files
files = list(input_dir.glob("*.csv")) + list(input_dir.glob("*.xlsx")) + list(input_dir.glob("*.json"))

for f in files:
    if f.suffix == '.csv':
        df = pd.read_csv(f)
    elif f.suffix in ['.xlsx', '.xls']:
        df = pd.read_excel(f)
    elif f.suffix == '.json':
        df = pd.read_json(f)

    print(f"\n{'='*60}")
    print(f"FILE: {f.name}")
    print(f"{'='*60}")
    print(f"Shape: {df.shape[0]:,} rows x {df.shape[1]} columns")
    print(f"\nColumn Types:\n{df.dtypes.to_string()}")
    print(f"\nMissing Values:\n{df.isnull().sum().to_string()}")
    print(f"\nSample (first 3 rows):")
    print(df.head(3).to_string())
    print(f"\nUnique counts per column:")
    for col in df.columns:
        print(f"  {col}: {df[col].nunique()} unique")
```

### Step 3: Clean the Data
Follow the Content Profiler agent instructions:
- Handle missing values (fill categorical with "Unknown", dates as NaT, numerical with median)
- Remove duplicate rows
- Standardize column names (lowercase, underscores)
- Parse date columns
- Strip whitespace from string columns
- Save cleaned data to `output/{argument}/{argument}_cleaned.csv`

### Step 4: Generate Scan Report
Create `output/{argument}/scan_report.md` with:
- Dataset overview (source, rows, columns)
- Column inventory table
- Missing data summary
- Data quality score
- Cleaning actions taken
- Key observations

## Output
- `output/{argument}/scan_report.md`
- `output/{argument}/{argument}_cleaned.csv`
