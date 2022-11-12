from game import Game
import neat

import pickle

import numpy as np

import os

WIN_W = 600
WIN_H = 600
 
NB_MAPS_W = 10
NB_MAPS_H = 1

NB_BLOCS_W = 12
NB_BLOCS_H = 12

# def main():
#     game = Game(WIN_W, WIN_H, NB_MAPS_W * NB_MAPS_H, NB_MAPS_W, NB_MAPS_H, NB_BLOCS_W, NB_BLOCS_H, 1/12)
#     game.run()

# main()

def run(config_path, winner_path, nb_runs):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    n = config.pop_size
    w = NB_MAPS_W
    h = int(np.ceil(n/w))

    game = Game(WIN_W, WIN_H, n, w, h, NB_BLOCS_W, NB_BLOCS_H, 1/2000)

    pop = neat.Population(config)

    pop.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    pop.add_reporter(stats)

    game.gen = 0
    game.general_max_size = 0

    winner = pop.run(game.run_neat, nb_runs)

    # Save winner to file
    with open(winner_path, 'wb') as f:
        pickle.dump(winner, f)
        f.close()


def replay_genome(config_path, genome_path):
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        config_path
    )

    game = Game(WIN_W, WIN_H, 1, 1, 1, NB_BLOCS_W, NB_BLOCS_H, 1/20)

    with open(genome_path, "rb") as f:
        genome = pickle.load(f)

    genomes = [(1, genome)]

    game.gen = 0
    game.general_max_size = 0
    game.run_neat(genomes, config)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config-feedforward.txt')
    winner_path = os.path.join(local_dir, 'winner.pkl')

    run(config_path, winner_path, nb_runs = 5000)
    # replay_genome(config_path, winner_path)
