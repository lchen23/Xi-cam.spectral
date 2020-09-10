import time

import event_model
import h5py
from dask import array as da
from pathlib import Path
from xarray import DataArray


def ingest_cxi(path):

    # assert len(path) == 1
    # path = path[0]

    h5 = h5py.File(path, 'r')
    #TODO: maybe sorting not needed, since energies might be in 'random' order anyways --> sort later by energy
    h5_entry_dict = {}
    for key in h5.keys():
        if 'entry' in key:
            h5_entry_dict[key] = key.split('_')[-1].zfill(3)
    sorted_entry_list = sorted(h5_entry_dict.items(), key=lambda item: item[1])

    frames_stack = []
    rec_stack = []
    energy_stack = []
    energy_eV_stack = []
    pixel_x_stack = []
    pixel_y_stack = []
    wavelength_stack = []

    for entry in sorted_entry_list:
        # frames_stack.append(h5[entry[0]]['data_1']['data'][()])  # diffraction patterns 3D array (N*X*Y)
        rec_stack.append(h5[entry[0]]['image_1']['data'][()])  # reconstructed imnage data 2D array (X*Y)
        pixel_x_stack.append(h5[entry[0]]['instrument_1']['detector_1']['x_pixel_size'][()])
        pixel_y_stack.append(h5[entry[0]]['instrument_1']['detector_1']['y_pixel_size'][()])
        energy = h5[entry[0]]['instrument_1']['source_1']['energy'][()]
        energy_stack.append(energy)      # energy in Joule
        energy_eV_stack.append(energy/e)
        wavelength_stack.append(speed_of_light/energy)
        # translation = h5['entry_1']['data_1']['translation'][()]  # positions of diffraction patterns



    #/Users/jreinhardt/Data/ALS/NS_200805056_full.cxi"
    ### Create data array
    # #TODO energy, coords len not matching number of frames
    # xarray = DataArray(rec_stack, dims=['E (eV)', 'y (μm)', 'x (μm)'], coords=[energy_eV_stack, pixel_x_stack, pixel_x_stack])
    # dask_data = da.from_array(xarray)

    return energy_eV_stack, pixel_x_stack, pixel_y_stack, rec_stack

    # ### describe projections and create databroker run catalog (=run_bundle)
    # projections = [('NXcxi_ptycho',
    #                     {'entry_1/data_1/data': ('primary', 'raw'),
    #                      'entry_1/instrument_1/source_1/energy': energy,
    #                      #TODO how to define sample coords from cxi
    #                      'entry_1/instrument_1/detector_1/x_pixel_size': sample_x,
    #                      'entry_1/instrument_1/detector_1/y_pixel_size': sample_y}
    # )]
    #
    # # Compose bluseksy run
    # run_bundle = event_model.compose_run()  # type: event_model.ComposeRunBundle
    #
    # #Create start document
    # start_doc = run_bundle.start_doc
    # start_doc["sample_name"] = Path(paths[0]).resolve().stem
    #
    # #TODO add projections once defined
    # #start_doc["projections"] = projections
    # yield 'start', start_doc
    #
    # # Compose descriptor
    # source = 'nx_cxi'
    # frame_data_keys = {'raw': {'source': source,
    #                            'dtype': 'number',
    #                            'dims': xarray.dims,
    #                            # 'coords': [energy, sample_y, sample_x],
    #                            'shape': data.shape}}
    # frame_stream_name = 'primary'
    # frame_stream_bundle = run_bundle.compose_descriptor(data_keys=frame_data_keys,
    #                                                     name=frame_stream_name,
    #                                                     # configuration=_metadata(path)
    #                                                     )
    # yield 'descriptor', frame_stream_bundle.descriptor_doc
    #
    # yield 'event', frame_stream_bundle.compose_event(data={'raw': dask_data},
    #                                                  timestamps={'raw': time.time()})
    #
    # #create stop document
    # yield 'stop', run_bundle.compose_stop()
    #
    # # return run_bundle