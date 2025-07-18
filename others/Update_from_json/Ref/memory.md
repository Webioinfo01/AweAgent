# Project Data Synchronization Memory

## Overview

This project provides a set of Python scripts to synchronize project data stored in JSON files with two main output formats:

- **README.md**: Markdown tables summarizing project categories and entries
- **index.html**: JavaScript projectData variable and statistics for a web interface

## Components

### Scripts

- `add_record_interactive.py`: Interactive CLI tool to add new project records to a JSON file. Supports selecting category and entering fields with validation and auto-generation of GitHub stars badge URLs.
- `update_readme.py`: Reads JSON data and updates markdown tables in README.md accordingly.
- `update_html.py`: Reads JSON data and updates the JavaScript projectData variable and statistics in index.html.
- `update_all.py`: Convenience script to run both README and HTML update scripts in one command.
- `utils.py`: Shared utility functions for loading JSON, creating backups, comparing data, escaping text, and validating file permissions.

## Data Structure

- JSON data is organized by categories: `ai-agents`, `foundation-models`, `ai-tools`, `databases`, `benchmarks`, `reviews`.
- Each category contains a list of project entries.
- Each project entry is a dictionary with fields:
  - `year` (required)
  - `title` (required)
  - `team`
  - `team website`
  - `affiliation`
  - `domain`
  - `venue`
  - `paperUrl`
  - `codeUrl`
  - `githubStars`

## Features

- Automatic backup creation before file updates.
- Change detection to avoid unnecessary file writes.
- GitHub stars badge support with auto-generation from repo URLs.
- Consistent table column structure across categories.
- Interactive record addition with input validation.
- Automatic statistics update in HTML (counts, charts, nav tabs).

## Usage

- Use `add_record_interactive.py` to add new records interactively to any JSON file.
- Use `update_readme.py` to update README.md tables from JSON.
- Use `update_html.py` to update index.html projectData and stats from JSON.
- Use `update_all.py` to run both README and HTML updates together.

## Integration

- Suitable for CI/CD pipelines, git hooks, scheduled tasks, and manual workflows.
- Designed for extensibility and easy maintenance.

## Notes

- JSON validation ensures required fields are present and non-empty.
- Scripts handle escaping for markdown and JavaScript contexts.
- Backup files include timestamps for easy recovery.
- The project uses standard Python 3 libraries with no external dependencies.

This memory file provides a quick summary for any AI or developer to understand the project structure, purpose, and usage. 