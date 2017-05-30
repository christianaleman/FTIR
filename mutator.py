import random
import math
from solution import Solution


# class for handling the mutation of the parameters to optimize
class Mutator:
    def __init__(self, tau):
        self.tau = tau

    # apply the mutation
    def apply_to(self, solution):
        sigma = {
            key: solution.sigma[key] * math.exp(self.tau * random.gauss(0.0, 1.0))
            for key in solution.sigma
        }
        y = {key: max(0, solution.y[key] + random.gauss(0, solution.sigma[key])) for key in solution.y}
        return Solution(sigma, y, None)
