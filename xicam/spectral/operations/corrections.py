import enum
from typing import Union
import numpy as np
from sklearn.decomposition import PCA, NMF
import umap
from xicam.plugins.operationplugin import operation, categories, display_name, output_names, visible, input_names

# Spectra
## Poly-line interpolation "Rubber Band"
# scipy.interpolate.interp1d
## Automatic linear interpolation
@operation
def interpolate_1d()

# scipy.spatial.ConvexHull
## Background spectra subtraction
