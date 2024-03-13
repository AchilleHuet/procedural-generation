import pygame
from random import choice
from typing import Set, Optional, Tuple

DARK_GREEN = (0, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 200)

SCREEN_SIZE = (1000, 500)
TILE_SIZE = (5, 5)
MAP_SIZE = (SCREEN_SIZE[0]//TILE_SIZE[0], SCREEN_SIZE[1]//TILE_SIZE[1])


types = [
    "forest",
    "meadow",
    "beach",
    "water",
]

type_to_color = {
    "forest": DARK_GREEN,
    "meadow": GREEN,
    "beach": YELLOW,
    "sea": BLUE,
}

allowed_neighbors = {
    "forest": {"forest", "meadow"},
    "meadow": {"forest", "meadow", "beach"},
    "beach": {"meadow", "beach", "sea"},
    "sea": {"beach", "sea"},
}


class Tile:

    def __init__(self, i, j):
        self.x: int = TILE_SIZE[0]*i
        self.y: int = TILE_SIZE[1]*j
        self.choices: Set[str] =  {"forest", "meadow", "beach", "sea"}
        self.type: Optional[str] = None
        self.color: Tuple[int] = (0, 0, 0)
    
    @property
    def score(self):
        return len(self.choices) if len(self.choices) > 0 else None
    
    def draw(self):
        rect = pygame.Rect(self.x, self.y, TILE_SIZE[0], TILE_SIZE[1])
        pygame.draw.rect(screen, self.color, rect)


tiles = [[Tile(i, j) for i in range(MAP_SIZE[0])] for j in range(MAP_SIZE[1])]

def update_neighbors(tiles, tile_type, i, j):
    tiles_to_update = []
    if i > 0:
        tiles_to_update.append((i-1,j))
    if j > 0:
        tiles_to_update.append((i,j-1))
    if i < MAP_SIZE[0]-1:
        tiles_to_update.append((i+1,j))
    if j < MAP_SIZE[1]-1: 
        tiles_to_update.append((i,j+1))
    for (i1, j1) in tiles_to_update:
            tile = tiles[j1][i1]
            tile.choices = tile.choices.intersection(allowed_neighbors[tile_type])
    return tiles

def find_and_update_most_constrained_tile(tiles):
    scores = [tile.score for row in tiles for tile in row if tile.score is not None]
    if scores == []:
        return None
    minimum = min(scores)

    for j, row in enumerate(tiles):
        for i, tile in enumerate(row):
            if tile.choices is not None and len(tile.choices) == minimum:
                new_type = choice(list(tile.choices))
                tile.type = new_type
                tile.color = type_to_color[new_type]

                tiles = update_neighbors(tiles, new_type, i, j)

                tile.choices = set()
                tile.draw()
                return tiles
            

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
            tiles = find_and_update_most_constrained_tile(tiles)

        pygame.display.flip()

    # Exit main loop
    pygame.quit()
