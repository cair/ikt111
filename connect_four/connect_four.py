import os
import numpy as np
import time
import pygame
pygame.init()

import config

colors = {
    'black': (0, 0, 0),
    'white': (255, 255, 255),
    'blue':  (0, 0, 255)
}

pieces = {
    'board': 0,
    'player1': 1,
    'player2': 2
}

gfx_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gfx')


class Highlighter(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'highlight.png'))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [(12.5 + (81.3 * 6)), 55]


class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'background.png'))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [0, 0]

class RedPiece(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'red_piece.png'))
        self.rect = self.image.get_rect()
        self.rect.center = location

class YellowPiece(pygame.sprite.Sprite):
    def __init__(self, location):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'yellow_piece.png'))
        self.rect = self.image.get_rect()
        self.rect.center = location


class ConnectFour():
    def __init__(self):
        self.font_style = pygame.font.SysFont(None, 80)
        self.width   = config.WIDTH
        self.height  = config.HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Connect Four')
        self.clock = pygame.time.Clock()
        
        self.background = Background()
        self.highlighter = Highlighter()

        self.piece_size = config.PIECE_SIZE
        self.game_pieces = []
        self.board = [[pieces['board'] for _ in range(config.ROWS)] for _ in range(config.COLS)]
        self.ai = lambda placeholder: self._game_over(msg='No AI registered!')


    def _display_message(self, msg, color=colors['black']):
        """Helper function to show message on display"""
        message = self.font_style.render(msg, True, color)
        message_rect = message.get_rect(center=(self.width / 2, self.height / 2))

        self.display.blit(message, message_rect)
        pygame.display.update()
        time.sleep(1)


    def _update_display(self):
        """Helper function to update pygame display"""
        self.display.fill(colors['white'])
        self.display.blit(self.background.image, 
                            self.background.rect)

        for piece in self.game_pieces:
            self.display.blit(piece.image, piece.rect)
        pygame.display.update()

    def _exit(self):
        """Helper function to exit the game"""
        pygame.quit()
        quit()


    def _check_quit_event(self, event):
        """Helper function to check for "user want's to quit" conditions"""
        if event.type == pygame.QUIT:
            self._game_over(msg='Quitting...')
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self._game_over(msg='Quitting...')


    def _game_over(self, msg='You Lost'):
        """Helper function to display a loss-condition message"""
        self._display_message(msg)
        self._exit()


    def _game_won(self, msg='You Won!'):
        """Helper function to display a win-condition message"""
        self._display_message(msg)
        self._exit()


    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f


    def start(self):
        # Game Loop
        while True:
            for event in pygame.event.get():
                self._check_quit_event(event)
            
            self._update_display()

            self.clock.tick(config.CLOCK_SPEED)
    