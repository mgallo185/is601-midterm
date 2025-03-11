from decimal import Decimal
from typing import Callable, List
from app.calculation.calculation import Calculation
import pandas as pd
import os
import logging
from datetime import datetime

class History:
    # In-memory storage for calculations
    history: List[Calculation] = []
    
    # File path configuration
    data_dir = './data'
    default_filename = 'calculation_history.csv'
    
    @classmethod
    def add_calculation(cls, calculation: Calculation):
        """Add a new calculation to the history."""
        cls.history.append(calculation)
        logging.info(f"Added calculation: {calculation.a} {calculation.operation.__name__} {calculation.b}")
    
    @classmethod
    def get_history(cls) -> List[Calculation]:
        """Retrieve the entire history of calculations."""
        return cls.history
    
    @classmethod
    def clear_history(cls):
        """Clear the history of calculations."""
        count = len(cls.history)
        cls.history.clear()
        logging.info(f"Cleared history ({count} calculations)")
    
    @classmethod
    def get_latest(cls) -> Calculation:
        """Get the latest calculation. Returns None if there's no history."""
        if cls.history:
            return cls.history[-1]
        return None
    
    @classmethod
    def find_by_operation(cls, operation_name: str) -> List[Calculation]:
        """Find and return a list of calculations by operation name."""
        matched = [calc for calc in cls.history if calc.operation.__name__ == operation_name]
        logging.info(f"Found {len(matched)} calculations with operation '{operation_name}'")
        return matched
    
    @classmethod
    def ensure_data_directory(cls):
        """Ensure data directory exists and is writable."""
        if not os.path.exists(cls.data_dir):
            os.makedirs(cls.data_dir)
            logging.info(f"Created directory '{cls.data_dir}'")
        elif not os.access(cls.data_dir, os.W_OK):
            logging.error(f"The directory '{cls.data_dir}' is not writable.")
            return False
        return True
    
    @classmethod
    def get_file_path(cls, filename=None):
        """Get the absolute and relative file paths."""
        if filename is None:
            filename = cls.default_filename
        
        relative_path = os.path.join(cls.data_dir, filename)
        absolute_path = os.path.abspath(relative_path)
        
        logging.info(f"Relative path: {relative_path}")
        logging.info(f"Absolute path: {absolute_path}")
        
        return relative_path
    
    @classmethod
    def save_to_csv(cls, filename=None):
        """Save calculation history to a CSV file."""
        if not cls.ensure_data_directory():
            return False
            
        file_path = cls.get_file_path(filename)
        
        # Convert calculation objects to a format pandas can handle
        history_data = []
        for calc in cls.history:
            # Extract the data we want to save
            history_data.append({
                'Timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                'First Operand': str(calc.a),
                'Second Operand': str(calc.b),
                'Operation': calc.operation.__name__,
                'Result': str(calc.perform())
            })
        
        # Create DataFrame and save to CSV
        if history_data:
            df = pd.DataFrame(history_data)
            df.to_csv(file_path, index=False)
            logging.info(f"Saved {len(history_data)} calculations to '{file_path}'")
            return True
        else:
            logging.warning("No calculations to save")
            return False
    
    @classmethod
    def load_from_csv(cls, filename=None):
        """Load calculation history from a CSV file."""
        file_path = cls.get_file_path(filename)
        
        if not os.path.exists(file_path):
            logging.error(f"File not found: '{file_path}'")
            return False
        
        try:
            # Load data from CSV
            df = pd.read_csv(file_path)
            logging.info(f"Read {len(df)} records from '{file_path}'")
            
            # Clear current history before loading
            cls.clear_history()
            
            # Import necessary operations for reconstruction
            from app.operations.operations import add, subtract, multiply, divide
            
            # Map operation names to actual functions
            operation_map = {
                'add': add,
                'subtract': subtract,
                'multiply': multiply,
                'divide': divide
            }
            
            # Reconstruct Calculation objects
            loaded_count = 0
            for _, row in df.iterrows():
                operation_name = row['Operation']
                if operation_name in operation_map:
                    a = Decimal(row['First Operand'])
                    b = Decimal(row['Second Operand'])
                    operation = operation_map[operation_name]
                    
                    # Create and add calculation to history
                    calc = Calculation.create(a, b, operation)
                    cls.add_calculation(calc)
                    loaded_count += 1
            
            logging.info(f"Successfully loaded {loaded_count} calculations")
            return True
        except Exception as e:
            logging.error(f"Error loading history: {e}")
            return False
    
    @classmethod
    def remove_at_index(cls, index):
        """Remove a calculation at the specified index."""
        if 0 <= index < len(cls.history):
            calculation = cls.history[index]
            cls.history.pop(index)
            logging.info(f"Removed calculation at index {index}: "
                         f"{calculation.a} {calculation.operation.__name__} {calculation.b}")
            return True
        logging.error(f"Invalid index: {index}")
        return False
    
    @classmethod
    def get_history_as_dataframe(cls):
        """Return the history as a pandas DataFrame for analysis."""
        history_data = []
        for calc in cls.history:
            history_data.append({
                'First Operand': float(calc.a),
                'Second Operand': float(calc.b),
                'Operation': calc.operation.__name__,
                'Result': float(calc.perform())
            })
        
        if history_data:
            return pd.DataFrame(history_data)
        return pd.DataFrame()
