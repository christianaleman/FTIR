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

    plt.figure(1)  # the first figure
    plt.subplot(221)  # the first subplot in the first figure
    plt.title("Sample")
    plt.scatter(xsamp, ysamp, color = 'red')
    plt.subplot(222)  # the second subplot in the first figure
    plt.title("Calibration files")
    plt.scatter(xcal, ycal, color = 'blue')
    plt.subplot(223)
    plt.title("Residue")
    plt.scatter(xsamp, residue, color = 'green')

    #plt.plot(xsamp, ysamp, 'b-' , xcal, ycal, "r-", xsamp , residue , "g--")
    plt.show()