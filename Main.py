import math
from LinearFit import *
from Input import *
from ReadSampleFile import read_sample_file
from SumSpectra import *
from DeterminationFitFactor import *
from DrawLines import *
from evolutionStrategy import EvolutionStrategy
from fitnessCalculator import FitnessCalculator

sample_spectrum = read_sample_file()
molecule_spectra = input_molecules()
molecule_concentrations = {}

molecules = ['H2O', 'CO2']
es = EvolutionStrategy(10, 100, 1.0 / math.sqrt(2 * len(molecule_spectra)), FitnessCalculator(sample_spectrum, molecule_spectra))
es.init_population(0.1, molecule_spectra.keys())

for x in range(0, 50):
    es.mutate()
    es.calculate_fitness()
    es.select()

print(es.population.solutions[0].f_y)
print(es.population.solutions[0].y)

#Berekenen van de spectra y bij concentratie x
calculated_individual_spectra = Linearfit(es.population.solutions[0].y, molecule_spectra)
#Optellen van alle spectra
sum_all_spectra = SumSpectra(calculated_individual_spectra)
#Bepalen fitfactor
# print(fitfactor(sample_spectrum, sum_all_spectra))


#Weergeven data in grafiek pas op het laatst uitvoeren
plot_lines(sum_all_spectra, sample_spectrum)