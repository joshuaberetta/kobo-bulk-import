#!/usr/bin/env python3
"""
Simple KoboToolbox Submission Script

This script provides a straightforward way to submit XML to KoboToolbox
using the exact API format that KoboToolbox expects.

Usage:
    python simple_submit.py
    
    Or import and use:
    from simple_submit import submit_data
    status, uuid = submit_data(xml_bytes, uuid)
"""

import io
import requests
from pathlib import Path


# ============================================================================
# CONFIGURATION
# ============================================================================

# KoboToolbox API Configuration
KOBO_URL = 'https://kc.kobotoolbox.org/api/v1/submissions'
KOBO_TOKEN = 'YOUR_TOKEN_HERE'  # Replace with your actual token

# Or for KoboToolbox EU server:
# KOBO_URL = 'https://eu.kobotoolbox.org/api/v1/submissions'

# Or for humanitarian server:
# KOBO_URL = 'https://kobo.humanitarianresponse.info/api/v1/submissions'


# ============================================================================
# SUBMISSION FUNCTION
# ============================================================================

def submit_data(xml, _uuid, url=KOBO_URL, token=KOBO_TOKEN):
    """
    Submit XML data to KoboToolbox API.
    
    This follows the exact format required by KoboToolbox's v1 submissions endpoint.
    
    Args:
        xml: XML data as bytes or string
        _uuid: Submission UUID
        url: KoboToolbox API URL (default: KOBO_URL)
        token: API token (default: KOBO_TOKEN)
        
    Returns:
        Tuple of (status_code, uuid)
    """
    # Convert string to bytes if needed
    if isinstance(xml, str):
        xml = xml.encode('utf-8')
    
    # Prepare headers
    headers = {
        'Authorization': f'Token {token}',
    }
    
    # Create file tuple for submission
    file_tuple = (_uuid, io.BytesIO(xml))
    files = {'xml_submission_file': file_tuple}
    
    # Create request
    req = requests.Request(
        method='POST',
        url=url,
        files=files,
        headers=headers,
    )
    
    # Send request
    session = requests.Session()
    response = session.send(req.prepare())
    
    return response.status_code, _uuid


# ============================================================================
# BATCH SUBMISSION
# ============================================================================

def submit_multiple(xml_dict, url=KOBO_URL, token=KOBO_TOKEN):
    """
    Submit multiple XML submissions.
    
    Args:
        xml_dict: Dictionary mapping UUID to XML (bytes or string)
        url: KoboToolbox API URL
        token: API token
        
    Returns:
        Dictionary with results
    """
    results = {
        'successful': [],
        'failed': [],
        'responses': {}
    }
    
    for uuid, xml in xml_dict.items():
        print(f"Submitting {uuid}...", end=' ')
        
        status_code, returned_uuid = submit_data(xml, uuid, url, token)
        
        results['responses'][uuid] = status_code
        
        if status_code in [200, 201]:
            print(f"✓ Success (HTTP {status_code})")
            results['successful'].append(uuid)
        else:
            print(f"✗ Failed (HTTP {status_code})")
            results['failed'].append(uuid)
    
    return results


# ============================================================================
# CONVENIENCE FUNCTIONS
# ============================================================================

def submit_from_file(xml_file_path, uuid=None, url=KOBO_URL, token=KOBO_TOKEN):
    """
    Submit XML from a file.
    
    Args:
        xml_file_path: Path to XML file
        uuid: Optional UUID (if None, extracts from filename)
        url: KoboToolbox API URL
        token: API token
        
    Returns:
        Tuple of (status_code, uuid)
    """
    xml_path = Path(xml_file_path)
    
    # Extract UUID from filename if not provided
    if uuid is None:
        uuid = xml_path.stem  # Filename without extension
    
    # Read XML file
    with open(xml_path, 'rb') as f:
        xml_bytes = f.read()
    
    # Submit
    return submit_data(xml_bytes, uuid, url, token)


def submit_from_directory(directory, url=KOBO_URL, token=KOBO_TOKEN):
    """
    Submit all XML files from a directory.
    
    Args:
        directory: Path to directory containing XML files
        url: KoboToolbox API URL
        token: API token
        
    Returns:
        Dictionary with results
    """
    dir_path = Path(directory)
    xml_files = list(dir_path.glob('*.xml'))
    
    print(f"Found {len(xml_files)} XML files in {directory}\n")
    
    results = {
        'successful': [],
        'failed': [],
        'responses': {}
    }
    
    for xml_file in xml_files:
        uuid = xml_file.stem
        status_code, returned_uuid = submit_from_file(xml_file, uuid, url, token)
        
        results['responses'][uuid] = status_code
        
        if status_code in [200, 201]:
            results['successful'].append(uuid)
        else:
            results['failed'].append(uuid)
    
    return results


# ============================================================================
# EXAMPLE USAGE
# ============================================================================

def example_usage():
    """Example of how to use this script."""
    
    print("""
================================================================================
                    KOBO SUBMISSION SCRIPT - EXAMPLES
================================================================================
""")
    
    # Example 1: Submit a single XML file
    print("\nExample 1: Submit a single XML file")
    print("-" * 60)
    print("""
    from simple_submit import submit_from_file
    
    status, uuid = submit_from_file(
        'path/to/submission.xml',
        uuid='optional-uuid-if-not-in-filename'
    )
    
    if status in [200, 201]:
        print(f"Success! {uuid} submitted")
    """)
    
    # Example 2: Submit from XML string
    print("\nExample 2: Submit from XML string")
    print("-" * 60)
    print("""
    from simple_submit import submit_data
    
    xml_string = '''<submission>...</submission>'''
    status, uuid = submit_data(xml_string, 'my-uuid-123')
    """)
    
    # Example 3: Submit all files from directory
    print("\nExample 3: Submit all files from directory")
    print("-" * 60)
    print("""
    from simple_submit import submit_from_directory
    
    results = submit_from_directory('./xml_output')
    print(f"Successful: {len(results['successful'])}")
    print(f"Failed: {len(results['failed'])}")
    """)
    
    # Example 4: Submit multiple from dict
    print("\nExample 4: Submit multiple from dictionary")
    print("-" * 60)
    print("""
    from simple_submit import submit_multiple
    
    submissions = {
        'uuid-1': '<submission1>...</submission1>',
        'uuid-2': '<submission2>...</submission2>',
    }
    
    results = submit_multiple(submissions)
    """)
    
    # Example 5: Integration with excel_to_kobo_xml
    print("\nExample 5: Integration with excel_to_kobo_xml")
    print("-" * 60)
    print("""
    from excel_to_kobo_xml import ExcelToKoboXML
    from simple_submit import submit_data
    
    # Convert Excel to XML
    converter = ExcelToKoboXML('data.xlsx', 'mapping.json')
    submissions = converter.convert_all()
    
    # Submit each
    for uuid, xml_string in submissions.items():
        status, _ = submit_data(xml_string, uuid)
        print(f"{uuid}: HTTP {status}")
    """)
    
    print("""
================================================================================
""")


# ============================================================================
# MAIN
# ============================================================================

def main():
    """Command-line interface."""
    import sys
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Submit XML to KoboToolbox API'
    )
    parser.add_argument('--file', help='Submit a single XML file')
    parser.add_argument('--dir', help='Submit all XML files from directory')
    parser.add_argument('--uuid', help='UUID for single file submission')
    parser.add_argument('--url', default=KOBO_URL, help='KoboToolbox API URL')
    parser.add_argument('--token', default=KOBO_TOKEN, help='API token')
    parser.add_argument('--examples', action='store_true', help='Show usage examples')
    
    args = parser.parse_args()
    
    if args.examples:
        example_usage()
        return 0
    
    if args.token == 'YOUR_TOKEN_HERE':
        print("Error: Please provide an API token with --token or update KOBO_TOKEN in the script")
        return 1
    
    if args.file:
        status, uuid = submit_from_file(args.file, args.uuid, args.url, args.token)
        print(f"\nResult: HTTP {status} for {uuid}")
        return 0 if status in [200, 201] else 1
    
    elif args.dir:
        results = submit_from_directory(args.dir, args.url, args.token)
        print(f"\nResults:")
        print(f"  Successful: {len(results['successful'])}")
        print(f"  Failed: {len(results['failed'])}")
        return 0 if not results['failed'] else 1
    
    else:
        parser.print_help()
        print("\nFor usage examples, run: python simple_submit.py --examples")
        return 0


if __name__ == '__main__':
    import sys
    sys.exit(main())
