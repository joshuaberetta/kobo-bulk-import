#!/usr/bin/env python3
"""
Generate mapping file from KoboToolbox survey content.json

This script parses the KoboToolbox survey definition (content.json) and automatically 
generates:
1. Field path mappings (for nested groups and repeat groups)
2. Choice label-to-name mappings (for select_one and select_multiple questions)

Usage:
    python generate_mapping.py content.json [output_mapping.json]
"""

import json
import sys
from pathlib import Path


def build_field_paths(survey_items):
    """
    Build field path mappings from survey structure using $xpath.
    
    Uses the $xpath field from content.json which contains the full hierarchical path.
    
    Returns dict mapping field names to their full paths.
    """
    field_paths = {}
    
    for item in survey_items:
        item_name = item.get('name', '')
        xpath = item.get('$xpath', '')
        
        if item_name and xpath:
            # Use the xpath directly from content.json
            field_paths[item_name] = xpath
    
    return field_paths


def build_choice_mappings(survey_items, choices):
    """
    Build choice mappings for select_one and select_multiple questions.
    
    Maps choice names to their display labels for each question that uses choices.
    
    Returns dict mapping field names to their choice mappings.
    """
    choice_mappings = {}
    
    # First, organize choices by list_name
    choices_by_list = {}
    for choice in choices:
        list_name = choice.get('list_name')
        if not list_name:
            continue
            
        if list_name not in choices_by_list:
            choices_by_list[list_name] = {}
        
        choice_name = choice.get('name')
        choice_label = choice.get('label')
        
        # Labels are often arrays with one element
        if isinstance(choice_label, list) and len(choice_label) > 0:
            choice_label = choice_label[0]
        
        if choice_name and choice_label:
            # Map label to name (for reverse lookup during conversion)
            choices_by_list[list_name][choice_label] = choice_name
    
    # Now find all select_one/select_multiple questions and link to their choices
    for item in survey_items:
        item_type = item.get('type', '')
        item_name = item.get('name', '')
        
        # Check if this is a select question
        if item_type.startswith('select_one') or item_type.startswith('select_multiple'):
            # Get the choice list name
            list_name = item.get('select_from_list_name')
            
            if list_name and list_name in choices_by_list and item_name:
                # Store the choice mapping for this field
                choice_mappings[item_name] = choices_by_list[list_name]
    
    return choice_mappings


def generate_mapping(content_file, output_file=None):
    """
    Generate mapping file from KoboToolbox content.json
    
    Args:
        content_file: Path to content.json
        output_file: Path to output mapping file (default: auto-generated-mapping.json)
    """
    # Read content.json
    with open(content_file, 'r', encoding='utf-8') as f:
        content = json.load(f)
    
    survey = content.get('survey', [])
    choices = content.get('choices', [])
    
    print(f"Processing survey with {len(survey)} items and {len(choices)} choices...")
    
    # Generate field paths
    field_paths = build_field_paths(survey)
    print(f"Generated {len(field_paths)} field paths")
    
    # Generate choice mappings
    choice_mappings = build_choice_mappings(survey, choices)
    print(f"Generated choice mappings for {len(choice_mappings)} fields")
    
    # Create the combined mapping structure
    mapping = {
        "fields": field_paths,
        "choices": choice_mappings
    }
    
    # Determine output file
    if not output_file:
        output_file = 'auto-generated-mapping.json'
    
    # Write mapping file
    with open(output_file, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    print(f"\nMapping file written to: {output_file}")
    print(f"  - {len(field_paths)} field paths")
    print(f"  - {len(choice_mappings)} choice mappings")
    
    return mapping


def main():
    """Command-line interface"""
    if len(sys.argv) < 2:
        print("Usage: python generate_mapping.py <content.json> [output_mapping.json]")
        print("\nExample:")
        print("  python generate_mapping.py content.json")
        print("  python generate_mapping.py content.json my-mapping.json")
        sys.exit(1)
    
    content_file = sys.argv[1]
    output_file = sys.argv[2] if len(sys.argv) > 2 else None
    
    if not Path(content_file).exists():
        print(f"Error: Content file not found: {content_file}")
        sys.exit(1)
    
    try:
        generate_mapping(content_file, output_file)
        print("\n✓ Success!")
    except Exception as e:
        print(f"\n✗ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
