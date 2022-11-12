import pygame

import neat

import numpy as np
import time
from numba import jit, cuda

from map import Map
from snake import Snake


# Controls main game
class Game:
    
    def __init__(self, win_w, win_h, nb_snakes, nb_maps_w, nb_maps_h, nb_blocs_w, nb_blocs_h, update_time):
        # Initiate pygame
        pygame.init()

        # Setup for rendering
        while win_w % (nb_blocs_w * nb_maps_w) != 0:
            win_w -=1
        while win_h % (nb_blocs_h * nb_maps_h) != 0:
            win_h -=1

        self.win = pygame.display.set_mode((win_w, win_h))

        self.NB_SNAKES = nb_snakes
        self.NB_MAPS_W, self.NB_MAPS_H = nb_maps_w, nb_maps_h
        self.NB_BLOCS_W, self.NB_BLOCS_H = nb_blocs_w, nb_blocs_h

        self.bloc_size_x = (win_w / nb_maps_w) / nb_blocs_w
        self.bloc_size_y = (win_h / nb_maps_h) / nb_blocs_h

        # Setup maps and snakes
        self.maps = []
        self.snakes = []

        # Setup game variables
        self.running = False
        self.paused = False
        self.UPDATE_TIME = update_time
        self.last_update = time.time()

    
    # Launches the classic game
    
    def run(self):
        self.clock = pygame.time.Clock()

        self.maps = []
        self.snakes = []

        k = 0
        for i in range(self.NB_MAPS_H):
            if k == self.NB_SNAKES:
                break
            for j in range(self.NB_MAPS_W):
                if k == self.NB_SNAKES:
                    break
                map = Map(self.NB_BLOCS_W, self.NB_BLOCS_H, j, i, [255, 255, 255], [255, 0, 255])
                self.maps.append(map)
                self.snakes.append(Snake(map, 2, [255, 0, 0], [0, 255, 255]))
                k += 1

        # Main game loop
        self.running = True
        while self.running:
            self.clock.tick(30)

            if time.time() - self.last_update > self.UPDATE_TIME:
                self.handle_events(handle_movement=True)

                if not self.paused:
                    self.update()

                self.draw()

                self.last_update = time.time()
    

    # Updates game status for each step
    
    def update(self):
        # Update each snake (movement, growing...)
        for snake in self.snakes:
            snake.update()

        # Update each map (mainly handle fruit spawning)
        for map in self.maps:
            map.update()


    # Draw all what is to be drawn on screen
    # @jit(target_backend ="cuda")
    def draw(self, generation=None, max_size = None, general_max_size = None):
        fill_color = [0, 0, 0]
        self.win.fill(fill_color)

        # Draw maps (walls + fruits)
        for map in self.maps:
            map.draw(self.win, self.bloc_size_x, self.bloc_size_y)

        # Draw snakes
        for snake in self.snakes:
            snake.draw(self.win, self.bloc_size_x, self.bloc_size_y, debug=False)

        # Draw info texts if specified
        if generation is not None:
            STAT_FONT = pygame.font.SysFont('comicsans', 15)
            text = STAT_FONT.render('Gen: ' + str(generation), 1, (255, 255, 255))
            self.win.blit(text, (12, 10))

        if max_size is not None:
            STAT_FONT = pygame.font.SysFont('comicsans', 12)
            text = STAT_FONT.render('Max size: ' + str(max_size), 1, (255, 255, 255))
            self.win.blit(text, (132, 10))
        
        if general_max_size is not None:
            STAT_FONT = pygame.font.SysFont('comicsans', 12)
            text = STAT_FONT.render('Max size (all): ' + str(general_max_size), 1, (255, 255, 255))
            self.win.blit(text, (132, 25))

        pygame.display.update()

    
    # Handles main game events (quit, pause, reset)
    
    def handle_events(self, handle_movement=True):
        for event in pygame.event.get():
            # Quit program if quit event occurs
            if event.type == pygame.QUIT:
                self.running = False
                pygame.quit()
                quit()

            if event.type == pygame.KEYUP:
                # Quit program if 'escape' key pressed
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    pygame.quit()
                    quit()

                # Pause game if 'p' key pressed
                if event.key == pygame.K_p:
                    self.paused = not self.paused

                # Reset dead snakes, unpause if all snakes dead
                if event.key == pygame.K_SPACE:
                    all_snakes_dead = True
                    for i in range(len(self.snakes)):
                        if not self.snakes[i].alive:
                            self.snakes[i] = Snake(self.snakes[i].map, 2, [255, 0, 0], [0, 255, 255], hunger_threshold=100)
                        else:
                            all_snakes_dead = False
                    if all_snakes_dead:
                        self.paused = False
                
                if handle_movement:
                    # Move up
                    if event.key == pygame.K_UP:
                        for snake in self.snakes:
                            snake.change_dir('up')

                    # Move down
                    elif event.key == pygame.K_DOWN:
                        for snake in self.snakes:
                            snake.change_dir('down')

                    # Move left
                    elif event.key == pygame.K_LEFT:
                        for snake in self.snakes:
                            snake.change_dir('left')

                    # Move right
                    elif event.key == pygame.K_RIGHT:
                        for snake in self.snakes:
                            snake.change_dir('right')

    
    # Trains neat algorithm (alternative to classic run)
    
    def run_neat(self, genomes, config):
        self.clock = pygame.time.Clock()

        max_size = 0

        # Keep track of genomes and corresponding neural networks
        sizes = []
        self.maps = []
        self.snakes = []
        ge = []
        nets = []

        k = 0
        for i in range(self.NB_MAPS_H):
            if k == len(genomes):
                break
            for j in range(self.NB_MAPS_W):
                if k == len(genomes):
                    break
                map = Map(self.NB_BLOCS_W, self.NB_BLOCS_H, j, i, [255, 255, 255], [255, 0, 255])
                self.maps.append(map)
                self.snakes.append(Snake(map, 2, [255, 0, 0], [0, 255, 255], hunger_threshold=50))
                sizes.append(2)
                k += 1

        for _, genome in genomes:
            ge.append(genome)
            genome.fitness = 0

            net = neat.nn.FeedForwardNetwork.create(genome, config)
            nets.append(net)

        # Main game loop
        self.running = True
        while self.running:
            self.clock.tick(30)

            if time.time() - self.last_update > self.UPDATE_TIME:
                self.handle_events(handle_movement=False)       # Do not handle movement since AI takes care of that

                if not self.paused:
                    # Observe and take action for each snake
                    for i in range(len(self.snakes)):
                        is_empty, is_fruit = self.snakes[i].check_neighbours(n=5)
                        is_empty = [n for row in is_empty for n in row]
                        # is_fruit = [n for row in is_fruit for n in row]
                        output = nets[i].activate([
                            *is_empty,
                            # *is_fruit,
                            *self.snakes[i].distances_to_walls(),
                            *self.snakes[i].distances_to_fruit(),
                            self.snakes[i].x_vel,
                            self.snakes[i].y_vel,
                            *self.snakes[i].tail_vel(),
                        ])

                        th = 0.5
                        if np.max(output) == output[0]:
                            if output[0] > th:
                                self.snakes[i].change_dir('up')
                        elif np.max(output) == output[1]:
                            if output[1] > th:
                                self.snakes[i].change_dir('down')
                        elif np.max(output) == output[2]:
                            if output[2] > th:
                                self.snakes[i].change_dir('left')
                        elif np.max(output) == output[3]:
                            if output[3] > th:
                                self.snakes[i].change_dir('right')

                    # Update game
                    self.update()

                    elems_to_remove = []
                    # Reward good snakes and kill hungry ones
                    for i in range(len(self.snakes)):
                        if self.snakes[i].size > max_size:
                            max_size = self.snakes[i].size

                        if max_size > self.general_max_size:
                            self.general_max_size = max_size

                        if self.snakes[i].size > sizes[i]:
                            # ge[i].fitness += 3
                            sizes[i] = self.snakes[i].size

                        if self.snakes[i].hungry:
                            self.snakes[i].alive = False
                            # ge[i].fitness -= 1.5

                            self.snakes[i].steps -= 50

                        if not self.snakes[i].alive:
                            # if not self.snakes[i].hungry:
                                # ge[i].fitness -= 1
                            elems_to_remove.append(i)

                        ge[i].fitness = ((self.snakes[i].size - 2) ** 3) / self.snakes[i].steps

                    # Remove dead snakes from lists
                    sizes[:] = [sizes[i] for i in range(len(sizes)) if i not in elems_to_remove]
                    self.snakes[:] = [self.snakes[i] for i in range(len(self.snakes)) if i not in elems_to_remove]
                    self.maps[:] = [self.maps[i] for i in range(len(self.maps)) if i not in elems_to_remove]
                    ge[:] = [ge[i] for i in range(len(ge)) if i not in elems_to_remove]
                    nets[:] = [nets[i] for i in range(len(nets)) if i not in elems_to_remove]

                    # Stop run if all snakes dead
                    if len(self.snakes) == 0:
                        self.running = False

                self.draw(max_size=max_size, general_max_size=self.general_max_size, generation=self.gen)

                self.last_update = time.time()

        self.gen += 1
