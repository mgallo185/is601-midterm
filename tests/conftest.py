"""# conftest.py"""

from decimal import Decimal
from faker import Faker
from app.operations.operations import add, subtract, multiply, divide

# Initialize Faker for generating random test data
fake = Faker()
fake.seed_instance(12345)

# Define operation mappings globally
operation_mappings = {
    'add': add,
    'subtract': subtract,
    'multiply': multiply,
    'divide': divide
}

def generate_test_data(num_records):
    """Generate test data"""
    for i in range(num_records):
        # Ensure a mix of normal values and zero divisors
        if i % 4 == 0:
            a, b, operation_name = Decimal('10'), Decimal('0'), 'divide'
        else:
            a, b = Decimal(fake.random_number(digits=2)), Decimal(fake.random_number(digits=2))
            operation_name = fake.random_element(elements=list(operation_mappings.keys()))

        operation_func = operation_mappings[operation_name]

        # Skip division by zero cases as they're handled separately
        if operation_name == 'divide' and b == 0:
            continue

        expected = operation_func(a, b)
        yield a, b, operation_name, operation_func, expected

def pytest_addoption(parser):
    """Add command-line option for number of test records"""
    parser.addoption(
        "--num_records",
        action="store",
        default=10,
        type=int,
        help="Number of test records to generate"
    )

def pytest_generate_tests(metafunc):
    """Generate test parameters"""
    if {"a", "b", "expected"}.intersection(metafunc.fixturenames):
        num_records = metafunc.config.getoption("num_records")
        parameters = list(generate_test_data(num_records))

        metafunc.parametrize("a,b,operation,expected", [
            (a, b, operation_name if "operation_name" in metafunc.fixturenames else operation_func, expected)
            for a, b, operation_name, operation_func, expected in parameters
        ])
