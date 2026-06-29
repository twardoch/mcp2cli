# Authentication

mcp2cli supports static headers, OAuth 2.0 (authorization code + PKCE and client credentials),
and safe secret injection. All auth mechanisms work across MCP, OpenAPI, and GraphQL modes.

## Static API key / Bearer token

```bash
# Custom header (any name)
mcp2cli --mcp https://mcp.example.com/sse \
  --auth-header "x-api-key:sk-..." --list

# Authorization: Bearer
mcp2cli --spec ./spec.json \
  --auth-header "Authorization:Bearer tok_abc123" list-pets

# Multiple headers
mcp2cli --spec ./spec.json \
  --auth-header "Authorization:Bearer tok_..." \
  --auth-header "x-tenant-id:acme" \
  list-pets
```

The `--auth-header` format is `Name:Value`. The colon is the delimiter.

## OAuth 2.0

### Authorization code + PKCE (interactive)

Used for APIs that require a user login. mcp2cli opens the browser, starts a local callback
server, captures the authorization code, and exchanges it for tokens.

```bash
mcp2cli --mcp https://mcp.example.com/sse --oauth --list
```

Tokens are cached in `~/.cache/mcp2cli/oauth/` and refreshed automatically when they expire. You
only log in once per server.

Supply a pre-registered client ID to skip dynamic client registration (required by some servers):

```bash
mcp2cli --mcp https://mcp.example.com/sse \
  --oauth --oauth-client-id "my-client-id" --list
```

For servers that issue confidential clients (e.g. Slack), supply both client ID and secret:

```bash
mcp2cli --mcp https://mcp.example.com/sse \
  --oauth-client-id "my-client-id" \
  --oauth-client-secret "my-secret" \
  --oauth-flow authorization_code \
  --list
```

### Client credentials (machine-to-machine)

For server-to-server calls where no user is involved:

```bash
mcp2cli --spec https://api.example.com/spec.json \
  --oauth-client-id "my-client-id" \
  --oauth-client-secret "my-secret" \
  list-pets
```

mcp2cli detects client credentials automatically when both `--oauth-client-id` and
`--oauth-client-secret` are present. Override with `--oauth-flow client_credentials`.

### Scopes and redirect URI

```bash
# Request specific scopes
mcp2cli --graphql https://api.example.com/graphql \
  --oauth --oauth-scope "read write" users

# Use a custom redirect URI (port must be explicit)
mcp2cli --mcp https://mcp.example.com/sse \
  --oauth --oauth-redirect-uri "http://localhost:3334/callback" --list
```

## Secret injection

Passing secrets directly as CLI arguments makes them visible in process listings and shell history.
mcp2cli supports two safe alternatives:

### From an environment variable

```bash
export MY_TOKEN=sk-...
mcp2cli --mcp https://mcp.example.com/sse \
  --auth-header "Authorization:env:MY_TOKEN" --list
```

### From a file

```bash
mcp2cli --mcp https://mcp.example.com/sse \
  --oauth-client-secret "file:/run/secrets/client_secret" \
  --oauth-client-id "my-client-id" --list
```

Both prefixes work on `--auth-header` values, `--oauth-client-id`, `--oauth-client-secret`, and
`--oauth-client-name`. Baked configs with `env:` references never store the resolved secret.

## Clearing cached tokens

To force a fresh OAuth login:

```bash
mcp2cli --mcp https://mcp.example.com/sse --oauth-logout --list
```
