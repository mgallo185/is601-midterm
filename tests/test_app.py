"""Test suite for the App class."""
import logging
import os
from unittest.mock import patch, MagicMock
import pytest

from app import App
from app.commands import Command

@pytest.fixture
def setup_env_vars():
    """Set up test environment variables."""
    old_env = os.environ.copy()
    os.environ['APP_NAME'] = 'TestApp'
    os.environ['ENVIRONMENT'] = 'TEST'
    os.environ['COMMAND_HISTORY_SIZE'] = '50'
    os.environ['DEBUG_MODE'] = 'True'
    os.environ['LOG_LEVEL'] = 'DEBUG'
    yield
    os.environ.clear()
    os.environ.update(old_env)


def test_app_initialization(setup_env_vars):
    """Test that the App initializes correctly with env variables."""
    with patch('app.CommandHandler') as mock_handler:
        with patch('app.App.load_plugins') as mock_load_plugins:
            app = App()

            # Check that environment variables were correctly loaded
            assert app.app_name == 'TestApp'
            assert app.environment == 'TEST'
            assert app.command_history_size == 50

            # Verify that command handler was initialized
            mock_handler.assert_called_once()

            # Verify that plugins were loaded
            mock_load_plugins.assert_called_once()


def test_app_default_initialization():
    """Test that the App initializes correctly with default values."""
    with patch('app.CommandHandler'):
        with patch('app.App.load_plugins'):
            with patch.dict(os.environ, {}, clear=True):  # Clear all env variables
                app = App()

                # Check that default values were used
                assert app.app_name == 'Calculator'
                assert app.environment == 'PRODUCTION'
                assert app.command_history_size == 100


def test_app_start_exit_command(monkeypatch):
    """Test that the REPL exits correctly on 'exit' command."""
    # Simulate user entering 'exit' to end the loop
    monkeypatch.setattr('builtins.input', lambda _: 'exit')

    app = App()

    # Use pytest's 'monkeypatch' to avoid running the REPL in an infinite loop
    with pytest.raises(SystemExit):  # Expect a SystemExit exception to indicate termination
        app.start()  # Should exit the loop and raise a SystemExit


def test_app_start_unknown_command(capfd, monkeypatch):
    """Test how the REPL handles an unknown command before exiting."""
    # Simulate user entering an unknown command followed by 'exit'
    inputs = iter(['unknown_command', 'exit'])  # Input sequence to simulate user behavior
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))  # Mock the input function

    app = App()

    # Catch the SystemExit to test the exit behavior
    with pytest.raises(SystemExit):
        app.start()

    # Optionally, check for specific output
    captured = capfd.readouterr()
    assert "No such command: unknown_command" in captured.out

def test_plugin_load_success_and_failure(caplog, monkeypatch):
    """Test both successful and failed plugin loading."""
    # Set up logging to capture logs - redirect root logger to caplog
    monkeypatch.setattr('app.configure_logging', lambda: None)  # Disable app's logging configuration
    logging.basicConfig(level=logging.INFO)  # Set up basic logging for pytest to capture

    # Create a mock CommandHandler
    mock_command_handler = MagicMock()

    # Create a mock Command class
    mock_command_class = MagicMock(spec=Command)

    # Create a mock module with a Command subclass
    mock_module = MagicMock()
    mock_module.__name__ = "working_plugin"
    # Add the mock command class to the module's attributes
    mock_module.SomeCommand = mock_command_class

    def mock_import_module(name):
        """Mock import_module to handle both success and failure cases."""
        if 'broken_plugin' in name:
            raise ImportError("Mock import error")
        return mock_module

    # Mock iter_modules to return both a working and broken plugin
    with patch('pkgutil.iter_modules', return_value=[('', 'working_plugin', ''), ('', 'broken_plugin', '')]):
        # Mock importlib.import_module
        with patch('importlib.import_module', side_effect=mock_import_module):
            # Mock CommandHandler to avoid its initialization
            with patch('app.commands.CommandHandler', return_value=mock_command_handler):
                # Mock issubclass to always return True for our mock command class
                with patch('inspect.issubclass', return_value=True):
                    # Create app instance which will trigger plugin loading
                    _ = App()

    # Check logs in stderr instead of caplog.text
    stderr_logs = caplog.text
    assert "Failed to load plugin broken_plugin" in stderr_logs or "Failed to load plugin broken_plugin" in caplog.records
    assert "Attempting to load plugin: working_plugin" in stderr_logs or "Attempting to load plugin: working_plugin" in caplog.records

def test_app_command_with_args(capfd, monkeypatch):
    """Test executing a command with arguments."""
    # Simulate user entering a command with arguments, then exit
    inputs = iter(['add 5 3', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    app = App()

    # Catch the SystemExit to test the exit behavior
    with pytest.raises(SystemExit):
        app.start()


def test_app_command_execution_error(capfd, monkeypatch):
    """Test how the REPL handles a command execution error."""
    # Simulate user entering a command that raises an error, then exit
    inputs = iter(['error_command', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    app = App()

    # Mock command_handler to raise an exception for the error_command
    app.command_handler = MagicMock()
    app.command_handler.execute_command.side_effect = [None, Exception("Command execution error"), None]

    # Catch the SystemExit to test the exit behavior
    with pytest.raises(SystemExit):
        app.start()
    # Check the error was handled
    captured = capfd.readouterr()
    assert "An error occurred" in captured.out


def test_app_keyboard_interrupt(capfd, monkeypatch):
    """Test how the REPL handles a keyboard interrupt (Ctrl+C)."""
    # Simulate user pressing Ctrl+C, then entering 'exit'
    inputs = [KeyboardInterrupt(), 'exit']
    input_mock = MagicMock(side_effect=inputs)
    monkeypatch.setattr('builtins.input', input_mock)

    app = App()
    app.command_handler = MagicMock()

    with pytest.raises(SystemExit):
        app.start()

    # Check the interrupt was handled
    captured = capfd.readouterr()
    assert "Interrupted" in captured.out


def test_app_eof_error(capfd, monkeypatch):
    """Test how the REPL handles an EOFError (Ctrl+D)."""
    # Simulate user pressing Ctrl+D
    monkeypatch.setattr('builtins.input', MagicMock(side_effect=EOFError()))

    app = App()
    app.command_handler = MagicMock()

    with pytest.raises(SystemExit):
        app.start()

    # Check the EOF was handled
    captured = capfd.readouterr()
    assert "Exiting" in captured.out


def test_app_unexpected_error(capfd, monkeypatch):
    """Test how the REPL handles an unexpected error."""
    # Simulate an unexpected error, then exit
    inputs = [RuntimeError("Unexpected error"), 'exit']
    input_mock = MagicMock(side_effect=inputs)
    monkeypatch.setattr('builtins.input', input_mock)

    app = App()
    app.command_handler = MagicMock()

    with pytest.raises(SystemExit):
        app.start()

    # Check the error was handled
    captured = capfd.readouterr()
    assert "An unexpected error occurred" in captured.out


def test_empty_input_handling(capfd, monkeypatch):
    """Test how the REPL handles empty input."""
    # Simulate user entering empty string, then exit
    inputs = iter(['', 'exit'])
    monkeypatch.setattr('builtins.input', lambda _: next(inputs))

    app = App()
    app.command_handler = MagicMock()

    with pytest.raises(SystemExit):
        app.start()

    # Verify command handler wasn't called for empty input
    assert app.command_handler.execute_command.call_count == 1  # Only for menu at startup

def test_menu_display_error(capfd, monkeypatch):
    """Test fallback message when menu display fails at startup."""
    # Mock command_handler.execute_command to raise an exception for the menu command
    mock_command_handler = MagicMock()
    mock_command_handler.execute_command.side_effect = Exception("Menu display error")

    # Simulate user entering 'exit' to end the loop
    monkeypatch.setattr('builtins.input', lambda _: 'exit')

    # Create the app and replace its command handler with our mock
    with patch('app.CommandHandler', return_value=mock_command_handler):
        app = App()

        # Use pytest's monkeypatch to avoid running the REPL in an infinite loop
        with pytest.raises(SystemExit):
            app.start()

    # Check the captured output for the fallback message
    captured = capfd.readouterr()
    assert "Type 'help' or 'menu' to see available commands" in captured.out

    # Verify the command handler tried to execute the menu command
    mock_command_handler.execute_command.assert_called_with("menu")
