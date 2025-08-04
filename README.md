# S.A.V.E. - Simple Autonomous Validation Engine
### AIE7 Certification Challenge

**S.A.V.E.** is a comprehensive AI-powered chatbot system designed for food data queries, UPC validation, and nutritional information lookup. This project demonstrates advanced AI agent capabilities, RAG (Retrieval Augmented Generation) systems, and multi-tool integration for intelligent food product analysis.

![Project Status](https://img.shields.io/badge/Status-Active-brightgreen)
![Python](https://img.shields.io/badge/Python-3.13%2B-blue)
![Node.js](https://img.shields.io/badge/Node.js-18%2B-green)
![FastAPI](https://img.shields.io/badge/FastAPI-Backend-teal)
![Next.js](https://img.shields.io/badge/Next.js-Frontend-black)

## 🎯 Project Overview

S.A.V.E. is a certification challenge prototype that showcases:

- **🤖 Intelligent AI Agent**: LangGraph-powered agent with specialized tools
- **🏷️ UPC Code Processing**: Extract, validate, and lookup product information
- **🥗 Nutritional Data**: Integration with USDA Food Data Central API
- **🔍 Advanced Search**: RAG-based product knowledge retrieval
- **🌐 Web Intelligence**: Tavily-powered web search capabilities
- **📊 Evaluation Framework**: RAGAS-based evaluation system

## 🏗️ Architecture

```
AIE7_Certification_Challenge/
├── src/
│   ├── api/              # FastAPI backend with agent integration
│   ├── frontend/         # Next.js React frontend
│   └── utils/            # Agentic system (LangGraph + tools)
├── data/                 # Product knowledge base (40+ products)
├── rag_data_generation/  # Tools for creating training data
├── evaluation/           # RAGAS evaluation framework
└── sample_notebooks/     # Example usage and demonstrations
```

## 🚀 Quick Start

### Prerequisites

- **Python 3.13+** and **uv** package manager
- **Node.js 18+** and **npm**
- **API Keys** from:
  - [OpenAI](https://platform.openai.com/api-keys) (embeddings)
  - [Anthropic](https://console.anthropic.com/settings/keys) (primary LLM)
  - [Tavily](https://tavily.com/) (web search)
  - [USDA FDC](https://api.nal.usda.gov/fdc/v1) (nutritional data)

### Installation & Setup

1. **Clone and navigate to project:**
   ```bash
   cd AIE7_Certification_Challenge
   ```

2. **Install uv (if not already installed):**
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. **Start the development environment:**
   ```bash
   chmod +x src/start_dev.sh
   ./src/start_dev.sh
   ```

4. **Access the application:**
   - 🎨 **Frontend**: http://localhost:3000
   - 📡 **API Backend**: http://localhost:8000
   - 📊 **API Documentation**: http://localhost:8000/docs

5. **Configure API Keys:**
   - The app will redirect you to setup page on first visit
   - Enter all required API keys (not stored permanently for security)
   - Click "Proceed to Chat"

## 💬 Usage Examples

### UPC Code Queries
```
"What are the ingredients for UPC 041548750927?"
"Validate UPC code 123456789012"
"Tell me about the nutrition facts for UPC 0-28400-43330-3"
```

### General Product Queries
```
"Tell me about Cheetos Flamin' Hot chips"
"What energy drinks do you know about?"
"Find products with high protein content"
"Compare the nutrition of different ice cream flavors"
```

### Nutritional Analysis
```
"What's the calorie content of corn chips?"
"Show me products with low sodium levels"
"Find organic certified products"
```

## 🤖 Agent Capabilities

The S.A.V.E. agent integrates multiple specialized tools:

| Tool | Purpose | Data Source |
|------|---------|-------------|
| **UPC Extraction** | Extract UPC codes from natural language | Built-in validation |
| **UPC Validator** | Validate format and check digits | Algorithm-based |
| **USDA FDC Tool** | Nutritional information lookup | USDA Food Data Central |
| **RAG Tool** | Product knowledge retrieval | Local vector database |
| **OpenFoodFacts Tool** | Product data enrichment | OpenFoodFacts API |
| **Tavily Search** | Web search for food information | Tavily Search API |

## 📊 Key Features

### 🔧 Technical Features
- **LangGraph Architecture**: Sophisticated agent workflow management
- **Vector Database**: Qdrant-powered RAG system with 40+ product documents
- **Streaming Responses**: Real-time chat with progress indicators
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Hot Reload**: Development environment with automatic code reloading

### 🍽️ Domain Features
- **UPC Code Processing**: Extract from text, validate format, calculate check digits
- **Nutritional Analysis**: Comprehensive nutrient information and comparisons
- **Ingredient Analysis**: Detailed ingredient breakdown and allergen identification
- **Product Discovery**: Intelligent search across multiple data sources
- **Quality Assessment**: OpenFoodFacts nutrition grades and certifications

## 📁 Project Components

### Data Generation (`rag_data_generation/`)
Tools for creating synthetic product documents from OpenFoodFacts API:
- Comprehensive product summaries
- RAG-optimized content structure
- Metadata generation for evaluation

### Evaluation Framework (`evaluation/`)
RAGAS-based evaluation system for RAG performance:
- Answer relevancy assessment
- Context precision and recall
- Faithfulness scoring
- Performance analytics

### Sample Data (`data/`)
40+ curated product summaries including:
- Ben & Jerry's ice cream varieties
- Energy drinks (Monster, Red Bull, Celsius)
- Snack foods (Cheetos, Lay's, Pringles)
- Cookies and treats (Oreo, Chips Ahoy)

## 🛠️ Development

### Manual Development Setup
```bash
# Backend (Terminal 1)
uv run python -m src.api.app

# Frontend (Terminal 2)  
cd src/frontend && npm run dev
```

### Running Evaluations
```bash
# Navigate to evaluation directory
cd evaluation

# Run Jupyter notebook
jupyter notebook Ragas_Evaluation.ipynb
```

### Generating New RAG Data
```bash
# Navigate to RAG generation directory
cd rag_data_generation

# Run the generator notebook
jupyter notebook generate_rag_data.ipynb
```

## 📋 API Endpoints

### Agent Endpoints
- `POST /api/agent/chat` - Main chat interface
- `POST /api/agent/chat/stream` - Streaming responses
- `GET /api/agent/capabilities` - Agent status and tools

### Utility Endpoints
- `POST /api/keys` - Configure API keys
- `GET /api/health` - System health check
- `POST /api/rag/query` - Direct RAG queries

## 🧪 Testing & Validation

### Manual Testing
1. Start both backend and frontend services
2. Access http://localhost:3000
3. Configure API keys through setup interface
4. Try example queries provided above
5. Monitor responses and tool usage

### API Testing
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

## 🔍 Troubleshooting

### Common Issues
- **"Agent not initialized"**: Verify all API keys are configured correctly
- **Empty responses**: Check that data files exist in `/data` directory  
- **Import errors**: Run `uv sync` to ensure dependencies are installed
- **Frontend connection issues**: Verify backend is running on port 8000

### Performance Tips
- Use the automated startup script for best experience
- API keys are validated on first use - check console for validation errors
- Large queries may take 10-30 seconds due to multiple tool calls

## 🔧 Technical Implementation

### Agent Tools Overview

**UPC Processing Tools**
- **UPC Extraction Tool**: Extracts UPC codes from natural language using regex patterns
- **UPC Validator Tool**: Implements UPC-A check digit calculation and format validation

**External API Integrations**
- **USDA FDC Tool**: Queries USDA Food Data Central for nutritional information
- **OpenFoodFacts Tool**: Retrieves comprehensive product information via UPC/barcode
- **Tavily Search Tool**: Performs intelligent web searches for food-related queries

**RAG System**
- **Vector Database**: Qdrant with OpenAI text-embedding-3-small
- **Collection**: 40+ product documents with metadata
- **Retrieval**: Top-k similarity search with score thresholds

### Frontend Technology Stack

- **Next.js 14** with App Router and TypeScript
- **React 18** with modern hooks and patterns
- **Tailwind CSS** for utility-first styling
- **Axios** for API communication with FastAPI backend

### API Endpoints Summary

- `POST /api/agent/chat` - Main chat interface with the agent
- `POST /api/keys` - Configure API keys dynamically
- `GET /api/agent/capabilities` - Get agent status and available tools
- `GET /api/health` - System health and connectivity check

## 📚 Documentation

For additional documentation:
- [`rag_data_generation/RAG_DOCUMENT_GENERATOR_README.md`](rag_data_generation/RAG_DOCUMENT_GENERATOR_README.md) - Data generation tools
- [`src/QUICK_START.md`](src/QUICK_START.md) - Detailed setup instructions

## 🤝 Contributing

This is a certification challenge project. Key areas for enhancement:
- Additional data sources and product categories
- Enhanced evaluation metrics and benchmarks
- Advanced agent capabilities and tool integration
- Performance optimization and caching
- User interface improvements

## 📄 License

This project is part of the AIE7 Certification Challenge. Please refer to course materials for licensing and usage guidelines.

---

**Built with ❤️ for the AIE7 Certification Challenge**

*S.A.V.E. demonstrates advanced AI agent capabilities, RAG systems, and modern web development practices in the food technology domain.*