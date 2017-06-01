from tkinter.filedialog import askopenfilename
import re

def read_sample_file():
    filename_open = askopenfilename()
    filename = open(filename_open, "r")
    sample_spectrum ={}
    for line in filename:
        line = line.rstrip()
        concentration_per_wavenumber = re.findall('\S*\S', line)
        key = concentration_per_wavenumber[0]
        if key != "":
            value = concentration_per_wavenumber[1]
            sample_spectrum[key] = value
        else:
            continue
    filename.close()
    return sample_spectrum
