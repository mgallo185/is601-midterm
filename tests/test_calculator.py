'''My Calculator Test'''
from faker import Faker
from app.calculation import Calculator


# Create a Faker instance
fake = Faker()

def test_addition():
    '''Test that addition function works with random numbers'''
    a = fake.random_int(min=1, max=100)
    b = fake.random_int(min=1, max=100)
    expected = a + b
    assert Calculator.add(a, b) == expected

def test_subtraction():
    '''Test that subtraction function works with random numbers'''
    a = fake.random_int(min=1, max=100)
    b = fake.random_int(min=1, max=100)
    expected = a - b
    assert Calculator.subtract(a, b) == expected

def test_divide():
    '''Test that division function works with random numbers'''
    a = fake.random_int(min=1, max=100)
    b = fake.random_int(min=1, max=100)
    # Prevent division by zero
    b = b if b != 0 else 1
    expected = a / b
    assert Calculator.divide(a, b) == expected

def test_multiply():
    '''Test that multiplication function works with random numbers'''
    a = fake.random_int(min=1, max=100)
    b = fake.random_int(min=1, max=100)
    expected = a * b
    assert Calculator.multiply(a, b) == expected
