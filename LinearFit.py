import bisect


def Linearfit(molecule_concentrations, molecule_spectra):
    new_spectra_list = {}
    for mol, value in molecule_concentrations.items():
        cal_concs = molecule_spectra[mol][1]

        i = bisect.bisect(cal_concs, value)
        if i == 0:
            lo, hi = 0, min(1, len(cal_concs) - 1)
        elif i >= len(cal_concs):
            lo, hi = len(cal_concs) - 2, len(cal_concs) - 1
        else:
            lo, hi = i - 1, i

        c_lo = cal_concs[lo]
        c_hi = cal_concs[hi]
        denom = c_hi - c_lo

        component = {}
        for wn, absorptions in molecule_spectra[mol][0].items():
            if denom == 0:
                component[wn] = absorptions[lo]
            else:
                component[wn] = absorptions[lo] + (absorptions[hi] - absorptions[lo]) / denom * (value - c_lo)

        new_spectra_list[mol] = component

    return new_spectra_list
