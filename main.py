import os
import asyncio
import uvicorn
from fastapi import FastAPI
from langfuse import Langfuse
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from langchain_core.messages import SystemMessage, HumanMessage
from config.config import RequestObject
from MarketInsight.components.agent import agent
from MarketInsight.utils.tools import get_stock_price
from MarketInsight.utils.logger import get_logger

logger = get_logger(__name__)
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Update with your Vercel URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)


@app.get("/health")
async def health_check():
    """Health check endpoint for service monitoring and keep-alive pings"""
    return {"status": "ok", "message": "Service is running"}


@app.post("/api/chat")
async def chat(request: RequestObject):
    config = {'configurable': {'thread_id': request.threadId}}
    async def generate():
        try:
            prompt = request.prompt.content.strip()
            is_indian_market_overview = (
                "indian stock market" in prompt.lower()
                or ("nifty" in prompt.lower() and "sensex" in prompt.lower())
            )
            prefetched_market_data = ""
            prefetched_market_data = ""

            if is_indian_market_overview:
                yield "Fetching live NIFTY 50 and Sensex prices...\n\n"
                prices = await asyncio.gather(
                    asyncio.to_thread(get_stock_price.invoke, {"ticker": "^NSEI"}),
                    asyncio.to_thread(get_stock_price.invoke, {"ticker": "^BSESN"}),
                )
                yield (
                    f"NIFTY 50 (^NSEI): {prices[0]}\n"
                    f"Sensex (^BSESN): {prices[1]}\n\n"
                    "These live index values provide the current market snapshot. "
                    "Prices can change during the trading session, so use this as "
                    "informational market data rather than investment advice."
                )
                return

            # Create a span for the entire request
            with langfuse.start_as_current_observation(
                as_type="span", 
                name="chat-request",
                input=prompt
            ) as span:
                # Set user_id as metadata
                span.update(metadata={"user_id": request.threadId})
                
                # Create a nested generation for the LLM/agent call
                with langfuse.start_as_current_observation(
                    as_type="generation",
                    name="agent-stream",
                    model="agentic-workflow",
                    input=prompt
                ) as generation:
                    
                    full_response = ""
                    async for token, _ in agent.astream(
                        {
                            'messages': [
                                SystemMessage(content=(
                                    "You are a professional stock market analyst. "
                                    "Use only retrieved data and never fabricate values. "
                                    "For an Indian market overview, the backend has already "
                                    "called get_stock_price and supplied live values below. "
                                    "Do not call another tool for this request. "
                                    "Answer in under 200 words with the values and a brief caveat."
                                    f"{prefetched_market_data}"
                                )),
                                HumanMessage(content=prompt)
                            ]
                        },
                        stream_mode='messages',
                        config=config
                    ):
                        content = token.content
                        token_type = getattr(token, "type", "")
                        if (
                            token_type == "AIMessageChunk"
                            and isinstance(content, str)
                            and content
                        ):
                            full_response += content
                            yield content
                    
                    # Update generation with the complete output
                    generation.update(output=full_response)
                
                # Update span with completion status
                span.update(output="Request completed successfully")
                
        except Exception as e:
            logger.error(f"Error in chat: {e}")
            yield "I couldn't complete that analysis right now. Please try again in a moment."
    
    return StreamingResponse(generate(), media_type='text/event-stream',
        headers={
            'cache-control': 'no-cache, no-transform', 
            'connection': 'keep-alive'
        })

if __name__ == '__main__':
    logger.info("App Initiated Successfully")
    uvicorn.run(app, host='0.0.0.0', port=8000)