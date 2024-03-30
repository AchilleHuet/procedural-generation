import pygame
from random import choices
from typing import Optional, Tuple
import numpy as np
from time import time

DARK_GREEN = (0, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 200)
GRAY = (100, 100, 100)

SCREEN_SIZE = (1000, 500)
TILE_SIZE = (5, 5)
MAP_SIZE = (SCREEN_SIZE[0]//TILE_SIZE[0], SCREEN_SIZE[1]//TILE_SIZE[1])


TIMER = {}

def timer(func):
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        total_time = TIMER.get(func_name, 0)
        t1 = time()
        value = func(*args, **kwargs)
        t2 = time()
        TIMER[func_name] = total_time + t2 - t1
        return value
    return wrapper


class Tile:
    """
    Represents a square of terrain, with a specific type and corresponding color.
    Proximity constraints are applied, forbidding certain types of tiles to be next to one another.
    """

    types = [
        "forest",
        "meadow",
        "beach",
        "sea",
        "mountains",
    ]

    type_to_color = {
        "forest": DARK_GREEN,
        "meadow": GREEN,
        "beach": YELLOW,
        "sea": BLUE,
        "mountains": GRAY,
    }

    allowed_neighbors = {
        "mountains": {"mountains", "forest"},
        "forest": {"mountains", "forest", "meadow"},
        "meadow": {"forest", "meadow", "beach"},
        "beach": {"meadow", "beach", "sea"},
        "sea": {"beach", "sea"},
    }

    type_weights = {
        "mountains": 1,
        "forest": 1.5,
        "meadow": 2,
        "beach": 1,
        "sea": 0.75,
    }

    max_score = len(types)+1

    def __init__(self, i, j):
        self.x: int = TILE_SIZE[0]*i
        self.y: int = TILE_SIZE[1]*j
        self.choices: list[str] =  Tile.types
        self.type: Optional[str] = None
        self.color: Tuple[int] = (0, 0, 0)
        self.rect = pygame.Rect(self.x, self.y, TILE_SIZE[0], TILE_SIZE[1])
    
    @property
    def score(self):
        return Tile.max_score if self.type is not None else len(self.choices)
    
    def choose_type(self):
        [self.type] = choices(self.choices, weights=[Tile.type_weights[c] for c in self.choices])
        self.color = Tile.type_to_color[self.type]
        # self.choices.remove(self.type)
        return self.type
    
    def draw(self):
        pygame.draw.rect(screen, self.color, self.rect)


tiles = [[Tile(i, j) for i in range(MAP_SIZE[0])] for j in range(MAP_SIZE[1])]
scores = np.array([[tile.score for tile in row] for row in tiles])

@timer
def get_neighbors(i, j):
    neighbors = []
    if i > 0:
        neighbors.append((i-1,j))
    if j > 0:
        neighbors.append((i,j-1))
    if i < MAP_SIZE[0]-1:
        neighbors.append((i+1,j))
    if j < MAP_SIZE[1]-1: 
        neighbors.append((i,j+1))
    return neighbors

@timer
def check_neighbors(tiles, tile_type, neighbors):
    for (i1, j1) in neighbors:
        tile = tiles[j1][i1]
        new_choices = [x for x in tile.choices if x in Tile.allowed_neighbors[tile_type]]
        if tile.type is None and len(new_choices) == 0:
            return False
    return True

@timer
def update_neighbors(tiles, scores, tile_type, neighbors):
    for (i1, j1) in neighbors:
            tile = tiles[j1][i1]
            tile.choices = [x for x in tile.choices if x in Tile.allowed_neighbors[tile_type]]
            scores[j1][i1] = tile.score
    return tiles, scores

@timer
def choose_tile(scores, minimum):
    target_tiles = list(zip(*np.where(scores==minimum)))
    [(j, i)] = choices(target_tiles)
    return i, j

@timer
def find_and_update_most_constrained_tile(tiles, scores):
    minimum = np.min(scores)
    if minimum == Tile.max_score:
        return None, None, None
    
    # chosse a random tile from the tiles with the least possibilities    
    i, j = choose_tile(scores, minimum)

    # update the tile
    tile = tiles[j][i]
    neighbors = get_neighbors(i,j)
    valid = False
    while not valid:
        new_type = tile.choose_type()
        valid = check_neighbors(tiles, new_type, neighbors)
        if not valid:
            tile.choices.remove(new_type)

    tile.draw()
    scores[j][i] = tile.score

    # update nearby tile constraints and scores
    tiles, scores = update_neighbors(tiles, scores, new_type, neighbors)

    return tiles, scores, tile

@timer
def update_screen(tile):
    if tile is not None:
        pygame.display.update(tile.rect)


if __name__ == "__main__":
    
    pygame.init()

    pygame.display.set_caption("Procedural Generation")
    screen = pygame.display.set_mode(SCREEN_SIZE)
    screen.fill((0, 0, 0))
    
    # Main Loop
    clock = pygame.time.Clock()
    RUN = True

    while RUN:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                RUN = False

        if tiles is not None:
            tiles, scores, updated_tile = find_and_update_most_constrained_tile(tiles, scores)
            update_screen(updated_tile)

    print(TIMER)

    # Exit main loop
    pygame.quit()
