from .campaigns import CAMPAIGN_TOOLS, handle_campaign_tool
from .insights import INSIGHT_TOOLS, handle_insight_tool

ALL_TOOLS = CAMPAIGN_TOOLS + INSIGHT_TOOLS


def handle_tool(tool_name, tool_input, client):
    if tool_name in [t["name"] for t in CAMPAIGN_TOOLS]:
        return handle_campaign_tool(tool_name, tool_input, client)
    if tool_name in [t["name"] for t in INSIGHT_TOOLS]:
        return handle_insight_tool(tool_name, tool_input, client)
    raise ValueError(f"Unknown tool: {tool_name}")
