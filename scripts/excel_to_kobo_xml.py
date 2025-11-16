#!/usr/bin/env python3
"""
Excel to KoboToolbox XML Converter

This script converts Excel data exported from KoboToolbox (with multiple sheets for repeat groups)
back into the XML submission format required by the KoboToolbox API.

Usage:
    python excel_to_kobo_xml.py input.xlsx question_mapping.json output_dir/
    
    Or use as a module:
    from excel_to_kobo_xml import ExcelToKoboXML
    converter = ExcelToKoboXML('input.xlsx', 'mapping.json')
    xml_files = converter.convert_all()
"""

import pandas as pd
import json
import xml.etree.ElementTree as ET
from xml.dom import minidom
from pathlib import Path
from typing import Dict, List, Optional, Any
import argparse
import sys


class ExcelToKoboXML:
    """Converts Excel data with repeat groups to KoboToolbox XML submission format."""
    
    def __init__(self, excel_path: str, mapping_path: str, form_id: str = "aiBgJcvz5AFHB54fKpG2y5", 
                 formhub_uuid: str = None,
                 form_version_id: str = "vdjkkW3B5b9mKHZVoDPYbA",
                 use_labels: bool = False,
                 debug: bool = False):
        """
        Initialize the converter.
        
        Args:
            excel_path: Path to the Excel file with data
            mapping_path: Path to the JSON file with question name to path mapping
            form_id: The form ID for the XML root element
            formhub_uuid: The formhub UUID for the form
            form_version_id: The form version ID
            use_labels: If True, convert choice labels to choice names using mapping
            debug: If True, enable debug output
        """
        self.excel_path = excel_path
        self.mapping_path = mapping_path
        self.form_id = form_id
        self.formhub_uuid = formhub_uuid
        self.form_version_id = form_version_id
        self.use_labels = use_labels
        self.debug = debug
        
        # Load the question mapping
        with open(mapping_path, 'r') as f:
            mapping_data = json.load(f)
            
        # Handle both old format (just paths) and new format (with choices)
        if isinstance(mapping_data, dict) and 'fields' in mapping_data:
            # New format with fields and choices
            self.mapping = mapping_data['fields']
            self.choice_mappings = mapping_data.get('choices', {})
        else:
            # Old format - just field paths
            self.mapping = mapping_data
            self.choice_mappings = {}
        
        # Create reverse mapping (column name -> path)
        self.col_to_path = {k: v for k, v in self.mapping.items()}
        
        # Identify group-only mappings (structural markers that shouldn't create elements)
        # A mapping is group-only if: column_name == last_part_of_path AND other fields have this as prefix
        self.group_only_fields = set()
        for col_name, path in self.col_to_path.items():
            path_parts = path.split('/')
            # If column name equals the last part of the path, it might be a group marker
            if col_name == path_parts[-1]:
                # Check if any other mapping has this path as a prefix
                is_group = any(
                    other_path.startswith(path + '/') 
                    for other_path in self.col_to_path.values() 
                    if other_path != path
                )
                if is_group:
                    self.group_only_fields.add(col_name)
        
        # Load all Excel sheets
        self.xl_file = pd.ExcelFile(excel_path)
        self.sheets = {}
        for sheet_name in self.xl_file.sheet_names:
            self.sheets[sheet_name] = pd.read_excel(self.xl_file, sheet_name=sheet_name)
    
    def _convert_label_to_name(self, field_name: str, value: Any) -> Any:
        """
        Convert choice label to choice name if use_labels is enabled.
        
        Args:
            field_name: The field/question name
            value: The value (possibly a label)
            
        Returns:
            The choice name if mapping exists, otherwise original value
        """
        if not self.use_labels or pd.isna(value):
            return value

        # If there is no mapping for this field, leave value unchanged
        if field_name not in self.choice_mappings:
            return value

        mapping = self.choice_mappings[field_name]

        # Normalize incoming value
        value_str = str(value).strip()

        # First check if value is already a choice name (code) - if so, keep it as-is
        # Check if value appears as a VALUE in the mapping (meaning it's already a code)
        if value_str in mapping.values():
            return value

        # If mapping is label -> name (common), direct lookup
        if value_str in mapping:
            return mapping[value_str]

        # If mapping is name -> label (older format), try reverse lookup
        for name_key, label_val in mapping.items():
            if str(label_val).strip() == value_str:
                return name_key

        # Handle multi-select values (common separators: ';', '|', ' ')
        for sep in [';', '|', ' ']:
            if sep in value_str:
                parts = [p.strip() for p in value_str.split(sep) if p.strip()]
                converted_parts = []
                for part in parts:
                    # Check if already a code
                    if part in mapping.values():
                        converted_parts.append(part)
                    elif part in mapping:
                        converted_parts.append(mapping[part])
                    else:
                        # try reverse lookup
                        found = False
                        for name_key, label_val in mapping.items():
                            if str(label_val).strip() == part:
                                converted_parts.append(name_key)
                                found = True
                                break
                        if not found:
                            converted_parts.append(part)
                # Join using space which is the ODK internal separator for multiples
                return ' '.join(converted_parts)

        # No mapping found, return original value
        return value
    
    def _create_nested_element(self, parent: ET.Element, path: str, value: Any, field_name: str = None) -> ET.Element:
        """
        Create nested XML elements based on path (e.g., 'org_details/FOCAL_POINTS/email').
        
        Args:
            parent: Parent XML element
            path: Slash-separated path for the element
            value: Value to set for the leaf element
            field_name: Original field name for choice mapping lookup
            
        Returns:
            The leaf element that was created or found
        """
        parts = path.split('/')
        current = parent
        
        # Navigate/create the path
        for i, part in enumerate(parts):
            # Check if this element already exists
            existing = current.find(part)
            if existing is not None:
                current = existing
            else:
                # Create new element
                new_elem = ET.SubElement(current, part)
                current = new_elem
        
        # Convert label to name if needed
        converted_value = self._convert_label_to_name(field_name, value) if field_name else value
        
        # Set the value on the leaf element
        if pd.notna(converted_value):
            # Convert value to string, handling different types
            if isinstance(converted_value, (int, float)):
                current.text = str(int(converted_value) if isinstance(converted_value, float) and converted_value.is_integer() else converted_value)
            else:
                current.text = str(converted_value)
        else:
            # Empty element for NaN/None values
            current.text = ""
            
        return current
    
    def _build_group_hierarchy(self, row: pd.Series, parent: ET.Element, path_prefix: str = "") -> None:
        """
        Build the hierarchical XML structure for a single row of data.
        
        Args:
            row: Pandas Series containing the data
            parent: Parent XML element to add children to
            path_prefix: Prefix to filter paths (for repeat groups)
        """
        # Process fields in the order they appear in the mapping (not Excel column order)
        for col_name, path in self.col_to_path.items():
            # Skip if column doesn't exist in the row
            if col_name not in row.index:
                continue
                
            # Skip the UUID column and other metadata
            if col_name == '_submission__uuid' or col_name.startswith('_') or col_name == 'deprecatedID':
                continue
            
            # Skip group-only mappings (structural markers, not actual fields)
            if col_name in self.group_only_fields:
                continue
            
            value = row[col_name]
            
            if path:
                # If we have a path prefix (for repeat groups), only process matching paths
                if path_prefix and not path.startswith(path_prefix):
                    continue
                
                # Remove the prefix if present
                if path_prefix:
                    relative_path = path[len(path_prefix):].lstrip('/')
                else:
                    relative_path = path
                
                # Create the nested element (pass field_name so label->name conversion can occur)
                self._create_nested_element(parent, relative_path, value, field_name=col_name)
    
    def _add_repeat_group(self, parent: ET.Element, repeat_name: str, 
                         repeat_data: pd.DataFrame, uuid: str) -> None:
        """
        Add repeat group instances to the parent element.
        
        Args:
            parent: Parent XML element (usually RESPONSES or similar)
            repeat_name: Name of the repeat group (e.g., 'FIGURES_COMMUNITY')
            repeat_data: DataFrame containing the repeat group data
            uuid: The submission UUID to filter data
        """
        # Filter repeat data for this submission
        submission_repeats = repeat_data[repeat_data['_submission__uuid'] == uuid]
        
        if submission_repeats.empty:
            return
        
        # Get the path for this repeat group to determine the full prefix
        repeat_path = self.col_to_path.get(repeat_name, repeat_name)
        
        # Add each repeat instance
        for idx, (_, row) in enumerate(submission_repeats.iterrows(), start=1):
            repeat_elem = ET.SubElement(parent, repeat_name)
            
            # Check if this repeat group has a 'position' field in the data
            has_position = any('position' in str(col) for col in row.index if not col.startswith('_'))
            
            if has_position:
                # Only add position if it's not already in the data columns
                position_col = f"{repeat_path}/position"
                if position_col not in row.index or pd.isna(row.get(position_col)):
                    position_elem = ET.SubElement(repeat_elem, 'position')
                    position_elem.text = str(idx)
            
            # Build the hierarchy for this repeat instance
            # For repeat groups, columns already have the full path, so we need to strip the repeat group path
            for col_name, path in self.col_to_path.items():
                if col_name not in row.index or col_name.startswith('_'):
                    continue
                
                # Skip group-only mappings
                if col_name in self.group_only_fields:
                    continue
                
                # Only process columns that belong to this repeat group
                if not path.startswith(repeat_path + '/'):
                    continue
                
                # Get the relative path (remove the repeat group prefix)
                relative_path = path[len(repeat_path) + 1:]  # +1 for the trailing slash
                
                value = row[col_name]
                
                # Create the nested element
                self._create_nested_element(repeat_elem, relative_path, value, field_name=col_name)
    
    def _prettify_xml(self, elem: ET.Element) -> str:
        """
        Return a pretty-printed XML string.
        
        Args:
            elem: XML element to prettify
            
        Returns:
            Pretty-printed XML string
        """
        rough_string = ET.tostring(elem, encoding='unicode')
        reparsed = minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="    ")
    
    def convert_submission(self, uuid: str, form_version: str = None) -> str:
        """
        Convert a single submission to XML format.
        
        Args:
            uuid: The submission UUID to convert
            form_version: Form version string (will use auto-generated if None)
            
        Returns:
            XML string for the submission
        """
        from datetime import datetime
        
        # Get the main data row
        main_data = self.sheets['data']
        submission_row = main_data[main_data['_submission__uuid'] == uuid]
        
        if submission_row.empty:
            raise ValueError(f"No submission found with UUID: {uuid}")
        
        submission_row = submission_row.iloc[0]
        
        # Auto-generate version string if not provided
        if form_version is None:
            form_version = f"8 ({datetime.now().strftime('%Y-%m-%d %H:%M:%S')})"
        
        # DEBUG: Print form_id being used
        if self.debug:
            print(f"DEBUG: Creating XML with form_id: {self.form_id}")
        
        # Create root element with form_id as the tag name
        root = ET.Element(self.form_id)
        root.set('id', self.form_id)
        root.set('version', form_version)
        
        # Add formhub element with UUID (only if provided)
        # The formhub UUID must match the form, otherwise submissions go to wrong form
        if self.formhub_uuid:
            formhub = ET.SubElement(root, 'formhub')
            formhub_uuid_elem = ET.SubElement(formhub, 'uuid')
            formhub_uuid_elem.text = self.formhub_uuid
        
        # Build the main structure
        self._build_group_hierarchy(submission_row, root)
        
        # Add repeat groups
        for sheet_name in self.xl_file.sheet_names:
            if sheet_name == 'data':
                continue
            
            # Skip sheets that don't have _submission__uuid (these are reference sheets, not repeat groups)
            repeat_data = self.sheets[sheet_name]
            if '_submission__uuid' not in repeat_data.columns:
                continue
            
            # Find the parent element for this repeat group
            # This assumes repeat groups are under RESPONSES, but adjust as needed
            repeat_parent = root
            
            # Try to find the correct parent based on the mapping
            if sheet_name in self.col_to_path:
                parent_path = self.col_to_path[sheet_name].rsplit('/', 1)[0] if '/' in self.col_to_path[sheet_name] else ''
                
                if parent_path:
                    for part in parent_path.split('/'):
                        temp_parent = repeat_parent.find(part)
                        if temp_parent is None:
                            temp_parent = ET.SubElement(repeat_parent, part)
                        repeat_parent = temp_parent
            
            # Add the repeat group instances
            self._add_repeat_group(repeat_parent, sheet_name, repeat_data, uuid)
        
        # Add __version__ element
        version_elem = ET.SubElement(root, '__version__')
        version_elem.text = self.form_version_id
        
        # Add meta element with instanceID at the end
        meta = ET.SubElement(root, 'meta')
        instance_id = ET.SubElement(meta, 'instanceID')
        instance_id.text = f'uuid:{uuid}'
        
        # Add deprecatedID if present (for editing existing submissions)
        if 'deprecatedID' in submission_row.index and pd.notna(submission_row['deprecatedID']):
            deprecated_id = ET.SubElement(meta, 'deprecatedID')
            deprecated_value = submission_row['deprecatedID']
            # Ensure it has uuid: prefix
            if not str(deprecated_value).startswith('uuid:'):
                deprecated_id.text = f'uuid:{deprecated_value}'
            else:
                deprecated_id.text = str(deprecated_value)
        
        # Convert to pretty XML string
        xml_string = self._prettify_xml(root)
        
        # Remove XML declaration line and extra whitespace
        lines = xml_string.split('\n')
        lines = [line for line in lines if line.strip() and not line.strip().startswith('<?xml')]
        
        return '\n'.join(lines)
    
    def convert_all(self, output_dir: Optional[str] = None, form_version: Optional[str] = None) -> Dict[str, str]:
        """
        Convert all submissions in the Excel file to XML.
        
        Args:
            output_dir: Optional directory to write XML files to
            form_version: Optional form version string to use for all submissions
            
        Returns:
            Dictionary mapping UUID to XML string
        """
        main_data = self.sheets['data']
        uuids = main_data['_submission__uuid'].unique()
        
        results = {}
        
        for uuid in uuids:
            try:
                xml_string = self.convert_submission(uuid, form_version=form_version)
                results[uuid] = xml_string
                
                # Write to file if output directory specified
                if output_dir:
                    output_path = Path(output_dir)
                    output_path.mkdir(parents=True, exist_ok=True)
                    
                    file_path = output_path / f'{uuid}.xml'
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(xml_string)
                    
                    print(f"✓ Converted {uuid} -> {file_path}")
            
            except Exception as e:
                print(f"✗ Error converting {uuid}: {e}", file=sys.stderr)
                
        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Convert Excel data to KoboToolbox XML submission format'
    )
    parser.add_argument('excel_file', help='Path to Excel file with data')
    parser.add_argument('mapping_file', help='Path to JSON mapping file')
    parser.add_argument('output_dir', nargs='?', help='Output directory for XML files')
    parser.add_argument('--form-id', default='aiBgJcvz5AFHB54fKpG2y5',
                       help='Form ID for XML root element')
    parser.add_argument('--formhub-uuid', default='a5c29b3b422446a0acf55f72d9a443d1',
                       help='Formhub UUID for the form')
    parser.add_argument('--version-id', default='vdjkkW3B5b9mKHZVoDPYbA',
                       help='Form version ID')
    
    args = parser.parse_args()
    
    # Create converter
    converter = ExcelToKoboXML(
        args.excel_file, 
        args.mapping_file, 
        args.form_id,
        args.formhub_uuid,
        args.version_id
    )
    
    # Convert all submissions
    results = converter.convert_all(args.output_dir)
    
    print(f"\n✓ Converted {len(results)} submissions successfully")


if __name__ == '__main__':
    main()
