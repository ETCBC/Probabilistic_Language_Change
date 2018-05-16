from scipy.cluster.hierarchy import dendrogram, linkage, fcluster
import matplotlib.pyplot as plt
from scipy.spatial.distance import squareform
import numpy as np
import random

clusterMethods = {"single","complete","average","weighted","median","centroid","ward"}

#Hierarchical Clustering
def dendogramPlot(linkageMatrix, labels):
    # Input: linkage Matrix, labels for the objects.
    # Output: dendogram plot
    plt.figure(figsize=(25,20))
    ax = plt.gca()
    dendrogram(linkageMatrix, labels = labels, orientation ="right")
    ax.tick_params(axis='y', which='major', labelsize=20)
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


def k_medoids(distances, k=3):

    m = distances.shape[0] # number of points

    # Pick k random medoids.
    curr_medoids = np.array([-1]*k)
    while not len(np.unique(curr_medoids)) == k:
        curr_medoids = np.array([random.randint(0, m - 1) for _ in range(k)])
    old_medoids = np.array([-1]*k) # Doesn't matter what we initialize these to.
    new_medoids = np.array([-1]*k)
   
    # Until the medoids stop updating, do the following:
    while not ((old_medoids == curr_medoids).all()):
        # Assign each point to cluster with closest medoid.
        clusters = assign_points_to_clusters(curr_medoids, distances)

        # Update cluster medoids to be lowest cost point. 
        for curr_medoid in curr_medoids:
            cluster = np.where(clusters == curr_medoid)[0]
            new_medoids[curr_medoids == curr_medoid] = compute_new_medoid(cluster, distances)

        old_medoids[:] = curr_medoids[:]
        curr_medoids[:] = new_medoids[:]

    return clusters, curr_medoids

def assign_points_to_clusters(medoids, distances):
    distances_to_medoids = distances[:,medoids]
    clusters = medoids[np.argmin(distances_to_medoids, axis=1)]
    clusters[medoids] = medoids
    return clusters

def compute_new_medoid(cluster, distances):
    mask = np.ones(distances.shape)
    mask[np.ix_(cluster,cluster)] = 0.
    cluster_distances = np.ma.masked_array(data=distances, mask=mask, fill_value=10e9)
    costs = cluster_distances.sum(axis=1)
    return costs.argmin(axis=0, fill_value=10e9)



