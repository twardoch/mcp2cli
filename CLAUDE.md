# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## What this is

mcp2cli turns any **MCP server**, **OpenAPI spec**, or **GraphQL endpoint** into a CLI at runtime — no code generation. It introspects the source, builds an argparse CLI dynamically, executes the call, and prints the result. The motivating use case is token efficiency for LLM agents: instead of loading every tool schema into context each turn, an agent shells out to `mcp2cli`.

## Commands

```bash
# Install with test + MCP deps (note: .python-version pins 3.14, but requires-python is >=3.10)
uv sync --extra test

# Run the full suite (~96 tests)
uv run pytest tests/ -v

# Single file / single test
uv run pytest tests/test_graphql.py -v
uv run pytest tests/test_bake.py::test_name -v

# Token-savings tests print measurements; run with -s
uv run pytest tests/test_token_savings.py -v -s

# Run the CLI from source
uv run mcp2cli --help

# Build / publish (CI does this on tag via .github/workflows/publish.yml)
uv build
```

There is no separate lint step configured in CI; CI only builds and publishes.

## Architecture

**Nearly all logic lives in `src/mcp2cli/__init__.py`** (~4000 lines), organized into labeled `# ---` sections. `__main__.py` is a 4-line shim. Treat `__init__.py` as the whole program; its section banners (Helpers, Caching, Usage tracking, OAuth support, OpenAPI, MCP, GraphQL, Bake, Sessions, Main entry point) are the map.

### Core flow

`main()` → checks `argv[1]` for the `bake` subcommand or an `@name` baked-tool reference (handled before argparse), otherwise → `_main_impl()`.

`_main_impl()` is the dispatcher:
1. `_build_main_parser()` builds the global pre-parser.
2. `_split_at_subcommand()` splits argv at the subcommand boundary so tool params that collide with global flags (e.g. a tool's own `--env`/`--refresh`) aren't swallowed by the pre-parser. **This split is load-bearing — see GH #15. Don't "simplify" it into a single parse_args.**
3. Validates source modes (`--spec` / `--mcp` / `--mcp-stdio` / `--graphql` are mutually exclusive), sets up OAuth, then routes to one of: `handle_graphql`, `handle_mcp`, or `_handle_openapi_mode`.

### The three source backends

Each backend follows the same shape: **load/introspect → extract commands → (list | execute)**, all normalized onto the shared `CommandDef` / `ParamDef` dataclasses so downstream listing, filtering, sorting, and execution are source-agnostic.

- **OpenAPI**: `load_openapi_spec` → `resolve_refs` (inlines `$ref`) → `extract_openapi_commands` → `execute_openapi` (builds an httpx request).
- **MCP**: `handle_mcp` over HTTP (`run_mcp_http`, with `--transport auto|sse|streamable` fallback) or stdio (`run_mcp_stdio`); tools come from `_fetch_mcp_tools` → `extract_mcp_commands`. Uses the `mcp` SDK's async client inside `_mcp_session`; sync entry points wrap it. Also handles MCP resources (`_handle_resources`) and prompts (`_handle_prompts`).
- **GraphQL**: `load_graphql_schema` runs `GRAPHQL_INTROSPECTION_QUERY` → `extract_graphql_commands`; `_build_selection_set` auto-generates selection sets (override with `--fields`), `_build_graphql_document` constructs the parameterized query, `execute_graphql` sends it.

### Cross-cutting subsystems

- **Bake mode** (`# Baked config CRUD`, `# Bake subcommands`): persists connection settings + filters as named configs in `~/.config/mcp2cli/baked.json`. `@name` expands a config back into argv via `_baked_to_argv` and re-enters `_main_impl` with a `BakeConfig`. Bake names are validated against `_BAKE_NAME_RE`.
- **Caching** (`~/.cache/mcp2cli/`, 1h default TTL): caches specs and MCP tool lists. Local file specs are never cached.
- **Usage tracking** (`usage.json`): `record_usage` logs invocations; `sort_commands` / `_resolve_sort_mode` rank `--list` output by frequency when usage data exists.
- **OAuth** (`build_oauth_provider`, `FileTokenStorage`): auth-code+PKCE (spins a local callback server, `_CallbackHandler` on a `_find_free_port`) and client-credentials flows; tokens persisted under `~/.cache/mcp2cli/oauth/`.
- **Sessions** (`# Sessions`): a daemon (`_run_session_daemon`) keeps a long-lived MCP stdio server alive behind a Unix socket; `_session_request` dispatches JSON-RPC-style calls via `_SESSION_DISPATCH`. Avoids re-spawning the server per call.
- **Secrets**: `resolve_secret` expands `env:` and `file:` prefixes on auth/OAuth values so secrets never appear in argv.
- **Output**: `output_result` handles `--pretty` / `--raw` / `--toon` (TOON encoding shells out via `_find_toon_cli`) / `--head`.

### Config/cache locations (override via env)

- `MCP2CLI_CACHE_DIR` → cache, usage, oauth tokens, sessions
- `MCP2CLI_CONFIG_DIR` → `baked.json`

## Conventions

- **Single-module design is intentional** — keep new functionality in `__init__.py` under the appropriate section banner rather than splitting into new modules, unless a section grows genuinely unwieldy.
- Tool/command names are normalized to kebab-case (`to_kebab`); parameter schemas are mapped to argparse types via `schema_type_to_python` / `coerce_value`.
- Tests use real local servers (`tests/_mcp_http_server.py`, `tests/mcp_test_server.py`) and an in-process petstore spec fixture in `conftest.py`, not mocks — when adding a backend behavior, add or extend a fixture server.
- The package ships `py.typed` and an installable agent skill under `skills/mcp2cli/SKILL.md`.
