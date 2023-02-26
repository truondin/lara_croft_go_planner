from enum import Enum
from Trap import MovingTrap, Trap


class AnimalType(Enum):
    SNAKE = 1
    SPIDER = 2
    LIZARD = 3


class Animal(Trap):
    type: AnimalType


class MovingAnimal(Animal, MovingTrap):
    pass
