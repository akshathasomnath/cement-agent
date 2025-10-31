from fastapi import FastAPI

app = FastAPI(title="Mock ADK Server")

@app.get("/")
async def root():
    return {"status": "ok", "message": "Mock ADK server running"}
