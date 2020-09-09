import random
from snake import SnakeGame

snake = SnakeGame()

@snake.register_ai
def super_ai():
    return [random.choice(['up', 'down', 'left', 'right'])]

snake.start(use_ai=False)