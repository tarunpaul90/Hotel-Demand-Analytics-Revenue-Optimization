"""
Exploratory Script - STR/CoStar Data
Section 3: Data Cleaning for #3 - STR/CoStar

This script explores the structure of the hotel booking CSV files.
"""

import pandas as pd
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Define paths
DATA_PATH = Path(r"C:\Users\HP\Music\new project\#3 — STR  CoStar")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\str_costar")

# Create output directory
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STR/COSTAR DATA - EXPLORATORY ANALYSIS")
print("=" * 60)

# List all CSV files
csv_files = list(DATA_PATH.glob("*.csv"))
print(f"\nFound {len(csv_files)} CSV files:")
for f in csv_files:
    print(f"  - {f.name}")

# Explore each file
for csv_file in csv_files:
    print(f"\n{'='*60}")
    print(f"FILE: {csv_file.name}")
    print(f"Size: {csv_file.stat().st_size / (1024*1024):.2f} MB")
    print("=" * 60)

    # Read with different encodings if needed
    try:
        df = pd.read_csv(csv_file, nrows=10)
    except:
        try:
            df = pd.read_csv(csv_file, nrows=10, encoding='latin-1')
        except:
            df = pd.read_csv(csv_file, nrows=10, encoding='ISO-8859-1')

    print(f"\nShape (sample): {df.shape}")
    print(f"\nColumns ({len(df.columns)}):")
    for i, col in enumerate(df.columns, 1):
        print(f"  {i}. {col}")

    print(f"\nFirst 3 rows:")
    print(df.head(3).to_string())

    print(f"\nData Types:")
    print(df.dtypes)

    print(f"\nMissing Values:")
    missing = df.isnull().sum()
    if missing.any():
        print(missing[missing > 0])
    else:
        print("  No missing values in sample")

print("\n" + "=" * 60)
print("EXPLORATION COMPLETE")
print("=" * 60)
