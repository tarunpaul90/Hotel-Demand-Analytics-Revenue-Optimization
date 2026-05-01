"""
Data Cleaning Script - UK ONS Tourism Data
Section 3: Data Cleaning for #1 - UK ONS Tourism Data

This script:
1. Reads all UK ONS Tourism Data Excel files
2. Explores their structure
3. Cleans and merges overlapping year ranges
4. Handles missing values
5. Exports a unified clean dataset
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Define paths
DATA_PATH = Path(r"C:\Users\HP\Music\new project\#1 — UK ONS Tourism Data")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data")

# Create output directory
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("UK ONS TOURISM DATA - EXPLORATORY ANALYSIS")
print("=" * 60)

# List all Excel files
excel_files = list(DATA_PATH.glob("*.xls*"))
print(f"\nFound {len(excel_files)} Excel files:")
for f in excel_files:
    print(f"  - {f.name}")

# Function to explore Excel file structure
def explore_excel(filepath):
    """Explore all sheets in an Excel file"""
    print(f"\n{'='*60}")
    print(f"FILE: {filepath.name}")
    print("=" * 60)

    try:
        # Get sheet names
        xl_file = pd.ExcelFile(filepath)
        sheet_names = xl_file.sheet_names
        print(f"Sheets: {sheet_names}")

        for sheet in sheet_names:
            print(f"\n--- Sheet: '{sheet}' ---")
            try:
                df = pd.read_excel(filepath, sheet_name=sheet, nrows=10)
                print(f"Shape (sample): {df.shape}")
                print(f"Columns: {list(df.columns)}")
                print(f"\nFirst 3 rows:")
                print(df.head(3).to_string())
            except Exception as e:
                print(f"Error reading sheet: {e}")

        xl_file.close()
    except Exception as e:
        print(f"Error opening file: {e}")

# Explore each file
print("\n\n" + "=" * 60)
print("EXPLORING EACH FILE STRUCTURE")
print("=" * 60)

for file in excel_files:
    explore_excel(file)
    print("\n\n")

print("\n" + "=" * 60)
print("EXPLORATION COMPLETE")
print("=" * 60)
