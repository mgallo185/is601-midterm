from app.commands import Command
import logging
from app.calculation.history import History
import os

# Initialize logger
logger = logging.getLogger(__name__)

class HistoryCommand(Command):
    def __init__(self, command_handler):
        super().__init__()
        self.command_handler = command_handler
        
    def execute(self, *args):
        """Handle history commands with subcommands."""
        logger.info(f"Executing history command with args: {args}")
        
        if not args or len(args) == 0:
            # Default behavior: display history
            self._display_history()
            return
            
        subcommand = args[0].lower()
        subcommand_args = args[1:] if len(args) > 1 else []
        
        # Map subcommands to methods
        subcommand_map = {
            "show": self._display_history,
            "clear": self._clear_history,
            "save": self._save_history,
            "load": self._load_history,
            "delete": self._delete_history,
            "analyze": self._analyze_history,
            "filter": self._filter_history
            
        }
        
        if subcommand in subcommand_map:
            subcommand_map[subcommand](*subcommand_args)
        else:
            logger.error(f"Unknown history subcommand: {subcommand}")
            print(f"Unknown history subcommand: '{subcommand}'")
    
    def _display_history(self, *args):
        """Display the calculation history."""
        history = History.get_history()
        if not history:
            logger.info("No calculations in history")
            print("No calculations in history.")
            return
            
        print("Calculation History:")
        for i, calc in enumerate(history):
            operation_name = calc.operation.__name__
            result = calc.perform()
            print(f"{i}: {calc.a} {operation_name} {calc.b} = {result}")
            
        logger.info(f"Displayed {len(history)} calculation records")
    
    def _clear_history(self, *args):
        """Clear the calculation history."""
        history_size = len(History.get_history())
        History.clear_history()
    
        # Save the empty history to update the CSV file
        success = History.save_to_csv()
    
        logger.info(f"Cleared {history_size} calculations from history")
    
        if success:
            print("History cleared and saved file updated.")
        else:
            print("History cleared in memory, but there was an issue updating the file.")
    
    def _save_history(self, *args):
        """Save the calculation history to a CSV file."""
        logger.info("Executing save history command")
        
        # Parse filename from args if provided
        filename = args[0] if args and len(args) > 0 else None
        
        # Ensure data directory exists
        if not History.ensure_data_directory():
            logger.error("Data directory not accessible")
            print("Error: Data directory not accessible")
            return
        
        # Get file path and save
        try:
            if History.save_to_csv(filename):
                file_path = History.get_file_path(filename)
                logger.info(f"Successfully saved history to {file_path}")
                print(f"History saved to {file_path}")
            else:
                logger.warning("No history to save")
                print("No history to save or error occurred.")
        except Exception as e:
            logger.exception(f"Error saving history: {e}")
            print(f"Error: {e}")
    
    def _load_history(self, *args):
        """Load the calculation history from a CSV file."""
        logger.info("Executing load history command")
        
        # Parse filename from args if provided
        filename = args[0] if args and len(args) > 0 else None
        file_path = History.get_file_path(filename)
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            print(f"Error: File not found at {file_path}")
            return
            
        try:
            if History.load_from_csv(filename):
                logger.info(f"Successfully loaded history from {file_path}")
                print(f"History loaded from {file_path}")
            else:
                logger.error("Failed to load history")
                print("Error occurred while loading history.")
        except Exception as e:
            logger.exception(f"Error loading history: {e}")
            print(f"Error: {e}")
    
    def _delete_history(self, *args):
        """Delete a specific calculation from history by index."""
        logger.info("Executing delete history command")
        
        # Check if an index was provided
        if not args or len(args) == 0:
            logger.error("No index provided for deletion")
            print("Error: Please provide an index to delete (e.g., 'delete 2')")
            return
            
        try:
            # Convert argument to integer index
            index = int(args[0])
            
            # Attempt to remove the calculation at the specified index
            if History.remove_at_index(index):
                logger.info(f"Successfully deleted calculation at index {index}")
                print(f"Deleted calculation at index {index}")
            else:
                logger.error(f"Failed to delete calculation at index {index}")
                print(f"Error: Could not delete calculation at index {index}")
        except ValueError:
            logger.error(f"Invalid index format: {args[0]}")
            print(f"Error: '{args[0]}' is not a valid index. Please provide a number.")
        except Exception as e:
            logger.exception(f"Error during deletion: {e}")
            print(f"Error: {e}")
    
    def _analyze_history(self, *args):
        """Analyze calculation history and display statistics."""
        logger.info("Executing analyze history command")
        
        # Get history as DataFrame
        df = History.get_history_as_dataframe()
        
        if df.empty:
            logger.info("No calculations in history to analyze")
            print("No calculations in history to analyze.")
            return
            
        # Calculate basic statistics
        total_calculations = len(df)
        operations_count = df['Operation'].value_counts()
        avg_result = df['Result'].mean()
        max_result = df['Result'].max()
        min_result = df['Result'].min()
        
        # Display statistics
        print(f"\nHistory Analysis:")
        print(f"Total calculations: {total_calculations}")
        print(f"\nOperations breakdown:")
        for op, count in operations_count.items():
            print(f"  - {op}: {count} ({count/total_calculations*100:.1f}%)")
            
        print(f"\nResults statistics:")
        print(f"  - Average result: {avg_result:.2f}")
        print(f"  - Maximum result: {max_result:.2f}")
        print(f"  - Minimum result: {min_result:.2f}")
            
        logger.info("Completed history analysis")
    
    def _filter_history(self, *args):
        """Filter and display history by operation type."""
        logger.info("Executing filter history command")
        
        # Check if an operation was provided
        if not args or len(args) == 0:
            logger.error("No operation provided for filtering")
            print("Error: Please provide an operation to filter by (e.g., 'filter add')")
            return
            
        operation_name = args[0].lower()
        filtered_history = History.find_by_operation(operation_name)
        
        if not filtered_history:
            logger.info(f"No calculations found with operation '{operation_name}'")
            print(f"No calculations found with operation '{operation_name}'.")
            return
            
        # Format and display filtered history
        print(f"Filtered History ({operation_name}):")
        for i, calc in enumerate(filtered_history):
            result = calc.perform()
            print(f"{i}: {calc.a} {operation_name} {calc.b} = {result}")
            
        logger.info(f"Displayed {len(filtered_history)} filtered calculation records")
    
  