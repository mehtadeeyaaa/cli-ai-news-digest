#the live HTTP server, this is its own file cuz the web server needs to keep running continuously 

from fastapi import FastAPI 
from datetime import datetime, timezone
import traceback
import aiosqlite
from db import DB_PATH  # same shared path mainio.py uses, so both files always agree on the DB location


# API endpoint to retrieve the daily digest of Hacker News stories, which are stored in a SQLite database. The endpoint queries the database for stories fetched on the current date and returns them as a list of dictionaries.
app = FastAPI(Title = "Hacker News Digest API")

#A helper to convert database into clean JSON format to get structured labeled data 
def row_to_dict(row):
    return {
        "id": row[0],
        "title": row[1],
        "url": row[2],
        "summary": row[3],
        "fetched_at": row[4]
    }

@app.get("/digest") #decorator to define the endpoint for retrieving the stories, it tells FastAPI that this function should be called when a GET request is made to the /digest URL.
async def get_digest():
    try:
        today = datetime.now(timezone.utc).date().isoformat()
        async with aiosqlite.connect(DB_PATH, timeout=10) as db:
            cursor = await db.execute(
                "SELECT id, title, url, summary, fetched_at FROM story WHERE date(fetched_at) = ? ORDER BY fetched_at DESC",(today,)

            ) 
            rows = await cursor.fetchall()
        return [row_to_dict(row) for row in rows]
    except Exception:
        traceback.print_exc()
        return {"error": "something went wrong, check server terminal"}
    
@app.get("/search")
async def search_stories(q: str):
    # Lets anyone search saved stories by keyword, the bonus deliverable (Deliverable 6)
    try:
        async with aiosqlite.connect(DB_PATH, timeout=10) as db:
            cursor = await db.execute(
                "SELECT id, title, url, summary, fetched_at FROM story WHERE title LIKE ? OR summary LIKE ? ORDER BY fetched_at DESC",
                (f"%{q}%", f"%{q}%")
            )
            rows = await cursor.fetchall()
        return [row_to_dict(r) for r in rows]
    except Exception:
        traceback.print_exc()
        return {"error": "something went wrong, check server terminal"}