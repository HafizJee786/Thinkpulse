from fastapi import FastAPI, Request, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from contextlib import asynccontextmanager
import json
import os
from datetime import datetime
from agent import research_topic


# ── History Storage ───────────────────────────────────────
HISTORY_FILE = "research_history.json"

def load_history():
    if os.path.exists(HISTORY_FILE):
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def save_history(history):
    with open(HISTORY_FILE, "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

# ── App Setup ─────────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("AI Research Assistant API is starting...")
    yield

app = FastAPI(
    title="AI Research Assistant API",
    description="Automatically research any topic using AI and web search",
    version="1.0.0",
    lifespan=lifespan
)

# ── Middleware ────────────────────────────────────────────
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ── Static & Templates ────────────────────────────────────
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# ── Routes ────────────────────────────────────────────────

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse(request, "index.html")


@app.get("/health")
def health():
    return {"status": "AI Research Assistant is running!", "version": "1.0.0"}


@app.post("/research")
async def research(
    topic: str = Form(...),
    depth: str = Form(default="standard")
):
    try:
        if not topic.strip():
            return JSONResponse(
                status_code=400,
                content={"error": "Topic cannot be empty"}
            )

        # Run research
        result = research_topic(topic.strip(), depth)

        # Save to history
        history = load_history()
        history_entry = {
            "id": len(history) + 1,
            "topic": topic.strip(),
            "depth": depth,
            "report": result["report"],
            "status": result["status"],
            "timestamp": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }
        history.insert(0, history_entry)

        # Keep only last 20 searches
        history = history[:20]
        save_history(history)

        return {
            "topic": topic.strip(),
            "depth": depth,
            "report": result["report"],
            "status": result["status"],
            "timestamp": history_entry["timestamp"]
        }

    except Exception as e:
        return JSONResponse(
            status_code=500,
            content={"error": str(e)}
        )


@app.get("/history")
def get_history():
    history = load_history()
    return {
        "total": len(history),
        "history": history
    }


@app.delete("/history")
def clear_history():
    save_history([])
    return {"message": "History cleared successfully"}


@app.get("/history/{item_id}")
def get_history_item(item_id: int):
    history = load_history()
    item = next((h for h in history if h["id"] == item_id), None)
    if not item:
        return JSONResponse(
            status_code=404,
            content={"error": "History item not found"}
        )
    return item
