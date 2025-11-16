# Changelog: deprecatedID Feature

## Date: November 16, 2025

### Feature Added: Bulk Edit Existing Submissions

Added support for editing existing KoboToolbox submissions in bulk using the `deprecatedID` field.

## Changes Made

### 1. Code Changes

#### `scripts/transform_to_kobo.py`
- **Lines 278-280**: Added automatic detection of `deprecatedID` column
- If the column exists in raw data, it's now preserved in the transformed output
- No manual configuration needed - works automatically

#### `scripts/excel_to_kobo_xml.py`
- **Line 217**: Added `deprecatedID` to metadata skip list (not a regular field)
- **Lines 392-400**: Added logic to include `deprecatedID` in XML `<meta>` section
  - Automatically adds "uuid:" prefix if not present
  - Only included if column exists and has a value
  - Placed after `instanceID` in meta section

### 2. Documentation Updates

#### `README.md`
- Added section explaining editing workflow
- Included example table showing deprecatedID usage
- Listed new documentation file

#### `docs/QUICKSTART.md`
- Added "Editing Existing Submissions" section
- Included example Excel structure
- Showed XML output format

#### `QUICK_REFERENCE.md`
- Updated workflow section with editing steps
- Added reference to new documentation

#### `docs/EDITING_SUBMISSIONS.md` (NEW)
- Comprehensive guide for editing submissions
- Step-by-step instructions
- Best practices and troubleshooting
- Complete example workflow

## How It Works

### Input (Excel with deprecatedID column):
```
| deprecatedID                           | _submission__uuid                      | field1 | field2 |
|----------------------------------------|----------------------------------------|--------|--------|
| 00a06a53-1804-4290-bc62-5afc4e2b420a  | 59f2da4c-0f5b-42a7-9854-65ead887f66c  | value1 | value2 |
```

### Output (Generated XML):
```xml
<meta>
  <instanceID>uuid:59f2da4c-0f5b-42a7-9854-65ead887f66c</instanceID>
  <deprecatedID>uuid:00a06a53-1804-4290-bc62-5afc4e2b420a</deprecatedID>
</meta>
```

### Result:
- KoboToolbox updates the submission with `deprecatedID` instead of creating a new one
- The new `instanceID` becomes the identifier for the updated submission
- No duplicates are created

## Usage

### For New Submissions (No Change)
```bash
python transform.py raw-data/data.xlsx
python submit.py --config config/config.json
```

### For Editing Existing Submissions (New)
1. Add `deprecatedID` column to your Excel with original UUIDs
2. Add new `_submission__uuid` values for each row
3. Use the same commands as above - automatic detection!

```bash
python transform.py raw-data/data_with_deprecatedID.xlsx
python submit.py --config config/config.json
```

## Backward Compatibility

✅ **Fully backward compatible**
- Existing workflows work without changes
- `deprecatedID` is optional - only used if present
- No breaking changes to API or file formats

## Testing Recommendations

1. **Test with dry-run first:**
   ```bash
   python submit.py --config config/config.json --dry-run
   ```

2. **Verify XML output:**
   - Check `xml_output/` folder
   - Confirm `deprecatedID` appears in meta section
   - Ensure proper UUID formatting

3. **Submit test batch:**
   - Start with 1-2 submissions
   - Verify updates in KoboToolbox
   - Check no duplicates created

## Files Modified

- `scripts/transform_to_kobo.py`
- `scripts/excel_to_kobo_xml.py`
- `README.md`
- `docs/QUICKSTART.md`
- `QUICK_REFERENCE.md`

## Files Created

- `docs/EDITING_SUBMISSIONS.md`
- `CHANGELOG_DEPRECATEDID.md` (this file)

## Benefits

1. **Bulk corrections**: Fix errors across many submissions at once
2. **No duplicates**: Updates existing records instead of creating new ones
3. **Automatic**: No manual XML editing required
4. **Flexible**: Works with any fields in your form
5. **Safe**: Test with dry-run before submitting

## Support

See `docs/EDITING_SUBMISSIONS.md` for:
- Detailed instructions
- Best practices
- Troubleshooting guide
- Complete examples
