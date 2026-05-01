"""
Data Consolidation Script - VisitBritain Hotel Occupancy Data
Section 3: Data Cleaning for #2 - VisitBritain Hotel Occupancy

This script:
1. Reads the extracted Excel data
2. Identifies and consolidates key metrics (Occupancy, Room Rates, RevPAR)
3. Creates a unified clean dataset by region and time period
4. Exports final cleaned Excel file
"""

import pandas as pd
from pathlib import Path
import re
import warnings

warnings.filterwarnings('ignore')

# Define paths
RAW_DATA_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\visitbritain\visitbritain_hotel_occupancy_raw.xlsx")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\visitbritain")

print("=" * 60)
print("VISITBRITAIN HOTEL OCCUPANCY - DATA CONSOLIDATION")
print("=" * 60)

# Read the extraction summary to understand what we have
summary_df = pd.read_csv(OUTPUT_PATH / "extraction_summary.csv")
print(f"\nTotal tables extracted: {len(summary_df)}")

# Read all sheets from the Excel file
xl_file = pd.ExcelFile(RAW_DATA_PATH)
sheet_names = xl_file.sheet_names
print(f"Sheets in Excel file: {len(sheet_names)}")

# Function to identify table type based on content
def identify_table_type(df):
    """Identify what type of data the table contains"""
    text_content = ' '.join(df.astype(str).values.flatten()).lower()

    if 'occupancy' in text_content:
        return 'occupancy'
    elif 'revpar' in text_content or 'revenue per available room' in text_content:
        return 'revpar'
    elif 'adr' in text_content or 'average daily rate' in text_content:
        return 'adr'
    elif 'room' in text_content and 'rate' in text_content:
        return 'room_rate'
    elif 'bookings' in text_content or 'rooms' in text_content:
        return 'bookings'
    else:
        return 'other'

# Function to extract region from table
def extract_region(df):
    """Extract region name from table"""
    text_content = ' '.join(df.astype(str).values.flatten())

    regions = ['England', 'London', 'South East', 'South West', 'East of England',
               'East Midlands', 'West Midlands', 'Yorkshire', 'North East', 'North West',
               'Derbyshire', 'Dorset', 'Greater Manchester', 'Liverpool', 'Leicester',
               'Birmingham', 'Bristol', 'Leeds', 'Sheffield', 'Newcastle', 'Nottingham']

    for region in regions:
        if region.lower() in text_content.lower():
            return region

    return 'England'  # Default

# Function to clean and standardize table data
def clean_table_data(df, source_info):
    """Clean a single table's data"""
    # Remove empty rows and columns
    df = df.dropna(how='all', axis=0).dropna(how='all', axis=1)

    # Use first row as header if it looks like headers
    if len(df) > 1:
        # Check if first row has unique values (likely headers)
        if len(df.columns) == len(set(df.columns)):
            new_header = df.iloc[0]
            df = df[1:]
            df.columns = new_header

    # Reset index
    df = df.reset_index(drop=True)

    return df

# Collect all data with metadata
all_clean_data = []

print("\nProcessing tables...")
for sheet in sheet_names[:100]:
    try:
        df = pd.read_excel(RAW_DATA_PATH, sheet_name=sheet)

        if df.shape[0] < 3 or df.shape[1] < 2:
            continue

        # Identify table characteristics
        table_type = identify_table_type(df)
        region = extract_region(df)

        # Get year/month from sheet name lookup
        sheet_info = summary_df[summary_df.apply(lambda x: f"Table_{int(x.name)+1:03d}" == sheet, axis=1)]

        year = "Unknown"
        month = "Unknown"
        source_file = "Unknown"

        if len(sheet_info) > 0:
            year = sheet_info['year'].values[0]
            month = sheet_info['month'].values[0]
            source_file = sheet_info['source_file'].values[0]

        # Only keep relevant tables
        if table_type in ['occupancy', 'revpar', 'adr', 'room_rate']:
            cleaned_df = clean_table_data(df, sheet_info)

            all_clean_data.append({
                'source_sheet': sheet,
                'source_file': source_file,
                'year': year,
                'month': month,
                'table_type': table_type,
                'region': region,
                'data': cleaned_df,
                'shape': cleaned_df.shape
            })

            print(f"  {sheet}: {table_type} - {region} - {cleaned_df.shape}")

    except Exception as e:
        print(f"  Error processing {sheet}: {e}")

print(f"\nIdentified {len(all_clean_data)} relevant data tables")

# Create consolidated output Excel
output_excel_path = OUTPUT_PATH / "visitbritain_consolidated.xlsx"

with pd.ExcelWriter(output_excel_path, engine='openpyxl') as writer:
    # Summary sheet
    summary_output = pd.DataFrame([{
        'source_sheet': d['source_sheet'],
        'source_file': d['source_file'],
        'year': d['year'],
        'month': d['month'],
        'table_type': d['table_type'],
        'region': d['region'],
        'rows': d['shape'][0],
        'columns': d['shape'][1]
    } for d in all_clean_data])

    summary_output.to_excel(writer, sheet_name="Summary", index=False)

    # Create sheets by table type
    for table_type in ['occupancy', 'revpar', 'adr', 'room_rate']:
        type_data = [d for d in all_clean_data if d['table_type'] == table_type]

        if type_data:
            # Combine all dataframes of this type
            combined_df = pd.concat([d['data'] for d in type_data], ignore_index=True)

            if len(combined_df) > 0:
                sheet_name = f"{table_type.upper()}_Data"
                combined_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                print(f"  Saved {sheet_name}: {combined_df.shape}")

    # Create sheets by year
    for year in sorted(set(d['year'] for d in all_clean_data if d['year'] != 'Unknown')):
        year_data = [d for d in all_clean_data if d['year'] == year]

        if year_data:
            try:
                combined_df = pd.concat([d['data'] for d in year_data], ignore_index=True)

                if len(combined_df) > 0:
                    sheet_name = f"Year_{year}"
                    combined_df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
                    print(f"  Saved {sheet_name}: {combined_df.shape}")
            except Exception as e:
                print(f"  Error saving Year_{year}: {e}")

xl_file.close()

print(f"\nConsolidated data saved to: {output_excel_path}")

# Create a final summary report
print("\n" + "=" * 60)
print("CONSOLIDATION SUMMARY")
print("=" * 60)

print(f"\nBy Table Type:")
for table_type in ['occupancy', 'revpar', 'adr', 'room_rate']:
    count = len([d for d in all_clean_data if d['table_type'] == table_type])
    print(f"  {table_type.upper()}: {count} tables")

print(f"\nBy Year:")
for year in sorted(set(d['year'] for d in all_clean_data if d['year'] != 'Unknown')):
    count = len([d for d in all_clean_data if d['year'] == year])
    print(f"  {year}: {count} tables")

print(f"\nBy Region:")
for region in sorted(set(d['region'] for d in all_clean_data)):
    count = len([d for d in all_clean_data if d['region'] == region])
    print(f"  {region}: {count} tables")

print("\n" + "=" * 60)
print("CONSOLIDATION COMPLETE")
print("=" * 60)
