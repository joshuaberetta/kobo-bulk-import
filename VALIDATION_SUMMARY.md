# Validation Enhancement Summary

## What Was Added

Enhanced the bulk import script to track and report data quality issues during the conversion process.

## Features

### 1. Dry-Run Mode Validation Report

When running with `--dry-run`, the script now provides a detailed validation report showing:

- **Blank Parishes**: Submissions with empty parish values
- **Blank Communities**: Submissions with empty community values  
- **Unmatched Parishes**: Parish values that don't match any pcode in the form
- **Unmatched Communities**: Community values that don't match any pcode in the form

Example output:
```
================================================================================
⚠️  VALIDATION ISSUES DETECTED
================================================================================

⚠️  Unmatched Communities (2 occurrences):
   - 'Strathbogie' (2x) - e.g., 8ea90304-f5c1-4c41-b61e-59547fa2cc15

================================================================================
⚠️  These values were kept as-is in the XML but may not match
    the KoboToolbox form's expected choice values (pcodes).
================================================================================
```

### 2. Pre-Submission Warning

When running without `--dry-run` (actual submission mode), if validation issues are detected:

- Script displays a warning with issue count summary
- Prompts user for confirmation before proceeding
- User can cancel to review issues or continue with submission

Example warning:
```
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
⚠️  WARNING: VALIDATION ISSUES DETECTED
!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!

Found 2 validation issue(s):
  - 2 unmatched community value(s)

These values may not match KoboToolbox form's expected pcodes.
Submissions with invalid values may not appear correctly in reports.

Run with --dry-run to see detailed validation report.

!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
Do you want to continue with submission? (yes/no):
```

## Technical Implementation

### Modified Files

1. **scripts/excel_to_kobo_xml.py**
   - Added `validation_issues` dict to track 4 types of issues
   - Modified `_convert_label_to_name()` to accept tracking parameters
   - Updated `_create_nested_element()` to pass uuid for tracking
   - Updated `_build_group_hierarchy()` to propagate uuid through call chain
   - Added validation reporting in `convert_all()` method

2. **scripts/submit_to_kobo.py**
   - Added pre-submission validation check
   - Prompts user for confirmation if issues detected
   - Allows cancellation before submission

### Validation Logic

The script validates parish and community fields by:

1. Checking if value is blank/null → tracked as blank
2. Converting label to pcode using case-insensitive matching
3. If no match found, checking if value is already a pcode (starts with "JM" + digits)
4. If not a pcode, tracking as unmatched with original value and UUID

## Example: WFP Data Validation

Running dry-run on WFP data (`data/20251118-wfp-with-repeats.xlsx`):

```bash
python scripts/submit_to_kobo.py --config config/config.json \
  --excel data/20251118-wfp-with-repeats.xlsx \
  --dry-run --use-labels
```

Results:
- **38 submissions** processed
- **2 validation issues** detected
- Issue: Community "Strathbogie" (appears 2x in submission 8ea90304...)
- Root cause: "Strathbogie" is not in the form's admin2 choice list
- Action needed: Either add "Strathbogie" to form choices or correct data to use existing community

## Benefits

1. **Data Quality**: Catches mapping issues before submission
2. **Transparency**: Users see exactly which values don't match
3. **Safety**: Prevents accidental submission of problematic data
4. **Debugging**: Detailed report helps identify data cleanup needs
5. **Flexibility**: Warning allows informed decision to proceed or cancel

## Usage

### Check for issues (dry-run):
```bash
python scripts/submit_to_kobo.py --config config/config.json \
  --excel your-data.xlsx --dry-run --use-labels
```

### Submit with validation check:
```bash
python scripts/submit_to_kobo.py --config config/config.json \
  --excel your-data.xlsx --use-labels
```
(Will prompt for confirmation if issues found)
