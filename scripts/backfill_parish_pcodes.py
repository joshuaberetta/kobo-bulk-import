#!/usr/bin/env python3
"""
Backfill missing parish pcodes in Excel files based on community names.

This script uses the odpem.geojson reference data to map community names
to their corresponding parish pcodes. It looks for rows where a community
is specified but the parish is missing, then fills in the parish based on
the community-to-parish mapping from the GeoJSON.

Usage:
    python scripts/backfill_parish_pcodes.py <input_excel> [output_excel]

Examples:
    # Backfill and save to new file
    python scripts/backfill_parish_pcodes.py raw-data/20251116-one-love.xlsx raw-data/20251116-one-love-filled.xlsx
    
    # Backfill and overwrite original file
    python scripts/backfill_parish_pcodes.py raw-data/20251116-one-love.xlsx
"""

import json
import sys
import pandas as pd
from pathlib import Path
from difflib import get_close_matches


def load_geojson_mapping(geojson_path='reference/odpem.geojson'):
    """Load the GeoJSON and create a community-to-parish mapping."""
    with open(geojson_path, 'r') as f:
        data = json.load(f)
    
    # Create mapping: community_name -> parish info
    community_to_parish = {}
    
    for feature in data['features']:
        props = feature['properties']
        community_name = props.get('ADM2_EN', '').strip()
        parish_pcode = props.get('ADM1_PCODE', '').strip()
        parish_name = props.get('ADM1_EN', '').strip()
        community_pcode = props.get('ADM2_PCODE', '').strip()
        
        if community_name:
            # Store both original and lowercase for case-insensitive matching
            key = community_name.lower()
            community_to_parish[key] = {
                'parish_pcode': parish_pcode,
                'parish_name': parish_name,
                'community_pcode': community_pcode,
                'community_name': community_name
            }
    
    return community_to_parish


def normalize_name(name):
    """Normalize a name for fuzzy matching."""
    if pd.isna(name):
        return ''
    return str(name).strip().lower()


def find_parish_for_community(community_name, mapping, fuzzy=True):
    """
    Find parish information for a given community name.
    
    Args:
        community_name: The community name to look up
        mapping: The community-to-parish mapping dictionary
        fuzzy: If True, attempt fuzzy matching when exact match fails
    
    Returns:
        Dictionary with parish info, or None if not found
    """
    if pd.isna(community_name):
        return None
    
    normalized = normalize_name(community_name)
    
    # Try exact match first
    if normalized in mapping:
        return mapping[normalized]
    
    # Try fuzzy matching
    if fuzzy:
        matches = get_close_matches(normalized, mapping.keys(), n=1, cutoff=0.85)
        if matches:
            return mapping[matches[0]]
    
    return None


def backfill_parish_pcodes(input_file, output_file=None, geojson_path='reference/odpem.geojson',
                           parish_col='parish', community_col='community', dry_run=False):
    """
    Backfill missing parish pcodes in an Excel file based on community names.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file (if None, overwrites input_file)
        geojson_path: Path to the GeoJSON reference file
        parish_col: Name of the parish column
        community_col: Name of the community column
        dry_run: If True, only show what would be changed without saving
    
    Returns:
        DataFrame with backfilled data
    """
    # Load the mapping
    print(f"Loading GeoJSON mapping from {geojson_path}...")
    mapping = load_geojson_mapping(geojson_path)
    print(f"Loaded {len(mapping)} community-to-parish mappings")
    
    # Load the Excel file
    print(f"\nLoading Excel file from {input_file}...")
    df = pd.read_excel(input_file)
    print(f"Loaded {len(df)} rows")
    
    # Check if required columns exist
    if parish_col not in df.columns:
        raise ValueError(f"Parish column '{parish_col}' not found in Excel file")
    if community_col not in df.columns:
        raise ValueError(f"Community column '{community_col}' not found in Excel file")
    
    # Find rows that need backfilling
    needs_backfill = (df[community_col].notna()) & (df[parish_col].isna())
    num_to_backfill = needs_backfill.sum()
    
    print(f"\nFound {num_to_backfill} rows with community but no parish")
    
    if num_to_backfill == 0:
        print("No rows need backfilling!")
        return df
    
    # Process each row that needs backfilling
    backfilled_count = 0
    not_found_count = 0
    not_found_communities = set()
    
    for idx in df[needs_backfill].index:
        community = df.loc[idx, community_col]
        parish_info = find_parish_for_community(community, mapping)
        
        if parish_info:
            # Backfill the parish with the parish name from GeoJSON
            df.loc[idx, parish_col] = parish_info['parish_name']
            backfilled_count += 1
            
            if dry_run:
                print(f"  Row {idx}: '{community}' -> '{parish_info['parish_name']}' (pcode: {parish_info['parish_pcode']})")
        else:
            not_found_count += 1
            not_found_communities.add(str(community))
            if dry_run:
                print(f"  Row {idx}: '{community}' -> NOT FOUND in GeoJSON")
    
    # Summary
    print(f"\nBackfill Summary:")
    print(f"  Successfully backfilled: {backfilled_count}")
    print(f"  Not found in GeoJSON: {not_found_count}")
    
    if not_found_communities:
        print(f"\nCommunities not found in GeoJSON:")
        for comm in sorted(not_found_communities):
            print(f"  - {comm}")
    
    # Save the file
    if not dry_run:
        output_path = output_file if output_file else input_file
        print(f"\nSaving to {output_path}...")
        df.to_excel(output_path, index=False)
        print("Done!")
    else:
        print("\n[DRY RUN] No changes saved.")
    
    return df


def main():
    """Main entry point for the script."""
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    input_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    # Check if input file exists
    if not Path(input_file).exists():
        print(f"Error: Input file '{input_file}' not found!")
        sys.exit(1)
    
    # Run the backfill
    backfill_parish_pcodes(input_file, output_file, dry_run=False)


if __name__ == '__main__':
    main()
