
from pystxmtools.corrections.register import register_operation
from pystxmtools.corrections.filter import median_filter_operation, wiener_filter_operation, denoise_operation, despike_operation
from pystxmtools.corrections.optical_density import calc_opt_density_operation
from pystxmtools.corrections.fitting import lsq_fit_operation

# from ..operations.register import RegisterOperation
# from shop.correction.filter import median_filter, wiener_filter

from xicam.core.execution import Workflow

class StxmWorkflow(Workflow):
    """Example workflow that contains register frames stack"""
    def __init__(self):
        super(StxmWorkflow, self).__init__(name="STXM Workflow")

        # Create instances of operations
        register = register_operation()
        wiener = median_filter_operation()
        median = wiener_filter_operation()
        denoise = denoise_operation()
        #TODO: how can calcOD receive IO map in workflow editor
        calc_OD = calc_opt_density_operation()
        lstsq_fit = lsq_fit_operation()

        # Add operation to the workflow
        self.add_operations(register)
        self.add_operations(wiener)
        self.add_operations(median)
        self.add_operation(denoise)
        self.add_operation(calc_OD)
        self.add_operation(lstsq_fit)
        # self.auto_connect_all()
        #connect one operation's output with another operation's input
        # self.add_link()

