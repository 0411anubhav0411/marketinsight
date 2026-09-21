import os
from pathlib import Path
from dotenv import load_dotenv
from langchain_openai import ChatOpenAI
from MarketInsight.utils.tools import *
from MarketInsight.utils.logger import get_logger
from langgraph.checkpoint.memory import MemorySaver
from langchain.agents import create_agent


load_dotenv(Path(__file__).resolve().parents[2] / ".env")
logger = get_logger(__name__)

provider = os.getenv("AI_PROVIDER", "ollama").lower()
if provider == "ollama":
    model_name = os.getenv("AI_MODEL", "llama3.1:8b")
    base_url = os.getenv("AI_BASE_URL", "http://localhost:11434/v1")
    api_key = os.getenv("OLLAMA_API_KEY") or os.getenv("OPENAI_API_KEY") or "ollama"
else:
    model_name = os.getenv("AI_MODEL", "c1/openai/gpt-5/v-20250930")
    base_url = os.getenv("AI_BASE_URL", "https://api.thesys.dev/v1/embed/")
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError(
            "OPENAI_API_KEY is not set. Add it to the project .env file "
            "or set AI_PROVIDER=ollama to use a local model."
        )

model = ChatOpenAI(
    model=model_name,
    base_url=base_url,
    api_key=api_key,
    max_tokens=600,
)

agent = create_agent(
    model,
    tools = [get_stock_price, get_historical_data, get_stock_news, get_balance_sheet, get_income_statement, get_cash_flow,
            get_company_info, get_dividends, get_splits, get_institutional_holders, get_major_shareholders,
            get_mutual_fund_holders, get_insider_transactions, get_analyst_recommendations, get_analyst_recommendations_summary, get_ticker],
    checkpointer = MemorySaver()
)

logger.info("Agent Initiated Successfully")