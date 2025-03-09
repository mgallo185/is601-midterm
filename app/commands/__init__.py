from abc import ABC, abstractmethod
class Command(ABC):
    """Abstract base class for commands."""
    @abstractmethod
    def execute(self):
        pass

class CommandHandler:
    """Handles command registration and execution."""
    def __init__(self):
        self.commands = {}

    def register_command(self, command_name: str, command: Command):
        """Registers a command with a name."""
        self.commands[command_name] = command

    def execute_command(self, command_name: str, *args):
        """Executes a registered command."""
        if command_name in self.commands:
            command = self.commands[command_name]
            command.execute(*args)  # Execute the command synchronously
        else:
            print(f"No such command: {command_name}")

    def get_registered_commands(self):
        """Returns a list of registered command names."""
        return list(self.commands.keys())
