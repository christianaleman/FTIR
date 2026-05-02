import csv
import os
import shutil
import types
from concurrent.futures import ProcessPoolExecutor, as_completed
from datetime import datetime
from multiprocessing import Manager
from threading import Event, Thread

import matplotlib.pyplot as plt
from rich.console import Console
from rich.live import Live
from rich.panel import Panel
from rich.progress import BarColumn, Progress, SpinnerColumn, TextColumn, TimeRemainingColumn
from rich.table import Table

from DrawLines import plot_lines
from Input import configure_ea_params, configure_fit_params, select_molecules, select_sample_files, DONE_DIR
from LinearFit import Linearfit
from ReadSampleFile import read_sample_file
from SumSpectra import SumSpectra
from evolutionStrategy import EvolutionStrategy
from fitnessCalculator import FitnessCalculator

console = Console()
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))


def _run_ea_once(sample_spectrum, molecule_spectra, mu, lambda_, iterations, tau,
                 patience, tolerance, wn_min, wn_max, max_absorption, baseline, weights,
                 label):
    """Run one EA pass. Returns (solution, steps_taken, stopped_early, conc_history, res_history)."""
    es = EvolutionStrategy(mu, lambda_, tau,
                           FitnessCalculator(sample_spectrum, molecule_spectra,
                                             wn_min, wn_max, max_absorption, baseline, weights))
    es.init_population(0.1, molecule_spectra.keys())

    conc_history, res_history = [], []
    best_residual = float('inf')
    steps_no_improve = 0
    stopped_early = False
    prev_print_residual = float('inf')

    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{label}  Step {{task.completed}}/{{task.total}}"),
        BarColumn(bar_width=30),
        TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
        TextColumn("  Residual: [bold red]{task.fields[residual]:.6f}"),
        TimeRemainingColumn(),
        console=console,
        refresh_per_second=10,
    ) as progress:
        task = progress.add_task("ea", total=iterations, residual=float('inf'))

        for step in range(iterations):
            es.mutate()
            es.calculate_fitness()
            es.select()

            best = es.population.solutions[0]
            conc_history.append(dict(best.y))
            res_history.append(best.f_y)
            progress.update(task, advance=1, residual=best.f_y)

            if best_residual - best.f_y > tolerance:
                best_residual = best.f_y
                steps_no_improve = 0
            else:
                steps_no_improve += 1

            if (step + 1) % 5 == 0:
                delta = prev_print_residual - best.f_y
                if prev_print_residual == float('inf'):
                    delta_str = "[dim]─[/dim]"
                elif delta > 1e-9:
                    delta_str = f"[green]▼{delta:.6f}[/green]"
                else:
                    delta_str = f"[yellow]─{abs(delta):.6f}[/yellow]"
                parts = "  ".join(
                    f"[cyan]{mol}[/cyan] [bold]{val:.4f}[/bold]"
                    for mol, val in best.y.items()
                )
                console.print(
                    f"  [dim]Step {step + 1:>4}[/dim]"
                    f"  Res: [bold red]{best.f_y:.6f}[/bold red]"
                    f"  Δ: {delta_str}"
                    f"  {parts}"
                )
                prev_print_residual = best.f_y

            if steps_no_improve >= patience:
                progress.update(task, completed=iterations)
                stopped_early = True
                break

    return es.population.solutions[0], len(res_history), stopped_early, conc_history, res_history


def _run_ea_restart_worker(args):
    """Single EA restart without UI — picklable for ProcessPoolExecutor."""
    (sample_spectrum, molecule_spectra, mu, lambda_, iterations, tau,
     patience, tolerance, wn_min, wn_max, max_absorption, baseline, weights) = args

    es = EvolutionStrategy(mu, lambda_, tau,
                           FitnessCalculator(sample_spectrum, molecule_spectra,
                                             wn_min, wn_max, max_absorption, baseline, weights))
    es.init_population(0.1, molecule_spectra.keys())

    res_history = []
    best_residual = float('inf')
    steps_no_improve = 0

    for step in range(iterations):
        es.mutate()
        es.calculate_fitness()
        es.select()
        best = es.population.solutions[0]
        res_history.append(best.f_y)
        if best_residual - best.f_y > tolerance:
            best_residual = best.f_y
            steps_no_improve = 0
        else:
            steps_no_improve += 1
        if steps_no_improve >= patience:
            break

    sol = es.population.solutions[0]
    return {'y': dict(sol.y), 'f_y': sol.f_y, 'steps': step + 1, 'res_history': res_history}


def _calibration_warnings(concentrations, molecule_spectra):
    warnings = []
    for mol, conc in concentrations.items():
        cal_concs = molecule_spectra[mol][1]
        cal_min = min(c for c in cal_concs if c > 0)
        cal_max = max(cal_concs)
        if conc > cal_max:
            warnings.append(f"  [bold yellow]WARNING:[/bold yellow] {mol} = {conc:.4f} is above calibration max ({cal_max})")
    for w in warnings:
        console.print(w)
    return warnings


def _print_result_table(sample_name, best, steps_taken, molecule_spectra, restart_info=''):
    title = f"[bold green]{sample_name}[/bold green]"
    if restart_info:
        title += f"  [dim]{restart_info}[/dim]"
    table = Table(title=title, border_style="green")
    table.add_column("Molecule", style="cyan", min_width=12)
    table.add_column("Concentration", style="bold green", justify="right", min_width=14)
    table.add_column("Unit", style="dim", min_width=8)
    for mol, conc in best.y.items():
        table.add_row(mol, f"{conc:.4f}", molecule_spectra[mol][2])
    table.add_row("[dim]Residual[/dim]", f"[bold red]{best.f_y:.6f}[/bold red]", "")
    table.add_row("[dim]Steps[/dim]", str(steps_taken), "")
    console.print(table)


def run_sample(sample_path, molecule_spectra, mu, lambda_, iterations, tau,
               patience, tolerance, n_restarts, wn_min, wn_max, max_absorption,
               baseline, weights, sample_index, total_samples, is_last):
    sample_name = os.path.basename(sample_path)
    sample_spectrum = read_sample_file(sample_path)
    console.print(f"[green]OK[/green] {len(sample_spectrum)} points from [italic]{sample_name}[/italic]")

    best_solution, best_steps, best_stopped_early, best_res_hist = None, 0, False, []

    if n_restarts > 1:
        console.print(f"  [cyan]Running {n_restarts} restarts in parallel...[/cyan]")
        worker_args = (sample_spectrum, molecule_spectra, mu, lambda_, iterations, tau,
                       patience, tolerance, wn_min, wn_max, max_absorption, baseline, weights)
        done_count = 0
        with ProcessPoolExecutor() as executor:
            futures = [executor.submit(_run_ea_restart_worker, worker_args)
                       for _ in range(n_restarts)]
            with Progress(
                SpinnerColumn(),
                TextColumn("[bold blue]{task.description}"),
                BarColumn(bar_width=30),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                console=console,
            ) as progress:
                task = progress.add_task(
                    f"[{sample_index}/{total_samples}] 0/{n_restarts} restarts done",
                    total=n_restarts,
                )
                for future in as_completed(futures):
                    r = future.result()
                    done_count += 1
                    if best_solution is None or r['f_y'] < best_solution.f_y:
                        best_solution = types.SimpleNamespace(y=r['y'], f_y=r['f_y'])
                        best_steps = r['steps']
                        best_res_hist = r['res_history']
                    progress.update(
                        task, advance=1,
                        description=f"[{sample_index}/{total_samples}] {done_count}/{n_restarts} restarts done  best: {best_solution.f_y:.6f}",
                    )
        console.print(f"  [cyan]Best residual across {n_restarts} restarts: {best_solution.f_y:.6f}[/cyan]")
    else:
        label = f"[{sample_index}/{total_samples}]"
        solution, steps, stopped_early, conc_hist, res_hist = _run_ea_once(
            sample_spectrum, molecule_spectra, mu, lambda_, iterations, tau,
            patience, tolerance, wn_min, wn_max, max_absorption, baseline, weights,
            label,
        )
        best_solution, best_steps, best_stopped_early, best_res_hist = solution, steps, stopped_early, res_hist
        if best_stopped_early:
            console.print(f"  [yellow]Converged early at step {best_steps}[/yellow]")

    warnings = _calibration_warnings(best_solution.y, molecule_spectra)

    os.makedirs(DONE_DIR, exist_ok=True)
    shutil.move(sample_path, os.path.join(DONE_DIR, sample_name))
    console.print(f"  [dim]Moved to done/{sample_name}[/dim]")

    restart_info = f"best of {n_restarts} restarts" if n_restarts > 1 else ""
    _print_result_table(sample_name, best_solution, best_steps, molecule_spectra, restart_info)

    if is_last:
        calculated_spectra = Linearfit(best_solution.y, molecule_spectra)
        plot_lines(SumSpectra(calculated_spectra), sample_spectrum,
                   title=sample_name, individual_spectra=calculated_spectra,
                   residual_history=best_res_hist)

    return {
        'sample_file': sample_name,
        'concentrations': dict(best_solution.y),
        'residual': best_solution.f_y,
        'steps': best_steps,
        'warnings': len(warnings),
    }


def run_sample_parallel(args):
    (sample_path, molecule_spectra, mu, lambda_, iterations, tau,
     patience, tolerance, n_restarts, wn_min, wn_max, max_absorption, baseline, weights,
     progress_queue) = args
    sample_name = os.path.basename(sample_path)
    sample_spectrum = read_sample_file(sample_path)

    best_solution = None
    best_steps = 0

    for _ in range(n_restarts):
        es = EvolutionStrategy(mu, lambda_, tau,
                               FitnessCalculator(sample_spectrum, molecule_spectra,
                                                 wn_min, wn_max, max_absorption, baseline, weights))
        es.init_population(0.1, molecule_spectra.keys())
        best_residual = float('inf')
        steps_no_improve = 0

        for step in range(iterations):
            es.mutate()
            es.calculate_fitness()
            es.select()
            best = es.population.solutions[0]
            if best_residual - best.f_y > tolerance:
                best_residual = best.f_y
                steps_no_improve = 0
            else:
                steps_no_improve += 1
            if (step + 1) % 5 == 0:
                progress_queue.put((sample_name, step + 1, iterations, best.f_y))
            if steps_no_improve >= patience:
                break

        sol = es.population.solutions[0]
        if best_solution is None or sol.f_y < best_solution.f_y:
            best_solution = sol
            best_steps = step + 1

    progress_queue.put((sample_name, best_steps, iterations, best_solution.f_y))
    return {
        'sample_file': sample_name,
        'sample_path': sample_path,
        'concentrations': dict(best_solution.y),
        'residual': best_solution.f_y,
        'steps': best_steps,
    }


def write_csv(results, molecule_spectra, output_path):
    molecules = list(molecule_spectra.keys())
    units = {mol: molecule_spectra[mol][2] for mol in molecules}
    fieldnames = (['sample_file']
                  + [f"{mol} ({units[mol]})" for mol in molecules]
                  + ['residual', 'steps', 'warnings'])

    with open(output_path, 'w', newline='', encoding='utf-8') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        for r in results:
            row = {'sample_file': r['sample_file']}
            for mol in molecules:
                row[f"{mol} ({units[mol]})"] = f"{r['concentrations'][mol]:.4f}".replace('.', ',')
            row['residual'] = f"{r['residual']:.6f}".replace('.', ',')
            row['steps'] = r['steps']
            row['warnings'] = r.get('warnings', 0)
            writer.writerow(row)


if __name__ == '__main__':
    console.print(Panel.fit(
        "[bold cyan]FTIR Spectrum Fitting[/bold cyan]\n[dim]Evolutionary Strategy Optimizer[/dim]",
        border_style="cyan",
        padding=(1, 4),
    ))

    console.print("\n[bold]Sample Spectrum[/bold]")
    sample_paths = select_sample_files(console)
    if not sample_paths:
        console.print("[red]No sample files found. Add files to sample_data/ and rerun.[/red]")
        raise SystemExit

    console.print("[bold]Molecule Library[/bold]")
    molecule_spectra = select_molecules(console)

    mu, lambda_, iterations, tau, patience, tolerance, n_restarts, parallel = configure_ea_params(
        console, len(molecule_spectra))
    wn_min, wn_max, max_absorption, baseline, weights = configure_fit_params(console, sample_paths[0])

    all_results = []

    if parallel and len(sample_paths) > 1:
        console.print(f"\n[bold]Running {len(sample_paths)} samples in parallel...[/bold]\n")

        mgr = Manager()
        q = mgr.Queue()

        sample_names = [os.path.basename(p) for p in sample_paths]
        # status per sample: (step, total_steps, residual, done)
        status = {name: (0, iterations, float('inf'), False) for name in sample_names}

        def _make_table(n_done):
            t = Table(
                title=f"[bold]Parallel fitting — {n_done}/{len(sample_names)} done[/bold]",
                border_style="cyan",
            )
            t.add_column("Sample",   style="cyan",     min_width=22)
            t.add_column("Step",     justify="right",  min_width=10)
            t.add_column("Residual", justify="right",  min_width=12, style="bold red")
            for name in sample_names:
                step, total, residual, done = status[name]
                if done:
                    continue
                if step == 0:
                    step_str = "[dim]waiting[/dim]"
                else:
                    pct = step / total * 100
                    step_str = f"{step}/{total} ({pct:.0f}%)"
                res_str = f"{residual:.6f}" if residual != float('inf') else "─"
                t.add_row(name, step_str, res_str)
            return t

        stop_drain = Event()

        def _drain():
            while not stop_drain.is_set():
                try:
                    name, step, total, residual = q.get(timeout=0.05)
                    step_, total_, res_, done_ = status[name]
                    status[name] = (step, total, residual, done_)
                except Exception:
                    pass

        drain_thread = Thread(target=_drain, daemon=True)
        drain_thread.start()

        args = [
            (p, molecule_spectra, mu, lambda_, iterations, tau, patience, tolerance,
             n_restarts, wn_min, wn_max, max_absorption, baseline, weights, q)
            for p in sample_paths
        ]
        n_done = 0

        with Live(_make_table(0), refresh_per_second=10, console=console) as live:
            with ProcessPoolExecutor() as executor:
                futures = {executor.submit(run_sample_parallel, a): a[0] for a in args}
                for future in as_completed(futures):
                    result = future.result()
                    n_done += 1
                    name = result['sample_file']
                    status[name] = (result['steps'], iterations, result['residual'], True)
                    live.update(_make_table(n_done))
                    all_results.append(result)

        stop_drain.set()
        drain_thread.join(timeout=1.0)

        all_results.sort(key=lambda r: r['sample_file'])
        last = None
        for r in all_results:
            src = r.get('sample_path', '')
            if os.path.exists(src):
                os.makedirs(DONE_DIR, exist_ok=True)
                shutil.move(src, os.path.join(DONE_DIR, r['sample_file']))
            warnings = _calibration_warnings(r['concentrations'], molecule_spectra)
            r['warnings'] = len(warnings)
            _print_result_table(r['sample_file'], type('S', (), {'y': r['concentrations'], 'f_y': r['residual']})(),
                                r['steps'], molecule_spectra)
            last = r

        if last:
            done_path = os.path.join(DONE_DIR, last['sample_file'])
            spectrum = read_sample_file(done_path)
            calculated_spectra = Linearfit(last['concentrations'], molecule_spectra)
            plt.ioff()
            plot_lines(SumSpectra(calculated_spectra), spectrum,
                       title=last['sample_file'], individual_spectra=calculated_spectra)

    else:
        for i, sample_path in enumerate(sample_paths, 1):
            console.print(f"\n[bold]--- Sample {i}/{len(sample_paths)}: {os.path.basename(sample_path)} ---[/bold]\n")
            result = run_sample(
                sample_path, molecule_spectra,
                mu, lambda_, iterations, tau, patience, tolerance, n_restarts,
                wn_min, wn_max, max_absorption, baseline, weights,
                i, len(sample_paths),
                is_last=(i == len(sample_paths)),
            )
            all_results.append(result)

    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    results_dir = os.path.join(SCRIPT_DIR, 'results')
    os.makedirs(results_dir, exist_ok=True)
    csv_path = os.path.join(results_dir, f'results_{timestamp}.csv')
    write_csv(all_results, molecule_spectra, csv_path)
    console.print(f"\n[bold green]Results saved to:[/bold green] [italic]{csv_path}[/italic]")
    console.print("[dim]Close all plot windows to exit.[/dim]")
    plt.ioff()
    plt.show(block=True)
