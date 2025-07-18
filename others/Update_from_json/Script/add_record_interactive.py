import json
import os
import argparse

DATA_TYPES = ["ai-agents", "foundation-models", "ai-tools", "databases", "benchmarks", "reviews"]

FIELDS = ["year", "title", "team", "team website", "affiliation", "domain", "venue", "paperUrl", "codeUrl", "githubStars"]


def prompt_data_type():
    print("Select data type to add a record:")
    for i, dt in enumerate(DATA_TYPES, 1):
        print(f"{i}. {dt}")
    while True:
        choice = input("Enter number or name: ").strip()
        if choice.isdigit():
            idx = int(choice) - 1
            if 0 <= idx < len(DATA_TYPES):
                print("Note: 'year' and 'title' fields are mandatory.")
                return DATA_TYPES[idx]
        elif choice in DATA_TYPES:
            print("Note: 'year' and 'title' fields are mandatory.")
            return choice
        print("Invalid choice. Please try again.")


def prompt_record_fields():
    print("Enter record fields separated by semicolons (;). Use empty quotes \"\" for empty values.")
    print("Fields: year; title; team; team website; affiliation; domain; venue; paperUrl; codeUrl; githubStars")
    while True:
        line = input("Record: ").strip()
        parts = [p.strip() for p in line.split(';')]
        # Auto-fill missing fields with empty strings
        if len(parts) < len(FIELDS):
            parts.extend([""] * (len(FIELDS) - len(parts)))
        elif len(parts) > len(FIELDS):
            print(f"Too many fields. Expected {len(FIELDS)} but got {len(parts)}. Please try again.")
            continue
        # Replace "" with empty string
        parts = ["" if p == '""' else p for p in parts]
        # Validate mandatory fields
        if not parts[0]:
            print("Year is mandatory. Please enter a value.")
            continue
        if not parts[1]:
            print("Title is mandatory. Please enter a value.")
            continue

        # Auto-generate githubStars if codeUrl is a GitHub repo URL
        code_url = parts[8]
        if "github.com" in code_url:
            # Extract owner/repo from URL
            try:
                # Remove protocol and domain
                path = code_url.split("github.com/")[1].strip("/")
                # Only keep owner/repo part
                owner_repo = "/".join(path.split("/")[:2])
                badge_url = f"https://img.shields.io/github/stars/{owner_repo}"
                parts[9] = badge_url
            except Exception:
                pass

        return dict(zip(FIELDS, parts))


def load_json(json_path):
    if not os.path.exists(json_path):
        return {dt: [] for dt in DATA_TYPES}
    with open(json_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def save_json(json_path, data):
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def main():
    parser = argparse.ArgumentParser(description='Interactive JSON record adder')
    parser.add_argument('--json-path', required=True, help='Path to JSON file to add records')
    args = parser.parse_args()

    data_type = prompt_data_type()
    record = prompt_record_fields()

    data = load_json(args.json_path)
    if data_type not in data:
        data[data_type] = []
    data[data_type].append(record)

    save_json(args.json_path, data)
    print(f"Record added to {data_type} successfully in {args.json_path}.")


if __name__ == '__main__':
    main() 