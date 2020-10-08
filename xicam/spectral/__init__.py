import numpy as np
from qtpy.QtWidgets import QLabel, QComboBox, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy
from xicam.core import msg
from xicam.plugins import GUIPlugin, GUILayout
from xicam.plugins.guiplugin import PanelState
from xicam.gui.widgets.imageviewmixins import XArrayView, DepthPlot, BetterTicks, BetterLayout, BetterPlots
import logging
from xicam.gui.widgets.library import LibraryWidget
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor
from databroker.core import BlueskyRun
from xicam.core.execution import Workflow
import xarray as xr


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


class CatalogViewerBlend(BetterPlots, BetterLayout, DepthPlot, XArrayView):
    def __init__(self, *args, **kwargs):
        # CatalogViewerBlend inherits methods from XArrayView and CatalogView
        # super allows us to access both methods when calling super() from Blend
        super(CatalogViewerBlend, self).__init__(*args, **kwargs)


class SpectralPlugin(GUIPlugin):
    name = "Spectral"

    def __init__(self):
        self.current_catalog = None

        # TODO: use catalogs as output of workflows
        self.current_data = None

        self.catalog_viewer = CatalogViewerBlend()
        self.library_viewer = LibraryWidget()

        self.treatment_workflow = Workflow()
        self.treatment_editor = WorkflowEditor(self.treatment_workflow,
                                               callback_slot=self.append_treatment,
                                               finished_slot=self.show_treatment,
                                               kwargs_callable=self.treatment_kwargs,
                                               execute_iterative=True)

        self.stages = {
            "Acquire": GUILayout(QWidget()),
            "Library": GUILayout(left=PanelState.Disabled, lefttop=PanelState.Disabled, center=self.library_viewer, right=self.catalog_viewer),
            "Map": GUILayout(self.catalog_viewer, right=self.treatment_editor),
            "Decomposition": GUILayout(QWidget()),
            "Clustering": GUILayout(QWidget()),
        }
        super(SpectralPlugin, self).__init__()

    def treatment_kwargs(self, workflow):

        # FIXME: Putting this here for now...
        self.current_data = None
        return {'data': project_nxSTXM(self.current_catalog)}

    def append_treatment(self, result_set):
        if self.current_data is None:
            self.current_data = result_set['data']
        else:
            self.current_data = xr.concat([self.current_data, result_set['data']], dim='E (eV)')  # FIXME do this better

    def show_treatment(self):
        self.catalog_viewer.setImage(self.current_data, reset_crosshair=True, autoRange=True)

    def appendCatalog(self, run_catalog, **kwargs):
        self.current_catalog = run_catalog
        try:
            # Apply nxSTXM projection
            xdata = project_nxSTXM(run_catalog)

            self.catalog_viewer.setImage(xdata, autoRange=True)

        except Exception as e:
            msg.logError(e)
            msg.showMessage("Unable to display: ", str(e))


