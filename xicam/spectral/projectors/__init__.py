import numpy as np
from databroker.core import BlueskyRun


def project_nxSTXM(run_catalog: BlueskyRun):
    _, projection = next(filter(lambda projection: projection[0] == 'nxSTXM', run_catalog.metadata['start']['projections']))
    stream, field = projection['irmap/DATA/data']
    sample_x = projection['irmap/DATA/sample_x']
    sample_y = projection['irmap/DATA/sample_y']
    energy = projection['irmap/DATA/energy']

    xdata = getattr(run_catalog, stream).to_dask()[field]  # type: xr.DataArray

    xdata = np.squeeze(xdata)

    xdata = xdata.assign_coords({xdata.dims[0]: energy, xdata.dims[2]: sample_x, xdata.dims[1]: sample_y})

    return xdata