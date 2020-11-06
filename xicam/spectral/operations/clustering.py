# k-means
## scikit-learn.cluster.kmeans
# hierarchical clustering analysis "EMSC" (Extended Multiplicative Scattering Correction)
## https://scikit-learn.org/stable/modules/clustering.html#hierarchical-clustering
## https://github.com/RPCausin/EMSC/blob/master/EMSC.py: (Bassan, Konevskikh)
import enum
from typing import Union
import numpy as np
from sklearn.cluster import KMeans
from xicam.plugins.operationplugin import operation, categories, display_name, output_names, visible, input_names, intent
from xicam.core.intents import PlotIntent, ImageIntent


class init(enum.Enum):
    k_means = 'k-means++'
    random = 'random'

class algorithm(enum.Enum):
    auto = 'auto'
    full = 'full'
    elkan = 'elkan'

@operation
# @categories('Clustering')
@categories(('Spectral Imaging', 'Clustering'))
@display_name('K-means Clustering')
@output_names('data')
@visible('data', False)
@input_names('data', 'Number of clusters', 'Init method', 'Number of init run', 'Max iter', 'Tolerance', 'Verbose', 'Copy', 'algorithm', 'Random State')
@intent(ImageIntent, 'K-means clusters', output_map={'image':'data'})
def kmeans(data:np.ndarray, n_clusters:int=8, init:init='k-means++', n_init:int=10, max_iter:int=300, tol:float=0.0001, verbose:int=0, copy_x:bool=True, algorithm:algorithm='auto', random_state:int=None):
    km = KMeans(n_clusters, init=init, n_init=n_init, max_iter=max_iter, tol=tol, verbose=verbose, copy_x=copy_x, algorithm=algorithm, random_state=random_state)
    row, col, n_w = data.shape
    data = np.asarray(data).reshape(-1, n_w)
    km.fit(data)
    labels = km.predict(data)
    return labels.reshape(row, col)