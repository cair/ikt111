from ikt111_games import ConnectFour

difficulty = "easy"  # "easy", "medium", "hard"

game = ConnectFour(difficulty=difficulty)


@game.register_ai
def super_ai():
    import random
    import time

    time.sleep(0.5)
    return random.randint(0, 6)


game.start(use_ai=True)
