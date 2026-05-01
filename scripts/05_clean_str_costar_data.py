"""
Data Cleaning Script - STR/CoStar Hotel Data
Section 3: Data Cleaning for #3 - STR/CoStar

This script:
1. Reads both hotel booking CSV files
2. Cleans and standardizes the data
3. Handles missing values
4. Exports cleaned Excel files
"""

import pandas as pd
import numpy as np
from pathlib import Path
import warnings

warnings.filterwarnings('ignore')

# Define paths
DATA_PATH = Path(r"C:\Users\HP\Music\new project\#3 — STR  CoStar")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\str_costar")

# Create output directory
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("STR/COSTAR DATA - CLEANING PROCESS")
print("=" * 60)

# ============================================================
# FILE 1: Hotel Reservations.csv
# ============================================================
print("\n" + "=" * 60)
print("CLEANING: Hotel Reservations.csv")
print("=" * 60)

df1 = pd.read_csv(DATA_PATH / "Hotel Reservations.csv")
print(f"\nOriginal shape: {df1.shape}")

# Check for duplicates
duplicates = df1.duplicated().sum()
print(f"Duplicate rows: {duplicates}")
if duplicates > 0:
    df1 = df1.drop_duplicates()
    print(f"Shape after removing duplicates: {df1.shape}")

# Check missing values
print(f"\nMissing values before cleaning:")
missing = df1.isnull().sum()
print(missing[missing > 0] if missing.any() else "  None")

# Handle missing values (if any)
for col in df1.columns:
    if df1[col].isnull().any():
        if df1[col].dtype in ['int64', 'float64']:
            df1[col].fillna(df1[col].median(), inplace=True)
        else:
            df1[col].fillna(df1[col].mode()[0], inplace=True)

print(f"Missing values after cleaning: {df1.isnull().sum().sum()}")

# Standardize column names
df1.columns = df1.columns.str.lower().str.replace(' ', '_')

# Create derived columns
df1['total_nights'] = df1['no_of_weekend_nights'] + df1['no_of_week_nights']
df1['total_guests'] = df1['no_of_adults'] + df1['no_of_children']

# Create date string and parse with error handling
df1['date_str'] = df1['arrival_year'].astype(str) + '-' + df1['arrival_month'].astype(str).str.zfill(2) + '-' + df1['arrival_date'].astype(str).str.zfill(2)
df1['arrival_date_full'] = pd.to_datetime(df1['date_str'], errors='coerce', dayfirst=False)
df1['arrival_weekday'] = df1['arrival_date_full'].dt.day_name()
df1.drop(columns=['date_str'], inplace=True)

# Calculate RevPAR-related metrics
df1['total_revenue'] = df1['avg_price_per_room'] * df1['total_nights']

# Data type conversions
df1['no_of_adults'] = df1['no_of_adults'].astype(int)
df1['no_of_children'] = df1['no_of_children'].astype(int)
df1['lead_time'] = df1['lead_time'].astype(int)
df1['avg_price_per_room'] = df1['avg_price_per_room'].astype(float)

# Summary statistics
print(f"\nData Summary:")
print(f"  Total bookings: {len(df1)}")
print(f"  Date range: {df1['arrival_date_full'].min()} to {df1['arrival_date_full'].max()}")
print(f"  Cancellation rate: {(df1['booking_status'] == 'Canceled').mean() * 100:.2f}%")
print(f"  Avg price per room: £{df1['avg_price_per_room'].mean():.2f}")
print(f"  Avg lead time: {df1['lead_time'].mean():.1f} days")

# Save cleaned data
output_file1 = OUTPUT_PATH / "hotel_reservations_cleaned.xlsx"
with pd.ExcelWriter(output_file1, engine='openpyxl') as writer:
    df1.to_excel(writer, sheet_name="Cleaned_Data", index=False)

    # Summary sheet
    summary1 = pd.DataFrame({
        'Metric': ['Total Bookings', 'Canceled', 'Not Canceled', 'Cancellation Rate',
                   'Avg Price Per Room', 'Avg Total Nights', 'Avg Lead Time'],
        'Value': [
            len(df1),
            (df1['booking_status'] == 'Canceled').sum(),
            (df1['booking_status'] == 'Not_Canceled').sum(),
            f"{(df1['booking_status'] == 'Canceled').mean() * 100:.2f}%",
            f"£{df1['avg_price_per_room'].mean():.2f}",
            f"{df1['total_nights'].mean():.2f}",
            f"{df1['lead_time'].mean():.1f} days"
        ]
    })
    summary1.to_excel(writer, sheet_name="Summary", index=False)

print(f"\nSaved to: {output_file1}")

# ============================================================
# FILE 2: hotel_bookings.csv
# ============================================================
print("\n" + "=" * 60)
print("CLEANING: hotel_bookings.csv")
print("=" * 60)

# Try reading with different approaches
try:
    df2 = pd.read_csv(DATA_PATH / "hotel_bookings.csv")
except PermissionError:
    # Copy file first to avoid permission issues
    import shutil
    temp_path = OUTPUT_PATH / "hotel_bookings_temp.csv"
    shutil.copy(DATA_PATH / "hotel_bookings.csv", temp_path)
    df2 = pd.read_csv(temp_path)
    print(f"Read from temp file: {temp_path}")
print(f"\nOriginal shape: {df2.shape}")

# Check for duplicates
duplicates = df2.duplicated().sum()
print(f"Duplicate rows: {duplicates}")
if duplicates > 0:
    df2 = df2.drop_duplicates()
    print(f"Shape after removing duplicates: {df2.shape}")

# Check missing values
print(f"\nMissing values before cleaning:")
missing = df2.isnull().sum()
print(missing[missing > 0] if missing.any() else "  None")

# Handle missing values BEFORE any type conversions
# Fill children and babies first (they have few NaNs)
df2['children'] = df2['children'].fillna(0)
df2['babies'] = df2['babies'].fillna(0)

# agent and company have NaNs - these are valid (direct bookings)
df2['agent'] = df2['agent'].fillna(-1)  # -1 indicates no agent
df2['company'] = df2['company'].fillna(-1)  # -1 indicates no company
df2['country'] = df2['country'].fillna('Unknown')

# Convert data types (use nullable Int64 for agent/company)
df2['agent'] = df2['agent'].astype('Int64')
df2['company'] = df2['company'].astype('Int64')
df2['children'] = df2['children'].astype(int)
df2['babies'] = df2['babies'].astype(int)

print(f"\nMissing values after cleaning: {df2.isnull().sum().sum()}")

# Standardize column names
df2.columns = df2.columns.str.lower().str.replace(' ', '_')

# Create derived columns
df2['total_nights'] = df2['stays_in_weekend_nights'] + df2['stays_in_week_nights']
df2['total_guests'] = df2['adults'] + df2['children'] + df2['babies']
df2['total_revenue'] = df2['adr'] * df2['total_nights']

# Convert arrival date to datetime
df2['arrival_date_full'] = pd.to_datetime(
    df2['arrival_date_year'].astype(str) + '-' +
    df2['arrival_date_month'] + '-' +
    df2['arrival_date_day_of_month'].astype(str),
    errors='coerce'
)
df2['arrival_weekday'] = df2['arrival_date_full'].dt.day_name()
df2['arrival_month_num'] = df2['arrival_date_full'].dt.month

# Calculate RevPAR metrics
# Occupancy can be derived from room type assignments
df2['room_changed'] = (df2['reserved_room_type'] != df2['assigned_room_type']).astype(int)

# Summary statistics
print(f"\nData Summary:")
print(f"  Total bookings: {len(df2)}")
print(f"  Hotels: {df2['hotel'].unique()}")
print(f"  Date range: {df2['arrival_date_full'].min()} to {df2['arrival_date_full'].max()}")
print(f"  Cancellation rate: {df2['is_canceled'].mean() * 100:.2f}%")
print(f"  Avg daily rate (ADR): £{df2['adr'].mean():.2f}")
print(f"  Avg lead time: {df2['lead_time'].mean():.1f} days")

# Save cleaned data
output_file2 = OUTPUT_PATH / "hotel_bookings_cleaned.xlsx"
with pd.ExcelWriter(output_file2, engine='openpyxl') as writer:
    df2.to_excel(writer, sheet_name="Cleaned_Data", index=False)

    # Summary sheet
    summary2 = pd.DataFrame({
        'Metric': ['Total Bookings', 'Canceled', 'Not Canceled', 'Cancellation Rate',
                   'Avg Daily Rate (ADR)', 'Avg Total Nights', 'Avg Lead Time',
                   'Bookings with Agent', 'Bookings with Company'],
        'Value': [
            len(df2),
            df2['is_canceled'].sum(),
            (1 - df2['is_canceled']).sum(),
            f"{df2['is_canceled'].mean() * 100:.2f}%",
            f"£{df2['adr'].mean():.2f}",
            f"{df2['total_nights'].mean():.2f}",
            f"{df2['lead_time'].mean():.1f} days",
            (df2['agent'] > 0).sum(),
            (df2['company'] > 0).sum()
        ]
    })
    summary2.to_excel(writer, sheet_name="Summary", index=False)

    # Pivot tables
    # By hotel
    hotel_summary = df2.groupby('hotel').agg({
        'is_canceled': ['mean', 'sum', 'count'],
        'adr': 'mean',
        'total_nights': 'mean',
        'total_revenue': 'sum'
    }).round(2)
    hotel_summary.columns = ['_'.join(col).strip() for col in hotel_summary.columns]
    hotel_summary.to_excel(writer, sheet_name="By_Hotel")

    # By month
    monthly_summary = df2.groupby('arrival_date_month').agg({
        'is_canceled': 'mean',
        'adr': 'mean',
        'total_nights': 'mean',
        'total_revenue': 'sum'
    }).round(2)
    monthly_summary.to_excel(writer, sheet_name="By_Month")

print(f"\nSaved to: {output_file2}")

# ============================================================
# FINAL SUMMARY
# ============================================================
print("\n" + "=" * 60)
print("CLEANING COMPLETE")
print("=" * 60)

print(f"\nOutput files:")
print(f"  1. {output_file1}")
print(f"  2. {output_file2}")

print(f"\nFiles location: {OUTPUT_PATH}")
