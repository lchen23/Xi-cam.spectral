import numpy as np
import xarray as xr
from databroker.in_memory import BlueskyInMemoryCatalog
from qtpy.QtWidgets import QLabel, QComboBox, QHBoxLayout, QWidget, QSpacerItem, QSizePolicy

from xicam.core import msg
from xicam.core.execution.workflow import project_intents, ingest_result_set
from xicam.core.workspace import Ensemble
from xicam.gui.models import EnsembleModel, IntentsModel
from xicam.gui.widgets.ndimageview import NDImageView
from xicam.gui.widgets.views import DataSelectorView, StackedCanvasView
from xicam.plugins import GUIPlugin, GUILayout
from xicam.plugins.guiplugin import PanelState
from xicam.gui.widgets.library import LibraryWidget
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor
from databroker.core import BlueskyRun
from xicam.core.execution import Workflow
from xicam.plugins import GUIPlugin
from ..widgets.image_viewers import CatalogViewerBlend
from ..projectors import project_nxSTXM, project_all


class SpectralBase(GUIPlugin):
    name = "Spectral"

    def __init__(self):
        self.ensemble_model = EnsembleModel()
        self.intents_model = IntentsModel()
        self.intents_model.setSourceModel(self.ensemble_model)
        self.data_selector_view = DataSelectorView()
        self.data_selector_view.setModel(self.ensemble_model)

        self.current_catalog = None

        # TODO: use catalogs as output of workflows
        self.current_data = None

        self.catalog_viewer = NDImageView()
        self.library_viewer = LibraryWidget()

        super(SpectralBase, self).__init__()

    def treatment_kwargs(self, workflow):

        # FIXME: Putting this here for now...
        self.current_data = None
        return {'data': project_all(self.current_catalog)}

    def append_treatment(self, result_set):
        if self.current_data is None:
            self.current_data = result_set['data']
        else:
            self.current_data = xr.concat([self.current_data, result_set['data']], dim='E (eV)')  # FIXME do this better

    def show_treatment(self):
        self.catalog_viewer.setImage(self.current_data, reset_crosshair=True, autoRange=True)

    def appendCatalog(self, run_catalog: BlueskyRun, **kwargs):
        # catalog.metadata.update(self.schema())
        ensemble = Ensemble()
        ensemble.append_catalog(run_catalog)
        self.ensemble_model.add_ensemble(ensemble, project_nxSTXM)

        try:
            # Apply nxSTXM projection
            xdata = project_nxSTXM(run_catalog)

            self.catalog_viewer.setData(xdata, view_dims=('y (μm)', 'x (μm)'))

        except Exception as e:
            msg.logError(e)
            msg.showMessage("Unable to display: ", str(e))

        self.current_catalog = run_catalog


class AcquireStage(SpectralBase):
    def __init__(self):
        super(AcquireStage, self).__init__()
        self.stages["Acquire"] = GUILayout(QWidget())


class LibraryStage(SpectralBase):
    def __init__(self):
        super(LibraryStage, self).__init__()
        self.stages["Library"] = GUILayout(left=PanelState.Disabled,
                                                 lefttop=PanelState.Disabled,
                                                 center=self.library_viewer,
                                                 right=self.catalog_viewer)


class MapStage(SpectralBase):
    def __init__(self):
        super(MapStage, self).__init__()

        self.canvases_view = StackedCanvasView()
        self.canvases_view.setModel(self.intents_model)

        self.preprocess_workflow = Workflow()
        self.preprocess_editor = WorkflowEditor(self.preprocess_workflow,
                                               callback_slot=self.append_result,
                                               # finished_slot=self.append_result,
                                               kwargs_callable=self.treatment_kwargs)

        self.stages["Map"] = GUILayout(self.catalog_viewer,
                                       right=self.preprocess_editor,
                                       bottom=self.canvases_view,
                                       righttop=self.data_selector_view)

    def append_result(self, *result_set):
        ensemble = Ensemble()
        doc_generator = ingest_result_set(self.preprocess_workflow, result_set)
        #### TODO: replace with Dan's push-based
        documents = list(doc_generator)
        catalog = BlueskyInMemoryCatalog()
        # TODO -- change upsert signature to put start and stop as kwargs
        # TODO -- ask about more convenient way to get a BlueskyRun from a document generator
        catalog.upsert(documents[0][1], documents[-1][1], ingest_result_set, [self.preprocess_workflow, result_set], {})
        run_catalog = catalog[-1]
        ####
        ensemble.append_catalog(run_catalog)
        self.ensemble_model.add_ensemble(ensemble, project_intents)


class ClusteringStage(SpectralBase):
    def __init__(self):
        super(ClusteringStage, self).__init__()
        self.stages["Clustering"] = GUILayout(QWidget())


class DecompositionStage(SpectralBase):
    def __init__(self):
        super(DecompositionStage, self).__init__()
        self.stages["Decomposition"] = GUILayout(QWidget())
