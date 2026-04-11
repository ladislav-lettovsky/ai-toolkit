class BaseAgent:
    """
    Core AI Agent abstraction.
    All generated agents inherit from this.
    """

    def __init__(self, name: str):
        self.name = name
        self.memory = []
        self.tools = {}

    def register_tool(self, name: str, func):
        self.tools[name] = func

    def think(self, input_text: str) -> str:
        return f"[{self.name}] analyzing: {input_text}"

    def act(self, thought: str) -> str:
        return f"[{self.name}] acting on: {thought}"

    def run(self, input_text: str) -> str:
        thought = self.think(input_text)
        result = self.act(thought)
        self.memory.append({"input": input_text, "output": result})
        return result
