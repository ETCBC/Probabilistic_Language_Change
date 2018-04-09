import pandas as pd
import matplotlib.pyplot as plt 

def raw_transPictures(Trans, raw):
    diff = pd.DataFrame([Trans,raw], index = ["Transformed","Raw"]).T
    plt.figure()
    diff.plot(kind ="bar",figsize = (15,10))
    plt.title("Transformation of number of transitions")
    plt.xlabel("Book")
    plt.ylabel("Number of transitions")
    plt.show()