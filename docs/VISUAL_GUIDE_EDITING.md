# Visual Guide: Edit Existing Submissions

## The Complete Workflow

```
┌─────────────────────────────────────────────────────────────────┐
│                    1. EXPORT FROM KOBOTOOLS                     │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    Go to Project → DATA → Downloads → Excel
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Downloaded: 5W__Hurricane_Melissa_..._2025-11-16.xlsx         │
│                                                                 │
│  Sheet: "5W__Hurricane_Melissa_Humanitarian_Response..."       │
│  ┌──────────┬─────────────┬────────┬──────────┬───────────┐   │
│  │   _id    │ _status     │ _uuid  │ LeadOrg  │  sector   │   │
│  ├──────────┼─────────────┼────────┼──────────┼───────────┤   │
│  │   123    │ validated   │ 00a0.. │  Org1    │  Health   │   │
│  │   124    │ validated   │ 0114.. │  Org2    │  WASH     │   │
│  └──────────┴─────────────┴────────┴──────────┴───────────┘   │
│                                                                 │
│  Contains metadata columns: _id, _status, _submission_time,    │
│  _tags, _notes, etc. (will be auto-filtered)                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│               2. ADD deprecatedID & NEW UUIDs                   │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    Option A: Manual in Excel
    1. Copy _submission__uuid column
    2. Create new column "deprecatedID"
    3. Paste copied values
    4. Generate new UUIDs for _submission__uuid
                              ↓
    Option B: Using Helper Script
    python scripts/generate_uuids.py --excel data/export.xlsx
    (Then manually copy old UUIDs to deprecatedID)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Prepared: export_with_deprecatedID.xlsx                       │
│  ┌─────────────┬──────────┬────────┬──────────┬──────────┐    │
│  │ deprecatedID│  _uuid   │  _id   │ LeadOrg  │ sector   │    │
│  ├─────────────┼──────────┼────────┼──────────┼──────────┤    │
│  │   00a0..    │ 59f2..   │  123   │  Org1    │ Health   │    │
│  │   0114..    │ 7f3c..   │  124   │  Org2    │ WASH     │    │
│  └─────────────┴──────────┴────────┴──────────┴──────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      3. MAKE YOUR EDITS                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    Edit any fields you need to change
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Edited: export_with_deprecatedID.xlsx                         │
│  ┌─────────────┬──────────┬────────┬──────────┬──────────┐    │
│  │ deprecatedID│  _uuid   │  _id   │ LeadOrg  │ sector   │    │
│  ├─────────────┼──────────┼────────┼──────────┼──────────┤    │
│  │   00a0..    │ 59f2..   │  123   │  Org1    │ NUTRITION│← changed
│  │   0114..    │ 7f3c..   │  124   │  Org2    │ Shelter  │← changed
│  └─────────────┴──────────┴────────┴──────────┴──────────┘    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    4. SUBMIT (DRY-RUN FIRST)                    │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    python submit.py --config config.json --dry-run
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│  Generated XML: xml_output/59f2da4c-....xml                    │
│  ┌───────────────────────────────────────────────────────────┐ │
│  │ <meta>                                                    │ │
│  │   <instanceID>uuid:59f2da4c-...</instanceID>             │ │
│  │   <deprecatedID>uuid:00a06a53-...</deprecatedID>  ← ✓    │ │
│  │ </meta>                                                   │ │
│  │ <RESPONSES>                                               │ │
│  │   <sector>NUTRITION</sector>                      ← ✓    │ │
│  │ </RESPONSES>                                              │ │
│  └───────────────────────────────────────────────────────────┘ │
│                                                                 │
│  ✓ First sheet auto-detected                                   │
│  ✓ Metadata columns filtered (_id, _status, etc.)              │
│  ✓ deprecatedID included in <meta>                             │
│  ✓ Only form data in XML body                                  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
            Review XML looks correct? YES
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                      5. SUBMIT FOR REAL                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    python submit.py --config config.json
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  KOBOTOOLS RECEIVES XML                         │
│                                                                 │
│  Checks: Is there a deprecatedID?                              │
│    YES → Find submission with UUID: 00a06a53-...               │
│       → Replace it with new data                               │
│       → New instanceID: 59f2da4c-...                            │
│                                                                 │
│  Result: UPDATED (not duplicated)                              │
└─────────────────────────────────────────────────────────────────┘
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                  6. VERIFY IN KOBOTOOLS                         │
└─────────────────────────────────────────────────────────────────┘
                              ↓
    Check your project:
    ✓ Same number of submissions (no duplicates)
    ✓ Sector changed to NUTRITION
    ✓ Instance ID is now 59f2da4c-...
    ✓ All other data preserved
                              ↓
                        ✅ COMPLETE!
```

## What Happens Automatically

```
┌─────────────────────────────────────────────────────────────────┐
│                    AUTOMATIC PROCESSING                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  YOUR EXCEL:                                                    │
│  ┌──────────┬─────────┬──────────┬──────────┬────────┬──────┐ │
│  │   _id    │ _status │ _tags    │ _uuid    │ sector │ ...  │ │
│  │   123    │ valid   │ tag1     │ 59f2..   │ Health │ ...  │ │
│  └──────────┴─────────┴──────────┴──────────┴────────┴──────┘ │
│                                                                 │
│                           ↓                                     │
│                  AUTOMATIC FILTERING                            │
│                           ↓                                     │
│                                                                 │
│  WHAT GETS INCLUDED IN XML:                                     │
│  ┌──────────┬────────┐                                         │
│  │  _uuid   │ sector │  ← Only form fields + UUID              │
│  │  59f2..  │ Health │                                         │
│  └──────────┴────────┘                                         │
│                                                                 │
│  WHAT GETS FILTERED OUT:                                        │
│  ✗ _id                    (Kobo metadata)                       │
│  ✗ _status                (Kobo metadata)                       │
│  ✗ _tags                  (Kobo metadata)                       │
│  ✗ _submission_time       (Kobo metadata)                       │
│  ✗ _validation_status     (Kobo metadata)                       │
│  ✗ _notes                 (Kobo metadata)                       │
│  ✗ All other _* columns   (Kobo metadata)                       │
│                                                                 │
│  WHAT GETS PRESERVED:                                           │
│  ✓ _submission__uuid      (Required)                            │
│  ✓ deprecatedID           (For editing)                         │
│  ✓ All form data fields   (Your actual data)                   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

## Key Points

### ✅ What You Need to Do
1. Export from Kobo
2. Add deprecatedID column
3. Generate new UUIDs
4. Make edits
5. Submit

### ✅ What Happens Automatically
1. First sheet detected as main data
2. All Kobo metadata filtered out
3. deprecatedID added to XML <meta>
4. Only form data included in submission
5. Kobo updates existing record (no duplicate)

### ❌ What You DON'T Need to Do
- ❌ Rename sheets to "data"
- ❌ Delete metadata columns
- ❌ Clean up the export
- ❌ Manually create XML
- ❌ Worry about XML structure

## Common Scenarios

### Scenario 1: Fix Wrong Sector (Bulk)
```
Export → Add deprecatedID → Change sector column → Submit
Result: All sectors updated, no duplicates
```

### Scenario 2: Update Organization Names
```
Export → Add deprecatedID → Change org names → Submit
Result: Org names updated, data preserved
```

### Scenario 3: Correct Date Entries
```
Export → Add deprecatedID → Fix dates → Submit
Result: Dates corrected, everything else unchanged
```

## Troubleshooting

### Problem: Duplicates Created Instead of Updates
```
Check: Does deprecatedID column exist?
Check: Are deprecatedID values correct original UUIDs?
Check: Did you generate NEW _submission__uuid values?
```

### Problem: Changes Not Showing
```
Check: Did you edit the right fields?
Check: Did you submit with --dry-run (test mode)?
Check: Review the generated XML in xml_output/
```

### Problem: Some Metadata in XML
```
This shouldn't happen - if it does, report as bug
The filter should catch all _* columns
```

## Need Help?

- See `docs/EDITING_SUBMISSIONS.md` for detailed guide
- See `CHANGELOG_KOBO_EXPORT.md` for technical details
- Run with `--dry-run` to test safely
