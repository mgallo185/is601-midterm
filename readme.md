# IS 601 Midterm Project: Advanced Python Repl Calculator by Michael Gallo

## Project Overview

This midterm requires the development of an advanced Python-based calculator application. Designed to underscore the importance of professional software development practices, the application integrates clean, maintainable code, the application of design patterns, comprehensive logging, dynamic configuration via environment variables, sophisticated data handling with Pandas, and a command-line interface (REPL) for real-time user interaction.

The project does the following arithmetic operations: add, subtract, multiply, and divide. The solution is calculated and errors are handled using the EAFP apporach via try and except statements. 

The user can also manage their calculation history where it can display their previous calculations, save their history, clear their entire history, delete specific calculations, and filter and analyze their history using Pandas.
## Table of Contents

1. [Installation and Usage](#installation-and-usage)
2. [Design Patterns](#design-patterns)
3. [Logging and Environment Variables](#logging-and-environment-variables)
4. [Exception Handling](#exception-handling)
5. [Testing](#testing)


## Installation and Usage

### Prerequisites
Ensure you have the following installed before proceeding:
- Python 3.x ([Download Here](https://www.python.org/downloads/))
- Git ([Download Here](https://git-scm.com/downloads))
- Ubuntu or a compatible terminal environment
- VS Code

### Setting Up the Program

1. **In your terminal Clone the repository**  
```sh
   git clone https://github.com/mgallo185/is601-midterm.git
   cd is601-midterm
```
2. **Open the project in VS Code**
```sh
   code .
```
3. **Create and activate a virtual environment**
```sh
  python3 -m venv venv
  source venv/bin/activate
  ```

4. **Install dependencies**
```sh
pip install -r requirements.txt
```
### Running the Calculator Program
```sh
  python main.py
  ```
When ran, the user should be welcomed by the menu displaying all of the possible commands, they can use:
<img width="545" alt="image" src="https://github.com/user-attachments/assets/5af4cf2c-6da5-4999-851a-48e926db7894" />

### Summary of each command
- add [number] [number] This adds numbers
- subtract [num] [num]: This subtracts numbers
- multiply [num] [num]: This multiplies numbers
- divide [num] [num]: This divides numbers
- history show: This displays history
- history clear: This clears all history
- history save: This saves history to .csv file
- history load: This loads history from .csv file
- history delete <index>: This deletes a specific calcualtion at the specfied index
- history filter <operation> This filters history by operation
- history analyze: This shows history stats
### Demo Video
https://github.com/mgallo185/is601-midterm/blob/main/MidtermDemoIS601.mp4

## Design Patterns

### Command Pattern
This encapsulates a request as an object, allowing parameterization of clients with different requests

Implementation:  Used in [app/commands/__init__.py](app/commands/__init__.py) defines the abstract Command class and CommandHandler. Concrete command implementations are in the [app/plugins](app/plugins) directory, with each command (like AddCommand) implementing the execute() method. 

### Factory Method Pattern
Creates objects without specifying the exact class of that object

Implementation: [app/calculation/calculation.py](app/calculation/calculation.py) contains the Calculation.create() static method that acts as a factory method for creating Calculation objects.

### Strategy Pattern
This defines a collection of algorithms where it encapsulates each one, which makes them interchangeable at runtime

Implementation: [app/operations/operations.py](app/operations/operations.py) contains the different calculation strategies (add, subtract, multiply, divide) that are passed as callable parameters to the Calculator methods.

### Plugin Pattern
Allows for dynamic loading of modules and extending app functionality

Implementation: [app/__init__.py](app/__init__.py) includes the load_plugins() method that dynamically discovers and loads command plugins from the [app/plugins](app/plugins) directory.

### Singleton Pattern
Ensures a class has only one instance with a global point of access.
Implementation: [app/calculation/history.py](app/calculation/history.py) uses class variables and class methods to maintain a single history instance across the application.

### Facade Pattern
Provides a simplified interface to a complex subsystem.

Implementation: [app/calculation/history.py](app/calculation/history.py) offers simplified methods like save_to_csv(), load_from_csv(), and get_history_as_dataframe() that hide the complexity of Pandas data manipulations and file operations behind a clean, easy-to-use interface.

## Logging and Environment Variables
This app uses a logging system to track application behavior and user interactions. Uses different log messages based such as INFO, WARNING, ERROR for good monitoring. It has detailed logs based on errors, operations, data manipulation, etc.

### Logging Configuration
1. The logging system is configured with the [logging.conf](logging.conf) file which defines loggers, handlers, and formatters in the standard Python format. This is shown here:
   ```ini
   [loggers]
   keys=root
   
   [handlers]
   keys=fileHandler,consoleHandler

   [formatters]
   keys=simpleFormatter

   [logger_root]
   level=INFO
   handlers=fileHandler,consoleHandler

   [handler_fileHandler]
   class=handlers.RotatingFileHandler
   level=INFO
   formatter=simpleFormatter
   args=('logs/app.log', 'a', 1048576, 5)

   [handler_consoleHandler]
   class=StreamHandler
   level=INFO
   formatter=simpleFormatter
   args=(sys.stderr,)

   [formatter_simpleFormatter]
   format=%(asctime)s - %(name)s - %(levelname)s - %(message)s
   datefmt=
   ```
This uses a rotating file handler and uses a consistent format for logs with timestamps, name, log level, and message

### Enviroment Variable Configuration
Enviroment variables are loaded using the ``python-dotenv `` package where it reads from a .env file in the project root.
It is loaded at the start of the application like the following:
   ```python
      from dotenv import load_dotenv

      load_dotenv()
```

It uses the defined envrioment variables specfied or it will fall back to default variables if needed. Some of these variales APP_NAME, DEFAULT_FILENAME, DEBUG_MODE

Logging is also supported in the configuration in the configure_logging() function in [app/__init__.py](app/__init__.py) file where it uses enviroment variables such as LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_FILE where these are all specified in a .env file that is not tracked on Github.

### Logging in Action
Here is a screenshot of logging in action when the application is running where it showcases lifecycle events, plugin loading, command registration, command execution, error handling, and user interface events.
<img width="503" alt="image" src="https://github.com/user-attachments/assets/b78ed50d-fb43-4105-8119-328626e0a866" />

### Log Storage
Logs are stored in the directory `` logs/ `` where it gets created automatically if it does not exist. It can be specfied via the enviroment variables. This directory is excluded on the Github repo.



## Exception Handling

### EAFP (Easier to Ask for Forgiveness than Permission)
I used EAFP approach slightly more. In my plugins involving the math operation commands, I used the EAFP approach to attempt the operation first and then catch and handle any execeptions that occur. One of these instances are in [/app/plugins/add_command.py](app/plugins/add_command.py) and similar logic is used for subtraction, mulitiplication, and division located in the same directory
```python
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
```

It is also used in [/app/__init__.py](app/__init__.py) in the `` load_plugins() `` 
```python
try:
    plugin_module = importlib.import_module(f"{plugins_package}.{plugin_name}")
    # ... code that might fail
except ImportError as ie:
    failed_plugins += 1
    logger.error(f"Failed to load plugin {plugin_name}: {ie}")
```

Additionally, in the [app/calculation/history.py](app/calculation/history.py) in the `` load_from_csv() `` method
```python
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

```

### LBYL (Look Before you Leap)
The Look Before You Leap method checks conditions before attempting an operation

1. In [app/__init__.py](app/__init__.py)

```python
if not os.path.exists(plugin_path):
    logger.warning(f"Plugin directory {plugin_path} does not exist")
    return
```


2. It is also used in [app/plugins/history_command.py](app/plugins/history_command.py)

```python
if not args or len(args) == 0:
    # Default behavior: display history
    self._display_history()
    return
```
3. Additionally, in the [app/calculation/history.py](app/calculation/history.py)
```python
if not os.path.exists(file_path):
    logging.error(f"File not found: '{file_path}'")
    return False

```

### Combination of both

1. This [app/plugins/history_command.py](app/plugins/history_command.py) uses both here in the delete_history method:

```python
# LBYL: Check if an index was provided first
if not args or len(args) == 0:
    logger.error("No index provided for deletion")
    print("Error: Please provide an index to delete (e.g., 'delete 2')")
    return
    
try:
    # EAFP: Try to convert and use the index
    index = int(args[0])
    
    # Another LBYL check inside the try block
    if History.remove_at_index(index):
        logger.info(f"Successfully deleted calculation at index {index}")
        print(f"Deleted calculation at index {index}")
    else:
        logger.error(f"Failed to delete calculation at index {index}")
        print(f"Error: Could not delete calculation at index {index}")
except ValueError:
    logger.error(f"Invalid index format: {args[0]}")
    print(f"Error: '{args[0]}' is not a valid index. Please provide a number.")
```



## Testing

This project uses **Pytest** for unit testing, **Pylint** for code quality checks, and **Coverage.py** to measure test coverage. Below are the key commands to run tests and analyze coverage.

### Running Tests  
To execute all tests, including Pylint and code coverage checks, run:  

```sh
pytest --pylint --cov
```
<img width="489" alt="image" src="https://github.com/user-attachments/assets/22f32672-9351-489a-93c7-e2ac6fc6facc" />

I acheieved 99% test coverage where the only lines that were troublesome to test where testing the plugin setup with enviroment variables.

### Running Test with Custom Number of Records
To run tests with a custom numbe of records:
```sh
pytest --num_records=10
```

### Checking Coverage
To Generate a detailed line coverage report:
```sh
coverage report -m

```
### Checking Coverage for Specfific Module

To check test coverage for the [app/](app/) module and display missing lines:

```sh
pytest --cov=app --cov-report=term-missing

```
<img width="516" alt="image" src="https://github.com/user-attachments/assets/29f798cd-4b13-4210-9668-2c74a4737039" />

