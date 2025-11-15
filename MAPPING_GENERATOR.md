# Automatic Mapping Generation

This document explains how to automatically generate mapping files from KoboToolbox survey definitions.

## Overview

The `generate_mapping.py` script automatically creates:
1. **Field path mappings**: Maps Excel column names to their hierarchical XML paths
2. **Choice label mappings**: Maps choice labels (like "National NGO") to their internal names (like "NATIONAL_NGO")

This eliminates the need to manually create mapping files.

## Quick Start

```bash
# Generate mapping from content.json
python generate_mapping.py content.json output-mapping.json
```

### Getting content.json

### Option 1: Use the API (Recommended)

```bash
# Replace {form_id} with your actual form ID
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://kf.kobotoolbox.org/api/v2/assets/{form_id}/?format=json" \
  > content.json
```

The API response includes:
- `survey`: Array of question definitions with `$xpath` for each field
- `choices`: Array of choice options with labels and names

## Generated Mapping Structure

The script generates an enhanced mapping format:

```json
{
  "fields": {
    "start": "start",
    "today": "today",
    "LeadOrganization_type": "org_details/ORAGANIZATION_LEAD/LeadOrganization_type",
    "email": "org_details/FOCAL_POINTS/email",
    "parish": "RESPONSES/FIGURES_COMMUNITY/parish"
  },
  "choices": {
    "LeadOrganization_type": {
      "National NGO": "NATIONAL_NGO",
      "International NGO": "INTERNATIONAL_NGO",
      "UN Agency": "UN_AGENCY",
      "Government": "GOVERNMENT",
      "Red Cross/Red Crescent Movement": "RED_CROSS_MOVEMENT",
      "Private Sector": "PRIVATE_SECTOR",
      "Academia/Research": "ACADEMIA_RESEARCH",
      "Other": "OTHER"
    },
    "same_as_lead": {
      "Yes": "yes",
      "No": "no"
    }
  }
}
```

## How It Works

### Field Path Mapping

The script extracts paths directly from KoboToolbox's survey structure:

1. **Reads `$xpath` field**: Each survey item in `content.json` has a pre-calculated `$xpath` value
2. **Maps name to xpath**: Creates a mapping from the question `name` to its `$xpath`
3. **No parsing needed**: KoboToolbox already provides the correct hierarchical paths

Example from `content.json`:
```json
{
  "name": "LeadOrganization_type",
  "$xpath": "org_details/ORAGANIZATION_LEAD/LeadOrganization_type",
  "type": "select_one",
  "select_from_list_name": "org_types"
}
```

→ Mapping: `"LeadOrganization_type": "org_details/ORAGANIZATION_LEAD/LeadOrganization_type"`

### Choice Mapping

The script:

1. **Organizes choices by list**: Groups all choices by their `list_name`
2. **Finds select questions**: Identifies all `select_one` and `select_multiple` questions
3. **Links choices to questions**: Matches each question with its choice list
4. **Creates label→name mappings**: For each choice, maps the display label to the internal name

This enables the `--use-labels` feature to convert human-readable labels back to database values.

## Using the Generated Mapping

### With label conversion (when Excel has labels)

```bash
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping auto-generated-mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_TOKEN \
    --use-labels
```

### Without label conversion (when Excel has internal names)

```bash
python submit_to_kobo.py \
    --excel data.xlsx \
    --mapping auto-generated-mapping.json \
    --form-id YOUR_FORM_ID \
    --token YOUR_TOKEN
```

## Troubleshooting

### "No choices found for field X"

This happens when:
- Your Excel contains choice labels (like "National NGO")
- But the field is not in the `choices` section of the mapping
- You're using `--use-labels`

**Solutions:**
1. Regenerate the mapping from a complete content.json
2. Don't use `--use-labels` if your Excel has internal names
3. Manually add the choice mapping to your JSON file

### "Path not found in mapping"

This means a column in your Excel doesn't have a corresponding entry in the mapping.

**Solutions:**
1. Check for typos in column names
2. Regenerate mapping from latest content.json
3. Manually add the missing field to the mapping

### Incorrect hierarchical paths

If the generated paths don't match your expected structure:

1. **Check content.json structure**: Verify that `begin_group`/`end_group` pairs are balanced
2. **Look for naming mismatches**: Ensure group names match between Excel and content.json
3. **Compare with manual mapping**: If you have a working manual mapping, compare the paths

## Advanced: Customizing the Script

You can modify `generate_mapping.py` to:

### Skip certain fields

```python
def build_field_paths(survey_items):
    # ... existing code ...
    
    # Skip fields you don't want
    SKIP_FIELDS = ['calc_field', 'hidden_value']
    
    if item_name in SKIP_FIELDS:
        continue
    
    # ... rest of code ...
```

### Add custom transformations

```python
def build_choice_mappings(survey_items, choices):
    # ... existing code ...
    
    # Custom label transformation
    if choice_label:
        # Convert to lowercase for case-insensitive matching
        choice_label = choice_label.lower()
        choices_by_list[list_name][choice_label] = choice_name
```

## Examples

### Example 1: Simple form

```bash
# content.json contains simple flat form
python generate_mapping.py content.json simple-mapping.json
```

### Example 2: Form with nested groups

```bash
# content.json contains groups within groups
python generate_mapping.py content.json nested-mapping.json
```

### Example 3: Form with repeat groups

```bash
# content.json contains repeat groups like FOCAL_POINTS
python generate_mapping.py content.json repeat-mapping.json
```

The script handles all these cases automatically!

## Comparison with Manual Mapping

| Feature | Auto-Generated | Manual |
|---------|----------------|--------|
| Speed | ⚡ Instant | ⏱️ Slow (manual work) |
| Accuracy | ✅ Perfect for structure | ⚠️ Error-prone |
| Choice mappings | ✅ Automatic | ❌ Must create manually |
| Maintenance | ✅ Re-run when form changes | ❌ Must update manually |
| Customization | ⚠️ Limited | ✅ Full control |

**Recommendation**: Use auto-generation for initial setup and routine updates. Use manual mapping only when you need special customizations.

## Integration with Workflow

Typical workflow:

```bash
# 1. Get your form definition
curl -H "Authorization: Token YOUR_TOKEN" \
  "https://kf.kobotoolbox.org/api/v2/assets/FORM_ID/?format=json" \
  > content.json

# 2. Generate mapping
python generate_mapping.py content.json mapping.json

# 3. Export data from KoboToolbox to Excel

# 4. Convert and submit
python submit_to_kobo.py \
  --excel data.xlsx \
  --mapping mapping.json \
  --form-id FORM_ID \
  --token YOUR_TOKEN \
  --use-labels
```

When your form changes:
- Just re-run steps 1-2 to update the mapping
- No need to manually track changes
