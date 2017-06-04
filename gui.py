from tkinter import *
from tkinter import ttk
from ReadSampleFile import *
from tkinter.filedialog import askopenfilename
import re
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

def set_calibration_file(*args):
    molecules_selected = {"CO": CO_entry.get(), "C2H4": C2H4_entry.get(), "NH3": NH3_entry.get(),
                          "H2O": H2O_entry.get()}
    molecules_selected_true ={}
    for key,value in molecules_selected.items():
        if value==1:
            molecules_selected_true[key]=value
    print(molecules_selected_true)

#Functie nog aanpassen!!!!!!!!!!!!!!!!!!!!!
def calculate(*args):
    try:
        value = float(number_of_iterarions.get())
    except ValueError:
        pass

def read_sample_file(event):
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
    input_file.set(filename_open)
    filename.close()
    return sample_spectrum

#Master frame
root = Tk()
root.title("FTIR EVOLUTION")

mainframe = ttk.Frame(root)
mainframe.grid(column=0, row=0)
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

secondframe = ttk.Frame(mainframe)
secondframe.grid(column=1,row=8, sticky=(W))

#Input sample file and number of iterations
input_file = StringVar()
number_of_iterarions = StringVar()

input_file_entry = ttk.Entry(mainframe, width=100, textvariable=input_file)
input_file_entry.grid(column=2, row=1, sticky=(W, E))

number_of_iterarions_entry = ttk.Entry(mainframe, width=7, textvariable=number_of_iterarions)
number_of_iterarions_entry.grid(column=2, row=2, sticky=(W, E))

ttk.Label(mainframe, text="Entry sample file: ").grid(column=1, row=1, sticky=E)
ttk.Label(mainframe, text="Number of iterations").grid(column=1, row=2, sticky=E)

#Placement of several molecules !!aanpassen naar meer flexibel formaat!!
ttk.Label(mainframe, text="").grid(column=1, row=3, sticky=E)
ttk.Label(mainframe, text="Standaard moleculen in omgevingslucht").grid(column=1, row=4, sticky=E)

CO_entry = IntVar()
check_CO_entry = ttk.Checkbutton(mainframe, text = "CO", variable = CO_entry).grid(column=2, row=4, sticky=E)
C2H4_entry = IntVar()
check_C2H4_entry = ttk.Checkbutton(mainframe, text = "C2H4", variable = C2H4_entry).grid(column=3, row=4, sticky=W)
NH3_entry = IntVar()
check_NH3_entry = ttk.Checkbutton(mainframe, text = "NH3", variable = NH3_entry).grid(column=4, row=4, sticky=W)
H2O_entry = IntVar()
check_H2O_entry = ttk.Checkbutton(mainframe, text = "H2O", variable = H2O_entry).grid(column=5, row=4, sticky=W)

#Set calibration files button
ttk.Button(mainframe, text="Confirm calibration files", command=set_calibration_file).grid(column=4, row=6, sticky=W)

#Calculation button
ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=5, row=6, sticky=W)

#Adding the graphs
fig = Figure()
ax = fig.add_subplot(131)
ay = fig.add_subplot(132)
az = fig.add_subplot(133)

canvas = FigureCanvasTkAgg(fig, master=secondframe)
canvas.show()
canvas.get_tk_widget().grid(column =1, row=5)

#Preform calculation
root.bind('<Return>', calculate)

#Event input sample file name
input_file_entry.bind('<Button-1>', read_sample_file)

root.mainloop()