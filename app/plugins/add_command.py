from decimal import Decimal, InvalidOperation
from app.calculation import Calculator
from app.commands import Command
import logging

# Initialize logger
logger = logging.getLogger(__name__)

class AddCommand(Command):
    def __init__(self):
        super().__init__()

    def execute(self, *args):
        if len(args) != 2:
            logger.warning("Invalid number of arguments for add command")
            print("Usage: add <number1> <number2>")
            return
        
        try:
            num1, num2 = map(Decimal, args)
            result = Calculator.add(num1, num2)
            logger.info(f"Add command executed with numbers: {num1} and {num2}, result: {result}")
            print(f"Result: {num1} + {num2} = {result}")
        except InvalidOperation:
            logger.error("Invalid input, failed to convert input to Decimal")
            print("Invalid input. Please enter valid numbers.")
        except Exception as e:
            logger.exception(f"Error during addition: {e}")
            print(f"Error: {e}")
