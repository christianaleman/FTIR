import bisect


def Linearfit(molecule_concentrations, molecule_spectra):
    new_spectra_list = {}
    for key,value in molecule_concentrations.items():
        new_spectra_list_per_component ={}
        kalibratielijst = molecule_spectra[key][1]

        i = bisect.bisect(kalibratielijst, value)
        low_value = i - 1 if i < len(kalibratielijst) else i - 2
        high_value = i if i < len(kalibratielijst) else i - 1
        low_value_calibrationlist = kalibratielijst[low_value]
        high_value_calibrationlist = kalibratielijst[high_value]

        for iter1, iter2 in molecule_spectra[key][0].items():
            slope = (float(iter2[high_value])-float(iter2[low_value]))/(float(high_value_calibrationlist)-float(low_value_calibrationlist))
            intersect = float(iter2[low_value])
            nieuwe_waarde = slope * (value - low_value_calibrationlist) + intersect
            new_spectra_list_per_component[iter1] = nieuwe_waarde

        new_spectra_list[key] = new_spectra_list_per_component

    return(new_spectra_list)



