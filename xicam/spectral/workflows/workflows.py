
from pystxmtools.corrections.register import RegisterOperation
from pystxmtools.corrections.filter import MedianFilterOperation, WienerFilterOperation, Denoise, Despike
from pystxmtools.corrections.optical_density import CalcOpticalDensity
from pystxmtools.corrections.fitting import LeastSquaresFit

# from ..operations.register import RegisterOperation
# from shop.correction.filter import median_filter, wiener_filter

from xicam.core.execution import Workflow

class StxmWorkflow(Workflow):
    """Example workflow that contains register frames stack"""
    def __init__(self):
        super(StxmWorkflow, self).__init__(name="STXM Workflow")

        # Create instances of operations
        register = RegisterOperation()
        wiener = MedianFilterOperation()
        median = WienerFilterOperation()
        denoise = Denoise()
        #TODO: how can calcOD receive IO map in workflow editor
        # calc_OD = CalcOpticalDensity()
        lstsq_fit = LeastSquaresFit()

        # Add operation to the workflow
        self.add_operations(register)
        self.add_operations(wiener)
        self.add_operations(median)
        self.add_operation(denoise)
        # self.add_operation(calc_OD)
        self.add_operation(lstsq_fit)
        # self.auto_connect_all()
        #connect one operation's output with another operation's input
        # self.add_link()

