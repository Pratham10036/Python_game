import random

def random_sum():
    numbers = [random.randint(1, 100) for _ in range(10)]
    print("Numbers:", numbers)
    print("Sum:", sum(numbers))

def random_choice():
    items = ['apple', 'banana', 'cherry', 'date']
    print("Random fruit:", random.choice(items))

def random_float():
    print("Random float between 0 and 1:", random.random())

random_sum()
random_choice()
random_float()
for i in range(3):
    print(f"Random int {i+1}:", random.randint(1, 50))
