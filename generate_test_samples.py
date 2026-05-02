"""
Generates random synthetic FTIR sample files from the molecules in the molecules/ folder.
Each sample is a random mixture of randomly selected molecules at random concentrations
within their calibration range.

Usage:
    python generate_test_samples.py [n_samples]

    n_samples: number of sample files to generate (default: 10)
"""
import os
import re
import sys
import bisect
import random

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOLECULES_DIR = os.path.join(SCRIPT_DIR, 'molecules')
OUTPUT_DIR = os.path.join(SCRIPT_DIR, 'sample_data')


def load_molecule(name):
    path = os.path.join(MOLECULES_DIR, name, name + '.txt')
    with open(path) as f:
        lines = f.readlines()

    unit_parts = lines[1].strip().split('\t')
    unit = unit_parts[-1].strip() if len(unit_parts) >= 2 else 'ppm'

    concentrations = [float(x) for x in re.findall(r'\S+', lines[2].strip())[1:]]

    spectrum = {}
    for line in lines[3:]:
        parts = re.findall(r'\S+', line.strip())
        if len(parts) < 2:
            continue
        spectrum[parts[0]] = [float(x) for x in parts[1:]]

    return spectrum, concentrations, unit


def interpolate(spectrum, concentrations, value):
    i = bisect.bisect(concentrations, value)
    if i == 0:
        lo, hi = 0, min(1, len(concentrations) - 1)
    elif i >= len(concentrations):
        lo, hi = len(concentrations) - 2, len(concentrations) - 1
    else:
        lo, hi = i - 1, i

    result = {}
    for wn, absorptions in spectrum.items():
        if concentrations[hi] == concentrations[lo]:
            result[wn] = absorptions[lo]
        else:
            slope = (absorptions[hi] - absorptions[lo]) / (concentrations[hi] - concentrations[lo])
            result[wn] = absorptions[lo] + slope * (value - concentrations[lo])
    return result


def detect_molecules():
    names = []
    for name in sorted(os.listdir(MOLECULES_DIR)):
        path = os.path.join(MOLECULES_DIR, name, name + '.txt')
        if os.path.isfile(path):
            names.append(name)
    return names


def random_concentration(concentrations):
    lo = min(c for c in concentrations if c > 0)
    hi = max(concentrations)
    return round(random.uniform(lo, hi), 4)


def make_sample(molecule_concentrations, noise_std=0.0):
    combined = {}
    for name, conc in molecule_concentrations.items():
        spectrum, concentrations, _ = load_molecule(name)
        interp = interpolate(spectrum, concentrations, conc)
        for wn, val in interp.items():
            combined[wn] = combined.get(wn, 0.0) + val

    if noise_std > 0:
        for wn in combined:
            combined[wn] += random.gauss(0, noise_std)

    return combined


def write_sample(filename, spectrum):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    path = os.path.join(OUTPUT_DIR, filename)
    with open(path, 'w') as f:
        for wn in sorted(spectrum.keys(), key=float):
            f.write(f" {wn}\t{spectrum[wn]:.6f}\n")
    return path


def generate(n_samples, max_molecules=5):
    all_molecules = detect_molecules()
    if not all_molecules:
        print("No molecules found in molecules/ folder.")
        return

    print(f"Found molecules: {', '.join(all_molecules)}")
    print(f"Generating {n_samples} random sample files...\n")

    # Load concentration ranges
    ranges = {}
    for name in all_molecules:
        _, concentrations, unit = load_molecule(name)
        ranges[name] = (concentrations, unit)

    for i in range(1, n_samples + 1):
        # Pick a random subset of the requested size
        n_pick = min(max_molecules, len(all_molecules))
        n_mols = random.randint(1, n_pick)
        chosen = random.sample(all_molecules, n_mols)

        concentrations = {}
        label_parts = []
        for name in chosen:
            conc_list, unit = ranges[name]
            conc = random_concentration(conc_list)
            concentrations[name] = conc
            label_parts.append(f"{name}={conc}{unit}")

        # Small chance of adding noise
        noise = random.choice([0.0, 0.0, 0.0, 0.0005])

        spectrum = make_sample(concentrations, noise_std=noise)

        conc_tag = '_'.join(
            f"{name}={round(conc, 1)}{ranges[name][1].replace('%', 'pct')}"
            for name, conc in concentrations.items()
        )
        noise_tag = "_noisy" if noise > 0 else ""
        base = f"random_{i:03d}_{conc_tag}{noise_tag}"
        # Windows MAX_PATH is 260; keep filename under 200 chars
        if len(base) > 195:
            base = base[:195]
        filename = base + ".txt"
        path = write_sample(filename, spectrum)

        noise_info = " + noise" if noise > 0 else ""
        print(f"  [{i:>{len(str(n_samples))}}] {filename}  -  {', '.join(label_parts)}{noise_info}")

    print(f"\nDone. {n_samples} files written to sample_data/")


if __name__ == '__main__':
    n = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    max_mols = int(sys.argv[2]) if len(sys.argv) > 2 else 5
    generate(n, max_mols)
