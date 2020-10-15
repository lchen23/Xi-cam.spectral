import time
import numpy as np
from astropy.io import fits
import event_model
from pathlib import Path
import dask.array as da
from xarray import DataArray
import mimetypes

mimetypes.add_type('application/x-fits', '.fits')


# ttype - coords
# tunits
# ttype5
# tform5 (?)
# trvals position of first point
# tdelts pixel sizes
# 1-d array of frames

ENERGY_FIELD = 'E (eV)'
SAMPLE_X_FIELD = 'Sample X (um)'
SAMPLE_Y_FIELD = 'Sample Y (um)'
ANGLE_FIELD = '???'

projections = [{'name': 'arpes',
                'version': '0.1.0',
                'projection':
                    {'data': {'type': 'linked',
                              'stream': 'primary',
                              'location': 'event',
                              'field': 'raw'},
                     'energy': {'type': 'linked',
                                'stream': 'primary',
                                'location': 'event',
                                'field': ENERGY_FIELD},
                     'sample_x': {'type': 'linked',
                                  'stream': 'primary',
                                  'location': 'event',
                                  'field': SAMPLE_X_FIELD},
                     'sample_y': {'type': 'linked',
                                  'stream': 'primary',
                                  'location': 'event',
                                  'field': SAMPLE_Y_FIELD},
                     'angle???': {'type': 'linked',
                                  'stream': 'primary',
                                  'location': 'event',
                                  'field': ANGLE_FIELD},
                     }

                }]


def ingest_NXarpes(paths):
    assert len(paths) == 1
    path = paths[0]

    f = fits.open(path)

    frame_count = f[1].data.shape[0]
    data = np.stack([f[1].data[i][-1] for i in range(frame_count)])
    data = data.reshape((f[0].header["N_0_0"], f[0].header["N_0_1"], data.shape[1], data.shape[2]))
    energy = np.arange(f[0].header["SFSE_0"], f[0].header["SFEE_0"], 1. / f[0].header["SFPEV_0"] * f[0].header["SFBE0"])
    sample_x = np.linspace(f[0].header["ST_0_0"], f[0].header["EN_0_0"], f[0].header["N_0_0"])
    sample_y = np.linspace(f[0].header["ST_0_1"], f[0].header["EN_0_1"], f[0].header["N_0_1"])
    unknown_axis_coords = np.arange(data.shape[2])

    dim0 = f"{f[0].header['NM_0_0']} ({f[0].header['UN_0_0']})"
    dim1 = f"{f[0].header['NM_0_1']} ({f[0].header['UN_0_1']})"

    xarray = DataArray(data, dims=[dim1, dim0, '???', 'E (eV)'],
                       coords=[sample_y, sample_x, unknown_axis_coords, energy])
    # dask_data = da.from_array(xarray)

    # Compose run start
    run_bundle = event_model.compose_run()  # type: event_model.ComposeRunBundle
    start_doc = run_bundle.start_doc
    start_doc["sample_name"] = Path(paths[0]).resolve().stem
    start_doc["projections"] = projections
    yield 'start', start_doc

    # Compose descriptor
    source = 'nxSTXM'
    frame_data_keys = {'raw': {'source': source,
                               'dtype': 'number',
                               'dims': xarray.dims,
                               # 'coords': [energy, sample_y, sample_x],
                               'shape': data.shape},
                       ENERGY_FIELD: {'source': source,
                                      'dtype': 'number',
                                      'shape': energy.shape},
                       SAMPLE_X_FIELD: {'source': source,
                                        'dtype': 'number',
                                        'shape': sample_x.shape},
                       SAMPLE_Y_FIELD: {'source': source,
                                        'dtype': 'number',
                                        'shape': sample_y.shape},
                       ANGLE_FIELD: {'source': source,
                                     'dtype': 'number',
                                     'shape': unknown_axis_coords.shape}
                       }
    frame_stream_name = 'primary'
    frame_stream_bundle = run_bundle.compose_descriptor(data_keys=frame_data_keys,
                                                        name=frame_stream_name,
                                                        # configuration=_metadata(path)
                                                        )
    yield 'descriptor', frame_stream_bundle.descriptor_doc

    # NOTE: Resource document may be meaningful in the future. For transient access it is not useful
    # # Compose resource
    # resource = run_bundle.compose_resource(root=Path(path).root, resource_path=path, spec='NCEM_DM', resource_kwargs={})
    # yield 'resource', resource.resource_doc

    # Compose datum_page
    # z_indices, t_indices = zip(*itertools.product(z_indices, t_indices))
    # datum_page_doc = resource.compose_datum_page(datum_kwargs={'index_z': list(z_indices), 'index_t': list(t_indices)})
    # datum_ids = datum_page_doc['datum_id']
    # yield 'datum_page', datum_page_doc

    yield 'event', frame_stream_bundle.compose_event(data={'raw': xarray,
                                                           ENERGY_FIELD: energy,
                                                           SAMPLE_X_FIELD: sample_x,
                                                           SAMPLE_Y_FIELD: sample_y,
                                                           ANGLE_FIELD: unknown_axis_coords},
                                                     timestamps={'raw': time.time(),
                                                                 ENERGY_FIELD:time.time(),
                                                                 SAMPLE_X_FIELD:time.time(),
                                                                 SAMPLE_Y_FIELD:time.time(),
                                                                 ANGLE_FIELD:time.time()})

    yield 'stop', run_bundle.compose_stop()


if __name__ == "__main__":
    path = '20161214_00034.fits'

    docs = list(ingest_NXarpes([path]))

    print(docs)
