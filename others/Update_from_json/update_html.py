#!/usr/bin/env python3
"""
Update index.html with project data from JSON file.

This script reads project data from a JSON file and updates the JavaScript
projectData variable in the HTML file. It preserves the existing HTML structure
and only updates the data content.
"""

import argparse
import json
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
    escape_javascript,
    validate_file_permissions
)


def parse_html_project_data(html_path: str) -> Dict[str, List[Dict]]:
    """
    Extract projectData variable from HTML file.
    
    Args:
        html_path (str): Path to HTML file
        
    Returns:
        Dict[str, List[Dict]]: Extracted project data
    """
    if not os.path.exists(html_path):
        return {}
    
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return {}
    
    # Find projectData variable assignment
    # Look for: const projectData = { ... };
    pattern = r'const\s+projectData\s*=\s*(\{.*?\});'
    match = re.search(pattern, content, re.DOTALL)
    
    if not match:
        print("Warning: projectData variable not found in HTML file")
        return {}
    
    js_object_str = match.group(1)
    
    try:
        # Convert JavaScript object to JSON by cleaning up the format
        # Remove trailing commas and fix quotes
        cleaned_str = re.sub(r',\s*}', '}', js_object_str)  # Remove trailing commas before }
        cleaned_str = re.sub(r',\s*]', ']', cleaned_str)    # Remove trailing commas before ]
        cleaned_str = re.sub(r'(\w+):', r'"\1":', cleaned_str)  # Quote property names
        
        # Parse as JSON
        data = json.loads(cleaned_str)
        return data
        
    except json.JSONDecodeError as e:
        print(f"Warning: Could not parse projectData as JSON: {e}")
        return {}


def generate_js_object(project_data: Dict) -> str:
    """
    Generate JavaScript object string from project data.
    
    Args:
        project_data (Dict): Project data dictionary
        
    Returns:
        str: Formatted JavaScript object string
    """
    def format_value(value):
        """Format a value for JavaScript object."""
        if isinstance(value, str):
            # Escape the string and wrap in quotes
            escaped = escape_javascript(value)
            return f'"{escaped}"'
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, bool):
            return 'true' if value else 'false'
        elif value is None:
            return 'null'
        else:
            return f'"{escape_javascript(str(value))}"'
    
    def format_object(obj, indent_level=0):
        """Format an object with proper indentation."""
        indent = "    " * indent_level
        next_indent = "    " * (indent_level + 1)
        
        if isinstance(obj, dict):
            if not obj:
                return "{}"
            
            lines = ["{"]
            items = list(obj.items())
            for i, (key, value) in enumerate(items):
                formatted_value = format_object(value, indent_level + 1)
                comma = "," if i < len(items) - 1 else ""
                lines.append(f'{next_indent}"{key}": {formatted_value}{comma}')
            lines.append(f"{indent}}}")
            return "\n".join(lines)
            
        elif isinstance(obj, list):
            if not obj:
                return "[]"
                
            lines = ["["]
            for i, item in enumerate(obj):
                formatted_item = format_object(item, indent_level + 1)
                comma = "," if i < len(obj) - 1 else ""
                lines.append(f"{next_indent}{formatted_item}{comma}")
            lines.append(f"{indent}]")
            return "\n".join(lines)
            
        else:
            return format_value(obj)
    
    return format_object(project_data, 1)


def update_html_file(html_path: str, new_js_data: str) -> bool:
    """
    Update HTML file with new projectData variable.
    
    Args:
        html_path (str): Path to HTML file
        new_js_data (str): New JavaScript object string
        
    Returns:
        bool: True if file was updated successfully
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading HTML file: {e}")
        return False
    
    # Find and replace projectData variable
    pattern = r'(const\s+projectData\s*=\s*)\{.*?\};'
    replacement = f'\\1{new_js_data};'
    
    updated_content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    if updated_content == content:
        print("Warning: projectData variable not found or not updated")
        return False
    
    # Write updated content
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(updated_content)
        return True
    except Exception as e:
        print(f"Error writing HTML file: {e}")
        return False


def update_html_stats(html_path: str, project_data: Dict) -> bool:
    """
    Update statistics in HTML file based on project data.
    
    Args:
        html_path (str): Path to HTML file
        project_data (Dict): Project data dictionary
        
    Returns:
        bool: True if stats were updated successfully
    """
    try:
        with open(html_path, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"Error reading HTML file for stats update: {e}")
        return False
    
    # Calculate statistics
    total_projects = sum(len(projects) for projects in project_data.values())
    ai_agents = len(project_data.get('ai-agents', []))
    foundation_models = len(project_data.get('foundation-models', []))
    ai_tools = len(project_data.get('ai-tools', []))
    databases = len(project_data.get('databases', []))
    benchmarks = len(project_data.get('benchmarks', []))
    reviews = len(project_data.get('reviews', []))
    
    # Update total projects count
    content = re.sub(
        r'(<div class="stat-number" id="total-count">)\d+(</div>)',
        f'\\1{total_projects}\\2',
        content
    )
    
    # Update navigation tab counts
    nav_replacements = [
        (r'(All Projects \()\d+(\))', f'\\1{total_projects}\\2'),
        (r'(AI Agents \()\d+(\))', f'\\1{ai_agents}\\2'),
        (r'(Foundation Models \()\d+(\))', f'\\1{foundation_models}\\2'),
        (r'(AI Tools \()\d+(\))', f'\\1{ai_tools}\\2'),
        (r'(Databases \()\d+(\))', f'\\1{databases}\\2'),
        (r'(Benchmarks \()\d+(\))', f'\\1{benchmarks}\\2'),
        (r'(Reviews \()\d+(\))', f'\\1{reviews}\\2'),
    ]
    
    for pattern, replacement in nav_replacements:
        content = re.sub(pattern, replacement, content)
    
    # Update chart data
    chart_data_pattern = r'(data:\s*\[)[^\]]+(\])'
    new_chart_data = f'\\1{ai_agents}, {foundation_models}, {ai_tools}, {databases}, {benchmarks}, {reviews}\\2'
    content = re.sub(chart_data_pattern, new_chart_data, content)
    
    # Update stats grid numbers
    stats_patterns = [
        (r'(<div class="stat-number">)23(</div>\s*<div class="stat-label">AI Agents</div>)', f'\\1{ai_agents}\\2'),
        (r'(<div class="stat-number">)45(</div>\s*<div class="stat-label">Foundation Models</div>)', f'\\1{foundation_models}\\2'),
        (r'(<div class="stat-number">)5(</div>\s*<div class="stat-label">AI Tools</div>)', f'\\1{ai_tools}\\2'),
        (r'(<div class="stat-number">)9(</div>\s*<div class="stat-label">Databases</div>)', f'\\1{databases}\\2'),
        (r'(<div class="stat-number">)4(</div>\s*<div class="stat-label">Benchmarks</div>)', f'\\1{benchmarks}\\2'),
        (r'(<div class="stat-number">)8(</div>\s*<div class="stat-label">Reviews</div>)', f'\\1{reviews}\\2'),
    ]
    
    for pattern, replacement in stats_patterns:
        content = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    # Write updated content
    try:
        with open(html_path, 'w', encoding='utf-8') as f:
            f.write(content)
        return True
    except Exception as e:
        print(f"Error writing HTML file for stats update: {e}")
        return False


def main():
    """Main function to orchestrate HTML update process."""
    parser = argparse.ArgumentParser(description='Update index.html with project data from JSON')
    parser.add_argument('--json-path', default='Input/test.json',
                       help='Path to JSON file with project data')
    parser.add_argument('--html-path', default='docs/index.html',
                       help='Path to index.html file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backup before updating')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if no changes detected')
    parser.add_argument('--update-stats', action='store_true',
                       help='Also update statistics in HTML')
    
    args = parser.parse_args()
    
    print("=== HTML Update Script ===")
    print(f"JSON source: {args.json_path}")
    print(f"HTML target: {args.html_path}")
    
    # Validate input files
    if not os.path.exists(args.json_path):
        print(f"Error: JSON file not found: {args.json_path}")
        return 1
    
    if not os.path.exists(args.html_path):
        print(f"Error: HTML file not found: {args.html_path}")
        return 1
    
    if not validate_file_permissions(args.html_path):
        print(f"Error: Cannot write to HTML file: {args.html_path}")
        return 1
    
    try:
        # Load project data from JSON
        print("Loading project data from JSON...")
        source_data = load_project_data(args.json_path)
        print(f"Loaded {len(source_data)} categories")
        
        # Parse existing HTML projectData
        print("Parsing existing HTML projectData...")
        target_data = parse_html_project_data(args.html_path)
        print(f"Found {len(target_data)} existing categories")
        
        # Compare data
        differences = compare_project_data(source_data, target_data)
        
        if differences['changes_count'] == 0 and not args.force:
            print("No changes detected. HTML is up to date.")
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
            create_backup(args.html_path)
        
        # Generate new JavaScript object
        print("Generating JavaScript object...")
        new_js_data = generate_js_object(source_data)
        
        # Update HTML file
        print("Updating HTML file...")
        if update_html_file(args.html_path, new_js_data):
            print("✓ HTML projectData updated successfully!")
            
            # Update statistics if requested
            if args.update_stats:
                print("Updating HTML statistics...")
                if update_html_stats(args.html_path, source_data):
                    print("✓ HTML statistics updated successfully!")
                else:
                    print("⚠ Warning: Could not update HTML statistics")
            
            return 0
        else:
            print("✗ Failed to update HTML file")
            return 1
            
    except Exception as e:
        print(f"Error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 