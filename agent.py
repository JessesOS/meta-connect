import os
import json
from pathlib import Path
from dotenv import load_dotenv
import anthropic
from meta_client import MetaClient
from tools import ALL_TOOLS, handle_tool

load_dotenv()

MODEL = "claude-opus-4-8"
SYSTEM_PROMPT = Path("prompts/system.txt").read_text()


def run_agent(user_message: str):
    client = anthropic.Anthropic()
    meta = MetaClient()
    messages = [{"role": "user", "content": user_message}]

    while True:
        response = client.messages.create(
            model=MODEL,
            max_tokens=4096,
            system=SYSTEM_PROMPT,
            tools=ALL_TOOLS,
            messages=messages,
        )

        messages.append({"role": "assistant", "content": response.content})

        if response.stop_reason == "end_turn":
            for block in response.content:
                if hasattr(block, "text"):
                    print(block.text)
            break

        if response.stop_reason == "tool_use":
            tool_results = []
            for block in response.content:
                if block.type == "tool_use":
                    print(f"\n[tool] {block.name}({json.dumps(block.input, indent=2)})")
                    try:
                        result = handle_tool(block.name, block.input, meta)
                    except Exception as e:
                        result = json.dumps({"error": str(e)})
                    print(f"[result] {result[:300]}{'...' if len(result) > 300 else ''}")
                    tool_results.append({
                        "type": "tool_result",
                        "tool_use_id": block.id,
                        "content": result,
                    })

            messages.append({"role": "user", "content": tool_results})


if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) if len(sys.argv) > 1 else input("What would you like to do? ")
    run_agent(prompt)
