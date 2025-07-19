import os
import sys
import time
import threading
from dotenv import load_dotenv
from src.aweagent import PaperAgent
from agno.models.deepseek import DeepSeek
from agno.models.openai import OpenAIChat
from agno.models.google import Gemini
from agno.models.mistral import MistralChat
from agno.models.openai.like import OpenAILike
from agno.utils.pprint import pprint_run_response

# Load environment variables from .env file, if present
load_dotenv()

EXAMPLE_QUERY = """
Find papers:
 query: AI agent|large language model|foundation model
 publication_date: 2025-07-01 to 2025-07-15
 limit: 100
 fields: "paperId", "externalIds", "url", "title", "abstract", "venue", "publicationVenue", "publicationTypes", "publicationDate", "journal", "authors", "citations"
 fields_of_study: "Medicine", "Biology"
 pre-defined category: ["AI agent", "AI Tools", "Foundation Models", "Databases", "Benchmarks", "Reviews"]
"""

class Spinner:
    def __init__(self, message="Processing..."):
        self.message = message
        self.stop_running = False
        self.spinner_thread = None

    def start(self):
        self.stop_running = False
        self.spinner_thread = threading.Thread(target=self._spin)
        self.spinner_thread.start()

    def _spin(self):
        while not self.stop_running:
            for char in "|/-\\":
                sys.stdout.write(f"\r{self.message} {char}")
                sys.stdout.flush()
                time.sleep(0.1)
        sys.stdout.write("\r" + " " * (len(self.message) + 2) + "\r") # Clear line
        sys.stdout.flush()

    def stop(self):
        self.stop_running = True
        if self.spinner_thread:
            self.spinner_thread.join()
            
    def update_message(self, new_message):
        self.message = new_message

def select_model_and_get_keys():
    """Interactively select the model and get API keys."""
    print("Please select the AI model provider:")
    print("1: OpenAI")
    print("2: DeepSeek")
    print("3: Gemini")
    print("4: Mistral")
    print("5: OpenAILike (for custom endpoints)")
    
    model_map = {
        "1": "openai",
        "2": "deepseek",
        "3": "gemini",
        "4": "mistral",
        "5": "openaillm"
    }
    
    while True:
        choice = input("Enter the number of your choice (1-5): ")
        if choice in model_map:
            provider = model_map[choice]
            break
        print("Invalid choice. Please try again.")

    while True:
        api_key = input(f"Please enter your {provider.upper()} API key: ")
        if api_key:
            break
        print("Error: API key cannot be empty. Please try again.")
        
    base_url = None
    if provider == "openaillm":
        while True:
            base_url = input("Please enter the base URL for the OpenAILike model: ")
            if base_url:
                break
            print("Error: Base URL cannot be empty for OpenAILike models. Please try again.")
        
    while True:
        semanticscholar_api_key = input("Please enter your Semantic Scholar API key: ")
        if semanticscholar_api_key:
            break
        print("Error: Semantic Scholar API key cannot be empty. Please try again.")

    return provider, api_key, base_url, semanticscholar_api_key

def get_model(provider, api_key, base_url):
    """Instantiate the selected model."""
    if provider == "openai":
        return OpenAIChat(api_key=api_key)
    elif provider == "deepseek":
        return DeepSeek(api_key=api_key)
    elif provider == "gemini":
        return Gemini(api_key=api_key)
    elif provider == "mistral":
        return MistralChat(api_key=api_key)
    elif provider == "openaillm":
        return OpenAILike(api_key=api_key, base_url=base_url)
    return OpenAIChat(api_key=api_key)

def parse_example_query(example_str):
    """Parse the multiline example query string into a dictionary."""
    defaults = {}
    lines = example_str.strip().split('\n')[1:]  # Skip the "Find papers:" line
    for line in lines:
        if ':' in line:
            key, value = line.split(':', 1)
            defaults[key.strip()] = value.strip()
    return defaults

def build_query_interactively():
    """Guide the user to build a query step-by-step using defaults."""
    print("\nLet's build your query. Defaults are from the example query.")
    print("Press Enter to accept the default value.")
    
    defaults = parse_example_query(EXAMPLE_QUERY)
    
    query_parts = ["Find papers:"]
    
    def get_input_with_default(key, prompt):
        default_val = defaults.get(key, '')
        user_input = input(f"{prompt} (default: {default_val}): ")
        return user_input or default_val

    q = get_input_with_default("query", "Enter search query")
    if q: query_parts.append(f" query: {q}")

    pd = get_input_with_default("publication_date", "Enter publication date range")
    if pd: query_parts.append(f" publication_date: {pd}")

    limit = get_input_with_default("limit", "Enter result limit")
    if limit: query_parts.append(f" limit: {limit}")

    fields = get_input_with_default("fields", "Enter desired fields")
    if fields: query_parts.append(f" fields: {fields}")

    fos = get_input_with_default("fields_of_study", "Enter fields of study")
    if fos: query_parts.append(f" fields_of_study: {fos}")

    cat = get_input_with_default("pre-defined category", "Enter pre-defined categories")
    if cat: query_parts.append(f" pre-defined category: {cat}")

    return "\n".join(query_parts)

def main():
    provider, api_key, base_url, semanticscholar_api_key = select_model_and_get_keys()
    
    db_path = input("Enter path for database directory (default: ./SemanticScholar_db): ") or "./SemanticScholar_db"
    
    output_choice = input("Output report to (1) Screen or (2) File? (default: 1): ") or "1"
    
    output_filename = None
    if output_choice == '2':
        output_filename = input("Enter output filename (default: research_report.md): ") or "research_report.md"

    model = get_model(provider, api_key, base_url)
    
    spinner = Spinner()
    agent = PaperAgent(model=model, semanticscholar_api_key=semanticscholar_api_key, status_callback=spinner.update_message)
    
    print("\nWould you like to use the example query or build your own?")
    use_example = input("Enter 'yes' to use the example, or anything else to build your own: ").lower()
    
    if use_example == 'yes':
        user_query = EXAMPLE_QUERY
        print("\nUsing example query:")
        print(user_query)
    else:
        user_query = build_query_interactively()

    spinner.start()
    report = agent.run(user_query, db_path=db_path)
    spinner.stop()

    if output_filename:
        with open(output_filename, 'w', encoding='utf-8') as f:
            f.write(report.content)
        print(f"\nReport saved to {output_filename}")
    else:
        print("\n--- Report ---")
        pprint_run_response(report, markdown=True)

if __name__ == "__main__":
    main() 