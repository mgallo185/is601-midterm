"""Test for Command abstract base class."""
from app.commands import Command
class TestCommand(Command):
    """Test implementation of Command class."""
    def execute(self):
        """Deliberately call parent's execute to test base class behavior."""
        # We explicitly want to test the parent class implementation
        # pylint: disable=useless-parent-delegation
        return super().execute()


def test_command_execute():
    """Test that concrete command can call abstract execute method."""
    command = TestCommand()
    command.execute()
