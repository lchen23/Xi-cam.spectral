import numpy as np
from qtpy.QtWidgets import QLabel, QComboBox, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy
from xicam.core import msg
from xicam.plugins import GUIPlugin, GUILayout
from xicam.plugins.guiplugin import PanelState
from xicam.gui.widgets.imageviewmixins import XArrayView, CatalogView, StreamSelector, BetterPlots, \
    FieldSelector, BetterLayout, DepthPlot  # , DepthPlot, BetterTicks, BetterLayout, BetterPlots,
from xicam.core.intents import ImageIntent
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


class CatalogViewerBlend(BetterPlots, BetterLayout, DepthPlot, XArrayView):
    def __init__(self, *args, **kwargs):
        # CatalogViewerBlend inherits methods from XArrayView and CatalogView
        # super allows us to access both methods when calling super() from Blend
        super(CatalogViewerBlend, self).__init__(*args, **kwargs)


class SpectralPlugin(GUIPlugin):
    name = "Spectral"

    def __init__(self):
        self.current_catalog = None
        self.current_raw = None

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
        return {'data': self.current_raw}

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
            # Apply projections
            intents = project_all(run_catalog)

            self.current_raw = intents[0].image

            self.catalog_viewer.setImage(self.current_raw, autoRange=True)

        except Exception as e:
            msg.logError(e)
            msg.showMessage("Unable to display: ", str(e))
