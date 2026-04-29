import os
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

SYSTEM_PROMPT = """You are a query translator. Convert the user's natural language question about surveillance events into a MongoDB filter dict. Events have fields: cam_id (string), timestamp (ISO string), zone (string: entrance or aisle), objects (array of objects with type, confidence). Return ONLY valid JSON dict, no explanation."""

async def query_to_filter(natural_language_query: str) -> dict:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            print("Warning: ANTHROPIC_API_KEY not set")
            return {}

        llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            anthropic_api_key=api_key,
            temperature=0
        )
        
        messages = [
            SystemMessage(content=SYSTEM_PROMPT),
            HumanMessage(content=natural_language_query)
        ]
        
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        if content.startswith("```json"):
            content = content[7:]
        if content.endswith("```"):
            content = content[:-3]
            
        return json.loads(content.strip())
        
    except Exception as e:
        print(f"Failed to parse NLQ to MongoDB filter: {e}")
        return {}

if __name__ == "__main__":
    import asyncio
    query = "Show me all people in the entrance zone"
    filter_dict = asyncio.run(query_to_filter(query))
    print(f"Query: {query}")
    print(f"Filter: {json.dumps(filter_dict, indent=2)}")
