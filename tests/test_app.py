"""Test suite for the App class."""
import importlib
import logging
import pytest
from app import App


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
