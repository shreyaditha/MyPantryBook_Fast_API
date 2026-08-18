# My Pantry Book — Quick Start

## Start the server

```powershell
cd "c:\Users\lenov\OneDrive\shreya\Projects\fast_api_pantry"
python -m uvicorn app.main:app --host 0.0.0.0 --port 8003
```

Then open in your browser:
**http://localhost:8003**

> If port 8003 is taken, use any free port — e.g. `--port 8010`

## Pages

| Page | URL |
|---|---|
| Home | http://localhost:8003/ |
| Pantry Shelf | http://localhost:8003/pantry |
| Recipe Book | http://localhost:8003/recipes |
| What Can I Cook? | http://localhost:8003/suggestions |
| Notifications | http://localhost:8003/notifications |
| API Docs | http://localhost:8003/docs |

## Re-seed recipes (if DB is empty)

```powershell
python -m seeds.seed_data
```
