# librarian

```bash
$ poetry run uvicorn asgi:app --reload
INFO: Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO: Started reloader process [10212]
INFO: Started server process [10216]
INFO: Waiting for application startup.
INFO: Tortoise-ORM startup
    connections: {'default': {'engine': 'tortoise.backends.sqlite', 'credentials': {'file_path': 'db.sqlite3'}}}
    apps: {'models': {'models': ['models'], 'default_connection': 'default'}}
```
