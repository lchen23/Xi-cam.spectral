import numpy as np
from databroker.core import BlueskyRun

from xicam.core.intents import ImageIntent


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


def project_nxCXI_ptycho(run_catalog: BlueskyRun):
    projection = next(filter(lambda projection: projection['name'] == 'NXcxi_ptycho', run_catalog.metadata['start']['projections']))

    transmission_rec_stream = projection['projection']['object_transmission']['stream']
    transmission_rec_field = projection['projection']['object_transmission']['field']
    phase_rec_stream = projection['projection']['object_phase']['stream']
    phase_rec_field = projection['projection']['object_phase']['field']
    energy = run_catalog.primary.read()['E [eV]'].data[0]
    coords_x = run_catalog.primary.read()['x [nm]'].data[0]
    coords_y = run_catalog.primary.read()['y [nm]'].data[0]

    # rec_data = getattr(run_catalog, transmission_rec_stream).to_dask().rename({transmission_rec_field: 'object_transmission', \
    #                                                                           phase_rec_field: 'object_phase'})
    rec_data_trans = getattr(run_catalog, transmission_rec_stream).to_dask()[transmission_rec_field]
    rec_data_trans = np.squeeze(rec_data_trans)
    rec_data_phase = getattr(run_catalog, phase_rec_stream).to_dask()[phase_rec_field]
    rec_data_phase = np.squeeze(rec_data_phase)

    rec_data_trans = rec_data_trans.assign_coords(
        {rec_data_trans.dims[0]: energy, rec_data_trans.dims[1]: coords_y, rec_data_trans.dims[2]: coords_x})

    return [ImageIntent(item_name='Transmission Reconstruction', image=rec_data_trans),
                # ImageIntent(image=rec_data_phase, item_name='phase reconstruction')
            ]


projection_mapping = {'NXcxi_ptycho': project_nxCXI_ptycho,
                      'nxSTXM': project_nxSTXM}


def project_all(run_catalog: BlueskyRun):
    for projection in run_catalog.metadata['start']['projections']:
        projector = projection_mapping.get(projection['name'])
        if projector:
            return projector(run_catalog)