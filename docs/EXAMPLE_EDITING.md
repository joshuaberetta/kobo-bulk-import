# Example: Editing Submissions with deprecatedID

## Scenario
You need to correct the sector for 3 existing submissions in bulk.

## Original Submissions in KoboToolbox

| _submission__uuid (instanceID)          | LeadOrganization_type | sector              | activity_type |
|----------------------------------------|----------------------|---------------------|---------------|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | INTERNATIONAL_NGO    | Food Security       | hot_meal      |
| 0114436d-e9a1-43b2-a154-a166154e7fac  | NATIONAL_NGO         | WASH                | water_supply  |
| 0262b887-9cb5-4bea-bb30-0f11cffd3845  | LOCAL_NGO            | Health              | clinic        |

## Issue
The sector was recorded incorrectly and needs to be updated for all three.

## Solution: Create Edit Spreadsheet

Create an Excel file with these columns:

### Excel Structure (`data/corrections_2025-11-16.xlsx`)

| deprecatedID                           | _submission__uuid                      | LeadOrganization_type | sector                          | activity_type | ... other fields ... |
|----------------------------------------|----------------------------------------|-----------------------|---------------------------------|---------------|---------------------|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | 59f2da4c-0f5b-42a7-9854-65ead887f66c  | INTERNATIONAL_NGO     | Food Security & NUTRITION       | hot_meal      | ...                 |
| 0114436d-e9a1-43b2-a154-a166154e7fac  | 7f3c8d21-9a4b-4e5f-b8c6-1d2e3f4a5b6c  | NATIONAL_NGO          | WASH & Hygiene                  | water_supply  | ...                 |
| 0262b887-9cb5-4bea-bb30-0f11cffd3845  | 8a4d9e32-0b5c-4f6g-c9d7-2e3f4g5h6i7j  | LOCAL_NGO             | Health & Nutrition              | clinic        | ...                 |

### Key Points:

1. **deprecatedID**: The original UUID from KoboToolbox (without "uuid:" prefix)
2. **_submission__uuid**: Generate NEW unique UUIDs for each edit
3. **Other fields**: Include ALL fields with corrected values

### Generate New UUIDs

You can generate UUIDs using:
- Python: `import uuid; print(uuid.uuid4())`
- Online: https://www.uuidgenerator.net/
- Command line: `uuidgen` (Mac/Linux)

## Step-by-Step Process

### 1. Export Current Data
```bash
# Download from KoboToolbox as Excel
# Save as: raw-data/current_data_export.xlsx
```

### 2. Prepare Edit File
```bash
# Open in Excel/Google Sheets
# Add deprecatedID column
# Fill with original UUIDs
# Generate new _submission__uuid values
# Make your corrections
# Save as: raw-data/corrections_2025-11-16.xlsx
```

### 3. Transform (if needed)
```bash
# If your file is already in Kobo format, skip this step
python transform.py raw-data/corrections_2025-11-16.xlsx
# Output: data/corrections_2025-11-16_kobo_import_20251116.xlsx
```

### 4. Test First
```bash
# Generate XML without submitting
python submit.py --config config/config.json --dry-run
```

### 5. Verify XML Output
Check `xml_output/59f2da4c-0f5b-42a7-9854-65ead887f66c.xml`:

```xml
<meta>
  <instanceID>uuid:59f2da4c-0f5b-42a7-9854-65ead887f66c</instanceID>
  <deprecatedID>uuid:00a06a53-1804-4290-bc62-5afc4e2b420a</deprecatedID>
</meta>
```

✅ Correct: Both instanceID and deprecatedID present

### 6. Submit
```bash
python submit.py --config config/config.json
```

### 7. Verify in KoboToolbox
- Check that only 3 submissions exist (not 6)
- Verify the sectors are corrected
- Confirm the instanceID has changed to the new UUID

## What Happens

1. **Before submission**: 3 submissions with old UUIDs and incorrect sectors
2. **XML generated**: Contains both old (deprecatedID) and new (instanceID) UUIDs
3. **API submission**: KoboToolbox finds submission with deprecatedID
4. **Update**: Replaces old submission with new data
5. **After submission**: Same 3 submissions, new UUIDs, corrected sectors

## Common Mistakes to Avoid

❌ **Wrong:**
```
| deprecatedID                                    | _submission__uuid                     |
|------------------------------------------------|---------------------------------------|
| uuid:00a06a53-1804-4290-bc62-5afc4e2b420a     | uuid:59f2da4c-...                     |
```
Don't include "uuid:" prefix in Excel - it's added automatically

❌ **Wrong:**
```
| deprecatedID                           | _submission__uuid                     |
|----------------------------------------|---------------------------------------|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | 00a06a53-1804-4290-bc62-5afc4e2b420a |
```
Don't reuse the same UUID - generate a new one for _submission__uuid

❌ **Wrong:**
```
Only including the fields you want to change
```
Include ALL required fields - missing fields may be cleared

✅ **Correct:**
```
| deprecatedID                           | _submission__uuid                     | ... all fields ... |
|----------------------------------------|---------------------------------------|-------------------|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | 59f2da4c-0f5b-42a7-9854-65ead887f66c | ...               |
```

## Tips

1. **Keep a backup**: Export and save current data before editing
2. **Test on one first**: Submit a single edit before bulk processing
3. **Track your changes**: Keep a log of which deprecatedIDs you edited
4. **Verify incrementally**: Check KoboToolbox after each batch
5. **Use dry-run**: Always test XML generation first

## Questions?

See `docs/EDITING_SUBMISSIONS.md` for comprehensive documentation.
