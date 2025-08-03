from langchain_core.tools import tool
from utils.rag_graph import rag_graph
from langchain_core.messages import HumanMessage

@tool
def rag_tool(query: str) -> str:
    """
    Search the product knowledge base for information about the given query.
    """
    response = rag_graph.invoke({"question": query})
    return{
      "messages": [HumanMessage(content=response["response"])],
      "context": response["context"]
    }