from tkinter import *
from tkinter import ttk

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
        input_file.set(value)
    except ValueError:
        pass


#Master frame
root = Tk()
root.title("Feet to Meters")

mainframe = ttk.Frame(root, padding="3 3 12 12")
mainframe.grid(column=0, row=0, sticky=(N, W, E, S))
mainframe.columnconfigure(0, weight=1)
mainframe.rowconfigure(0, weight=1)

#Input sample file and number of iterations
input_file = StringVar()
number_of_iterarions = StringVar()

input_file_entry = ttk.Entry(mainframe, width=7, textvariable=input_file)
input_file_entry.grid(column=2, row=1, sticky=(W, E))

number_of_iterarions_entry = ttk.Entry(mainframe, width=7, textvariable=number_of_iterarions)
number_of_iterarions_entry.grid(column=2, row=2, sticky=(W, E))

ttk.Label(mainframe, text="Entry sample file: ").grid(column=1, row=1, sticky=W)
ttk.Label(mainframe, text="Number of iterations").grid(column=1, row=2, sticky=W)

#Placement of several molecules !!aanpassen naar meer flexibel formaat!!
ttk.Label(mainframe, text="").grid(column=1, row=3, sticky=E)
ttk.Label(mainframe, text="Standaard moleculen in omgevingslucht").grid(column=1, row=4, sticky=E)

CO_entry = IntVar()
check_CO_entry = ttk.Checkbutton(mainframe, text = "CO", variable = CO_entry).grid(column=1, row=5, sticky=E)
C2H4_entry = IntVar()
check_C2H4_entry = ttk.Checkbutton(mainframe, text = "C2H4", variable = C2H4_entry).grid(column=2, row=5, sticky=W)
NH3_entry = IntVar()
check_NH3_entry = ttk.Checkbutton(mainframe, text = "NH3", variable = NH3_entry).grid(column=3, row=5, sticky=W)
H2O_entry = IntVar()
check_H2O_entry = ttk.Checkbutton(mainframe, text = "H2O", variable = H2O_entry).grid(column=4, row=5, sticky=W)

#Set calibration files button
ttk.Button(mainframe, text="Confirm calibration files", command=set_calibration_file).grid(column=4, row=6, sticky=W)

#Calculation button
ttk.Button(mainframe, text="Calculate", command=calculate).grid(column=5, row=6, sticky=W)

#Preform calculation
root.bind('<Return>', calculate)

root.mainloop()