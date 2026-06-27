import os
import subprocess
import tempfile
from pathlib import Path

def test_bake_install_groups_script():
    # Create a temporary directory to act as sandbox
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir_path = Path(tmpdir)
        
        # Path to the script under test
        script_path = Path(__file__).parent.parent.parent / "mcp2cli-bake-install-groups.sh"
        assert script_path.exists(), f"Script not found at {script_path}"
        
        # We will create a mock mcp2cli executable in our temporary directory
        mock_mcp2cli = tmpdir_path / "mcp2cli"
        mock_mcp2cli_content = """#!/usr/bin/env bash
# Log the arguments for verification
echo "MOCK_CALLED: $@" >> "$MOCK_LOG"

if [ "$1" = "--mcp" ] && [ "$3" = "--compact" ]; then
    echo "foo--bar foo--baz abc--def xyz--item unrelated-tool"
    exit 0
elif [ "$1" = "bake" ] && [ "$2" = "create" ]; then
    echo "Created baked config for $3"
    exit 0
elif [ "$1" = "bake" ] && [ "$2" = "install" ]; then
    echo "Installed wrapper: $3"
    exit 0
else
    echo "Unknown mock arguments: $@" >&2
    exit 1
fi
"""
        mock_mcp2cli.write_text(mock_mcp2cli_content)
        mock_mcp2cli.chmod(0o755)
        
        # Prepare environment
        env = os.environ.copy()
        # Prepend tmpdir to PATH so our mock mcp2cli is picked up
        env["PATH"] = f"{tmpdir}:{env.get('PATH', '')}"
        
        # Log file path for mock calls
        log_file = tmpdir_path / "mock_calls.log"
        env["MOCK_LOG"] = str(log_file)
        
        # Explicitly set MCP2CLI_BIN to 'mcp2cli' to use PATH resolution
        env["MCP2CLI_BIN"] = "mcp2cli"
        
        # Run the script
        result = subprocess.run(
            [str(script_path), "http://localhost:8000/sse"],
            env=env,
            capture_output=True,
            text=True
        )
        
        # Verify execution
        assert result.returncode == 0, f"Script failed with output:\nSTDOUT:\n{result.stdout}\nSTDERR:\n{result.stderr}"
        
        # Check stdout contents
        assert "Found the following unique group name(s):" in result.stdout
        assert "- abc" in result.stdout
        assert "- foo" in result.stdout
        assert "- xyz" in result.stdout
        # "unrelated-tool" has no double hyphen, so it should not be a group
        assert "- unrelated-tool" not in result.stdout
        
        # Verify the mock calls logged
        assert log_file.exists()
        calls = log_file.read_text().splitlines()
        
        # The first call should be listing the tools
        assert "--mcp http://localhost:8000/sse --compact" in calls[0]
        
        # The remaining calls should be bake create / install for abc, foo, xyz in sorted order
        # groups are: abc, foo, xyz
        expected_calls = [
            "bake create abc --mcp http://localhost:8000/sse --include abc--* --force",
            "bake install abc",
            "bake create foo --mcp http://localhost:8000/sse --include foo--* --force",
            "bake install foo",
            "bake create xyz --mcp http://localhost:8000/sse --include xyz--* --force",
            "bake install xyz"
        ]
        
        # Filter calls file to look only for the actual bake commands
        bake_calls = [c.replace("MOCK_CALLED: ", "") for c in calls if "bake" in c]
        assert bake_calls == expected_calls
