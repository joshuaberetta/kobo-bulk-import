#!/usr/bin/env python3
"""
Complete End-to-End Example: Excel to KoboToolbox

This script demonstrates the complete workflow using the correct KoboToolbox API.
"""

import io
import requests
from excel_to_kobo_xml import ExcelToKoboXML


# ============================================================================
# CONFIGURATION
# ============================================================================

CONFIG = {
    # Files
    'excel_file': 'your_data.xlsx',
    'mapping_file': 'question_mapping.json',
    'output_dir': './xml_output',
    
    # KoboToolbox API
    'api_url': 'https://kc.kobotoolbox.org/api/v1/submissions',
    'api_token': 'YOUR_TOKEN_HERE',
    
    # Options
    'dry_run': True,  # Set False to actually submit
}


# ============================================================================
# SUBMISSION FUNCTION (Exact KoboToolbox Format)
# ============================================================================

def submit_to_kobo(xml, uuid, api_url, api_token):
    """
    Submit XML to KoboToolbox using the exact API format.
    
    This matches the format from your provided code:
    - Uses /api/v1/submissions endpoint
    - Sends as multipart file upload
    - Uses 'xml_submission_file' as field name
    
    Args:
        xml: XML data as string or bytes
        uuid: Submission UUID
        api_url: KoboToolbox API URL
        api_token: API token
        
    Returns:
        Tuple of (status_code, uuid)
    """
    # Convert to bytes if string
    if isinstance(xml, str):
        xml = xml.encode('utf-8')
    
    # Prepare headers
    headers = {
        'Authorization': f'Token {api_token}',
    }
    
    # Create file tuple
    file_tuple = (uuid, io.BytesIO(xml))
    files = {'xml_submission_file': file_tuple}
    
    # Create and send request
    req = requests.Request(
        method='POST',
        url=api_url,
        files=files,
        headers=headers,
    )
    session = requests.Session()
    response = session.send(req.prepare())
    
    return response.status_code, uuid


# ============================================================================
# MAIN WORKFLOW
# ============================================================================

def main():
    print("""
================================================================================
                EXCEL TO KOBO - COMPLETE WORKFLOW
================================================================================
""")
    
    # Step 1: Convert Excel to XML
    print("STEP 1: Converting Excel to XML")
    print("-" * 60)
    
    try:
        converter = ExcelToKoboXML(
            excel_path=CONFIG['excel_file'],
            mapping_path=CONFIG['mapping_file']
        )
        
        submissions = converter.convert_all(output_dir=CONFIG['output_dir'])
        
        print(f"✓ Converted {len(submissions)} submissions")
        print(f"✓ XML files saved to: {CONFIG['output_dir']}\n")
        
    except FileNotFoundError as e:
        print(f"✗ Error: File not found - {e}")
        print("\nPlease update CONFIG with your file paths:")
        print("  - CONFIG['excel_file']")
        print("  - CONFIG['mapping_file']")
        return 1
    except Exception as e:
        print(f"✗ Conversion error: {e}")
        return 1
    
    # Step 2: Submit to KoboToolbox
    if CONFIG['dry_run']:
        print("STEP 2: DRY RUN MODE")
        print("-" * 60)
        print("✓ XML files generated successfully")
        print(f"✓ Review files in: {CONFIG['output_dir']}")
        print("\nTo submit for real:")
        print("  1. Set CONFIG['dry_run'] = False")
        print("  2. Update CONFIG['api_token'] with your token")
        print("  3. Update CONFIG['api_url'] if using different server")
        print("  4. Run this script again\n")
        return 0
    
    print("STEP 2: Submitting to KoboToolbox")
    print("-" * 60)
    print(f"API URL: {CONFIG['api_url']}")
    print(f"Submissions: {len(submissions)}\n")
    
    if CONFIG['api_token'] == 'YOUR_TOKEN_HERE':
        print("✗ Error: Please set your API token in CONFIG['api_token']")
        return 1
    
    # Submit each
    results = {'successful': [], 'failed': []}
    
    for uuid, xml_string in submissions.items():
        print(f"Submitting {uuid}...", end=' ')
        
        try:
            status_code, returned_uuid = submit_to_kobo(
                xml=xml_string,
                uuid=uuid,
                api_url=CONFIG['api_url'],
                api_token=CONFIG['api_token']
            )
            
            if status_code in [200, 201]:
                print(f"✓ Success (HTTP {status_code})")
                results['successful'].append(uuid)
            else:
                print(f"✗ Failed (HTTP {status_code})")
                results['failed'].append({'uuid': uuid, 'status': status_code})
                
        except Exception as e:
            print(f"✗ Error: {e}")
            results['failed'].append({'uuid': uuid, 'error': str(e)})
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print("="*60)
    print(f"Total: {len(submissions)}")
    print(f"✓ Successful: {len(results['successful'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed submissions:")
        for failure in results['failed']:
            uuid = failure['uuid']
            error = failure.get('error', f"HTTP {failure.get('status')}")
            print(f"  - {uuid}: {error}")
    
    print("="*60 + "\n")
    
    return 0 if not results['failed'] else 1


# ============================================================================
# ALTERNATIVE: USING THE SIMPLE_SUBMIT MODULE
# ============================================================================

def alternative_with_simple_submit():
    """
    Alternative approach using the simple_submit module.
    """
    print("""
You can also use the simple_submit module:

    from excel_to_kobo_xml import ExcelToKoboXML
    from simple_submit import submit_data
    
    # Convert
    converter = ExcelToKoboXML('data.xlsx', 'mapping.json')
    submissions = converter.convert_all()
    
    # Submit
    for uuid, xml_string in submissions.items():
        status, _ = submit_data(
            xml=xml_string,
            _uuid=uuid,
            url='https://kc.kobotoolbox.org/api/v1/submissions',
            token='YOUR_TOKEN'
        )
        print(f"{uuid}: HTTP {status}")
""")


if __name__ == '__main__':
    import sys
    
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
