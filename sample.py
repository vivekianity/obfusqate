import random
import datetime


# Sample variable assignments
name = "John Doe"
age = 30
city = "New York"


# Additional operations
def generate_greeting(name):
   greetings = ["Hello", "Hi", "Greetings", "Salutations", "Hey"]
   return f"{random.choice(greetings)}, {name}!"


def get_current_date():
   return datetime.datetime.now().date()


def favorite_color():
   colors = ["Red", "Blue", "Green", "Yellow", "Purple"]
   return random.choice(colors)


def describe_person(name, age, city):
   return f"{name} is {age} years old and lives in {city}."


# More variable assignments
greeting = generate_greeting(name)
current_date = get_current_date()
color = favorite_color()
description = describe_person(name, age, city)


# Print results
print(greeting)
print("Today's date is:", current_date)
print("Favorite color is:", color)
print(description)


# Further operations
people = [("Alice", 28, "Los Angeles"), ("Bob", 34, "Chicago"), ("Eve", 22, "San Francisco")]
descriptions = [describe_person(person[0], person[1], person[2]) for person in people]


for desc in descriptions:
   print(desc)