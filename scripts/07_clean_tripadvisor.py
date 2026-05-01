"""
Data Cleaning Script - TripAdvisor & Booking.com Review Scores
Section 3: Data Cleaning for #5 — TripAdvisor/Booking.com

This script:
1. Reads both CSV files (tripadvisor_hotel_reviews.csv, Hotel_Reviews.csv)
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
DATA_PATH = Path(r"C:\Users\HP\Music\new project\#5 — TripAdvisor  Booking.com (Review Scores)")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\tripadvisor")

# Create output directory
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("TRIPADVISOR/BOOKING.COM DATA - CLEANING PROCESS")
print("=" * 60)

# Get all CSV files
csv_files = list(DATA_PATH.glob("*.csv"))
print(f"\nFound {len(csv_files)} CSV files:")
for f in csv_files:
    print(f"  - {f.name}")

# ============================================================
# CLEANING FUNCTION FOR TRIPADVISOR
# ============================================================
def clean_tripadvisor_data(df):
    """Clean TripAdvisor reviews dataset"""

    print(f"\n{'='*60}")
    print("FILE: tripadvisor_hotel_reviews.csv")
    print(f"{'='*60}")
    print(f"\nOriginal shape: {df.shape}")

    # 1. Standardize column names
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

    # Fill missing values based on column type
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ['int64', 'float64']:
                # Use median for numeric columns
                df[col].fillna(df[col].median(), inplace=True)
            elif col in ['hotel_name', 'location', 'user_profile']:
                df[col].fillna('Unknown', inplace=True)
            else:
                mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                df[col].fillna(mode_val, inplace=True)

    print(f"\nMissing values after cleaning: {df.isnull().sum().sum()}")

    # 4. Fix data types
    # Convert rating columns to numeric
    rating_cols = [col for col in df.columns if 'rating' in col.lower() or 'score' in col.lower()]
    for col in rating_cols:
        if df[col].dtype == 'object':
            # Remove any non-numeric characters
            df[col] = df[col].astype(str).str.replace('[^0-9.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert review count to integer
    if 'no_reviews' in df.columns:
        df['no_reviews'] = pd.to_numeric(df['no_reviews'], errors='coerce').fillna(0).astype(int)

    # 5. Standardize text columns
    if 'hotel_name' in df.columns:
        df['hotel_name'] = df['hotel_name'].astype(str).str.strip().str.title()

    if 'location' in df.columns:
        df['location'] = df['location'].astype(str).str.strip().str.title()

    # 6. Identify outliers
    print(f"\nOutlier Detection (IQR method):")
    outlier_report = {}

    for col in ['rating', 'no_reviews']:
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

            print(f"  {col}: {outliers:,} outliers ({outlier_pct:.1f}%) - Bounds: [{lower_bound:.1f}, {upper_bound:.1f}]")

    # 7. Create derived columns
    if 'rating' in df.columns:
        # Rating category
        df['rating_category'] = pd.cut(
            df['rating'],
            bins=[-1, 2, 3, 4, 5],
            labels=['Poor', 'Average', 'Good', 'Excellent']
        )

        # Review volume category
        if 'no_reviews' in df.columns:
            df['review_volume'] = pd.cut(
                df['no_reviews'],
                bins=[-1, 50, 200, 500, 1000, float('inf')],
                labels=['Very Low', 'Low', 'Medium', 'High', 'Very High']
            )

    print(f"\nFinal shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")

    return df, outlier_report

# ============================================================
# CLEANING FUNCTION FOR BOOKING.COM
# ============================================================
def clean_booking_data(df):
    """Clean Booking.com/Hotel_Reviews dataset"""

    print(f"\n{'='*60}")
    print("FILE: Hotel_Reviews.csv")
    print(f"{'='*60}")
    print(f"\nOriginal shape: {df.shape}")

    # 1. Standardize column names
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

    # Fill missing values
    for col in df.columns:
        if df[col].isnull().any():
            if df[col].dtype in ['int64', 'float64']:
                df[col].fillna(df[col].median(), inplace=True)
            elif col in ['hotel_name', 'city', 'country']:
                df[col].fillna('Unknown', inplace=True)
            else:
                mode_val = df[col].mode()[0] if len(df[col].mode()) > 0 else 'Unknown'
                df[col].fillna(mode_val, inplace=True)

    print(f"\nMissing values after cleaning: {df.isnull().sum().sum()}")

    # 4. Fix data types
    # Convert score columns to numeric
    score_cols = [col for col in df.columns if 'score' in col.lower() or 'rating' in col.lower()]
    for col in score_cols:
        if df[col].dtype == 'object':
            df[col] = df[col].astype(str).str.replace('[^0-9.]', '', regex=True)
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)

    # Convert review counts to integer
    count_cols = [col for col in df.columns if 'review' in col.lower() and 'count' in col.lower()]
    for col in count_cols:
        if df[col].dtype in ['int64', 'float64']:
            df[col] = df[col].fillna(0).astype(int)

    # 5. Standardize text columns
    text_cols = ['hotel_name', 'city', 'country']
    for col in text_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.strip().str.title()

    # 6. Identify outliers
    print(f"\nOutlier Detection (IQR method):")
    outlier_report = {}

    for col in df.columns:
        if df[col].dtype in ['int64', 'float64']:
            Q1 = df[col].quantile(0.25)
            Q3 = df[col].quantile(0.75)
            IQR = Q3 - Q1
            lower_bound = Q1 - 1.5 * IQR
            upper_bound = Q3 + 1.5 * IQR

            outliers = ((df[col] < lower_bound) | (df[col] > upper_bound)).sum()
            outlier_pct = (outliers / len(df)) * 100

            if outliers > 0:
                outlier_report[col] = {
                    'count': outliers,
                    'percentage': outlier_pct,
                    'lower_bound': lower_bound,
                    'upper_bound': upper_bound,
                    'min': df[col].min(),
                    'max': df[col].max(),
                    'median': df[col].median()
                }

                print(f"  {col}: {outliers:,} outliers ({outlier_pct:.1f}%) - Bounds: [{lower_bound:.1f}, {upper_bound:.1f}]")

    # 7. Create derived columns
    # Find the main score column
    main_score_col = None
    for col in ['overall_score', 'score', 'average_score']:
        if col in df.columns:
            main_score_col = col
            break

    if main_score_col:
        # Score category
        df['score_category'] = pd.cut(
            df[main_score_col],
            bins=[-1, 6, 7, 8, 9, 10],
            labels=['Poor', 'Fair', 'Good', 'Very Good', 'Excellent']
        )

    print(f"\nFinal shape: {df.shape}")
    print(f"Columns: {len(df.columns)}")

    return df, outlier_report

# ============================================================
# PROCESS EACH FILE
# ============================================================
all_clean_data = {}
all_outlier_reports = {}

for csv_file in csv_files:
    # Read CSV
    try:
        df = pd.read_csv(csv_file, low_memory=False)
    except Exception as e:
        try:
            df = pd.read_csv(csv_file, encoding='latin-1', low_memory=False)
        except:
            print(f"Error reading {csv_file.name}: {e}")
            continue

    # Clean based on file type
    if 'tripadvisor' in csv_file.name.lower():
        cleaned_df, outlier_report = clean_tripadvisor_data(df)
        file_key = 'tripadvisor'
    else:
        cleaned_df, outlier_report = clean_booking_data(df)
        file_key = 'booking_com'

    all_clean_data[file_key] = cleaned_df
    all_outlier_reports[file_key] = outlier_report

# ============================================================
# SAVE OUTPUT FILES
# ============================================================
print("\n" + "=" * 60)
print("SAVING OUTPUT FILES")
print("=" * 60)

for file_key, df in all_clean_data.items():
    output_file = OUTPUT_PATH / f"{file_key}_cleaned.xlsx"

    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main cleaned data
        df.to_excel(writer, sheet_name="Cleaned_Data", index=False)

        # Summary statistics
        numeric_summary = df.describe().round(2)
        numeric_summary.to_excel(writer, sheet_name="Summary_Stats")

        # Score/Rating distribution
        rating_col = None
        for col in ['rating', 'overall_score', 'score', 'average_score']:
            if col in df.columns:
                rating_col = col
                break

        if rating_col:
            rating_dist = df[rating_col].value_counts().reset_index()
            rating_dist.columns = ['Score', 'Count']
            rating_dist.to_excel(writer, sheet_name="Score_Dist", index=False)

            if f'{rating_col}_category' in df.columns:
                cat_dist = df[f'{rating_col}_category'].value_counts().reset_index()
                cat_dist.columns = ['Category', 'Count']
                cat_dist.to_excel(writer, sheet_name="Category_Dist", index=False)

        # Outlier report
        city_outliers = all_outlier_reports.get(file_key, {})
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

    print(f"\n{file_key}:")
    print(f"  Records: {len(df):,}")
    print(f"  Saved to: {output_file.name}")

# ============================================================
# CREATE MASTER SUMMARY
# ============================================================
master_summary = pd.DataFrame([
    {
        'Source': source,
        'Total Reviews': len(df),
        'Avg Score': f"{df[[c for c in df.columns if 'rating' in c or 'score' in c][0]].mean():.2f}" if any('rating' in c or 'score' in c for c in df.columns) else 'N/A',
        'Median Score': f"{df[[c for c in df.columns if 'rating' in c or 'score' in c][0]].median():.2f}" if any('rating' in c or 'score' in c for c in df.columns) else 'N/A',
        'Unique Hotels': df['hotel_name'].nunique() if 'hotel_name' in df.columns else 'N/A'
    }
    for source, df in all_clean_data.items()
])

master_summary.to_csv(OUTPUT_PATH / "master_summary.csv", index=False)
print(f"\nMaster summary saved to: master_summary.csv")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"\nSources processed: {len(all_clean_data)}")
for source, df in all_clean_data.items():
    print(f"  {source}: {len(df):,} reviews")

print(f"\nOutput location: {OUTPUT_PATH}")
