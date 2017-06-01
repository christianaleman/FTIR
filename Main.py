from LinearFit import *
from Input import *
from ReadSampleFile import read_sample_file
from SumSpectra import*
from DeterminationFitFactor import *
from DrawLines import *

sample_spectrum = read_sample_file()
molecule_spectra = input_molecules()
molecule_concentrations = {}

#DIT MOET AANGEPAST WORDEN !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
for key,value in molecule_spectra.items():
    molecule_concentrations[key] = 2

#Berekenen van de spectra y bij concentratie x
calculated_individual_spectra = Linearfit(molecule_concentrations, molecule_spectra)
#Optellen van alle spectra
sum_all_spectra = SumSpectra(calculated_individual_spectra)
#Bepalen fitfactor
print(fitfactor(sample_spectrum, sum_all_spectra))


#Weergeven data in grafiek pas op het laatst uitvoeren
plot_lines(sum_all_spectra, sample_spectrum)