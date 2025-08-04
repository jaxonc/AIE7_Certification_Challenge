from langchain_core.tools import tool
from .ensemble_rag_graph import get_rag_graph
from langchain_core.messages import HumanMessage

@tool
def rag_tool(query: str) -> str:
    """
    Search for information using RAG (Retrieval-Augmented Generation).
    This tool searches through product documentation and knowledge base.
    """
    try:
        rag_graph = get_rag_graph()
        if rag_graph is None:
            return "RAG system not available - API keys may not be configured."
        
        result = rag_graph.invoke({"question": query})
        return result.get("response", "No response generated from RAG system.")
    except Exception as e:
        return f"Error using RAG tool: {str(e)}"