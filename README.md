# 🚀 Advanced Research Agent

An AI-powered research agent that discovers, analyzes, and compares developer tools using web search, website scraping, and structured LLM analysis.

Instead of simply answering questions, the agent follows a multi-step research workflow to identify relevant developer tools, gather information from official websites, analyze them using an LLM, and generate concise recommendations.

---

## Features

- 🔍 Searches the web for relevant developer tools
- 🌐 Scrapes official websites using Firecrawl
- 🤖 Uses an LLM to extract structured information
- 📊 Compares multiple developer tools
- 💰 Identifies pricing models
- 🛠️ Extracts supported technologies and programming languages
- 🔌 Detects API availability
- 🔗 Finds integrations
- 📝 Generates concise recommendations

---

## Workflow

```text
User Query
     │
     ▼
Search Comparison Articles
     │
     ▼
Extract Tool Names
     │
     ▼
Research Official Websites
     │
     ▼
Scrape Website Content
     │
     ▼
LLM Analysis
     │
     ▼
Structured Company Information
     │
     ▼
Developer Recommendations
```

---

## Tech Stack

- Python
- LangGraph
- LangChain
- Firecrawl API
- OpenAI GPT-4o Mini *(tutorial default)*
- Pydantic
- python-dotenv
- uv

> **Note:** This project can easily be adapted to use Groq or other LLM providers by replacing the language model configuration.

---

## Project Structure

```
advanced-agent/
│
├── main.py                 # CLI entry point
├── pyproject.toml
├── README.md
├── uv.lock
│
└── src/
    ├── firecrawl.py        # Firecrawl service
    ├── models.py           # Pydantic models
    ├── prompts.py          # LLM prompts
    └── workflow.py         # LangGraph workflow
```

---

## Installation

Clone the repository

```bash
git clone https://github.com/rajmurade/Advance-Research-Assistant.git
cd Advance-Research-Assistant/advanced-agent
```

Install dependencies

```bash
uv sync
```

---

## Environment Variables

Create a `.env` file in the project root.

```env
OPENAI_API_KEY=your_openai_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

If using Groq instead of OpenAI:

```env
GROQ_API_KEY=your_groq_api_key
FIRECRAWL_API_KEY=your_firecrawl_api_key
```

---

## Running the Project

```bash
uv run main.py
```

Example query:

```
Best authentication providers for Python
```

---

## Example Output

```
1. Supabase
Website: https://supabase.com
Pricing: Freemium
API: Available
Language Support: Python, JavaScript, Go
Tech Stack: PostgreSQL, REST, GraphQL

2. Clerk
Website: https://clerk.com
Pricing: Paid
API: Available

Developer Recommendation:
Supabase is the best choice for open-source projects and rapid backend development, while Clerk offers a more polished authentication experience for production applications.
```

---

## Key Concepts

- LangGraph workflow orchestration
- Multi-step AI pipelines
- Structured LLM outputs with Pydantic
- Prompt engineering
- Firecrawl web search and scraping
- State management
- Modular project architecture

---

## Future Improvements

- Replace OpenAI with Groq
- Parallelize company analysis
- Add retry logic for failed requests
- Cache previous research
- Support GitHub and documentation search
- Export results to Markdown or PDF

---

## Acknowledgements

Built while following and extending the tutorial by **Tech With Tim**.

Repository:
https://github.com/techwithtim/Advanced-Research-Agent

---

## License

This project is intended for educational and learning purposes.
