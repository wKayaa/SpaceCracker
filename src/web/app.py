from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import asyncio
import json
from typing import List, Dict, Any

app = FastAPI(title="SpaceCracker V2 Web Interface")

# Mount static files and templates
app.mount("/static", StaticFiles(directory="src/web/static"), name="static")
templates = Jinja2Templates(directory="src/web/templates")

# Active WebSocket connections
active_connections: List[WebSocket] = []

class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)

    async def broadcast(self, message: str):
        for connection in self.active_connections:
            try:
                await connection.send_text(message)
            except:
                # Remove dead connections
                self.active_connections.remove(connection)

manager = ConnectionManager()

@app.get("/", response_class=HTMLResponse)
async def dashboard(request):
    """Main dashboard"""
    return templates.TemplateResponse("dashboard.html", {"request": request})

@app.get("/api/stats")
async def get_stats():
    """Get current statistics"""
    # This would integrate with the StatsManager
    return {
        "hits": 0,
        "checked_urls": 0,
        "threads": 5000,
        "status": "idle"
    }

@app.post("/api/scan/start")
async def start_scan(scan_config: Dict[str, Any]):
    """Start a new scan"""
    # This would integrate with the Orchestrator
    return {"status": "started", "scan_id": "12345"}

@app.post("/api/scan/stop")
async def stop_scan():
    """Stop current scan"""
    return {"status": "stopped"}

@app.get("/api/results")
async def get_results():
    """Get scan results"""
    # This would return actual results from the database
    return {"results": []}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send periodic updates
            stats = {
                "type": "stats_update",
                "data": {
                    "hits": 0,
                    "checked_urls": 0,
                    "threads": 5000,
                    "status": "running"
                }
            }
            await manager.send_personal_message(json.dumps(stats), websocket)
            await asyncio.sleep(1)
    except WebSocketDisconnect:
        manager.disconnect(websocket)