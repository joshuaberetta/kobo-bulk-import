# 5W Data Transformation Script for Kobo Import

## Overview

`transform_to_kobo.py` transforms 5W offline form Excel files from any organization into the format required for importing to Kobo.

## Features

- **Auto-detection**: Automatically detects the header row in Excel files
- **Flexible input**: Works with any organization's 5W form (not just MercyChef)
- **Smart naming**: Generates descriptive output filenames based on input
- **Customizable**: Override sheet name and header row when needed

## What It Does

1. Reads Excel files from any location (typically `raw-data/` directory)
2. Auto-detects the header row or uses a specified row number
3. Extracts data from the specified sheet (default: "Data Entry")
4. Selects only the 21 columns required for Kobo import
5. Generates a unique UUID for each submission record
6. Removes any completely empty rows
7. Saves the transformed data to the `data/` directory

## Usage

### Basic Usage (Auto-detect everything)

```bash
python transform_to_kobo.py raw-data/Organization_5W_Form.xlsx
```

This will automatically:
- Detect the header row
- Use "Data Entry" as the sheet name
- Generate output: `data/Organization_5W_Form_kobo_import_YYYYMMDD.xlsx`

### Specify Custom Output File

```bash
python transform_to_kobo.py raw-data/input.xlsx data/custom_output.xlsx
```

### Specify Sheet Name

```bash
python transform_to_kobo.py input.xlsx -s "Sheet1"
```

### Specify Header Row (0-based index)

```bash
python transform_to_kobo.py input.xlsx -r 8
```

### All Options Combined

```bash
python transform_to_kobo.py input.xlsx output.xlsx -s "Data Entry" -r 8
```

### Help

```bash
python transform_to_kobo.py --help
```

## Examples for Different Organizations

### MercyChef
```bash
python transform_to_kobo.py raw-data/MercyChef-Jamaica_Melissa_5W_OfflineForm.xlsx
```

### Another Organization
```bash
python transform_to_kobo.py raw-data/RedCross_5W_Data.xlsx
```

### Custom Configuration
```bash
python transform_to_kobo.py raw-data/NGO_Form.xlsx -s "Responses" -r 5
```

## Command-Line Options

| Option | Short | Description |
|--------|-------|-------------|
| `input_file` | - | Path to the input Excel file (required) |
| `output_file` | - | Path to the output file (optional, auto-generated if omitted) |
| `--sheet` | `-s` | Sheet name to read (default: "Data Entry") |
| `--header-row` | `-r` | Header row number, 0-based (default: auto-detect) |
| `--help` | `-h` | Show help message |

The script produces an Excel file with 22 columns:

1. LeadOrganization_type
2. LeadOrganization_type_2
3. LeadOrganization_name
4. LeadOrganization_name_2
5. same_as_lead
6. ImplementingOrganization_type
7. ImplementingOrganization_type_2
8. ImplementingOrganization_name
9. ImplementingOrganization_name_2
10. sector
11. scetor_2
12. activity_type
13. activity_type_other
14. activity_title
15. activity_Status
16. comments
17. URL_to_important_resources
18. resource_type
19. resource_type_other
20. resource_unit_type
21. resource_unit_type_other
22. _submission__uuid (generated)

## Requirements

- Python 3.x
- pandas
- openpyxl

Install dependencies:
```bash
pip install pandas openpyxl
```

(These are already in `requirements.txt`)

## Example Output

```
Reading raw data from: raw-data/Organization_5W_Form.xlsx
Auto-detecting header row...
Detected header at row 9
Read 246 rows from raw data file
Transformed data: 246 rows, 22 columns
Saving transformed data to: data/Organization_5W_Form_kobo_import_20251115.xlsx
✓ Successfully transformed 246 records
✓ Output file: data/Organization_5W_Form_kobo_import_20251115.xlsx
```

## Next Steps

After running this script, use the generated file in the `data/` directory with the Kobo import scripts (e.g., `submit_to_kobo.py`) to upload the data to Kobo.
