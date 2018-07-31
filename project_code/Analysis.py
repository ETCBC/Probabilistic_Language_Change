#import os
#os.chdir("C:/Users/etien/Documents/Github/Probabilistic_Language_Change/project_code")

import pandas as pd 
import numpy as np
import collections
import matplotlib.pyplot as plt
from itertools import chain
from scipy.cluster import hierarchy
import seaborn as sns

#Libraries
from data.bhsa import * #Load data
from markov.Markov_Chain import * #Transitions
from clustering.Clustering_analysis import *

dataset = get_data(books=["sbh","lbh"])
del dataset["trees"]


# =============================================================================
# Unique values
# =============================================================================
features_unique = collections.defaultdict(dict)
for f in dataset.keys():
    unique_values = set()
    for d in dataset[f].keys():    
        for b in dataset[f][d].keys():
            clauses = dataset[f][d][b]
            if f == "clause_types":
                feature_values = set(clauses[0])
            else:
                feature_values = set(chain(*clauses))
            unique_values = unique_values | feature_values
    features_unique[f] = list(unique_values)
print([len(v) for k,v in features_unique.items()])   
print(features_unique)   


# =============================================================================
# Samples per book
# =============================================================================

samples_ = collections.defaultdict(dict)
for f in dataset.keys():
    for d in dataset[f].keys():
        for b in dataset[f][d].keys():
            items = dataset[f][d][b]            
            if f == "clause_types":
                samples_[f+"_"+d][b] = len(items[0])
            else:
                samples_[f+"_"+d][b] = len(list(chain(*items)))
df_samples = pd.DataFrame(samples_).fillna(0).mean(0).sort_values()
df_samples.plot(kind="barh", title="Average number of items per book")

# =============================================================================
# Remove information
# =============================================================================

del dataset["clause_types"]

for f in dataset.keys():
    del dataset[f]["D"]
    del dataset[f]["?"]

removelist = []
for f in dataset.keys():
    for d in dataset[f].keys():
        for b in dataset[f][d].keys():
            n = samples_[f+"_"+d][b]
            if n < 100:
                removelist.append([f,d,b])

for i in removelist:
    del dataset[i[0]][i[1]][i[2]]          

features = ['phrase_functions', 'phrase_types', 'word_pos']
domain = ['N', 'Q']

# =============================================================================
# Markov Chains
# =============================================================================

dataset_trans = collections.defaultdict(dict)
dataset_MC = collections.defaultdict(dict)
for f in dataset.keys():
    for d in dataset[f].keys():
        df = dataset[f][d]
        transMatrix = transitionMatrix(df, True)
        dataset_trans[f][d] = transMatrix
        dataset_MC[f][d] = MCTransformation(transMatrix)
        
#Sanity check
dataset_trans["phrase_functions"]["N"]["Genesis"] 
dataset_MC["phrase_functions"]["N"]["Genesis"].sum(1) 



# =============================================================================
# Distance between Markov chains
# =============================================================================
from scipy.spatial.distance import euclidean
#Distance
dataset_distance = collections.defaultdict(dict)
distan = []
distance_metric = "HELLINGER"

for f in dataset_MC.keys():
    for d in dataset_MC[f].keys():
        df = dataset_MC[f][d]
        
        distance_matrix = collections.defaultdict(dict)
        
        books = list(df.keys())
        for i in range(0, len(books)):
            for j in range(i+1, len(books)):
                MC_1 = df[books[i]]
                MC_2 = df[books[j]]
                
                distances = []
                
                if distance_metric == "TV":
                    dist_matrix = MC_1.subtract(MC_2).fillna(0)
                    for index, row in dist_matrix.T.iteritems():
                        dist = np.max(abs(row)) 
                        distances.append(dist)
                        info = [f,d,books[i],books[j],index,dist]
                        distan.append(info)
                
                if distance_metric == "HELLINGER":
                    dist_matrix = np.sqrt(MC_1).subtract(np.sqrt(MC_2)).fillna(0)
                    for index, row in dist_matrix.T.iteritems():
                        dist = np.linalg.norm(row, np.inf) / np.sqrt(2)
                        distances.append(dist)
                        info = [f,d,books[i],books[j],index,dist]
                        distan.append(info)
                
                if distance_metric == "Bhattacharyya":
                    dist_matrix = np.sqrt(MC_1.multiply(MC_2).fillna(0))
                    
                    for index, row in dist_matrix.T.iteritems():
                        som = np.sum(row)
                        if som > 0:
                            dist = -1 * np.log(som)
                            distances.append(dist)
                            info = [f,d,books[i],books[j],index,dist]
                            distan.append(info)
                
                if distance_metric == "alternative":
                    dist_matrix = np.sqrt(MC_1).subtract(np.sqrt(MC_2)).fillna(0)
                    for index, row in dist_matrix.T.iteritems():
                        dist = np.mean(abs(row))
                        distances.append(dist)
                        info = [f,d,books[i],books[j],index,dist]
                        distan.append(info)
                        
                distance_matrix[books[i]][books[j]] = np.mean(distances)
                distance_matrix[books[j]][books[i]] = np.mean(distances)
        dataset_distance[f][d] = pd.DataFrame(distance_matrix).fillna(0)

# =============================================================================
# Analysing distances
# =============================================================================
results = pd.DataFrame(distan, columns=["Feature","Domain","Book1","Book2","Item","Distance"]) 

k =  results.groupby("Item")["Distance"].mean()
results= results[results.Item.isin(k[k > 0].index)]


results.groupby(["Feature","Domain"])["Distance"].plot(kind="density", legend=True, figsize=(16,5))
results.boxplot(column = "Distance", by = ["Feature","Domain"], figsize = (15,7))


for f in features:
    for d in domain:
        df = results[((results.Feature == f) & (results.Domain == d))]
        grouped = df.groupby(["Item"])
        df= pd.DataFrame({col:vals['Distance'] for col,vals in grouped})
        meds = df.median().sort_values(ascending=False)
        df[meds.index].boxplot(figsize = (18,7))
        plt.show()

v = results[(results.Book1.isin(sbh_books)) & (results.Book2.isin(sbh_books))]
w = results[(results.Book1.isin(lbh_books)) & (results.Book2.isin(lbh_books))]

v.Distance.mean()
w.Distance.mean()
v.Distance.std()
w.Distance.std()     





# =============================================================================
# Distance between distance metrics
# =============================================================================

features = ['phrase_functions', 'phrase_types', 'word_pos']
domain = ['N', 'Q']

dataset_similarity = collections.defaultdict(dict)
for f1 in features:
    for d1 in domain:
        
        for f2 in features:
            for d2 in domain:
                df1 = dataset_distance[f1][d1]
                df2 = dataset_distance[f2][d2]
                distance = np.mean(abs(df1.subtract(df2)).mean())
                dataset_similarity[d1+f1][d2+f2] = distance

diff = pd.DataFrame(dataset_similarity)

sns.heatmap(diff)

# =============================================================================
# Hierarchical clustering
# =============================================================================

columns = len(domain)
rows = len(features)

#Per individual 
plt.figure(101, figsize = (20,20))
i = 1
for f in features:
    for d in domain:
        plt.subplot(rows, columns, i)
        dm = dataset_distance[f][d]
        Z = linkageFunction(dm, "ward")
        hierarchy.dendrogram(Z,labels=dataset_distance[f][d].columns, orientation = "right")
        plt.gca().set_title(f+" "+d)
        i = i +1
plt.show()

#Overall
mean_distance = dataset_distance['phrase_functions']['N'].fillna(0)
for f in features:
    for d in domain:
        if not f == 'phrase_functions' and not d == "N":
            dm = dataset_distance[f][d]
            mean_distance = mean_distance.add(dm, fill_value = 0)

plt.figure(101, figsize = (10,5))
Z = linkageFunction(mean_distance, "ward")
hierarchy.dendrogram(Z,labels=mean_distance.columns, orientation = "right")
       
# =============================================================================
# Kmediods
# =============================================================================
   
from clustering.Kmediods import *
from sklearn.metrics.pairwise import pairwise_distances
from scipy.spatial.distance import pdist, squareform
from sklearn.metrics import silhouette_score
import seaborn as sns

for f in features:
    for d in domain:
        print(f,d)
        dm = dataset_distance[f][d]
        
        scores = pd.DataFrame(np.zeros((100,len(dm.columns))), columns = dm.columns)
        sil_sc = []
        for i in range(0,1000):
            M, C = kMedoids(np.array(dm), 2, tmax = 1000)
            
            for label, value in C.items():
                books = list(dm.index[value])
                for book in books:
                    scores.loc[i,book] = label   
            
            sil = silhouette_score(dm,labels = scores.loc[i,], metric='precomputed')
            sil_sc.append(sil)

        print(np.max(sil_sc))   
                    
                    
        agreements = pdist(scores.T, 'jaccard')
        ag = pd.DataFrame(squareform(agreements), index=dm.columns, columns = dm.columns)
        order = [a for a in list(("Genesis","Exods","Judges","2_Kings","1_Samuel","2_Samuel","Joshua","Deuteronomy","1_Kings","Leviticus")+lbh_books) if a in dm.columns]
        ag = ag[order]
        ag = ag.reindex(index = order)

        sns.heatmap(ag)
        plt.show()

