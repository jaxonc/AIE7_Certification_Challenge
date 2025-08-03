# Food Data Agent - Complete Web Application

A comprehensive AI-powered chatbot system for food data queries, UPC validation, and nutritional information lookup. This application integrates multiple tools and data sources to provide intelligent responses about food products.

## 🏗️ Architecture

```
src/
├── api/           # FastAPI backend with agent integration
├── frontend/      # Next.js React frontend
└── utils/         # Agentic system (LangGraph + tools)
```

## 🤖 Agent Capabilities

The system includes a sophisticated multi-tool agent that can:

- **UPC Code Processing**: Extract, validate, and calculate check digits for UPC codes
- **Product Database Lookup**: Query USDA Food Data Central for nutritional information
- **RAG System**: Use vector search on product knowledge base
- **Web Search**: Perform intelligent web searches for food information
- **Conversation**: Maintain context across multiple exchanges

### Available Tools

1. **UPC Extraction Tool**: Extracts UPC codes from natural language
2. **UPC Validator Tool**: Validates UPC code format and check digits
3. **UPC Check Digit Calculator**: Calculates proper check digits
4. **USDA FDC Tool**: Queries USDA Food Data Central API
5. **RAG Tool**: Vector-based product information retrieval
6. **Tavily Search Tool**: Web search for food-related queries

## 🚀 Quick Start

### Prerequisites

- Python 3.8+
- Node.js 18+
- npm or yarn
- API Keys for:
  - OpenAI (for embeddings and some models)
  - Anthropic Claude (primary LLM)
  - Tavily (web search)

### Environment Setup

1. **Set API Keys** (create a `.env` file in the project root):
```bash
OPENAI_API_KEY=your-openai-api-key
ANTHROPIC_API_KEY=your-anthropic-api-key
TAVILY_API_KEY=your-tavily-api-key
```

2. **Install Backend Dependencies**:
```bash
cd src/api
pip install -r requirements.txt
```

3. **Install Frontend Dependencies**:
```bash
cd src/frontend
npm install
```

### Running the Application

#### Option 1: Manual Start

**Terminal 1 - Backend:**
```bash
cd src/api
python app.py
```

**Terminal 2 - Frontend:**
```bash
cd src/frontend
npm run dev
```

#### Option 2: Automated Start (Recommended)

```bash
# From project root
./src/start_dev.sh
```

### Access Points

- 🎨 **Frontend**: http://localhost:3000
- 📡 **API Backend**: http://localhost:8000
- 📊 **API Documentation**: http://localhost:8000/docs

## 🛠️ API Endpoints

### Agent Endpoints

- `POST /api/agent/chat` - Main chat interface with the agent
- `POST /api/agent/chat/stream` - Streaming chat responses
- `GET /api/agent/capabilities` - Get agent capabilities and status

### RAG Endpoints

- `POST /api/rag/query` - Direct RAG queries with context

### Utility Endpoints

- `GET /api/health` - System health check
- `POST /api/chat` - Legacy OpenAI chat endpoint

## 💬 Usage Examples

### UPC Code Queries
```
"What's the nutrition info for UPC 028400596008?"
"Validate UPC code 123456789012"
"I have a product with UPC 0-28400-43330-3, tell me about it"
```

### General Product Queries
```
"Tell me about Cheetos Flamin' Hot chips"
"What are the ingredients in energy drinks?"
"Find products with high protein content"
```

### Nutritional Information
```
"What's the calorie content of corn chips?"
"Show me the sodium levels in different snacks"
"Compare the nutrition of different energy drinks"
```

## 🔧 Configuration

### Backend Configuration

The FastAPI app (`src/api/app.py`) includes:
- CORS middleware for frontend communication
- Agent graph initialization
- Error handling and logging
- Session management

### Frontend Configuration

The Next.js app (`src/frontend/`) features:
- TypeScript for type safety
- Tailwind CSS for styling
- Responsive design
- Real-time chat interface
- API proxy configuration

### Agent Configuration

The agent system (`src/utils/`) supports:
- Model selection (Claude Sonnet, GPT models)
- Tool configuration and priority
- RAG system with Qdrant vector store
- Prompt customization

## 🧪 Testing

### Manual Testing

1. Start both backend and frontend
2. Open http://localhost:3000
3. Try the example queries above
4. Check the API documentation at http://localhost:8000/docs

### API Testing

Test endpoints directly:

```bash
# Health check
curl http://localhost:8000/api/health

# Agent capabilities
curl http://localhost:8000/api/agent/capabilities

# Chat with agent
curl -X POST http://localhost:8000/api/agent/chat \
  -H "Content-Type: application/json" \
  -d '{"message": "What is UPC 028400596008?"}'
```

## 🐛 Troubleshooting

### Common Issues

1. **Agent not initialized**: Check API keys are set correctly
2. **Import errors**: Ensure all dependencies are installed
3. **Frontend API calls failing**: Verify backend is running on port 8000
4. **Empty responses**: Check that data files exist in `/data` directory

### Logs and Debugging

- Backend logs appear in the terminal running the API
- Frontend logs appear in browser console
- Enable debug mode in agent graph for detailed tool execution logs

## 📁 Data Sources

The system uses:
- Product summaries in `/data/*.txt` files for RAG
- USDA Food Data Central API for nutritional data
- Tavily for web search capabilities
- OpenAI embeddings for vector search

## 🔄 Development Workflow

1. Make changes to backend or frontend code
2. Services will auto-reload (FastAPI and Next.js both support hot reload)
3. Test changes in the frontend interface
4. Use API docs at `/docs` for direct API testing

## 📚 Next Steps

Potential enhancements:
- Add user authentication and session persistence
- Implement conversation memory across sessions
- Add support for image uploads (product photos)
- Integrate barcode scanning functionality
- Add export capabilities for nutritional data
- Implement rate limiting and caching

---

For detailed documentation on individual components, see:
- `src/api/README.md` - Backend documentation
- `src/frontend/README.md` - Frontend documentation
- `src/utils/` - Agent system code and tools