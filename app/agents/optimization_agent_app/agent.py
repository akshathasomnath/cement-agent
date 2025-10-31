from fastapi import FastAPI, Request
from pydantic import BaseModel
from google.cloud import aiplatform
from google import genai
import os

PROJECT_ID = "glossy-observer-425809-e5"
REGION = "us-central1"
ENDPOINT_ID = "7614631494278971392"

aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

app = FastAPI(title="Optimization Agent API", description="Cement optimization with Gemini suggestions")

class OptimizationInput(BaseModel):
    feed_rate: float
    kiln_temp: float
    fuel_type: str
    power_kwh_per_ton: float
    fineness: float
    residue: float
    quality: float

def predict_optimization(data: OptimizationInput) -> dict:
    """Call Vertex AI endpoint for prediction"""
    try:
        instance = data.dict()
        response = endpoint.predict([instance])
        prediction = response.predictions[0]
        return {"prediction": prediction}
    except Exception as e:
        return {"error": str(e)}

def generate_gemini_suggestions(inputs: OptimizationInput, prediction: dict) -> list:
    """Generate optimization suggestions using Gemini"""
    client = genai.Client(vertexai=True, project=PROJECT_ID, location=REGION)
    model = client.models.get("gemini-1.5-flash")

    prompt = f"""
    You are an industrial AI expert optimizing a cement plant.
    Given:
    - Feed rate: {inputs.feed_rate} t/h
    - Kiln temp: {inputs.kiln_temp} °C
    - Fuel type: {inputs.fuel_type}
    - Power consumption: {inputs.power_kwh_per_ton} kWh/ton
    - Fineness: {inputs.fineness}
    - Residue: {inputs.residue}%
    - Quality target: {inputs.quality}/100

    The model predicted: {prediction}

    Suggest 3 actionable optimizations to improve efficiency and product quality.
    Keep suggestions short and practical.
    """

    result = model.generate_content(prompt)
    suggestions = result.text.strip().split("\n")
    return [s for s in suggestions if s.strip()]

@app.post("/predict")
async def predict(request: OptimizationInput):
    """Main prediction + Gemini suggestions"""
    vertex_output = predict_optimization(request)
    if "error" in vertex_output:
        return vertex_output

    suggestions = generate_gemini_suggestions(request, vertex_output["prediction"])
    return {
        "prediction": vertex_output["prediction"],
        "suggestions": suggestions
    }

@app.get("/")
def root():
    return {"status": "Optimization Agent running "}

if __name__ == "__main__":
    import uvicorn
    port = int(os.getenv("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
