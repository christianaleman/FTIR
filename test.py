import math
from evolutionStrategy import EvolutionStrategy


molecules = ['H2O', 'CO2']
es = EvolutionStrategy(10, 100, 1.0 / math.sqrt(2 * len(molecules)))
es.init_population(0.1, molecules)

for x in range(0, 50):
    es.mutate()
    es.calculate_fitness()
    es.select()

print(es.population.solutions[0].f_y)
print(es.population.solutions[0].y)
