#script that fetches HN stories, summarizes them via AI and saves them.

import aiohttp  #for async HTTP requests
import asyncio  #managing asynchronous tasks
import aiosqlite  #for async SQLite database operations
from datetime import datetime, timezone  #for handling date and time
from dotenv import load_dotenv  #loads our API key from .env so it can never lives int his code
from openai import AsyncOpenAI 
import os
from db import init_db, DB_PATH

load_dotenv()

# Client for calling the AI summarizer through OpenRouter (Deliverable 3)
# timeout=15 stops a single hung request from freezing the whole script forever

client = AsyncOpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=os.getenv("OPENROUTER_API_KEY"),
    timeout = 15.0 # 15 second timeout
)

#Fetching story from Hacker News API

HN_API = "https://hacker-news.firebaseio.com/v0"  

async def fetch_story(session, story_id):
    async with session.get(f"{HN_API}/item/{story_id}.json") as response:  #sends a GET request to fetch story details
        return await response.json()  #awaits and parses the JSON response

#fetches one story but rate-limited
async def fetch_story_limited(session, story_id, semaphore):
    async with semaphore:  #limits the number of concurrent requests
        return await fetch_story(session, story_id)
    
async def save_story(db, story):
    # Writes one story into SQLite with the exact schema the project asked for (Deliverable 2)
    # INSERT OR REPLACE means re-running this won't crash on duplicate HN ids
    await db.execute(
        "INSERT OR REPLACE INTO story (id, title, url, summary, fetched_at) VALUES (?, ?, ?, ?, ?)",
        (story["id"], story.get("title"), story.get("url"), story.get("summary"), datetime.now(timezone.utc).isoformat())
    )
    
#generates the summary
async def generate_summary(client, story, retries=4):
    #Generates a summary for the given story using the OpenAI API, with retry logic for handling transient errors.
    for attempt in range(retries):
        try:
            response = await client.chat.completions.create(
                model="openai/gpt-4o-mini",  # or any model slug from openrouter.ai/models
                messages=[
                    {"role": "user", "content": f"Summarize the following news story in two sentences: {story.get('title')}"}
                ]
            )
            return response.choices[0].message.content
        except Exception as e:
            if attempt == retries - 1:
                print(f"Failed to summarize story {story.get('id')}: {e}")
                return None
            await asyncio.sleep(2 ** attempt)

async def refresh_digest():
    # Main entry point: fetch -> summarize -> store, the whole pipeline in one place
    await init_db()  #applies schema.sql
    
    async with aiosqlite.connect(DB_PATH, timeout=10) as db:
    
    # timeout on the session so a slow/dead HN API fails loudly instead of hanging forever
        timeout = aiohttp.ClientTimeout(total=15)  #sets a total timeout of 15 seconds for HTTP requests    
        async with aiohttp.ClientSession(timeout=timeout) as session:  #creates a session
            # Fetch top story IDs
            async with session.get(f"{HN_API}/topstories.json") as response:  #sends a GET request to fetch top story IDs
                story_ids = await response.json()  #awaits and parses the JSON response 

            #Fetches the forst 20 stories
            semaphore = asyncio.Semaphore(10)  #limits concurrent requests to 10
            tasks = [fetch_story_limited(session, sid, semaphore) for sid in story_ids[:20]] 
            stories = await asyncio.gather(*tasks)  #runs the tasks concurrently and waits for them to complete

        #Summarize and Save stories to the database

        for story in stories:
            if story:
                story["summary"] = await generate_summary(client, story)
                await save_story(db, story)
                await asyncio.sleep(7)  # ~8-9 requests/minute, safely under the 10 RPM free-tier cap
        await db.commit()  #commits the changes to the database

        # Just a sanity-check print so we can see something happened without manually querying the DB
        cursor = await db.execute("SELECT id, title, url, summary, fetched_at FROM story ORDER BY fetched_at DESC LIMIT 5")  #executes a SQL query to fetch stories
        rows = await cursor.fetchall()  #fetches all rows from the query

        print(f"Saved {len([s for s in stories if s])} stories to the database. Top 5 by fetched_at:")  #prints the number of saved stories
        for row in rows:
            print(f" [{row[2]}] {row[1][:50]}")  #prints the story URL and title


if __name__ == "__main__":
    #only runs when this file is executed directly 
    asyncio.run(refresh_digest())  #runs the refresh_digest function asynchronously

        