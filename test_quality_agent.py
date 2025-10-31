from quality_agent import QualityAgent

PROJECT_ID = "glossy-observer-425809-e5"       
LOCATION = "us-central1"             
MODEL_ID = "cement_quality_model"    

agent = QualityAgent(PROJECT_ID, LOCATION, MODEL_ID)

result = agent.predict_quality(
    feed_rate=120.5,
    temp=1450,
    kwh_per_ton=95,
    fuel_type="RDF"
)

print("Predicted Blaine / Residue:", result)

