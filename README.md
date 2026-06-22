# CLI AI News Digest Tool

A FastAPI application that stores Hacker News stories in SQLite and provides endpoints to generate a digest and search saved stories.

## Run

```bash
uvicorn app.main:app --reload
```

## Sample Requests

```bash
curl http://127.0.0.1:8000/digest
```

```bash
curl "http://127.0.0.1:8000/search?q=Claude"
```