from qtpy.QtWidgets import QLabel, QComboBox, QHBoxLayout, QWidget, QSpacerItem,
from xicam.gui.widgets.linearworkfloweditor import WorkflowEditor
from xicam.plugins import GUIPlugin, GUILayout
from .workflows.workflows import MapWorkflow

class RegisterStack(QWidget):
    name = "Register Stack Plugin"

    def __init__(self, *args, **kwargs):
        """
        """
        # self._catalog_viewer = CatalogView()  # Create a widget to view the loaded catalog
        # self._results_viewer = DynImageView()  # Create a widget to view the result image

        self._workflow = MapWorkflow()  # Create a workflow
        # Create a widget for the workflow; this shows the operations and their parameters,
        # and we can run the workflow with this widget
        self._workflow_editor = WorkflowEditor(workflow=self._workflow)
        # The WorkflowEditor emits a "sigRunWorkflow" signal when its "Run Workflow" is clicked
        # This will call our run_workflow method whenever this signal is emitted (whenever the button is clicked).
        self._workflow_editor.sigRunWorkflow.connect(self.run_workflow)

        # Create a layout to organize our widgets
        # The first argument (which corresponds to the center widget) is required.
        catalog_viewer_layout = GUILayout(self._catalog_viewer,
                                          right=self._workflow_editor,
                                          bottom=self._results_viewer)
        super(RegisterStack, self).__init__(*args, **kwargs)
