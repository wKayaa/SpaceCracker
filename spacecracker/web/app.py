#!/usr/bin/env python3
"""
SpaceCracker V2 - Web Panel Application
FastAPI application with real-time WebSocket updates
"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Request
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
import json
import asyncio
import time
from typing import List, Dict, Any
from pathlib import Path

# Get the directory of this file
current_dir = Path(__file__).parent

app = FastAPI(title="SpaceCracker V2 Web Panel", description="Real-time credential scanning dashboard")

# Mount static files and templates
app.mount("/static", StaticFiles(directory=current_dir / "static"), name="static")
templates = Jinja2Templates(directory=current_dir / "templates")


class ConnectionManager:
    """Manages WebSocket connections for real-time updates"""
    
    def __init__(self):
        self.active_connections: List[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def send_personal_message(self, message: str, websocket: WebSocket):
        await websocket.send_text(message)
    
    async def broadcast(self, data: Dict[str, Any]):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(data))
            except:
                # Remove dead connections
                try:
                    self.active_connections.remove(connection)
                except:
                    pass


manager = ConnectionManager()


@app.get("/", response_class=HTMLResponse)
async def dashboard(request: Request):
    """Main dashboard page"""
    return templates.TemplateResponse("dashboard.html", {"request": request})


@app.get("/scan", response_class=HTMLResponse) 
async def scan_page(request: Request):
    """Scan configuration page"""
    return templates.TemplateResponse("scan.html", {"request": request})


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """WebSocket endpoint for real-time updates"""
    await manager.connect(websocket)
    try:
        while True:
            # Keep connection alive and listen for messages
            data = await websocket.receive_text()
            
            # Echo back for testing
            await manager.send_personal_message(f"Echo: {data}", websocket)
            
    except WebSocketDisconnect:
        manager.disconnect(websocket)


@app.post("/api/scan/start")
async def start_scan(request: Request):
    """Start a new scan"""
    data = await request.json()
    targets = data.get('targets', [])
    modules = data.get('modules', [])
    
    # Simulate scan start
    scan_id = f"scan_{int(time.time())}"
    
    # Broadcast scan started event
    await manager.broadcast({
        "type": "scan_started",
        "scan_id": scan_id,
        "targets": targets,
        "modules": modules,
        "timestamp": time.time()
    })
    
    return {"success": True, "scan_id": scan_id}


@app.get("/api/scan/status/{scan_id}")
async def get_scan_status(scan_id: str):
    """Get scan status and results"""
    # Simulate scan status
    return {
        "scan_id": scan_id,
        "status": "running",
        "progress": 45.2,
        "findings": 12,
        "targets_processed": 450,
        "total_targets": 1000,
        "start_time": time.time() - 300,
        "eta": 420
    }


@app.post("/api/scan/stop/{scan_id}")
async def stop_scan(scan_id: str):
    """Stop a running scan"""
    # Simulate scan stop
    await manager.broadcast({
        "type": "scan_stopped",
        "scan_id": scan_id,
        "timestamp": time.time()
    })
    
    return {"success": True, "message": f"Scan {scan_id} stopped"}


# Demo endpoint to simulate real-time updates
@app.post("/api/demo/stats")
async def demo_stats():
    """Demo endpoint to send fake real-time stats"""
    import random
    
    # Simulate statistics update
    stats = {
        "type": "stats_update",
        "crack_id": f"#202509050{random.randint(10, 99)}",
        "hits": random.randint(0, 20),
        "checked_paths": random.randint(1000, 50000),
        "checked_urls": random.randint(100, 5000),
        "invalid_urls": random.randint(10, 200),
        "total_urls": random.randint(5000, 100000),
        "progression": random.uniform(5, 95),
        "avg_checks_per_sec": random.randint(100, 2000),
        "avg_url_per_sec": random.randint(10, 100),
        "current_target": f"https://target-{random.randint(1, 100)}.example.com",
        "status": "running",
        "timestamp": time.time()
    }
    
    await manager.broadcast(stats)
    return {"success": True}


# Demo endpoint to simulate new hit
@app.post("/api/demo/hit")
async def demo_hit():
    """Demo endpoint to send fake hit notification"""
    import random
    
    services = ["sendgrid", "aws_ses", "mailgun", "stripe"]
    service = random.choice(services)
    
    hit = {
        "type": "new_hit",
        "crack_id": f"#202509050{random.randint(10, 99)}",
        "service": service,
        "severity": "Critical",
        "url": f"https://target-{random.randint(1, 100)}.example.com/.env",
        "response_time": round(random.uniform(0.1, 2.0), 3),
        "validation": {
            "valid": True,
            "plan": "Pro Account" if service == "sendgrid" else "Production SES",
            "credits": random.randint(1000, 100000)
        },
        "timestamp": time.time()
    }
    
    await manager.broadcast(hit)
    return {"success": True}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8080)