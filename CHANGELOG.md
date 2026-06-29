# Changelog

## [3.1.0] — current

### Added
- `mcp2cli-bake-install-groups.sh` helper script: auto-creates and installs one baked config per
  tool-name prefix (`group--action` convention) found on an MCP server.
- `docs/` directory with beginner-friendly guides: MCP, OpenAPI, GraphQL, Bake, Authentication.
- CI test workflow (`.github/workflows/test.yml`) running pytest on Python 3.10, 3.11, 3.12.
- `[tool.ruff]`, `[tool.mypy]`, and `[tool.pytest.ini_options]` sections in `pyproject.toml`.
- `Documentation` URL in `[project.urls]`.

### Changed
- `pyproject.toml` description updated to mention GraphQL alongside MCP and OpenAPI.
- `assets/hero.png` re-compressed (3.1 MB → 920 KB).

### Fixed
- `tests/test_bake_install_groups.py` path lookup corrected to find the script inside the repo
  root (`parent.parent`) instead of the parent directory (`parent.parent.parent`).

---

## [3.0.x] — upstream history

For earlier history see the upstream repository:
<https://github.com/knowsuchagency/mcp2cli>
