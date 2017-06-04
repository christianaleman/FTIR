from multiprocessing.pool import Pool

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
        self.pool = Pool()

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
            self.pool.map_async(
                self.mutator.apply_to,
                [
                    solution
                    for x in range(0, self.lambda_ // self.mu)
                    for solution in self.population.solutions
                ]
            ).get()
        )

    def calculate_fitness(self):
        result = self.pool.map_async(
            self.fitness_calculator.calculate,
            [solution.y for solution in self.population.solutions]
        ).get()
        for (f_y, solution) in zip(result, self.population.solutions):
            solution.f_y = f_y

    def select(self):
        self.population.solutions.sort(key=attrgetter('f_y'))
        self.population.solutions = self.population.solutions[:self.mu]
