# Bake mode

Bake mode saves a set of connection flags — source URL, auth headers, transport, filters — as a
named configuration so you never have to repeat them.

## Create a baked config

```bash
# From an MCP HTTP server
mcp2cli bake create myserver --mcp https://mcp.example.com/sse \
  --auth-header "x-api-key:sk-..."

# From a local MCP stdio server
mcp2cli bake create mygit --mcp-stdio "npx @mcp/github" \
  --include "search-*,list-*" --exclude "delete-*"

# From an OpenAPI spec (read-only subset)
mcp2cli bake create petstore --spec https://api.example.com/spec.json \
  --exclude "delete-*,update-*" --methods GET,POST --cache-ttl 7200

# From a GraphQL endpoint
mcp2cli bake create mygql --graphql https://api.example.com/graphql \
  --auth-header "Authorization:Bearer tok_..."
```

## Use a baked config

Prefix the config name with `@`:

```bash
mcp2cli @myserver --list
mcp2cli @myserver search --query "test"
mcp2cli @petstore list-pets --status available
mcp2cli @mygql users
```

All the saved flags are silently injected — you only type what is different about this specific call.

## Manage baked configs

```bash
mcp2cli bake list                       # show all saved configs
mcp2cli bake show myserver              # show the config (secrets masked)
mcp2cli bake update myserver --cache-ttl 3600
mcp2cli bake remove myserver
```

## Install a shell wrapper

`bake install` creates a small shell script in `~/.local/bin/` so the config can be invoked
without the `mcp2cli @` prefix:

```bash
mcp2cli bake install petstore
# Creates ~/.local/bin/petstore → wraps `mcp2cli @petstore "$@"`

petstore --list
petstore list-pets --limit 5
```

Install to a custom directory:

```bash
mcp2cli bake install petstore --dir ./scripts/
```

## Auto-group tools by prefix

Many MCP servers name their tools with a `group--action` convention (`github--search-repos`,
`github--list-prs`). The included helper script creates one baked config per group:

```bash
./mcp2cli-bake-install-groups.sh https://mcp.example.com/sse
```

This lists all tools, extracts the unique prefixes (the part before `--`), and for each one runs:

```bash
mcp2cli bake create <group> --mcp <url> --include '<group>--*' --force
mcp2cli bake install <group>
```

## Storage

Baked configs are stored in `~/.config/mcp2cli/baked.json`. Override the location with the
`MCP2CLI_CONFIG_DIR` environment variable.

Secrets stored in baked configs (auth-header values, OAuth client IDs/secrets) can be passed as
`env:VAR` or `file:/path` references so they are never stored in plaintext. See
[Authentication](auth.md).
