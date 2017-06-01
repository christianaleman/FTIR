def fitfactor(samplefile, somkalibratiefile):
    residue = []
    for key, value in samplefile.items():
        residue.append(abs((float(samplefile[key]))- somkalibratiefile[key]))
    total_sum_residue = (sum(residue))
    return total_sum_residue