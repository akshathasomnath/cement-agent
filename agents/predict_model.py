from google.cloud import aiplatform

aiplatform.init(project="glossy-observer-425809-e5", location="us-central1")

endpoint = aiplatform.Endpoint("7614631494278971392")  

instances = [
    {
        "feed_rate": "25.5",           
        "fuel_type": "coal",           
        "fineness": "320",            
        "residue": "1.5",              
        "quality": "A",                
        "power_kwh_per_ton": "95.2",   
        "kiln_temp": "1450"            
    }
]

predictions = endpoint.predict(instances=instances)
print("Predictions:", predictions)
