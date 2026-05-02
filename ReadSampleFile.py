import re

def read_sample_file(path='sample.txt'):
    sample_spectrum = {}
    with open(path) as f:
        for line in f:
            parts = re.findall(r'\S+', line.strip())
            if len(parts) == 2:
                sample_spectrum[float(parts[0])] = float(parts[1])
    return sample_spectrum
