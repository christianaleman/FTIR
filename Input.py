from Moleculeclass import*

def input_molecules():
    print("Welkom by ons fantastische fit-algoritme")
    print("Voor nu de gewenste moeleculen in en indien u wilt stoppen voer dan s in: ")

    input_molecules = True
    list_of_molecules = []

    while input_molecules:
        name_of_molecule = input("Voer de naam van het molecuul in: ")
        if name_of_molecule == "s":
            break
        list_of_molecules.append(name_of_molecule)

    dict_of_molecules = {}
    length_list_molecules = len(list_of_molecules)

    for counter_of_number_molecules in range(0, length_list_molecules):
        dict_of_molecules[counter_of_number_molecules] = list_of_molecules[counter_of_number_molecules]

    dict_of_molecules = {value: Molecule(value) for key,value in dict_of_molecules.items()}
    spectra_of_molecules = {}
    spectra_of_molecules = {key: Molecule(str(value)).determine_spectrum() for key, value in dict_of_molecules.items()}
    return spectra_of_molecules