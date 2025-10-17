# CLI Tests

Comprehensive test suite for the `cli.py` tool using pytest.

## Setup

Install dev dependencies:

```bash
uv sync --group dev
```

This will install:
- `pytest>=8.4.2` - Testing framework
- `pytest-mock>=3.14.0` - Mocking utilities

## Running Tests

### Run all tests
```bash
pytest
```

### Run with verbose output
```bash
pytest -v
```

### Run specific test file
```bash
pytest tests/test_cli.py
```

### Run specific test class
```bash
pytest tests/test_cli.py::TestNewCommand
```

### Run specific test
```bash
pytest tests/test_cli.py::TestNewCommand::test_new_project_with_template
```

### Run with coverage (if pytest-cov installed)
```bash
pytest --cov=cli --cov-report=html
```

## Test Structure

The test suite contains **22 comprehensive tests** organized into 5 test classes:

### `TestHelperFunctions` (6 tests)
Tests utility functions that power the CLI:
- ✅ `test_get_templates_dir` - Template directory resolution
- ✅ `test_get_projects_dir` - Projects directory resolution
- ✅ `test_list_available_templates` - Template listing
- ✅ `test_list_existing_projects` - Project listing
- ✅ `test_copy_tree_simple` - Basic directory copying
- ✅ `test_copy_tree_with_ignore_patterns` - Copying with exclusions

### `TestListCommand` (1 test)
Tests the `vibe list` command:
- ✅ `test_list_templates` - Verifies template listing output

### `TestNewCommand` (7 tests)
Tests the `vibe new <project-name>` command:
- ✅ `test_new_project_no_template` - Create empty project
- ✅ `test_new_project_with_template` - Create from template
- ✅ `test_new_project_already_exists` - Duplicate detection
- ✅ `test_new_project_invalid_template` - Invalid template handling
- ✅ `test_new_project_opens_cursor` - Cursor IDE integration
- ✅ `test_new_project_no_open_flag` - Skip Cursor opening
- ✅ `test_new_project_cursor_not_found` - Graceful degradation

### `TestOpenCommand` (3 tests)
Tests the `vibe open [project-name]` command:
- ✅ `test_open_lists_projects` - List available projects
- ✅ `test_open_specific_project` - Open existing project
- ✅ `test_open_nonexistent_project` - Error handling

### `TestMainCallback` (3 tests)
Tests the main entry point and CLI metadata:
- ✅ `test_no_command_shows_help` - Default help display
- ✅ `test_version_flag` - Version information
- ✅ `test_help_flag` - Help text

### `TestEdgeCases` (2 tests)
Tests edge cases and special scenarios:
- ✅ `test_project_with_special_characters` - Dashes, underscores
- ✅ `test_copy_tree_preserves_structure` - Nested directories

## Test Coverage Summary

| Category | Coverage |
|----------|----------|
| **Helper Functions** | ✅ Complete |
| **Commands** | ✅ All 3 commands tested |
| **Error Handling** | ✅ Invalid inputs, missing files |
| **Edge Cases** | ✅ Special characters, complex structures |
| **Integration** | ✅ Subprocess, file system operations |
| **User Interaction** | ✅ Interactive prompts, CLI output |

## Testing Approach

This test suite uses **integration-style testing** that:

1. **Tests against real filesystem** - Uses actual project/template directories with unique names
2. **Mocks external dependencies** - Subprocess calls (e.g., opening Cursor)
3. **Auto-cleanup** - Removes test projects after execution
4. **Unique naming** - Each test uses UUID-based names to avoid conflicts

### Key Testing Tools

- **`typer.testing.CliRunner`** - Invokes CLI commands in test environment
- **`unittest.mock.patch`** - Mocks subprocess calls
- **`pytest fixtures`** - Provides unique names and cleanup
- **`tmp_path`** - Pytest fixture for temporary directories (unit tests)

## Writing New Tests

When adding tests for new CLI functionality:

### 1. Add to appropriate test class

```python
class TestNewCommand:
    def test_my_new_feature(self, unique_name):
        """Test description."""
        runner = CliRunner()
        
        with patch("cli.subprocess.run"):
            result = runner.invoke(app, ["new", unique_name, "--my-flag"])
        
        assert result.exit_code == 0
        assert "expected output" in result.stdout
```

### 2. Use the AAA pattern

- **Arrange** - Set up test data, fixtures, mocks
- **Act** - Execute the CLI command
- **Assert** - Verify exit code and output

### 3. Handle interactive input

For commands that prompt for input, provide it via the `input` parameter:

```python
result = runner.invoke(app, ["new", "myproject"], input="0\n")  # Select option 0
```

### 4. Mock external calls

Always mock subprocess calls to prevent side effects:

```python
with patch("cli.subprocess.run") as mock_run:
    mock_run.return_value = MagicMock()
    result = runner.invoke(app, ["command"])
```

### 5. Clean up resources

Tests that create projects use the `unique_name` fixture for automatic cleanup.

## Continuous Integration

Example GitHub Actions workflow:

```yaml
name: Test

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Install uv
        run: curl -LsSf https://astral.sh/uv/install.sh | sh
      
      - name: Install dependencies
        run: uv sync --group dev
      
      - name: Run tests
        run: uv run pytest -v
```

## Test Results

Current status: **✅ 22/22 tests passing**

```
tests/test_cli.py::TestHelperFunctions::test_get_templates_dir PASSED
tests/test_cli.py::TestHelperFunctions::test_get_projects_dir PASSED
tests/test_cli.py::TestHelperFunctions::test_list_available_templates PASSED
tests/test_cli.py::TestHelperFunctions::test_list_existing_projects PASSED
tests/test_cli.py::TestHelperFunctions::test_copy_tree_simple PASSED
tests/test_cli.py::TestHelperFunctions::test_copy_tree_with_ignore_patterns PASSED
tests/test_cli.py::TestListCommand::test_list_templates PASSED
tests/test_cli.py::TestNewCommand::test_new_project_no_template PASSED
tests/test_cli.py::TestNewCommand::test_new_project_with_template PASSED
tests/test_cli.py::TestNewCommand::test_new_project_already_exists PASSED
tests/test_cli.py::TestNewCommand::test_new_project_invalid_template PASSED
tests/test_cli.py::TestNewCommand::test_new_project_opens_cursor PASSED
tests/test_cli.py::TestNewCommand::test_new_project_no_open_flag PASSED
tests/test_cli.py::TestNewCommand::test_new_project_cursor_not_found PASSED
tests/test_cli.py::TestOpenCommand::test_open_lists_projects PASSED
tests/test_cli.py::TestOpenCommand::test_open_specific_project PASSED
tests/test_cli.py::TestOpenCommand::test_open_nonexistent_project PASSED
tests/test_cli.py::TestMainCallback::test_no_command_shows_help PASSED
tests/test_cli.py::TestMainCallback::test_version_flag PASSED
tests/test_cli.py::TestMainCallback::test_help_flag PASSED
tests/test_cli.py::TestEdgeCases::test_project_with_special_characters PASSED
tests/test_cli.py::TestEdgeCases::test_copy_tree_preserves_structure PASSED
```

