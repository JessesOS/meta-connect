# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**Meta Connect** is a Claude agent orchestration system that integrates with Meta Business Suite and Meta Ads Manager (Facebook/Instagram). The goal is to automate and orchestrate tasks across Meta's APIs using Claude as the AI backbone.

## Key Integrations

- **Meta Graph API** — core API for Business Suite, Pages, Ad Manager, and Insights
- **Meta Marketing API** — campaign/ad management, reporting, budget control
- **Claude API (Anthropic)** — agent orchestration, decision-making, and automation logic

## Architecture Intent

This is an AI agent system. When building features:

- Claude agents should call Meta APIs as tools, not as raw HTTP calls inline in business logic
- Keep Meta API credentials/tokens out of code — use environment variables
- Agent prompts and tool definitions live separately from API client code
- Prefer composable, single-purpose tools that agents can chain

## Environment Variables

The following env vars are expected (use a `.env` file locally):

```
ANTHROPIC_API_KEY=
META_APP_ID=
META_APP_SECRET=
META_ACCESS_TOKEN=        # long-lived page/system user token
META_AD_ACCOUNT_ID=       # act_XXXXXXXXX format
META_BUSINESS_ID=
```

## Claude API Usage

Always use the latest capable model. Current default: `claude-sonnet-4-6`. For complex multi-step agent reasoning, prefer `claude-opus-4-8`.

Use the Anthropic SDK tool-use pattern for agent tools. Structure tools as:
1. A schema definition (name, description, input_schema)
2. A handler function that executes the actual Meta API call
3. An agent loop that processes `tool_use` blocks from Claude responses

## Meta API Notes

- All Graph API calls use base URL: `https://graph.facebook.com/v21.0/`
- Ad accounts are referenced as `act_{ad_account_id}`
- Rate limits apply per token — implement exponential backoff
- Insights data has async job patterns for large date ranges (use `AdReportRun`)
