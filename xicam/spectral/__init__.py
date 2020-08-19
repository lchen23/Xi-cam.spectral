import numpy as np
from qtpy.QtWidgets import QLabel, QComboBox, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy
from xicam.core import msg
from xicam.plugins import GUIPlugin, GUILayout
from xicam.plugins.guiplugin import PanelState
from xicam.gui.widgets.imageviewmixins import XArrayView, DepthPlot, BetterTicks, BetterLayout, BetterPlots
import logging
from xicam.gui.widgets.library import LibraryWidget
from databroker.core import BlueskyRun
from xarray import DataArray


def project_nxSTXM(run_catalog: BlueskyRun):
    _, projection = next(filter(lambda projection: projection[0] == 'nxSTXM', run_catalog.metadata['start']['projections']))
    stream, field = projection['irmap/DATA/data']
    sample_x = projection['irmap/DATA/sample_x']
    sample_y = projection['irmap/DATA/sample_y']
    energy = projection['irmap/DATA/energy']

    xdata = getattr(run_catalog, stream).to_dask()[field]  # type: DataArray

    xdata = np.squeeze(xdata)

    xdata = xdata.assign_coords({xdata.dims[0]: energy, xdata.dims[1]: sample_y, xdata.dims[2]: sample_x})

    return xdata


class CatalogViewerBlend(BetterPlots, BetterLayout, DepthPlot, XArrayView):
    def __init__(self, *args, **kwargs):
        # CatalogViewerBlend inherits methods from XArrayView and CatalogView
        # super allows us to access both methods when calling super() from Blend
        super(CatalogViewerBlend, self).__init__(*args, **kwargs)


class SpectralPlugin(GUIPlugin):
    name = "Spectral"

    def __init__(self):
        self.catalog_viewer = CatalogViewerBlend()
        self.library_viewer = LibraryWidget()
        self.stages = {
            "Acquire": GUILayout(QWidget()),
            "Library": GUILayout(left=PanelState.Disabled, lefttop=PanelState.Disabled, center=self.library_viewer, right=self.catalog_viewer),
            "Map": GUILayout(self.catalog_viewer),
            "Decomposition": GUILayout(QWidget()),
            "Clustering": GUILayout(QWidget()),
        }
        super(SpectralPlugin, self).__init__()

    def appendCatalog(self, run_catalog, **kwargs):
        try:
            self.stream_fields = get_all_image_fields(run_catalog)
            stream_names = get_all_streams(run_catalog)

            msg.showMessage(f"Loading primary image for {run_catalog.name}")
            # # try and startup with primary catalog and whatever fields it has
            # if "primary" in self.stream_fields:
            #     default_stream_name = "primary" if "primary" in stream_names else stream_names[0]
            # else:
            #     default_stream_name = list(self.stream_fields.keys())[0]

            # Apply nxSTXM projection
            xdata = project_nxSTXM(run_catalog)

            self.catalog_viewer.setImage(xdata)

        except Exception as e:
            msg.logError(e)
            msg.showMessage("Unable to display: ", str(e))


### small helper functions
def get_stream_data_keys(run_catalog, stream):
    return run_catalog[stream].metadata["descriptors"][0]["data_keys"]


def get_all_streams(run_catalog):
    return list(run_catalog)


def get_all_image_fields(run_catalog):
    # image_fields = []
    all_streams_image_fields = {}
    for stream in get_all_streams(run_catalog):
        stream_fields = get_stream_data_keys(run_catalog, stream)
        field_names = stream_fields.keys()
        for field_name in field_names:
            field_shape = len(stream_fields[field_name]["shape"])
            if field_shape > 1 and field_shape < 5:
                # if field contains at least 1 entry that is at least one-dimensional (shape=2)
                # or 2-dimensional (shape=3) or up to 3-dimensional (shape=4)
                # then add field e.g. 'fccd_image'
                if stream in all_streams_image_fields.keys():  # add values to stream dict key
                    all_streams_image_fields[stream].append(field_name)
                else:  # if stream does not already exist in dict -> create new entry
                    all_streams_image_fields[stream] = [field_name]
            # TODO how to treat non image data fields in streams
            # else:
    return all_streams_image_fields


# Problem: primary image field does not show up anymore...
# Problem: primary image field does not show up anymore...
