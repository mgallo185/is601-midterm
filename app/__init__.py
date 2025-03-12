import os
import pkgutil
import importlib
import inspect
import sys
import logging
import logging.config
from dotenv import load_dotenv
from app.commands import CommandHandler
from app.commands import Command

# Load environment variables first
load_dotenv()

# Create logs directory
logs_dir = os.getenv('LOG_DIR', 'logs')
os.makedirs(logs_dir, exist_ok=True)

# Get log level from environment or default to INFO
log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
log_file = os.getenv('LOG_FILE', f'{logs_dir}/calculator.log')
debug_mode = os.getenv('DEBUG_MODE', 'False').lower() in ('true', '1', 't', 'yes')

# Load the logging configuration if it exists
if os.path.exists('logging.conf'):
    logging.config.fileConfig('logging.conf', disable_existing_loggers=False)
else:
    # Basic configuration if no config file found
    logging.basicConfig(
        level=getattr(logging, log_level, logging.INFO),
        format=os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s'),
        datefmt=os.getenv('LOG_DATE_FORMAT', '%Y-%m-%d %H:%M:%S'),
        handlers=[
            logging.FileHandler(log_file),
            logging.StreamHandler()
        ]
    )

# Create a logger for the App class
logger = logging.getLogger(__name__)
logger.setLevel(getattr(logging, log_level, logging.INFO))

class App:
    def __init__(self):
        # Load other environment variables
        self.app_name = os.getenv('APP_NAME', 'Calculator')
        self.environment = os.getenv('ENVIRONMENT', 'PRODUCTION')
        self.command_history_size = int(os.getenv('COMMAND_HISTORY_SIZE', '100'))
        
        # Initialize command handler
        self.command_handler = CommandHandler()
        logger.info(f"Initializing {self.app_name} in {self.environment} environment...")
        
        # Log debug information if in debug mode
        if debug_mode:
            logger.debug(f"Debug mode: ON")
            logger.debug(f"Log level: {log_level}")
            logger.debug(f"Log file: {log_file}")
            logger.debug(f"Command history size: {self.command_history_size}")
        
        self.load_plugins()  # Load plugins dynamically

    def load_plugins(self):
        """Dynamically load all plugins from the `app/plugins` directory."""
        plugins_package = "app.plugins"
        logger.info(f"Loading plugins from {plugins_package}...")
        
        loaded_plugins = 0
        failed_plugins = 0
        
        for _, plugin_name, _ in pkgutil.iter_modules([plugins_package.replace(".", "/")]):
            try:
                logger.info(f"Attempting to load plugin: {plugin_name}")
                plugin_module = importlib.import_module(f"{plugins_package}.{plugin_name}")
                
                plugin_commands = 0
                for item_name in dir(plugin_module):
                    item = getattr(plugin_module, item_name)
                    if isinstance(item, type) and issubclass(item, Command) and item is not Command:
                        command_name = plugin_name.replace("_command", "")
                        
                        try:
                            init_signature = inspect.signature(item.__init__)
                            if len(init_signature.parameters) > 1:
                                self.command_handler.register_command(command_name, item(self.command_handler))
                            else:
                                self.command_handler.register_command(command_name, item())
                                
                            logger.info(f"Registered command: {command_name}")
                            plugin_commands += 1
                        except Exception as command_error:
                            logger.error(f"Failed to register command {command_name}: {command_error}")
                            if debug_mode:
                                logger.exception("Command registration error details:")
                
                if plugin_commands > 0:
                    loaded_plugins += 1
                    logger.info(f"Successfully loaded plugin {plugin_name} with {plugin_commands} commands")
                else:
                    logger.warning(f"Plugin {plugin_name} loaded but no commands were registered")
                    
            except Exception as e:
                failed_plugins += 1
                logger.error(f"Failed to load plugin {plugin_name}: {e}")
                if debug_mode:
                    logger.exception("Plugin loading error details:")
        
        logger.info(f"Plugin loading complete. Successfully loaded {loaded_plugins} plugins, {failed_plugins} failed")

    def start(self):
        """Start the REPL loop for user interaction."""
        logger.info("Starting the REPL loop...")
        print(f"Welcome to {self.app_name}! Type 'menu' to see available commands, or 'exit' to quit.")
        
        try:
            # Show available commands at startup
            self.command_handler.execute_command("menu")
        except Exception as e:
            logger.error(f"Error displaying menu: {e}")
            print("Type 'help' or 'menu' to see available commands.")

        while True:
            try:
                user_input = input("Enter command: ").strip()
                
                if not user_input:
                    continue
                    
                logger.debug(f"User input: {user_input}")
                
                if user_input.lower() == "exit":
                    logger.info("User requested exit")
                    print(f"Exiting {self.app_name}...")
                    sys.exit(0)
                    
                user_input_split = user_input.split()
                command_name = user_input_split[0]
                args = user_input_split[1:]
                
                logger.info(f"Executing command: {command_name} with arguments: {args}")
                
                try:
                    self.command_handler.execute_command(command_name, *args)
                except KeyError:
                    logger.warning(f"Unknown command: {command_name}")
                    print(f"Unknown command: '{command_name}'. Type 'menu' to see available commands.")
                except Exception as command_error:
                    logger.error(f"Error executing command {command_name}: {command_error}")
                    if debug_mode:
                        logger.exception("Command execution error details:")
                        print(f"Error: {str(command_error)}")
                    else:
                        print(f"An error occurred while executing '{command_name}'. See logs for details.")
                    
            except KeyboardInterrupt:
                logger.info("Keyboard interrupt detected")
                print(f"\nInterrupted. Enter 'exit' to quit {self.app_name}.")
                
            except EOFError:
                logger.info("EOF detected, exiting")
                print("\nExiting...")
                sys.exit(0)
                
            except Exception as e:
                logger.error(f"Unexpected error in REPL loop: {e}")
                if debug_mode:
                    logger.exception("REPL loop error details:")
                print(f"An unexpected error occurred. Enter 'exit' to quit.")