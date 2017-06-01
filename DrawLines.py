import matplotlib.pyplot as plt

xcal = []
ycal =[]
xsamp =[]
ysamp = []
residue = []



def plot_lines(sumcalspectra, samplespectra):
    xsamp = sorted(samplespectra)
    xcal = sorted(sumcalspectra)

    for k in xcal:
        ycal.append(float(sumcalspectra[k]))

    for k in xsamp:
        ysamp.append(float(samplespectra[k]))

    for iterator in range(0,len(xcal)):
        residue.append(float(ysamp[iterator])-float(ycal[iterator]))

    plt.plot(xsamp, ysamp, 'b-' , xcal, ycal, "r-", xsamp , residue , "g--")
    plt.show()