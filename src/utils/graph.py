from langgraph.graph import END
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict
from .model import get_model
from .upc_validator import UPCValidatorTool, UPCCheckDigitCalculatorTool
# from .openfoodfacts_tool import OpenFoodFactsTool
from .rag_tool import rag_tool
from .usda_fdc_tool import USDAFoodDataCentralTool
from .extraction_tool import UPCExtractionTool
from .prompts import get_upc_assistant_prompt
try:
    from langchain_tavily import TavilySearchResults
except ImportError:
    from langchain_community.tools.tavily_search import TavilySearchResults
from langgraph.prebuilt import ToolNode
from langgraph.graph import START, StateGraph
from IPython.display import Image, display
from langchain_core.messages import SystemMessage


def build_graph(model_name: str = 'claude-sonnet-4-20250514', display_graph: bool = False, debug_extraction: bool = False):
    # Initialize model first (needed for extraction tool)
    model = get_model(model_name)
    
    # Initialize tools
    tavily_tool = TavilySearchResults(max_results=5)
    upc_validator = UPCValidatorTool()
    upc_check_digit_calculator = UPCCheckDigitCalculatorTool()
    upc_extraction_tool = UPCExtractionTool(model=model, debug=debug_extraction)

    tool_belt = [
        upc_extraction_tool,  # Put extraction tool first for priority
        rag_tool,
        tavily_tool,
        upc_validator,
        upc_check_digit_calculator,
        # OpenFoodFactsTool(), # commenting out for RAG implementation
        USDAFoodDataCentralTool(),
    ]

    model = model.bind_tools(tool_belt)
    
    class GraphState(TypedDict):
        messages: Annotated[list[AnyMessage], add_messages]

    # Define the function that determines whether to continue or not
    def should_continue(state: GraphState):
        messages = state["messages"]
        last_message = messages[-1]
        if last_message.tool_calls:
            return "tools"
        return END

    # Node for handling all user requests
    def assistant(state: GraphState):
        messages = state["messages"]
        last_message = messages[-1]
        
        # Create a comprehensive system message for the UPC assistant
        system_message = get_upc_assistant_prompt()
                
        # Add the system message to the conversation
        system_msg = SystemMessage(content=system_message)
        enhanced_messages = [system_msg] + messages
        
        response = model.invoke(enhanced_messages)
        return {"messages": [response]}
  
    # Node
    tool_node = ToolNode(tool_belt)

    # Define a new graph for the agent
    builder = StateGraph(GraphState)

    # Define the two nodes we will cycle between
    builder.add_node("assistant", assistant)
    builder.add_node("tools", tool_node)

    # Set the entrypoint as `assistant`
    builder.add_edge(START, "assistant")

    # Making a conditional edge
    # should_continue will determine which node is called next.
    builder.add_conditional_edges("assistant", should_continue, ["tools", END])

    # Making a normal edge from `tools` to `assistant`.
    # The `assistant` node will be called after the `tool`.
    builder.add_edge("tools", "assistant")

    # Compile and display the graph for a visual overview
    react_graph = builder.compile()
    if display_graph:
        display(Image(react_graph.get_graph(xray=True).draw_mermaid_png()))
    return react_graph

# Lazy initialization - only build when API keys are available  
_agent_graph = None

def get_agent_graph():
    """Get or build the agent graph with lazy initialization"""
    global _agent_graph
    if _agent_graph is None:
        try:
            _agent_graph = build_graph(model_name="claude-sonnet-4-20250514")
        except Exception as e:
            print(f"⚠️ Agent graph initialization deferred: {e}")
            return None
    return _agent_graph

# For backward compatibility
agent_graph = None