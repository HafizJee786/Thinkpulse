import os
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_tavily import TavilySearch
from langchain_core.messages import HumanMessage, SystemMessage

load_dotenv()

# ── Initialize LLM ────────────────────────────────────────
def get_llm():
    return ChatGroq(
        api_key=os.getenv("GROQ_API_KEY"),
        model_name="llama-3.3-70b-versatile",
        temperature=0.3,
        max_tokens=4096
    )

# ── Initialize Search Tool ────────────────────────────────
def get_search_tool():
    return TavilySearch(
        api_key=os.getenv("TAVILY_API_KEY"),
        max_results=5
    )

# ── Search Web ────────────────────────────────────────────
def search_web(topic: str, depth: str = "standard") -> list:
    search_tool = get_search_tool()

    if depth == "quick":
        queries = [topic]
    elif depth == "deep":
        queries = [
            f"{topic} overview",
            f"{topic} latest developments 2025",
            f"{topic} expert opinions",
            f"{topic} future trends",
            f"{topic} key challenges"
        ]
    else:
        queries = [
            f"{topic} overview",
            f"{topic} recent developments",
            f"{topic} key facts and findings"
        ]

    all_results = []
    for query in queries:
        try:
            results = search_tool.invoke(query)
            all_results.extend(results)
        except Exception as e:
            print(f"Search error for '{query}': {e}")

    return all_results

# ── Format Search Results ──────────────────────────────────
def format_results(results) -> str:
    formatted = ""
    seen_urls = set()

    # Handle both old and new Tavily response formats
    if isinstance(results, str):
        return results

    for i, r in enumerate(results):
        # New format - result is a string
        if isinstance(r, str):
            formatted += f"\nResult {i+1}:\n{r}\n"
            formatted += "-" * 50 + "\n"
        # Old format - result is a dict
        elif isinstance(r, dict):
            url = r.get("url", "")
            if url in seen_urls:
                continue
            seen_urls.add(url)
            formatted += f"\nSource {i+1}: {url}\n"
            formatted += f"Content: {r.get('content', '')}\n"
            formatted += "-" * 50 + "\n"

    return formatted

# ── Generate Report with LLM ──────────────────────────────
def generate_report(topic: str, search_results: str, depth: str) -> str:
    llm = get_llm()

    if depth == "quick":
        detail = "Write a brief 2-3 paragraph summary."
    elif depth == "deep":
        detail = "Write a very detailed and comprehensive report with multiple sections."
    else:
        detail = "Write a well-structured report with key sections."

    messages = [
        SystemMessage(content="""You are an expert AI research assistant. 
        Your job is to analyze search results and generate professional research reports.
        Always structure your report with clear headings and sections.
        Include key findings, important facts, and cite sources where possible."""),
        HumanMessage(content=f"""Based on the following search results, generate a comprehensive research report about: {topic}

{detail}

Structure your report with these sections:
1. Executive Summary
2. Key Findings
3. Recent Developments
4. Important Facts
5. Conclusion
6. Sources

Search Results:
{search_results}

Generate the report now:""")
    ]

    response = llm.invoke(messages)
    return response.content

# ── Main Research Function ────────────────────────────────
def research_topic(topic: str, depth: str = "standard") -> dict:
    """
    Main function to research a topic
    depth: 'quick' or 'standard' or 'deep'
    """
    try:
        print(f"Searching web for: {topic}")
        results = search_web(topic, depth)

        if not results:
            return {
                "topic": topic,
                "depth": depth,
                "report": "No search results found. Please try a different topic.",
                "status": "error"
            }

        print(f"Found {len(results)} results. Generating report...")
        formatted = format_results(results)
        report = generate_report(topic, formatted, depth)

        return {
            "topic": topic,
            "depth": depth,
            "report": report,
            "status": "success"
        }

    except Exception as e:
        return {
            "topic": topic,
            "depth": depth,
            "report": f"Error: {str(e)}",
            "status": "error"
        }