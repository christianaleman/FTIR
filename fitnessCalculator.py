import numpy as np

ABSORPTION_PENALTY = 1000.0


class FitnessCalculator:
    def __init__(self, sample_spectrum, molecule_spectra,
                 wn_min=None, wn_max=None, max_absorption=None,
                 baseline=None, weights=None):
        self.mol_names = list(molecule_spectra.keys())
        self.baseline = baseline
        self.max_absorption = max_absorption

        # Wavenumber grid from first molecule (all molecules share one grid)
        all_wns = sorted(molecule_spectra[self.mol_names[0]][0].keys())
        if wn_min is not None or wn_max is not None:
            all_wns = [wn for wn in all_wns
                       if (wn_min is None or wn >= wn_min)
                       and (wn_max is None or wn <= wn_max)]
        self.wn_array = np.array(all_wns, dtype=np.float64)
        n_wn = len(self.wn_array)

        # Per-molecule calibration data: (n_concs, n_wn) arrays
        self.cal_concs_arr = {}
        self.cal_abs = {}
        for mol in self.mol_names:
            spec, concs, _unit = molecule_spectra[mol]
            self.cal_concs_arr[mol] = np.array(concs, dtype=np.float64)
            matrix = np.zeros((len(concs), n_wn), dtype=np.float64)
            for j, wn in enumerate(all_wns):
                if wn in spec:
                    matrix[:, j] = spec[wn]
            self.cal_abs[mol] = matrix

        # Sample spectrum mapped to molecule wavenumber grid (nearest neighbour)
        sw = sorted(sample_spectrum.keys())
        sa = np.array([sample_spectrum[wn] for wn in sw], dtype=np.float64)
        sw_arr = np.array(sw, dtype=np.float64)
        idx = np.searchsorted(sw_arr, self.wn_array)
        idx_lo = np.clip(idx - 1, 0, len(sw) - 1)
        idx_hi = np.clip(idx,     0, len(sw) - 1)
        nearest = np.where(
            np.abs(sw_arr[idx_hi] - self.wn_array) <= np.abs(sw_arr[idx_lo] - self.wn_array),
            idx_hi, idx_lo,
        )
        self.sample_array = sa[nearest]

        # Weight array
        self.weight_array = np.ones(n_wn, dtype=np.float64)
        if weights:
            for lo, hi, w in weights:
                self.weight_array[(self.wn_array >= lo) & (self.wn_array <= hi)] = w

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def calculate(self, molecule_concentrations):
        """Single-solution evaluation (used for the final visualisation step)."""
        class _Wrap:
            def __init__(self, y): self.y = y
        return self.calculate_batch([_Wrap(molecule_concentrations)])[0]

    def calculate_batch(self, solutions):
        """Vectorised evaluation of a list of Solution objects.

        Returns a plain list of residual floats in the same order.
        """
        n_off = len(solutions)
        n_wn  = len(self.wn_array)

        # Concentration matrix (n_off, n_mol)
        conc_matrix = np.array(
            [[sol.y[mol] for mol in self.mol_names] for sol in solutions],
            dtype=np.float64,
        )

        fitted_all = np.zeros((n_off, n_wn), dtype=np.float64)

        for m_idx, mol in enumerate(self.mol_names):
            concs = conc_matrix[:, m_idx]          # (n_off,)
            cal_c = self.cal_concs_arr[mol]
            n_c   = len(cal_c)

            if n_c == 1:
                fitted_all += self.cal_abs[mol][0]
                continue

            i  = np.searchsorted(cal_c, concs, side='right')
            lo = np.clip(i - 1, 0, n_c - 2)
            hi = lo + 1

            denom = cal_c[hi] - cal_c[lo]
            t     = np.where(denom > 0, (concs - cal_c[lo]) / denom, 0.0)  # (n_off,)

            abs_lo = self.cal_abs[mol][lo]   # fancy-index → (n_off, n_wn)
            abs_hi = self.cal_abs[mol][hi]
            fitted_all += abs_lo + t[:, np.newaxis] * (abs_hi - abs_lo)

        if self.baseline:
            residuals_bl = self.sample_array[np.newaxis, :] - fitted_all
            offsets, slopes = self._fit_baseline_batch(residuals_bl)
            fitted_all += offsets[:, np.newaxis] + slopes[:, np.newaxis] * self.wn_array

        diff      = np.abs(self.sample_array[np.newaxis, :] - fitted_all)   # (n_off, n_wn)
        residuals = diff @ self.weight_array                                  # (n_off,)

        if self.max_absorption is not None:
            excess     = np.sum(np.maximum(0.0, fitted_all - self.max_absorption), axis=1)
            residuals += ABSORPTION_PENALTY * excess

        return residuals.tolist()

    # ------------------------------------------------------------------
    # Internals
    # ------------------------------------------------------------------

    def _fit_baseline_batch(self, residuals_batch):
        """Fit a baseline to each row of residuals_batch (n_off, n_wn).

        Returns (offsets, slopes) each of shape (n_off,).
        """
        if self.baseline == 'offset':
            return np.mean(residuals_batch, axis=1), np.zeros(len(residuals_batch))

        wns  = self.wn_array
        n    = len(wns)
        sx   = float(np.sum(wns))
        sx2  = float(np.dot(wns, wns))
        sy   = np.sum(residuals_batch, axis=1)   # (n_off,)
        sxy  = residuals_batch @ wns              # (n_off,)
        denom = n * sx2 - sx ** 2
        if denom == 0:
            return sy / n, np.zeros(len(residuals_batch))
        slopes  = (n * sxy - sx * sy) / denom
        offsets = (sy - slopes * sx) / n
        return offsets, slopes
