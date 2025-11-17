# Excel to KoboToolbox Bulk Import Utility

A set of tools to transform Excel data and bulk import submissions to KoboToolbox.

## 📁 Directory Structure

```
.
├── README.md                 # This file
├── requirements.txt          # Python dependencies
├── transform.py              # Quick wrapper: Transform data to Kobo format
├── submit.py                 # Quick wrapper: Submit data to Kobo
│
├── config/                   # Configuration files
│   ├── config.example.json   # Template configuration
│   ├── config.json          # Your actual config (git-ignored)
│   ├── content.json         # Kobo form structure
│   └── question-mapping.json # Field mapping
│
├── scripts/                  # Main Python scripts
│   ├── transform_to_kobo.py  # Transform Excel to Kobo format
│   ├── submit_to_kobo.py     # Submit data to Kobo API
│   ├── excel_to_kobo_xml.py  # Excel to XML converter
│   ├── generate_mapping.py   # Auto-generate field mappings
│   └── cleanup.sh           # Cleanup test files
│
├── docs/                     # Documentation
│   ├── QUICKSTART.md
│   ├── CONFIG.md
│   ├── MAPPING_GENERATOR.md
│   ├── TRANSFORM_MERCYCHEF_README.md
│   └── OLD_README.md        # Original detailed README
│
├── data/                     # Processed data ready for import
├── raw-data/                 # Original source data files
└── venv/                     # Python virtual environment
```

## 🚀 Quick Start

### 1. Transform Data to Kobo Format

Transform any organization's 5W offline form Excel file:

```bash
python transform.py raw-data/YourOrganization_5W_Form.xlsx
```

Output will be saved to `data/` folder with proper Kobo import format.

### 2. Submit to Kobo

```bash
# First time: Setup configuration
cp config/config.example.json config/config.json
# Edit config/config.json with your API token and form ID

# Submit data
python submit.py --config config/config.json
```

## 📚 Documentation

- **[QUICKSTART.md](docs/QUICKSTART.md)** - Get started in 5 minutes
- **[EDITING_SUBMISSIONS.md](docs/EDITING_SUBMISSIONS.md)** - Edit existing submissions in bulk
- **[CONFIG.md](docs/CONFIG.md)** - Configuration file reference
- **[MAPPING_GENERATOR.md](docs/MAPPING_GENERATOR.md)** - Auto-generate field mappings
- **[TRANSFORM_MERCYCHEF_README.md](docs/TRANSFORM_MERCYCHEF_README.md)** - Data transformation details
- **[OLD_README.md](docs/OLD_README.md)** - Original comprehensive documentation

## 🛠️ Advanced Usage

### Transform with Options

```bash
# Specify output file
python scripts/transform_to_kobo.py input.xlsx output.xlsx

# Specify sheet name and header row
python scripts/transform_to_kobo.py input.xlsx -s "Sheet1" -r 8

# Get help
python scripts/transform_to_kobo.py --help
```

### Submit with Options

```bash
# Dry run (don't actually submit)
python scripts/submit_to_kobo.py --config config/config.json --dry-run

# Process specific file
python scripts/submit_to_kobo.py --excel data/your-file.xlsx --config config/config.json
```

## 📦 Installation

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

## 🔧 Requirements

- Python 3.7+
- pandas
- openpyxl
- requests

## 📝 Workflow

### Creating New Submissions

1. **Place raw data** → `raw-data/` folder
2. **Transform data** → `python transform.py raw-data/file.xlsx`
3. **Configure API** → Edit `config/config.json`
4. **Submit to Kobo** → `python submit.py --config config/config.json`

### Editing Existing Submissions

To edit existing submissions in bulk, include a `deprecatedID` column in your spreadsheet:

1. **Export from KoboToolbox** → Download your data as Excel
2. **Add deprecatedID column** → Copy `_submission__uuid` values to a new column named `deprecatedID`
3. **Generate new UUIDs** → Create new values for `_submission__uuid` column
4. **Make your edits** → Update any fields you want to change
5. **Submit** → Use the same workflow as creating new submissions

The tool automatically:
- Uses the first sheet as main data (no need to rename)
- Filters out Kobo metadata columns
- Includes deprecatedID in the XML for proper updates

**Example:**
```
| deprecatedID                           | _submission__uuid                      | ... other fields ... |
|----------------------------------------|----------------------------------------|----------------------|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | 59f2da4c-0f5b-42a7-9854-65ead887f66c  | ...                  |
```

The `deprecatedID` will be included in the XML submission metadata, allowing KoboToolbox to update the existing submission rather than creating a duplicate.

See [EDITING_SUBMISSIONS.md](docs/EDITING_SUBMISSIONS.md) for detailed instructions.

## 🧹 Maintenance

Clean up test files and outputs:

```bash
bash scripts/cleanup.sh
```

## 📄 License

MIT License - See project repository for details.
