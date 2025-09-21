from google.cloud import aiplatform
from google.cloud import agent, aiplatform


app = agent.AgentApp("cement_quality_agent")

PROJECT_ID = "glossy-observer-425809-e5"
LOCATION = "us-central1"
ENDPOINT_ID = "7614631494278971392"

aiplatform.init(project=PROJECT_ID, location=LOCATION)
endpoint = aiplatform.Endpoint(ENDPOINT_ID)


@app.intent("predict_quality")
def predict_quality(ctx: agent.Context, feed_rate: float, temp: float, kwh: float, fuel: str):
    """Predict Blaine and Residue from plant inputs"""
    response = endpoint.predict(instances=[{
        "feed_rate": feed_rate,
        "kiln_temp": temp,
        "power_kwh_per_ton": kwh,
        "fuel_type": fuel
    }])

    prediction = response.predictions[0]
    return {
        "blaine": prediction.get("blaine"),
        "residue": prediction.get("residue")
    }

if __name__ == "__main__":
    app.run()

