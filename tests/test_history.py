"""Test calculation history"""

# Correct the import order by placing standard library imports before third-party library imports,
# adhering to PEP 8 guidelines for import ordering.
import os
from decimal import Decimal
from unittest.mock import patch, MagicMock
import pytest
import pandas as pd


# Import Calculation and Calculations classes from the calculator package,
# assuming these are the correct paths following Python's package and module naming conventions.
from app.calculation.calculation import Calculation
from app.calculation.history import History

# Import arithmetic operation functions (add and subtract) to be tested.
from app.operations.operations import add, subtract, multiply, divide

# pytest.fixture is a decorator that marks a function as a fixture,
# a setup mechanism used by pytest to initialize a test environment.
# Here, it's used to define a fixture that prepares the test environment for calculations tests.
@pytest.fixture
def setup_calculations():
    """Clear history and add sample calculations for tests."""
    # Clear any existing calculation history to ensure a clean state for each test.
    History.clear_history()
    # Add sample calculations to the history to set up a known state for testing.
    # These calculations represent typical use cases and allow tests to verify that
    # the history functionality is working as expected.
    History.add_calculation(Calculation(Decimal('10'), Decimal('5'), add))
    History.add_calculation(Calculation(Decimal('20'), Decimal('3'), subtract))

def test_add_calculation(setup_calculations):
    """Test adding a calculation to the history."""
    # Create a new Calculation object to add to the history.
    calc = Calculation(Decimal('2'), Decimal('2'), add)
    # Add the calculation to the history.
    History.add_calculation(calc)
    # Assert that the calculation was added to the history by checking
    # if the latest calculation in the history matches the one we added.
    assert History.get_latest() == calc, "Failed to add the calculation to the history"

def test_get_history(setup_calculations):
    """Test retrieving the entire calculation history."""
    # Retrieve the calculation history.
    history = History.get_history()
    # Assert that the history contains exactly 2 calculations,
    # which matches our setup in the setup_calculations fixture.
    assert len(history) == 2, "History does not contain the expected number of calculations"

def test_clear_history(setup_calculations):
    """Test clearing the entire calculation history."""
    # Clear the calculation history.
    History.clear_history()
    # Assert that the history is empty by checking its length.
    assert len(History.get_history()) == 0, "History was not cleared"

def test_get_latest(setup_calculations):
    """Test getting the latest calculation from the history."""
    # Retrieve the latest calculation from the history.
    latest = History.get_latest()
    # Assert that the latest calculation matches the expected values,
    # specifically the operands and operation used in the last added calculation
    # in the setup_calculations fixture.
    assert latest.a == Decimal('20') and latest.b == Decimal('3'), "Did not get the correct latest calculation"

def test_find_by_operation(setup_calculations):
    """Test finding calculations in the history by operation type."""
    # Find all calculations with the 'add' operation.
    add_operations = History.find_by_operation("add")
    # Assert that exactly one calculation with the 'add' operation was found.
    assert len(add_operations) == 1, "Did not find the correct number of calculations with add operation"
    # Find all calculations with the 'subtract' operation.
    subtract_operations = History.find_by_operation("subtract")
    # Assert that exactly one calculation with the 'subtract' operation was found.
    assert len(subtract_operations) == 1, "Did not find the correct number of calculations with subtract operation"

def test_get_latest_with_empty_history():
    """Test getting the latest calculation when the history is empty."""
    # Ensure the history is empty by clearing it.
    History.clear_history()
    # Assert that the latest calculation is None since the history is empty.
    assert History.get_latest() is None, "Expected None for latest calculation with empty history"

def test_ensure_data_directory():
    """Test the directory creation functionality."""
    # Mock os.path.exists to simulate directory not existing
    with patch('os.path.exists', return_value=False), \
         patch('os.makedirs') as mock_makedirs:
        result = History.ensure_data_directory()
        mock_makedirs.assert_called_once_with(History.data_dir)
        assert result is True, "Should return True when directory is created"

    # Mock os.path.exists to simulate directory existing but not writable
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=False):
        result = History.ensure_data_directory()
        assert result is False, "Should return False when directory is not writable"

    # Mock os.path.exists to simulate directory existing and writable
    with patch('os.path.exists', return_value=True), \
         patch('os.access', return_value=True):
        result = History.ensure_data_directory()
        assert result is True, "Should return True when directory exists and is writable"

def test_get_file_path():
    """Test the file path generation functionality."""
    # Test with default filename
    with patch('os.path.abspath', return_value='/absolute/path/to/calculation_history.csv'):
        path = History.get_file_path()
        assert path == os.path.join(History.data_dir, History.default_filename), \
               "Default file path should use default filename"

    # Test with custom filename
    custom_filename = 'custom_history.csv'
    with patch('os.path.abspath', return_value=f'/absolute/path/to/{custom_filename}'):
        path = History.get_file_path(custom_filename)
        assert path == os.path.join(History.data_dir, custom_filename), \
               "Custom file path should use provided filename"

def test_save_to_csv(setup_calculations):
    """Test saving calculation history to CSV."""
    # Mock ensure_data_directory to fail
    with patch.object(History, 'ensure_data_directory', return_value=False):
        result = History.save_to_csv()
        assert result is False, "Should return False when directory check fails"
    # Mock pandas DataFrame.to_csv and datetime
    mock_datetime = MagicMock()
    mock_datetime.now.return_value.strftime.return_value = "2025-03-11 12:00:00"

    with patch('pandas.DataFrame.to_csv') as mock_to_csv, \
         patch('datetime.datetime', mock_datetime), \
         patch.object(History, 'ensure_data_directory', return_value=True), \
         patch.object(History, 'get_file_path', return_value='test_path.csv'):

        result = History.save_to_csv()

        mock_to_csv.assert_called_once()
        assert result is True, "Should return True when CSV is saved successfully"

    # Test with empty history
    History.clear_history()
    with patch.object(History, 'ensure_data_directory', return_value=True):
        result = History.save_to_csv()
        assert result is False, "Should return False when history is empty"

def test_load_from_csv():
    """Test loading calculation history from CSV."""
    # Mock file not existing
    with patch('os.path.exists', return_value=False):
        result = History.load_from_csv()
        assert result is False, "Should return False when file doesn't exist"

    # Create mock data
    mock_data = pd.DataFrame({
        'Timestamp': ['2025-03-11 12:00:00', '2025-03-11 12:01:00'],
        'First Operand': ['10', '20'],
        'Second Operand': ['5', '3'],
        'Operation': ['add', 'subtract'],
        'Result': ['15', '17']
    })

    # Mock successful load
    with patch('os.path.exists', return_value=True), \
         patch('pandas.read_csv', return_value=mock_data), \
         patch.object(History, 'clear_history') as mock_clear, \
         patch.object(History, 'add_calculation') as mock_add:

        result = History.load_from_csv()

        mock_clear.assert_called_once()
        assert mock_add.call_count == 2, "Should add both calculations from the CSV"
        assert result is True, "Should return True when load is successful"

    # Mock exception during load
    with patch('os.path.exists', return_value=True), \
         patch('pandas.read_csv', side_effect=Exception("CSV error")):

        result = History.load_from_csv()
        assert result is False, "Should return False when an exception occurs"

def test_remove_at_index(setup_calculations):
    """Test removing a calculation at a specific index."""
    # Valid index
    initial_count = len(History.get_history())
    result = History.remove_at_index(0)
    assert result is True, "Should return True when index is valid"
    assert len(History.get_history()) == initial_count - 1, "Should have one less calculation after removal"

    # Invalid index (negative)
    result = History.remove_at_index(-1)
    assert result is False, "Should return False when index is negative"

    # Invalid index (too large)
    result = History.remove_at_index(len(History.get_history()) + 10)
    assert result is False, "Should return False when index is out of range"

def test_get_history_as_dataframe(setup_calculations):
    """Test converting history to DataFrame."""
    # Test with calculations in history
    df = History.get_history_as_dataframe()
    assert isinstance(df, pd.DataFrame), "Should return a pandas DataFrame"
    assert len(df) == 2, "DataFrame should have 2 rows for our test data"
    assert 'First Operand' in df.columns, "DataFrame should have 'First Operand' column"
    assert 'Operation' in df.columns, "DataFrame should have 'Operation' column"

    # Test with empty history
    History.clear_history()
    df = History.get_history_as_dataframe()
    assert isinstance(df, pd.DataFrame), "Should return an empty DataFrame"
    assert len(df) == 0, "DataFrame should be empty when history is empty"

def test_multiple_operations(setup_calculations):
    """Test with multiple operation types."""
    # Add multiply and divide operations
    History.add_calculation(Calculation(Decimal('4'), Decimal('5'), multiply))
    History.add_calculation(Calculation(Decimal('15'), Decimal('3'), divide))

    # Verify all operations are in history
    assert len(History.find_by_operation("add")) == 1
    assert len(History.find_by_operation("subtract")) == 1
    assert len(History.find_by_operation("multiply")) == 1
    assert len(History.find_by_operation("divide")) == 1

    # Verify total count
    assert len(History.get_history()) == 4, "History should contain 4 calculations"
