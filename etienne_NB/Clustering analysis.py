from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib.pyplot as plt
from scipy.spatial.distance import squareform

clusterMethods = {"single","complete","average","weighted","median","centroid","ward"}

#Hierarchical Clustering
def dendogramPlot(linkageMatrix, labels):
    # Input: linkage Matrix, labels for the objects.
    # Output: dendogram plot
    plt.figure(figsize=(25,10))
    dendrogram(Z, labels = books)
    plt.show()
    
def linkageFunction(y, method):
    # Input: Y: Condensed distance matrix y. N rows and 2 columns. 
    # Method: Single, Complete, Average, Weighted, Ward, Median, Centroid
    # Output: Hierarchical clustering encoded as a linkage matrix
    return linkage(y, method)

def squareFormFunction(v):
    # Input: Either a condensed or redundant distance matrix
    # Ouput: If a condensed distance matrix is passed, a redundant one is returned.
    # if a redundant one is passed, a condensed distance matrix is returned.
    return squareform(v)

def flattenClustering(linkageMatrix, t, criterion):
    # Input: linkage Matrix, t = threshold, criterion: maxclust or other
    # Output: Array with objects in clusters
    return fcluster(linkageMatrix, t, criterion) 




