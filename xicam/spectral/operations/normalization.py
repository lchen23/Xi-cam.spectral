import enum
import numpy as np

from xicam.core.intents import ImageIntent
from xicam.plugins.operationplugin import operation, input_names, categories, display_name, output_names, visible, \
    intent
from sklearn.preprocessing import StandardScaler, Normalizer
from xarray import DataArray


@operation
@categories(('Spectral Imaging', 'Normalization'), ('BSISB', 'Normalization'))
@display_name('Standard Scaler')
@output_names('data')
@visible('data', False)
@intent(ImageIntent, 'Normalized Data', output_map={'image': 'data'})
def standard_scaler(data: np.ndarray, copy: bool = True, with_mean: bool = True, with_std: bool = True) -> np.ndarray:
    return _standard_scaler(data, copy, with_mean, with_std)


def _standard_scaler(data: np.ndarray, copy: bool = True, with_mean: bool = True, with_std: bool = True) -> np.ndarray:
    if data.ndim > 2:
        return np.array([_standard_scaler(data=slc, copy=copy, with_mean=with_mean, with_std=with_std) for slc in data])
    else:
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
@intent(ImageIntent, 'Normalized Data', output_map={'image': 'data'}, )
def normalizer(data: np.ndarray, norm: Norm = Norm.l2.name, copy:bool=True):
    return _normalizer(data=data, norm=norm, copy=copy)


def _normalizer(data: np.ndarray, norm: Norm = Norm.l2.name, copy:bool=True):
    if data.ndim > 2:
        return np.array([_normalizer(data=slc, norm=norm, copy=copy) for slc in data])
    else:
        transformer = Normalizer(norm=norm, copy=copy).fit(data)
        ret = transformer.transform(data, copy)
        if isinstance(data, DataArray):
            ret = DataArray(ret, dims=data.dims, coords=data.coords)
        return ret
