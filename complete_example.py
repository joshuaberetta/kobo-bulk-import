#!/usr/bin/env python3
"""
Complete Integration Example

This demonstrates the full workflow of converting Excel data to XML
and submitting to KoboToolbox, with error handling and validation.

Customize the configuration section below for your use case.
"""

from excel_to_kobo_xml import ExcelToKoboXML
import requests
from pathlib import Path
import sys


# ============================================================================
# CONFIGURATION - Customize these for your project
# ============================================================================

CONFIG = {
    # File paths
    'excel_file': 'your_data.xlsx',
    'mapping_file': 'question_mapping.json',
    'output_dir': './xml_output',
    
    # KoboToolbox settings
    'form_id': 'aiBgJcvz5AFHB54fKpG2y5',  # Your form ID
    'api_token': 'YOUR_API_TOKEN_HERE',    # Your API token
    'server_url': 'https://kf.kobotoolbox.org',
    
    # Processing options
    'dry_run': False,           # Set True to test without submitting
    'stop_on_error': False,     # Set True to stop on first error
    'validate_before': True,    # Validate XML before submission
}


# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def validate_xml_structure(xml_string: str) -> bool:
    """
    Basic XML validation.
    
    Args:
        xml_string: XML string to validate
        
    Returns:
        True if valid, False otherwise
    """
    try:
        import xml.etree.ElementTree as ET
        root = ET.fromstring(xml_string)
        
        # Check for required elements
        required = ['formhub', 'meta']
        for elem in required:
            if root.find(elem) is None:
                print(f"  ⚠ Warning: Missing required element '{elem}'")
                return False
        
        return True
        
    except ET.ParseError as e:
        print(f"  ✗ XML parsing error: {e}")
        return False


def submit_to_kobo(form_id: str, xml_string: str, uuid: str, api_token: str, 
                   server_url: str) -> dict:
    """
    Submit XML to KoboToolbox API using the v1 submissions endpoint.
    
    Args:
        form_id: KoboToolbox form/asset ID (kept for reference, not used in v1 API)
        xml_string: XML submission data
        uuid: Submission UUID
        api_token: API authentication token
        server_url: KoboToolbox server URL
        
    Returns:
        Response dictionary with success status and details
    """
    import io
    
    # KoboToolbox API v1 submissions endpoint
    url = f'{server_url}/api/v1/submissions'
    
    try:
        # Create file tuple as required by KoboToolbox
        file_tuple = (uuid, io.BytesIO(xml_string.encode('utf-8')))
        files = {'xml_submission_file': file_tuple}
        
        # Create and send request
        req = requests.Request(
            method='POST',
            url=url,
            files=files,
            headers={'Authorization': f'Token {api_token}'}
        )
        
        session = requests.Session()
        response = session.send(req.prepare(), timeout=30)
        
        return {
            'success': response.status_code in [200, 201],
            'status_code': response.status_code,
            'message': response.text if response.status_code not in [200, 201] else 'Success'
        }
        
    except requests.exceptions.RequestException as e:
        return {
            'success': False,
            'error': str(e)
        }


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def main():
    """Execute the complete workflow."""
    
    print("\n" + "="*70)
    print("EXCEL TO KOBO XML - COMPLETE WORKFLOW")
    print("="*70 + "\n")
    
    # Validate configuration
    if not Path(CONFIG['excel_file']).exists():
        print(f"✗ Error: Excel file not found: {CONFIG['excel_file']}")
        print("  Please update CONFIG['excel_file'] with your file path")
        return 1
    
    if not Path(CONFIG['mapping_file']).exists():
        print(f"✗ Error: Mapping file not found: {CONFIG['mapping_file']}")
        print("  Please generate it using: python generate_mapping.py")
        return 1
    
    if CONFIG['api_token'] == 'YOUR_API_TOKEN_HERE' and not CONFIG['dry_run']:
        print("✗ Error: Please set your API token in CONFIG['api_token']")
        print("  Or set CONFIG['dry_run'] = True to test without submitting")
        return 1
    
    # ========================================================================
    # STEP 1: CONVERT EXCEL TO XML
    # ========================================================================
    
    print("STEP 1: Converting Excel to XML")
    print("-" * 70)
    
    try:
        converter = ExcelToKoboXML(
            excel_path=CONFIG['excel_file'],
            mapping_path=CONFIG['mapping_file'],
            form_id=CONFIG['form_id']
        )
        
        # Convert all submissions
        submissions = converter.convert_all(output_dir=CONFIG['output_dir'])
        
        print(f"✓ Converted {len(submissions)} submissions")
        print(f"✓ XML files saved to: {CONFIG['output_dir']}")
        
    except Exception as e:
        print(f"✗ Conversion failed: {e}")
        return 1
    
    # ========================================================================
    # STEP 2: VALIDATE XML (Optional)
    # ========================================================================
    
    if CONFIG['validate_before']:
        print(f"\nSTEP 2: Validating XML")
        print("-" * 70)
        
        validation_failed = []
        for uuid, xml_string in submissions.items():
            print(f"Validating {uuid}...", end=' ')
            if validate_xml_structure(xml_string):
                print("✓")
            else:
                print("✗")
                validation_failed.append(uuid)
        
        if validation_failed:
            print(f"\n⚠ Warning: {len(validation_failed)} submissions failed validation")
            print("  Review these XML files before submitting")
            if not CONFIG['dry_run']:
                response = input("\nContinue anyway? (yes/no): ")
                if response.lower() != 'yes':
                    print("Aborted.")
                    return 1
    
    # ========================================================================
    # STEP 3: SUBMIT TO KOBO (or dry-run)
    # ========================================================================
    
    if CONFIG['dry_run']:
        print(f"\nSTEP 3: DRY RUN MODE")
        print("-" * 70)
        print("✓ XML generated successfully")
        print(f"✓ Review files in: {CONFIG['output_dir']}")
        print("\nTo submit for real:")
        print("  1. Set CONFIG['dry_run'] = False")
        print("  2. Add your CONFIG['api_token']")
        print("  3. Run this script again")
        return 0
    
    print(f"\nSTEP 3: Submitting to KoboToolbox")
    print("-" * 70)
    print(f"Server: {CONFIG['server_url']}")
    print(f"Form ID: {CONFIG['form_id']}")
    print(f"Submissions: {len(submissions)}\n")
    
    results = {
        'successful': [],
        'failed': []
    }
    
    for uuid, xml_string in submissions.items():
        print(f"Submitting {uuid}...", end=' ')
        
        result = submit_to_kobo(
            form_id=CONFIG['form_id'],
            xml_string=xml_string,
            uuid=uuid,
            api_token=CONFIG['api_token'],
            server_url=CONFIG['server_url']
        )
        
        if result['success']:
            print("✓")
            results['successful'].append(uuid)
        else:
            print(f"✗")
            error_msg = result.get('message', result.get('error', 'Unknown error'))
            print(f"  Error: {error_msg[:100]}")
            results['failed'].append({'uuid': uuid, 'error': error_msg})
            
            if CONFIG['stop_on_error']:
                print("\nStopping due to error (stop_on_error=True)")
                break
    
    # ========================================================================
    # STEP 4: SUMMARY
    # ========================================================================
    
    print(f"\n{'='*70}")
    print("SUMMARY")
    print("="*70)
    print(f"Total submissions: {len(submissions)}")
    print(f"✓ Successful: {len(results['successful'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed submissions (see XML files for details):")
        for failure in results['failed']:
            uuid = failure['uuid']
            error = failure['error'][:100]
            xml_file = Path(CONFIG['output_dir']) / f'{uuid}.xml'
            print(f"  - {uuid}")
            print(f"    Error: {error}")
            print(f"    XML: {xml_file}")
    
    if results['successful']:
        print(f"\n✓ Successfully submitted {len(results['successful'])} submissions!")
    
    print("="*70 + "\n")
    
    return 0 if not results['failed'] else 1


if __name__ == '__main__':
    try:
        exit_code = main()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n⚠ Interrupted by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
