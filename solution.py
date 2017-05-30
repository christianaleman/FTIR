# class representing a single solution
class Solution:
    # mutation strengths
    sigma = {}

    # solution representation
    y = {}

    # fitness F(y)
    f_y = {}

    def __init__(self, sigma, y, f_y):
        self.sigma = sigma
        self.y = y
        self.Fy = f_y
