from connect_four import ConnectFour

game = ConnectFour()

@game.register_ai
def super_ai():
    pass


game.start()