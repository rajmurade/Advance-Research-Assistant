import json
import os
import re
import subprocess
import sys
import tempfile
from typing import Dict, Any
# pyrefly: ignore [missing-import]
from langgraph.graph import StateGraph, END
# pyrefly: ignore [missing-import]
from langchain_groq import ChatGroq
# pyrefly: ignore [missing-import]
from langchain_core.messages import HumanMessage, SystemMessage
from .models import ResearchState, CompanyInfo, CompanyAnalysis, CodeOutput
from .firecrawl import TavilyService
from .prompts import DeveloperToolsPrompts

for _stream in (sys.stdout, sys.stderr):
    if _stream is not None and hasattr(_stream, "reconfigure"):
        try:
            _stream.reconfigure(encoding="utf-8", errors="replace")
        except Exception:
            pass


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
        graph.add_node("classify", self._classify_request)
        graph.add_node("extract_tools", self._extract_tools_step)
        graph.add_node("research", self._research_step)
        graph.add_node("analyze", self._analyze_step)
        graph.add_node("code_generate", self._code_generate_step)
        graph.add_node("code_execute", self._code_execute_step)
        graph.add_node("code_explain", self._code_explain_step)
        graph.set_entry_point("classify")
        graph.add_conditional_edges(
            "classify",
            self._route_by_type,
            {"code": "code_generate", "research": "extract_tools"},
        )
        graph.add_edge("extract_tools", "research")
        graph.add_edge("research", "analyze")
        graph.add_edge("analyze", END)
        graph.add_edge("code_generate", "code_execute")
        graph.add_conditional_edges(
            "code_execute",
            self._code_route,
            {"retry": "code_generate", "done": "code_explain"},
        )
        graph.add_edge("code_explain", END)
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
                all_content += scraped.markdown[:1500] + "\n\n"

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

    def _analyze_from_knowledge(self, tool_name: str) -> CompanyAnalysis:
        fallback_messages = [
            SystemMessage(content="You are a developer tools expert. Return only JSON, no explanation."),
            HumanMessage(content=f"""Return a JSON object for {tool_name} with these exact fields:
            {{
                "pricing_model": "Free/Freemium/Paid/Enterprise",
                "is_open_source": true/false,
                "tech_stack": ["item1", "item2"],
                "description": "one sentence description",
                "api_available": true/false,
                "language_support": ["lang1", "lang2"],
                "integration_capabilities": ["tool1", "tool2"]
            }}""")
        ]

        try:
            response = self.llm.invoke(fallback_messages)
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
                if scraped and scraped.markdown and scraped.markdown.strip():
                    analysis = self._analyze_company_content(company.name, scraped.markdown)
                else:
                    analysis = self._analyze_from_knowledge(tool_name)

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

    MAX_CODE_ATTEMPTS = 3

    def _classify_request(self, state: ResearchState) -> Dict[str, Any]:
        try:
            messages = [
                SystemMessage(content=self.prompts.REQUEST_CLASSIFIER_SYSTEM),
                HumanMessage(content=self.prompts.classifier_user(state.query)),
            ]
            response = self.llm.invoke(messages)
            label = self._clean_response(str(response.content)).strip().lower()
            return {"request_type": "code" if label.startswith("code") else "research"}
        except Exception as e:
            print(e)
            return {"request_type": "research"}

    def _route_by_type(self, state: ResearchState) -> str:
        return "code" if state.request_type == "code" else "research"

    def _extract_code(self, content: str):
        fences = re.findall(r"```([a-zA-Z0-9+#\-]*)\n(.*?)```", content, re.DOTALL)
        if fences:
            language, code = fences[-1]
            return code.strip(), (language.strip() or "python").lower()
        return content.strip(), "python"

    def _extract_explanation(self, content: str) -> str:
        prefix = content.split("```")[0]
        return prefix.replace("EXPLANATION:", "").strip()

    def _code_generate_step(self, state: ResearchState) -> Dict[str, Any]:
        if state.code_error:
            messages = [
                SystemMessage(content=self.prompts.CODE_GENERATION_SYSTEM),
                HumanMessage(content=self.prompts.code_generation_user(state.query, state.code, state.code_error)),
            ]
        else:
            messages = [
                SystemMessage(content=self.prompts.CODE_GENERATION_SYSTEM),
                HumanMessage(content=self.prompts.code_generation_user(state.query)),
            ]
        response = self.llm.invoke(messages)
        content = str(response.content)
        code, language = self._extract_code(content)
        explanation = self._extract_explanation(content)
        return {
            "code": code,
            "code_language": language,
            "code_explanation": explanation,
            "code_error": None,
        }

    def _code_sandbox_dir(self) -> str:
        sandbox = os.path.join(tempfile.gettempdir(), "era_code_exec")
        os.makedirs(sandbox, exist_ok=True)
        return sandbox

    def _execute_python(self, code: str):
        try:
            result = subprocess.run(
                [sys.executable, "-"],
                input=code,
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="replace",
                timeout=15,
                cwd=self._code_sandbox_dir(),
            )
            output = (result.stdout or "").strip()
            if result.returncode != 0:
                error = (result.stderr or "").strip() or f"process exited with code {result.returncode}"
                return output, error
            return output, None
        except subprocess.TimeoutExpired:
            return "", "Execution timed out after 15 seconds."
        except Exception as e:
            return "", str(e)

    def _code_execute_step(self, state: ResearchState) -> Dict[str, Any]:
        language = (state.code_language or "").lower()
        executed = False
        output = ""
        error = None
        if language in ("python", "py", ""):
            executed = True
            output, error = self._execute_python(state.code)
        return {
            "code_output": output,
            "code_error": error,
            "code_executed": executed,
            "code_attempts": state.code_attempts + 1,
        }

    def _code_route(self, state: ResearchState) -> str:
        if state.code_error and state.code_attempts < self.MAX_CODE_ATTEMPTS:
            return "retry"
        return "done"

    def _code_explain_step(self, state: ResearchState) -> Dict[str, Any]:
        try:
            messages = [
                SystemMessage(content=self.prompts.CODE_EXPLAIN_SYSTEM),
                HumanMessage(content=self.prompts.code_explain_user(
                    state.query, state.code_language, state.code_executed,
                    state.code_output, state.code_error or "", state.code,
                )),
            ]
            response = self.llm.invoke(messages)
            explanation = str(response.content).strip()
        except Exception as e:
            print(e)
            explanation = state.code_explanation or "Code generated."
        return {
            "code_explanation": explanation,
            "code_result": CodeOutput(
                code=state.code,
                language=state.code_language,
                explanation=explanation,
                output=state.code_output,
                error=state.code_error,
                executed=state.code_executed,
                retries=max(0, state.code_attempts - 1),
                execution_count=state.code_attempts,
            ),
        }
