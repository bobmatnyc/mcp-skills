# Verification Commands for Package Rename

## Quick Verification

```bash
# 1. Check package is installed with correct name
source .venv/bin/activate
pip show mcp-skillkit | grep Name
# Expected: Name: mcp-skillkit

# 2. Verify CLI command works
mcp-skillkit --version
# Expected: mcp-skillkit, version 0.1.0

# 3. Test main commands
mcp-skillkit --help
mcp-skillkit search --help
mcp-skillkit setup --help

# 4. Verify completions exist
ls -la completions/
# Expected: mcp-skillkit-completion.{bash,zsh,fish}

# 5. Test completion generation
./scripts/generate_completions.sh
# Expected: Success for all three shells
```

## Comprehensive Verification

```bash
# Check all documentation references
grep -r "mcp-skills[^-]" README.md docs/ --include="*.md" | wc -l
# Expected: 0 (all should be mcp-skillkit now)

# Check pyproject.toml
grep "^name = " pyproject.toml
# Expected: name = "mcp-skillkit"

grep "mcp-skillkit = " pyproject.toml
# Expected: mcp-skillkit = "mcp_skills.cli.main:cli"

# Verify dev script renamed
ls -la | grep "mcp-skill.*-dev"
# Expected: mcp-skillkit-dev (not mcp-skills-dev)

# Check GitHub URLs
grep "github.com/bobmatnyc" pyproject.toml
# Expected: All URLs contain mcp-skillkit

# Test Python import
python -c "import mcp_skills; print('✅ Import successful')"
# Expected: ✅ Import successful
```

## Test Installation Flow

```bash
# Simulate fresh install
pip uninstall -y mcp-skillkit
pip install -e .

# Verify command available
which mcp-skillkit
# Expected: /path/to/.venv/bin/mcp-skillkit

# Test basic functionality
mcp-skillkit config
mcp-skillkit health
```

## Shell Completion Testing

### Bash
```bash
source completions/mcp-skillkit-completion.bash
# Type: mcp-skillkit <TAB>
# Expected: Shows all commands (config, health, index, info, list, mcp, recommend, repo, search, setup, stats)
```

### Zsh
```bash
source completions/mcp-skillkit-completion.zsh
# Type: mcp-skillkit <TAB>
# Expected: Shows all commands with descriptions
```

### Fish
```bash
source completions/mcp-skillkit-completion.fish
# Type: mcp-skillkit <TAB>
# Expected: Shows all commands
```

## Build Testing

```bash
# Clean previous builds
rm -rf dist/ build/ *.egg-info

# Build new package
python -m build

# Check distribution files
ls -la dist/
# Expected: mcp_skillkit-0.1.0.tar.gz and mcp_skillkit-0.1.0-py3-none-any.whl

# Verify wheel contents
unzip -l dist/mcp_skillkit-0.1.0-py3-none-any.whl | grep "scripts"
# Expected: Should show mcp-skillkit entry point
```

## PyPI Upload Testing (Dry Run)

```bash
# Install twine if needed
pip install twine

# Check package
twine check dist/*
# Expected: Checking dist/mcp_skillkit-0.1.0.tar.gz: PASSED

# Test upload (doesn't actually upload)
# twine upload --repository testpypi dist/*
```

## Regression Testing

```bash
# Run test suite
pytest tests/ -v

# Run specific tests that reference CLI
pytest tests/test_cli.py -v
pytest tests/e2e/test_cli_commands.py -v

# Check for any failing tests due to rename
pytest tests/ -k "setup or cli" -v
```

## Files to Check Manually

1. **README.md**: All command examples use `mcp-skillkit`
2. **pyproject.toml**: Package name and CLI entry point correct
3. **docs/SHELL_COMPLETIONS.md**: All references updated
4. **completions/**: Only `mcp-skillkit-completion.*` files exist
5. **scripts/generate_completions.sh**: Uses correct command name

## Success Criteria

- ✅ Package name is `mcp-skillkit`
- ✅ CLI command is `mcp-skillkit`
- ✅ All documentation uses `mcp-skillkit`
- ✅ Shell completions work with `mcp-skillkit`
- ✅ All tests pass
- ✅ No references to `mcp-skills` command (only package/directory names)
- ✅ GitHub URLs point to `mcp-skillkit` repository
- ✅ PyPI badges reference `mcp-skillkit`
