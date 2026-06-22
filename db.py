#knows where the database is located and applies the 
#This exists so both mainio.py and api.py can import the same DB_PATH variable

import aiosqlite


DB_PATH = "hn_stories.db"  # Path to the SQLite database file
SCHEMA_PATH = "schema.sql"  # Path to the SQL schema file

async def init_db():
    """Applies schema.sql to the database, it makes
    sure the table exists before anything else touches it.
    This is migration, basically run this is how to we set up brand, new 
    database from scratch."""

    async with aiosqlite.connect(DB_PATH) as db:
        with open(SCHEMA_PATH, "r") as f:
            schema_sql = f.read()
        await db.executescript(schema_sql)
        await db.commit()  # Commit the changes to the database

if __name__ == "__main__":
    # Lets us run `python db.py` directly to set up the database
    # without needing to run mainio.py's full fetch/summarize pipeline first.
    import asyncio
    asyncio.run(init_db())  # Run the init_db function to initialize the database when this script is executed directly
    print(f"Schema applied to {DB_PATH}.")