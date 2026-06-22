#test /digest and /search without needing real HN data or AI working key
#this is "seed script"- fake but realistic 

import asyncio
from datetime import datetime, timezone
import aiosqlite
from db import init_db, DB_PATH

# A handful of fake stories for testing the FastAPI endpoints (/digest, /search)
# without needing to hit Hacker News or burn AI API quota every time.

SAMPLE_STORIES = [
    {
        "id": 1000001,
        "title": "Show HN: A tiny async task scheduler",
        "url": "https://example.com/async-scheduler",
        "summary": "A developer built a lightweight async task scheduler for Python projects needing simple periodic jobs. It avoids heavier dependencies by relying only on asyncio's built-in primitives.",
    },
    {
        "id": 1000002,
        "title": "Why SQLite is enough for most side projects",
        "url": "https://example.com/sqlite-is-enough",
        "summary": "The article argues that SQLite handles the read/write load of most small to medium projects without needing a dedicated database server. It highlights simplicity and zero-configuration as key advantages for solo developers.",
    },
    {
        "id": 1000003,
        "title": "An open-source AI summarizer for newsletters",
        "url": "https://example.com/ai-newsletter-summarizer",
        "summary": "A new open-source tool automatically condenses long newsletters into short, readable summaries using an LLM API. The project is aimed at people who subscribe to too many newsletters to read in full.",
    },
]

async def seed():
    await init_db()  # Ensure the database schema is applied before inserting data
    async with aiosqlite.connect(DB_PATH, timeout=10) as db:
        for story in SAMPLE_STORIES:
            await db.execute(
                "INSERT OR REPLACE INTO story (id, title, url, summary, fetched_at) VALUES (?, ?, ?, ?, ?)",
                (story["id"], story["title"], story["url"], story["summary"], datetime.now(timezone.utc).isoformat())
            )
        await db.commit()  # Commit the changes to the database
    print(f"Seeded {len(SAMPLE_STORIES)} sample stories into {DB_PATH}.")

if __name__ == "__main__":
    asyncio.run(seed())  # Run the seed function to populate the database with sample stories when this script is executed directly