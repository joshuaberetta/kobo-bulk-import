#!/usr/bin/env python3
"""
Example: Complete workflow demonstration

This script shows the complete workflow from Excel to XML to KoboToolbox.
It uses the provided sample data to demonstrate each step.
"""

from excel_to_kobo_xml import ExcelToKoboXML
from pathlib import Path
import json


def example_basic_conversion():
    """Example 1: Basic conversion to XML files."""
    print("\n" + "="*60)
    print("EXAMPLE 1: Basic Conversion")
    print("="*60 + "\n")
    
    converter = ExcelToKoboXML(
        excel_path='../uploads/345WData_md103-edit_copy.xlsx',
        mapping_path='../uploads/question-mapping.json',
        form_id='aiBgJcvz5AFHB54fKpG2y5'
    )
    
    # Convert all submissions
    submissions = converter.convert_all(output_dir='./example_output')
    
    print(f"✓ Converted {len(submissions)} submissions")
    print(f"✓ XML files saved to ./example_output/\n")
    
    return submissions


def example_get_xml_string():
    """Example 2: Get XML as string (for direct API use)."""
    print("\n" + "="*60)
    print("EXAMPLE 2: Get XML as String")
    print("="*60 + "\n")
    
    converter = ExcelToKoboXML(
        excel_path='../uploads/345WData_md103-edit_copy.xlsx',
        mapping_path='../uploads/question-mapping.json'
    )
    
    # Get one submission as XML string
    uuid = 'b12be739-107b-49d7-914e-b177ac7ec5d0'
    xml_string = converter.convert_submission(uuid)
    
    print(f"XML for {uuid}:")
    print("-" * 60)
    print(xml_string[:500] + "...")
    print("-" * 60)
    print(f"\nXML length: {len(xml_string)} characters\n")
    
    return xml_string


def example_filtering():
    """Example 3: Convert only specific submissions."""
    print("\n" + "="*60)
    print("EXAMPLE 3: Filtering Submissions")
    print("="*60 + "\n")
    
    import pandas as pd
    
    converter = ExcelToKoboXML(
        excel_path='../uploads/345WData_md103-edit_copy.xlsx',
        mapping_path='../uploads/question-mapping.json'
    )
    
    # Load main data
    main_data = converter.sheets['data']
    
    print(f"Total submissions in Excel: {len(main_data)}")
    
    # Filter by date
    recent = main_data[main_data['today'] >= '2025-11-07']
    print(f"Submissions from 2025-11-07 onwards: {len(recent)}")
    
    # Convert only filtered submissions
    results = {}
    for uuid in recent['_submission__uuid']:
        xml = converter.convert_submission(uuid)
        results[uuid] = xml
    
    print(f"\n✓ Converted {len(results)} filtered submissions\n")
    
    return results


def example_inspect_structure():
    """Example 4: Inspect the form structure."""
    print("\n" + "="*60)
    print("EXAMPLE 4: Inspect Form Structure")
    print("="*60 + "\n")
    
    # Load mapping
    with open('../uploads/question-mapping.json', 'r') as f:
        mapping = json.load(f)
    
    # Group by hierarchy level
    levels = {}
    for name, path in mapping.items():
        level = path.count('/')
        if level not in levels:
            levels[level] = []
        levels[level].append((name, path))
    
    print("Form Structure by Hierarchy Level:")
    print("-" * 60)
    
    for level in sorted(levels.keys()):
        items = levels[level]
        print(f"\nLevel {level} ({len(items)} fields):")
        
        # Show a few examples
        for name, path in sorted(items)[:3]:
            indent = "  " * level
            print(f"{indent}- {name}")
            print(f"{indent}  → {path}")
        
        if len(items) > 3:
            print(f"{indent}  ... and {len(items) - 3} more")
    
    print("\n")


def example_analyze_repeats():
    """Example 5: Analyze repeat group data."""
    print("\n" + "="*60)
    print("EXAMPLE 5: Analyze Repeat Groups")
    print("="*60 + "\n")
    
    import pandas as pd
    
    # Load Excel file
    xl = pd.ExcelFile('../uploads/345WData_md103-edit_copy.xlsx')
    
    print("Sheets in Excel file:")
    for sheet in xl.sheet_names:
        df = pd.read_excel(xl, sheet_name=sheet)
        print(f"\n{sheet}:")
        print(f"  Rows: {len(df)}")
        print(f"  Columns: {len(df.columns)}")
        
        if '_submission__uuid' in df.columns:
            print(f"  Unique submissions: {df['_submission__uuid'].nunique()}")
            
            # Show repeat counts per submission
            if sheet != 'data':
                counts = df['_submission__uuid'].value_counts()
                print(f"  Repeat instances per submission:")
                for uuid, count in counts.items():
                    print(f"    {uuid[:8]}...: {count} repeat(s)")
    
    print("\n")


def main():
    """Run all examples."""
    print("\n" + "="*60)
    print("EXCEL TO KOBO XML - EXAMPLES")
    print("="*60)
    
    try:
        # Run examples
        example_basic_conversion()
        example_get_xml_string()
        example_filtering()
        example_inspect_structure()
        example_analyze_repeats()
        
        print("="*60)
        print("✓ All examples completed successfully!")
        print("="*60 + "\n")
        
    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback
        traceback.print_exc()


if __name__ == '__main__':
    main()
