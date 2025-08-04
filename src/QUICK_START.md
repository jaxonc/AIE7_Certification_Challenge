# 🚀 Quick Start Guide - S.A.V.E. (Simple Autonomous Validation Engine)

## Prerequisites

Before you begin, make sure you have:

### Required Software
- **Python 3.8+** (check with `python3 --version`)
- **Node.js 18+** (check with `node --version`)
- **npm** (usually comes with Node.js, check with `npm --version`)

### Required API Keys
You'll need API keys from these services:

1. **OpenAI** (for embeddings and some models)
   - Get yours at: https://platform.openai.com/api-keys
   - Format: `sk-...`

2. **Anthropic Claude** (primary AI model)
   - Get yours at: https://console.anthropic.com/settings/keys
   - Format: `sk-ant-...`

3. **Tavily** (web search)
   - Get yours at: https://tavily.com/
   - Format: `tvly-...`

4. **USDA Food Data Central** (nutritional data)
   - Get yours at: https://api.nal.usda.gov/fdc/v1
   - Format: alphanumeric key

## 🎯 Option 1: Quick Start (Automated with uv)

1. **Navigate to the project directory:**
   ```bash
   cd /path/to/AIE7_Certification_Challenge
   ```

2. **Make the startup script executable:**
   ```bash
   chmod +x src/start_dev.sh
   ```

3. **Run the automated startup:**
   ```bash
   ./src/start_dev.sh
   ```
   
   This will:
   - Check for uv installation
   - Create virtual environment if needed
   - Sync Python dependencies with uv (using pyproject.toml)
   - Install Node.js dependencies
   - Start both services

4. **Open your browser to:**
   - Frontend: http://localhost:3000
   - API Docs: http://localhost:8000/docs

5. **Configure API Keys:**
   - The app will automatically redirect you to the setup page
   - Enter all required API keys (fresh each time for security)
   - Click "Proceed to Chat"

> **Security Note:** API keys are never stored permanently and must be re-entered each session. This ensures your credentials are never persisted on disk.

> **Note:** The backend may show warnings about agent graphs until API keys are configured - this is normal!

## 🛠️ Option 2: Manual Start with uv

### Setup (First Time)

```bash
# Sync dependencies (creates venv and installs dependencies)
uv sync
```

### Option 2A: Manual with Helper Script

```bash
# First time: sync dependencies
uv sync

# Make script executable
chmod +x src/start_dev_manual.sh

# Run the helper script
./src/start_dev_manual.sh
```

### Option 2B: Completely Manual

**Step 1: Start the Backend**

```bash
# Start the FastAPI server with uv (from project root)
uv run python -m src.api.app
```

The backend will start on http://localhost:8000

**Step 2: Start the Frontend (New Terminal)**

```bash
# Navigate to frontend directory
cd src/frontend

# Install Node.js dependencies (first time only)
npm install

# Start the Next.js development server
npm run dev
```

The frontend will start on http://localhost:3000

## 📝 First Time Setup

1. **Open your browser to http://localhost:3000**

2. **You'll see the API Keys Setup page**

3. **Enter your API keys for all four services:**
   - OpenAI API Key
   - Anthropic Claude API Key
   - Tavily Search API Key
   - USDA Food Data Central API Key

4. **Click "Proceed to Chat"**

5. **Start chatting with the agent!**

## 💬 Example Queries to Try

Once you're in the chat interface, try these:

- `"What's are the ingredients for UPC 041548750927?"`
- `"Tell me about Cheetos Flamin' Hot chips"`
- `"Validate UPC code 123456789012"`
- `"Find products with high protein content"`
- `"What are the ingredients in energy drinks?"`

## 🔧 Troubleshooting

### "Directory not found" errors
- Make sure you're running the script from the project root directory
- The script looks for `src/api` and `src/frontend` directories

### uv specific issues
- **"uv not found"**: Install uv with `curl -LsSf https://astral.sh/uv/install.sh | sh`
- **"No module named pip"**: This is expected with uv, use the updated scripts
- **Virtual environment issues**: Try `rm -rf .venv && uv sync`

### Python dependency errors
- Make sure you have uv installed:
  ```bash
  # Install uv if not available
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```
- If virtual environment issues occur:
  ```bash
  # Remove and recreate virtual environment
  rm -rf .venv
  uv sync
  ```

### Node.js permission errors
- Try running with sudo (not recommended) or fix npm permissions:
  ```bash
  npm config set prefix ~/.npm-global
  export PATH=~/.npm-global/bin:$PATH
  ```

### API key errors
- Double-check that all your API keys are valid
- Make sure you've copied them completely (no extra spaces)
- Check that you have credits/quota remaining on each service

### Backend not responding
- Check if port 8000 is already in use
- Look at the terminal output for error messages
- Try restarting the backend process

### Frontend build errors
- Delete `node_modules` and `package-lock.json`, then run `npm install` again
- Check Node.js version compatibility

## 🏃‍♂️ Development Tips

- Both servers support hot reload - changes will be reflected automatically
- Check browser console (F12) for frontend errors
- Check terminal output for backend errors
- Use the API documentation at http://localhost:8000/docs to test endpoints directly

## 🛑 Stopping the Services

To stop both services:
- If using the automated script: Press `Ctrl+C`
- If running manually: Press `Ctrl+C` in each terminal window

## 📚 Next Steps

Once everything is running:
1. Explore the chat interface
2. Try different types of queries
3. Check out the agent capabilities in the UI
4. Review the API documentation
5. Examine the code in `src/utils/` to understand the agent system

---

**Need help?** Check the main README.md for comprehensive documentation, or refer to the RAG data generation tools documentation in `rag_data_generation/`.