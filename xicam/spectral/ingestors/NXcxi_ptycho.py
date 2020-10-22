import mimetypes
import time
import event_model
import h5py
from dask import array as da
from pathlib import Path
from xarray import DataArray
from scipy.constants import h, e, speed_of_light
import numpy as np

from xicam.core import msg

mimetypes.add_type('application/x-cxi', '.cxi')


ENERGY_FIELD = 'E [eV]'
COORDS_X_FIELD = 'x [nm]'
COORDS_Y_FIELD = 'y [nm]'

### describe projections (not needed for CatalogViewer but for technique-specific plugin that will use intents
# TODO match key names with NX structures
projections = [{'name': 'NXcxi_ptycho',
                'version': '0.1.0',
                'projection':
                    {'object_transmission': {'type': 'linked',
                              'stream': 'primary',
                              'location': 'event',
                              'field': 'transmission'},
                     'object_phase': {'type': 'linked',
                              'stream': 'primary',
                              'location': 'event',
                              'field': 'phase'},
                     'energy': {'type': 'linked',
                                'stream': 'primary',
                                'location': 'event',
                                'field': ENERGY_FIELD},
                     'coords_x': {'type': 'linked',
                                  'stream': 'primary',
                                  'location': 'event',
                                  'field': COORDS_X_FIELD},
                     'coords_y': {'type': 'linked',
                                  'stream': 'primary',
                                  'location': 'event',
                                  'field': COORDS_Y_FIELD}
                     }
                }]


def rec_psize_nm(energy, corner_x, corner_y, corner_z):
    l = (1239.852 / (energy / e)) * 1e-9
    NA = np.sqrt(corner_x ** 2 + corner_y ** 2) / np.sqrt(2.) / corner_z
    return np.round(l / 2. / NA * 1e9, 2)


def ingest_cxi(paths):
    assert len(paths) == 1
    path = paths[0]

    h5 = h5py.File(path, 'r')

    #TODO: What initial sorting is needed for a general dataset
    h5_entry_dict = {}
    for key in h5.keys():
        if 'entry' in key:
            h5_entry_dict[key] = key.split('_')[-1].zfill(3)
    sorted_entry_list = sorted(h5_entry_dict.items(), key=lambda item: item[1])
    # TODO check if energies are "continuous" or have interruptions
    # the removal of last for entries is only temporary due to the example dataset
    del sorted_entry_list[-4:]

    frames_stack = []
    rec_stack = []
    energy_stack = []
    energy_eV_stack = []
    wavelength_stack = []

    rec_shape = h5['entry_1']['image_1']['data'].shape
    dim_x = rec_shape[0]
    dim_y = rec_shape[1]

    for entry in sorted_entry_list:
        rec = da.from_array(h5[entry[0]]['image_1']['data'])
        rec_stack.append(rec)  # reconstructed image data 2D array (X*Y)
        energy = h5[entry[0]]['instrument_1']['source_1']['energy'][()]
        energy_stack.append(energy)      # energy in Joule
        energy_eV_stack.append(energy/e)
        wavelength_stack.append(speed_of_light/energy)

        # TODO if diffraction patterns are required load them and their positions
        # frames_stack.append(da.from_array(h5[entry[0]]['data_1']['data']))  # diffraction patterns 3D array (N*X*Y)
        # translation = h5['entry_1']['data_1']['translation'][()]  # positions of diffraction patterns

    # TODO
    #  [x] get pixelsize from cxi file or calculate from corner_position and energy
    #  [ ] what if multiple scans with different pixel size should be compared?
    #  [ ] check if energy is in J or eV?
    try:
        pxsize = h5['entry_1/image_1/pixel_size'][()]
    except KeyError:
        msg.logMessage('Image pixel size not found in file >> calculating from corner position and energy', msg.WARNING)
        corner_x, corner_y, corner_z = h5[entry[0]]['instrument_1/detector_1/corner_position'][()]
        pxsize = rec_psize_nm(energy, corner_x, corner_y, corner_z)

    # calc coords from pxsize
    coords_x = [pxsize*i for i in range(dim_x)]
    coords_y = [pxsize*i for i in range(dim_y)]

    ### Create data array
    xarray_trans = DataArray(np.abs(da.stack(rec_stack)), dims=('E (eV)', 'y (nm)', 'x (nm)'), coords=[energy_eV_stack, coords_y, coords_x])
    xarray_phase = DataArray(np.angle(rec_stack), dims=('E (eV)', 'y (nm)', 'x (nm)'), coords=[energy_eV_stack, coords_y, coords_x])
    # xarray_sortE = xarray.sortby('E [eV]')
    #return energy_eV_stack, rec_stack, pxsize, xarray#, xarray_sortE #,dask_data


    # Compose bluesky run
    run_bundle = event_model.compose_run()  # type:event_model.ComposeRunBundle
    #Create start document
    start_doc = run_bundle.start_doc
    start_doc["sample_name"] = Path(paths[0]).resolve().stem
    start_doc["projections"] = projections
    yield 'start', start_doc

    source = 'nxCXI_ptycho'
    frame_data_keys = {'transmission': {'source': source,
                               'dtype': 'number',
                               'dims': xarray_trans.dims,
                               # 'coords': [energy, sample_y, sample_x],
                               'shape': xarray_trans.shape},
                       'phase': {'source': source,
                               'dtype': 'number',
                               'dims': xarray_phase.dims,
                               # 'coords': [energy, sample_y, sample_x],
                               'shape': xarray_phase.shape},
                       ENERGY_FIELD: {'source': source,
                                      'dtype': 'number',
                                      'shape': np.asarray(energy_eV_stack).shape},
                       COORDS_Y_FIELD: {'source': source,
                                        'dtype': 'number',
                                        'shape': np.asarray(coords_x).shape},
                       COORDS_X_FIELD: {'source': source,
                                        'dtype': 'number',
                                        'shape': np.asarray(coords_y).shape}
                       }

    # TODO: decide on stream names for derived data
    frame_stream_name = 'primary'
    # Compose descriptor
    frame_stream_bundle = run_bundle.compose_descriptor(data_keys=frame_data_keys,
                                                        name=frame_stream_name,
                                                        # configuration=_metadata(path)
                                                        )
    yield 'descriptor', frame_stream_bundle.descriptor_doc
    t = time.time()
    yield 'event', frame_stream_bundle.compose_event(data={'transmission': xarray_trans,
                                                           'phase': xarray_phase,
                                                           ENERGY_FIELD: energy_eV_stack,
                                                           COORDS_Y_FIELD: coords_y,
                                                           COORDS_X_FIELD: coords_x},
                                                     timestamps={'transmission': t,
                                                                 'phase': t,
                                                                 ENERGY_FIELD: t,
                                                                 COORDS_Y_FIELD: t,
                                                                 COORDS_X_FIELD: t})
    #create stop document
    yield 'stop', run_bundle.compose_stop()

