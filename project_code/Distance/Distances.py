from scipy.spatial.distance import pdist
from scipy.stats import pearsonr, kendalltau, spearmanr
from scipy.linalg import norm
from scipy.spatial.distance import euclidean

boolVectorsMetric = {"sokalmichener", "sokalsneath","russellrao","rogerstanimoto","kulsinski","dice", "yule"} #Boolean = {0,1}
agreementMetric = {"jaccard","hamming"} #number of same values / length vector
simpleMetric = {"euclidean","cityblock","correlation","sqeuclidean","cosine","canberra","braycurtis","chebyshev"} #Correlation is pearson
advancedMetric = {"wminkowski","mahalanobis","seuclidean"} #Expects extra parameters. 
         
#Normal distance
def matrixDistances(X, metric):
    # Input: X is an m by n array of m original observations in an n-dimensional space.
    # Metrics: 'braycurtis’, ‘canberra’, ‘chebyshev’, ‘cityblock’, ‘correlation’, ‘cosine’, ‘dice’, ‘euclidean’, ‘hamming’, 
    # ‘jaccard’,‘kulsinski’, ‘mahalanobis’, ‘matching’, ‘minkowski’, ‘rogerstanimoto’, ‘russellrao’, ‘seuclidean’, ‘sokalmichener’, 
    # ‘sokalsneath’, ‘sqeuclidean’, ‘yule’.
    # Output: Returns a condensed distance matrix Y
    return pdist(X, metric)

def correlation(x,y):
    # Input: vector x, vector y
    # Output: spearman rank and kendall tau rank correlation
    correlations = [spearmanr(x,y),kendalltau(x,y)]
    return correlations

def correlationToDistance(corr):
    # Input: Correlation
    # Output: Distance, either 1-correlation or sqrt(1-cor^2)
    return (1-corr)

def helligerDistance(x,y):
    return euclidean(np.sqrt(x), np.sqrt(y)) / np.sqrt(2)  