
from shop.correction.register import RegisterOperation
from shop.correction.filter import MedianFilterOperation, WienerFilterOperation

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
        # Add operation to the workflow
        self.add_operations(register)
        self.add_operations(wiener)
        self.add_operations(median)
        #connect one operation's output with another operation's input
        # self.add_link()

