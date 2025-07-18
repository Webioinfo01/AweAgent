# Design Document

## Overview

The project data synchronization system consists of two independent Python scripts:
1. `update_readme.py` - Synchronizes JSON data with README.md markdown tables
2. `update_html.py` - Synchronizes JSON data with index.html JavaScript projectData variable

Both scripts follow a similar pattern: read source JSON, parse target file, compare data, and update if differences are found.

## Architecture

```
Input/data.json
    ↓
[Script Logic]
    ↓
readme.md / docs/index.html
```

### Script Architecture Pattern
1. **Data Loading**: Read and parse JSON source data
2. **Target Parsing**: Extract existing data from target file
3. **Comparison**: Detect differences between source and target
4. **Generation**: Create updated content in target format
5. **File Update**: Write changes back to target file

## Components and Interfaces

### 1. JSON Data Loader
**Purpose**: Read and validate the source JSON file
**Interface**:
```python
def load_project_data(json_path: str) -> dict:
    """Load and validate project data from JSON file"""
    pass
```

### 2. README Markdown Processor
**Purpose**: Parse and generate markdown table content
**Interface**:
```python
def parse_readme_tables(readme_path: str) -> dict:
    """Extract existing project data from README tables"""
    pass

def generate_markdown_table(projects: list, category: str) -> str:
    """Generate markdown table for a project category"""
    pass

def update_readme_file(readme_path: str, new_tables: dict) -> None:
    """Update README file with new table content"""
    pass
```

### 3. HTML JavaScript Processor
**Purpose**: Parse and generate JavaScript object content
**Interface**:
```python
def parse_html_project_data(html_path: str) -> dict:
    """Extract projectData variable from HTML file"""
    pass

def generate_js_object(project_data: dict) -> str:
    """Generate JavaScript object string"""
    pass

def update_html_file(html_path: str, new_js_data: str) -> None:
    """Update HTML file with new projectData variable"""
    pass
```

### 4. Data Comparison Utility
**Purpose**: Compare source and target data structures
**Interface**:
```python
def compare_project_data(source: dict, target: dict) -> dict:
    """Compare project data and return differences"""
    pass
```

## Data Models

### Project Entry Structure
```python
{
    "year": "2025.06",
    "title": "Project Title",
    "team": "Team Name",
    "team website": "https://...",
    "affiliation", "The affiliation for corresponding author",
    "domain": "Research Domain",
    "venue": "Publication Venue",
    "paperUrl": "https://...",
    "codeUrl": "https://...",
    "githubStars": "https://..."
}
```

### Category Mapping
```python
CATEGORIES = {
    "ai-agents": {
        "display_name": "AI Agents",
        "columns": ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper URL", "Code URL", "GitHub Stars"]
    },
    "foundation-models": {
        "display_name": "Foundation Models", 
        "columns": ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper URL", "Code URL", "GitHub Stars"]
    },
    "ai-tools": {
        "display_name": "AI Tools",
        "columns": ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper URL", "Code URL", "GitHub Stars"]
    },
    "databases": {
        "display_name": "Databases/Simulation",
        "columns": ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper URL", "Code URL", "GitHub Stars"]
    },
    "benchmarks": {
        "display_name": "Benchmarks",
        "columns": ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper URL", "Code URL", "GitHub Stars"]
    },
    "reviews": {
        "display_name": "Reviews",
        "columns": ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper URL", "Code URL", "GitHub Stars"]
    }
}
```

## Error Handling

### JSON Validation
- Validate JSON syntax and structure
- Check for required fields in project entries
- Handle missing or malformed data gracefully

### File Operations
- Check file existence and permissions
- Create backups before modifications
- Handle file I/O errors with informative messages

### Data Integrity
- Validate URLs format
- Handle special characters in markdown and JavaScript
- Ensure proper escaping for different output formats

## Testing Strategy

### Unit Tests
- Test JSON loading and validation
- Test markdown table generation
- Test JavaScript object generation
- Test data comparison logic

### Integration Tests
- Test complete README update workflow
- Test complete HTML update workflow
- Test with various project data scenarios

### Edge Case Testing
- Empty JSON data
- Malformed project entries
- Special characters in titles/descriptions
- Missing URLs or empty fields

## Implementation Details

### README Markdown Generation
- Use proper markdown table syntax with alignment
- Generate GitHub Stars badges: `![GitHub Stars](https://img.shields.io/github/stars/repo)`
- Create proper link formatting: `[Link](url)`
- Handle empty URLs by showing empty cells

### HTML JavaScript Generation
- Properly escape quotes and special characters
- Maintain proper JSON formatting within JavaScript
- Preserve existing HTML structure around projectData variable
- Use regex patterns to locate and replace projectData assignment

### File Backup Strategy
- Create `.bak` files before modifications
- Include timestamp in backup filename
- Provide option to restore from backup

## Configuration

### Script Parameters
```python
# Default file paths
DEFAULT_JSON_PATH = "Input/data.json"
DEFAULT_README_PATH = "readme.md" 
DEFAULT_HTML_PATH = "docs/index.html"

# Backup settings
CREATE_BACKUPS = True
BACKUP_SUFFIX = ".bak"
```

### Command Line Interface
```bash
# README update script
python update_readme.py [--json-path PATH] [--readme-path PATH] [--no-backup]

# HTML update script  
python update_html.py [--json-path PATH] [--html-path PATH] [--no-backup]
```