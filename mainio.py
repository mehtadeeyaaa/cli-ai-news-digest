import aiohttp  #for async HTTP requests
import asyncio  #managing asynchronous tasks
import time  #for measuring elapsed time
import aiosqlite  #for async SQLite database operations
from datetime import datetime, timezone  #for handling date and time
from google import genai  #for interacting with Google GenAI API
from dotenv import load_dotenv
load_dotenv()

client = genai.Client()  #initializes Google GenAI client

#Fetching  story from Hacker News API

HN_API = "https://hacker-news.firebaseio.com/v0"  

async def fetch_story(session, story_id):
    async with session.get(f"{HN_API}/item/{story_id}.json") as response:  #sends a GET request to fetch story details
        return await response.json()  #awaits and parses the JSON response

async def fetch_story_limited(session, story_id, semaphore):
    async with semaphore:  #limits the number of concurrent requests
        story = await fetch_story(session, story_id)  #fetches the story details
        if story:
            return story
        return None
    
async def save_story(db, story):
    await db.execute(
        "INSERT OR REPLACE INTO story (id, title, url, summary, fetched_at) VALUES (?, ?, ?, ?, ?)",
        (story["id"], story.get("title"), story.get("url"), story.get("summary"), datetime.now(timezone.utc).isoformat())
    )

async def main():
    
    #Initialize database

    async with aiosqlite.connect("hn_stories.db", timeout=10) as db:  #opens SQLite database
         #runs SQL statement
        await db.execute("""       
            CREATE TABLE IF NOT EXISTS story (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                summary TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                    """)  #creates the story table if it doesn't exist
        await db.commit()  #commits the changes to the database

        #Fetch stories

        async with aiohttp.ClientSession() as session:  #creates a session
            # Fetch top story IDs
            async with session.get(f"{HN_API}/topstories.json") as response:  #sends a GET request to fetch top story IDs
                story_ids = await response.json()  #awaits and parses the JSON response 

            semaphore = asyncio.Semaphore(10)  #limits concurrent requests to 10
            tasks = [fetch_story_limited(session, sid, semaphore) for sid in story_ids[:20]] 
            stories = await asyncio.gather(*tasks)  #runs the tasks concurrently and waits for them to complete

        #Save stories to the database

        for story in stories:
            if story:
                story["summary"] = await generate_summary(client, story)
                await save_story(db, story)
                await asyncio.sleep(7)  # ~8-9 requests/minute, safely under the 10 RPM free-tier cap
        await db.commit()  #commits the changes to the database

        #Query and display stories
        cursor = await db.execute("SELECT id, title, url, summary, fetched_at FROM story ORDER BY fetched_at DESC LIMIT 5")  #executes a SQL query to fetch stories
        rows = await cursor.fetchall()  #fetches all rows from the query

        print(f"Saved {len([s for s in stories if s])} stories to the database. Top 5 by fetched_at:")  #prints the number of saved stories
        for row in rows:
            print(f" [{row[2]}] {row[1][:50]}")  #prints the story URL and title

async def generate_summary(client, story, retries=4):
    return f"Placeholder summary for: {story.get('title')}"  # TODO: swap back once quota issue is resolved

asyncio.run(main())  #runs the main function in the event loop