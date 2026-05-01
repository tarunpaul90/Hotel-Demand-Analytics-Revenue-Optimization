"""
Data Extraction Script - VisitBritain Hotel Occupancy Data
Section 3: Data Cleaning for #2 - VisitBritain Hotel Occupancy

This script:
1. Reads all PDF files from the VisitBritain Hotel Occupancy folder
2. Extracts tables from each PDF
3. Cleans and standardizes the data
4. Exports to Excel format
"""

import pdfplumber
import pandas as pd
from pathlib import Path
import re
from datetime import datetime
import warnings

warnings.filterwarnings('ignore')

# Define paths
DATA_PATH = Path(r"C:\Users\HP\Music\new project\#2 — VisitBritain Hotel Occupancy")
OUTPUT_PATH = Path(r"C:\Users\HP\Hotel_RevPAR_Project\data\visitbritain")

# Create output directory
OUTPUT_PATH.mkdir(parents=True, exist_ok=True)

print("=" * 60)
print("VISITBRITAIN HOTEL OCCUPANCY - PDF TO EXCEL EXTRACTION")
print("=" * 60)

# Get all PDF files
pdf_files = list(DATA_PATH.rglob("*.pdf"))
print(f"\nFound {len(pdf_files)} PDF files")

def extract_month_year_from_filename(filename):
    """Extract month and year from PDF filename"""
    name = filename.stem.lower()

    # Year patterns
    year_match = re.search(r'(20\d{2})', name)
    year = year_match.group(1) if year_match else "Unknown"

    # Month patterns
    months = {
        'january': '01', 'february': '02', 'march': '03', 'april': '04',
        'may': '05', 'june': '06', 'july': '07', 'august': '08',
        'september': '09', 'october': '10', 'november': '11', 'december': '12'
    }

    month = "Unknown"
    for month_name, month_num in months.items():
        if month_name in name:
            month = month_num
            break

    # Handle multi-month reports (e.g., "may, june, july and august")
    multi_months = re.findall(r'(january|february|march|april|may|june|july|august|september|october|november|december)', name)
    if len(multi_months) > 1:
        month = "Multi"

    return month, year

def extract_tables_from_pdf(pdf_path):
    """Extract all tables from a PDF file"""
    all_tables = []

    try:
        with pdfplumber.open(pdf_path) as pdf:
            print(f"\n  Processing: {pdf_path.name}")
            print(f"  Pages: {len(pdf.pages)}")

            for page_num, page in enumerate(pdf.pages, 1):
                tables = page.extract_tables()
                if tables:
                    print(f"    Page {page_num}: Found {len(tables)} table(s)")
                    for table_idx, table in enumerate(tables):
                        if table and len(table) > 1:  # Has data
                            df = pd.DataFrame(table)
                            all_tables.append({
                                'page': page_num,
                                'table_idx': table_idx,
                                'dataframe': df,
                                'shape': df.shape
                            })
    except Exception as e:
        print(f"  Error: {e}")

    return all_tables

# Process each PDF and collect data
all_data = []

for i, pdf_file in enumerate(pdf_files, 1):
    print(f"\n[{i}/{len(pdf_files)}] {pdf_file.name}")

    # Extract metadata from filename
    month, year = extract_month_year_from_filename(pdf_file)

    # Extract tables
    tables = extract_tables_from_pdf(pdf_file)

    for table_info in tables:
        df = table_info['dataframe']

        # Only keep tables with meaningful data (more than 2 rows and 2 columns)
        if df.shape[0] > 2 and df.shape[1] > 1:
            all_data.append({
                'source_file': pdf_file.name,
                'year': year,
                'month': month,
                'page': table_info['page'],
                'dataframe': df
            })

print("\n" + "=" * 60)
print(f"Extracted {len(all_data)} tables from {len(pdf_files)} PDFs")
print("=" * 60)

# Save each table to Excel
print("\nSaving tables to Excel...")

excel_output_path = OUTPUT_PATH / "visitbritain_hotel_occupancy_raw.xlsx"

with pd.ExcelWriter(excel_output_path, engine='openpyxl') as writer:
    for idx, data in enumerate(all_data[:100], 1):  # Limit to 100 tables
        df = data['dataframe']
        sheet_name = f"Table_{idx:03d}"

        # Excel sheet name max length is 31
        try:
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
            print(f"  Saved: {sheet_name} - {df.shape}")
        except Exception as e:
            print(f"  Error saving {sheet_name}: {e}")

print(f"\nRaw data saved to: {excel_output_path}")

# Create a summary file
summary_df = pd.DataFrame([{
    'source_file': d['source_file'],
    'year': d['year'],
    'month': d['month'],
    'page': d['page'],
    'rows': d['dataframe'].shape[0],
    'columns': d['dataframe'].shape[1]
} for d in all_data])

summary_path = OUTPUT_PATH / "extraction_summary.csv"
summary_df.to_csv(summary_path, index=False)
print(f"Summary saved to: {summary_path}")

print("\n" + "=" * 60)
print("EXTRACTION COMPLETE")
print("=" * 60)
