class Player:
    def __init__(self, name, age):
        self.name = name
        self.age = age
        self.gender = None

    def __str__(self):
        return f"Name: {self.name}, Age: {self.age}"