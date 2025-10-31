from grinding_agent import GrindingAgent

PROJECT_ID = "glossy-observer-425809-e5"
LOCATION = "us-central1"

agent = GrindingAgent(PROJECT_ID, LOCATION)

result = agent.analyze_and_optimize()
print("Grinding Optimization Recommendation:\n", result)
