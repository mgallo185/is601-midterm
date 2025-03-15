"""Test suite for HistoryCommand class."""
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd
from app.plugins.history_command import HistoryCommand
from app.calculation.history import History

@pytest.fixture
def history_command():
    """Fixture to create HistoryCommand instance."""
    command_handler = MagicMock()
    return HistoryCommand(command_handler)

@pytest.fixture
def mock_calculations():
    """Fixture to create mock calculation objects."""
    mock_calc1 = MagicMock(a=5, b=3, operation=MagicMock(__name__="add"))
    mock_calc1.perform.return_value = 8

    mock_calc2 = MagicMock(a=10, b=2, operation=MagicMock(__name__="multiply"))
    mock_calc2.perform.return_value = 20

    return [mock_calc1, mock_calc2]

@pytest.fixture(autouse=True)
def clear_history():
    """Clear history before and after each test."""
    History.clear_history()
    yield
    History.clear_history()

class TestHistoryCommand:
    """Tests for the HistoryCommand class."""

    def _execute_and_capture(self, history_command, capsys, *args):
        """Helper method to execute a command and capture output."""
        history_command.execute(*args)
        return capsys.readouterr()

    def test_display_history(self, history_command, capsys, mock_calculations):
        """Test displaying empty and non-empty history."""
        with patch('app.calculation.history.History.get_history', return_value=[]):
            captured = self._execute_and_capture(history_command, capsys)
            assert "No calculations in history" in captured.out

        with patch('app.calculation.history.History.get_history', return_value=mock_calculations):
            captured = self._execute_and_capture(history_command, capsys, "show")
            assert "5 add 3 = 8" in captured.out
            assert "10 multiply 2 = 20" in captured.out

    def test_clear_history(self, history_command, capsys):
        """Test clearing history with successful and failed save."""
        # Test when both clearing and saving succeed
        with patch('app.calculation.history.History.clear_history') as mock_clear, \
            patch('app.calculation.history.History.save_to_csv', return_value=True):
            captured = self._execute_and_capture(history_command, capsys, "clear")
            mock_clear.assert_called_once()
            assert "History cleared and saved file updated." in captured.out
        # Test when clearing succeeds but saving fails
        with patch('app.calculation.history.History.clear_history') as mock_clear, \
            patch('app.calculation.history.History.save_to_csv', return_value=False):
            captured = self._execute_and_capture(history_command, capsys, "clear")
            mock_clear.assert_called_once()
            assert "History cleared in memory, but there was an issue updating the file." in captured.out

    @pytest.mark.parametrize("save_return, expected_output", [
        (True, "History saved to"), (False, "No history to save")
    ])
    def test_save_history(self, history_command, capsys, save_return, expected_output):
        """Test saving history with different outcomes."""
        with patch('app.calculation.history.History.ensure_data_directory', return_value=True), \
             patch('app.calculation.history.History.save_to_csv', return_value=save_return):
            captured = self._execute_and_capture(history_command, capsys, "save")
            assert expected_output in captured.out

    def test_save_history_failures(self, history_command, capsys):
        """Test errors during history saving."""
        with patch('app.calculation.history.History.ensure_data_directory', return_value=False):
            captured = self._execute_and_capture(history_command, capsys, "save")
            assert "Error: Data directory not accessible" in captured.out

        with patch('app.calculation.history.History.ensure_data_directory', return_value=True), \
             patch('app.calculation.history.History.save_to_csv', side_effect=Exception("Test save error")):
            captured = self._execute_and_capture(history_command, capsys, "save")
            assert "Error: Test save error" in captured.out

    def test_load_history(self, history_command, capsys):
        """Test loading history scenarios."""
        with patch('os.path.exists', return_value=True), \
             patch('app.calculation.history.History.load_from_csv', return_value=True):
            captured = self._execute_and_capture(history_command, capsys, "load", "history.csv")
            assert "History loaded from" in captured.out

        with patch('os.path.exists', return_value=False):
            captured = self._execute_and_capture(history_command, capsys, "load", "nonexistent.csv")
            assert "Error: File not found" in captured.out

        with patch('os.path.exists', return_value=True), \
             patch('app.calculation.history.History.load_from_csv', return_value=False):
            captured = self._execute_and_capture(history_command, capsys, "load", "history.csv")
            assert "Error occurred while loading history" in captured.out

          # New: Test exception handling
        with patch('os.path.exists', return_value=True), \
            patch('app.calculation.history.History.load_from_csv', side_effect=Exception("Test load error")), \
            patch('app.plugins.history_command.logger') as mock_logger:
            captured = self._execute_and_capture(history_command, capsys, "load", "history.csv")

            mock_logger.exception.assert_called_once_with("Error loading history: Test load error")
            assert "Error: Test load error" in captured.out

    def test_delete_history(self, history_command, capsys):
        """Test deleting history entries."""
        # Test successful deletion with file update
        with patch('app.calculation.history.History.remove_at_index', return_value=True), \
            patch('app.calculation.history.History.save_to_csv', return_value=True):
            captured = self._execute_and_capture(history_command, capsys, "delete", "1")
            assert "Deleted calculation at index 1 and updated file" in captured.out

        # Test successful deletion but failed file update
        with patch('app.calculation.history.History.remove_at_index', return_value=True), \
            patch('app.calculation.history.History.save_to_csv', return_value=False):
            captured = self._execute_and_capture(history_command, capsys, "delete", "1")
            assert "Deleted calculation at index 1 but failed to update file" in captured.out

        # Test missing index
        captured = self._execute_and_capture(history_command, capsys, "delete")
        assert "Error: Please provide an index" in captured.out

        # Test invalid index format
        captured = self._execute_and_capture(history_command, capsys, "delete", "abc")
        assert "is not a valid index" in captured.out

        # Test failed deletion
        with patch('app.calculation.history.History.remove_at_index', return_value=False):
            captured = self._execute_and_capture(history_command, capsys, "delete", "99")
            assert "Error: Could not delete calculation at index" in captured.out

        # Test exception during deletion
        with patch('app.calculation.history.History.remove_at_index', side_effect=Exception("Test delete error")), \
            patch('app.plugins.history_command.logger') as mock_logger:
            captured = self._execute_and_capture(history_command, capsys, "delete", "1")

            mock_logger.exception.assert_called_once_with("Error during deletion: Test delete error")
            assert "Error: Test delete error" in captured.out

    def test_analyze_history(self, history_command, capsys):
        """Test analyzing history."""
        test_data = pd.DataFrame({'Operation': ['add', 'multiply'], 'Result': [8, 20]})

        with patch('app.calculation.history.History.get_history_as_dataframe', return_value=test_data):
            captured = self._execute_and_capture(history_command, capsys, "analyze")
            assert "History Analysis:" in captured.out

        with patch('app.calculation.history.History.get_history_as_dataframe', return_value=pd.DataFrame()):
            captured = self._execute_and_capture(history_command, capsys, "analyze")
            assert "No calculations in history to analyze" in captured.out

    def test_filter_history(self, history_command, mock_calculations, capsys):
        """Test filtering history by operation."""
        with patch('app.calculation.history.History.find_by_operation', return_value=[mock_calculations[0]]):
            captured = self._execute_and_capture(history_command, capsys, "filter", "add")
            assert "Filtered History (add):" in captured.out
            assert "5 add 3 = 8" in captured.out

        with patch('app.calculation.history.History.find_by_operation', return_value=[]):
            captured = self._execute_and_capture(history_command, capsys, "filter", "divide")
            assert "No calculations found with operation 'divide'" in captured.out

        captured = self._execute_and_capture(history_command, capsys, "filter")
        assert "Error: Please provide an operation to filter by" in captured.out

    def test_unknown_subcommand(self, history_command, capsys):
        """Test handling unknown subcommand."""
        captured = self._execute_and_capture(history_command, capsys, "unknown_command")
        assert "Unknown history subcommand" in captured.out
