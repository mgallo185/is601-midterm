from app.commands import Command
import logging

logger = logging.getLogger(__name__)

class MenuCommand(Command):
    def __init__(self, command_handler):
        super().__init__()
        self.command_handler = command_handler
        
    def execute(self, *args):
        """Display available commands by category."""
        logger.info("Displaying available commands")
        
        # Define command categories
        categories = {
            "Calculation Commands": ["add", "subtract", "multiply", "divide"],
            "History Management": [
                "history",
                "  ├─ show           (Display history)",
                "  ├─ clear          (Clear all history)",
                "  ├─ save [file]    (Save history to file)",
                "  ├─ load [file]    (Load history from file)",
                "  ├─ delete <N>     (Delete entry at index N)",
                "  ├─ filter <op>    (Filter history by operation)",
                "  ├─ analyze        (Show history statistics)" 
            ],
            "System Commands": ["menu", "exit"]
        }
        
        print("\nAvailable Commands:")
        
        for category, commands in categories.items():
            print(f"\n{category}:")
            for cmd in commands:
                if isinstance(cmd, str) and cmd.strip() in self.command_handler.get_registered_commands():
                    print(f"  🔹 {cmd.strip()}")
                else:
                    print(f"    {cmd}")  # Indented for history subcommands
        
        print("\nType 'exit' to quit.")
