# Parish Pcode Backfill Script

## Overview

The `backfill_parish_pcodes.py` script automatically fills in missing parish data in Excel files by looking up community names in the ODPEM GeoJSON reference data.

## Problem it Solves

Sometimes Excel data has community names but missing parish values. This script:
1. Reads the community name from each row
2. Looks it up in the `reference/odpem.geojson` file
3. Fills in the corresponding parish name based on the GeoJSON mapping

## Usage

### Basic Usage

Backfill and save to a new file:
```bash
python scripts/backfill_parish_pcodes.py raw-data/20251116-one-love.xlsx raw-data/20251116-one-love-filled.xlsx
```

Backfill and overwrite the original file:
```bash
python scripts/backfill_parish_pcodes.py raw-data/20251116-one-love.xlsx
```

### As a Python Module

You can also use it programmatically:

```python
from scripts.backfill_parish_pcodes import backfill_parish_pcodes

# Test what would be changed (dry-run)
df = backfill_parish_pcodes(
    'raw-data/20251116-one-love.xlsx',
    dry_run=True
)

# Actually backfill and save
df = backfill_parish_pcodes(
    'raw-data/20251116-one-love.xlsx',
    'raw-data/20251116-one-love-filled.xlsx',
    dry_run=False
)
```

## How It Works

1. **Loads GeoJSON Mapping**: Reads `reference/odpem.geojson` and creates a mapping of community names to parish information
2. **Identifies Missing Data**: Finds rows where `community` column has data but `parish` column is empty
3. **Fuzzy Matching**: Uses both exact and fuzzy matching (85% similarity threshold) to find community names
4. **Backfills Data**: Populates the parish column with the parish name from the GeoJSON

## Output

The script provides detailed output:
- Number of rows that need backfilling
- Success/failure count for each backfill attempt
- List of community names that couldn't be found in the GeoJSON
- Summary statistics

Example output:
```
Loading GeoJSON mapping from reference/odpem.geojson...
Loaded 729 community-to-parish mappings

Loading Excel file from raw-data/20251116-one-love.xlsx...
Loaded 319 rows

Found 83 rows with community but no parish

Backfill Summary:
  Successfully backfilled: 5
  Not found in GeoJSON: 78

Communities not found in GeoJSON:
  - Amity Hall (Location not plotted on Map
  - Frenchman
  - Montego Bay
  ...
```

## Limitations

- Only backfills rows where community exists but parish is missing
- Community names must match (or closely match) names in the GeoJSON
- Non-standard community names or typos may not be found
- The script fills in parish names, not pcodes (the column is named "parish" not "parish_pcode")

## Dependencies

- pandas
- openpyxl (for Excel file handling)

Install with:
```bash
pip install pandas openpyxl
```
