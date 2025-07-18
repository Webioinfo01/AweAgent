#!/usr/bin/env python3
"""
Update both README.md and index.html with project data from JSON file.

This convenience script runs both update_readme.py and update_html.py
to synchronize project data across all output formats.
"""

import argparse
import os
import subprocess
import sys


def run_script(script_name: str, args: list) -> bool:
    """
    Run a script with arguments and return success status.
    
    Args:
        script_name (str): Name of script to run
        args (list): Arguments to pass to script
        
    Returns:
        bool: True if script ran successfully
    """
    script_path = os.path.join(os.path.dirname(__file__), script_name)
    
    if not os.path.exists(script_path):
        print(f"Error: Script not found: {script_path}")
        return False
    
    cmd = [sys.executable, script_path] + args
    
    try:
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        # Print output
        if result.stdout:
            print(result.stdout)
        if result.stderr:
            print(result.stderr, file=sys.stderr)
        
        return result.returncode == 0
        
    except Exception as e:
        print(f"Error running {script_name}: {e}")
        return False


def main():
    """Main function to run both update scripts."""
    parser = argparse.ArgumentParser(
        description='Update both README.md and index.html with project data from JSON'
    )
    parser.add_argument('--json-path', default='Input/test.json',
                       help='Path to JSON file with project data')
    parser.add_argument('--readme-path', default='readme.md',
                       help='Path to README.md file')
    parser.add_argument('--html-path', default='docs/index.html',
                       help='Path to index.html file')
    parser.add_argument('--no-backup', action='store_true',
                       help='Do not create backups before updating')
    parser.add_argument('--force', action='store_true',
                       help='Force update even if no changes detected')
    parser.add_argument('--update-stats', action='store_true',
                       help='Also update statistics in HTML')
    parser.add_argument('--readme-only', action='store_true',
                       help='Update only README file')
    parser.add_argument('--html-only', action='store_true',
                       help='Update only HTML file')
    
    args = parser.parse_args()
    
    print("=== Project Data Synchronization ===")
    print(f"JSON source: {args.json_path}")
    
    if not os.path.exists(args.json_path):
        print(f"Error: JSON file not found: {args.json_path}")
        return 1
    
    success_count = 0
    total_updates = 0
    
    # Prepare common arguments
    common_args = [
        '--json-path', args.json_path,
    ]
    if args.no_backup:
        common_args.append('--no-backup')
    if args.force:
        common_args.append('--force')
    
    # Update README
    if not args.html_only:
        total_updates += 1
        print(f"\n{'='*50}")
        print("UPDATING README")
        print(f"{'='*50}")
        
        readme_args = common_args + ['--readme-path', args.readme_path]
        
        if run_script('update_readme.py', readme_args):
            success_count += 1
            print("README update completed successfully!")
        else:
            print("README update failed!")
    
    # Update HTML
    if not args.readme_only:
        total_updates += 1
        print(f"\n{'='*50}")
        print("UPDATING HTML")
        print(f"{'='*50}")
        
        html_args = common_args + ['--html-path', args.html_path]
        if args.update_stats:
            html_args.append('--update-stats')
        
        if run_script('update_html.py', html_args):
            success_count += 1
            print("HTML update completed successfully!")
        else:
            print("HTML update failed!")
    
    # Summary
    print(f"\n{'='*50}")
    print("SUMMARY")
    print(f"{'='*50}")
    print(f"Updates attempted: {total_updates}")
    print(f"Updates successful: {success_count}")
    print(f"Updates failed: {total_updates - success_count}")
    
    if success_count == total_updates:
        print("✓ All updates completed successfully!")
        return 0
    else:
        print("✗ Some updates failed!")
        return 1


if __name__ == "__main__":
    sys.exit(main()) 