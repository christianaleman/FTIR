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
        self.population = Population(
            [
                Solution(
                    {key: sigma for key in molecules},
                    {key: 0 for key in molecules},
                    None
                ) for x in range(0, self.mu)
            ]
        )

    def mutate(self):
        self.population = Population(
            [
                self.mutator.apply_to(solution)
                for x in range(0, self.lambda_ // self.mu)
                for solution in self.population.solutions
            ]
        )

    def calculate_fitness(self):
        for solution in self.population.solutions:
            solution.f_y = self.fitness_calculator.calculate(solution.y)
            # sum([abs(10 - solution.y[key]) for key in solution.y])

    def select(self):
        self.population.solutions.sort(key=attrgetter('f_y'))
        self.population.solutions = self.population.solutions[:self.mu]
