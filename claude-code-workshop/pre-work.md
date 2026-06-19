# Pre-Work: Getting Ready for the Workshop

Welcome! This page asks you to do three small things before we meet. Each step
takes about five minutes. If anything goes wrong, do not worry — we sort it out
together at the very start of the session.

---

## Step 1 — Create a Claude Account with Paid Access

Claude Code requires a paid Claude account. A free account will hit rate limits
during the hands-on parts of the day.

1. Go to [claude.ai](https://claude.ai) and create an account if you do not
   have one.
2. Upgrade to **Claude Pro** or **Claude Max** (recommended — flat monthly fee,
   no per-message surprises during the workshop).
   Alternatively, if you prefer pay-as-you-go, enable **API billing** at
   [console.anthropic.com](https://console.anthropic.com) and add a credit
   balance. Either path works; Pro/Max is simpler for a full workshop day.
3. Keep your login details handy — you will use them to authenticate the CLI.

---

## Step 2 — Install Node.js

Claude Code uses Node.js packages to connect to external tools. You need
Node.js version 18 or later.

- **Mac**: download the installer from [nodejs.org](https://nodejs.org) and run
  it. Choose the "LTS" version.
- **Windows**: same — download the LTS installer from
  [nodejs.org](https://nodejs.org) and run it. Restart your computer after
  installing.

To confirm it worked, open your terminal and type:

```
node --version
```

You should see something like `v20.x.x`. Any version 18 or higher is fine.

---

## Step 3 — Install Claude Code and Confirm It Opens

1. In your terminal, run:

   ```
   npm install -g @anthropic-ai/claude-code
   ```

2. Once that finishes, run:

   ```
   claude --version
   ```

   You should see a version number printed (for example, `1.x.x`).

3. Try starting it:

   ```
   claude
   ```

   A welcome screen will appear and ask you to log in or confirm your account.
   Follow the browser prompt to authenticate, then come back to the terminal.

---

## That Is It

If `claude --version` prints a number and `claude` opens, you are fully ready.

**If any step fails, don't worry — we fix it together in the first block.**
Bring your laptop to the session and we will get you running as a group.

---

*Questions before the day? Contact the facilitator.*
