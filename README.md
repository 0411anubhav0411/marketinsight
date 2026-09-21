# Market Insight

An AI-powered stock market analysis platform that provides comprehensive financial data and intelligent insights through a conversational interface.

## Overview

Market Insight leverages advanced AI agents to deliver real-time stock market information, financial analysis, and investment insights. The platform combines the power of LangChain and OpenAI's language models with Yahoo Finance data to create an intelligent assistant for stock market research.

## Technology Stack

**Backend:**
- FastAPI for high-performance API endpoints
- LangChain & LangGraph for AI agent orchestration
- OpenAI GPT models for intelligent responses
- YFinance for financial data retrieval
- Langfuse for observability and tracing

**Frontend:**
- Modern React-based interface
- Real-time streaming responses
- Responsive design for all devices

## Getting Started

### Prerequisites
- Python 3.x
- Node.js (for frontend)
- Ollama (free local AI) or a compatible hosted AI provider

### Installation

1. Clone the repository
2. Install Python dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. For a free local setup, install Ollama, download a tool-capable model,
   and create `.env` from `.env.example`:
   ```bash
   ollama pull llama3.1:8b
   ```
   Keep `.env` local and never commit it. The default configuration uses
   Ollama at `http://localhost:11434/v1` and does not require an API key.

   For a deployed backend such as Render, use Ollama Cloud instead because
   a hosted server cannot access Ollama running on your computer. Set these
   environment variables in the hosting dashboard:
   ```
   AI_PROVIDER=ollama
   AI_MODEL=<an Ollama Cloud model>
   AI_BASE_URL=https://ollama.com/v1
   OLLAMA_API_KEY=<your Ollama API key>
   ```
4. Install frontend dependencies:
   ```bash
   cd frontend
   npm install
   ```
5. From the `MarketInsight` project directory, run the backend server:
   ```bash
   python main.py
   ```
6. Run the frontend development server:
   ```bash
   cd frontend
   npm run dev
   ```
7. Access the API at `http://localhost:8000` and frontend at `http://localhost:5173`

## Project Structure

```
MarketInsight/
├── components/     # AI agent configuration
├── utils/          # Tools and utilities
├── config/         # Configuration files
├── frontend/       # React frontend application
└── main.py         # FastAPI server entry point
```

## API Capabilities

The platform provides 16 specialized tools for comprehensive stock analysis:
- Stock price tracking
- Historical data analysis
- Financial statements (Balance Sheet, Income Statement, Cash Flow)
- Company information and ratios
- Dividend and split history
- Ownership and holder data
- Insider transactions
- Analyst recommendations
- Company ticker lookup