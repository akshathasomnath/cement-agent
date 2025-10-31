
import os
import requests

class ToolboxClient:
    """
    Local HTTP client to call your sub-agents (clinker, fuel, material, optimization, quality).
    """

    def __init__(self):
        self.agents = {
            "clinker": os.getenv("CLINKER_AGENT_URL", "http://localhost:8081/v1"),
            "fuel": os.getenv("FUEL_AGENT_URL", "http://localhost:8082/v1"),
            "raw_material": os.getenv("MATERIAL_AGENT_URL", "http://localhost:8083/v1"),
            "optimization": os.getenv("OPTIMIZATION_AGENT_URL", "http://localhost:8084/v1"),
            "quality": os.getenv("QUALITY_AGENT_URL", "http://localhost:8085/v1"),
        }

    def call_agent(self, agent_name: str, payload: dict):
        """Send POST request to sub-agent"""
        if agent_name not in self.agents:
            return {"error": f"Unknown agent: {agent_name}"}
        try:
            url = self.agents[agent_name]
            response = requests.post(url, json=payload)
            response.raise_for_status()
            return response.json()
        except Exception as e:
            return {"error": str(e)}

    def predict_all(self, payload: dict):
        """Call all agents and return merged results"""
        results = {}
        for name in self.agents:
            results[name] = self.call_agent(name, payload)
        return results


if __name__ == "__main__":
    tb = ToolboxClient()
    sample_payload = {
        "feed_rate": 120,
        "kiln_temp": 1450,
        "fuel_type": "coal",
        "power_kwh_per_ton": 90,
        "fineness": 280,
        "residue": 12,
        "quality": 95
    }
    print(tb.predict_all(sample_payload))
