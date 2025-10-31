
class Agent:
    def __init__(self, name, description="", model=None):
        self.name = name
        self.description = description
        self.model = model
        self.children = []

    def add_child(self, agent):
        self.children.append(agent)

    async def run(self, input_data):
       
        response = f"[{self.name}] processed: {input_data}"
        results = []
        for child in self.children:
            result = await child.run(input_data)
            results.append(result)
        return response + " | children: " + ", ".join(results)
