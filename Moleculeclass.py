import re
import os

class Molecule:
    def __init__(self, name):
        self.name = name

    def determine_spectrum(self):
        path = os.path.join('molecules', self.name, self.name + '.txt')
        with open(path) as f:
            lines = f.readlines()

        unit_parts = lines[1].strip().split('\t')
        unit = unit_parts[-1].strip() if len(unit_parts) >= 2 else 'ppm'

        header = re.findall(r'\S+', lines[2].strip())
        n_cols = len(header)
        concentrations = [float(x) for x in header[1:]]

        spectrum = {}
        for line in lines[3:]:
            parts = re.findall(r'\S+', line.strip())
            if len(parts) < 2:
                continue
            wavenumber = float(parts[0])
            absorptions = [float(x) for x in parts[1:n_cols]]
            spectrum[wavenumber] = absorptions

        return (spectrum, concentrations, unit)
