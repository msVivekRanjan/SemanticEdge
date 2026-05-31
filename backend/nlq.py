import os
import json
from langchain_anthropic import ChatAnthropic
from langchain_core.messages import SystemMessage, HumanMessage
from dotenv import load_dotenv

load_dotenv()

ROUTER_PROMPT = """You are the AI brain for a privacy-first video surveillance system.
You receive natural language queries from security operators and must decide how to fetch the data.

You have three possible routing outputs:
1. "mongo": Use this for exact metadata matches, counts, or timeframe queries.
   (e.g., "How many unique persons?", "How many cars passed between 9am and 12pm?", "Any person in the entrance?")
2. "chroma": Use this for semantic visual/fuzzy searches WITH a specified time or date context.
   (e.g., "Did a white SUV pass by yesterday?", "Red backpack today", "Black color shirt male on October 14th")
3. "needs_date": Use this if the user asks for a semantic visual search but DOES NOT provide any temporal context (like a date, time, "today", "yesterday"). The database is too large to do unbounded semantic searches.
   (e.g., "person wearing blue shirt", "red backpack")

Respond ONLY with a JSON object.
Format for "mongo":
{"engine": "mongo", "pipeline": [<MongoDB Aggregation Pipeline Array>]}
Format for "chroma":
{"engine": "chroma", "search_text": "The exact visual description to search for"}
Format for "needs_date":
{"engine": "needs_date", "reason": "Please provide a specific date or time range to narrow down the search (e.g. 'yesterday', 'on Oct 14')."}

Events collection schema:
- cam_id (string)
- timestamp (ISO 8601 string, e.g. '2023-10-27T10:00:00Z')
- zone (string: 'entrance' or 'aisle')
- track_id (int)
- objects (array of dicts: {type: string, confidence: float, attributes: dict, bbox: [x,y,x,y]})
- frame_path (string)
"""

RESPONSE_PROMPT = """You are an AI surveillance assistant. 
You are given the operator's original question and the raw JSON results returned by the database.
Your job is to answer the operator's question in a clear, concise, and helpful natural language format.
Be brief. Highlight key details like timestamps, zones, and confidence scores. 
If the database results are empty, say so politely.
If there is a frame available, mention it (the bot will attach it automatically)."""

async def route_query(natural_language_query: str) -> dict:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return {"error": "ANTHROPIC_API_KEY not set"}

        llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            anthropic_api_key=api_key,
            temperature=0
        )
        
        messages = [
            SystemMessage(content=ROUTER_PROMPT),
            HumanMessage(content=natural_language_query)
        ]
        
        response = await llm.ainvoke(messages)
        content = response.content.strip()
        
        # Robust JSON extraction
        import re
        json_match = re.search(r'```json\s*(.*?)\s*```', content, re.DOTALL)
        if json_match:
            content = json_match.group(1)
        elif content.startswith("{") and content.endswith("}"):
            pass # Already JSON
        else:
            # Fallback string matching
            start_idx = content.find('{')
            end_idx = content.rfind('}')
            if start_idx != -1 and end_idx != -1:
                content = content[start_idx:end_idx+1]
                
        return json.loads(content.strip())
    except Exception as e:
        print(f"Failed to route query: {e}")
        return {"error": str(e)}

async def generate_response(query: str, db_results: list) -> str:
    try:
        api_key = os.getenv("ANTHROPIC_API_KEY")
        if not api_key:
            return str(db_results)

        llm = ChatAnthropic(
            model="claude-3-5-haiku-20241022",
            anthropic_api_key=api_key,
            temperature=0
        )
        
        context = f"Operator Question: {query}\n\nDatabase JSON Results:\n{json.dumps(db_results, indent=2)}"
        
        messages = [
            SystemMessage(content=RESPONSE_PROMPT),
            HumanMessage(content=context)
        ]
        
        response = await llm.ainvoke(messages)
        return response.content.strip()
    except Exception as e:
        print(f"Failed to generate natural response: {e}")
        return "Failed to generate a readable response from database results."
