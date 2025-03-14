"""Test suite for the App class."""
import importlib
import logging
import os
from unittest.mock import patch, MagicMock, call
import pytest

from app import App


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
    # Set up logging to capture ERROR level logs
    caplog.set_level(logging.ERROR)

    def mock_import_module(name):
        """Mock import_module to handle both success and failure cases."""
        if 'broken_plugin' in name:
            raise ImportError("Mock import error")
        return importlib.__import__('builtins')  # Return a real module for success case

    # Mock pkgutil.iter_modules to return both a working and broken plugin
    monkeypatch.setattr('pkgutil.iter_modules',
                       lambda _: [('', 'working_plugin', ''), ('', 'broken_plugin', '')])
    # Mock importlib.import_module
    monkeypatch.setattr('importlib.import_module', mock_import_module)
    # Create app instance which will trigger plugin loading
    _ = App()

# Check that the error was logged
    assert "Failed to load plugin broken_plugin" in caplog.text

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

