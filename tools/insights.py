import json

INSIGHT_TOOLS = [
    {
        "name": "get_performance_insights",
        "description": "Get performance metrics (impressions, clicks, spend, CPC, CPM, CTR, conversions) for campaigns or ad sets.",
        "input_schema": {
            "type": "object",
            "properties": {
                "level": {
                    "type": "string",
                    "enum": ["account", "campaign", "adset", "ad"],
                    "description": "Aggregation level for the report.",
                },
                "date_preset": {
                    "type": "string",
                    "enum": ["today", "yesterday", "last_3d", "last_7d", "last_14d",
                             "last_28d", "last_30d", "last_90d", "this_month", "last_month"],
                },
                "start_date": {"type": "string", "description": "YYYY-MM-DD. Use instead of date_preset for custom ranges."},
                "end_date": {"type": "string", "description": "YYYY-MM-DD."},
            },
            "required": ["level"],
        },
    },
    {
        "name": "get_adsets",
        "description": "List ad sets for a campaign, including targeting, budget, and optimization goal.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string", "description": "Scope to a specific campaign. Omit for all ad sets."},
            },
        },
    },
]


def handle_insight_tool(tool_name, tool_input, client):
    if tool_name == "get_performance_insights":
        if "start_date" in tool_input and "end_date" in tool_input:
            results = client.get_insights_by_date_range(
                start_date=tool_input["start_date"],
                end_date=tool_input["end_date"],
                level=tool_input.get("level", "campaign"),
            )
        else:
            results = client.get_insights(
                level=tool_input.get("level", "campaign"),
                date_preset=tool_input.get("date_preset", "last_7d"),
            )
        return json.dumps([dict(r) for r in results], indent=2)

    if tool_name == "get_adsets":
        results = client.get_adsets(campaign_id=tool_input.get("campaign_id"))
        return json.dumps([dict(r) for r in results], indent=2)
