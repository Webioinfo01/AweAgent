import json
import argparse


def reorder_project_keys(project: dict, key_order: list) -> dict:
    """Reorder keys in project dict according to key_order."""
    new_project = {}
    for key in key_order:
        if key in project:
            new_project[key] = project[key]
    # Add any other keys not in key_order at the end
    for key in project:
        if key not in new_project:
            new_project[key] = project[key]
    return new_project


def add_columns_to_json(json_path: str, output_path: str) -> None:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Categories that need 'team' column added if missing
    add_team_categories = ['ai-tools', 'reviews']

    # Define desired key order
    base_key_order = ["year", "title", "team", "team website", "affiliation", "domain", "venue", "paperUrl", "codeUrl", "githubStars"]

    for category, projects in data.items():
        for i, project in enumerate(projects):
            # Add 'team' column to specified categories if missing
            if category in add_team_categories and 'team' not in project:
                new_project = {}
                for key in project:
                    new_project[key] = project[key]
                    if key == 'title':
                        new_project['team'] = ""
                project = new_project

            # Add 'team website' and 'affiliation' after 'team'
            if 'team' in project:
                if 'team website' not in project:
                    project['team website'] = ""
                if 'affiliation' not in project:
                    project['affiliation'] = ""

            # Reorder keys
            project = reorder_project_keys(project, base_key_order)
            projects[i] = project

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Add 'team', 'team website' and 'affiliation' columns to JSON data with ordered keys")
    parser.add_argument('--json-path', type=str, required=True, help='Path to input JSON file')
    parser.add_argument('--output-path', type=str, required=True, help='Path to output JSON file')
    args = parser.parse_args()

    add_columns_to_json(args.json_path, args.output_path)


if __name__ == '__main__':
    main() 