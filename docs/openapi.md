# OpenAPI specs

## What is OpenAPI?

**OpenAPI** (formerly Swagger) is the most widely-used format for describing REST APIs. An OpenAPI
document is a JSON or YAML file that lists every HTTP endpoint an API provides, the parameters
each one accepts, and the shape of the responses.

When you hand that file to mcp2cli with `--spec`, it reads every `paths` entry, converts each
HTTP operation into a CLI subcommand with typed flags, and lets you call any endpoint without
writing a single line of code.

## Basic usage

```bash
# Remote spec (JSON or YAML)
mcp2cli --spec https://petstore3.swagger.io/api/v3/openapi.json --list

# Local file
mcp2cli --spec ./openapi.yaml --base-url https://api.example.com --list

# Call an endpoint
mcp2cli --spec https://petstore3.swagger.io/api/v3/openapi.json \
  list-pets --status available --limit 5
```

`--base-url` is required when using a local file — the spec itself does not know the server address.

## How commands are named

mcp2cli derives a CLI name from the OpenAPI `operationId`:

| operationId | CLI command |
|---|---|
| `listPets` | `list-pets` |
| `createUser` | `create-user` |
| `getPetById` | `get-pet-by-id` |

When there is no `operationId`, the name is generated from the HTTP method and path
(e.g. `get-pets-petid`).

## Parameters

All parameter locations are supported:

| OpenAPI location | Behaviour |
|---|---|
| `path` | Substituted into the URL template |
| `query` | Appended to the query string |
| `header` | Sent as an HTTP header |
| `body` (JSON) | Sent as `application/json` |
| `body` (multipart) | Sent as `multipart/form-data`; binary fields take a local file path |

## Sending a JSON body

For `POST`/`PUT` endpoints with a JSON request body, pass body fields as flags:

```bash
mcp2cli --spec ./spec.json create-pet --name "Fido" --tag "dog" --age 3
```

Or pipe the entire body from stdin:

```bash
echo '{"name": "Fido", "tag": "dog"}' | mcp2cli --spec ./spec.json create-pet --stdin
```

`--stdin` always wins over individual flags when both are provided.

## Caching

Remote specs are cached in `~/.cache/mcp2cli/` for one hour. Override with:

```bash
# Force re-download
mcp2cli --spec https://api.example.com/spec.json --refresh --list

# Keep the cache for 24 hours
mcp2cli --spec https://api.example.com/spec.json --cache-ttl 86400 --list
```

## Filtering

When a spec is very large you can narrow which commands are exposed:

```bash
mcp2cli --spec ./spec.json --include "list-*,get-*" --list
mcp2cli --spec ./spec.json --exclude "delete-*" --list
mcp2cli --spec ./spec.json --methods GET,POST --list
```

These filters are most useful in combination with [bake mode](bake.md).
