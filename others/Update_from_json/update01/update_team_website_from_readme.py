import json
import argparse
import re


def strip_markdown(text: str) -> str:
    """Strip markdown formatting like **bold** from text."""
    # Remove **bold**
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    # Remove other markdown if needed (e.g., _italic_)
    text = re.sub(r'_(.*?)_', r'\1', text)
    return text.strip()


def extract_team_websites_from_readme(readme_path: str) -> dict:
    """Extract team website URLs from all markdown tables in the README."""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find all markdown tables starting with '## ' header
    table_pattern = re.compile(r'## (.+?)\n\n((\|.*\|\n)+)', re.MULTILINE)

    team_websites = {}

    for match in table_pattern.finditer(content):
        category = match.group(1).strip()
        table_md = match.group(2)

        lines = table_md.strip().split('\n')
        if len(lines) < 3:
            continue

        headers = [h.strip() for h in lines[0].strip('|').split('|')]
        data_lines = lines[2:]

        # Check if 'Title' and 'Team Website' columns exist
        if 'Title' not in headers or 'Team Website' not in headers:
            continue

        title_idx = headers.index('Title')
        team_website_idx = headers.index('Team Website')

        for line in data_lines:
            cols = [c.strip() for c in line.strip('|').split('|')]
            if len(cols) <= max(title_idx, team_website_idx):
                continue
            title = strip_markdown(cols[title_idx])
            team_website = cols[team_website_idx]
            # Extract URL from markdown link
            url_match = re.search(r'\((.*?)\)', team_website)
            url = url_match.group(1) if url_match else ""
            team_websites[title] = url

    return team_websites


def update_team_website_in_json(json_path: str, readme_path: str, output_path: str) -> None:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    team_websites = extract_team_websites_from_readme(readme_path)

    # Update JSON data
    for category, projects in data.items():
        for project in projects:
            title = strip_markdown(project.get('title', ''))
            if title in team_websites:
                project['team website'] = team_websites[title]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Update 'team website' in JSON data from README markdown")
    parser.add_argument('--json-path', type=str, required=True, help='Path to input JSON file')
    parser.add_argument('--readme-path', type=str, required=True, help='Path to README markdown file')
    parser.add_argument('--output-path', type=str, required=True, help='Path to output JSON file')
    args = parser.parse_args()

    update_team_website_in_json(args.json_path, args.readme_path, args.output_path)


if __name__ == '__main__':
    main() 