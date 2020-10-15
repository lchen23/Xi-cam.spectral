import enum
import numpy as np
from xicam.plugins.operationplugin import operation, input_names, categories, display_name, output_names, visible
from sklearn.preprocessing import StandardScaler, Normalizer
from xarray import DataArray


@operation
@categories(('Spectral Imaging', 'Normalization'), ('BSISB', 'Normalization'))
@display_name('Standard Scaler')
@output_names('data')
@visible('data', False)
def standard_scaler(data: np.ndarray, copy: bool = True, with_mean: bool = True, with_std: bool = True) -> np.ndarray:
    scaler = StandardScaler(copy=copy, with_mean=with_mean, with_std=with_std)
    scaler.fit(data)
    ret = scaler.transform(data, copy)
    if isinstance(data, DataArray):
        ret = DataArray(ret, dims=data.dims, coords=data.coords)
    return ret


# Careful! These are "l"'s, not "1"'s
class Norm(enum.Enum):
    l2 = 'l2'
    l1 = 'l1'
    max = 'max'


@operation
@categories(('Spectral Imaging', 'Normalization'), ('BSISB', 'Normalization'))
@display_name('Normalizer')
@output_names('data')
@visible('data', False)
def normalizer(data: np.ndarray, norm: Norm = Norm.l2.name, copy:bool=True):
    transformer = Normalizer(norm=norm, copy=copy).fit(data)
    ret = transformer.transform(data, copy)
    if isinstance(data, DataArray):
        ret = DataArray(ret, dims=data.dims, coords=data.coords)
    return ret
