from mutator import Mutator
from population import Population
from solution import Solution
from operator import attrgetter


class EvolutionStrategy:
    def __init__(self, mu, lambda_, tau, fitness_calculator):
        self.mu = mu
        self.lambda_ = lambda_
        self.tau = tau
        self.population = None
        self.mutator = Mutator(tau)
        self.fitness_calculator = fitness_calculator

    def init_population(self, sigma, molecules):
        self.population = Population([
            Solution(
                {key: sigma for key in molecules},
                {key: 0 for key in molecules},
                None,
            ) for _ in range(self.mu)
        ])

    def mutate(self):
        offspring = [
            self.mutator.apply_to(solution)
            for _ in range(self.lambda_ // self.mu)
            for solution in self.population.solutions
        ]
        self.population = Population(offspring)

    def calculate_fitness(self):
        residuals = self.fitness_calculator.calculate_batch(self.population.solutions)
        for sol, res in zip(self.population.solutions, residuals):
            sol.f_y = res

    def select(self):
        self.population.solutions.sort(key=attrgetter('f_y'))
        self.population.solutions = self.population.solutions[:self.mu]
