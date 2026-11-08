import unittest

def add(a, b):
    return a + b

class TestCalculator(unittest.TestCase):
    def test_addition(self):
        # For RED demo, temporarily change expected value 4 to 5.
        self.assertEqual(add(2, 2), 4)
