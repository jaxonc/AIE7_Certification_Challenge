# Import required FastAPI components for building the API
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
# Import Pydantic for data validation and settings management
from pydantic import BaseModel
# Import OpenAI client for interacting with OpenAI's API
from openai import OpenAI
import os
import sys
import asyncio
from typing import Optional, List, Dict, Any
from langchain_core.messages import HumanMessage

# Add the src directory to the path so we can import our agentic system
src_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, src_path)

try:
    from utils.graph import get_agent_graph
    from utils.rag_graph import get_rag_graph
    print("✅ Successfully imported agent graph builders")
except ImportError as e:
    print(f"❌ Failed to import agent graph builders: {e}")
    # Fallback imports if the above doesn't work
    utils_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'utils'))
    sys.path.insert(0, utils_path)
    try:
        from graph import get_agent_graph
        from rag_graph import get_rag_graph
        print("✅ Successfully imported agent graph builders (fallback)")
    except ImportError as e2:
        print(f"❌ Fallback import also failed: {e2}")
        get_agent_graph = lambda: None
        get_rag_graph = lambda: None

# Initialize FastAPI application with a title
app = FastAPI(title="Food Data Agent API")

# Configure CORS (Cross-Origin Resource Sharing) middleware
# This allows the API to be accessed from different domains/origins
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows requests from any origin
    allow_credentials=True,  # Allows cookies to be included in requests
    allow_methods=["*"],  # Allows all HTTP methods (GET, POST, etc.)
    allow_headers=["*"],  # Allows all headers in requests
)

# Agent graphs will be built lazily when API keys are configured
main_agent = None
rag_agent = None

def initialize_agents():
    """Initialize agent graphs when API keys are available"""
    global main_agent, rag_agent
    try:
        print("🔄 Initializing agent graphs...")
        main_agent = get_agent_graph()
        rag_agent = get_rag_graph()
        
        if main_agent and rag_agent:
            print("✅ All agent graphs initialized successfully")
            return True
        else:
            print("⚠️ Some agent graphs failed to initialize")
            return False
    except Exception as e:
        print(f"❌ Failed to initialize agent graphs: {e}")
        main_agent = None
        rag_agent = None
        return False

print("ℹ️ Agent graphs will be initialized when API keys are configured")

# Define the data model for chat requests using Pydantic
# This ensures incoming request data is properly validated
class ChatRequest(BaseModel):
    developer_message: str  # Message from the developer/system
    user_message: str      # Message from the user
    model: Optional[str] = "gpt-4.1-mini"  # Optional model selection with default
    api_key: str          # OpenAI API key for authentication

# Define data model for agent chat requests
class AgentChatRequest(BaseModel):
    message: str  # User message to send to the agent
    session_id: Optional[str] = None  # Optional session ID for conversation tracking

# Define data model for RAG requests
class RAGRequest(BaseModel):
    question: str  # Question to ask the RAG system

# Define response models
class AgentResponse(BaseModel):
    response: str
    session_id: Optional[str] = None

class RAGResponse(BaseModel):
    response: str
    context: List[Dict[str, Any]]  # Context documents used for the response

# Define API keys configuration model
class ApiKeysRequest(BaseModel):
    openai_api_key: str
    anthropic_api_key: str
    tavily_api_key: str
    usda_api_key: str

# Define the main chat endpoint that handles POST requests
@app.post("/api/chat")
async def chat(request: ChatRequest):
    try:
        # Initialize OpenAI client with the provided API key
        client = OpenAI(api_key=request.api_key)
        
        # Create an async generator function for streaming responses
        async def generate():
            # Create a streaming chat completion request
            stream = client.chat.completions.create(
                model=request.model,
                messages=[
                    {"role": "developer", "content": request.developer_message},
                    {"role": "user", "content": request.user_message}
                ],
                stream=True  # Enable streaming response
            )
            
            # Yield each chunk of the response as it becomes available
            for chunk in stream:
                if chunk.choices[0].delta.content is not None:
                    yield chunk.choices[0].delta.content

        # Return a streaming response to the client
        return StreamingResponse(generate(), media_type="text/plain")
    
    except Exception as e:
        # Handle any errors that occur during processing
        raise HTTPException(status_code=500, detail=str(e))

# New agent chat endpoint that uses the agentic system
@app.post("/api/agent/chat", response_model=AgentResponse)
async def agent_chat(request: AgentChatRequest):
    """
    Chat with the intelligent food data agent that can:
    - Extract and validate UPC codes
    - Search product databases (USDA FDC)
    - Perform web searches for food information
    - Use RAG for product knowledge
    """
    if main_agent is None:
        raise HTTPException(status_code=500, detail="Agent system not initialized")
    
    try:
        # Create a human message from the user input
        user_message = HumanMessage(content=request.message)
        
        # Invoke the agent with the message
        result = main_agent.invoke({"messages": [user_message]})
        
        # Extract the response from the agent's output
        agent_response = result["messages"][-1].content if result["messages"] else "No response generated"
        
        return AgentResponse(
            response=agent_response,
            session_id=request.session_id
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Agent error: {str(e)}")

# RAG endpoint for product information queries
@app.post("/api/rag/query", response_model=RAGResponse)
async def rag_query(request: RAGRequest):
    """
    Query the RAG system for product information using vector search
    """
    if rag_agent is None:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        # Invoke the RAG agent with the question
        result = rag_agent.invoke({"question": request.question})
        
        # Format context documents for response
        context_docs = []
        if "context" in result:
            for doc in result["context"]:
                context_docs.append({
                    "content": doc.page_content,
                    "metadata": doc.metadata
                })
        
        return RAGResponse(
            response=result.get("response", "No response generated"),
            context=context_docs
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"RAG error: {str(e)}")

# Streaming agent chat endpoint
@app.post("/api/agent/chat/stream")
async def agent_chat_stream(request: AgentChatRequest):
    """
    Streaming version of agent chat for real-time responses
    """
    if main_agent is None:
        raise HTTPException(status_code=500, detail="Agent system not initialized")
    
    async def generate():
        try:
            # Create a human message from the user input
            user_message = HumanMessage(content=request.message)
            
            # For streaming, we'll invoke the agent and yield the response
            # Note: LangGraph doesn't have built-in streaming, so we simulate it
            result = main_agent.invoke({"messages": [user_message]})
            agent_response = result["messages"][-1].content if result["messages"] else "No response generated"
            
            # Simulate streaming by yielding chunks
            words = agent_response.split()
            for i, word in enumerate(words):
                if i > 0:
                    yield " "
                yield word
                # Add a small delay to simulate streaming
                await asyncio.sleep(0.05)
                
        except Exception as e:
            yield f"Error: {str(e)}"
    
    return StreamingResponse(generate(), media_type="text/plain")

# Get agent capabilities endpoint
@app.get("/api/agent/capabilities")
async def get_agent_capabilities():
    """
    Get information about what the agent can do
    """
    return {
        "capabilities": [
            "UPC code extraction and validation",
            "USDA Food Data Central integration",
            "Web search for food information",
            "Product knowledge via RAG",
            "Nutritional data lookup",
            "Product comparison and analysis"
        ],
        "tools": [
            "UPC Extraction Tool",
            "UPC Validator Tool", 
            "UPC Check Digit Calculator",
            "USDA FDC Tool",
            "Tavily Search Tool",
            "RAG Tool"
        ],
        "status": "online" if main_agent is not None else "offline"
    }

# API Keys configuration endpoint
@app.post("/api/configure-keys")
async def configure_api_keys(request: ApiKeysRequest):
    """
    Configure API keys for the session and initialize agents
    """
    global main_agent, rag_agent
    try:
        # Set environment variables for this process
        os.environ["OPENAI_API_KEY"] = request.openai_api_key
        os.environ["ANTHROPIC_API_KEY"] = request.anthropic_api_key
        os.environ["TAVILY_API_KEY"] = request.tavily_api_key
        os.environ["USDA_API_KEY"] = request.usda_api_key
        
        # Initialize agent graphs now that API keys are available
        success = initialize_agents()
        
        return {
            "status": "success" if success else "partial",
            "message": "API keys configured and agents initialized" if success else "API keys configured but some agents failed to initialize",
            "agents_ready": success
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to configure API keys: {str(e)}")

# Define a health check endpoint to verify API status
@app.get("/api/health")
async def health_check():
    # Check which API keys are configured
    keys_status = {
        "openai": bool(os.environ.get("OPENAI_API_KEY")),
        "anthropic": bool(os.environ.get("ANTHROPIC_API_KEY")),
        "tavily": bool(os.environ.get("TAVILY_API_KEY")),
        "usda": bool(os.environ.get("USDA_API_KEY"))
    }
    
    return {
        "status": "ok",
        "agent_status": "online" if main_agent is not None else "offline",
        "rag_status": "online" if rag_agent is not None else "offline",
        "api_keys_configured": keys_status
    }

# Entry point for running the application directly
if __name__ == "__main__":
    import uvicorn
    # Start the server on all network interfaces (0.0.0.0) on port 8000
    uvicorn.run(app, host="0.0.0.0", port=8000)
