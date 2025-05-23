from training import TrainingGame, TrainingAI
from quoridor.constants import BLACK, WHITE
import numpy as np
import pygame
import time
from colorama import Fore, Style, init
init(autoreset=True) 

pygame.init()


def generate_random_weights():
    # Range of weights = [0.1, 10]
    return np.random.uniform(low=0.1, high=10, size=4)

def self_play(agent_1_weights, agent_2_weights, num_games=10, timeout_seconds=120):
    #agent 1 = White, agent 2 = Black
    agent_1_wins = agent_2_wins = 0
    # Track the number of games that timed out, usually caused by AI being stuck in a loop, default timeout is 120 seconds
    timeout_games = 0

    for game in range(num_games):
        # Random opponent for each game
        agent_2_weights = generate_random_weights()

        print(f"\nGame: {game} \nAgent 1 weights: {agent_1_weights}\nAgent 2 weights: {agent_2_weights}")

        run = True
        clock = pygame.time.Clock()
        # To visualise the games add pass a pygame window to TrainingGame and uncomment game.update() below
        game = TrainingGame(None, [agent_1_weights, agent_2_weights])
        agent_1 = TrainingAI()
        agent_2 = TrainingAI()

        start_time = time.time()
        
        while run:
            clock.tick(60)

            if time.time() - start_time > timeout_seconds:
                timeout_games += 1
                # If the game times out, we can assume both agents are stuck in a loop
                # Therefore punish the agent we are training by giving the other agent a win
                agent_2_wins += 1
                run = False
                break

            if game.turn == WHITE:
                _, new_board, _ = agent_1.negamax(game.get_board(), 2, float("-inf"), float("inf"), WHITE)
                if new_board is not None:
                    game.ai_move(new_board)
            
            if game.turn == BLACK:
                _, new_board, _ = agent_2.negamax(game.get_board(), 2, float("-inf"), float("inf"), BLACK)
                if new_board is not None:
                    game.ai_move(new_board)
            
            if game.winner() != None:
                if game.winner() == WHITE:
                    agent_1_wins += 1
                else:
                    agent_2_wins += 1
                run = False
                    
            # game.update()
    print(f"Timeout games: {timeout_games}")
    print(f"Agent 1 wins: {agent_1_wins}, Agent 2 wins: {agent_2_wins} \n")
    pygame.quit()
    return agent_1_wins, agent_2_wins


def evaluate_population(population):
    scores = []
    for weights in population:
        # Each agent plays against a random opponent to evaluate their performance
        agent_1_wins, agent_2_wins = self_play(weights, generate_random_weights())
        total_games = agent_1_wins + agent_2_wins
        # Calculate win rate for agent 1 (the one we are training)
        win_rate = agent_1_wins / total_games if total_games > 0 else 0  
        scores.append((win_rate, weights))
    
    # Sort population based on highest win rates
    return sorted(scores, key=lambda x: -x[0])

# Select the top performers based on a retain ratio defaults to selecting top 40% of the population
def select_top_performers(sorted_population, retain_ratio=0.4):
    retain_length = max(2, int(len(sorted_population) * retain_ratio))
    return [weight for _, weight in sorted_population[:retain_length]]

# Mutate weights of the child with a mutation rate of 10%
# Mutations are done by multiplying the weight by a random number between 0.8 and 1.2
def mutate_weights(weights, mutation_rate=0.1):
    if np.random.rand() < mutation_rate:
        idx = np.random.randint(len(weights))
        weights[idx] *= np.random.uniform(0.8, 1.2)
    return weights

# Crossover between two parents to create a child
def crossover(parent1, parent2):
    split = np.random.randint(1, len(parent1))
    child = np.concatenate([parent1[:split], parent2[split:]])
    return mutate_weights(child)


# Generate the next generation of the population by taking selected top performers and creating children
# through crossover and mutation
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
    # Set the initial population size to large to consider various weights 
    initial_population_size = 50
    population = [generate_random_weights() for _ in range(initial_population_size)]

    # Set population size of subsequent generations to lower value and consider only top performers of the initial ones
    population_size = 10
    num_generations = 12

    with open("new.txt", "w") as file: 
        for generation in range(num_generations):
            print(Style.BRIGHT + Fore.RED + "\033[4m" + f"Generation {generation+1}" + "\033[0m")
            file.write(f"Generation {generation+1}\n")

            # Evaluate the population and sort them based on win rates
            sorted_population = evaluate_population(population)
            # Select the top performers based on a retain ratio
            top_performers = select_top_performers(sorted_population)

            best_win_rate = sorted_population[0][0]
            best_weights = sorted_population[0][1]

            print(Fore.GREEN + f"Best win rate: {best_win_rate} with weights {best_weights}")
            print(Fore.GREEN + f"Top performers: {top_performers}")

            file.write(f"Best win rate: {best_win_rate} with weights {best_weights}\n")
            file.write(f"Top performers: {top_performers}\n\n")

            # Generate the next generation of the population
            population = generate_next_generation(top_performers, population_size)

        weight_names = [  
            "Path weight total", 
            "Wall weight", 
            "Blockade weight", 
            "Forward weight"
        ]

        best_weights_to_use = ""
        for i, weight in enumerate(sorted_population[0][1]):
            best_weights_to_use += f"{weight_names[i]}: {weight}, "

        print(Fore.MAGENTA + "-" * 150)
        print(Fore.CYAN + f"\n Final population: {population}\n")
        print(Fore.CYAN + f"Final sorted population: {sorted_population}\n")
        print(Fore.CYAN + f"Best win rate: {best_win_rate} with weights {best_weights}\n")

        print(Fore.CYAN + f"\n Best weights to use: {best_weights_to_use}\n")
        print(Fore.MAGENTA + "-" * 150)

        file.write(F"-" * 150 + "\n")
        file.write(f"\n Final population: {population}\n")
        file.write(f"Final sorted population: {sorted_population}\n")
        file.write(f"Best win rate: {best_win_rate} with weights {best_weights}\n")
        file.write(f"\n Best weights to use: {best_weights_to_use}\n")
        file.write("-" * 150 + "\n")


    
if __name__ == "__main__":
    main() 