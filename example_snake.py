import random
from ikt111_games import Snake
snake = Snake()

@snake.register_ai
def super_ai():
    return [random.choice(['up', 'down', 'left', 'right'])]

snake.start(use_ai=True)
