"""
Airbnb Dataset - Data Cleaning Script
Cleans Places, Hosts, and Neighborhoods sheets and merges into one dataset.
"""

import pandas as pd
import numpy as np

# ============================================================
# 1. LOAD RAW DATA
# ============================================================
FILE = "Airbnb dataset.xlsx"

places = pd.read_excel(FILE, sheet_name="Places")
hosts = pd.read_excel(FILE, sheet_name="Hosts")
neighborhoods = pd.read_excel(FILE, sheet_name="Neighborhoods")

print("=" * 60)
print("RAW DATA SHAPE")
print(f"  Places:        {places.shape}")
print(f"  Hosts:         {hosts.shape}")
print(f"  Neighborhoods: {neighborhoods.shape}")

# ============================================================
# 2. CLEAN PLACES
# ============================================================

# Drop junk/reference columns (Unnamed:12 is all NaN;
# Price Range, Min. Price, Service Fee have only 4 values — they are lookup references, not per-listing data)
cols_to_drop = ["Unnamed: 12", "Price Range", "Min. Price", "Service Fee"]
places.drop(columns=[c for c in cols_to_drop if c in places.columns], inplace=True)

# Drop rows with null Place Name (1 row)
places.dropna(subset=["Place Name"], inplace=True)

# Strip whitespace from Place Name
places["Place Name"] = places["Place Name"].str.strip()

# Convert Instant Book to boolean
places["Instant Book"] = places["Instant Book"].map({"Yes": True, "No": False})

# Rename for consistency
places.rename(columns={"# of Reviews": "Num_Reviews"}, inplace=True)

print(f"\n  Places after cleaning: {places.shape}")
print(f"  Nulls remaining:\n{places.isnull().sum().to_string()}")

# ============================================================
# 3. CLEAN HOSTS
# ============================================================

# Drop all unnamed junk columns
unnamed_cols = [c for c in hosts.columns if c.startswith("Unnamed")]
hosts.drop(columns=unnamed_cols, inplace=True)

# Parse Date Joined from YYYYMMDD integer to datetime
hosts["Date Joined"] = pd.to_datetime(hosts["Date Joined"].astype(str), format="%Y%m%d")

# Convert Superhost to boolean
hosts["Superhost"] = hosts["Superhost"].map({"Yes": True, "No": False})

# Response Rate and Acceptance Rate are already 0-1 decimals — convert to percentage
hosts["Response Rate"] = (hosts["Response Rate"] * 100).round(1)
hosts["Acceptance Rate"] = (hosts["Acceptance Rate"] * 100).round(1)

print(f"\n  Hosts after cleaning: {hosts.shape}")
print(f"  Nulls remaining:\n{hosts.isnull().sum().to_string()}")

# ============================================================
# 4. MERGE INTO ONE CLEAN DATASET
# ============================================================

# Places + Neighborhoods
df = places.merge(neighborhoods, on="Neighborhood ID", how="left")

# + Hosts
df = df.merge(hosts, on="Host ID", how="left")

# Reorder columns logically
df = df[[
    # Listing info
    "Place Name", "Room Type", "Accommodates", "Price", "Rating",
    "Num_Reviews", "First Review", "Last Review", "Availability", "Instant Book",
    # Location
    "Neighborhood ID", "District", "Neighborhood",
    # Host info
    "Host ID", "Host Name", "Email", "Date Joined", "Host Location",
    "Response Time", "Response Rate", "Acceptance Rate", "Superhost",
]]

# Derived columns
df["Listing Age (days)"] = (pd.Timestamp("2020-04-01") - df["First Review"]).dt.days
df["Days Since Last Review"] = (pd.Timestamp("2020-04-01") - df["Last Review"]).dt.days
df["Host Tenure (years)"] = ((pd.Timestamp("2020-04-01") - df["Date Joined"]).dt.days / 365.25).round(1)

print(f"\n  Final merged dataset: {df.shape}")
print(f"  Nulls in merged data:\n{df.isnull().sum().to_string()}")

# ============================================================
# 5. SAVE CLEAN DATA
# ============================================================
df.to_csv("airbnb_cleaned.csv", index=False)
print(f"\n{'=' * 60}")
print("Saved: airbnb_cleaned.csv")
print(f"Final shape: {df.shape[0]} rows x {df.shape[1]} columns")
print(f"{'=' * 60}")

# ============================================================
# 6. QUICK DATA PROFILE
# ============================================================
print("\n--- COLUMN SUMMARY ---")
print(df.dtypes.to_string())

print("\n--- NUMERIC STATS ---")
print(df.describe().round(2).to_string())

print("\n--- CATEGORICAL DISTRIBUTION ---")
for col in ["Room Type", "District", "Superhost", "Instant Book", "Response Time"]:
    print(f"\n{col}:")
    print(df[col].value_counts().to_string())
