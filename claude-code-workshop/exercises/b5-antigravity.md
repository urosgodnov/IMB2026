# Block 5 — A Second Cockpit: Antigravity

## Goal
Open the same project in Google Antigravity (a visual, browser-based agentic IDE),
connect the same MCP server you set up in Block 4, and add a chart to the report —
all by telling the agent what you want in plain English. This shows that MCP is not
tied to the terminal; the tools move with you.

## Type this
1. Open [Antigravity](https://antigravity.google) in your browser and sign in with
   your Google account (free tier, no payment needed).
2. Click **Open project** and navigate to this project's folder on your computer.
3. In Antigravity's settings panel, find **MCP servers** and add the filesystem
   server. If you are not sure of the JSON format, copy the contents of
   `fallbacks/b5-antigravity-mcp-config.json` into the configuration box.
4. Once the project is open and the MCP server shows as connected, paste this into
   the Antigravity agent prompt:
   `Open data/orders.csv and add a bar chart of monthly revenue to the report.`
5. Approve each action the agent proposes, just as you did in Claude Code.

## You should see
- Antigravity's visual IDE with your project files visible in the sidebar.
- The MCP server listed as active in the tools panel.
- The agent reading `data/orders.csv`, computing monthly revenue, and adding a
  bar chart (PNG or inline plot) alongside the existing report output.
- December (2024-12) standing out as the tallest bar — confirming the same
  answer you found in Block 2.

## If it looks wrong
- **Free-tier quota exhausted**: Antigravity's free tier runs on a weekly quota.
  If you see a "quota exceeded" or "upgrade required" message, switch to the
  facilitator's live demo or the fallback recording. You have not lost your work —
  come back next week and the quota resets.
- **MCP server not connecting**: double-check that you pasted the config from
  `fallbacks/b5-antigravity-mcp-config.json` exactly. The `"."` path in the config
  must match the folder Antigravity has open.
- **Chart does not appear**: ask the agent `Show me the chart you generated.` — it
  may have saved it as a file rather than displaying it inline.
