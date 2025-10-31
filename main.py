"""from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from agent.root_agent import RootAgent  

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

root_agent = RootAgent()

@app.post("/v1")
async def predict(input: dict):
   
    user_input = input.get("input", {})
    result = await root_agent.run(input=user_input)  
    return result  

@app.get("/")
async def health():
    return {"message": "RootAgent is live"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)"""


'''from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os
from agent.root_agent import root_agent, mcp_server
from adk.server import mount_mcp  # <-- helper

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/v1")
async def predict(input: dict):
    user_input = input.get("input", {})
    result = await root_agent.run(input=user_input)
    return result

@app.get("/")
async def health():
    return {"message": "RootAgent is live"}

# ✅ Mount MCP server
mount_mcp(app, mcp_server)

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)'''

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from agent.root_agent import root_agent, mcp_server
from adk.server import mount_mcp
import os

app = FastAPI(title="Master Agent API")

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount MCP tools under /mcp
mount_mcp(app, mcp_server)

@app.post("/v1")
async def predict(input: dict):
    result = await root_agent.run(input=input)
    return result

@app.get("/")
async def health():
    return {"message": "RootAgent + MCP Server are live"}

if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)


