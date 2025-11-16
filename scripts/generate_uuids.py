#!/usr/bin/env python3
"""
UUID Generator for Editing Submissions

This helper script generates new UUIDs for editing existing submissions.
It can read an Excel file with deprecatedID values and add new _submission__uuid values.

Usage:
    # Generate N random UUIDs
    python scripts/generate_uuids.py --count 10
    
    # Add UUIDs to an Excel file (reads deprecatedID, adds new _submission__uuid)
    python scripts/generate_uuids.py --excel data/edits.xlsx --output data/edits_with_uuids.xlsx
    
    # Generate and copy to clipboard (macOS)
    python scripts/generate_uuids.py --count 5 --clipboard
"""

import uuid
import argparse
import sys
import pandas as pd


def generate_uuids(count):
    """Generate a list of UUIDs."""
    return [str(uuid.uuid4()) for _ in range(count)]


def add_uuids_to_excel(input_file, output_file=None, sheet_name='data'):
    """
    Add new _submission__uuid values to an Excel file.
    
    Args:
        input_file: Path to input Excel file
        output_file: Path to output Excel file (optional)
        sheet_name: Name of the sheet to process (default: 'data')
    """
    # Read the Excel file
    df = pd.read_excel(input_file, sheet_name=sheet_name)
    
    # Check if deprecatedID column exists
    if 'deprecatedID' not in df.columns:
        print("Warning: 'deprecatedID' column not found in Excel file.")
        print("Creating column with empty values.")
        df['deprecatedID'] = ''
    
    # Check if _submission__uuid already exists
    if '_submission__uuid' in df.columns:
        print("Warning: '_submission__uuid' column already exists.")
        response = input("Overwrite existing UUIDs? (y/N): ").strip().lower()
        if response != 'y':
            print("Aborted. No changes made.")
            return
    
    # Generate new UUIDs for each row
    df['_submission__uuid'] = [str(uuid.uuid4()) for _ in range(len(df))]
    
    # Determine output file
    if output_file is None:
        output_file = input_file.replace('.xlsx', '_with_uuids.xlsx')
    
    # Save to Excel
    df.to_excel(output_file, sheet_name=sheet_name, index=False)
    
    print(f"✓ Added {len(df)} new UUIDs")
    print(f"✓ Saved to: {output_file}")
    print(f"\nNext steps:")
    print(f"1. Review {output_file}")
    print(f"2. Ensure 'deprecatedID' column has the original UUIDs")
    print(f"3. Submit: python submit.py --config config/config.json")


def main():
    parser = argparse.ArgumentParser(
        description='Generate UUIDs for editing submissions',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  # Generate 10 UUIDs and print them
  python generate_uuids.py --count 10
  
  # Add UUIDs to an Excel file
  python generate_uuids.py --excel data/edits.xlsx
  
  # Specify output file
  python generate_uuids.py --excel data/edits.xlsx --output data/ready_to_submit.xlsx
  
  # Generate one UUID (quick)
  python generate_uuids.py
        '''
    )
    
    parser.add_argument('-c', '--count', type=int, default=1,
                       help='Number of UUIDs to generate (default: 1)')
    parser.add_argument('-e', '--excel', 
                       help='Excel file to add UUIDs to')
    parser.add_argument('-o', '--output',
                       help='Output Excel file (optional, will auto-generate if not provided)')
    parser.add_argument('-s', '--sheet', default='data',
                       help='Sheet name to process (default: "data")')
    parser.add_argument('--clipboard', action='store_true',
                       help='Copy UUIDs to clipboard (macOS only)')
    
    args = parser.parse_args()
    
    # If Excel file provided, add UUIDs to it
    if args.excel:
        add_uuids_to_excel(args.excel, args.output, args.sheet)
    else:
        # Just generate and print UUIDs
        uuids = generate_uuids(args.count)
        
        if args.count == 1:
            print(uuids[0])
        else:
            print(f"\n{args.count} UUIDs generated:\n")
            for i, uuid_str in enumerate(uuids, 1):
                print(f"{i}. {uuid_str}")
        
        # Copy to clipboard if requested (macOS only)
        if args.clipboard:
            try:
                import subprocess
                uuid_text = '\n'.join(uuids)
                subprocess.run(['pbcopy'], input=uuid_text.encode(), check=True)
                print(f"\n✓ Copied to clipboard")
            except Exception as e:
                print(f"\n✗ Could not copy to clipboard: {e}")


if __name__ == '__main__':
    main()
