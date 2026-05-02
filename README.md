# FTIR Spectrum Fitting

Identifies gas concentrations in a mixed FTIR spectrum by fitting a combination of reference spectra using an evolutionary strategy (ES) optimiser.

## How it works

The algorithm searches for the concentration of each molecule that minimises the residual between the measured sample spectrum and the sum of the scaled reference spectra. It uses a (μ, λ) evolution strategy with self-adaptive mutation step sizes.

Fitness evaluation is fully vectorised with NumPy: all λ offspring in a generation are evaluated simultaneously using pre-built calibration matrices, making the optimisation significantly faster than a pure-Python loop.

## Project structure

```
FTIR-master/
├── Main.py                    # Entry point
├── Input.py                   # Terminal UI: file/molecule/parameter selection
├── evolutionStrategy.py       # (μ, λ) evolution strategy loop
├── fitnessCalculator.py       # Vectorised residual calculation (NumPy)
├── mutator.py                 # Mutation operator
├── population.py              # Population container
├── solution.py                # Single solution (concentrations + sigma)
├── LinearFit.py               # Interpolates reference spectrum at a given concentration
├── SumSpectra.py              # Sums individual spectra into one
├── DeterminationFitFactor.py  # Computes residual between sample and fit
├── ReadSampleFile.py          # Reads a two-column sample spectrum file
├── Moleculeclass.py           # Loads a molecule calibration file
├── DrawLines.py               # Final spectral fit plot (4 subplots)
├── create_test_molecules.py   # Utility: generates synthetic molecule calibration files
├── generate_test_samples.py   # Utility: generates synthetic sample files
│
├── molecules/                 # Reference spectra (one subfolder per molecule)
│   └── <Name>/<Name>.txt
│
├── molecule_lists.json        # Saved molecule selections (created on first save)
├── sample_data/               # Drop sample files here before running
├── done/                      # Processed sample files are moved here automatically
└── results/                   # CSV output files saved here
```

## Adding a new molecule

Create a folder `molecules/<Name>/` and add a calibration file `<Name>.txt` in the following format:

```
<Name>
Golfgetal [cm-1]	<unit>          (unit is ppm or vol%)
cm-1	0 <c1> <c2> ... <cn>        (concentrations used in calibration)
<wavenumber>	<abs@c0> <abs@c1> ... <abs@cn>
...
```

The tool auto-detects any molecule folder matching this format.

## Running

1. Place one or more sample `.txt` files in `sample_data/`
2. Run:
   ```
   python Main.py
   ```
3. Follow the prompts:
   - Select which sample files to process (single or batch)
   - Select which molecules to fit (all, a saved list, or a custom selection)
   - Set EA parameters (or press Enter to accept defaults)
4. Results are saved to `results/results_<timestamp>.csv` and processed files are moved to `done/`

## EA parameters

| Parameter | Default | Description |
|-----------|---------|-------------|
| μ (mu) | 10 | Number of best solutions kept per generation |
| λ (lambda) | 100 | Offspring generated per generation |
| Max iterations | 250 | Hard upper limit on generations |
| τ (tau) | 1/√(2n) | Controls how fast mutation strength adapts |
| Early stop patience | 15 | Stops if residual doesn't improve for this many steps |
| Early stop tolerance | 1e-6 | Minimum improvement to count as progress |
| Restarts | 1 | Independent runs per sample; the best result is kept |
| Parallel batch | no | Run multiple sample files simultaneously |

### Choosing max iterations

Because early stopping terminates the run as soon as the residual stops improving, max iterations is effectively a safety cap rather than the actual run length. A good rule of thumb is **~10× the number of molecules** (e.g. 100 for 10 molecules, 200 for 20). Use the residual-per-step graph in the final plot to check whether convergence happened well before the cap — if it consistently does, you can lower the value.

## Terminal progress

During a run, concentrations and residual are printed to the terminal every 5 steps:

```
  Step    5  Res: 0.043821  Δ: ▼0.012345  H2O 0.1234  CO2 0.5678
  Step   10  Res: 0.031456  Δ: ▼0.003211  H2O 0.1456  CO2 0.5432
  Step   15  Res: 0.031200  Δ: ─0.000000  H2O 0.1460  CO2 0.5430
```

- **Δ ▼** (green) — residual is still dropping; the algorithm is making progress
- **Δ ─** (yellow) — residual has flattened; early stopping will trigger soon

## Final plot

After the last sample is processed a four-panel matplotlib window opens:

| Panel | Contents |
|-------|----------|
| Sample | Measured spectrum (red scatter) |
| Fitted Spectrum | Individual molecule contributions + total fit |
| Residue | Point-by-point difference between sample and fit |
| Residual per Step | Convergence curve (red) with 5-step rolling Δ (blue dashed) |

## Parallel modes

### Parallel restarts (single file)
Setting **Restarts > 1** runs all restarts for a single sample simultaneously using multiple CPU cores. A progress bar tracks how many restarts have completed and shows the best residual found so far. The step-by-step terminal output is suppressed in this mode.

### Parallel batch (multiple files)
Setting **Parallel batch = yes** processes all selected sample files at the same time. A live table shows each sample's current step, progress percentage, and best residual, updated continuously while the workers run.

## Output

Results are written to `results/results_<timestamp>.csv` using **semicolon (`;`) as column separator** and **comma (`,`) as decimal separator** — the European format that Excel reads correctly without import configuration.

Columns: `sample_file`, one column per molecule with its unit, `residual`, `steps`, `warnings`.

## Generating test samples

```
python generate_test_samples.py
```

Creates synthetic sample files in `sample_data/` with known concentrations so you can verify the algorithm recovers the correct values.

## Dependencies

```
pip install matplotlib rich numpy
```
