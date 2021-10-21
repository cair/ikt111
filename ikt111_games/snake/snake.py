import random
import time
import colorsys
import pygame
import numpy as np
from pathlib import Path
from . import utils
from . import config

gfx_path = Path(__file__, "..", "gfx").resolve()

pygame.init()

colors = {
    "red": (255, 0, 0),
    "green": (0, 255, 0),
    "blue": (0, 0, 255),
    "black": (0, 0, 0),
    "gray": (100, 100, 100),
    "white": (255, 255, 255),
}

states = {"board": 0, "snake_body": 1, "snake_head": 2, "apple": 3}


class SnakeGame:
    def __init__(self):
        self.font_style = pygame.font.SysFont(None, 50)

        self.width = config.WIDTH
        self.height = config.HEIGHT
        self.display = pygame.display.set_mode((self.width, self.height))
        pygame.display.set_caption("Snake")

        self.main_layer = pygame.Surface((self.width, self.height))
        self.search_layer = pygame.Surface((self.width, self.height), pygame.SRCALPHA)
        self.visited_nodes = {}

        self.clock = pygame.time.Clock()

        self.snake = None
        self.apple = None

        self.snake_delta_x = 0
        self.snake_delta_y = 0

        self.snake_len = config.SNAKE_START_LEN
        self.sprite_size = utils.find_common_divisor(
            config.WIDTH, config.HEIGHT, config.MAX_SPRITE_SIZE, config.MIN_SPRITE_SIZE
        )
        if not self.sprite_size:
            self._game_over(msg=f"Invalid game size {self.width}x{self.height}")

        self.sprites = {
            "apple": pygame.image.load(f"{gfx_path}/apple.png").convert_alpha(),
            "bend": pygame.image.load(f"{gfx_path}/bend.png").convert_alpha(),
            "head": pygame.image.load(f"{gfx_path}/head.png").convert_alpha(),
            "straight": pygame.image.load(f"{gfx_path}/straight.png").convert_alpha(),
            "tail": pygame.image.load(f"{gfx_path}/tail.png").convert_alpha(),
        }

        self.square_font = pygame.font.SysFont(None, int(25 * self.sprite_size / 40))

        self._update_game_state()

        self.moves = []
        self.ai = lambda placeholder: self._game_over(msg="No AI registered!")

    def _display_message(self, msg, color=colors["blue"]):
        """Helper function to show message on display"""
        message = self.font_style.render(msg, True, color)
        message_rect = message.get_rect(center=(self.width / 2, self.height / 2))

        self.display.blit(message, message_rect)
        pygame.display.update()
        time.sleep(1)

    def _get_sprite(self, sprite_name, color_key=None):
        """Helper function to get sprite from the sprite dict"""
        image = self.sprites[sprite_name]
        image = pygame.transform.scale(image, (self.sprite_size, self.sprite_size))
        if color_key:
            image.set_colorkey(color_key)
        return image

    def _draw_snake(self):
        """Helper function to draw snake on display"""
        # Determine correct image for snake head
        snake_head = self.snake[-1]
        if snake_head[1] < self.snake[-2][1]:
            # Moving Up
            image = self._get_sprite("head")

        elif snake_head[0] > self.snake[-2][0]:
            # Moving right
            image = self._get_sprite("head")
            image = pygame.transform.rotate(image, 270)

        elif snake_head[1] > self.snake[-2][1]:
            # Moving down
            image = self._get_sprite("head")
            image = pygame.transform.rotate(image, 180)

        elif snake_head[0] < self.snake[-2][0]:
            # Moving left
            image = self._get_sprite("head")
            image = pygame.transform.rotate(image, 90)

        self.main_layer.blit(image, snake_head)

        # Determine correct image for snake tail
        snake_tail = self.snake[0]
        if snake_tail[1] > self.snake[1][1]:
            # Moving Up
            image = self._get_sprite("tail")

        elif snake_tail[0] < self.snake[1][0]:
            # Moving right
            image = self._get_sprite("tail")
            image = pygame.transform.rotate(image, 270)

        elif snake_tail[1] < self.snake[1][1]:
            # Moving down
            image = self._get_sprite("tail")
            image = pygame.transform.rotate(image, 180)

        elif snake_tail[0] > self.snake[1][0]:
            # Moving left
            image = self._get_sprite("tail")
            image = pygame.transform.rotate(image, 90)

        self.main_layer.blit(image, snake_tail)

        # Determine correct image for the body
        for i, seg in enumerate(self.snake[1:-1], 1):
            p_seg = self.snake[i + 1]
            n_seg = self.snake[i - 1]

            if n_seg[0] < seg[0] < p_seg[0] or p_seg[0] < seg[0] < n_seg[0]:
                # Horizontal segment
                image = self._get_sprite("straight")

            elif n_seg[1] < seg[1] < p_seg[1] or p_seg[1] < seg[1] < n_seg[1]:
                # Vertical segment
                image = self._get_sprite("straight")
                image = pygame.transform.rotate(image, 90)

            elif (n_seg[0] > seg[0] and p_seg[1] < seg[1]) or (
                p_seg[0] > seg[0] and n_seg[1] < seg[1]
            ):
                # Angle Left-Up
                image = self._get_sprite("bend")

            elif (n_seg[1] < seg[1] and p_seg[0] < seg[0]) or (
                p_seg[1] < seg[1] and n_seg[0] < seg[0]
            ):
                # Angle Top-Left
                image = self._get_sprite("bend")
                image = pygame.transform.rotate(image, 90)

            elif (n_seg[0] < seg[0] and p_seg[1] > seg[1]) or (
                p_seg[0] < seg[0] and n_seg[1] > seg[1]
            ):
                # Angle Left-Down
                image = self._get_sprite("bend")
                image = pygame.transform.rotate(image, 180)

            elif (n_seg[1] > seg[1] and p_seg[0] > seg[0]) or (
                p_seg[1] > seg[1] and n_seg[0] > seg[0]
            ):
                # Angle Down-Right
                image = self._get_sprite("bend")
                image = pygame.transform.rotate(image, 270)

            else:
                # Failsafe - probably won't happen
                pygame.draw.rect(
                    self.main_layer,
                    colors["green"],
                    [seg[0], seg[1], self.sprite_size, self.sprite_size],
                )
                return

            self.main_layer.blit(image, seg)

    def _draw_apple(self):
        """Helper function to draw apple on display"""
        image = self._get_sprite("apple")
        self.main_layer.blit(image, self.apple)

    def _update_display(self):
        """Helper function to update pygame display"""
        self.main_layer.fill(colors["white"])
        self._draw_apple()
        self._draw_snake()
        self.display.blit(self.main_layer, (0, 0))
        pygame.display.update()
        self._update_game_state()

    def _set_direction(self, direction):
        """Helper function to set snake direction delta"""
        if (
            direction == "up"
            and self.snake_delta_y != self.sprite_size
            and not self._is_stationary()
        ):
            self.snake_delta_y = -self.sprite_size
            self.snake_delta_x = 0
        elif direction == "down" and self.snake_delta_y != -self.sprite_size:
            self.snake_delta_y = self.sprite_size
            self.snake_delta_x = 0
        elif direction == "left" and self.snake_delta_x != self.sprite_size:
            self.snake_delta_x = -self.sprite_size
            self.snake_delta_y = 0
        elif direction == "right" and self.snake_delta_x != -self.sprite_size:
            self.snake_delta_x = self.sprite_size
            self.snake_delta_y = 0
        else:
            # Unknown move - do nothing
            pass

    def _is_stationary(self):
        """Helper function to check if snake is standing still"""
        if self.snake_delta_x == 0 and self.snake_delta_y == 0:
            return True
        else:
            return False

    def _move_snake(self):
        """Helper function to move snake position"""
        snake_head = self.snake[-1].copy()
        snake_head[0] += self.snake_delta_x
        snake_head[1] += self.snake_delta_y
        self.snake.append(snake_head)

        if len(self.snake) > self.snake_len:
            del self.snake[0]

    def _check_move_event(self, event):
        """Helper function to extract move from user keyboard input"""
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_LEFT:
                self._set_direction("left")
            if event.key == pygame.K_RIGHT:
                self._set_direction("right")
            if event.key == pygame.K_UP:
                self._set_direction("up")
            if event.key == pygame.K_DOWN:
                self._set_direction("down")

    def _check_quit_event(self, event):
        """Helper function to check for "user want's to quit" conditions"""
        if event.type == pygame.QUIT:
            self._game_over(msg="Quitting...")
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_q:
                self._game_over(msg="Quitting...")

    def _check_if_apple_eaten(self):
        """Helper function to check if snake has eaten the apple"""
        if self.snake[-1] == self.apple:
            self.apple = self._get_random_position()
            self.snake_len += 1
            self.visited_nodes.clear()
            self.search_layer.fill((0, 0, 0, 0))

    def _check_collision_with_self(self):
        """Helper function to check if snake has eaten itself"""
        if self.snake_len > 1 and self.snake[-1] in self.snake[:-1]:
            self._game_over()

    def _check_out_of_bounds(self):
        """Helper function to check if snake has moved outside the board"""
        snake_head = self.snake[-1]
        if (
            snake_head[0] >= self.width
            or snake_head[0] < 0
            or snake_head[1] >= self.height
            or snake_head[1] < 0
        ):
            self._game_over()

    def _check_win_condition(self):
        """Helper function to check for win-conditions"""
        # Check win condition
        if 0 not in self.game_state:
            self._game_won()

    def _get_random_position(self):
        """Helper function to generate a random, legal position"""
        if not self.snake and not self.apple:
            return [
                utils.rand_p(self.width, self.sprite_size),
                utils.rand_p(self.height, self.sprite_size),
            ]

        legal_positions = self._get_legal_positions()
        pos = random.choice(legal_positions)
        return [pos[0] * self.sprite_size, pos[1] * self.sprite_size]

    def _init_snake(self):
        """Helper function to generate initial snake position"""
        snake = []
        for i in range(self.snake_len):
            x = int(self.width / self.sprite_size / 2) * self.sprite_size
            y = int(self.height / self.sprite_size / 2) * self.sprite_size
            y += i * self.sprite_size
            snake.append([x, y])
        return snake

    def _get_legal_positions(self):
        """Helper function to get all current legal positions"""
        return np.array([p for p in zip(*np.where(self.game_state == 0))])

    def _game_over(self, msg="You Lost"):
        """Helper function to display a loss-condition message and exit the game"""
        self._display_message(msg)
        self._exit()

    def _game_won(self, msg="You Won!"):
        """Helper function to display a win-condition message and exit the game"""
        self._display_message(msg)
        self._exit()

    def _exit(self):
        """Helper function to exit the game"""
        pygame.quit()
        quit()

    def _update_game_state(self):
        """Converts the game canvas into a 2D numpy representation and
        updates the game state

        Possible game states:
            0: Empty location
            1: Snake body segment
            2: Snake head segment
            3: Apple
        """
        self.game_state = np.zeros(
            (int(self.width / self.sprite_size), int(self.height / self.sprite_size))
        )

        if self.snake:
            self.game_state[
                utils.pos_to_int(self.snake[-1], self.sprite_size)
            ] = states["snake_head"]
            for segment in self.snake[:-1]:
                self.game_state[utils.pos_to_int(segment, self.sprite_size)] = states[
                    "snake_body"
                ]

        if self.apple:
            self.game_state[utils.pos_to_int(self.apple, self.sprite_size)] = states[
                "apple"
            ]

    def is_legal(self, moves):
        """Function to check if a move or a sequence of moves is legal / will not end
        in a loss-condition

        This function will simulate moving the snake according to the
        provided move or sequence of moves.

        If a singular move is given as a string, it is put into a tuple

        Returns:
            bool: True if all the moves are legal
            bool: False if any of the moves end in a loss-condition
        """
        temp_snake = self.snake.copy()

        if isinstance(moves, str):
            moves = (moves,)

        for move in moves:
            # Simulate move by updating temp_snake
            temp_head = temp_snake[-1].copy()
            temp_snake.append(temp_head)
            if len(temp_snake) > self.snake_len:
                del temp_snake[0]

            if move == "up":
                temp_head[1] += -self.sprite_size
            elif move == "down":
                temp_head[1] += self.sprite_size
            elif move == "left":
                temp_head[0] += -self.sprite_size
            elif move == "right":
                temp_head[0] += self.sprite_size
            else:
                # Illegal move?
                return False

            # Out of bounds
            if (temp_head[0] < 0 or temp_head[0] >= self.width) or (
                temp_head[1] < 0 or temp_head[1] >= self.height
            ):
                return False

            # Collision with self
            # if self.snake_len > 1 and temp_head in self.snake[:-1]:
            if temp_head in temp_snake[:-1]:
                return False

        return True

    def is_winning(self, moves):
        """Function to check if a move or a sequence of moves leads to the apple

        If a singular move is given as a string, it is put into a tuple

        NB! This function will not check for legal moves

        Returns:
            bool: True if the sequence lead to the apple
            bool: False if the sequence does not lead to the apple
        """
        temp_snake = self.snake.copy()
        temp_head = temp_snake[-1].copy()

        if isinstance(moves, str):
            moves = (moves,)

        for move in moves:

            if move == "up":
                temp_head[1] += -self.sprite_size
            elif move == "down":
                temp_head[1] += self.sprite_size
            elif move == "left":
                temp_head[0] += -self.sprite_size
            elif move == "right":
                temp_head[0] += self.sprite_size
            else:
                # Illegal move?
                return False

            if temp_head[0] == self.apple[0] and temp_head[1] == self.apple[1]:
                return True

        return False

    def simulate_move(self, pos, move):
        """Simulates a move from the given position, and returns the new position"""
        new_pos = pos.copy()
        if move == "up":
            new_pos[1] += -1
        elif move == "down":
            new_pos[1] += 1
        elif move == "left":
            new_pos[0] += -1
        elif move == "right":
            new_pos[0] += 1
        else:
            raise ValueError(f"Invalid Move '{move}'")
        return new_pos

    def get_snake_head_position(self):
        """Returns the current position og the snake head in the game state"""
        pos = np.where(self.game_state == states["snake_head"])
        return list(np.hstack(pos))

    def get_apple_position(self):
        """Returns the current position of the apple in the game state"""
        pos = np.where(self.game_state == states["apple"])
        return list(np.hstack(pos))

    def get_distance(self, p, q):
        """Calculates distance between two points"""
        return abs(p[0] - q[0]) + abs(p[1] - q[1])

    def register_ai(self, f):
        """Decorator for registering 'external' AI"""
        self.ai = f

    def start(self, use_ai=False):
        # self._update_game_state()
        self.snake = self._init_snake()
        self._update_game_state()
        self.apple = self._get_random_position()
        self._update_display()

        # Game Loop
        while True:
            for event in pygame.event.get():
                self._check_quit_event(event)

                if not use_ai:
                    self._check_move_event(event)

            if use_ai:
                if not self.moves:
                    self.moves = self.ai()
                    if not self.moves:
                        self._game_over()
                    if isinstance(
                        self.moves, str
                    ):  # For compatibility to older versions
                        self.moves = [self.moves]
                direction = self.moves.pop(0)
                self._set_direction(direction)

            if self._is_stationary():
                self.clock.tick(config.CLOCK_SPEED)
                continue

            self._move_snake()
            self._check_if_apple_eaten()
            self._check_out_of_bounds()
            self._check_collision_with_self()
            self._check_win_condition()

            self._update_display()
            self.clock.tick(config.CLOCK_SPEED)

    def draw_square(self, pos, value=None, pause=False, color=None, draw_heatmap=False, show_visit_count=False, tick_limit=0):
        """Helper function to draw a sprite sized square at a specified position.

        :param pos: Position of the square that is to be drawn. The coordinates used are the grid coordinates.
        :param value: Value to be written in the square. NB: Can be overwritten if other parameters are active.
        :param pause: Wait for user input by pressing down a key before drawing the square.
        :param color:  The color of the square. NB: Can be overwritten if other parameters are active.
        :param draw_heatmap: Draw the square as a part of a heatmap based on the number of times the position has been used earlier with draw_heatmap or show_visit_count. NB: Will overwrite the color parameter.
        :param show_visit_count: Draw the number of times the position has been used earlier with draw_heatmap or show_visit_count. NB: Will overwrite the value parameter.
        :param tick_limit: Set the limit of how many times the function can be called each second by adding delay. If the limit is set to 0, it will run without delay.
        """
        if pause:
            while True:
                next_step = False
                for event in pygame.event.get():
                    self._check_quit_event(event)

                    if event.type == pygame.KEYDOWN:
                        next_step = True
                if next_step:
                    break

        # Process events before drawing square
        for event in pygame.event.get():
            self._check_quit_event(event)

        count = 0
        # Decides if the number of times a position is visited gets counted
        if draw_heatmap or show_visit_count:
            pos = tuple(pos)
            if pos not in self.visited_nodes:
                self.visited_nodes[pos] = 1
            else:
                self.visited_nodes[pos] += 1
            count = self.visited_nodes.get(pos, 0)

        # Decides the color of the square
        if color is not None and not draw_heatmap:
            channel_count = len(color)
            if channel_count == 3:
                color = color + (160,)
            elif channel_count == 4:
                pass
            else:
                raise ValueError(f"The color is wrong. It should be of length 3 or 4. Got one of length: {len(color)}")
        elif draw_heatmap:
            hue = max((240 - count) / 360, 0)
            color = tuple([int(i * 255) for i in colorsys.hls_to_rgb(hue, 0.3, 1)]) + (160,)
        else:
            color = (0, 0, 240, 160)

        # Draw the square
        square = pygame.Rect([pos[0] * self.sprite_size, pos[1] * self.sprite_size, self.sprite_size, self.sprite_size])
        self.display.blit(self.main_layer, square.topleft, area=square)
        pygame.draw.rect(self.search_layer, color, square)

        # Render text in the drawn square
        if value is not None or show_visit_count:
            if show_visit_count:
                value = str(count)
            message = self.square_font.render(str(value), True, colors['black'])
            message_rect = message.get_rect(center=square.center)
            self.search_layer.blit(message, message_rect)

        self.display.blit(self.search_layer, square.topleft, area=square)
        pygame.display.update(square)
        self.clock.tick(tick_limit)
