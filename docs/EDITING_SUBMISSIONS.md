# Editing Existing Submissions in Bulk

This guide explains how to use the bulk import tool to edit existing submissions in KoboToolbox.

## Overview

When you include a `deprecatedID` column in your Excel data, the tool will generate XML submissions that update existing records rather than creating new ones. This is useful for:

- Correcting data errors in bulk
- Updating incomplete submissions
- Mass-editing submission fields

## How It Works

KoboToolbox uses the `deprecatedID` field in the submission XML to identify which existing submission should be replaced. The process is:

1. The `deprecatedID` contains the UUID of the submission you want to edit
2. The `_submission__uuid` contains a new UUID for this update
3. When submitted, KoboToolbox replaces the old submission with the new data

## Step-by-Step Guide

### 1. Export Existing Data

First, download your existing submissions from KoboToolbox in Excel format. This gives you the current data and the UUIDs you need.

### 2. Prepare Your Excel File

Add a `deprecatedID` column to your data:

```
| deprecatedID                           | _submission__uuid                      | LeadOrganization_type | sector | ... |
|----------------------------------------|----------------------------------------|-----------------------|--------|-----|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | 59f2da4c-0f5b-42a7-9854-65ead887f66c  | INTERNATIONAL_NGO     | Health | ... |
| 0114436d-e9a1-43b2-a154-a166154e7fac  | 7f3c8d21-9a4b-4e5f-b8c6-1d2e3f4a5b6c  | NATIONAL_NGO          | WASH   | ... |
```

**Important:**
- `deprecatedID`: The original UUID from the submission you want to edit (without "uuid:" prefix)
- `_submission__uuid`: A new, unique UUID for this edit operation
- All other columns: The updated data you want to submit

**Helper Script: Generate UUIDs**

Use the included helper script to automatically add new UUIDs:

```bash
# Add UUIDs to an Excel file that has deprecatedID column
python scripts/generate_uuids.py --excel data/edits.xlsx

# Or generate individual UUIDs
python scripts/generate_uuids.py --count 5
```

### 3. Transform the Data

Use the standard transform process if your data is in raw format:

```bash
python transform.py raw-data/your_updated_data.xlsx
```

The transform script automatically detects and preserves the `deprecatedID` column.

### 4. Submit the Updates

Submit using the standard submission process:

```bash
python submit.py --config config/config.json
```

Or with full options:

```bash
python scripts/submit_to_kobo.py \
    --excel data/your_updated_data.xlsx \
    --mapping config/question-mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_API_TOKEN
```

### 5. Verify the Updates

Check KoboToolbox to confirm:
- The original submissions have been updated
- No duplicate submissions were created
- All changes are reflected correctly

## Generated XML Structure

When you include `deprecatedID`, the generated XML includes both identifiers in the `<meta>` section:

```xml
<meta>
  <instanceID>uuid:59f2da4c-0f5b-42a7-9854-65ead887f66c</instanceID>
  <deprecatedID>uuid:00a06a53-1804-4290-bc62-5afc4e2b420a</deprecatedID>
</meta>
```

This tells KoboToolbox:
- `instanceID`: The new identifier for this submission
- `deprecatedID`: Replace the submission with this UUID

## Best Practices

### 1. Always Test First

Use the dry-run option to verify XML generation before submitting:

```bash
python submit.py --config config/config.json --dry-run
```

This generates XML files in the `xml_output/` directory for review.

### 2. Keep a Backup

Before bulk editing:
1. Export all your current data from KoboToolbox
2. Save it with a timestamp: `backup_2025-11-16.xlsx`
3. Keep this as a rollback option

### 3. Edit in Batches

For large datasets:
- Edit and submit in smaller batches (e.g., 50-100 at a time)
- Verify each batch before continuing
- This makes it easier to catch and fix issues

### 4. Track Your UUIDs

Keep a mapping of which deprecatedIDs you're updating:

```csv
deprecatedID,_submission__uuid,edit_reason,edit_date
00a06a53-1804-4290-bc62-5afc4e2b420a,59f2da4c-0f5b-42a7-9854-65ead887f66c,Corrected sector,2025-11-16
```

### 5. Verify After Submission

After submitting edits:
1. Download the data from KoboToolbox
2. Compare with your intended changes
3. Check that no duplicates were created

## Troubleshooting

### Submission Creates Duplicate Instead of Updating

**Possible causes:**
- The `deprecatedID` doesn't match an existing submission UUID
- Missing "uuid:" prefix (the tool should add this automatically)
- The original submission was deleted

**Solution:**
- Verify the deprecatedID exists in KoboToolbox
- Check the XML output to ensure proper formatting
- Ensure you have edit permissions on the form

### Missing deprecatedID in XML

**Possible cause:**
- The column is named incorrectly (must be exactly `deprecatedID`)
- The value is empty/null

**Solution:**
- Check column name spelling (case-sensitive)
- Ensure all rows have valid deprecatedID values
- Review the generated XML files

### Some Edits Work, Others Don't

**Possible cause:**
- Inconsistent deprecatedID values
- Some UUIDs don't exist in KoboToolbox

**Solution:**
- Cross-reference your deprecatedIDs with exported data
- Check which submissions failed and verify their UUIDs
- Re-submit failed submissions individually for debugging

## Example Workflow

Here's a complete example of editing submissions:

```bash
# 1. Export current data from KoboToolbox
# Save as: raw-data/kobo_export_2025-11-16.xlsx

# 2. Make your edits in Excel
# Add deprecatedID column with original UUIDs
# Add new _submission__uuid values for each row
# Update the fields you want to change

# 3. Transform the data (if needed)
python transform.py raw-data/kobo_export_2025-11-16_edited.xlsx

# 4. Test first with dry-run
python submit.py --config config/config.json --dry-run

# 5. Review generated XML in xml_output/
# Check that deprecatedID is present in meta section

# 6. Submit for real
python submit.py --config config/config.json

# 7. Verify in KoboToolbox
# Check that submissions were updated, not duplicated
```

## Advanced: Partial Updates

You can edit just specific fields:

1. Export existing data
2. Keep only the columns you want to edit (plus UUIDs)
3. Add deprecatedID column
4. Update only those fields
5. Submit

**Note:** All fields in your Excel will be submitted. If you omit a field, it may be cleared in KoboToolbox. Always include all required fields.

## Questions?

- Review the generated XML files to understand the structure
- Test with a single submission first before bulk editing
- Check KoboToolbox documentation for deprecatedID behavior
- Contact support if you encounter persistent issues
