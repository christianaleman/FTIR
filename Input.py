import os
import json
import math

from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, IntPrompt, FloatPrompt, Confirm

from Moleculeclass import Molecule

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
MOLECULE_LISTS_FILE = os.path.join(SCRIPT_DIR, 'molecule_lists.json')


SAMPLE_DIR = os.path.join(SCRIPT_DIR, 'sample_data')
DONE_DIR = os.path.join(SCRIPT_DIR, 'done')


def detect_sample_files():
    os.makedirs(SAMPLE_DIR, exist_ok=True)
    samples = []
    for fname in sorted(os.listdir(SAMPLE_DIR)):
        if not fname.endswith('.txt'):
            continue
        fpath = os.path.join(SAMPLE_DIR, fname)
        try:
            with open(fpath) as f:
                first_line = f.readline().strip()
            parts = first_line.split()
            if len(parts) == 2:
                float(parts[0])
                float(parts[1])
                samples.append(fpath)
        except (ValueError, Exception):
            continue
    return samples


def select_sample_files(console):
    samples = detect_sample_files()

    if not samples:
        console.print(f"[yellow]No sample files found in sample_data/[/yellow]")
        return []

    table = Table(title="Available Sample Files", border_style="cyan")
    table.add_column("#", style="dim", width=4)
    table.add_column("File", style="cyan")
    for i, fpath in enumerate(samples, 1):
        table.add_row(str(i), os.path.basename(fpath))
    console.print(table)

    if len(samples) == 1:
        console.print(f"[green]Using:[/green] {os.path.basename(samples[0])}\n")
        return [samples[0]]

    console.print("  [cyan]A[/cyan] - All files (batch)")
    console.print("  [green]S[/green] - Select specific files (comma-separated numbers)")
    mode = Prompt.ask("Choice", choices=["A", "S"], default="S").upper()

    if mode == "A":
        selected = samples
    else:
        indices_str = Prompt.ask(f"File numbers (1-{len(samples)})")
        selected = [samples[int(i.strip()) - 1] for i in indices_str.split(',')]

    names = ', '.join(os.path.basename(p) for p in selected)
    console.print(f"[green]Selected {len(selected)} file(s):[/green] {names}\n")
    return selected


def detect_molecule_files():
    molecules_dir = os.path.join(SCRIPT_DIR, 'molecules')
    molecules = []
    if not os.path.isdir(molecules_dir):
        return molecules
    for mol_name in sorted(os.listdir(molecules_dir)):
        mol_path = os.path.join(molecules_dir, mol_name, mol_name + '.txt')
        if not os.path.isfile(mol_path):
            continue
        try:
            with open(mol_path) as f:
                line1 = f.readline().strip()
                f.readline()
                line3 = f.readline().strip()
            if line1 and line1[0].isalpha() and line3.startswith('cm-1'):
                molecules.append(mol_name)
        except Exception:
            continue
    return molecules


def load_molecule_lists():
    if os.path.exists(MOLECULE_LISTS_FILE):
        with open(MOLECULE_LISTS_FILE) as f:
            return json.load(f)
    return {}


def save_molecule_list(name, molecules):
    lists = load_molecule_lists()
    lists[name] = molecules
    with open(MOLECULE_LISTS_FILE, 'w') as f:
        json.dump(lists, f, indent=2)


def select_molecules(console):
    available = detect_molecule_files()
    saved_lists = load_molecule_lists()

    mol_table = Table(title="Available Molecules", border_style="cyan")
    mol_table.add_column("#", style="dim", width=4)
    mol_table.add_column("Molecule", style="cyan")
    for i, m in enumerate(available, 1):
        mol_table.add_row(str(i), m)
    console.print(mol_table)

    if saved_lists:
        lists_table = Table(title="Saved Lists", border_style="yellow")
        lists_table.add_column("#", style="dim", width=4)
        lists_table.add_column("Name", style="yellow")
        lists_table.add_column("Molecules", style="cyan")
        for i, (name, mols) in enumerate(saved_lists.items(), 1):
            lists_table.add_row(str(i), name, ", ".join(mols))
        console.print(lists_table)

    choices = ["A", "C"]
    console.print("\n[bold]Select molecules:[/bold]")
    console.print("  [cyan]A[/cyan] - Use all available (default)")
    if saved_lists:
        console.print("  [yellow]L[/yellow] - Load a saved list")
        choices.append("L")
    console.print("  [green]C[/green] - Custom selection")

    choice = Prompt.ask("Choice", choices=choices, default="A").upper()

    if choice == "A":
        selected = available
    elif choice == "L":
        list_names = list(saved_lists.keys())
        name = Prompt.ask("List name", choices=list_names)
        selected = saved_lists[name]
    else:
        indices_str = Prompt.ask(f"Molecule numbers (comma-separated, 1-{len(available)})")
        selected = [available[int(i.strip()) - 1] for i in indices_str.split(',')]
        if Confirm.ask("Save this selection for future use?"):
            name = Prompt.ask("List name")
            save_molecule_list(name, selected)
            console.print(f"[green]OK Saved list '[bold]{name}[/bold]'[/green]")

    console.print(f"\n[green]Using:[/green] {', '.join(selected)}\n")

    spectra = {}
    for mol_name in selected:
        spectra[mol_name] = Molecule(mol_name).determine_spectrum()
        console.print(f"  [green]OK[/green] Loaded [cyan]{mol_name}[/cyan]")

    return spectra


def configure_fit_params(console, sample_path):
    from ReadSampleFile import read_sample_file
    wns = sorted(read_sample_file(sample_path).keys())
    default_min = wns[0]
    default_max = wns[-1]

    console.print(Panel(
        "[bold]Fit Options[/bold]\n[dim]Press Enter to accept defaults[/dim]",
        border_style="magenta",
    ))

    wn_min = FloatPrompt.ask("  Wavenumber range min", default=round(default_min, 2))
    wn_max = FloatPrompt.ask("  Wavenumber range max", default=round(default_max, 2))

    use_max_abs = Confirm.ask("  Limit by maximum absorption?", default=False)
    max_absorption = None
    if use_max_abs:
        max_absorption = FloatPrompt.ask("  Maximum absorption value")

    console.print("  Baseline correction:")
    console.print("    [cyan]N[/cyan] - None (default)")
    console.print("    [cyan]O[/cyan] - Offset (subtract constant drift)")
    console.print("    [cyan]L[/cyan] - Linear (subtract offset + slope)")
    baseline_choice = Prompt.ask("  Choice", choices=["N", "O", "L"], default="N").upper()
    baseline = {'N': None, 'O': 'offset', 'L': 'linear'}[baseline_choice]

    weights = None
    if Confirm.ask("  Add wavenumber region weights?", default=False):
        weights = []
        console.print("  Enter: wn_min wn_max weight  (empty line to finish)")
        while True:
            entry = Prompt.ask("  Region", default="")
            if not entry.strip():
                break
            parts = entry.split()
            if len(parts) == 3:
                try:
                    lo, hi, w = float(parts[0]), float(parts[1]), float(parts[2])
                    weights.append((lo, hi, w))
                    console.print(f"    Added: {lo:.1f}-{hi:.1f} x{w}")
                except ValueError:
                    console.print("  [red]Use format: wn_min wn_max weight[/red]")
        if not weights:
            weights = None

    table = Table(title="Fit Options", border_style="magenta")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="bold green", justify="right")
    table.add_row("Wavenumber min", f"{wn_min:.2f}")
    table.add_row("Wavenumber max", f"{wn_max:.2f}")
    table.add_row("Max absorption", str(max_absorption) if max_absorption is not None else "none")
    table.add_row("Baseline", baseline or "none")
    if weights:
        for lo, hi, w in weights:
            table.add_row(f"Weight {lo:.0f}-{hi:.0f}", f"x{w}")
    else:
        table.add_row("Weights", "uniform")
    console.print(table)

    return wn_min, wn_max, max_absorption, baseline, weights


def configure_ea_params(console, n_molecules):
    console.print(Panel(
        "[bold]Evolutionary Algorithm Parameters[/bold]\n[dim]Press Enter to accept defaults[/dim]",
        border_style="blue",
    ))

    default_tau = round(1.0 / math.sqrt(2 * n_molecules), 4)

    mu = IntPrompt.ask("  Population size (mu)", default=10)
    lambda_ = IntPrompt.ask("  Offspring per generation (lambda)", default=100)
    iterations = IntPrompt.ask("  Max iterations", default=250)
    tau = FloatPrompt.ask("  Mutation step size (tau)", default=default_tau)
    patience = IntPrompt.ask("  Early stop patience (steps without improvement)", default=15)
    tolerance = FloatPrompt.ask("  Early stop tolerance (min residual improvement)", default=1e-6)
    n_restarts = IntPrompt.ask("  Restarts per sample (keep best)", default=1)
    parallel = Confirm.ask("  Run batch in parallel (disables live plot)", default=False)

    table = Table(title="Configuration", border_style="blue")
    table.add_column("Parameter", style="cyan")
    table.add_column("Value", style="bold green", justify="right")
    table.add_row("Population size (mu)", str(mu))
    table.add_row("Offspring (lambda)", str(lambda_))
    table.add_row("Max iterations", str(iterations))
    table.add_row("Tau", str(tau))
    table.add_row("Early stop patience", str(patience))
    table.add_row("Early stop tolerance", str(tolerance))
    table.add_row("Restarts", str(n_restarts))
    table.add_row("Parallel batch", "yes" if parallel else "no")
    console.print(table)

    return mu, lambda_, iterations, tau, patience, tolerance, n_restarts, parallel
