import aiohttp  #for async HTTP requests
import asyncio  #managing asynchronous tasks
import time  #for measuring elapsed time
import aiosqlite  #for async SQLite database operations

#Fetching  headlines from Hacker News API

HN_API = "https://hacker-news.firebaseio.com/v0"  
async def fetch_story(session, story_id):
    async with session.get(f"{HN_API}/item/{story_id}.json") as response:  #sends a GET request to fetch story details
        return await response.json()  #awaits and parses the JSON response

async def main():
    async with aiohttp.ClientSession() as session:  #creates a session
        # Fetch top story IDs
        async with session.get(f"{HN_API}/topstories.json") as response:  #sends a GET request to fetch top story IDs
            headline_ids = await response.json()  #awaits and parses the JSON response 

#Fetching 20 headlines concurrently
        start = time.perf_counter()  #records the start time
        tasks = [fetch_story(session, story_id) for story_id in headline_ids[:20]]  #creates a list of tasks to fetch the first 20 stories
        stories = await asyncio.gather(*tasks)  #runs the tasks concurrently and waits for
        elapsed = time.perf_counter() - start  #calculates the elapsed time

        print(f"Concurrent: Fetched {len(stories)} stories in {elapsed:.2f} seconds.")
        print("\n Top 5 stories:")
        for story in stories[:5]:  #iterates through the first 5 stories
            print(f"  - {story.get('title', 'No Title')}")  #prints the title 

#Async Database Storage With aiosqlite

async def init_db():
    async with aiosqlite.connect(db_path) as db:  #connects to the SQLite database
        await db.execute("""
            CREATE TABLE IF NOT EXISTS headlines (
                id INTEGER PRIMARY KEY,
                title TEXT NOT NULL,
                url TEXT NOT NULL
                summary TEXT
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                         )
                    """)  #creates the headlines table if it doesn't exist
        await db.commit()  #commits the changes to the database

asyncio.run(main())  #runs the main function in the event loop