from langgraph.graph import END
from langchain_core.messages import AnyMessage
from langgraph.graph.message import add_messages
from typing import Annotated
from typing_extensions import TypedDict
from utils.model import get_model
from utils.upc_validator import UPCValidatorTool, UPCCheckDigitCalculatorTool
# from utils.openfoodfacts_tool import OpenFoodFactsTool
from utils.rag_tool import rag_tool
from utils.usda_fdc_tool import USDAFoodDataCentralTool
from utils.extraction_tool import UPCExtractionTool
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
        system_message = """You are a UPC product information assistant with access to multiple specialized tools.

        TOOL USAGE DECISION TREE:

        1. WHEN TO USE upc_extraction tool:
          - User message contains ANY numbers that could potentially be UPC codes (8+ digits)
          - User asks about specific products, even without explicit UPC mention
          - User mentions "UPC", "barcode", "product code", or similar terms
          - Any product-related query where you suspect a UPC might be present
          - When in doubt about product identification, try extraction first

        2. WORKFLOW for UPC product queries:
          a) FIRST: Use upc_extraction tool to extract UPC and description from user input
             NOTE: The extraction tool is flexible and can handle diverse phrasings, word orders, and sentence structures
          b) IF extraction succeeds: Follow UPC validation and lookup workflow below
          c) IF extraction fails: Ask user to clarify or provide more specific product information

        3. UPC VALIDATION AND LOOKUP WORKFLOW (after successful extraction):
          a) Use upc_validator tool to validate the extracted UPC
          b) If invalid: Use upc_check_digit_calculator to fix the UPC, then revalidate
          c) Once valid: Use the rag tool to search the product knowledge base for information about the product THEN use ALL available database lookup tools:
              - openfoodfacts_lookup tool for OpenFoodFacts data
              - usda_fdc_search tool for USDA Food Data Central data
          d) DESCRIPTION COMPARISON AND VALIDATION:
              - Compare the user's extracted description with the actual product information from APIs
              - Look for matches in product name, brand, category, or ingredients
              - Flag any significant discrepancies between user description and actual product data
              - If description doesn't match, inform user and ask for confirmation
              - If description matches well, mention this as additional validation
          e) Use tavily_search_results_json for additional web research:
              - If product found in databases: Search with actual product name for supplementary info
              - If not found in databases: Search with UPC and user description

        4. WHEN NOT to use upc_extraction:
          - General questions about UPC theory/concepts ("How do UPCs work?")
          - Non-product related queries
          - Follow-up questions in an existing UPC conversation
          - User explicitly asks about UPC concepts rather than specific products

        5. RESPONSE FORMAT:
          - Always mention extraction confidence when applicable
          - Show your validation process (original UPC → corrected UPC if needed)
          - DESCRIPTION COMPARISON RESULTS:
            * If descriptions match: "✅ User description '{description}' matches the product data"
            * If descriptions don't match: "⚠️ User described '{user_description}' but product is actually '{actual_product}' - please confirm this is the intended product"
            * If partial match: "🔍 User description '{description}' partially matches - found related terms in [category/ingredients/brand]"
          - Clearly distinguish between OpenFoodFacts, USDA FDC, and web search data
          - If no UPC found, politely explain and offer to help with other product information needs

        EXAMPLES:

        ✅ Use extraction for (examples of flexible patterns):
        - "I need info on product 028400433303"
        - "What's in the chips with barcode 028400433303?"
        - "Nutrition facts for UPC 028400433303 please"
        - "I bought something with code 0-28400-43330-3"
        - "I have information about a product with the upc code 028400596008 and the description hot fries"
        - "Check out this 123456789012 cereal I bought"
        - "The cookies have barcode 987654321098"
        - "What product has UPC 555666777888?"
        - "Can you look up 028400123456 for me?"
        - "Tell me about the snacks with code 012345678901"

        ❌ Don't use extraction for:
        - "How do UPC codes work?"
        - "What's the weather?"
        - "Thanks for that info" (follow-up)
        - "Explain check digit calculation"

        DESCRIPTION COMPARISON EXAMPLES:

        Good match scenario:
        User: "I need info on UPC 028400433303 for Lay's potato chips"
        → Extract: UPC="028400433303", description="Lay's potato chips"
        → API result: "Lay's Classic Potato Chips"
        → Response: "✅ User description 'Lay's potato chips' matches the product data"

        Mismatch scenario:
        User: "Tell me about UPC 028400433303 for chocolate bars"
        → Extract: UPC="028400433303", description="chocolate bars"  
        → API result: "Lay's Classic Potato Chips"
        → Response: "⚠️ User described 'chocolate bars' but product is actually 'Lay's Classic Potato Chips' - please confirm this is the intended product"

        Partial match scenario:
        User: "Info on UPC 028400433303 for snack chips"
        → Extract: UPC="028400433303", description="snack chips"
        → API result: "Lay's Classic Potato Chips" 
        → Response: "🔍 User description 'snack chips' partially matches - found related terms in [category: snacks, product: chips]"

        Be helpful, thorough, and transparent about your process."""
                
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

# agent_graph = build_graph(model_name="claude-sonnet-4-20250514")