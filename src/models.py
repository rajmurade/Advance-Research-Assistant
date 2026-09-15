from typing import List, Optional, Dict, Any
# pyrefly: ignore [missing-import]
from pydantic import BaseModel


class CompanyAnalysis(BaseModel):
    """Structured output for LLM company analysis focused on developer tools"""
    pricing_model: str  # Free, Freemium, Paid, Enterprise, Unknown
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    description: str = ""
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []


class CompanyInfo(BaseModel):
    name: str
    description: str
    website: str
    pricing_model: Optional[str] = None
    is_open_source: Optional[bool] = None
    tech_stack: List[str] = []
    competitors: List[str] = []
    # Developer-specific fields
    api_available: Optional[bool] = None
    language_support: List[str] = []
    integration_capabilities: List[str] = []
    developer_experience_rating: Optional[str] = None  # Poor, Good, Excellent


class CodeOutput(BaseModel):
    """Structured output for the code assistance workflow."""
    code: str = ""
    language: str = "python"
    explanation: str = ""
    output: str = ""
    error: Optional[str] = None
    executed: bool = False
    retries: int = 0
    execution_count: int = 0


class ResearchState(BaseModel):
    query: str
    request_type: str = "research"  # "code" or "research"
    extracted_tools: List[str] = []  # Tools extracted from articles
    companies: List[CompanyInfo] = []
    search_results: List[Dict[str, Any]] = []
    analysis: Optional[str] = None
    code: str = ""
    code_language: str = "python"
    code_output: str = ""
    code_error: Optional[str] = None
    code_executed: bool = False
    code_attempts: int = 0
    code_explanation: str = ""
    code_result: Optional[CodeOutput] = None


class RepoAnalysis(BaseModel):
    """Structured output for GitHub repository analysis"""
    name: str
    description: str
    stars: int
    language: str
    topics: List[str] = []
    dependencies: List[str] = []
    suggestion: str = ""
