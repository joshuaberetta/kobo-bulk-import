# Quick Start Guide

## Simplest Workflow (Auto-Mapping)

### 1. Setup Config File (One-time)

```bash
# 1. Copy the example config
cp config.example.json config.json

# 2. Edit config.json and set:
{
  "excel": "path/to/your/data.xlsx",
  "mapping": "content.json",              // ← Just point to content.json!
  "form-id": "YOUR_FORM_ID",
  "token": "YOUR_API_TOKEN",
  "use-labels": true,                     // Enable label-to-code conversion
  "dry-run": false
}
```

**Getting content.json:**
- API: `https://kf.kobotoolbox.org/api/v2/assets/{form_id}/?format=json`
- Or download from KoboToolbox form settings

### 2. Test and Submit

```bash
# Test with dry-run first (generates XML, doesn't submit)
python submit_to_kobo.py --config config.json --dry-run

# Submit for real
python submit_to_kobo.py --config config.json
```

**That's it!** The mapping is auto-generated in the background from `content.json`.

---

## Alternative: Manual Mapping Generation

If you prefer to generate the mapping file separately:

### 1. Generate Mapping from content.json (One-time setup)

```bash
# Auto-generate mapping with field paths and choice mappings
python generate_mapping.py content.json question_mapping.json
```

Then update your config to use `question_mapping.json` instead of `content.json`.

---

## Advanced Usage

### 2. Convert Excel to XML Only

```bash
# Convert and save XML files
python excel_to_kobo_xml.py data.xlsx question_mapping.json output_xml/
```

This creates one XML file per submission in the `output_xml/` directory.

### 3. Submit to KoboToolbox (Optional)

**Using a config file (recommended for repeated runs):**

```bash
# 1. Create config file from example
cp config.example.json config.json

# 2. Edit config.json with your values (API token, paths, etc.)

# 3. Run with config
python submit_to_kobo.py --config config.json

# 4. Override specific options as needed
python submit_to_kobo.py --config config.json --uuid SPECIFIC_UUID
```

**Or use command-line arguments directly:**

```bash
# Test first with dry-run
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_API_TOKEN \
    --dry-run \
    --output-dir ./xml_output

# Submit for real
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_API_TOKEN

# Submit with choice label conversion (if your Excel has labels like "National NGO" instead of "NATIONAL_NGO")
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_API_TOKEN \
    --use-labels

# Submit a single submission by UUID
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_API_TOKEN \
    --uuid 12db1b92-ec3b-466c-b41e-9882762575a4

# Full options with all parameters
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping question_mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_API_TOKEN \
    --server https://kc.kobotoolbox.org \
    --formhub-uuid a5c29b3b422446a0acf55f72d9a443d1 \
    --version-id vdjkkW3B5b9mKHZVoDPYbA \
    --form-version "8 (2025-11-13 17:03:35)" \
    --use-labels \
    --output-dir ./xml_output \
    --stop-on-error
```

**Available Options:**
- `--excel`: Path to Excel file (required)
- `--mapping`: Path to mapping JSON file (required)
- `--form-id`: KoboToolbox form ID (required)
- `--token`: API token (required)
- `--server`: Server URL (default: https://kc.kobotoolbox.org)
- `--formhub-uuid`: Formhub UUID for the form (optional)
- `--version-id`: Form version ID like "vdjkkW3B5b9mKHZVoDPYbA" (optional)
- `--form-version`: Form version string like "8 (2025-11-13 17:03:35)" (optional)
- `--uuid`: Submit only one submission with this UUID (optional)
- `--use-labels`: Convert choice labels to names (requires mapping with choices section) (optional)
- `--output-dir`: Save XML files to directory (optional)
- `--dry-run`: Generate XML without submitting (optional)
- `--stop-on-error`: Stop if any submission fails (optional)

## Use as Python Module

```python
from excel_to_kobo_xml import ExcelToKoboXML

# Convert
converter = ExcelToKoboXML('data.xlsx', 'mapping.json')
submissions = converter.convert_all(output_dir='./xml_output')

# Now you have XML strings ready for API submission
for uuid, xml_string in submissions.items():
    print(f"Ready to submit: {uuid}")
    # Your API submission code here
```

## Common Use Cases

### Converting Only Specific Submissions

```python
from excel_to_kobo_xml import ExcelToKoboXML
import pandas as pd

converter = ExcelToKoboXML('data.xlsx', 'mapping.json')

# Filter submissions
main_data = pd.read_excel('data.xlsx', sheet_name='data')
recent = main_data[main_data['today'] >= '2025-11-01']

# Convert only these
for uuid in recent['_submission__uuid']:
    xml = converter.convert_submission(uuid)
    # Process xml...
```

### Validating Before Submission

```python
from excel_to_kobo_xml import ExcelToKoboXML

converter = ExcelToKoboXML('data.xlsx', 'mapping.json')

# Generate all XML
submissions = converter.convert_all(output_dir='./xml_output')

# Review the XML files before submitting
print(f"Generated {len(submissions)} XML files")
print("Review them in ./xml_output/ before submitting")
```

## Troubleshooting

### "Column not found in mapping"
- Run `generate_mapping.py` again with your latest XLSForm
- Check that your Excel column names match your XLSForm question names

### "No submission found with UUID"
- Ensure your Excel has a `_submission__uuid` column
- Check that the UUID exists in all relevant sheets

### API submission fails
- Verify your API token: `https://kf.kobotoolbox.org/token/`
- Check form ID in URL: `https://kf.kobotoolbox.org/#/forms/{form_id}`
- Ensure you have edit permissions on the form

## File Structure

```
your_project/
├── excel_to_kobo_xml.py      # Main converter
├── generate_mapping.py        # Mapping generator
├── submit_to_kobo.py         # API submission helper
├── your_form.xlsx            # Your XLSForm
├── data.xlsx                 # Your data to convert
├── question_mapping.json     # Generated mapping
└── xml_output/               # Generated XML files
    ├── uuid1.xml
    ├── uuid2.xml
    └── ...
```

## Getting Your API Token

1. Go to https://kf.kobotoolbox.org/token/
2. Copy your token
3. Use it with `--token` flag or in Python code

## Getting Your Form ID

1. Open your form in KoboToolbox
2. Look at the URL: `https://kf.kobotoolbox.org/#/forms/{THIS_IS_YOUR_FORM_ID}`
3. Or find it in the form's XML: the root element name

## Need Help?

- Check README.md for detailed documentation
- Review the example files in output_xml/
- Test with `--dry-run` first
