import pytest

NUMBER_1 = 3.0
NUMBER_2 = 2.0


def add(x: int = 1, y: int = 2):
    sum = x + y
    return sum


def test_add():
    value = add(NUMBER_1, NUMBER_2)
    assert value == 5.0
