import pygame
import numpy as np

class Snake:
    def __init__(self, map, size, col_head, col_body, hunger_threshold = 200):
        # Put snake on the right map and give it the specified size
        self.map = map
        self.size = size
        self.COL_HEAD, self.COL_BODY = col_head, col_body
        self.HUNGER_TH = hunger_threshold

        # Create snake and put its head on a safe position (no collision at spawn)
        self.snake = np.zeros(shape=(self.size, 2), dtype=int)
        self.snake[0][0] = np.random.randint(self.size, self.map.MAP_H - self.size)     # y postion of the head
        self.snake[0][1] = np.random.randint(self.size, self.map.MAP_W - self.size)     # x postion of the head

        # Choose starting direction (-> towards farthest wall)
        self.x_vel = 0
        self.y_vel = 0

        self.changed_dir = False                # Used to make sure direction is only changed once per frame

        dists = self.distances_to_walls()
        
        if np.max(dists) == dists[0]:
            self.change_dir('up')
        elif np.max(dists) == dists[1]:
            self.change_dir('down')
        elif np.max(dists) == dists[2]:
            self.change_dir('left')
        elif np.max(dists) == dists[3]:
            self.change_dir('right')

        # Put body parts following direction
        for i in range(1, len(self.snake)):
            self.snake[i][0] = self.snake[i-1][0] - self.y_vel
            self.snake[i][1] = self.snake[i-1][1] - self.x_vel

        for i in range(len(self.snake)):
            self.map.map[self.snake[i][0]][self.snake[i][1]] = self.map.SNAKE

        # Setup snake properties
        self.alive = True
        self.steps = 0
        self.steps_without_eating = 0
        self.hungry = False

    
    # Updates the snake at each call
    def update(self):
        if self.alive:
            self.changed_dir = False

            self.move()

            if self.steps_without_eating > self.HUNGER_TH:
                self.hungry = True
            else:
                self.hungry = False

    
    # Moves the snake following the velocity, if move hits wall, snake dies
    def move(self):
        next_pos_x = (self.snake[0][1] + self.x_vel) % self.map.MAP_W
        next_pos_y = (self.snake[0][0] + self.y_vel) % self.map.MAP_H

        # Die if hits wall
        if self.map.map[next_pos_y][next_pos_x] == self.map.WALL:
            self.alive = False
            return

        # Die if hits self
        for i in range(1, len(self.snake)):
            if next_pos_x == self.snake[i][1] and next_pos_y == self.snake[i][0]:
                self.alive = False
                return

        # Grow if eats fruit
        if self.map.map[next_pos_y][next_pos_x] == self.map.FRUIT:
            self.size += 1
            self.steps_without_eating = -1

            self.map.fruit_on_map = False

            self.snake = np.append(self.snake, [[self.snake[-1][0] + self.tail_vel()[0], self.snake[-1][1] + self.tail_vel()[1]]], axis=0)

        
        # Move body if everything OK
        prev_x = self.snake[0][1]
        prev_y = self.snake[0][0]

        self.snake[0][1] = next_pos_x
        self.snake[0][0] = next_pos_y

        self.map.map[prev_y][prev_x] = self.map.EMPTY
        self.map.map[self.snake[0][0]][self.snake[0][1]] = self.map.SNAKE
        
        for i in range(1, len(self.snake)):
            tmp_x = self.snake[i][1]
            tmp_y = self.snake[i][0]

            self.snake[i][1] = prev_x
            self.snake[i][0] = prev_y

            prev_x = tmp_x
            prev_y = tmp_y

            self.map.map[prev_y][prev_x] = self.map.EMPTY
            self.map.map[self.snake[i][0]][self.snake[i][1]] = self.map.SNAKE

        # Increase steps taken
        self.steps += 1
        self.steps_without_eating += 1


    # Draw snake on window (on the right map)
    def draw(self, win, bloc_size_x, bloc_size_y, debug=False):
        map_pos_x_px = bloc_size_x * self.map.MAP_W * self.map.POS_X
        map_pos_y_px = bloc_size_y * self.map.MAP_H * self.map.POS_Y

        p = 1

        bloc_w = int(p * bloc_size_x)
        bloc_h = int(p * bloc_size_y)

        for i in range(len(self.snake)):
            pos_x = int(map_pos_x_px + bloc_size_x * self.snake[i][1] + (1 - p) * bloc_size_x / 2)
            pos_y = int(map_pos_y_px + bloc_size_y * self.snake[i][0] + (1 - p) * bloc_size_y / 2)
            
            col = self.COL_BODY
            if i == 0:
                col = self.COL_HEAD

            pygame.draw.rect(
                win,
                col,
                [
                    pos_x,
                    pos_y,
                    bloc_w,
                    bloc_h
                ]
            )

        if debug:
            n = 5
            is_empty, is_fruit = self.check_neighbours(n=n)

            for i in range(int(-(n-1) / 2), int(((n-1) / 2) + 1)):
                for j in range(int(-(n-1) / 2), int(((n-1) / 2) + 1)):
                    pos_x = int(map_pos_x_px + bloc_size_x * (self.snake[0][1] + j) + (1 - p) * bloc_size_x / 2)
                    pos_y = int(map_pos_y_px + bloc_size_y * (self.snake[0][0] + i) + (1 - p) * bloc_size_y / 2)

                    if i == 0 and j == 0:
                        continue

                    if is_empty[int((n - 1) / 2) + i][int((n - 1) / 2) + j]:
                        col = [0, 255, 0]
                        pygame.draw.rect(win, col, [pos_x, pos_y, bloc_w, bloc_h])
                    
                    if is_fruit[int((n - 1) / 2) + i][int((n - 1) / 2) + j]:
                        col = [0, 0, 255]
                        pygame.draw.rect(win, col, [pos_x, pos_y, bloc_w, bloc_h])


    # Changes velocity of the snake    
    def change_dir(self, dir):
        if not self.changed_dir:
            if dir == 'up' and self.y_vel != 1:
                self.y_vel = -1
                self.x_vel = 0

            elif dir == 'down' and self.y_vel != -1:
                self.y_vel = 1
                self.x_vel = 0

            elif dir == 'left' and self.x_vel != 1:
                self.y_vel = 0
                self.x_vel = -1

            elif dir == 'right' and self.x_vel != -1:
                self.y_vel = 0
                self.x_vel = 1

            self.changed_dir = True


    # Returns array with distances to edge walls
    def distances_to_walls(self):
        dists = [
            self.snake[0][0],                       # Distance to the top wall
            self.map.MAP_H - self.snake[0][0],      # Distance to the bot wall
            self.snake[0][1],                       # Distance to the left wall
            self.map.MAP_W - self.snake[0][1],      # Distance to the right wall
        ]

        return dists

    # Returns array with distance to fruit
    def distances_to_fruit(self):
        dists = [
            self.snake[0][0] - self.map.fruit_pos_y,    # Distance to fruit on y axis
            self.snake[0][1] - self.map.fruit_pos_x,    # Distance to fruit on x axis
        ]

        return dists

    
    # Function that checks whether blocks neighbouring the snake's head are empty or not
    def check_neighbours(self, n = 3):
        if n % 2 == 0:
            n += 1

        is_empty = np.full((n, n), True)
        is_fruit = np.full((n, n), False)

        pos_x = self.snake[0][1]
        pos_y = self.snake[0][0]

        for i in range(int(-(n-1) / 2), int(((n-1) / 2) + 1)):
            for j in range(int(-(n-1) / 2), int(((n-1) / 2) + 1)):
                if (pos_x + j <= 0) or (pos_x + j >= self.map.MAP_W) or (pos_y + i <= 0) or (pos_y + i >= self.map.MAP_H):
                    is_empty[int((n - 1) / 2) + i][int((n - 1) / 2) + j] = False
                    is_fruit[int((n - 1) / 2) + i][int((n - 1) / 2) + j] = False
                    continue

                elif self.map.map[pos_y + i][pos_x + j] == self.map.WALL:
                    is_empty[int((n - 1) / 2) + i][int((n - 1) / 2) + j] = False

                elif self.map.map[pos_y + i][pos_x + j] == self.map.FRUIT:
                    is_fruit[int((n - 1) / 2) + i][int((n - 1) / 2) + j] = True

                else:
                    for k in range(1, len(self.snake)):
                        if pos_y + i == self.snake[k][0] and pos_x + j == self.snake[k][1]:
                            is_empty[int((n - 1) / 2) + i][int((n - 1) / 2) + j] = False

        return is_empty, is_fruit


    # x and y velocities of the tail    
    def tail_vel(self):
        vel = [
            self.snake[-2][0] - self.snake[-1][0],      # Tail velocity on y axis
            self.snake[-2][1] - self.snake[-1][1],      # Tail velocity on x axis
        ]

        return vel