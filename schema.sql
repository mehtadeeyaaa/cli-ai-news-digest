--Deliverable 3
--just the table definitions for the database
--both mainio.py (the fetch/summarize pipeline) and api.py (the FastAPI app)
--rely on this same shape via db.py, instead of each defining it separately.

CREATE TABLE IF NOT EXISTS story(
    id INTEGER PRIMARY KEY,
    title TEXT NOT NULL,
    url TEXT NOT NULL,
    summary TEXT NOT NULL,
    fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
