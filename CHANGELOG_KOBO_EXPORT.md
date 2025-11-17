# Update: Kobo Export Support for Editing Workflow

## Summary

Enhanced the bulk import tool to work seamlessly with KoboToolbox data exports, making it easy to export, edit, and re-import data.

## Changes Made

### Code Enhancements

#### 1. **Dynamic Sheet Detection** (`excel_to_kobo_xml.py`)

**Before:** Hardcoded to use sheet named "data"
```python
main_data = self.sheets['data']
```

**After:** Automatically detects main data sheet
```python
# Uses first sheet with _submission__uuid column
# Falls back to first sheet if no UUID column found
main_data = self.sheets[self.main_sheet_name]
```

**Benefits:**
- Works with any sheet name (e.g., Kobo's "5W__Hurricane_Melissa_...")
- No manual sheet renaming required
- Automatic fallback for edge cases

#### 2. **Kobo Metadata Filtering** (`excel_to_kobo_xml.py`)

Added `_is_kobo_metadata_column()` method that automatically excludes:

**Metadata columns filtered out:**
```
_submission_time          _submission__submission_time
_validation_status        _submission__validation_status
_notes                   _submission__notes
_status                  _submission__status
_submitted_by            _submission__submitted_by
__version__              _submission___version__
_tags                    _submission__tags
_index                   
_id                      _parent_table_name
_submission__id          _parent_index
```

**Preserved columns:**
- `_submission__uuid` (required)
- `deprecatedID` (for editing)
- All actual form data fields

**Benefits:**
- Export from Kobo → Edit → Re-import (no cleanup needed)
- Automatic filtering in both main data and repeat groups
- No manual column deletion required

#### 3. **Enhanced Repeat Group Processing**

Updated repeat group iteration to use the new metadata filter:

**Before:**
```python
if col_name.startswith('_'):
    continue
```

**After:**
```python
if col_name == '_submission__uuid' or self._is_kobo_metadata_column(col_name):
    continue
```

**Benefits:**
- Consistent filtering across all data types
- Handles complex metadata patterns
- Works with nested repeat groups

### Documentation Updates

#### Enhanced Files:
1. **`docs/EDITING_SUBMISSIONS.md`**
   - Added "Method 1: Using Kobo Export (Recommended)" section
   - Documented automatic features
   - Step-by-step Kobo export workflow

2. **`README.md`**
   - Updated editing workflow with export-first approach
   - Listed automatic features

3. **`docs/QUICKSTART.md`**
   - Added quick workflow for Kobo exports
   - Highlighted automatic features

## Complete Editing Workflow (Export → Edit → Import)

### Step 1: Export from KoboToolbox
```
Go to project → DATA → Downloads → Excel
Save as: data/project_export_2025-11-16.xlsx
```

### Step 2: Prepare for Editing

**In Excel:**
1. Copy `_submission__uuid` column
2. Create new column named `deprecatedID`
3. Paste the copied UUIDs

**Using helper script:**
```bash
python scripts/generate_uuids.py --excel data/project_export_2025-11-16.xlsx
```
This generates new `_submission__uuid` values.

### Step 3: Make Your Edits

Edit any fields in Excel - the tool will:
- ✅ Automatically use the first sheet (no renaming needed)
- ✅ Filter out all Kobo metadata columns
- ✅ Preserve your `deprecatedID` values
- ✅ Include only actual form data in XML

### Step 4: Submit

```bash
# Test first
python submit.py --config config/config.json --dry-run

# Review XML in xml_output/ folder
# Verify deprecatedID is present in <meta> section

# Submit for real
python submit.py --config config/config.json
```

### Step 5: Verify in KoboToolbox

- Same number of submissions (no duplicates)
- Fields updated correctly
- New instanceID (from new _submission__uuid)

## Technical Details

### Sheet Detection Logic

```python
# 1. Search for sheet with _submission__uuid column
for sheet_name in excel_file.sheet_names:
    if '_submission__uuid' in sheet_columns:
        main_sheet_name = sheet_name
        break

# 2. Fallback to first sheet if not found
if main_sheet_name is None:
    main_sheet_name = first_sheet
```

### Metadata Filtering Logic

```python
def _is_kobo_metadata_column(col_name):
    # Exact matches
    if col_name in kobo_metadata_list:
        return True
    
    # Pattern matching
    if col_name.startswith('_submission__') and col_name != '_submission__uuid':
        return True
    
    # Underscore-prefixed (except allowed ones)
    if col_name.startswith('_') and col_name not in allowed:
        return True
    
    return False
```

### Applied Everywhere

- ✅ Main data sheet processing
- ✅ Repeat group processing
- ✅ Field hierarchy building
- ✅ XML generation

## Example Comparison

### Kobo Export (what you download):

| _id | _submission_time | _status | _submission__uuid | LeadOrg | sector | _tags |
|-----|------------------|---------|-------------------|---------|--------|-------|
| 123 | 2025-11-16 10:30 | valid   | 00a06a53-...     | Org1    | Health | tag1  |

### What You Edit (add deprecatedID, new UUID, change fields):

| deprecatedID | _submission__uuid | LeadOrg | sector    | _id | _status | ...metadata... |
|--------------|-------------------|---------|-----------|-----|---------|----------------|
| 00a06a53-... | 59f2da4c-...     | Org1    | **WASH**  | 123 | valid   | ...            |

### What Goes in XML (metadata filtered, only form data + UUIDs):

```xml
<meta>
  <instanceID>uuid:59f2da4c-0f5b-42a7-9854-65ead887f66c</instanceID>
  <deprecatedID>uuid:00a06a53-1804-4290-bc62-5afc4e2b420a</deprecatedID>
</meta>
<org_details>
  <ORAGANIZATION_LEAD>
    <LeadOrganization_name>Org1</LeadOrganization_name>
  </ORAGANIZATION_LEAD>
</org_details>
<RESPONSES>
  <sector>WASH</sector>
</RESPONSES>
```

## Benefits

### For Users
1. **No manual cleanup** - Export and edit directly
2. **No sheet renaming** - Works with any sheet name
3. **Fewer errors** - Automatic filtering prevents mistakes
4. **Faster workflow** - Export → Edit → Import

### Technical
1. **Robust** - Handles various Kobo export formats
2. **Flexible** - Works with custom sheet names
3. **Clean** - Only includes relevant data in XML
4. **Safe** - Preserves required metadata (_submission__uuid, deprecatedID)

## Backward Compatibility

✅ **100% backward compatible**
- Existing workflows unchanged
- "data" sheet name still works
- Manual data files work as before
- No breaking changes

## Testing Checklist

- [x] Dynamic sheet detection with various names
- [x] Metadata filtering in main data
- [x] Metadata filtering in repeat groups
- [x] Kobo export → edit → import workflow
- [x] Backward compatibility with "data" sheet
- [x] deprecatedID preservation
- [x] Multiple repeat groups
- [x] No syntax errors

## Files Modified

- `scripts/excel_to_kobo_xml.py` - Core changes
- `docs/EDITING_SUBMISSIONS.md` - Enhanced workflow documentation
- `README.md` - Updated editing section
- `docs/QUICKSTART.md` - Added Kobo export workflow

## Next Steps for Users

1. **Export your data** from KoboToolbox
2. **No cleanup needed** - use the export as-is
3. **Add deprecatedID** column with original UUIDs
4. **Generate new UUIDs** using helper script
5. **Make edits** to your data
6. **Submit** using standard workflow

The tool handles everything else automatically!
