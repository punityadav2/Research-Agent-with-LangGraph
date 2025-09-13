import operator
from typing import TypedDict, Annotated, List, Dict

class AgentState(TypedDict):
    """
    Represents the state of our research agent.
    """
    topic: str
    urls: List[str]
    scraped_content: Dict  # Changed from List[dict] to Dict for consistency
    summaries: Annotated[List[str], operator.add]
    report: str
    error: str