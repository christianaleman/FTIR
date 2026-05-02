import math
import matplotlib.pyplot as plt
from matplotlib.ticker import MaxNLocator


def _move_window(fig, x, y):
    try:
        fig.canvas.manager.window.wm_geometry(f"+{x}+{y}")
    except Exception:
        try:
            fig.canvas.manager.window.move(x, y)
        except Exception:
            pass


def plot_lines(sumcalspectra, samplespectra, title='', individual_spectra=None, residual_history=None):
    import bisect

    xcal = sorted(sumcalspectra.keys())
    xsamp = sorted(samplespectra.keys())
    ycal = [sumcalspectra[k] for k in xcal]
    ysamp = [samplespectra[k] for k in xsamp]

    residue = []
    for wn, val in zip(xsamp, ysamp):
        i = bisect.bisect_left(xcal, wn)
        if i == 0:
            nearest = xcal[0]
        elif i >= len(xcal):
            nearest = xcal[-1]
        else:
            nearest = xcal[i] if abs(xcal[i] - wn) <= abs(xcal[i - 1] - wn) else xcal[i - 1]
        residue.append(val - sumcalspectra[nearest])

    n_mols = len(individual_spectra) if individual_spectra else 0
    legend_rows = max(1, math.ceil((n_mols + 1) / 6))
    legend_height = 0.18 + 0.07 * max(0, legend_rows - 1)

    has_history = bool(residual_history)
    n_cols = 4 if has_history else 3
    fig_width = 22 if has_history else 16

    fig, axes = plt.subplots(1, n_cols, figsize=(fig_width, 4),
                             gridspec_kw={'bottom': legend_height + 0.12})
    fig.suptitle(f"Spectral Fit Results - {title}" if title else "Spectral Fit Results")

    axes[0].scatter(xsamp, ysamp, color='red', s=2, label='Sample')
    axes[0].set_title("Sample")
    axes[0].set_xlabel("Wavenumber")
    axes[0].set_ylabel("Absorption")
    axes[0].xaxis.set_major_locator(MaxNLocator(nbins=6))

    if individual_spectra:
        colors = plt.cm.tab20.colors
        handles = []
        for idx, (mol, mol_spec) in enumerate(individual_spectra.items()):
            xmol = sorted(mol_spec.keys())
            ymol = [mol_spec[k] for k in xmol]
            line, = axes[1].plot(xmol, ymol, color=colors[idx % len(colors)],
                                 linewidth=1.2, alpha=0.8, label=mol)
            handles.append(line)
        total_line, = axes[1].plot(xcal, ycal, color='black', linewidth=1.5,
                                   linestyle='--', label='Total fit')
        handles.append(total_line)
        fig.legend(handles=handles, loc='lower center', ncol=6,
                   fontsize=8, frameon=True,
                   bbox_to_anchor=(0.5, 0.01))
    else:
        axes[1].scatter(xcal, ycal, color='blue', s=2)
    axes[1].set_title("Fitted Spectrum")
    axes[1].set_xlabel("Wavenumber")
    axes[1].xaxis.set_major_locator(MaxNLocator(nbins=6))

    axes[2].scatter(xsamp, residue, color='green', s=2)
    axes[2].axhline(0, color='gray', linewidth=0.8, linestyle='--')
    axes[2].set_title("Residue")
    axes[2].set_xlabel("Wavenumber")
    axes[2].xaxis.set_major_locator(MaxNLocator(nbins=6))

    if has_history:
        steps = list(range(len(residual_history)))
        deltas = [0.0] + [residual_history[i - 1] - residual_history[i]
                          for i in range(1, len(residual_history))]
        window = 5
        smoothed_delta = [
            sum(deltas[max(0, i - window + 1):i + 1]) / min(i + 1, window)
            for i in range(len(deltas))
        ]

        ax_hist = axes[3]
        ax_hist.plot(steps, residual_history, color='crimson', linewidth=1.5, label='Residual')
        ax_hist.set_title("Residual per Step")
        ax_hist.set_xlabel("Step")
        ax_hist.set_ylabel("Residual", color='crimson')
        ax_hist.tick_params(axis='y', labelcolor='crimson')
        ax_hist.xaxis.set_major_locator(MaxNLocator(nbins=6))

        ax_delta = ax_hist.twinx()
        ax_delta.plot(steps, smoothed_delta, color='steelblue', linewidth=1.0,
                      linestyle='--', alpha=0.8, label='Δ (5-step avg)')
        ax_delta.axhline(0, color='gray', linewidth=0.5, linestyle=':')
        ax_delta.set_ylabel("Δ / step", color='steelblue')
        ax_delta.tick_params(axis='y', labelcolor='steelblue')

        lines1, labels1 = ax_hist.get_legend_handles_labels()
        lines2, labels2 = ax_delta.get_legend_handles_labels()
        ax_hist.legend(lines1 + lines2, labels1 + labels2, loc='upper right', fontsize=7)

    plt.show(block=False)
    _move_window(fig, 100, 100)


