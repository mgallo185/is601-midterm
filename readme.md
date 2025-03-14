# IS 601 Midterm Project: Advanced Python Repl Calculator by Michael Gallo

## Project Overview

This midterm requires the development of an advanced Python-based calculator application. Designed to underscore the importance of professional software development practices, the application integrates clean, maintainable code, the application of design patterns, comprehensive logging, dynamic configuration via environment variables, sophisticated data handling with Pandas, and a command-line interface (REPL) for real-time user interaction.


## Table of Contents

1. [Installation and Usage](#installation-and-usage)
2. [Design Patterns](#design-patterns)
3. [Logging](#logging)
4. [Exception Handling](#exception)
5. [Enviroment Variables](#enviroment-variables)
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

## Logging


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
