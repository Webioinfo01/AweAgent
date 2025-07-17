"""
Shared utilities for project data synchronization scripts.
"""

import json
import os
import shutil
from datetime import datetime
from typing import Dict, List, Optional, Any


def load_project_data(json_path: str) -> dict:
    """
    Load and validate project data from JSON file.
    
    Args:
        json_path (str): Path to the JSON file
        
    Returns:
        dict: Loaded project data
        
    Raises:
        FileNotFoundError: If JSON file doesn't exist
        json.JSONDecodeError: If JSON is malformed
        ValueError: If data structure is invalid
    """
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"JSON file not found: {json_path}")
    
    try:
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        raise json.JSONDecodeError(f"Invalid JSON format in {json_path}: {e}")
    
    # Validate data structure
    if not isinstance(data, dict):
        raise ValueError("JSON data must be a dictionary")
    
    # Validate each category
    for category, projects in data.items():
        if not isinstance(projects, list):
            raise ValueError(f"Category '{category}' must contain a list of projects")
        
        for i, project in enumerate(projects):
            if not isinstance(project, dict):
                raise ValueError(f"Project {i} in category '{category}' must be a dictionary")
            
            # Check required fields
            if 'year' not in project or 'title' not in project:
                raise ValueError(f"Project {i} in category '{category}' missing required fields: year, title")
            
            if not project['year'] or not project['title']:
                raise ValueError(f"Project {i} in category '{category}' has empty year or title")
    
    return data


def create_backup(file_path: str, create_backup: bool = True) -> Optional[str]:
    """
    Create a backup of the specified file.
    
    Args:
        file_path (str): Path to the file to backup
        create_backup (bool): Whether to create backup
        
    Returns:
        Optional[str]: Path to backup file if created, None otherwise
    """
    if not create_backup or not os.path.exists(file_path):
        return None
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_path = f"{file_path}.{timestamp}.bak"
    
    try:
        shutil.copy2(file_path, backup_path)
        print(f"Created backup: {backup_path}")
        return backup_path
    except Exception as e:
        print(f"Warning: Could not create backup of {file_path}: {e}")
        return None


def compare_project_data(source: dict, target: dict) -> dict:
    """
    Compare source and target project data to find differences.
    
    Args:
        source (dict): Source project data
        target (dict): Target project data
        
    Returns:
        dict: Dictionary containing differences
    """
    differences = {
        'added_categories': [],
        'removed_categories': [],
        'modified_categories': [],
        'changes_count': 0
    }
    
    source_categories = set(source.keys())
    target_categories = set(target.keys())
    
    # Find added and removed categories
    differences['added_categories'] = list(source_categories - target_categories)
    differences['removed_categories'] = list(target_categories - source_categories)
    
    # Find modified categories
    for category in source_categories & target_categories:
        if source[category] != target[category]:
            differences['modified_categories'].append(category)
    
    differences['changes_count'] = len(differences['added_categories']) + \
                                  len(differences['removed_categories']) + \
                                  len(differences['modified_categories'])
    
    return differences


def escape_markdown(text: str) -> str:
    """
    Escape special characters for markdown table cells.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Escaped text
    """
    if not text:
        return ""
    
    # Replace pipe characters with escaped version
    text = text.replace("|", "\\|")
    # Replace newlines with spaces
    text = text.replace("\n", " ").replace("\r", " ")
    # Clean up multiple spaces
    text = " ".join(text.split())
    
    return text


def escape_javascript(text: str) -> str:
    """
    Escape special characters for JavaScript strings.
    
    Args:
        text (str): Text to escape
        
    Returns:
        str: Escaped text
    """
    if not text:
        return ""
    
    # Escape quotes and backslashes
    text = text.replace("\\", "\\\\")
    text = text.replace('"', '\\"')
    text = text.replace("'", "\\'")
    text = text.replace("\n", "\\n")
    text = text.replace("\r", "\\r")
    text = text.replace("\t", "\\t")
    
    return text


def format_links_for_markdown(paper_url: str, code_url: str, github_stars: str) -> str:
    """
    Format paper and code links for markdown table.
    
    Args:
        paper_url (str): URL to paper
        code_url (str): URL to code repository
        github_stars (str): GitHub stars info (can be full URL or repo path)
        
    Returns:
        str: Formatted links string
    """
    links = []
    
    if paper_url:
        links.append(f"[Link]({paper_url})")
    
    if code_url:
        link_text = "[Link](" + code_url + ")"
        if github_stars:
            # Handle both full URLs and repo paths
            if github_stars.startswith('http'):
                # Full URL format like "https://img.shields.io/github/stars/mugpeng/DROMA"
                link_text += f" ![GitHub Stars]({github_stars})"
            else:
                # Legacy repo path format
                link_text += f" ![GitHub Stars](https://img.shields.io/github/stars/{github_stars})"
        links.append(link_text)
    
    return "<br>".join(links) if links else ""


def get_category_display_name(category_key: str) -> str:
    """
    Get display name for category.
    
    Args:
        category_key (str): Category key
        
    Returns:
        str: Display name
    """
    category_names = {
        'ai-agents': 'AI Agents',
        'foundation-models': 'Foundation models',  # Changed to match template
        'ai-tools': 'AI Tools',
        'databases': 'Databases/Simulation',
        'benchmarks': 'Benchmarks',
        'reviews': 'Reviews'
    }
    return category_names.get(category_key, category_key.replace('-', ' ').title())


def get_category_columns(category_key: str) -> List[str]:
    """
    Get table columns for a specific category.
    
    Args:
        category_key (str): Category key
        
    Returns:
        List[str]: List of column names
    """
    # All categories now use the same comprehensive column structure
    return ["Year", "Title", "Team", "Team Website", "Affiliation", "Domain", "Venue", "Paper/ Source", "Code/Product"]


def validate_file_permissions(file_path: str) -> bool:
    """
    Check if file can be read and written.
    
    Args:
        file_path (str): Path to file
        
    Returns:
        bool: True if file is accessible
    """
    try:
        # Check if file exists and is readable
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                f.read(1)  # Try to read first character
        
        # Check if file can be written (create temp file in same directory)
        dir_path = os.path.dirname(file_path) or '.'
        return os.access(dir_path, os.W_OK)
        
    except Exception:
        return False 