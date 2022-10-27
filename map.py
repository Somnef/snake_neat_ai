import pygame
import numpy as np

# Structure for each map in the game
class Map:
    def __init__(self, map_w, map_h, pos_x, pos_y, col_walls, col_fruits):
        # Initiate map properties
        self.MAP_W, self.MAP_H = map_w, map_h
        self.POS_X, self.POS_Y = pos_x, pos_y
        self.COL_WALLS, self.COL_FRUITS = col_walls, col_fruits

        # Possible states of each bloc
        self.EMPTY = 0
        self.WALL = 1
        self.FRUIT = 2
        self.SNAKE = 3

        # Map creation (walls on the edges, rest is empty)
        self.map = np.zeros(shape=(self.MAP_H, self.MAP_W))
        for i in range(self.MAP_H):
            for j in range(self.MAP_W):
                if i == 0 or j == 0 or i == self.MAP_H-1 or j == self.MAP_W-1:
                    self.map[i][j] = self.WALL
                else:
                    self.map[i][j] = self.EMPTY

        # Putting first fruit on map
        self.fruit_pos_x = 0
        self.fruit_pos_y = 0

        while self.map[self.fruit_pos_y][self.fruit_pos_x] != self.EMPTY:
            self.fruit_pos_x = np.random.randint(1, self.MAP_W-1)
            self.fruit_pos_y = np.random.randint(1, self.MAP_H-1)

        self.map[self.fruit_pos_y][self.fruit_pos_x] = self.FRUIT
        self.fruit_on_map = True

    
    # Updates the map at each call
    def update(self):
        # If there's no fruit on the map, delete the previous one from it and spawn a new one
        if not self.fruit_on_map:
            # Delete previous fruit from map
            # self.map[self.fruit_pos_y][self.fruit_pos_x] = self.EMPTY

            # Spawn fruit if random position is not on wall
            while self.map[self.fruit_pos_y][self.fruit_pos_x] != self.EMPTY:
                self.fruit_pos_x = np.random.randint(1, self.MAP_W-1)
                self.fruit_pos_y = np.random.randint(1, self.MAP_H-1)

            self.map[self.fruit_pos_y][self.fruit_pos_x] = self.FRUIT
            self.fruit_on_map = True

    
    # Draws the map at the specified position on the window
    def draw(self, win, bloc_size_x, bloc_size_y):
        p = 0.75
        
        map_pos_x_px = bloc_size_x * self.MAP_W * self.POS_X
        map_pos_y_px = bloc_size_y * self.MAP_H * self.POS_Y

        bloc_w = int(p * bloc_size_x)
        bloc_h = int(p * bloc_size_y)

        # Draw walls and fruit
        for i in range(self.MAP_H):
            for j in range(self.MAP_W):
                pos_x = int(map_pos_x_px + bloc_size_x * j + (1 - p) * bloc_size_x / 2)
                pos_y = int(map_pos_y_px + bloc_size_y * i + (1 - p) * bloc_size_y / 2)
                
                if self.map[i][j] == self.WALL:
                    pygame.draw.rect(
                        win,
                        self.COL_WALLS,
                        [
                            pos_x,
                            pos_y,
                            bloc_w,
                            bloc_h
                        ]
                    )
                
                if self.map[i][j] == self.FRUIT:
                    pygame.draw.rect(
                        win,
                        self.COL_FRUITS,
                        [
                            pos_x,
                            pos_y,
                            bloc_w,
                            bloc_h
                        ]
                    )
