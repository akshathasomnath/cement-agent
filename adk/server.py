from fastapi import FastAPI

app = FastAPI(title="ADK Server")

@app.get("/")
async def root():
    return {"status": "ok", "message": "ADK server running"}
