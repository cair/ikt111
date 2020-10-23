from bird import Bird
from flappy import Flappy

game = Flappy()

@game.register_ai
def super_ai(birds):
    birds = [Bird() for _ in range(100)]
    return birds

game.start()