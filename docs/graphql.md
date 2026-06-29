# GraphQL endpoints

## What is GraphQL?

**GraphQL** is a query language for APIs that lets clients request exactly the data they need.
Instead of many fixed REST endpoints, a GraphQL API exposes a single endpoint that accepts
*queries* (reads) and *mutations* (writes).

Every GraphQL server publishes its own schema — a complete description of every query and mutation
it supports. mcp2cli fetches that schema automatically via the standard *introspection* mechanism,
then maps each field in the schema to a CLI subcommand.

No SDL files, no codegen, no configuration — just point mcp2cli at the endpoint.

## Basic usage

```bash
# List all available queries and mutations
mcp2cli --graphql https://api.example.com/graphql --list

# Run a query
mcp2cli --graphql https://api.example.com/graphql users

# Run a query with arguments
mcp2cli --graphql https://api.example.com/graphql user --id 42

# Run a mutation
mcp2cli --graphql https://api.example.com/graphql create-user \
  --name "Alice" --email "alice@example.com"
```

## How commands are named

Queries and mutations become kebab-case CLI commands:

| GraphQL field | CLI command |
|---|---|
| `listUsers` | `list-users` |
| `createUser` | `create-user` |
| `deleteUserById` | `delete-user-by-id` |

When a field name exists in both the query type and the mutation type, mcp2cli prefixes it with
the operation type to avoid collisions:

```
query-getUser   # from Query.getUser
mutation-getUser  # hypothetical Mutation.getUser
```

## Selection sets

GraphQL queries must specify which fields to return. mcp2cli auto-generates a selection set by
walking the return type up to two levels deep and selecting all scalar and enum fields:

```graphql
# Auto-generated for "users"
query { users { id name email age status address { city country } } }
```

Override it with `--fields` when you need something different:

```bash
# Return only id and name
mcp2cli --graphql https://api.example.com/graphql users --fields "id name"

# Return nested data
mcp2cli --graphql https://api.example.com/graphql user --id 1 \
  --fields "id name address { city country }"
```

## Arguments

GraphQL arguments map directly to CLI flags. Types are converted as follows:

| GraphQL type | CLI type |
|---|---|
| `String`, `ID` | `str` |
| `Int` | `int` |
| `Float` | `float` |
| `Boolean` | flag (no value needed) |
| `[T]` (list) | `str` accepting JSON array or comma-separated values |
| Input object | `str` accepting a JSON object |
| Enum | `str` with `--choices` |

Required arguments (non-null in the schema) become required CLI flags.

## Sending variables from stdin

Pass a JSON object on stdin with `--stdin` to supply all variables at once:

```bash
echo '{"name": "Alice", "email": "alice@example.com", "age": 30}' | \
  mcp2cli --graphql https://api.example.com/graphql create-user --stdin
```

## Authentication

```bash
# Static Bearer token
mcp2cli --graphql https://api.example.com/graphql \
  --auth-header "Authorization:Bearer tok_..." users

# OAuth (opens browser once, caches tokens)
mcp2cli --graphql https://api.example.com/graphql --oauth users
```

See [Authentication](auth.md) for the full reference.
