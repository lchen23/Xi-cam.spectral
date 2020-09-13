import time

import event_model
import h5py
from dask import array as da
from pathlib import Path
from xarray import DataArray
from scipy.constants import h, e, speed_of_light
import numpy as np

def ingest_cxi(path):

    # assert len(path) == 1
    # path = path[0]
    # /Users/jreinhardt/Data/ALS/NS_200805056_full.cxi"

    h5 = h5py.File(path, 'r')
    #TODO: How to sort dict by energies?
    h5_entry_dict = {}
    for key in h5.keys():
        if 'entry' in key:
            h5_entry_dict[key] = key.split('_')[-1].zfill(3)
    sorted_entry_list = sorted(h5_entry_dict.items(), key=lambda item: item[1])
    del sorted_entry_list[-4:]

    frames_stack = []
    rec_stack = []
    energy_stack = []
    energy_eV_stack = []
    pxsize_stack = []

    det_psize_x_stack = []
    det_psize_y_stack = []
    coords_x_stack = []
    coords_y_stack = []
    wavelength_stack = []

    rec_shape = h5['entry_1']['image_1']['data'][()].shape
    dim_x = rec_shape[0]
    dim_y = rec_shape[1]

    def rec_psize_nm(energy, corner_x, corner_y, corner_z):
        l = (1239.852 / (energy/e)) * 1e-9
        NA = np.sqrt(corner_x**2 + corner_y**2) / np.sqrt(2.) / corner_z
        return np.round(l / 2. / NA * 1e9, 0)

    for entry in sorted_entry_list:
        # frames_stack.append(h5[entry[0]]['data_1']['data'][()])  # diffraction patterns 3D array (N*X*Y)
        rec = h5[entry[0]]['image_1']['data'][()]
        rec_stack.append(rec)  # reconstructed image data 2D array (X*Y)
        energy = h5[entry[0]]['instrument_1']['source_1']['energy'][()]
        energy_stack.append(energy)      # energy in Joule
        energy_eV_stack.append(energy/e)
        wavelength_stack.append(speed_of_light/energy)
        #TODO since pixelsize is different for each energy --> one coord system needs to be defined (resize all to largest pixels?)
        corner_x, corner_y, corner_z = h5['/entry_1/instrument_1/detector_1/corner_position'][()]
        pxsize_stack.append(rec_psize_nm(energy, corner_x, corner_y, corner_z))

        # det_psize_x = h5[entry[0]]['instrument_1']['detector_1']['x_pixel_size'][()]
        # det_psize_y = h5[entry[0]]['instrument_1']['detector_1']['y_pixel_size'][()]
        # det_psize_x_stack.append(det_psize_x)
        # det_psize_y_stack.append(det_psize_y)

        coords_x = []
        coords_y = []
        for i in range(dim_x):
            coords_x.append(pxsize_stack[0]*i)
        for i in range(dim_y):
            coords_y.append(pxsize_stack[0]*i)
        coords_x_stack.append(np.asarray(coords_x))
        coords_y_stack.append(np.asarray(coords_y))
        # translation = h5['entry_1']['data_1']['translation'][()]  # positions of diffraction patterns

    recs = np.asarray(rec_stack)

    ### Create data array
    xarray = DataArray(rec_stack, dims=('E', 'y in [nm]', 'x in [nm]'), coords=[energy_eV_stack, coords_x, coords_y])
    xarray_sortE = xarray.sortby('E')
    dask_data = da.from_array(xarray_sortE)

    return energy_eV_stack, recs, pxsize_stack, xarray, dask_data

    ### describe projections and create databroker run catalog (=run_bundle)
    projections = [('NXcxi_ptycho',
                        {'entry_1/data_1/data': ('primary', 'raw'),
                         'entry_1/instrument_1/source_1/energy': energy,
                         #TODO how to define sample coords from cxi
                         'entry_1/instrument_1/detector_1/x_pixel_size': sample_x,
                         'entry_1/instrument_1/detector_1/y_pixel_size': sample_y})]

    # Compose bluesky run
    run_bundle = event_model.compose_run()  # type: event_model.ComposeRunBundle
    #Create start document
    start_doc = run_bundle.start_doc
    start_doc["sample_name"] = Path(paths[0]).resolve().stem
    start_doc["projections"] = projections
    yield 'start', start_doc

    # Compose descriptor
    source = 'nx_cxi'
    frame_data_keys = {'raw': {'source': source,
                               'dtype': 'number',
                               'dims': xarray.dims,
                               # 'coords': [energy, sample_y, sample_x],
                               'shape': data.shape}}
    frame_stream_name = 'primary'
    frame_stream_bundle = run_bundle.compose_descriptor(data_keys=frame_data_keys,
                                                        name=frame_stream_name,
                                                        # configuration=_metadata(path)
                                                        )
    yield 'descriptor', frame_stream_bundle.descriptor_doc

    yield 'event', frame_stream_bundle.compose_event(data={'raw': dask_data},
                                                     timestamps={'raw': time.time()})
    #create stop document
    yield 'stop', run_bundle.compose_stop()


if __name__ == '__main__':
    ingest_cxi('/Users/jreinhardt/Data/ALS/NS_200805056_full.cxi')