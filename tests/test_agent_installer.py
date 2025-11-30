"""Tests for AI agent detection and installation modules.

Test Coverage:
- Agent detection across platforms (mocked)
- Config file parsing (valid/invalid JSON)
- Backup and restore operations
- Installation with various scenarios
- Error handling and rollback
- Cross-platform path resolution
"""

from __future__ import annotations

import json
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from mcp_skills.services.agent_detector import AgentDetector, DetectedAgent
from mcp_skills.services.agent_installer import AgentInstaller, InstallResult


class TestAgentDetector:
    """Test suite for AgentDetector."""

    def test_platform_detection(self):
        """Test platform normalization."""
        detector = AgentDetector()
        assert detector.platform in ["darwin", "win32", "linux"]

    @patch("platform.system")
    def test_darwin_platform(self, mock_system):
        """Test macOS platform detection."""
        mock_system.return_value = "Darwin"
        detector = AgentDetector()
        assert detector.platform == "darwin"

    @patch("platform.system")
    def test_windows_platform(self, mock_system):
        """Test Windows platform detection."""
        mock_system.return_value = "Windows"
        detector = AgentDetector()
        assert detector.platform == "win32"

    @patch("platform.system")
    def test_linux_platform(self, mock_system):
        """Test Linux platform detection."""
        mock_system.return_value = "Linux"
        detector = AgentDetector()
        assert detector.platform == "linux"

    def test_detect_all_returns_list(self):
        """Test that detect_all returns a list of DetectedAgent objects."""
        detector = AgentDetector()
        agents = detector.detect_all()

        assert isinstance(agents, list)
        assert len(agents) >= 3  # At least Claude Desktop, Claude Code, Auggie

        for agent in agents:
            assert isinstance(agent, DetectedAgent)
            assert agent.name
            assert agent.id
            assert isinstance(agent.config_path, Path)
            assert isinstance(agent.exists, bool)

    def test_detect_specific_agent_claude_desktop(self):
        """Test detecting Claude Desktop specifically."""
        detector = AgentDetector()
        agent = detector.detect_agent("claude-desktop")

        assert agent is not None
        assert agent.name == "Claude Desktop"
        assert agent.id == "claude-desktop"
        assert "Claude" in str(agent.config_path)

    def test_detect_specific_agent_claude_code(self):
        """Test detecting Claude Code specifically."""
        detector = AgentDetector()
        agent = detector.detect_agent("claude-code")

        assert agent is not None
        assert agent.name == "Claude Code"
        assert agent.id == "claude-code"
        assert "Code" in str(agent.config_path)

    def test_detect_unknown_agent(self):
        """Test detecting unknown agent returns None."""
        detector = AgentDetector()
        agent = detector.detect_agent("nonexistent-agent")

        assert agent is None

    def test_config_paths_are_absolute(self):
        """Test that all detected config paths are absolute."""
        detector = AgentDetector()
        agents = detector.detect_all()

        for agent in agents:
            assert agent.config_path.is_absolute()


class TestAgentInstaller:
    """Test suite for AgentInstaller."""

    @pytest.fixture
    def installer(self):
        """Create an AgentInstaller instance."""
        return AgentInstaller()

    @pytest.fixture
    def temp_agent(self, tmp_path):
        """Create a temporary detected agent for testing."""
        config_dir = tmp_path / "test_agent"
        config_dir.mkdir()
        config_path = config_dir / "config.json"

        return DetectedAgent(
            name="Test Agent",
            id="test-agent",
            config_path=config_path,
            exists=False,
        )

    def test_install_creates_new_config(self, installer, temp_agent, tmp_path):
        """Test installation creates new config when none exists."""
        result = installer.install(temp_agent)

        assert result.success
        assert result.agent_name == "Test Agent"
        assert result.config_path.exists()

        # Verify config content
        with open(result.config_path) as f:
            config = json.load(f)

        assert "mcpServers" in config
        assert "mcp-skillset" in config["mcpServers"]
        assert config["mcpServers"]["mcp-skillset"]["command"] == "mcp-skillset"

    def test_install_with_existing_config(self, installer, temp_agent):
        """Test installation updates existing config."""
        # Create existing config
        existing_config = {
            "someOtherSetting": "value",
            "mcpServers": {
                "other-server": {
                    "command": "other",
                    "args": [],
                }
            },
        }

        temp_agent.config_path.write_text(json.dumps(existing_config))
        temp_agent.exists = True

        result = installer.install(temp_agent)

        assert result.success

        # Verify config merged correctly
        with open(result.config_path) as f:
            config = json.load(f)

        assert config["someOtherSetting"] == "value"
        assert "other-server" in config["mcpServers"]
        assert "mcp-skillset" in config["mcpServers"]

    def test_install_creates_backup(self, installer, temp_agent):
        """Test that installation creates backup of existing config."""
        # Create existing config
        existing_config = {"existing": "data"}
        temp_agent.config_path.write_text(json.dumps(existing_config))
        temp_agent.exists = True

        result = installer.install(temp_agent)

        assert result.success
        assert result.backup_path is not None
        assert result.backup_path.exists()

        # Verify backup contains original data
        with open(result.backup_path) as f:
            backup_config = json.load(f)

        assert backup_config == existing_config

    def test_install_refuses_duplicate_without_force(self, installer, temp_agent):
        """Test installation fails if mcp-skillset already exists without --force."""
        # Create config with existing mcp-skillset
        existing_config = {
            "mcpServers": {
                "mcp-skillset": {
                    "command": "old-command",
                    "args": ["old"],
                }
            }
        }

        temp_agent.config_path.write_text(json.dumps(existing_config))
        temp_agent.exists = True

        result = installer.install(temp_agent, force=False)

        assert not result.success
        assert "already installed" in result.error

    def test_install_overwrites_with_force(self, installer, temp_agent):
        """Test installation overwrites existing mcp-skillset with --force."""
        # Create config with existing mcp-skillset
        existing_config = {
            "mcpServers": {
                "mcp-skillset": {
                    "command": "old-command",
                    "args": ["old"],
                }
            }
        }

        temp_agent.config_path.write_text(json.dumps(existing_config))
        temp_agent.exists = True

        result = installer.install(temp_agent, force=True)

        assert result.success

        # Verify new config
        with open(result.config_path) as f:
            config = json.load(f)

        assert config["mcpServers"]["mcp-skillset"]["command"] == "mcp-skillset"
        assert config["mcpServers"]["mcp-skillset"]["args"] == ["mcp"]

    def test_install_dry_run_no_changes(self, installer, temp_agent):
        """Test dry run mode doesn't modify files."""
        result = installer.install(temp_agent, dry_run=True)

        assert result.success
        assert "DRY RUN" in result.changes_made
        assert not temp_agent.config_path.exists()

    def test_install_handles_corrupted_json(self, installer, temp_agent):
        """Test installation fails gracefully with corrupted JSON."""
        # Write invalid JSON
        temp_agent.config_path.write_text("{ invalid json }")
        temp_agent.exists = True

        result = installer.install(temp_agent)

        assert not result.success
        assert "Failed to parse" in result.error

    def test_install_handles_missing_directory(self, installer, tmp_path):
        """Test installation fails when config directory doesn't exist."""
        nonexistent_dir = tmp_path / "nonexistent"
        config_path = nonexistent_dir / "config.json"

        agent = DetectedAgent(
            name="Test Agent",
            id="test-agent",
            config_path=config_path,
            exists=False,
        )

        result = installer.install(agent)

        assert not result.success
        assert "not found" in result.error

    def test_config_validation(self, installer):
        """Test configuration validation logic."""
        # Valid config
        valid_config = {
            "mcpServers": {
                "mcp-skillset": {
                    "command": "mcp-skillset",
                    "args": ["mcp"],
                    "env": {},
                }
            }
        }
        assert installer._validate_config(valid_config)

        # Missing mcpServers
        invalid_config = {"other": "data"}
        assert not installer._validate_config(invalid_config)

        # Invalid mcpServers type
        invalid_config = {"mcpServers": "not a dict"}
        assert not installer._validate_config(invalid_config)

        # Missing mcp-skillset
        invalid_config = {"mcpServers": {"other": {}}}
        assert not installer._validate_config(invalid_config)

        # Invalid mcp-skillset structure
        invalid_config = {
            "mcpServers": {
                "mcp-skillset": {
                    "command": "mcp-skillset",
                    # Missing 'args'
                }
            }
        }
        assert not installer._validate_config(invalid_config)

    def test_backup_path_format(self, installer, temp_agent):
        """Test backup file naming includes timestamp."""
        # Create existing config
        temp_agent.config_path.write_text("{}")
        temp_agent.exists = True

        result = installer.install(temp_agent)

        assert result.success
        assert result.backup_path is not None

        # Verify backup filename format
        backup_name = result.backup_path.name
        assert backup_name.startswith("config.json.backup.")
        assert len(backup_name.split(".")) >= 4  # name.json.backup.timestamp

    def test_install_preserves_json_formatting(self, installer, temp_agent):
        """Test that installed config is properly formatted JSON."""
        result = installer.install(temp_agent)

        assert result.success

        # Read and verify formatting
        config_text = result.config_path.read_text()

        # Should be valid JSON
        config = json.loads(config_text)
        assert isinstance(config, dict)

        # Should be pretty-printed (has indentation)
        assert "  " in config_text or "\t" in config_text

        # Should have trailing newline
        assert config_text.endswith("\n")

    def test_describe_changes_new_config(self, installer, temp_agent):
        """Test change description for new config."""
        description = installer._describe_changes({})
        assert "new config" in description.lower()

    def test_describe_changes_existing_config(self, installer, temp_agent):
        """Test change description for existing config."""
        existing = {"mcpServers": {"other": {}}}
        description = installer._describe_changes(existing)
        assert "add" in description.lower() or "mcp-skillset" in description.lower()

    def test_describe_changes_update_existing(self, installer, temp_agent):
        """Test change description when updating existing mcp-skillset."""
        existing = {"mcpServers": {"mcp-skillset": {"command": "old"}}}
        description = installer._describe_changes(existing)
        assert "update" in description.lower()


class TestClaudeCLIIntegration:
    """Test suite for Claude CLI integration (1M-432)."""

    @pytest.fixture
    def installer(self):
        """Create an AgentInstaller instance."""
        return AgentInstaller()

    @pytest.fixture
    def claude_code_agent(self, tmp_path):
        """Create a Claude Code agent for testing."""
        config_path = tmp_path / "Code" / "settings.json"
        return DetectedAgent(
            name="Claude Code",
            id="claude-code",
            config_path=config_path,
            exists=False,
        )

    @pytest.fixture
    def claude_desktop_agent(self, tmp_path):
        """Create a Claude Desktop agent for testing."""
        config_path = tmp_path / "Claude" / "claude_desktop_config.json"
        return DetectedAgent(
            name="Claude Desktop",
            id="claude-desktop",
            config_path=config_path,
            exists=False,
        )

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_installation_success(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test successful Claude CLI installation.

        Verifies that when the claude CLI is available and the add command
        succeeds, the installation completes successfully.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock get command failure (server doesn't exist), then add success
        mock_run.side_effect = [
            Mock(returncode=1, stdout="", stderr="Not found"),  # get fails
            Mock(returncode=0, stdout="", stderr=""),  # add succeeds
        ]

        # Install
        result = installer.install(claude_code_agent)

        # Verify success
        assert result.success
        assert result.agent_name == "Claude Code"
        assert result.agent_id == "claude-code"
        assert "Claude CLI" in result.changes_made

        # Verify subprocess calls (get and add)
        assert mock_run.call_count == 2

        # Verify get command
        get_call = mock_run.call_args_list[0][0][0]
        assert "claude" in get_call
        assert "mcp" in get_call
        assert "get" in get_call
        assert "mcp-skillset" in get_call

        # Verify add command
        add_call = mock_run.call_args_list[1][0][0]
        assert "claude" in add_call
        assert "mcp" in add_call
        assert "add" in add_call
        assert "mcp-skillset" in add_call

    @patch("shutil.which")
    def test_claude_cli_not_found(self, mock_which, installer, claude_code_agent):
        """Test error when Claude CLI is not found.

        Verifies that installation fails with clear error message when
        the claude CLI is not available on the system.
        """
        # Mock CLI not available
        mock_which.return_value = None

        # Install
        result = installer.install(claude_code_agent)

        # Verify failure
        assert not result.success
        assert result.error is not None
        assert "CLI not found" in result.error
        assert "install Claude Code" in result.error

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_already_installed(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test detection of already installed server.

        Verifies that without --force flag, installation fails when
        mcp-skillset is already installed.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock 'get' command returning success (server exists)
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Install without force
        result = installer.install(claude_code_agent, force=False)

        # Verify failure
        assert not result.success
        assert result.error is not None
        assert "already installed" in result.error
        assert "--force" in result.error

        # Verify 'get' command was called
        call_args = mock_run.call_args[0][0]
        assert "claude" in call_args
        assert "mcp" in call_args
        assert "get" in call_args
        assert "mcp-skillset" in call_args

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_force_reinstall(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test force reinstall workflow.

        Verifies that with --force flag, installation removes existing
        server and adds it again.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock successful CLI commands
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Install with force
        result = installer.install(claude_code_agent, force=True)

        # Verify success
        assert result.success
        assert "Claude CLI" in result.changes_made

        # Verify both remove and add commands were called
        assert mock_run.call_count >= 2

        # Check remove command
        remove_call = mock_run.call_args_list[0][0][0]
        assert "claude" in remove_call
        assert "mcp" in remove_call
        assert "remove" in remove_call
        assert "mcp-skillset" in remove_call

        # Check add command
        add_call = mock_run.call_args_list[1][0][0]
        assert "claude" in add_call
        assert "mcp" in add_call
        assert "add" in add_call
        assert "mcp-skillset" in add_call

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_dry_run(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test dry-run mode.

        Verifies that dry-run mode shows what would be done without
        actually making any changes.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock get command failure (server doesn't exist)
        mock_run.return_value = Mock(returncode=1, stdout="", stderr="Not found")

        # Install in dry-run mode
        result = installer.install(claude_code_agent, dry_run=True)

        # Verify success but no actual execution
        assert result.success
        assert result.changes_made is not None
        assert "[DRY RUN]" in result.changes_made
        assert "claude mcp add" in result.changes_made
        assert "mcp-skillset" in result.changes_made

        # Verify only get was called (to check if installed), not add/remove
        assert mock_run.call_count == 1
        call_args = mock_run.call_args[0][0]
        assert "get" in call_args

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_dry_run_with_force(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test dry-run mode with force flag.

        Verifies that dry-run mode shows both remove and add commands
        when force flag is used.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Install in dry-run mode with force
        result = installer.install(claude_code_agent, dry_run=True, force=True)

        # Verify success
        assert result.success
        assert "[DRY RUN]" in result.changes_made
        assert "remove" in result.changes_made
        assert "add" in result.changes_made

        # Verify NO subprocess calls
        assert not mock_run.called

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_add_command_fails(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test handling of failed add command.

        Verifies that installation fails gracefully when the CLI
        add command returns an error.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock failed add command
        mock_run.return_value = Mock(
            returncode=1,
            stdout="",
            stderr="Error: Failed to add MCP server",
        )

        # Install
        result = installer.install(claude_code_agent)

        # Verify failure
        assert not result.success
        assert result.error is not None
        assert "Failed to add" in result.error
        assert "Error:" in result.error

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_get_command_fails_allows_install(
        self, mock_which, mock_run, installer, claude_code_agent
    ):
        """Test that failed 'get' command allows installation.

        When checking if server exists fails (e.g., server doesn't exist),
        installation should proceed without force flag.
        """
        # Mock CLI available
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock get command failure (server doesn't exist), then add success
        mock_run.side_effect = [
            Mock(returncode=1, stdout="", stderr="Not found"),  # get fails
            Mock(returncode=0, stdout="", stderr=""),  # add succeeds
        ]

        # Install without force
        result = installer.install(claude_code_agent, force=False)

        # Verify success (should proceed since get failed)
        assert result.success
        assert "Claude CLI" in result.changes_made

    def test_backward_compatibility_claude_desktop(
        self, installer, claude_desktop_agent, tmp_path
    ):
        """Test backward compatibility with Claude Desktop.

        Verifies that Claude Desktop still uses JSON config file method
        and NOT the CLI method.
        """
        # Create config directory
        claude_desktop_agent.config_path.parent.mkdir(parents=True, exist_ok=True)

        # Install for Claude Desktop (should use JSON method)
        with patch("subprocess.run") as mock_run:
            result = installer.install(claude_desktop_agent)

            # Verify subprocess was NOT called (JSON method doesn't use subprocess)
            assert not mock_run.called

        # Verify config file was created (JSON method)
        assert result.success
        assert claude_desktop_agent.config_path.exists()

        # Verify it's valid JSON config
        with open(claude_desktop_agent.config_path) as f:
            config = json.load(f)
        assert "mcpServers" in config
        assert "mcp-skillset" in config["mcpServers"]

    @patch("subprocess.run")
    @patch("shutil.which")
    def test_claude_cli_routing_based_on_agent_id(
        self,
        mock_which,
        mock_run,
        installer,
        claude_code_agent,
        claude_desktop_agent,
        tmp_path,
    ):
        """Test that installation method is routed based on agent ID.

        Verifies that:
        - claude-code uses CLI method
        - claude-desktop uses JSON method
        """
        # Setup for CLI test
        mock_which.return_value = "/usr/local/bin/claude"

        # Mock get command failure (server doesn't exist), then add success
        mock_run.side_effect = [
            Mock(returncode=1, stdout="", stderr="Not found"),  # get fails
            Mock(returncode=0, stdout="", stderr=""),  # add succeeds
        ]

        # Install Claude Code (should use CLI)
        result_code = installer.install(claude_code_agent)
        assert result_code.success
        assert mock_run.call_count == 2  # get + add

        # Reset mocks
        mock_run.reset_mock()

        # Install Claude Desktop (should NOT use CLI)
        claude_desktop_agent.config_path.parent.mkdir(parents=True, exist_ok=True)
        result_desktop = installer.install(claude_desktop_agent)
        assert result_desktop.success
        assert not mock_run.called  # JSON method doesn't call subprocess


class TestCrossPlatformPaths:
    """Test cross-platform path resolution."""

    @patch("platform.system")
    def test_claude_desktop_paths_darwin(self, mock_system):
        """Test Claude Desktop paths on macOS."""
        mock_system.return_value = "Darwin"
        detector = AgentDetector()
        agent = detector.detect_agent("claude-desktop")

        assert agent is not None
        assert "Library/Application Support/Claude" in str(agent.config_path)

    @patch("platform.system")
    def test_claude_desktop_paths_linux(self, mock_system):
        """Test Claude Desktop paths on Linux."""
        mock_system.return_value = "Linux"
        detector = AgentDetector()
        agent = detector.detect_agent("claude-desktop")

        assert agent is not None
        assert ".config/Claude" in str(agent.config_path)

    @patch("platform.system")
    @patch.dict("os.environ", {"APPDATA": "C:\\Users\\Test\\AppData\\Roaming"})
    def test_claude_desktop_paths_windows(self, mock_system):
        """Test Claude Desktop paths on Windows."""
        mock_system.return_value = "Windows"
        detector = AgentDetector()
        agent = detector.detect_agent("claude-desktop")

        assert agent is not None
        # Windows path should contain Claude directory


class TestInstallResult:
    """Test InstallResult data class."""

    def test_install_result_success(self):
        """Test creating successful InstallResult."""
        result = InstallResult(
            success=True,
            agent_name="Test Agent",
            agent_id="test-agent",
            config_path=Path("/test/path"),
            backup_path=Path("/test/backup"),
            changes_made="Added mcp-skillset",
        )

        assert result.success
        assert result.agent_name == "Test Agent"
        assert result.error is None

    def test_install_result_failure(self):
        """Test creating failed InstallResult."""
        result = InstallResult(
            success=False,
            agent_name="Test Agent",
            agent_id="test-agent",
            config_path=Path("/test/path"),
            error="Something went wrong",
        )

        assert not result.success
        assert result.error == "Something went wrong"
        assert result.backup_path is None


class TestAgentNameDetection:
    """Test suite for agent name detection bug fixes."""

    def test_claude_code_name_is_correct(self):
        """Test that Claude Code is detected with correct name (Bug Fix #2)."""
        detector = AgentDetector()
        agent = detector.detect_agent("claude-code")

        assert agent is not None
        assert agent.name == "Claude Code"
        assert agent.id == "claude-code"
        assert "Code" in str(agent.config_path)
        assert "settings.json" in str(agent.config_path)

    def test_claude_desktop_name_is_correct(self):
        """Test that Claude Desktop is detected with correct name (Bug Fix #2)."""
        detector = AgentDetector()
        agent = detector.detect_agent("claude-desktop")

        assert agent is not None
        assert agent.name == "Claude Desktop"
        assert agent.id == "claude-desktop"
        assert "Claude" in str(agent.config_path)
        assert "claude_desktop_config.json" in str(agent.config_path)

    def test_all_agents_have_unique_names(self):
        """Test that all detected agents have unique, correct names."""
        detector = AgentDetector()
        agents = detector.detect_all()

        # Collect agent names
        names = {agent.name for agent in agents}

        # Verify expected agents have correct names
        assert "Claude Desktop" in names
        assert "Claude Code" in names
        assert "Auggie" in names

        # Verify no duplicate names
        assert len(names) == len(agents)

    def test_agent_name_matches_config_path(self):
        """Test that agent names correctly match their config paths."""
        detector = AgentDetector()
        agents = detector.detect_all()

        for agent in agents:
            if agent.id == "claude-desktop":
                assert agent.name == "Claude Desktop"
                assert "Claude" in str(agent.config_path)
                assert "claude_desktop_config.json" in str(agent.config_path)
            elif agent.id == "claude-code":
                assert agent.name == "Claude Code"
                assert "Code" in str(agent.config_path)
                assert "settings.json" in str(agent.config_path)
            elif agent.id == "auggie":
                assert agent.name == "Auggie"
                assert "Auggie" in str(agent.config_path)
