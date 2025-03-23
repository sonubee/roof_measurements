# file2.py
from file1 import ClassA

class ClassB:
    def __init__(self, a_value, b_value):
        self.a_instance = ClassA(a_value)
        self.b_value = b_value

    def interact(self):
        return f"{self.a_instance.display()}, Value of B: {self.b_value}"

# Example usage
b_instance = ClassB(10, 20)
print(b_instance.interact()) # Output: Value of A: 10, Value of B: 20