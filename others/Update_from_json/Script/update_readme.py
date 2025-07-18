#!/usr/bin/env python3
"""
Update README.md with project data from JSON file.

This script reads project data from a JSON file and updates the corresponding
markdown tables in the README.md file. It preserves the existing structure
and only updates the table content.
"""

import argparse
import os
import re
import sys
from typing import Dict, List, Optional

# Add the Script directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from utils import (
    load_project_data,
    create_backup,
    compare_project_data,
    escape_markdown,
    format_links_for_markdown,
    get_category_display_name,
    get_category_columns,
    validate_file_permissions
)


def parse_readme_tables(readme_path: str) -> Dict[str, List[Dict]]:
    """
    Extract existing project data from README tables.
    
    Args:
        readme_path (str): Path to README file
        
    Returns:
        Dict[str, List[Dict]]: Extracted project data by category
    """
    if not os.path.exists(readme_path):
        return {}
    
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading README file: {e}")
        return {}
    
    project_data = {}
    
    # Find sections with tables
    # Look for patterns like "## AI Agents" followed by a table
    section_pattern = r'## ([^#\n]+)\n(.*?)(?=\n## |\n# |\Z)'
    sections = re.findall(section_pattern, content, re.DOTALL)
    
    for section_title, section_content in sections:
        section_title = section_title.strip()
        
        # Skip sections that don't contain tables
        if '|' not in section_content:
            continue
        
        # Extract table data
        lines = section_content.strip().split('\n')
        table_lines = [line for line in lines if line.strip().startswith('|')]
        
        if len(table_lines) < 3:  # Header, separator, at least one data row
            continue
        
        # Parse header and data rows
        header_line = table_lines[0]
        data_lines = table_lines[2:]  # Skip separator line
        
        # Extract column names
        columns = [col.strip() for col in header_line.split('|')[1:-1]]
        
        # Extract project data
        projects = []
        for line in data_lines:
            cells = [cell.strip() for cell in line.split('|')[1:-1]]
            if len(cells) >= len(columns):
                project = {}
                for i, col in enumerate(columns):
                    if i < len(cells):
                        project[col.lower().replace(' ', '_').replace('/', '_')] = cells[i]
                projects.append(project)
        
        # Map section title to category key
        section_lower = section_title.lower()
        if 'ai agents' in section_lower:
            category_key = 'ai-agents'
        elif 'foundation models' in section_lower or 'foundation-models' in section_lower:
            category_key = 'foundation-models'
        elif 'ai tools' in section_lower:
            category_key = 'ai-tools'
        elif 'databases' in section_lower or 'simulation' in section_lower:
            category_key = 'databases'
        elif 'benchmarks' in section_lower:
            category_key = 'benchmarks'
        elif 'reviews' in section_lower:
            category_key = 'reviews'
        else:
            # Fallback: convert to kebab-case
            category_key = section_lower.replace(' ', '-').replace('/', '')
        
        project_data[category_key] = projects
    
    return project_data


def generate_markdown_table(projects: List[Dict], category: str) -> str:
    """
    Generate markdown table for a project category.
    
    Args:
        projects (List[Dict]): List of project entries
        category (str): Category key
        
    Returns:
        str: Generated markdown table
    """
    if not projects:
        return ""
    
    columns = get_category_columns(category)
    
    # Generate header
    header = "| " + " | ".join(columns) + " |"
    separator = "|" + "|".join([" " + "-" * (len(col) + 1) for col in columns]) + "|"
    
    # Generate data rows
    rows = []
    for project in projects:
        row_data = []
        
        for col in columns:
            if col == "Year":
                row_data.append(escape_markdown(project.get('year', '')))
            elif col == "Title":
                title = escape_markdown(project.get('title', ''))
                row_data.append(f"**{title}**" if title else "")
            elif col == "Team":
                team = escape_markdown(project.get('team', ''))
                row_data.append(team)
            elif col == "Team Website":
                team_website = project.get('team website', '')
                if team_website:
                    row_data.append(f"[Link]({team_website})")
                else:
                    row_data.append("")
            elif col == "Affiliation":
                affiliation = escape_markdown(project.get('affiliation', ''))
                row_data.append(affiliation)
            elif col == "Domain":
                domain = escape_markdown(project.get('domain', ''))
                row_data.append(domain)
            elif col == "Venue":
                venue = escape_markdown(project.get('venue', ''))
                row_data.append(venue)
            elif col == "Paper/ Source":
                paper_url = project.get('paperUrl', '')
                if paper_url:
                    row_data.append(f"[Link]({paper_url})")
                else:
                    row_data.append("")
            elif col == "Code/Product":
                code_url = project.get('codeUrl', '')
                github_stars = project.get('githubStars', '')
                if code_url:
                    link_text = f"[Link]({code_url})"
                    if github_stars:
                        # Handle both full URLs and repo paths
                        if github_stars.startswith('http'):
                            link_text += f" ![GitHub Stars]({github_stars})"
                        else:
                            link_text += f" ![GitHub Stars](https://img.shields.io/github/stars/{github_stars})"
                    row_data.append(link_text)
                else:
                    row_data.append("")

        
        row = "| " + " | ".join(row_data) + " |"
        rows.append(row)
    
    return "\n".join([header, separator] + rows)


def update_readme_file(readme_path: str, new_tables: Dict[str, str]) -> bool:
    """
    Update README file with new table content.
    
    Args:
        readme_path (str): Path to README file
        new_tables (Dict[str, str]): New table content by category
        
    Returns:
        bool: True if file was updated successfully
    """
    try:
        with open(readme_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading README file: {e}")
        return False
    
    # Update each section
    for category, table_content in new_tables.items():
        if not table_content:
            continue
        
        section_name = get_category_display_name(category)
        
        # Find the section and replace table content
        # Pattern: ## Section Name followed by table content until next section
        section_pattern = f'(## {re.escape(section_name)}\\s*\\n)(.*?)(?=\\n## |\\n# |\\Z)'
        
        def replace_section(match):
            section_header = match.group(1)
            
            # Keep any text before the table (like intro text)
            existing_content = match.group(2)
            lines = existing_content.split('\n')
            
            # Find where table starts (first line with |)
            table_start = 0
            for i, line in enumerate(lines):
                if line.strip().startswith('|'):
                    table_start = i
                    break
            
            # Keep content before table
            before_table = '\n'.join(lines[:table_start]).rstrip()
            if before_table:
                before_table += '\n\n'
            
            return section_header + before_table + table_content + '\n'
        
        content = re.sub(section_pattern, replace_section, content, flags=re.DOTALL)
    
    # Write updated content
    try:
        with open(readme_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing README file: {e}")
        return False


def main():
    """Main function to orchestrate README update process."""
    parser = argparse.ArgumentParser(description='Update README.md with project data from JSON')
    parser.add_argument('--json-path', default='Input/test.json',
                       help='Path to JSON file with project data')
    parser.add_argument('--readme-path', default='readme.md',
                       help='Path to README.md file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup before updating')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if no changes detected')
    
    args = parser.parse_args()
    
    print("=== README Update Script ===")
    print(f"JSON source: {args.json_path}")
    print(f"README target: {args.readme_path}")
    
    # Validate input files
    if not os.path.exists(args.json_path):
        print(f"Error: JSON file not found: {args.json_path}")
        return 1
    
    if not os.path.exists(args.readme_path):
        print(f"Error: README file not found: {args.readme_path}")
        return 1
    
    if not validate_file_permissions(args.readme_path):
        print(f"Error: Cannot write to README file: {args.readme_path}")
        return 1
    
    try:
        # Load project data from JSON
        print("Loading project data from JSON...")
        source_data = load_project_data(args.json_path)
        print(f"Loaded {len(source_data)} categories")
        
        # Parse existing README tables
        print("Parsing existing README tables...")
        target_data = parse_readme_tables(args.readme_path)
        print(f"Found {len(target_data)} existing categories")
        
        # Compare data
        differences = compare_project_data(source_data, target_data)
        
        if differences['changes_count'] == 0 and not args.force:
            print("No changes detected. README is up to date.")
            return 0
        
        print(f"Changes detected: {differences['changes_count']}")
        if differences['added_categories']:
            print(f"  Added categories: {differences['added_categories']}")
        if differences['removed_categories']:
            print(f"  Removed categories: {differences['removed_categories']}")
        if differences['modified_categories']:
            print(f"  Modified categories: {differences['modified_categories']}")
        
        # Create backup
        if not args.no_backup:
            create_backup(args.readme_path)
        
        # Generate new tables
        print("Generating markdown tables...")
        new_tables = {}
        for category, projects in source_data.items():
            table_content = generate_markdown_table(projects, category)
            if table_content:
                new_tables[category] = table_content
                print(f"  Generated table for {category}: {len(projects)} projects")
        
        # Update README file
        print("Updating README file...")
        if update_readme_file(args.readme_path, new_tables):
            print("✓ README updated successfully!")
            return 0
        else:
            print("✗ Failed to update README file")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 