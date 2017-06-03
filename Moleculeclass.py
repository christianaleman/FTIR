import re

class Molecule:
    """A simple example class"""

    def __init__(self, name):
        self.name = name

    def determine_spectrum(self):
        from tkinter.filedialog import askopenfilename
        filename_open = askopenfilename()
        filename = open(filename_open, "r")
        # Determination amount number of calibration files
        counter_calibration_files = 0
        for line in filename:
            line = line.rstrip()
            counter_calibration_files += 1
            if (counter_calibration_files == 3):
                f = re.findall('\S*\S', line)
                number_of_calibration_files = len(f)
                break
        # Determination of concentrations used in calibration
        concentrations_used_in_calfiles = []
        counter_concentrations = 0
        for item in range(1, number_of_calibration_files):
            concentrations_used_in_calfiles.append(float(f[counter_concentrations + 1]))
            counter_concentrations += 1
        # Reading the complete calibration file line by line and storing it in a dictionary {wavenumber, [c0,c1,...,cn]}
        spectrum = {}
        for line in filename:
            line = line.rstrip()
            concentration_per_wavenumber = re.findall('\S*\S', line)
            absorptions = []
            for item in range(1, number_of_calibration_files):
                absorptions.append(concentration_per_wavenumber[item])
                spectrum[concentration_per_wavenumber[0]] = absorptions
        filename.close()
        return(spectrum, concentrations_used_in_calfiles)
