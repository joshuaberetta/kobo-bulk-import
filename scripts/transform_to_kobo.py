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


def process_repeat_groups(df_raw, df_main, group_to_uuid_map):
    """
    Process repeat groups (FOCAL_POINTS and FIGURES_COMMUNITY) from raw data.
    
    Args:
        df_raw (pd.DataFrame): Original raw data with all columns
        df_main (pd.DataFrame): Main transformed data with UUIDs
        group_to_uuid_map (dict): Mapping of group keys to submission UUIDs
    
    Returns:
        tuple: (df_focal_points, df_figures_community)
    """
    
    # FOCAL_POINTS columns
    focal_points_cols = ['name', 'email', 'phone', 'job_title']
    
    # FIGURES_COMMUNITY columns (all the location and population data)
    figures_community_cols = [
        'position',
        'intro_community',
        'parish',
        'community',
        'location_type',
        'location_type_other',
        'location_address_comments',
        'quantity_resource',
        'budget_resource',
        'total_population_targeted',
        'total_population_reached',
        'category_of_people',
        'category_of_people_specify',
        'idp_household_targeted',
        'idp_household_reached',
        'warn_idp_targeted',
        'idp_people_targeted',
        'idp_women_targeted',
        'idp_men_targeted',
        'idp_children_targeted',
        'warn_idp_reached',
        'idp_people_reached',
        'idp_women_reached',
        'idp_men_reached',
        'idp_children_reached',
        'people_hosting_household_targeted',
        'people_hosting_household_reached',
        'warn_hosting_targeted',
        'hosting_people_targeted',
        'hosting_women_targeted',
        'hosting_men_targeted',
        'hosting_children_targeted',
        'warn_hosting_reached',
        'hosting_people_reached',
        'hosting_women_reached',
        'hosting_men_reached',
        'hosting_children_reached',
        'non_displaced_household_targeted',
        'non_displaced_household_reached',
        'warn_ndp_targeted',
        'ndp_people_targeted',
        'ndp_women_targeted',
        'ndp_men_targeted',
        'ndp_children_targeted',
        'warn_ndp_reached',
        'ndp_people_reached',
        'ndp_women_reached',
        'ndp_men_reached',
        'ndp_children_reached',
        'other_population_household_targeted',
        'other_population_household_reached',
        'warn_other_targeted',
        'other_people_targeted',
        'other_women_targeted',
        'other_men_targeted',
        'other_children_targeted',
        'warn_other_reached',
        'other_people_reached',
        'other_women_reached',
        'other_men_reached',
        'other_children_reached'
    ]
    
    # Grouping fields to determine which submission a row belongs to
    grouping_fields = ['LeadOrganization_name', 'LeadOrganization_name_2', 'activity_type', 'start_date', 'end_date']
    
    # Filter to only available grouping fields in raw data
    available_grouping_fields = [field for field in grouping_fields if field in df_raw.columns]
    
    # Format dates in raw data to match the formatted dates used in grouping
    df_raw_copy = df_raw.copy()
    for date_col in ['start_date', 'end_date']:
        if date_col in df_raw_copy.columns:
            df_raw_copy[date_col] = df_raw_copy[date_col].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and (isinstance(x, pd.Timestamp) or isinstance(x, datetime)) else x
            )
    
    # Process FOCAL_POINTS
    df_focal_points = None
    focal_points_available = [col for col in focal_points_cols if col in df_raw_copy.columns]
    
    if focal_points_available:
        focal_points_data = []
        for idx, row in df_raw_copy.iterrows():
            # Create group key from this row
            group_key = tuple(
                str(row[field]) if pd.notna(row[field]) else '' 
                for field in available_grouping_fields
            )
            
            uuid = group_to_uuid_map.get(group_key)
            if uuid:
                # Create entry with all available columns
                focal_entry = {}
                for col in focal_points_available:
                    focal_entry[col] = row[col] if pd.notna(row[col]) else None
                
                # Only add if there's at least email
                if focal_entry.get('email'):
                    focal_entry['_submission__uuid'] = uuid
                    focal_points_data.append(focal_entry)
        
        if focal_points_data:
            df_focal_points = pd.DataFrame(focal_points_data)
            # Remove duplicate focal points for the same submission
            df_focal_points = df_focal_points.drop_duplicates(subset=['email', '_submission__uuid'])
            # Ensure proper column order
            cols = [col for col in focal_points_available if col in df_focal_points.columns]
            df_focal_points = df_focal_points[cols + ['_submission__uuid']]
            print(f"Processed FOCAL_POINTS: {len(df_focal_points)} entries")
    
    # Process FIGURES_COMMUNITY
    df_figures_community = None
    figures_available = [col for col in figures_community_cols if col in df_raw_copy.columns]
    
    if figures_available:
        figures_data = []
        for idx, row in df_raw_copy.iterrows():
            # Create group key from this row
            group_key = tuple(
                str(row[field]) if pd.notna(row[field]) else '' 
                for field in available_grouping_fields
            )
            
            uuid = group_to_uuid_map.get(group_key)
            if uuid:
                # Create entry with all available columns
                community_entry = {}
                has_data = False
                
                for col in figures_available:
                    value = row[col] if pd.notna(row[col]) else None
                    community_entry[col] = value
                    # Check if this row has any meaningful data
                    if value is not None and col in ['parish', 'community', 'quantity_resource', 
                                                       'budget_resource', 'category_of_people', 
                                                       'location_type', 'total_population_targeted',
                                                       'total_population_reached']:
                        has_data = True
                
                # Only add if there's at least some community data
                if has_data:
                    community_entry['_submission__uuid'] = uuid
                    figures_data.append(community_entry)
        
        if figures_data:
            df_figures_community = pd.DataFrame(figures_data)
            # Ensure proper column order - put _submission__uuid last
            cols = [col for col in figures_available if col in df_figures_community.columns]
            df_figures_community = df_figures_community[cols + ['_submission__uuid']]
            print(f"Processed FIGURES_COMMUNITY: {len(df_figures_community)} entries")
    
    return df_focal_points, df_figures_community


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
    # These are the main submission columns (not in repeat groups)
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
        'sector_label',
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
        'resource_unit_type_other',
        'start_date',
        'end_date',
        'instruction_add_community'
    ]
    
    # Check if deprecatedID column exists (for editing existing submissions)
    if 'deprecatedID' in df.columns:
        kobo_columns.append('deprecatedID')
    
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
    
    # Format date columns to yyyy-mm-dd
    for date_col in ['start_date', 'end_date']:
        if date_col in df_kobo.columns:
            df_kobo[date_col] = df_kobo[date_col].apply(
                lambda x: x.strftime('%Y-%m-%d') if pd.notna(x) and (isinstance(x, pd.Timestamp) or isinstance(x, datetime)) else x
            )
    
    # Group rows by combination of key fields
    # Fields that define a unique submission:
    grouping_fields = ['LeadOrganization_name', 'LeadOrganization_name_2', 'activity_type', 'start_date', 'end_date']
    
    # Filter grouping fields to only those that exist in the dataframe
    available_grouping_fields = [field for field in grouping_fields if field in df_kobo.columns]
    
    print(f"\nGrouping submissions by: {', '.join(available_grouping_fields)}")
    
    # Create a grouping key for each row
    df_kobo['_group_key'] = df_kobo[available_grouping_fields].apply(
        lambda row: tuple(str(val) if pd.notna(val) else '' for val in row),
        axis=1
    )
    
    # Get unique groups and create one submission per group
    unique_groups = df_kobo['_group_key'].unique()
    
    # Create mapping of group key to UUID
    group_to_uuid_map = {group: generate_uuid() for group in unique_groups}
    
    # Add UUID to each row based on its group
    df_kobo['_submission__uuid'] = df_kobo['_group_key'].map(group_to_uuid_map)
    
    # For the main data sheet, we only want one row per unique group
    # Take the first row of each group as the main submission
    df_main = df_kobo.groupby('_group_key', as_index=False).first()
    
    # Remove the temporary _group_key column from main data
    if '_group_key' in df_main.columns:
        df_main = df_main.drop(columns=['_group_key'])
    
    print(f"Raw data rows: {len(df_kobo)}")
    print(f"Unique submissions (after grouping): {len(df_main)}")
    print(f"Transformed main data: {len(df_main)} rows, {len(df_main.columns)} columns")
    
    # Process repeat groups: FOCAL_POINTS and FIGURES_COMMUNITY
    # Pass the original df (with all rows) and the group_to_uuid_map
    df_focal_points, df_figures_community = process_repeat_groups(df, df_main, group_to_uuid_map)
    
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
    
    # Save to Excel with multiple sheets
    print(f"Saving transformed data to: {output_file}")
    with pd.ExcelWriter(output_file, engine='openpyxl') as writer:
        # Main sheet
        df_main.to_excel(writer, sheet_name='data', index=False)
        
        # Repeat group sheets
        if df_focal_points is not None and len(df_focal_points) > 0:
            df_focal_points.to_excel(writer, sheet_name='FOCAL_POINTS', index=False)
            print(f"  ✓ FOCAL_POINTS: {len(df_focal_points)} rows")
        
        if df_figures_community is not None and len(df_figures_community) > 0:
            df_figures_community.to_excel(writer, sheet_name='FIGURES_COMMUNITY', index=False)
            print(f"  ✓ FIGURES_COMMUNITY: {len(df_figures_community)} rows")
    
    print(f"✓ Successfully transformed {len(df_main)} main records")
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
