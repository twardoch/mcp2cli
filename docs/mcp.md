# MCP servers

## What is MCP?

**Model Context Protocol (MCP)** is an open standard that lets AI assistants discover and call
tools hosted on an external server. Think of it as a plugin system: an MCP server exposes a list
of *tools* (named functions with typed parameters), and clients — AI agents or shells — call them
by name.

Each tool has:
- a **name** (e.g. `search_files`)
- a **description** the AI reads to decide when to use it
- an **input schema** (JSON Schema) listing the parameters it accepts

Normally an AI agent loads every tool schema into its context window every turn. mcp2cli
eliminates that cost by being the middleman: it fetches the schema once (and caches it), exposes
each tool as a CLI subcommand, and lets the agent call `mcp2cli @myserver search-files --path /tmp`
instead.

## Connection modes

MCP servers speak one of two transports.

### HTTP / SSE (`--mcp`)

The server runs as a standalone HTTP process and streams responses over SSE or the newer
Streamable HTTP protocol.

```bash
# List available tools
mcp2cli --mcp https://mcp.example.com/sse --list

# Call a tool
mcp2cli --mcp https://mcp.example.com/sse search --query "hello"

# Force SSE transport (skips the streamable-HTTP probe)
mcp2cli --mcp https://mcp.example.com/sse --transport sse --list
```

mcp2cli tries Streamable HTTP first, then falls back to SSE automatically.

### stdio (`--mcp-stdio`)

The server is launched as a child process that communicates over stdin/stdout. This is common for
locally-installed tools such as filesystem servers, git helpers, and language-server bridges.

```bash
# Launch a local filesystem server and list its tools
mcp2cli --mcp-stdio "npx @modelcontextprotocol/server-filesystem /tmp" --list

# Call a tool
mcp2cli --mcp-stdio "npx @modelcontextprotocol/server-filesystem /tmp" \
  read-file --path /tmp/notes.txt

# Pass environment variables to the server process
mcp2cli --mcp-stdio "node my-server.js" --env API_KEY=sk-... search --query "test"
```

## Authentication

Most MCP HTTP servers require an API key or OAuth token. See [Authentication](auth.md).

```bash
# Static API key in a header
mcp2cli --mcp https://mcp.example.com/sse \
  --auth-header "x-api-key:sk-..." --list

# OAuth (opens browser once, then caches tokens)
mcp2cli --mcp https://mcp.example.com/sse --oauth --list
```

## Sessions (advanced)

For `--mcp-stdio` servers that are expensive to start (language servers, Docker-based servers),
mcp2cli can keep the process alive as a background daemon and reuse it across calls:

```bash
mcp2cli --mcp-stdio "node heavy-server.js" --session my-session search --query "test"
```

The daemon is stored under `~/.cache/mcp2cli/sessions/` and reused for subsequent calls with the
same `--session` name.

## MCP resources and prompts

Beyond tools, MCP servers can expose *resources* (files, database rows) and *prompts* (reusable
message templates). mcp2cli can list and read them:

```bash
# List resources
mcp2cli --mcp https://mcp.example.com/sse --resources --list

# List prompts
mcp2cli --mcp https://mcp.example.com/sse --prompts --list
```
