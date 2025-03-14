# IS 601 Midterm Project: Advanced Python Repl Calculator by Michael Gallo

## Project Overview

This midterm requires the development of an advanced Python-based calculator application. Designed to underscore the importance of professional software development practices, the application integrates clean, maintainable code, the application of design patterns, comprehensive logging, dynamic configuration via environment variables, sophisticated data handling with Pandas, and a command-line interface (REPL) for real-time user interaction.


## Table of Contents

1. [Installation and Usage](#installation-and-usage)
2. [Design Patterns](#design-patterns)
3. [Logging and Environment Variables](#logging-and-environment-variables)
4. [Exception Handling](#exception)

6. [Testing](#testing)


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

## Design Patterns

## Logging and Environment Variables
This app uses a logging system to track application behavior and user interactions.

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

It uses the defined envrioment variables specfied or it will fall back to default variables if needed.

Logging is also supported in the configuration in the configure_logging() function in [app/__init__.py](app/__init__.py) file where it uses enviroment variables such as LOG_DIR, LOG_LEVEL, LOG_FORMAT, LOG_FILE where these are all specified in a .env file that is not tracked on Github.

### Logging in Action
Here is a screenshot of logging in action when the application is running where it showcases lifecycle events, plugin loading, command registration, command execution, error handling, and user interface events.
<img width="503" alt="image" src="https://github.com/user-attachments/assets/b78ed50d-fb43-4105-8119-328626e0a866" />

### Log Storage
Logs are stored in the directory `` logs/ `` where it gets created automatically if it does not exist. It can be specfied via the enviroment variables. This directory is excluded on the Github repo.



## Exception Handling

## Testing

This project uses **Pytest** for unit testing, **Pylint** for code quality checks, and **Coverage.py** to measure test coverage. Below are the key commands to run tests and analyze coverage.

### Running Tests  
To execute all tests, including Pylint and code coverage checks, run:  

```sh
pytest --pylint --cov
```
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
