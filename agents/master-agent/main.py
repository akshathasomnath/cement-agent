from fastapi import FastAPI
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
    uvicorn.run(app, host="0.0.0.0", port=port)
