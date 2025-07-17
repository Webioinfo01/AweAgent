```
**Act as a Senior AI/ML Project Architect with deep expertise in bioinformatics, NLP, and full-stack automation pipelines.**

My goal is to build an AI agent that automates the discovery, filtering, and summarization of scientific papers for my GitHub project: `Awesome-AI-Meets-Biology`.

Here is my proposed workflow:
1.  **Search:** Given a time range (e.g., last month), search bioRxiv, arXiv, and NCBI/PubMed for papers with keywords: "AI agents," "foundation models," "benchmarks," and "reviews" in the context of biology and bioinformatics.
2.  **Screen:** Use NLP to analyze the abstracts of the search results to determine if they are relevant to my specific interests.
3.  **Extract Metadata:** For relevant papers, parse and record the Title, primary Domain (e.g., Genomics, Proteomics), Venue/Journal, first/last Author Affiliation, and a direct link.
4.  **Filter by Impact:** Prioritize papers from high-impact journals, well-known affiliations (e.g., Broad Institute, DeepMind), or respected research teams.
5.  **Store Data:** Update a central `papers.json` file with the newly filtered paper information in a structured format.
6.  **Update Repository Files:** Execute an existing local script that uses `papers.json` to regenerate the project's `README.md` and `index.html`.
7.  **Create Pull Request:** Use the GitHub API to automatically commit the changes and create a pull request to the main branch of the repository.
8.  **Summarize & Synthesize:** Download the full PDFs of the highest-priority papers and generate a coherent summary or a mini-review paragraph based on them.

**Your Task:**
Provide a comprehensive architectural and strategic plan. Address the following points:

1.  **Phased Roadmap:** Break this project down into logical, manageable phases (e.g., Phase 1: Core Data Pipeline, Phase 2: Automation & Git Integration, etc.). What would be a realistic Minimum Viable Product (MVP)?
2.  **Technical Stack Recommendations:** For each step in the workflow, suggest the best Python libraries, APIs, or tools. For example:
    * **Search (Step 1):** `Bio.Entrez` for NCBI, official arXiv API, bioRxiv API.
    * **Screening & Summarization (Steps 2 & 8):** Which NLP models or frameworks (e.g., Transformers, LangChain, LlamaIndex) are best suited? What are the pros and cons of using a local model vs. a commercial API (like Gemini or GPT-4)?
    * **Filtering (Step 4):** How can I programmatically determine "journal impact" or "affiliation prestige"? Are there APIs or databases for this?
    * **GitHub Integration (Step 7):** `PyGithub` or `gh` CLI? What are the best practices for managing API keys securely?
3.  **Identify Key Challenges & Bottlenecks:**
    * What are the most difficult parts of this workflow?
    * Assess the feasibility and complexity of Step 8 (multi-paper summarization into a review). Is this realistic? What are the major hurdles?
    * How should I handle rate limiting on the various APIs?
    * What is the best way to define my "interest fields" for the screening step in a way the AI can reliably use?
4.  **Actionable First Steps:** Based on your recommended MVP, what are the first 3-5 concrete actions I should take to start building this agent?
```

