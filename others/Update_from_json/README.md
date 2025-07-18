# Project Data Synchronization Scripts

This directory contains Python scripts to automatically synchronize project data from JSON files to README.md markdown tables and HTML JavaScript objects.

## Overview

The system consists of four main components:

1. **`utils.py`** - Shared utility functions for all scripts
2. **`update_readme.py`** - Updates README.md markdown tables from JSON
3. **`update_html.py`** - Updates HTML JavaScript projectData variable from JSON
4. **`update_all.py`** - Convenience script to run both updates

## JSON Data Structure

The scripts expect JSON data with the following structure:

```json
{
  "databases": [
    {
      "year": "2025.08",
      "title": "Project Title",
      "team": "Team Name",
      "team website": "https://github.com/team",
      "affiliation": "University/Institution",
      "domain": "Research Domain",
      "venue": "Publication Venue",
      "paperUrl": "https://link-to-paper.com",
      "codeUrl": "https://github.com/repo",
      "githubStars": "https://img.shields.io/github/stars/owner/repo"
    }
  ],
  "ai-agents": [...],
  "foundation-models": [...],
  "ai-tools": [...],
  "benchmarks": [...],
  "reviews": [...]
}
```

### Required Fields
- `year` - Publication/release year
- `title` - Project title

### Optional Fields
- `team` - Team or author name
- `team website` - Team's website URL
- `affiliation` - Institution/organization
- `domain` - Research domain/area
- `venue` - Publication venue
- `paperUrl` - Link to paper/publication
- `codeUrl` - Link to code repository
- `githubStars` - GitHub stars badge URL (supports both full URLs and repo paths)

## Table Column Structure

All categories now use the same comprehensive column structure:

`Year | Title | Team | Team Website | Affiliation | Domain | Venue | Paper/ Source | Code/Product`

This provides consistent formatting across all project categories and includes all available project information fields.

## Usage

### 1. Add Records Interactively

```bash
# Add new project records interactively to a JSON file
python Script/add_record_interactive.py --json-path Input/test.json
```

### 2. Update README Only

```bash
# Basic usage
python Script/update_readme.py

# With custom paths
python Script/update_readme.py --json-path Input/data.json --readme-path readme.md

# Force update without change detection
python Script/update_readme.py --force

# Skip backup creation
python Script/update_readme.py --no-backup
```

### 3. Update HTML Only

```bash
# Basic usage (automatically updates statistics)
python Script/update_html.py

# With custom paths
python Script/update_html.py --json-path Input/data.json --html-path docs/index.html

# Force update
python Script/update_html.py --force
```

### 4. Update Both (Recommended)

```bash
# Update both README and HTML (HTML stats auto-updated)
python Script/update_all.py

# Update only README
python Script/update_all.py --readme-only

# Update only HTML
python Script/update_all.py --html-only

# Force update both
python Script/update_all.py --force
```

```bash
# Validate scripts work with your JSON structure
python Script/test_scripts.py
```

## Command Line Options

### Common Options
- `--json-path PATH` - Path to JSON source file (default: `Input/test.json`)
- `--force` - Force update even if no changes detected
- `--no-backup` - Skip creating backup files

### README Specific
- `--readme-path PATH` - Path to README file (default: `readme.md`)

### HTML Specific
- `--html-path PATH` - Path to HTML file (default: `docs/index.html`)
- Statistics are automatically updated (stats bar, nav tabs, charts, section counts)

### Combined Script
- `--readme-only` - Update only README file
- `--html-only` - Update only HTML file

## Features

### Automatic Backup
- Creates timestamped backup files before modifications
- Format: `filename.YYYYMMDD_HHMMSS.bak`
- Can be disabled with `--no-backup`

### Change Detection
- Compares source and target data to detect differences
- Only updates files when changes are found
- Can be overridden with `--force`

### GitHub Stars Support
- Supports both full shield URLs and repo paths
- Full URL: `https://img.shields.io/github/stars/owner/repo`
- Repo path: `owner/repo` (automatically converted)

### Error Handling
- Validates JSON structure and required fields
- Checks file permissions before modification
- Provides detailed error messages and recovery suggestions

### Link Formatting
- Automatically formats paper and code links for markdown
- Handles empty URLs gracefully
- Supports GitHub stars badges

## File Structure

```
README.md           # This documentation
Script/
├── utils.py           # Shared utility functions
├── update_readme.py   # README update script
├── update_html.py     # HTML update script
├── update_all.py      # Combined update script
├── test_scripts.py    # Test validation script
└── add_record_interactive.py # Add Records Interactively to json
```

## Examples

### Example 1: Regular Update
```bash
# Update both README and HTML with the default test.json (HTML stats auto-updated)
python Script/update_all.py
```

### Example 2: Custom Paths
```bash
# Use custom JSON file and paths
python Script/update_all.py \
  --json-path data/projects.json \
  --readme-path docs/README.md \
  --html-path website/index.html
```

### Example 3: Development Workflow
```bash
# Test first
python Script/test_scripts.py

# Update if tests pass
python Script/update_all.py --force
```

## Troubleshooting

### JSON Validation Errors
- Check that `year` and `title` fields are present and non-empty
- Ensure JSON syntax is valid
- Verify category structure matches expected format

### File Permission Errors
- Check write permissions on target files
- Ensure directories exist
- Try running with elevated privileges if needed

### Backup Issues
- Check disk space for backup files
- Verify write permissions in target directories
- Use `--no-backup` to skip backup creation

### GitHub Stars Issues
- For full URLs, use format: `https://img.shields.io/github/stars/owner/repo`
- For repo paths, use format: `owner/repo`
- Leave empty if no GitHub repository

## Integration

These scripts can be integrated into:
- **CI/CD pipelines** for automatic updates
- **Git hooks** for pre-commit validation
- **Scheduled tasks** for periodic synchronization
- **Development workflows** for manual updates

## Dependencies

- Python 3.6+
- Standard library only (no external dependencies) 