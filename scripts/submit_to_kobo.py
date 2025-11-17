#!/usr/bin/env python3
"""
Example: Submit Excel data to KoboToolbox API

This script demonstrates the complete workflow:
1. Convert Excel data to XML
2. Submit to KoboToolbox via API
3. Handle responses and errors

Usage:
    python submit_to_kobo.py --excel data.xlsx --mapping mapping.json --token YOUR_TOKEN
"""

import argparse
import requests
from pathlib import Path
from excel_to_kobo_xml import ExcelToKoboXML
import sys
import json
import tempfile
from generate_mapping import generate_mapping


class KoboSubmitter:
    """Submit XML data to KoboToolbox API."""
    
    def __init__(self, api_token: str, base_url: str = "https://kc.kobotoolbox.org"):
        """
        Initialize the submitter.
        
        Args:
            api_token: Your KoboToolbox API token
            base_url: KoboToolbox server URL (default: https://kc.kobotoolbox.org)
        """
        self.api_token = api_token
        self.base_url = base_url.rstrip('/')
        self.session = requests.Session()
        self.session.headers.update({
            'Authorization': f'Token {api_token}',
        })
    
    def submit_xml(self, form_id: str, xml_string: str, uuid: str) -> dict:
        """
        Submit XML data to a specific form using KoboToolbox API v1 submissions endpoint.
        
        Args:
            form_id: The KoboToolbox form/asset ID (not used in v1 API, but kept for reference)
            xml_string: XML string to submit
            uuid: Submission UUID
            
        Returns:
            Response dictionary with status and details
        """
        import io
        import xml.etree.ElementTree as ET
        
        # Extract formhub UUID from XML for debugging
        try:
            root = ET.fromstring(xml_string)
            formhub_elem = root.find('formhub/uuid')
            formhub_uuid_in_xml = formhub_elem.text if formhub_elem is not None else 'NOT FOUND'
            root_tag = root.tag
            root_id = root.get('id', 'NOT FOUND')
        except:
            formhub_uuid_in_xml = 'PARSE ERROR'
            root_tag = 'PARSE ERROR'
            root_id = 'PARSE ERROR'
        
        # KoboToolbox API v1 submissions endpoint
        url = f'{self.base_url}/api/v1/submissions'
        
        if getattr(self, 'debug', False):
            print(f"  DEBUG: Submitting to {url}")
            print(f"  DEBUG: XML root tag: {root_tag}")
            print(f"  DEBUG: XML root id: {root_id}")
            print(f"  DEBUG: XML formhub/uuid: {formhub_uuid_in_xml}")
        
        try:
            # Create file tuple as required by KoboToolbox
            file_tuple = (uuid, io.BytesIO(xml_string.encode('utf-8')))
            files = {'xml_submission_file': file_tuple}
            
            # Create request
            req = requests.Request(
                method='POST',
                url=url,
                files=files,
                headers={'Authorization': f'Token {self.api_token}'}
            )
            
            # Send request
            response = self.session.send(req.prepare(), timeout=30)
            
            return {
                'success': response.status_code in [200, 201],
                'status_code': response.status_code,
                'response': response.text,
                'url': url
            }
            
        except requests.exceptions.RequestException as e:
            return {
                'success': False,
                'error': str(e),
                'url': url
            }
    
    def submit_multiple(self, form_id: str, submissions: dict, 
                       stop_on_error: bool = False) -> dict:
        """
        Submit multiple XML submissions.
        
        Args:
            form_id: The KoboToolbox form/asset ID
            submissions: Dictionary mapping UUID to XML string
            stop_on_error: Whether to stop on first error
            
        Returns:
            Dictionary with success/failure counts and details
        """
        results = {
            'successful': [],
            'failed': [],
            'total': len(submissions)
        }
        
        for uuid, xml_string in submissions.items():
            print(f"Submitting {uuid}...", end=' ')
            
            result = self.submit_xml(form_id, xml_string, uuid)
            
            if result['success']:
                print("✓ Success")
                results['successful'].append(uuid)
            else:
                print(f"✗ Failed: {result.get('response', result.get('error', 'Unknown error'))}")
                results['failed'].append({
                    'uuid': uuid,
                    'error': result.get('response', result.get('error'))
                })
                
                if stop_on_error:
                    print(f"\nStopping due to error (stop_on_error=True)")
                    break
        
        return results


def main():
    """Command-line interface."""
    parser = argparse.ArgumentParser(
        description='Convert Excel to XML and submit to KoboToolbox'
    )
    parser.add_argument('--config', help='Path to config.json file with default arguments')
    parser.add_argument('--excel', help='Path to Excel file')
    parser.add_argument('--mapping', help='Path to JSON mapping file (optional, will fetch from API if not provided)')
    parser.add_argument('--token', help='KoboToolbox API token')
    parser.add_argument('--form-id', help='KoboToolbox form ID')
    parser.add_argument('--server', default='https://kc.kobotoolbox.org',
                       help='KoboToolbox server URL (for submissions, deprecated - use --kc-server)')
    parser.add_argument('--kc-server', help='KoboToolbox KoboCAT server URL (for submissions)')
    parser.add_argument('--kf-server', help='KoboToolbox KPI server URL (for API calls)')
    parser.add_argument('--formhub-uuid', 
                       help='Formhub UUID (optional, uses default if not provided)')
    parser.add_argument('--version-id',
                       help='Form version ID (optional, uses default if not provided)')
    parser.add_argument('--form-version',
                       help='Form version string (e.g., "8 (2025-11-13 17:03:35)")')
    parser.add_argument('--dry-run', action='store_true',
                       help='Generate XML but do not submit')
    parser.add_argument('--output-dir', help='Save XML files to this directory')
    parser.add_argument('--stop-on-error', action='store_true',
                       help='Stop processing if any submission fails')
    parser.add_argument('--uuid', help='Submit only a single submission with this UUID')
    parser.add_argument('--use-labels', action='store_true',
                       help='Convert choice labels to names using mapping file')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug output')
    
    args = parser.parse_args()
    
    # Load config file if specified
    config = {}
    if args.config:
        try:
            with open(args.config, 'r') as f:
                config = json.load(f)
            print(f"✓ Loaded configuration from: {args.config}\n")
        except FileNotFoundError:
            print(f"Warning: Config file not found: {args.config}")
        except json.JSONDecodeError as e:
            print(f"Error: Invalid JSON in config file: {e}")
            sys.exit(1)
    
    # Merge config with command-line args (CLI args take precedence)
    # For boolean flags, only set if explicitly true in config
    def get_arg(name, default=None):
        """Get argument value: CLI arg > config file > default"""
        cli_value = getattr(args, name.replace('-', '_'))
        flag_name = '--' + name
        
        if cli_value is not None:
            # For booleans, check if it was explicitly set on CLI
            if isinstance(cli_value, bool):
                # If the flag appears in sys.argv, it was explicitly set
                if flag_name in sys.argv:
                    return cli_value
                # Otherwise use config or default
                return config.get(name, default if default is not None else cli_value)
            return cli_value
        return config.get(name, default)
    
    # Build final arguments
    excel = get_arg('excel')
    mapping = get_arg('mapping')
    token = get_arg('token')
    form_id = get_arg('form-id')
    server = get_arg('server', 'https://kc.kobotoolbox.org')
    kc_server = get_arg('kc-server')
    kf_server = get_arg('kf-server')
    formhub_uuid = get_arg('formhub-uuid')
    version_id = get_arg('version-id')
    form_version = get_arg('form-version')
    dry_run = get_arg('dry-run', False)
    output_dir = get_arg('output-dir')
    stop_on_error = get_arg('stop-on-error', False)
    uuid = get_arg('uuid')
    use_labels = get_arg('use-labels', False)
    debug = get_arg('debug', False)
    
    # Handle server URLs - support both old 'server' and new 'kc-server'/'kf-server'
    if not kc_server:
        kc_server = server
    if not kf_server:
        # Default to kf.kobotoolbox.org if not specified
        kf_server = server.replace('kc.kobotoolbox.org', 'kf.kobotoolbox.org')
    
    # Validate required arguments
    if not excel:
        parser.error("--excel is required (or set 'excel' in config file)")
    if not token:
        parser.error("--token is required (or set 'token' in config file)")
    if not form_id:
        parser.error("--form-id is required (or set 'form-id' in config file)")
    
    # Fetch and auto-generate mapping from Kobo API
    temp_mapping_file = None
    temp_content_file = None
    
    print(f"\n{'='*60}")
    print("FETCHING FORM STRUCTURE FROM KOBO API")
    print(f"{'='*60}\n")
    
    # Fetch the asset JSON from Kobo API
    asset_url = f"{kf_server}/api/v2/assets/{form_id}.json"
    print(f"Fetching from: {asset_url}")
    
    try:
        response = requests.get(
            asset_url,
            headers={'Authorization': f'Token {token}'},
            timeout=30
        )
        
        if response.status_code != 200:
            print(f"✗ Error fetching asset: HTTP {response.status_code}")
            print(f"Response: {response.text[:500]}")
            sys.exit(1)
        
        asset_data = response.json()
        
        # Extract the content dictionary
        if 'content' not in asset_data:
            print(f"✗ Error: No 'content' key found in asset response")
            sys.exit(1)
        
        content_data = asset_data['content']
        print(f"✓ Fetched form structure (version: {asset_data.get('version_id', 'unknown')})")
        
        # Save content to temporary file
        import os
        temp_fd, temp_content_file = tempfile.mkstemp(suffix='.json', prefix='content_')
        with os.fdopen(temp_fd, 'w') as f:
            json.dump(content_data, f, indent=2)
        
        print(f"✓ Saved content to temporary file\n")
        
        # Auto-generate mapping from content
        print(f"{'='*60}")
        print("AUTO-GENERATING MAPPING FROM CONTENT")
        print(f"{'='*60}\n")
        
        # Create temporary mapping file
        temp_fd, temp_mapping_file = tempfile.mkstemp(suffix='.json', prefix='mapping_')
        os.close(temp_fd)
        
        # Generate mapping
        try:
            generate_mapping(temp_content_file, temp_mapping_file)
            mapping = temp_mapping_file
            print(f"✓ Using auto-generated mapping\n")
        except Exception as e:
            print(f"✗ Error generating mapping: {e}")
            # Cleanup
            if temp_content_file:
                try:
                    os.unlink(temp_content_file)
                except:
                    pass
            sys.exit(1)
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching asset from API: {e}")
        sys.exit(1)
    
    # Step 1: Convert Excel to XML
    print(f"\n{'='*60}")
    print("STEP 1: Converting Excel to XML")
    print(f"{'='*60}\n")
    
    # Prepare converter arguments
    converter_kwargs = {
        'excel_path': excel,
        'mapping_path': mapping,
        'form_id': form_id
    }
    
    if formhub_uuid:
        converter_kwargs['formhub_uuid'] = formhub_uuid
    if version_id:
        converter_kwargs['form_version_id'] = version_id
    if use_labels:
        converter_kwargs['use_labels'] = True
    if debug:
        converter_kwargs['debug'] = debug
    
    converter = ExcelToKoboXML(**converter_kwargs)
    
    # Convert submissions (all or single)
    if uuid:
        # Convert single submission
        print(f"Converting single submission: {uuid}")
        xml_string = converter.convert_submission(uuid, form_version=form_version if form_version else None)
        submissions = {uuid: xml_string}
        
        # Optionally save to file
        if output_dir:
            from pathlib import Path
            output_path = Path(output_dir)
            output_path.mkdir(parents=True, exist_ok=True)
            file_path = output_path / f'{uuid}.xml'
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(xml_string)
            print(f"✓ XML file saved to: {file_path}")
    else:
        # Convert all submissions
        submissions = converter.convert_all(output_dir=output_dir, form_version=form_version if form_version else None)
    
    print(f"\n✓ Converted {len(submissions)} submissions to XML")
    
    if output_dir:
        print(f"✓ XML files saved to: {output_dir}")
    
    # Step 2: Submit to KoboToolbox (unless dry-run)
    if dry_run:
        print("\n[DRY RUN MODE] - Not submitting to KoboToolbox")
        print("XML files have been generated. Review them before actual submission.")
        
        # Cleanup temporary mapping file if created
        if temp_mapping_file:
            import os
            try:
                os.unlink(temp_mapping_file)
            except:
                pass
        
        # Cleanup temporary content file if created
        if temp_content_file:
            import os
            try:
                os.unlink(temp_content_file)
            except:
                pass
        
        return
    
    print(f"\n{'='*60}")
    print("STEP 2: Submitting to KoboToolbox")
    print(f"{'='*60}\n")
    print(f"KC Server (submissions): {kc_server}")
    print(f"KF Server (API): {kf_server}")
    print(f"Form ID: {form_id}")
    print(f"Submissions: {len(submissions)}\n")
    
    submitter = KoboSubmitter(token, kc_server)
    submitter.debug = debug
    results = submitter.submit_multiple(
        form_id,
        submissions,
        stop_on_error=stop_on_error
    )
    
    # Step 3: Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}\n")
    print(f"Total submissions: {results['total']}")
    print(f"✓ Successful: {len(results['successful'])}")
    print(f"✗ Failed: {len(results['failed'])}")
    
    if results['failed']:
        print("\nFailed submissions:")
        for failure in results['failed']:
            print(f"  - {failure['uuid']}: {failure['error'][:100]}")
    
    # Cleanup temporary mapping file if created
    if temp_mapping_file:
        import os
        try:
            os.unlink(temp_mapping_file)
        except:
            pass
    
    # Cleanup temporary content file if created
    if temp_content_file:
        import os
        try:
            os.unlink(temp_content_file)
        except:
            pass
    
    # Exit with error code if any failed
    sys.exit(0 if not results['failed'] else 1)


if __name__ == '__main__':
    main()