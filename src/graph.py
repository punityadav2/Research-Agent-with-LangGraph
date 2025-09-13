import os
import sqlite3
from langchain_groq import ChatGroq
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END
from langgraph.checkpoint.sqlite import SqliteSaver
from.agent_state import AgentState
from.tools import search_tool, scrape_tool

from dotenv import load_dotenv
 
load_dotenv()  # Load environment variables from .env

llm = ChatGroq(
    model="openai/gpt-oss-120b",
    temperature=0,
    api_key=os.getenv("GROQ_API_KEY")
)


# --- Node Functions ---

def search_node(state: AgentState):
    """
    Searches for articles on the given topic and updates the state with a list of URLs.
    """
    print("--- Searching for articles ---")
    results = search_tool.invoke(state['topic'])
    urls = [res['url'] for res in results if res and 'url' in res]
    return {"urls": urls}

def scrape_and_summarize_node(state: AgentState):
    """
    Scrapes a URL, and if the content is relevant, summarizes it and adds it to the state.
    If not relevant, it discards the content and moves to the next URL.
    """
    print("--- Scraping and summarizing content ---")
    urls = state.get('urls',)
    if not urls:
        return {"error": "No URLs to process."}

    # Take the next URL from the list
    url_to_scrape = urls.pop(0)
    
    content = scrape_tool.invoke({"url": url_to_scrape})
    
    if not content or content.startswith("Error"):
        print(f"URL: {url_to_scrape} - Failed to scrape or no content.")
        return {"urls": urls, "error": content}

    # This prompt asks the LLM to summarize ONLY if the content is relevant.
    # This is more robust than a simple 'yes'/'no' check.
    prompt = ChatPromptTemplate.from_template(
        "You are a research assistant. Your task is to summarize the following content about the topic: {topic}. "
        "If the content is NOT relevant to the topic, respond with only the single word 'IRRELEVANT'. "
        "Otherwise, provide a concise summary of the relevant information."
        "\n\nContent:\n{content}"
    )
    
    chain = prompt | llm
    summary_result = chain.invoke({"topic": state['topic'], "content": content[:8000]}).content
    
    # If the model returns "IRRELEVANT", we discard it. Otherwise, we add the summary.
    if "IRRELEVANT" in summary_result.upper():
        print(f"URL: {url_to_scrape} - Not relevant.")
        return {"urls": urls}
    else:
        print(f"URL: {url_to_scrape} - Summarized.")
        return {"urls": urls, "summaries": [summary_result]}

def compile_report_node(state: AgentState):
    """
    Takes all the collected summaries and synthesizes them into a final report.
    """
    print("--- Compiling final report ---")
    summaries = state.get('summaries',)
    if not summaries:
        return {"report": "No relevant information found to compile a report."}
    
    prompt = ChatPromptTemplate.from_template(
        "You are a research report writer. Synthesize the following summaries into a coherent and well-structured research report on the topic: {topic}."
        "\n\nSummaries:\n{summaries}"
    )
    
    chain = prompt | llm
    report = chain.invoke({"topic": state['topic'], "summaries": "\n\n---\n\n".join(summaries)}).content
    return {"report": report}

# --- Edge Logic ---

def should_continue_router(state: AgentState):
    """
    Determines whether the research loop should continue or end.
    """
    if state.get('urls'):
        return "scrape_and_summarize"  # Continue if there are more URLs
    else:
        return "compile_report"  # End the loop if all URLs are processed

# --- Graph Definition ---

workflow = StateGraph(AgentState)

# Add the nodes to the graph
workflow.add_node("search", search_node)
workflow.add_node("scrape_and_summarize", scrape_and_summarize_node)
workflow.add_node("compile_report", compile_report_node)

# Set the entry point and define the flow
workflow.set_entry_point("search")
workflow.add_edge("search", "scrape_and_summarize")
workflow.add_conditional_edges(
    "scrape_and_summarize",
    should_continue_router,
    {
        "scrape_and_summarize": "scrape_and_summarize",
        "compile_report": "compile_report"
    }
)
workflow.add_edge("compile_report", END)

# --- Compile with Checkpointer for Fault Tolerance ---
conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
memory = SqliteSaver(conn=conn)
app = workflow.compile(checkpointer=memory)