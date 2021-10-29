# Flappy

A small implementation of a zero-player based bird game that can simulate AI-generated birds!  
Developed as a supplement for IKT111, University of Agder.

## Getting Started
### Prerequisites

Developed and tested using Python3.7.5  
Package requirements are given in `requirements.txt`

---

### Installation

Download and install Python3.7.x >=

Open the `flappy` folder that you downloaded in Visual Studio Code and do the following in the Visual Studio Code terminal:

**Windows**
Install requirements
```powershell
py -m pip install -U -r requirements.txt --user
```

**Mac / Linux**
Create and activate a virtual environment

```bash
$ python3.7 -m venv venv
$ source venv/bin/activate
```

Install requirements

```bash
$ pip install -r requirements.txt
```

---

### Flappy AI
The game allows you to register a custom function to generate/edit the birds.
See example below on how to register an AI-function. 

The game expects the AI-function to return a list of birds.

Example code:
```python
from ikt111_games.flappy import Bird
from ikt111_games import Flappy
import random

# This determines both the bird lifespan
# and how many genes they have
MAX_LIFE = 1000

# This sets the maximum population size
MAX_POPULATION = 10

# Initialize the environment with a set MAX_LIFE and MAX_POPULATION
environment = Flappy(max_life=MAX_LIFE, max_population=MAX_POPULATION)


def generate_random_force(_min=-4, _max=4):
    """Generate a random force vector with x and y in the interval [_min, _max]

    Args:
        _min (int): Highest force in negative directions. Defaults to -4
        _max (int): Highest force in positive directions. Defaults to 4

    Returns:
        list: Force vector
    """
    return [random.randint(_min, _max), random.randint(_min, _max)]


# Probably some code/functions that can be implemented here


@environment.register_ai
def super_ai(birds):
    """A super AI function!"""

    # Do some AI magic here, instead of just returning the same birds

    return birds


environment.start()
```

### Adding and removing obstacles
Obstacles can be added by pressing and holding the left mouse button,
dragging the mouse to decide how large and where the obstacle should be placed,
before finally placing the obstacle by releasing the left mouse button.

The obstacles can be removed by hovering the mouse cursor over the obstacle and pressing the right mouse button.

---


## Reporting Bugs
If you encounter any bugs please raise an issue for it, or let me know either by email or in class :) 
