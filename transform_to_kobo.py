#!/usr/bin/env python3
"""
Transform 5W offline form data to Kobo import format.

This script reads Excel files from the raw-data directory and transforms them
into the format required for importing to Kobo, saving the result to the data directory.

Works with any organization's 5W offline form data.

Input: raw-data/*.xlsx
Output: data/*_kobo_import_YYYYMMDD.xlsx
"""

import pandas as pd
import uuid
from datetime import datetime
import os
import sys
import argparse


def generate_uuid():
    """Generate a UUID for submission tracking."""
    return str(uuid.uuid4())


def detect_header_row(df, max_rows=20):
    """
    Automatically detect which row contains the actual headers with data below.
    
    Args:
        df (pd.DataFrame): DataFrame with header=None
        max_rows (int): Maximum rows to search for headers
    
    Returns:
        int: Row index containing headers (0-based)
    """
    # Look for rows containing known Kobo field names
    key_fields = ['LeadOrganization_type', 'sector', 'activity_type', 'activity_title', 'same_as_lead']
    
    potential_headers = []
    
    for i in range(min(max_rows, len(df))):
        row_values = df.iloc[i].astype(str).tolist()
        # Check if this row contains at least 3 of our key fields (exact match)
        matches = sum(1 for field in key_fields if field in row_values)
        if matches >= 3:
            potential_headers.append(i)
    
    # If we found multiple header rows, prefer the one with consistent data below
    if potential_headers:
        best_header = potential_headers[-1]  # Default to last occurrence
        
        if len(potential_headers) > 1:
            max_score = -1
            for header_idx in potential_headers:
                # Score based on consistent data in rows below (not just filled, but consistent)
                score = 0
                prev_fill = None
                
                for j in range(header_idx + 1, min(header_idx + 6, len(df))):
                    fill_pct = df.iloc[j].notna().sum() / len(df.columns)
                    
                    # Data rows should have moderate fill (10-50% typically) and be consistent
                    if 0.10 <= fill_pct <= 0.50:
                        score += 2
                        # Bonus for consistency
                        if prev_fill is not None and abs(fill_pct - prev_fill) < 0.05:
                            score += 1
                        prev_fill = fill_pct
                    elif fill_pct < 0.10:  # Sparse/instruction rows
                        score -= 1
                
                if score > max_score:
                    max_score = score
                    best_header = header_idx
        
        return best_header
    
    # Default to row 8 (index 8) if not found
    print("Warning: Could not auto-detect header row, using default row 9 (index 8)")
    return 8


def transform_to_kobo_format(input_file, output_file=None, sheet_name='Data Entry', header_row=None):
    """
    Transform 5W offline form data to Kobo import format.
    
    Args:
        input_file (str): Path to the raw Excel file
        output_file (str): Path for the output file (optional)
        sheet_name (str): Name of the sheet to read (default: 'Data Entry')
        header_row (int): Row number containing headers (0-based). If None, auto-detect.
    
    Returns:
        str: Path to the output file
    """
    
    print(f"Reading raw data from: {input_file}")
    
    # Auto-detect header row if not specified
    if header_row is None:
        print("Auto-detecting header row...")
        df_temp = pd.read_excel(input_file, sheet_name=sheet_name, header=None)
        header_row = detect_header_row(df_temp)
        print(f"Detected header at row {header_row + 1}")
    
    # Read the raw data from the specified sheet, starting from the header row
    df = pd.read_excel(input_file, sheet_name=sheet_name, header=header_row)
    
    print(f"Read {len(df)} rows from raw data file")
    
    # Define the columns needed for Kobo import (excluding _submission__uuid which we'll add)
    kobo_columns = [
        'LeadOrganization_type',
        'LeadOrganization_type_2',
        'LeadOrganization_name',
        'LeadOrganization_name_2',
        'same_as_lead',
        'ImplementingOrganization_type',
        'ImplementingOrganization_type_2',
        'ImplementingOrganization_name',
        'ImplementingOrganization_name_2',
        'sector',
        'scetor_2',
        'activity_type',
        'activity_type_other',
        'activity_title',
        'activity_Status',
        'comments',
        'URL_to_important_resources',
        'resource_type',
        'resource_type_other',
        'resource_unit_type',
        'resource_unit_type_other'
    ]
    
    # Verify all columns exist in the raw data
    missing_columns = [col for col in kobo_columns if col not in df.columns]
    if missing_columns:
        print(f"Warning: The following columns are missing from the raw data: {missing_columns}")
        # Filter to only include columns that exist
        kobo_columns = [col for col in kobo_columns if col in df.columns]
    
    # Select only the columns needed for Kobo import
    df_kobo = df[kobo_columns].copy()
    
    # Remove rows where all values are NaN
    df_kobo = df_kobo.dropna(how='all')
    
    # Generate UUID for each row
    df_kobo['_submission__uuid'] = [generate_uuid() for _ in range(len(df_kobo))]
    
    print(f"Transformed data: {len(df_kobo)} rows, {len(df_kobo.columns)} columns")
    
    # Determine output file path
    if output_file is None:
        timestamp = datetime.now().strftime('%Y%m%d')
        # Extract base filename without extension
        base_name = os.path.splitext(os.path.basename(input_file))[0]
        # Remove common suffixes like (2), _raw, etc.
        base_name = base_name.replace('(2)', '').replace('_raw', '').strip()
        output_file = f'data/{base_name}_kobo_import_{timestamp}.xlsx'
    
    # Create output directory if it doesn't exist
    output_dir = os.path.dirname(output_file)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)
    
    # Save to Excel
    print(f"Saving transformed data to: {output_file}")
    df_kobo.to_excel(output_file, index=False)
    
    print(f"✓ Successfully transformed {len(df_kobo)} records")
    print(f"✓ Output file: {output_file}")
    
    return output_file


def main():
    """Main function to run the transformation."""
    
    parser = argparse.ArgumentParser(
        description='Transform 5W offline form data to Kobo import format',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Process a specific file (auto-detects header row)
  python transform_to_kobo.py raw-data/Organization_5W_Form.xlsx
  
  # Specify custom output location
  python transform_to_kobo.py raw-data/Organization_5W_Form.xlsx data/output.xlsx
  
  # Specify sheet name and header row
  python transform_to_kobo.py input.xlsx -s "Data Entry" -r 8
  
  # Process with all options
  python transform_to_kobo.py input.xlsx output.xlsx -s "Sheet1" -r 5
        '''
    )
    
    parser.add_argument('input_file', 
                        help='Path to the input Excel file')
    parser.add_argument('output_file', nargs='?', default=None,
                        help='Path to the output Excel file (optional, will auto-generate if not provided)')
    parser.add_argument('-s', '--sheet', default='Data Entry',
                        help='Name of the sheet to read (default: "Data Entry")')
    parser.add_argument('-r', '--header-row', type=int, default=None,
                        help='Row number containing headers (0-based). If not specified, will auto-detect.')
    
    args = parser.parse_args()
    
    # Check if input file exists
    if not os.path.exists(args.input_file):
        print(f"Error: Input file not found: {args.input_file}")
        sys.exit(1)
    
    # Run the transformation
    try:
        transform_to_kobo_format(
            input_file=args.input_file,
            output_file=args.output_file,
            sheet_name=args.sheet,
            header_row=args.header_row
        )
    except Exception as e:
        print(f"\nError during transformation: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
