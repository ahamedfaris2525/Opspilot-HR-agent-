from app.tools.registry import TOOLS


class ToolExecutor:
    def execute(self, tool_name: str, **kwargs):

        tool = TOOLS.get(tool_name)

        if not tool:
            raise ValueError(f"Unknown tool: {tool_name}")

        return tool(**kwargs)
