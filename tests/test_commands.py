"""Test suite for Calculator Command classes."""

from unittest.mock import patch
import pytest
from app.plugins.add_command import AddCommand
from app.plugins.subtract_command import SubtractCommand
from app.plugins.multiply_command import MultiplyCommand
from app.plugins.divide_command import DivideCommand



@pytest.fixture
def add_command():
    """Fixture to create AddCommand instance."""
    return AddCommand()


@pytest.fixture
def subtract_command():
    """Fixture to create SubtractCommand instance."""
    return SubtractCommand()


@pytest.fixture
def multiply_command():
    """Fixture to create MultiplyCommand instance."""
    return MultiplyCommand()


@pytest.fixture
def divide_command():
    """Fixture to create DivideCommand instance."""
    return DivideCommand()


class TestAddCommand:
    """Tests for the AddCommand class."""

    def test_add_valid_numbers(self, add_command, capsys):
        """Test addition with valid numbers."""
        add_command.execute("5", "3")
        captured = capsys.readouterr()
        assert "Result: 5 + 3 = 8" in captured.out

    def test_add_invalid_args_count(self, add_command, capsys):
        """Test addition with wrong number of arguments."""
        add_command.execute("5")
        captured = capsys.readouterr()
        assert "Usage: add <number1> <number2>" in captured.out

    def test_add_invalid_numbers(self, add_command, capsys):
        """Test addition with invalid number inputs."""
        add_command.execute("abc", "3")
        captured = capsys.readouterr()
        assert "Invalid input. Please enter valid numbers." in captured.out

    def test_add_general_error(self, add_command, capsys):
        """Test addition with a general error."""
        with patch('app.calculation.Calculator.add', side_effect=ValueError("Test error")):
            add_command.execute("5", "3")
            captured = capsys.readouterr()
            assert "Error: Test error" in captured.out


class TestSubtractCommand:
    """Tests for the SubtractCommand class."""

    def test_subtract_valid_numbers(self, subtract_command, capsys):
        """Test subtraction with valid numbers."""
        subtract_command.execute("5", "3")
        captured = capsys.readouterr()
        assert "Result: 5 - 3 = 2" in captured.out

    def test_subtract_invalid_args_count(self, subtract_command, capsys):
        """Test subtraction with wrong number of arguments."""
        subtract_command.execute("5")
        captured = capsys.readouterr()
        assert "Usage: subtract <number1> <number2>" in captured.out

    def test_subtract_invalid_numbers(self, subtract_command, capsys):
        """Test subtraction with invalid number inputs."""
        subtract_command.execute("abc", "3")
        captured = capsys.readouterr()
        assert "Invalid input. Please enter valid numbers." in captured.out
    def test_subtract_general_error(self, subtract_command, capsys):
        """Test subtraction with a general error."""
        with patch('app.calculation.Calculator.subtract', side_effect=ValueError("Test error")):
            subtract_command.execute("5", "3")
            captured = capsys.readouterr()
            assert "Error: Test error" in captured.out

class TestMultiplyCommand:
    """Tests for the MultiplyCommand class."""

    def test_multiply_valid_numbers(self, multiply_command, capsys):
        """Test multiplication with valid numbers."""
        multiply_command.execute("5", "3")
        captured = capsys.readouterr()
        assert "Result: 5 × 3 = 15" in captured.out

    def test_multiply_invalid_args_count(self, multiply_command, capsys):
        """Test multiplication with wrong number of arguments."""
        multiply_command.execute("5")
        captured = capsys.readouterr()
        assert "Usage: multiply <number1> <number2>" in captured.out

    def test_multiply_invalid_numbers(self, multiply_command, capsys):
        """Test multiplication with invalid number inputs."""
        multiply_command.execute("abc", "3")
        captured = capsys.readouterr()
        assert "Invalid input. Please enter valid numbers." in captured.out

    def test_multiply_general_error(self, multiply_command, capsys):
        """Test multiplication with a general error."""
        with patch('app.calculation.Calculator.multiply', side_effect=ValueError("Test error")):
            multiply_command.execute("5", "3")
            captured = capsys.readouterr()
            assert "Error: Test error" in captured.out


class TestDivideCommand:
    """Tests for the DivideCommand class."""

    def test_divide_valid_numbers(self, divide_command, capsys):
        """Test division with valid numbers."""
        divide_command.execute("6", "2")
        captured = capsys.readouterr()
        assert "Result: 6 ÷ 2 = 3" in captured.out

    def test_divide_by_zero(self, divide_command, capsys):
        """Test division by zero."""
        divide_command.execute("5", "0")
        captured = capsys.readouterr()
        assert "Error: Division by zero is not allowed" in captured.out

    def test_divide_invalid_args_count(self, divide_command, capsys):
        """Test division with wrong number of arguments."""
        divide_command.execute("5")
        captured = capsys.readouterr()
        assert "Usage: divide <number1> <number2>" in captured.out

    def test_divide_invalid_numbers(self, divide_command, capsys):
        """Test division with invalid number inputs."""
        divide_command.execute("abc", "3")
        captured = capsys.readouterr()
        assert "Invalid input. Please enter valid numbers." in captured.out

    def test_divide_general_error(self, divide_command, capsys):
        """Test division with a general error."""
        with patch('app.calculation.Calculator.divide', side_effect=ValueError("Test error")):
            divide_command.execute("5", "3")
            captured = capsys.readouterr()
            assert "Error: Test error" in captured.out
