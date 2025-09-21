import pandas as pd
import numpy as np

N = 2000

np.random.seed(42)

data = {
    "feed_rate": np.random.normal(120, 10, N).round(2),       
    "kiln_temp": np.random.normal(1450, 30, N).round(1),      
    "fuel_type": np.random.choice(["coal", "petcoke", "RDF", "biomass"], N),
    "power_kwh_per_ton": np.random.normal(95, 5, N).round(2), 
    "fineness": np.random.normal(320, 20, N).round(1),        
    "residue": np.random.uniform(2, 6, N).round(2),           
}

conditions = (
    (data["kiln_temp"] > 1420) & (data["kiln_temp"] < 1480) &
    (data["fineness"] > 300) & (data["fineness"] < 340) &
    (data["residue"] < 4.5)
)
quality = np.where(conditions, "good", "bad")
data["quality"] = quality

df = pd.DataFrame(data)

df.to_csv("cement_quality.csv", index=False)
print("✅ Synthetic dataset created: cement_quality.csv with", N, "rows")
