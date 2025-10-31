from google.adk.agents import Agent
from google.cloud import aiplatform
import traceback

PROJECT_ID = "glossy-observer-425809-e5"
REGION = "us-central1"
ENDPOINT_ID = "7614631494278971392"


aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

def predict_clinker(
    feed_rate: float,
    kiln_temp: float,
    fuel_type: str,
    power_kwh_per_ton: float,
    fineness: float,
    residue: float,
    quality: float
) -> dict:
    """Predict clinker parameters from input values using Vertex AI."""
    try:
        instance = {
            "feed_rate": feed_rate,
            "kiln_temp": kiln_temp,
            "fuel_type": fuel_type,
            "power_kwh_per_ton": power_kwh_per_ton,
            "fineness": fineness,
            "residue": residue,
            "quality": quality
        }
        response = endpoint.predict([instance])

        
        pred_value = None
        if response and hasattr(response, "predictions"):
            pred_value = response.predictions[0] if response.predictions else None

        return {
            "predicted_efficiency": float(pred_value) if pred_value else 0.0,
            "status": "success",
            "raw_response": response.predictions
        }
    except Exception as e:
        return {
            "status": "error",
            "error": str(e),
            "trace": traceback.format_exc()
        }


root_agent = Agent(
    name="clinker_agent",
    model="gemini-2.5-flash",
    description="Predict clinker parameters for optimal kiln operation",
    instruction="Use the predict_clinker function to analyze input parameters and return clinker predictions."
)


async def run(self, input: dict = None, context: dict = None) -> dict:
    if not input:
        return {"error": "No input data provided."}
    try:
        return predict_clinker(**input)
    except Exception as e:
        return {"error": str(e), "trace": traceback.format_exc()}

root_agent.run = run.__get__(root_agent)
