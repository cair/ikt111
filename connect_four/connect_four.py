from copy import deepcopy
import os
import numpy as np
import time
import random
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

score_table = { 
    pieces['player1']: {
        (pieces['board'], pieces['board'], pieces['board'], pieces['player1']): 	1/4,
        (pieces['board'], pieces['board'], pieces['player1'], pieces['player1']): 	2/4,
        (pieces['board'], pieces['player1'], pieces['player1'], pieces['player1']): 3/4,
    }, 
    pieces['player2']: {
        (pieces['board'], pieces['board'], pieces['board'], pieces['player2']): 	1/4,
        (pieces['board'], pieces['board'], pieces['player2'], pieces['player2']): 	2/4,
        (pieces['board'], pieces['player2'], pieces['player2'], pieces['player2']): 3/4,
    }
}

difficulty = {'easy': 3, 'medium': 5, 'hard': 7}

gfx_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'gfx')


class Node:
    def __init__(self, move, parent=None):
        self.move = move
        self.parent = parent
        self.score = 0
        if not parent:
            self.depth = 1
            self.is_opponent = False
        else:
            self.depth = parent.depth + 1
            self.is_opponent = not parent.is_opponent

    def move_list(self):
        moves = []
        node = self
        while node:
            moves.append((node.move, 1 if node.is_opponent else 2))
            node = node.parent
        moves.reverse()
        return moves

    def root_move(self):
        node = self
        while node.parent:
            node = node.parent
        return node.move


class Highlighter(pygame.sprite.Sprite):
    base_x = 12.5
    base_y = 55
    d_x = 81.3

    def __init__(self, column):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'highlight.png'))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [self.base_x + (self.d_x * column), self.base_y]

class Background(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'background.png'))
        self.rect = self.image.get_rect()
        self.rect.left, self.rect.top = [0, 0]

class BasePiece(pygame.sprite.Sprite):
    base_x = 53
    base_y = 94
    d_x = 81
    d_y = 80.8

    def calc_position(self, col, row):
        x = self.base_x + (self.d_x * col)
        y = self.base_y + (self.d_y * row)
        return [x, y]


class RedPiece(BasePiece):
    def __init__(self, col, row):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'red_piece.png'))
        self.rect = self.image.get_rect()
        self.rect.center = self.calc_position(col, row)


class YellowPiece(BasePiece):
    def __init__(self, col, row):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'yellow_piece.png'))
        self.rect = self.image.get_rect()
        self.rect.center = self.calc_position(col, row)

class TestPiece(BasePiece):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self)
        self.image = pygame.image.load(os.path.join(gfx_dir, 'red_piece.png'))
        self.rect = self.image.get_rect()
        self.rect.center = (53, 94)


class ConnectFour():
    def __init__(self):
        self.font_style = pygame.font.SysFont(None, 80)
        self.width   = config.WIDTH
        self.height  = config.HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption('Connect Four')
        self.clock = pygame.time.Clock()

        self.background = Background()
        self.highlighter = None

        self.piece_size = config.PIECE_SIZE
        self.game_pieces = []
        self.game_state = [[pieces['board'] for _ in range(config.ROWS)] for _ in range(config.COLS)]

        #self.max_depth = difficulty.get(config.DIFFICULTY, 'easy')
        self.max_depth = 3
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

        if self.highlighter:
            self.display.blit(self.highlighter.image,
                            self.highlighter.rect)

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


    def _check_highlighter_event(self, pos):
        """Helper function to draw column highligher when hover over"""
        col = self._pos_to_col(pos)
        if col == -1:
            self.highlighter = None
        else:
            self.highlighter = Highlighter(col)    


    def _pos_to_col(self, pos):
        x = pos[0]
        base = Highlighter.base_x
        d_x = Highlighter.d_x

        if x < base:
            return -1
        for i in range(1, 8):
            if x < (base + (d_x * i)):
                return i - 1
        return -1


    def _get_next_row(self, col, state=None):
        if not state:
            state = self.game_state
        return next((i - 1 for i, r in enumerate(state[col]) 
                     if r != pieces['board']), # Condition
                     config.ROWS - 1) # Default return value


    def _put_piece(self, player, col, row, state=None):
        """Helper function to insert player pieces on the board"""
        if not state:
            state = self.game_state
        
        if player == pieces['player1']:
            piece = RedPiece(col, row)
        elif player == pieces['player2']:
            piece = YellowPiece(col, row)
        else:
            raise Exception(f'Unknown player \'{player}\'')

        state[col][row] = player
        
        if state is self.game_state:
            self.game_pieces.append(piece)

    def _valid_cols(self, state=None):
        """Helper function to find valid cols with open rows given a state"""
        if not state:
            state = self.game_state
        for col in range(config.COLS):
            row = self._get_next_row(col, state=state)
            if row > -1:
                yield col        


    def _make_move(self):
        """Game AI"""
        def generate_children(parent_node, current_state):
            children = []
            for col in self._valid_cols(state=current_state):
                child = Node(col, parent=parent_node)
                child_state = self.simulate_moves(child.move_list())
                for window in self._generate_windows(state=child_state):
                    ## Check if child wins - break if
                    winner = self._check_winning_window(window)
                    if winner and winner == pieces['player1']:
                        parent_node.score = -1
                        return None
                    elif winner and winner == pieces['player2']:
                        raise Exception('Player won on game move - should not happen. Please report bug')
                    
                    ## Calculate child score
                    child.score = max(child.score, score_table[pieces['player1']].get(tuple(window), 0))
                children.append(child)
            return max(children, key=lambda x: x.score)

        open_list = []
        # Populate open_list with root nodes
        for col in self._valid_cols():
            open_list.append(Node(col))

        best_node = open_list[0]
        while open_list:
            node = open_list.pop(0)
            moves = node.move_list()
            new_state = self.simulate_moves(moves)
            
            if node.is_opponent:
                for col in self._valid_cols(state=new_state):
                    open_list.append(Node(col, parent=node))
            else:
                for window in self._generate_windows(state=new_state):
                    winner = self._check_winning_window(window)
                    if winner and winner == pieces['player2']:
                        # We assume any prev. opponent move is their best
                        return node.root_move()
                    elif winner and winner == pieces['player1']:
                        raise Exception('Player won on game move - should not happen. Please report bug')
                    
                    node.score = max(node.score, score_table[pieces['player2']].get(tuple(window), 0))
                        
                # Create opponent children
                if node.depth < self.max_depth:
                    child = generate_children(node, new_state)
                
                    if child:
                        open_list.append(child)
                if node.score > best_node.score:
                    best_node = node

        return best_node.root_move()


    def _check_if_col_is_full(self, col):
        """Helper function to check if a column is full"""
        return pieces['board'] in col

    def _check_winning_window(self, window):
        window = set(window)
        if pieces['board'] not in window and len(window) == 1:
            return window.pop()
        return None

    def _generate_horizontal_windows(self, state=None):
        if not state:
            state = self.game_state
        for row in range(config.ROWS):
            for col in range(config.COLS - 3):
                window = []
                for i in range(col, col + 4):
                    window.append(state[i][row])
                yield window

    def _generate_vertical_windows(self, state=None):
        if not state:
            state = self.game_state
        for col in range(config.COLS):
            for i in range(config.ROWS - 3):
                window = state[col][i:i + 4]
                yield window
    
    def _generate_diagonal_windows(self, state=None):
        if not state:
            state = self.game_state
        for col in range(config.COLS):
            for row in range(config.ROWS):
                if col + 3 < config.COLS and row < config.ROWS - 3:
                    window = [state[col + i][row + i] for i in range(4)]
                    yield window
                elif row >= 3 and col < config.COLS - 3:
                    window = [state[col + i][row - i] for i in range(4)]
                    yield window
                else:
                    continue


    def _generate_windows(self, state=None):
        if not state:
            state = self.game_state
        for window in self._generate_horizontal_windows(state):
            yield window
        for window in self._generate_vertical_windows(state):
            yield window
        for window in self._generate_diagonal_windows(state):
            yield window
        
    
    def _check_if_board_is_full(self, state=None):
        """Helper function to check if the board is full"""
        if not state:
            state = self.game_state
        for col in state:
            if 0 in col:
                return False
        return True

    def _check_if_winner(self):
        """Helper function for the game to know if there is a winner"""
        for window in self._generate_windows():
            winner = self._check_winning_window(window)
            if winner:
                if winner == pieces['player1']:
                    self._game_won()
                elif winner == pieces['player2']:
                    self._game_over()
                else:
                    raise Exception(f'Unknown winner \'{winner}\'')
        if self._check_if_board_is_full():
            self._game_over('Draw!')

    def _game_over(self, msg='You Lost'):
        """Helper function to display a loss-condition message"""
        self._display_message(msg)
        self._exit()


    def _game_won(self, msg='You Won!'):
        """Helper function to display a win-condition message"""
        self._display_message(msg)
        self._exit()


    def simulate_moves(self, moves):
        """Simulates a sequence of moves.

        This functions accepts a single move, or a list of moves.
        Each move is assumed to be a tupple like this: (col, player)

        Returns:
            A copy of the resulting game state if all moves are legal
            False if any move is illegal
        """
        new_state = deepcopy(self.game_state)
        for col, player in moves:
            row = self._get_next_row(col, state=new_state)
            if row == -1:
                return False
            self._put_piece(player, col, row, new_state)
             # player, col, row, state
        return new_state

    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f


    def start(self, use_ai=False):
        # Game Loop
        while True:
            move = None
            while move is None:
                self.clock.tick(config.CLOCK_SPEED)
                for event in pygame.event.get():
                    self._check_quit_event(event)

                    if not use_ai:
                        if event.type == pygame.MOUSEMOTION:
                            self._check_highlighter_event(pygame.mouse.get_pos())
                            self._update_display()

                        if event.type == pygame.MOUSEBUTTONUP:
                            move = self._pos_to_col(pygame.mouse.get_pos())
                            if move == -1:
                                move = None
                                continue
                if use_ai:
                    # Get next move from their AI
                    pass

            row = self._get_next_row(move)
            if row > -1:
                self._put_piece(pieces['player1'], move, row)

            self._update_display()
            self._check_if_winner()
            
            # Game AI moves after player
            move = self._make_move()
            row = self._get_next_row(move)
            if row > -1:
                self._put_piece(pieces['player2'], move, row)

            self._update_display()
            self._check_if_winner()

            # None of the above! Let's continue!
            self.clock.tick(config.CLOCK_SPEED)
    