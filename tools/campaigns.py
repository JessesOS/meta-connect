import json

CAMPAIGN_TOOLS = [
    {
        "name": "list_campaigns",
        "description": "List all campaigns in the ad account with their status, budget, and objective.",
        "input_schema": {
            "type": "object",
            "properties": {
                "status_filter": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["ACTIVE", "PAUSED", "ARCHIVED", "DELETED"]},
                    "description": "Filter by campaign status. Omit to return all.",
                }
            },
        },
    },
    {
        "name": "create_campaign",
        "description": "Create a new campaign. Always creates in PAUSED status for safety.",
        "input_schema": {
            "type": "object",
            "properties": {
                "name": {"type": "string"},
                "objective": {
                    "type": "string",
                    "enum": ["OUTCOME_AWARENESS", "OUTCOME_TRAFFIC", "OUTCOME_ENGAGEMENT",
                             "OUTCOME_LEADS", "OUTCOME_APP_PROMOTION", "OUTCOME_SALES"],
                },
                "daily_budget": {"type": "number", "description": "Daily budget in dollars."},
                "lifetime_budget": {"type": "number", "description": "Lifetime budget in dollars."},
            },
            "required": ["name", "objective"],
        },
    },
    {
        "name": "update_campaign_budget",
        "description": "Update the daily or lifetime budget of an existing campaign.",
        "input_schema": {
            "type": "object",
            "properties": {
                "campaign_id": {"type": "string"},
                "daily_budget": {"type": "number", "description": "New daily budget in dollars."},
                "lifetime_budget": {"type": "number", "description": "New lifetime budget in dollars."},
            },
            "required": ["campaign_id"],
        },
    },
    {
        "name": "pause_campaign",
        "description": "Pause an active campaign.",
        "input_schema": {
            "type": "object",
            "properties": {"campaign_id": {"type": "string"}},
            "required": ["campaign_id"],
        },
    },
    {
        "name": "activate_campaign",
        "description": "Activate (unpause) a paused campaign.",
        "input_schema": {
            "type": "object",
            "properties": {"campaign_id": {"type": "string"}},
            "required": ["campaign_id"],
        },
    },
]


def handle_campaign_tool(tool_name, tool_input, client):
    if tool_name == "list_campaigns":
        results = client.get_campaigns(status_filter=tool_input.get("status_filter"))
        return json.dumps([dict(r) for r in results], indent=2)

    if tool_name == "create_campaign":
        result = client.create_campaign(
            name=tool_input["name"],
            objective=tool_input["objective"],
            daily_budget=tool_input.get("daily_budget"),
            lifetime_budget=tool_input.get("lifetime_budget"),
        )
        return json.dumps(dict(result), indent=2)

    if tool_name == "update_campaign_budget":
        kwargs = {}
        if "daily_budget" in tool_input:
            kwargs["daily_budget"] = tool_input["daily_budget"]
        if "lifetime_budget" in tool_input:
            kwargs["lifetime_budget"] = tool_input["lifetime_budget"]
        result = client.update_campaign(tool_input["campaign_id"], **kwargs)
        return json.dumps({"success": True, "campaign_id": tool_input["campaign_id"]})

    if tool_name == "pause_campaign":
        client.pause_campaign(tool_input["campaign_id"])
        return json.dumps({"success": True, "status": "PAUSED"})

    if tool_name == "activate_campaign":
        client.activate_campaign(tool_input["campaign_id"])
        return json.dumps({"success": True, "status": "ACTIVE"})
