import random
import sys
import time 
import pygame
import numpy as np

pygame.init()
font_style = pygame.font.SysFont(None, 50)

def message(msg, color):
    global display, d_width, d_height

    mesg = font_style.render(msg, True, color)
    display.blit(mesg, [d_width / 2.4, d_height / 2.4])

colors = {
    'red':   (255, 0, 0),
    'green': (0, 255, 0),
    'blue':  (0, 0, 255),
    'black': (0, 0, 0),
    'gray':  (100, 100, 100),
    'white': (255, 255, 255),
}

d_width, d_height = 800, 400

display = pygame.display.set_mode((d_width, d_height))
pygame.display.set_caption('Snake')

game_over = False

clock = pygame.time.Clock()

snake_size = 40
snake_speed = 10

def load_image(img_path, colorkey=None):
    image = pygame.image.load(img_path).convert()
    image = pygame.transform.scale(image, (snake_size, snake_size))
    if colorkey:
        image.set_colorkey(colorkey)
    return image

def draw_snake(snake):
    # Determine correct image for snake head
    snake_head = snake[-1]
    if snake_head[1] < snake[-2][1]:
        # Moving Up
        image = load_image('gfx/head_white.png')

    elif snake_head[0] > snake[-2][0]:
        # Moving right
        image = load_image('gfx/head_white.png')
        image = pygame.transform.rotate(image, 270)

    elif snake_head[1] > snake[-2][1]:
        # Moving down
        image = load_image('gfx/head_white.png')
        image = pygame.transform.rotate(image, 180)

    elif snake_head[0] < snake[-2][0]:
        # Moving left
        image = load_image('gfx/head_white.png')
        image = pygame.transform.rotate(image, 90)

    display.blit(image, snake_head)

    # Determine correct image for snake tail
    snake_tail = snake[0]
    if snake_tail[1] > snake[1][1]:
        # Moving Up
        image = load_image('gfx/tail_white.png')

    elif snake_tail[0] < snake[1][0]:
        # Moving right
        image = load_image('gfx/tail_white.png')
        image = pygame.transform.rotate(image, 270)

    elif snake_tail[1] < snake[1][1]:
        # Moving down
        image = load_image('gfx/tail_white.png')
        image = pygame.transform.rotate(image, 180)

    elif snake_tail[0] > snake[1][0]:
        # Moving left
        image = load_image('gfx/tail_white.png')
        image = pygame.transform.rotate(image, 90)

    display.blit(image, snake_tail)
    
    # Determine correct image for the body
    for i, seg in enumerate(snake[1:-1], 1):
        p_seg = snake[i + 1]
        n_seg = snake[i - 1]

        if (n_seg[0] < seg[0] and p_seg[0] > seg[0]) or \
           (p_seg[0] < seg[0] and n_seg[0] > seg[0]):
            # Horisontal segment
            image = load_image('gfx/straight.png')

        elif (n_seg[1] < seg[1] and p_seg[1] > seg[1]) or \
             (p_seg[1] < seg[1] and n_seg[1] > seg[1]):
            # Vertical segment
            image = load_image('gfx/straight.png')
            image = pygame.transform.rotate(image, 90)

        elif (n_seg[0] > seg[0] and p_seg[1] < seg[1]) or \
             (p_seg[0] > seg[0] and n_seg[1] < seg[1]):
            # Angle Left-Up
            image = load_image('gfx/bend_white.png')

        elif (n_seg[1] < seg[1] and p_seg[0] < seg[0]) or \
             (p_seg[1] < seg[1] and n_seg[0] < seg[0]):
            # Angle Top-Left
            image = load_image('gfx/bend_white.png')
            image = pygame.transform.rotate(image, 90)    

        elif (n_seg[0] < seg[0] and p_seg[1] > seg[1]) or \
             (p_seg[0] < seg[0] and n_seg[1] > seg[1]):
            # Angle Left-Down
            image = load_image('gfx/bend_white.png')
            image = pygame.transform.rotate(image, 180)

        elif (n_seg[1] > seg[1] and p_seg[0] > seg[0]) or \
             (p_seg[1] > seg[1] and n_seg[0] > seg[0]):
            # Angle Down-Right
            image = load_image('gfx/bend_white.png')
            image = pygame.transform.rotate(image, 270)

        else:
            # Failsafe - probably won't happen
            pygame.draw.rect(display, colors['green'], [seg[0], seg[1], snake_size, snake_size])
            return
        
        display.blit(image, seg)

def draw_apple(pos):
    image = load_image('gfx/apple_white.png')
    display.blit(image, pos)

def rand_p(_max):
    return round(random.randrange(0, _max - snake_size) / snake_size) * snake_size

def random_position(illegal=[]):
    x = rand_p(d_width)
    y = rand_p(d_height)

    while [x, y] in illegal:
        x = rand_p(d_width)
        y = rand_p(d_height)

    return (x, y)

def is_stationary(x_d, y_d):
    if x_d == 0 and y_d == 0:
        return True
    else:
        return False

def pos_to_int(pos):
    return (int(pos[0] / snake_size), 
            int(pos[1] / snake_size))

def get_game_state(snake, apple):
    SNAKE = 1
    APPLE = 2

    game_state = np.zeros((int(d_width / snake_size), int(d_height / snake_size)))
    for segment in snake:
        game_state[pos_to_int(segment)] = SNAKE
    game_state[pos_to_int(apple)] = APPLE

    return game_state

def game_loop():
    game_over = False
    msg = 'You lost'

    x_delta = 0
    y_delta = 0


    snake_len = 3
    snake_list = [[int(d_width / 2), int((d_height / 2)) + i * snake_size] 
                  for i in range(snake_len)]

    apple_x, apple_y = random_position(illegal=snake_list)

    display.fill(colors['white'])
    draw_apple((apple_x, apple_y))
    draw_snake(snake_list)
    pygame.display.update()

    while not game_over:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game_over = True
                break
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    game_over = True
                    break
                if event.key == pygame.K_LEFT and x_delta != snake_size:
                    x_delta = -snake_size
                    y_delta = 0
                    break
                if event.key == pygame.K_RIGHT and x_delta != -snake_size:
                    x_delta = snake_size
                    y_delta = 0
                    break
                if event.key == pygame.K_UP and y_delta != snake_size and not is_stationary(x_delta, y_delta):
                    y_delta = -snake_size
                    x_delta = 0
                    break
                if event.key == pygame.K_DOWN and y_delta != -snake_size:
                    y_delta = snake_size
                    x_delta = 0
                    break

        if is_stationary(x_delta, y_delta):
            clock.tick(snake_speed)
            continue
        
        # Move the snake by creating a 'new head'
        # at the new position
        x, y = snake_list[-1]
        x += x_delta
        y += y_delta
        snake_list.append([x, y])

        if len(snake_list) > snake_len:
            del snake_list[0]

        # Check if snake is outside the game board
        if x >= d_width or x < 0 or y >= d_height or y < 0:
            break

        # Check win condition
        game_state = get_game_state(snake_list, (apple_x, apple_y))
        if not 0 in game_state:
            msg = 'You won!'
            break

        # Check if snake has eaten the apple
        # Don't remove the tail-end if true to allow growth
        if x == apple_x and y == apple_y:
            apple_x, apple_y = random_position(illegal=snake_list)
            snake_len += 1


        # Check if snake has collided with itself:
        if len(snake_list) > 1:
            for x_body, y_body in snake_list[:-1]:
                if x == x_body and y == y_body:
                    game_over = True

        if not game_over:
            display.fill(colors['white'])
            draw_apple((apple_x, apple_y))
            draw_snake(snake_list)          
            pygame.display.update()

            clock.tick(snake_speed)

    message(msg, colors['blue'])
    pygame.display.update()
    time.sleep(1)

    pygame.quit()
    quit()

if __name__ == '__main__':
    game_loop()