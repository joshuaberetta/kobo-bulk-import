# Configuration File

This directory contains a `config.example.json` file that shows all available configuration options for `submit_to_kobo.py`.

## Usage

1. **Copy the example config:**
   ```bash
   cp config.example.json config.json
   ```

2. **Edit your config.json with your values:**
   - Set your API token
   - Update paths to your Excel and mapping files
   - Configure form ID and other options

3. **Run with config file:**
   ```bash
   # Use config file for all settings
   python submit_to_kobo.py --config config.json
   
   # Override specific settings from command line
   python submit_to_kobo.py --config config.json --uuid b12be739-107b-49d7-914e-b177ac7ec5d0
   
   # Command-line args always take precedence
   python submit_to_kobo.py --config config.json --dry-run false
   ```

## Config Options

All command-line flags can be set in the config file:

```json
{
  "excel": "data/your-data.xlsx",
  "mapping": "your-mapping.json",
  "form-id": "your-form-id",
  "token": "your-api-token",
  "server": "https://kc.kobotoolbox.org",
  "formhub-uuid": null,
  "version-id": "vdjkkW3B5b9mKHZVoDPYbA",
  "form-version": null,
  "use-labels": true,
  "dry-run": true,
  "output-dir": "./xml_output",
  "stop-on-error": false,
  "uuid": null
}
```

## Notes

- **Required fields**: `excel`, `mapping`, `form-id`, `token`
- **Boolean flags**: Set to `true` or `false` (not as strings)
- **Optional fields**: Use `null` to leave unset
- **Command-line override**: Any CLI argument overrides the config file value
- **Security**: Add `config.json` to `.gitignore` to keep your API token private

## Priority Order

Arguments are resolved in this order (highest priority first):
1. Command-line arguments
2. Config file values
3. Default values

Example:
```bash
# config.json has "dry-run": true
# But CLI overrides it:
python submit_to_kobo.py --config config.json --dry-run false
# Result: Will actually submit (not dry-run)
```
