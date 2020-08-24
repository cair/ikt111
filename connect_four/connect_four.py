class ConnectFour():
    def __init__(self):
        self.ai = None


    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f


    def start(self):
        pass
    