from bird import Bird
from flappy import Flappy
from config import *

game = Flappy()

@game.register_ai
def super_ai(birds):
    return birds

game.start()