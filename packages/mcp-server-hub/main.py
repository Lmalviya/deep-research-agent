import os
from typing import Optional
from mcp.server.fastmcp import FastMCP
from tavily import TavilyClient
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastMCP server
mcp = FastMCP("RetrievalHub")

# Initialize Tavily client if API key is available
tavily_api_key = os.getenv("TAVILY_API_KEY")
tavily = TavilyClient(api_key=tavily_api_key) if tavily_api_key else None

@mcp.tool()
def internet_search(query: str, search_depth: str = "basic") -> str:
    """
    Search the internet for real-time information using Tavily.
    
    Args:
        query: The search query.
        search_depth: The depth of the search ('basic' or 'advanced').
    """
    if not tavily:
        return "Tavily API key not found. Please set TAVILY_API_KEY in .env"
    
    try:
        response = tavily.search(query=query, search_depth=search_depth)
        results = []
        for result in response.get("results", []):
            results.append(f"Title: {result['title']}\nURL: {result['url']}\nContent: {result['content']}\n")
        return "\n---\n".join(results) if results else "No results found."
    except Exception as e:
        return f"Error during search: {str(e)}"

@mcp.tool()
def search_vector_db(query: str, collection: str = "knowledge_base", limit: int = 3) -> str:
    """
    Search the internal vector database (Qdrant) for relevant context.
    
    Args:
        query: The semantic search query.
        collection: The name of the collection to search in.
        limit: Number of results to return.
    """
    # Placeholder for Qdrant integration
    # In a real scenario, you'd use qdrant_client here
    return f"Successfully searched collection '{collection}' for '{query}'.\nFound {limit} relevant snippets (MOCKED)."

@mcp.tool()
def read_local_resource(path: str) -> str:
    """
    Read a local file to provide context. Only allows reading from the current project directory.
    """
    # Basic security check
    if ".." in path or path.startswith("/"):
        return "Error: Access denied. Only relative paths within the project are allowed."
    
    try:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as f:
                return f.read()
        else:
            return f"Error: File not found at {path}"
    except Exception as e:
        return f"Error reading file: {str(e)}"

if __name__ == "__main__":
    mcp.run()
