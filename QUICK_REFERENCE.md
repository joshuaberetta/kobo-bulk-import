# Quick Reference

## 🎯 Common Commands

### Transform Data
```bash
# Basic (auto-detect everything)
python transform.py raw-data/Organization_5W_Form.xlsx

# With output path
python transform.py raw-data/input.xlsx data/output.xlsx

# Advanced options
python scripts/transform_to_kobo.py input.xlsx -s "Sheet1" -r 8
```

### Submit to Kobo
```bash
# Setup (first time only)
cp config/config.example.json config/config.json
# Edit config/config.json

# Dry run (test without submitting)
python submit.py --config config/config.json --dry-run

# Submit
python submit.py --config config/config.json
```

### Direct Script Access
```bash
# All scripts are in scripts/ folder
python scripts/transform_to_kobo.py --help
python scripts/submit_to_kobo.py --help
python scripts/generate_mapping.py --help

# Cleanup
bash scripts/cleanup.sh
```

## 📂 File Locations

| Type | Location | Description |
|------|----------|-------------|
| Raw data | `raw-data/` | Original Excel files |
| Processed data | `data/` | Transformed, ready for import |
| Config files | `config/` | API tokens, mappings, settings |
| Scripts | `scripts/` | Main Python scripts |
| Documentation | `docs/` | All documentation files |

## 🔑 Config Files

- `config/config.json` - Main configuration (git-ignored)
- `config/config.example.json` - Template to copy
- `config/content.json` - Kobo form structure
- `config/question-mapping.json` - Field mappings

## 📖 Documentation

- `README.md` - This quick overview
- `docs/QUICKSTART.md` - 5-minute tutorial
- `docs/EDITING_SUBMISSIONS.md` - Edit existing submissions in bulk
- `docs/CONFIG.md` - Config file reference
- `docs/MAPPING_GENERATOR.md` - Auto-mapping guide
- `docs/TRANSFORM_MERCYCHEF_README.md` - Transform details
- `docs/OLD_README.md` - Original comprehensive docs

## 🔄 Typical Workflow

### Creating New Submissions
1. Place Excel file in `raw-data/`
2. `python transform.py raw-data/yourfile.xlsx`
3. Edit `config/config.json` (first time only)
4. `python submit.py --config config/config.json --dry-run`
5. `python submit.py --config config/config.json`

### Editing Existing Submissions
1. Add `deprecatedID` column with original UUIDs to your Excel
2. Generate new `_submission__uuid` values for each row
3. Follow same workflow as creating new submissions
4. See `docs/EDITING_SUBMISSIONS.md` for details

## ⚡ Tips

- Use `--dry-run` first to test
- Check `config/config.json` paths are correct
- Wrapper scripts (`transform.py`, `submit.py`) are in root for convenience
- Full scripts are in `scripts/` for advanced options
