from training import TrainingGame, TrainingAI
from quoridor.constants import BLACK, WHITE, WIDTH, HEIGHT
import numpy as np
import pygame
import time


def generate_random_weights():
    return np.random.uniform(low=0.1, high=10, size=6)

def self_play(agent_1_weights, agent_2_weights, num_games=10, timeout_seconds=120):
    #agent 1 = White, agent 2 = Black
    agent_1_wins = agent_2_wins = 0
    timeout_games = 0

    for _ in range(num_games):
        run = True
        clock = pygame.time.Clock()
        game = TrainingGame(pygame.display.set_mode((WIDTH, HEIGHT)), [agent_1_weights, agent_2_weights])
        agent_1 = TrainingAI()
        agent_2 = TrainingAI()

        start_time = time.time()

        while run:
            clock.tick(60)

            if time.time() - start_time > timeout_seconds:
                timeout_games += 1
                agent_2_wins += 1
                run = False
                break

            if game.turn == WHITE:
                _, new_board = agent_1.negamax(game.get_board(), 1, float("-inf"), float("inf"), WHITE)
                if new_board is not None:
                    game.ai_move(new_board)
            
            if game.turn == BLACK:
                _, new_board = agent_2.negamax(game.get_board(), 1, float("-inf"), float("inf"), BLACK)
                if new_board is not None:
                    game.ai_move(new_board)
            
            if game.winner() != None:
                if game.winner() == WHITE:
                    agent_1_wins += 1
                else:
                    agent_2_wins += 1
                run = False
                    
            game.update()
    print(f"Timeout games: {timeout_games}")
    print(f"Agent 1 wins: {agent_1_wins}, Agent 2 wins: {agent_2_wins}")
    pygame.quit()
    return agent_1_wins, agent_2_wins


def evaluate_population(population):
    scores = []
    for weights in population:
        agent_1_wins, agent_2_wins = self_play(weights, generate_random_weights(), num_games=1)
        total_games = agent_1_wins + agent_2_wins
        win_rate = agent_1_wins / total_games if total_games > 0 else 0  
        scores.append((win_rate, weights))
    return sorted(scores, key=lambda x: -x[0])

def select_top_performers(sorted_population, retain_ratio=0.4):
    retain_length = max(2, int(len(sorted_population) * retain_ratio))
    return [weight for _, weight in sorted_population[:retain_length]]

def mutate_weights(weights, mutation_rate=0.1):
    if np.random.rand() < mutation_rate:
        idx = np.random.randint(len(weights))
        weights[idx] *= np.random.uniform(0.8, 1.2)
    return weights

def crossover(parent1, parent2):
    split = np.random.randint(1, len(parent1))
    child = np.concatenate([parent1[:split], parent2[split:]])
    return mutate_weights(child)

def generate_next_generation(selected_population, population_size):
    next_population = selected_population.copy()

    while len(next_population) < population_size:
        parent1, parent2 = np.random.choice(range(len(selected_population)), size=2, replace=False)
        parent1 = selected_population[parent1]
        parent2 = selected_population[parent2]
        child = crossover(parent1, parent2)
        next_population.append(child)
    return next_population


def main():
    population_size = 2
    population = [generate_random_weights() for _ in range(population_size)]

    num_generations = 2

    for generation in range(num_generations):
        print(f"Generation {generation+1}")
        
        sorted_population = evaluate_population(population)
        top_performers = select_top_performers(sorted_population)

        print(f"Best win rate: {sorted_population[0][0]} with weights {sorted_population[0][1]}")
        print(f"Top performers: {top_performers}")
        
        population = generate_next_generation(top_performers, population_size)

    print("-" * 20)
    print(f"\n Final population: {population}\n")
    print(f"Final sorted population: {sorted_population}\n")
    print(f"Best win rate: {sorted_population[0][0]} with weights {sorted_population[0][1]}\n")
    print(f"\n Best weights to use: {sorted_population[0][1]}\n")
    print("-" * 20)

    
if __name__ == "__main__":
    main() 