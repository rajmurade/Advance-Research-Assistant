import json
import re
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis
from .firecrawl import TavilyService
from .prompts import DeveloperToolsPrompts


class Workflow:
    def _clean_response(self, text: str) -> str:
        import re
        # Remove think blocks completely
        text = re.sub(r' thinking[\s\S]*? response', '', text)
        # Remove markdown code fences
        text = re.sub(r'```(?:json)?', '', text)
        text = text.replace('```', '')
        return text.strip()

    def _extract_names_from_titles(self, titles):
        prompt = (
            f"Extract only the product/tool names mentioned in these titles. "
            f"Return one name per line, no explanations.\n\n"
            f"Titles:\n" + "\n".join(titles)
        )
        try:
            response = self.llm.invoke([HumanMessage(content=prompt)])
            cleaned = self._clean_response(response.content)
            names = [
                line.strip()
                for line in cleaned.split("\n")
                if line.strip()
                and not line.startswith(('-', '*', '#', '<'))
            ][:4]
            return names
        except Exception as e:
            print(e)
            return titles[:4]

    def __init__(self):
        self.tavily = TavilyService()
        self.llm = ChatGroq(model="openai/gpt-oss-20b", temperature=0.1, max_tokens=800)
        self.prompts = DeveloperToolsPrompts()
        self.workflow = self._build_workflow()

    def _build_workflow(self):
        graph = StateGraph(ResearchState)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.set_entry_point("extract_tools")
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        return graph.compile()

    def _extract_tools_step(self, state: ResearchState) -> Dict[str, Any]:
        print(f"🔍 Finding articles about: {state.query}")

        article_query = f"{state.query} tools comparison best alternatives"
        search_results = self.tavily.search_companies(article_query, num_results=3)

        all_content = ""
        for result in search_results.data:
            url = result.get("url", "")
            scraped = self.tavily.scrape_company_pages(url)
            if scraped:
                all_content + scraped.markdown[:1500] + "\n\n"

        messages = [
            SystemMessage(content=self.prompts.TOOL_EXTRACTION_SYSTEM),
            HumanMessage(content=self.prompts.tool_extraction_user(state.query, all_content))
        ]

        try:
            response = self.llm.invoke(messages)
            cleaned = self._clean_response(response.content)
            tool_names = []
            for line in cleaned.split("\n"):
                line = line.strip()
                if not line:
                    continue
                if line.startswith(('-', '*', '#', '<', '1', '2', '3', '4', '5', '6', '7', '8', '9')):
                    continue
                if len(line) > 40:
                    continue
                skip_words = ['focus', 'limit', 'only', 'actual', 'provide', 'list', 'include', 'example', 'note']
                if any(word in line.lower() for word in skip_words):
                    continue
                tool_names.append(line)

            tool_names = tool_names[:5]

            if not tool_names:
                fallback_messages = [
                    SystemMessage(content="You are a developer tools expert."),
                    HumanMessage(content=f"List the top 5 most popular tools for: {state.query}. Return only tool names, one per line.")
                ]
                response = self.llm.invoke(fallback_messages)
                tool_names = [line.strip() for line in self._clean_response(response.content).split("\n") if line.strip() and len(line.strip()) < 30]

            print(f"Extracted tools: {', '.join(tool_names)}")
            return {"extracted_tools": tool_names}
        except Exception as e:
            print(e)
            return {"extracted_tools": []}

    def _analyze_company_content(self, company_name: str, content: str) -> CompanyAnalysis:
        messages = [
            SystemMessage(content=self.prompts.TOOL_ANALYSIS_SYSTEM),
            HumanMessage(content=self.prompts.tool_analysis_user(company_name, content))
        ]

        try:
            response = self.llm.invoke(messages)
            print("RAW RESPONSE:", response.content[:500])
            content = self._clean_response(response.content)
            result = json.loads(content)
            return CompanyAnalysis(**result)
        except Exception as e:
            print(e)
            return CompanyAnalysis(
                pricing_model="Unknown",
                is_open_source=None,
                tech_stack=[],
                description="Failed",
                api_available=None,
                language_support=[],
                integration_capabilities=[],
            )


    def _research_step(self, state: ResearchState) -> Dict[str, Any]:
        extracted_tools = getattr(state, "extracted_tools", [])

        if not extracted_tools:
            print("⚠️ No extracted tools found, falling back to direct search")
            search_results = self.tavily.search_companies(state.query, num_results=4)
            raw_titles = [
                result.get("metadata", {}).get("title", "Unknown")
                for result in search_results.data
            ]
            tool_names = self._extract_names_from_titles(raw_titles)
        else:
            tool_names = extracted_tools[:4]

        print(f"🔬 Researching specific tools: {', '.join(tool_names)}")

        companies = []
        for tool_name in tool_names:
            url = self._get_official_url(tool_name)

            if url:
                company = CompanyInfo(
                    name=tool_name,
                    description="",
                    website=url,
                    tech_stack=[],
                    competitors=[]
                )

                scraped = self.tavily.scrape_company_pages(url)
                if scraped:
                    content = scraped.markdown
                    analysis = self._analyze_company_content(company.name, content)

                    company.pricing_model = analysis.pricing_model
                    company.is_open_source = analysis.is_open_source
                    company.tech_stack = analysis.tech_stack
                    company.description = analysis.description
                    company.api_available = analysis.api_available
                    company.language_support = analysis.language_support
                    company.integration_capabilities = analysis.integration_capabilities

                companies.append(company)

        return {"companies": companies}

    def _get_official_url(self, tool_name: str) -> str:
        messages = [
            SystemMessage(content="You are a developer tools expert. Return only a URL, nothing else."),
            HumanMessage(content=f"What is the official homepage URL of {tool_name}? Return only the URL.")
        ]
        response = self.llm.invoke(messages)
        url = self._clean_response(response.content).strip()
        return url

    def _analyze_step(self, state: ResearchState) -> Dict[str, Any]:
        print("Generating recommendations")

        company_data = ", ".join([
            company.json() for company in state.companies
        ])

        messages = [
            SystemMessage(content=self.prompts.RECOMMENDATIONS_SYSTEM),
            HumanMessage(content=self.prompts.recommendations_user(state.query, company_data))
        ]

        response = self.llm.invoke(messages)
        content = self._clean_response(response.content)
        return {"analysis": content}

    def run(self, query: str) -> ResearchState:
        initial_state = ResearchState(query=query)
        final_state = self.workflow.invoke(initial_state)
        return ResearchState(**final_state)
