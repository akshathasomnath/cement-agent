from google.adk.agents import Agent
from google.cloud import aiplatform

PROJECT_ID = "glossy-observer-425809-e5"
REGION = "us-central1"
ENDPOINT_ID = "7614631494278971392"

aiplatform.init(project=PROJECT_ID, location=REGION)
endpoint = aiplatform.Endpoint(endpoint_name=ENDPOINT_ID)

def predict_fuel(
    feed_rate: float,
    kiln_temp: float,
    fuel_type: str,
    power_kwh_per_ton: float,
    fineness: float,
    residue: float,
    quality: float
) -> dict:
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
        return {"prediction": response.predictions}
    except Exception as e:
        return {"error": str(e)}

root_agent = Agent(
    name="fuel_agent",
    model="gemini-2.5-flash",
    description="Optimize fuel usage and thermal substitution rate",
    instruction="Use the function to predict fuel optimization / TSR.",
)
