"""
Generate 20 synthetic molecule calibration files for FTIR testing.
Spectra are physically motivated Gaussians scaled linearly with concentration.
"""
import os
import math
import random

random.seed(42)

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Wavenumber grid matching existing molecules (CO.txt)
WN_START = 594.44
WN_STEP = 7.72
WN_COUNT = 480

WAVENUMBERS = [WN_START + i * WN_STEP for i in range(WN_COUNT)]
NOISE = 3e-4  # baseline noise std


def gaussian(wn, center, fwhm, height):
    return height * math.exp(-4 * math.log(2) * ((wn - center) / fwhm) ** 2)


def make_absorption(wn_list, peaks, concentration, rng_seed):
    rng = random.Random(rng_seed)
    result = []
    for wn in wn_list:
        val = concentration * sum(gaussian(wn, c, w, h) for c, w, h in peaks)
        val += rng.gauss(0, NOISE)
        result.append(val)
    return result


# Each molecule: name, unit, calibration concentrations (must include 0),
# peaks as list of (center_wn, fwhm_wn, absorption_per_unit_conc)
MOLECULES = [
    {
        'name': 'Methane',
        'unit': 'ppm',
        'concs': [0, 100, 500, 1000, 2000],
        'peaks': [(3017, 60, 2.0e-4), (1306, 45, 1.5e-4)],
    },
    {
        'name': 'Propane',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(2968, 80, 1.8e-4), (1472, 30, 9e-5), (1378, 20, 7e-5)],
    },
    {
        'name': 'Butane',
        'unit': 'ppm',
        'concs': [0, 50, 100, 300, 500],
        'peaks': [(2962, 85, 2.2e-4), (1380, 25, 1.1e-4), (725, 18, 6e-5)],
    },
    {
        'name': 'Acetylene',
        'unit': 'ppm',
        'concs': [0, 50, 100, 250, 500],
        'peaks': [(3305, 18, 6e-4), (730, 28, 8e-4)],
    },
    {
        'name': 'Acetaldehyde',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(2723, 32, 1.4e-4), (1743, 22, 3.5e-4), (1113, 35, 8e-5)],
    },
    {
        'name': 'Formaldehyde',
        'unit': 'ppm',
        'concs': [0, 50, 100, 300, 500],
        'peaks': [(2779, 28, 2.8e-4), (1746, 18, 4.5e-4), (2843, 22, 1.5e-4)],
    },
    {
        'name': 'Methanol',
        'unit': 'ppm',
        'concs': [0, 200, 500, 1000, 2000],
        'peaks': [(3330, 110, 4e-5), (1033, 32, 3.5e-4), (2844, 40, 9e-5)],
    },
    {
        'name': 'Ethanol',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(3355, 130, 3e-5), (1052, 38, 2.8e-4), (2977, 55, 1.2e-4)],
    },
    {
        'name': 'HCl',
        'unit': 'ppm',
        'concs': [0, 20, 50, 100, 200],
        'peaks': [(2886, 35, 8e-4), (2926, 30, 6e-4)],
    },
    {
        'name': 'HF',
        'unit': 'ppm',
        'concs': [0, 10, 25, 50, 100],
        'peaks': [(3961, 40, 1.2e-3)],
    },
    {
        'name': 'NO',
        'unit': 'ppm',
        'concs': [0, 50, 100, 250, 500],
        'peaks': [(1876, 22, 5e-4), (1904, 18, 4e-4)],
    },
    {
        'name': 'NO2',
        'unit': 'ppm',
        'concs': [0, 50, 100, 200, 400],
        'peaks': [(1630, 45, 4e-4), (750, 35, 3e-4)],
    },
    {
        'name': 'SO2',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(1361, 32, 5e-4), (1151, 28, 4e-4)],
    },
    {
        'name': 'N2O',
        'unit': 'ppm',
        'concs': [0, 100, 500, 1000, 2000],
        'peaks': [(2224, 28, 5e-4), (1285, 22, 3.5e-4)],
    },
    {
        'name': 'HCN',
        'unit': 'ppm',
        'concs': [0, 50, 100, 250, 500],
        'peaks': [(714, 28, 1.2e-3), (3311, 18, 3.5e-4)],
    },
    {
        'name': 'Propylene',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(3091, 32, 4e-5), (990, 28, 7e-4), (912, 22, 4e-4)],
    },
    {
        'name': 'Toluene',
        'unit': 'ppm',
        'concs': [0, 20, 50, 100, 200],
        'peaks': [(3030, 38, 1.2e-4), (728, 22, 1.5e-3), (1083, 25, 6e-5)],
    },
    {
        'name': 'Benzene',
        'unit': 'ppm',
        'concs': [0, 10, 25, 50, 100],
        'peaks': [(3068, 32, 1.0e-4), (675, 22, 2.0e-3), (1479, 20, 5e-5)],
    },
    {
        'name': 'Acetone',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(1740, 32, 5e-4), (1220, 28, 2.5e-4), (2938, 45, 1e-4)],
    },
    {
        'name': 'Dimethylether',
        'unit': 'ppm',
        'concs': [0, 100, 300, 500, 1000],
        'peaks': [(2820, 50, 1.5e-4), (1170, 38, 6e-4), (928, 25, 4e-4)],
    },
]


def write_molecule(mol):
    name = mol['name']
    unit = mol['unit']
    concs = mol['concs']
    peaks = mol['peaks']

    mol_dir = os.path.join(SCRIPT_DIR, 'molecules', name)
    os.makedirs(mol_dir, exist_ok=True)
    out_path = os.path.join(mol_dir, name + '.txt')

    conc_header = '\t'.join(str(c) for c in concs)

    with open(out_path, 'w') as f:
        f.write(f"{name}\n")
        f.write(f"Golfgetal [cm-1]\t{unit}\n")
        f.write(f"cm-1\t{conc_header}\n")

        for seed, wn in enumerate(WAVENUMBERS):
            row_vals = []
            for ci, conc in enumerate(concs):
                rng_seed = seed * 1000 + ci
                absorptions = make_absorption([wn], peaks, conc, rng_seed)
                row_vals.append(absorptions[0])

            vals_str = '\t'.join(f"{v:.6f}" for v in row_vals)
            f.write(f"{wn:8.2f}\t{vals_str}\n")

    print(f"  Created: molecules/{name}/{name}.txt  ({len(concs)} concentrations, {len(peaks)} peak(s))")


if __name__ == '__main__':
    print(f"Generating {len(MOLECULES)} synthetic molecules...\n")
    for mol in MOLECULES:
        write_molecule(mol)
    print(f"\nDone. {len(MOLECULES)} molecule files written to molecules/")
