# Project Title

A small implementation of 🐍 that can either be played by a human, or by an AI!  
Developed as a supplement for IKT111, Univeristy of Agder.

## Getting Started
### Prerequisites

Developed and tested using Python3.7.5  
Package requirements are given in `requirements.txt`

### Installing

Download and install Python3.7.x

If you're using windows, I recommend adding Python to the system path during installation

**Windows**

Create and activate a virtual environment in PowerShell or CommandPrompt
```powershell
PS> py -3.7 -m venv C:\path\to\myenv  
PS> C:\path\to\myenv\Scripts\activate
```

Install requirements

```powershell
PS> py -m pip install -r requirements.txt
```

**Mac / Linux**

Create and activate a virtual environment

```bash
$ python3.7 -m venv venv
$ source venv/bin/activate
```

Install requirements

```bash
$ pip3 install -r requirements.txt
```

**Run Example**

Start the game for a human player:

```python
from snake import SnakeGame

snake = SnakeGame()
snake.start(use_ai=False)
```
### AI players
The game also allows you to 'register' an AI player.
If an AI is registered, each tick the game will provide the AI with a representation of the game state as an $N$x$M$ matrix. The different game elements are represented by numbers:  

`Background = 0`  
`Snake body = 1`  
`Snake head = 2`  
`Apple = 3`


Example:
```python
[[0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0],
 [0, 1, 0, 0, 0, 0],
 [0, 1, 1, 2, 0, 3],
 [0, 0, 0, 0, 0, 0],
 [0, 0, 0, 0, 0, 0]]
```

The game also expects the AI to return one of the following move actions each tick: `'up', 'down', 'left', 'right'`

To register a function as an AI, the game has a decorator that can be used. Example:
```python
from snake import SnakeGame

snake = SnakeGame()

@snake.register_ai # Decorator
def super_ai(game_state):
    #
    # Some magic AI stuff here
    #

    return move

snake.start(use_ai=True)
```
## Reporting Bugs
If you encounter any bugs please raise an issue for it, or let me know either by email or in class :) 
