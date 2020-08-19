
from shop.correction.register import RegisterOperation
from shop.correction.filter import MedianFilterOperation, WienerFilterOperation, Denoise, Despike
from shop.correction.opitcal_density import CalcOpticalDensity

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
        calcOD = CalcOpticalDensity()
        # Add operation to the workflow
        self.add_operations(register)
        self.add_operations(wiener)
        self.add_operations(median)
        self.add_operation(denoise)
        self.add_operation(calcOD)
        #connect one operation's output with another operation's input
        # self.add_link()

