from SumSpectra import *
from DeterminationFitFactor import fitfactor
from LinearFit import Linearfit


class FitnessCalculator:
    def __init__(self, sample_spectrum, molecule_spectra):
        self.sample_spectrum = sample_spectrum
        self.molecule_spectra = molecule_spectra

    def calculate(self, molecule_concentrations):
        # Berekenen van de spectra y bij concentratie x
        calculated_individual_spectra = Linearfit(molecule_concentrations, self.molecule_spectra)
        # Optellen van alle spectra
        sum_all_spectra = SumSpectra(calculated_individual_spectra)
        # Bepalen fitfactor
        return fitfactor(self.sample_spectrum, sum_all_spectra)
