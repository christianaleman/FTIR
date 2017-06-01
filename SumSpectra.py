def SumSpectra(spectra):
    y = {}
    for k, v in spectra.items():
        for wave_length, value in v.items():
            if wave_length not in y:
                y[wave_length] = []
            y[wave_length].append(value)
    return {k: sum(v) for k, v in y.items()}
