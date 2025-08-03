# S.A.V.E. Frontend

A modern React/Next.js frontend for the S.A.V.E. (Simple Autonomous Validation Engine) chatbot system.

## Features

- 🤖 Interactive chat interface with the AI agent
- 🏷️ UPC code validation and product lookup
- 📊 Nutritional information display
- 🔍 Product search capabilities
- 📱 Responsive design with Tailwind CSS
- ⚡ Real-time messaging with the FastAPI backend

## Getting Started

### Prerequisites

- Node.js 18+ and npm
- The FastAPI backend running on `http://localhost:8000`

### Installation

1. Install dependencies:
```bash
npm install
```

2. Start the development server:
```bash
npm run dev
```

3. Open [http://localhost:3000](http://localhost:3000) in your browser

### Build for Production

```bash
npm run build
npm start
```

## Usage

1. Open the chat interface
2. Type questions about food products, UPC codes, or nutritional information
3. The agent will respond using its integrated tools:
   - UPC validation and extraction
   - USDA Food Data Central lookup
   - RAG-based product knowledge
   - Web search capabilities

### Example Queries

- "What's the nutrition info for UPC 028400596008?"
- "Tell me about Cheetos Flamin' Hot"
- "Validate UPC code 123456789012"
- "Find products with high protein content"

## Architecture

- **Next.js 14** with App Router
- **React 18** with TypeScript
- **Tailwind CSS** for styling
- **Axios** for API communication
- **Lucide React** for icons

## API Integration

The frontend communicates with the FastAPI backend through these endpoints:

- `POST /api/agent/chat` - Main chat with the agent
- `GET /api/agent/capabilities` - Get agent capabilities
- `GET /api/health` - Health check

## Configuration

The `next.config.js` file is configured to proxy API requests to the FastAPI backend running on port 8000.

## Development

To add new features:

1. Create components in the `components/` directory
2. Add new pages in the `app/` directory
3. Update the API integration in the main page component
4. Style with Tailwind CSS classes