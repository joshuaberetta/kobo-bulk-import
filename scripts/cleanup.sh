#!/bin/bash
# Cleanup script to remove test files, duplicates, and redundant documentation
# Created: 2025-11-15

echo "🧹 Starting cleanup..."
echo ""

# Count files before
BEFORE=$(find . -type f | wc -l)

# Remove test output folders
echo "Removing test output folders..."
rm -rf test_auto_mapping/
rm -rf test_output/
rm -rf test_xml/
rm -rf test_xpath_mapping/
rm -rf xml_output/

# Remove test files
echo "Removing test files..."
rm -f test_output_generic.xlsx
rm -f test-mapping.json
rm -f test-mapping-xpath.json
rm -f aiBgJcvz5AFHB54fKpG2y5.json

# Remove redundant documentation
echo "Removing redundant documentation..."
rm -f START_HERE.txt
rm -f USAGE.txt
rm -f WORKFLOW.txt
rm -f QUICK_REFERENCE.txt
rm -f API_NOTES.txt

# Remove duplicate data file (keep the one without timestamp)
echo "Removing duplicate data files..."
rm -f data/MercyChef-Jamaica_Melissa_5W_OfflineForm_20251115_kobo_import_20251115.xlsx

# Remove example scripts (optional - comment out if you want to keep them)
echo "Removing example scripts..."
rm -f examples.py
rm -f complete_example.py
rm -f end_to_end_example.py
rm -f simple_submit.py

# Remove Python cache
echo "Removing Python cache..."
rm -rf __pycache__/

# Count files after
AFTER=$(find . -type f | wc -l)
REMOVED=$((BEFORE - AFTER))

echo ""
echo "✅ Cleanup complete!"
echo "📊 Files before: $BEFORE"
echo "📊 Files after: $AFTER"
echo "🗑️  Files removed: $REMOVED"
echo ""
echo "Kept files:"
echo "  ✓ Core scripts: transform_to_kobo.py, submit_to_kobo.py, excel_to_kobo_xml.py, generate_mapping.py"
echo "  ✓ Config files: config.json, config.example.json, question-mapping.json, content.json"
echo "  ✓ Documentation: README.md, CONFIG.md, MAPPING_GENERATOR.md, QUICKSTART.md, TRANSFORM_MERCYCHEF_README.md"
echo "  ✓ Data: raw-data/ and data/ folders"
echo "  ✓ Dependencies: requirements.txt, .gitignore, venv/"
