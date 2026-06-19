# Block 4 — Giving Claude Hands: MCP + GitHub

## Goal
Connect Claude to an extra tool (the filesystem MCP server) and then have Claude
open a GitHub pull request for you — entirely through plain-English instructions.
You will never type a git command yourself.

## Type this
**Part A — add the MCP server.**

1. In your terminal (outside the Claude chat, so press `Ctrl+C` or open a second
   terminal tab), run:
   `claude mcp add filesystem -- npx -y @modelcontextprotocol/server-filesystem .`
2. Confirm it was added:
   `claude mcp list`
   You should see `filesystem` in the list.
3. Start Claude again:
   `claude`
4. Inside the chat, check that MCP is active:
   `/mcp`

**Part B — push to GitHub.**

5. Ask Claude to create a repository and push the report script (paste as-is):
   `Create a new GitHub repository called adriatica-sales-report and push our report script to it.`
6. Once Claude confirms the repo exists, ask it to open a pull request:
   `Open a pull request that adds a short README describing the monthly report.`

## You should see
- `claude mcp list` showing `filesystem` with its status.
- Claude calling the `gh` CLI (GitHub's command-line tool) and the MCP server to
  create the repo, push the file, and open the PR.
- A GitHub repository URL and a pull request URL printed in the chat.

## If it looks wrong
- "Not signed in to GitHub" or `gh: command not found`:
  `Help me sign in to GitHub first, then try again.`
- The MCP server fails to start or `npx` is not found: ask the facilitator — Node.js
  may need to be installed.
- Claude creates the repo but can't open the PR: make sure you approved each step;
  if it is still stuck, say `Try the pull request step again.`
- If GitHub is unavailable on your network today, use the fallback example at
  `fallbacks/b4-pr-example.md` — it shows what a successful run looks like so you
  can follow along.
