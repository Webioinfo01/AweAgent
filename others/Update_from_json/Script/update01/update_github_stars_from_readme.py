import json
import argparse
import re


def strip_markdown(text: str) -> str:
    """Strip markdown formatting like **bold** from text."""
    text = re.sub(r'\*\*(.*?)\*\*', r'\1', text)
    text = re.sub(r'_(.*?)_', r'\1', text)
    return text.strip()


def extract_github_stars_from_readme(readme_path: str) -> dict:
    """Extract GitHub stars badge URLs from all markdown tables in the README."""
    with open(readme_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Regex to find all markdown tables starting with '## ' header
    table_pattern = re.compile(r'## (.+?)\n\n((\|.*\|\n)+)', re.MULTILINE)

    github_stars = {}

    for match in table_pattern.finditer(content):
        category = match.group(1).strip()
        table_md = match.group(2)

        lines = table_md.strip().split('\n')
        if len(lines) < 3:
            continue

        headers = [h.strip() for h in lines[0].strip('|').split('|')]
        data_lines = lines[2:]

        # Check if 'Title' column exists
        if 'Title' not in headers:
            continue

        title_idx = headers.index('Title')

        for line in data_lines:
            cols = [c.strip() for c in line.strip('|').split('|')]
            if len(cols) <= title_idx:
                continue
            title = strip_markdown(cols[title_idx])

            # Extract GitHub stars badge URL from the line
            # The badge is usually in the last column, find the pattern ![GitHub Stars](url)
            star_url = ""
            star_match = re.search(r'!\[GitHub Stars\]\((https://img.shields.io/github/stars/[^)]+)\)', line)
            if star_match:
                star_url = star_match.group(1)

            github_stars[title] = star_url

    return github_stars


def update_github_stars_in_json(json_path: str, readme_path: str, output_path: str) -> None:
    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    github_stars = extract_github_stars_from_readme(readme_path)

    # Update JSON data
    for category, projects in data.items():
        for project in projects:
            title = strip_markdown(project.get('title', ''))
            if title in github_stars:
                project['githubStars'] = github_stars[title]

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)


def main():
    parser = argparse.ArgumentParser(description="Update 'githubStars' in JSON data from README markdown")
    parser.add_argument('--json-path', type=str, required=True, help='Path to input JSON file')
    parser.add_argument('--readme-path', type=str, required=True, help='Path to README markdown file')
    parser.add_argument('--output-path', type=str, required=True, help='Path to output JSON file')
    args = parser.parse_args()

    update_github_stars_in_json(args.json_path, args.readme_path, args.output_path)


if __name__ == '__main__':
    main() 