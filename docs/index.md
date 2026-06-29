# mcp2cli

**Turn any MCP server, OpenAPI spec, or GraphQL endpoint into a CLI — at runtime, zero codegen.**

mcp2cli introspects an API source, builds a fully-featured `argparse` CLI on the fly, executes the
call you asked for, and prints the result. No SDK generation, no YAML templates, no project
scaffolding — just point it at an API and start calling operations.

## Why mcp2cli?

Every time an LLM agent handles a tool-call turn it must load the full schema for every available
tool into its context. With a large MCP server or OpenAPI spec this can cost **thousands of tokens
per turn**. mcp2cli replaces that with a single shell call — the agent asks the shell, gets a
result, and never touches the schema directly.

Savings from the [benchmark](../README.md): **96–99 % fewer tokens** compared to native tool
injection.

## Quick start

```bash
# Run without installing
uvx mcp2cli --help

# Install globally
uv tool install mcp2cli
```

Pick your API source and go:

```bash
# MCP server (HTTP)
mcp2cli --mcp https://mcp.example.com/sse --list

# OpenAPI spec (URL or local file)
mcp2cli --spec https://petstore3.swagger.io/api/v3/openapi.json --list

# GraphQL endpoint
mcp2cli --graphql https://api.example.com/graphql --list
```

## Guides

- [MCP servers](mcp.md) — what MCP is and how mcp2cli connects to one
- [OpenAPI](openapi.md) — turning a REST API spec into commands
- [GraphQL](graphql.md) — introspecting a GraphQL schema and calling operations
- [Bake mode](bake.md) — saving connection settings so you never repeat `--mcp`/`--spec` again
- [Authentication](auth.md) — API keys, Bearer tokens, OAuth, and secrets

## Concepts

| Term | Meaning |
|------|---------|
| **source** | Where mcp2cli reads the API definition (`--mcp`, `--spec`, `--graphql`, `--mcp-stdio`) |
| **command** | One callable operation — an MCP tool, an OpenAPI endpoint, or a GraphQL query/mutation |
| **baked config** | A named, saved set of connection flags (`mcp2cli bake create`) |
| **cache** | The locally-stored spec / tool list (`~/.cache/mcp2cli/`) |

## Requirements

- Python 3.10+
- `uvx` / `uv` (recommended) or `pip`
