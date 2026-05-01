"""
Data Cleaning Script - Inside Airbnb Data
Section 3: Data Cleaning for #4 — Inside Airbnb

This script:
1. Reads all 4 city CSV files (Bristol, Edinburgh, Greater Manchester, London)
2. Handles missing values
3. Removes duplicates
4. Fixes data types and formats
5. Standardizes column names and text
6. Identifies outliers
7. Exports cleaned Excel files
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings
import re

warnings.filterwarnings('ignore')

# Define paths
DATA_PATH = Path(r"C:\Users\HP\Music\new project\#4 — Inside Airbnb")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\inside_airbnb")

# Create output directory
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("INSIDE AIRBNB DATA - CLEANING PROCESS")
print("=" * 60)

# Get all CSV files
csv_files = list(DATA_PATH.glob("*.csv"))
print(f"\nFound {len(csv_files)} CSV files:")
for f in csv_files:
    print(f"  - {f.name}")

# ============================================================
# CLEANING FUNCTION
# ============================================================
def clean_airbnb_data(df, city_name):
    """Clean a single Airbnb dataset"""

    print(f"\n{'='*60}")
    print(f"CITY: {city_name}")
    print(f"{'='*60}")
    print(f"\nOriginal shape: {df.shape}")

    # 1. Standardize column names (lowercase, underscores)
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(' ', '_')
    df.columns = df.columns.str.replace('[^a-z0-9_]', '', regex=True)

    # 2. Remove duplicates
    duplicates_before = df.duplicated().sum()
    if duplicates_before > 0:
        df = df.drop_duplicates()
        print(f"Removed {duplicates_before} duplicate rows")
    print(f"Duplicates found: {duplicates_before}")

    # 3. Handle missing values
    print(f"\nMissing values before cleaning:")
    missing_before = df.isnull().sum()
    missing_report = missing_before[missing_before > 0]
    if len(missing_report) > 0:
        for col, count in missing_report.items():
            pct = (count / len(df)) * 100
            print(f"  {col}: {count:,} ({pct:.1f}%)")
    else:
        print("  None")

    # Categorize columns for different handling
    numeric_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    text_cols = df.select_dtypes(include=['object']).columns.tolist()

    # Fill numeric missing values
    for col in numeric_cols:
        if df[col].isnull().any():
            if df[col].dtype in ['int64', 'float64']:
                # Use median for numeric columns
                median_val = df[col].median()
                df[col].fillna(median_val, inplace=True)

    # Fill text missing values
    for col in text_cols:
        if df[col].isnull().any():
            if col in ['name', 'host_name']:
                df[col].fillna('Unknown', inplace=True)
            elif col in ['neighbourhood', 'neighbourhood_group']:
                df[col].fillna('Not Specified', inplace=True)
            else:
                mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                df[col].fillna(mode_val, inplace=True)

    print(f"\nMissing values after cleaning: {df.isnull().sum().sum()}")

    # 4. Fix data types
    # Price columns - remove currency symbols and convert to float
    price_cols = [col for col in df.columns if 'price' in col.lower()]
    for col in price_cols:
        if df[col].dtype == 'object':
            # Remove $, £, €, commas, and spaces
            df[col] = df[col].astype(str).str.replace('[$£€,]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert integer columns
    int_cols = ['minimum_nights', 'maximum_nights', 'number_of_reviews',
                'reviews_per_month', 'calculated_host_listings_count',
                'availability_365', 'bedrooms', 'beds', 'bathrooms']
    for col in int_cols:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0).astype(int)

    # 5. Standardize text columns
    text_standardize_cols = ['room_type', 'property_type', 'cancellation_policy']
    for col in text_standardize_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # 6. Identify and handle outliers
    print(f"\nOutlier Detection (IQR method):")
    outlier_report = {}

    for col in ['price', 'minimum_nights', 'maximum_nights', 'number_of_reviews']:
        if col in df.columns:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            outlier_pct = (outliers / len(df)) * 100

            outlier_report[col] = {
                'count': outliers,
                'percentage': outlier_pct,
                'lower_bound': lower_bound,
                'upper_bound': upper_bound,
                'min': df[col].min(),
                'max': df[col].max(),
                'median': df[col].median()
            }

            print(f"  {col}: {outliers:,} outliers ({outlier_pct:.1f}%) - Bounds: [{lower_bound:.0f}, {upper_bound:.0f}]")

    # Clip extreme outliers for price (cap at 95th percentile)
    if 'price' in df.columns:
        price_cap = df['price'].quantile(0.95)
        df['price_capped'] = df['price'].clip(upper=price_cap)
        print(f"\nPrice capped at 95th percentile: £{price_cap:.2f}")

    # 7. Create derived columns
    if 'price' in df.columns and 'minimum_nights' in df.columns:
        df['min_stay_cost'] = df['price_capped'] * df['minimum_nights']

    if 'number_of_reviews' in df.columns:
        df['review_category'] = pd.cut(
            df['number_of_reviews'],
            bins=[-1, 10, 50, 100, 500, float('inf')],
            labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
        )

    if 'price' in df.columns:
        df['price_category'] = pd.cut(
            df['price_capped'],
            bins=[-1, 50, 100, 200, 500, float('inf')],
            labels=['Budget', 'Mid-Range', 'Premium', 'Luxury', 'Ultra-Luxury']
        )

    print(f"\nFinal shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")

    return df, outlier_report

# ============================================================
# PROCESS EACH CITY
# ============================================================
all_clean_data = {}
all_outlier_reports = {}

for csv_file in csv_files:
    # Extract city name from filename
    city_name = csv_file.stem.replace('_', ' ').strip()

    # Read CSV
    try:
        df = pd.read_csv(csv_file, low_memory=False)
    except Exception as e:
        try:
            df = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)
        except:
            print(f"Error reading {csv_file.name}: {e}")
            continue

    # Clean data
    cleaned_df, outlier_report = clean_airbnb_data(df, city_name)

    all_clean_data[city_name] = cleaned_df
    all_outlier_reports[city_name] = outlier_report

# ============================================================
# SAVE OUTPUT FILES
# ============================================================
print("\n" + "=" * 60)
print("SAVING OUTPUT FILES")
print("=" * 60)

for city_name, df in all_clean_data.items():
    # Save to Excel
    output_file = OUTPUT_PATH / f"{city_name.replace(' ', '_')}_cleaned.xlsx"

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main cleaned data
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)

        # Summary statistics
        numeric_summary = df.describe().round(2)
        numeric_summary.to_excel(writer, sheet_name="Summary_Stats")

        # Room type distribution
        if 'room_type' in df.columns:
            room_type_dist = df['room_type'].value_counts().reset_index()
            room_type_dist.columns = ['Room Type', 'Count']
            room_type_dist.to_excel(writer, sheet_name="Room_Type_Dist", index=False)

        # Price distribution
        if 'price_category' in df.columns:
            price_dist = df['price_category'].value_counts().reset_index()
            price_dist.columns = ['Price Category', 'Count']
            price_dist.to_excel(writer, sheet_name="Price_Dist", index=False)

        # Outlier report
        city_outliers = all_outlier_reports.get(city_name, {})
        if city_outliers:
            outlier_df = pd.DataFrame([
                {
                    'Column': col,
                    'Outliers': info['count'],
                    'Percentage': f"{info['percentage']:.2f}%",
                    'Lower Bound': f"{info['lower_bound']:.2f}",
                    'Upper Bound': f"{info['upper_bound']:.2f}",
                    'Min': info['min'],
                    'Max': info['max'],
                    'Median': info['median']
                }
                for col, info in city_outliers.items()
            ])
            outlier_df.to_excel(writer, sheet_name="Outlier_Report", index=False)

    print(f"\n{city_name}:")
    print(f"  Records: {len(df):,}")
    print(f"  Saved to: {output_file.name}")

# ============================================================
# CREATE MASTER SUMMARY
# ============================================================
master_summary = pd.DataFrame([
    {
        'City': city,
        'Total Listings': len(df),
        'Avg Price': f"£{df['price_capped'].mean():.2f}" if 'price_capped' in df.columns else 'N/A',
        'Median Price': f"£{df['price_capped'].median():.2f}" if 'price_capped' in df.columns else 'N/A',
        'Avg Reviews': f"{df['number_of_reviews'].mean():.1f}" if 'number_of_reviews' in df.columns else 'N/A',
        'Room Types': df['room_type'].nunique() if 'room_type' in df.columns else 'N/A'
    }
    for city, df in all_clean_data.items()
])

master_summary.to_csv(OUTPUT_PATH / "master_summary.csv", index=False)
print(f"\nMaster summary saved to: master_summary.csv")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"\nCities processed: {len(all_clean_data)}")
for city, df in all_clean_data.items():
    print(f"  {city}: {len(df):,} listings")

print(f"\nOutput location: {OUTPUT_PATH}")
