from fastapi import FastAPI, Body, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from fastmcp import FastMCP
import uvicorn
import aiohttp

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Template and static files setup
templates = Jinja2Templates(directory="templates")

# Initialize MCP
mcp = FastMCP("demo server for test")

# Base URL for National Weather Service
NWS_API_BASE = "https://api.weather.gov"

# Helper for making async HTTP requests to the weather API
async def make_nws_request(url):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(url) as resp:
                print(f"Request to: {url} - Status: {resp.status}")
                return await resp.json()
    except Exception as e:
        print("Error making request:", e)
        return None

# Format the weather alert data
def format_alert(feature):
    props = feature.get("properties", {})
    headline = props.get("headline", "No headline")
    description = props.get("description", "No description")
    return f"**{headline}**\n{description}"

# Tool: Multiply
@mcp.tool()
def multiply(a, b):
    return a * b

# Tool: Get weather alerts for a state
@mcp.tool()
async def get_alerts(state: str) -> str:
    """Get weather alerts for a US state."""
    url = f"{NWS_API_BASE}/alerts/active/area/{state}"
    data = await make_nws_request(url)

    if not data or "features" not in data:
        return "Unable to fetch alerts or no alerts found."
    if not data["features"]:
        return "No active alerts for this state."

    alerts = [format_alert(feature) for feature in data["features"]]
    return "\n---\n".join(alerts)

# REST endpoint: Multiply
@app.post("/euron/mcp/multiply")
def call_multiply(data: dict = Body(...)):
    return {"result": multiply(data.get("a", 0), data.get("b", 0))}

# REST endpoint: Get Alerts
@app.post("/euron/mcp/get_alerts")
async def call_get_alerts(request: Request):
    data = await request.json()
    state = data.get("state", "")
    print(f"Received request for alerts for state: {state}")
    result = await get_alerts(state)
    print(f"Alert result: {result}")
    return {"alerts": result}

# Home route → renders frontend.html
@app.get("/", response_class=HTMLResponse)
async def home(request: Request):
    return templates.TemplateResponse("frontend.html", {"request": request})

if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
