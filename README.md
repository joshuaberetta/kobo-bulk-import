# Excel to KoboToolbox XML Converter

This script converts Excel data exported from KoboToolbox (with multiple sheets for repeat groups) back into the XML submission format required by the KoboToolbox API.

## Overview

When working with KoboToolbox data, you might need to:
1. Export data to Excel for external processing
2. Modify or add data in Excel
3. Re-submit the modified data back to KoboToolbox

This script handles step 3 by converting the Excel format back to the XML submission format that KoboToolbox expects.

## Key Features

- **Handles repeat groups**: Automatically processes multiple sheets for nested repeat groups
- **Preserves hierarchy**: Uses the question mapping to recreate the nested XML structure
- **Batch processing**: Converts all submissions in an Excel file at once
- **Flexible**: Can be used as a command-line tool or imported as a Python module

## File Structure

Your Excel file should have:
- **Main sheet** (`data`): Contains the primary form data with one row per submission
- **Repeat group sheets**: One sheet per repeat group (e.g., `FOCAL_POINTS`, `FIGURES_COMMUNITY`)
- **UUID column**: All sheets must have a `_submission__uuid` column to link records

## Installation

```bash
# No special installation needed, just standard libraries
pip install pandas openpyxl
```

## Usage

### Quick Start with Config File (Recommended)

The easiest way to use this tool is with a configuration file:

```bash
# 1. Copy the example config
cp config.example.json config.json

# 2. Edit config.json with your details
#    - Set "mapping" to your content.json file (mapping is auto-generated!)
#    - Set your API token, form ID, etc.

# 3. Run with dry-run to test
python submit_to_kobo.py --config config.json --dry-run

# 4. Submit for real
python submit_to_kobo.py --config config.json
```

**Note**: When you specify `content.json` as the mapping file, the pipeline automatically generates the field and choice mappings in the background. No need to run `generate_mapping.py` separately!

### Command Line

```bash
# Basic usage - creates XML files in specified directory
python excel_to_kobo_xml.py input.xlsx question_mapping.json output_dir/

# Custom form ID
python excel_to_kobo_xml.py input.xlsx mapping.json output/ --form-id myFormId123
```

### As a Python Module

```python
from excel_to_kobo_xml import ExcelToKoboXML

# Initialize converter
converter = ExcelToKoboXML(
    excel_path='data.xlsx',
    mapping_path='question_mapping.json',
    form_id='aiBgJcvz5AFHB54fKpG2y5'
)

# Convert all submissions and save to directory
xml_files = converter.convert_all(output_dir='./output')

# Or convert a specific submission
xml_string = converter.convert_submission(uuid='b12be739-107b-49d7-914e-b177ac7ec5d0')

# Use the XML string directly (e.g., for API submission)
print(xml_string)
```

### Integration with KoboToolbox API

Use the `submit_to_kobo.py` script for easy submission.

**Using a configuration file (recommended):**

```bash
# 1. Copy and edit the example config
cp config.example.json config.json
# Edit config.json with your API token, paths, form ID, etc.

# 2. Run with config file
python submit_to_kobo.py --config config.json

# 3. Override specific options as needed
python submit_to_kobo.py --config config.json --dry-run
python submit_to_kobo.py --config config.json --uuid SPECIFIC_UUID
```

See `CONFIG.md` for detailed configuration options.

**Or use command-line arguments:**

```bash
# Submit all submissions
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id aiBgJcvz5AFHB54fKpG2y5 \
    --token YOUR_API_TOKEN

# Submit a single submission
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id aiBgJcvz5AFHB54fKpG2y5 \
    --token YOUR_API_TOKEN \
    --uuid 12db1b92-ec3b-466c-b41e-9882762575a4

# Generate XML without submitting (dry-run)
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id aiBgJcvz5AFHB54fKpG2y5 \
    --token YOUR_API_TOKEN \
    --output-dir ./xml_output \
    --dry-run

# Full options
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id aiBgJcvz5AFHB54fKpG2y5 \
    --token YOUR_API_TOKEN \
    --server https://kc.kobotoolbox.org \
    --formhub-uuid a5c29b3b422446a0acf55f72d9a443d1 \
    --version-id vdjkkW3B5b9mKHZVoDPYbA \
    --form-version "8 (2025-11-13 17:03:35)" \
    --output-dir ./xml_output \
    --stop-on-error
```

**Command-line options:**
- `--excel`: Path to Excel file (required)
- `--mapping`: Path to mapping JSON file (required)
- `--form-id`: KoboToolbox form ID - determines which form receives submissions (required)
- `--token`: API token from https://kf.kobotoolbox.org/token/ (required)
- `--server`: Server URL (default: https://kc.kobotoolbox.org)
- `--formhub-uuid`: Formhub UUID for the `<formhub><uuid>` element (optional)
- `--version-id`: Form version ID for the `<__version__>` element (optional, default: vdjkkW3B5b9mKHZVoDPYbA)
- `--form-version`: Version string for root element attribute (optional, auto-generated if not provided)
- `--uuid`: Submit only one submission with this UUID (optional)
- `--output-dir`: Save XML files to directory (optional)
- `--dry-run`: Generate XML without submitting (optional)
- `--stop-on-error`: Stop processing if any submission fails (optional)

Or use the Python API directly:

```python
import io
import requests
from excel_to_kobo_xml import ExcelToKoboXML

# Convert Excel to XML
converter = ExcelToKoboXML('data.xlsx', 'mapping.json')
submissions = converter.convert_all()

# Submit to KoboToolbox (v1 API - correct format)
API_TOKEN = 'your_api_token'
API_URL = 'https://kc.kobotoolbox.org/api/v1/submissions'

for uuid, xml_string in submissions.items():
    # Prepare file tuple
    xml_bytes = xml_string.encode('utf-8')
    file_tuple = (uuid, io.BytesIO(xml_bytes))
    files = {'xml_submission_file': file_tuple}
    
    # Create request
    req = requests.Request(
        method='POST',
        url=API_URL,
        files=files,
        headers={'Authorization': f'Token {API_TOKEN}'}
    )
    
    # Send request
    session = requests.Session()
    response = session.send(req.prepare())
    
    if response.status_code in [200, 201]:
        print(f"✓ Submitted {uuid}")
    else:
        print(f"✗ Failed {uuid}: {response.text}")
```

**API Endpoints:**
- Standard: `https://kc.kobotoolbox.org/api/v1/submissions`
- EU Server: `https://eu.kobotoolbox.org/api/v1/submissions`
- Humanitarian: `https://kobo.humanitarianresponse.info/api/v1/submissions`

## Question Mapping Format

The `question_mapping.json` file maps column names to their hierarchical paths in the XML. It can be in one of two formats:

### Simple Format (paths only)
```json
{
    "today": "today",
    "LeadOrganization_type": "org_details/ORAGANIZATION_LEAD/LeadOrganization_type",
    "email": "org_details/FOCAL_POINTS/email",
    "FOCAL_POINTS": "org_details/FOCAL_POINTS",
    "quantity_resource": "RESPONSES/FIGURES_COMMUNITY/quantities/quantity_resource"
}
```

### Enhanced Format (with choice mappings)
```json
{
  "fields": {
    "today": "today",
    "LeadOrganization_type": "org_details/ORAGANIZATION_LEAD/LeadOrganization_type",
    "email": "org_details/FOCAL_POINTS/email"
  },
  "choices": {
    "LeadOrganization_type": {
      "National NGO": "NATIONAL_NGO",
      "International NGO": "INTERNATIONAL_NGO",
      "UN Agency": "UN_AGENCY"
    }
  }
}
```

The enhanced format allows you to use `--use-labels` flag to convert choice labels in your Excel back to their internal names.

### Auto-Generate Mapping from content.json

The easiest way to generate a mapping is from your KoboToolbox form's `content.json`:

```bash
# Generate mapping automatically
python generate_mapping.py content.json output-mapping.json
```

This will:
1. Extract field paths from the `$xpath` field in each survey item
2. Extract choice lists and create label-to-name mappings
3. Output both in the enhanced format

To get `content.json` from KoboToolbox:
1. Use the API: `https://kf.kobotoolbox.org/api/v2/assets/{form_id}/?format=json`
2. Or download from form settings (if available)
3. The response includes the survey structure with `$xpath` for each field and all choice lists

### Manual Mapping Creation

If you need to create the mapping manually (not recommended), you can extract it from `content.json`:

```python
import json

# Read content.json
with open('content.json') as f:
    data = json.load(f)

# Extract field paths from $xpath
field_paths = {}
for item in data['survey']:
    name = item.get('name')
    xpath = item.get('$xpath')
    if name and xpath:
        field_paths[name] = xpath

# Save as simple mapping
with open('question_mapping.json', 'w') as f:
    json.dump(field_paths, f, indent=2)
```

Note: This creates a simple mapping without choice label conversions. Use `generate_mapping.py` for the full enhanced format.

## XML Structure

The generated XML follows the KoboToolbox submission format:

```xml
<formId id="formId" version="version_string">
    <formhub>
        <uuid>form_uuid</uuid>
    </formhub>
    <today>2025-11-07</today>
    <org_details>
        <ORAGANIZATION_LEAD>
            <LeadOrganization_type>INTERNATIONAL_NGO</LeadOrganization_type>
        </ORAGANIZATION_LEAD>
        <FOCAL_POINTS>
            <position>1</position>
            <email>foo@goo.com</email>
        </FOCAL_POINTS>
    </org_details>
    <RESPONSES>
        <FIGURES_COMMUNITY>
            <position>1</position>
            <parish>JM04</parish>
        </FIGURES_COMMUNITY>
        <FIGURES_COMMUNITY>
            <position>2</position>
            <parish>JM05</parish>
        </FIGURES_COMMUNITY>
    </RESPONSES>
    <__version__>versionHash</__version__>
    <meta>
        <instanceID>uuid:submission_uuid</instanceID>
    </meta>
</formId>
```

## Repeat Groups

Repeat groups are handled automatically:
- Each repeat group has its own sheet in the Excel file
- Rows are linked via `_submission__uuid`
- A `<position>` element is added to each repeat instance
- The hierarchy is preserved based on the mapping file

## Configuration Options

### Form ID
The form ID should match your KoboToolbox form. Find it in:
- Form settings in KoboToolbox UI
- API URL: `https://kf.kobotoolbox.org/api/v2/assets/{form_id}/`

### Form Version
Optional version string that appears in the XML. Default: `"6 (2025-11-12 16:31:33)"`

### Formhub UUID
The UUID in the `<formhub>` element. This should be your form's unique identifier.
Find it in your form's settings or XML structure.

## Troubleshooting

### Missing Data
- Ensure all sheets have the `_submission__uuid` column
- Check that column names match the mapping file exactly
- Verify that repeat group sheet names match the mapping

### XML Validation Errors
- Confirm the form ID matches your KoboToolbox form
- Check that the formhub UUID is correct
- Ensure all required fields are present in the Excel data

### API Submission Failures
- Verify your API token has write permissions
- Check that the form ID in the API URL is correct
- Ensure the XML structure matches your form's structure

## Advanced Usage

### Custom Data Processing

```python
from excel_to_kobo_xml import ExcelToKoboXML

class CustomConverter(ExcelToKoboXML):
    def convert_submission(self, uuid, form_version=None):
        # Add custom data validation
        main_data = self.sheets['data']
        row = main_data[main_data['_submission__uuid'] == uuid].iloc[0]
        
        # Validate required fields
        if pd.isna(row.get('today')):
            raise ValueError(f"Missing required field 'today' for {uuid}")
        
        # Call parent method
        return super().convert_submission(uuid, form_version)

# Use custom converter
converter = CustomConverter('data.xlsx', 'mapping.json')
xml_files = converter.convert_all('./output')
```

### Filtering Submissions

```python
converter = ExcelToKoboXML('data.xlsx', 'mapping.json')

# Only convert submissions from a specific date
main_data = converter.sheets['data']
recent = main_data[main_data['today'] >= '2025-11-01']

results = {}
for uuid in recent['_submission__uuid']:
    xml_string = converter.convert_submission(uuid)
    results[uuid] = xml_string
```

## License

This script is provided as-is for use with KoboToolbox data processing workflows.

## Support

For issues related to:
- KoboToolbox API: https://support.kobotoolbox.org/
- XLSForm structure: https://xlsform.org/
- This script: Check the error messages and troubleshooting section above
