from xicam.gui.widgets.imageviewmixins import XArrayView, DepthPlot, BetterTicks, BetterLayout, BetterPlots


class CatalogViewerBlend(BetterPlots, BetterLayout, DepthPlot, XArrayView):
    def __init__(self, *args, **kwargs):
        # CatalogViewerBlend inherits methods from XArrayView and CatalogView
        # super allows us to access both methods when calling super() from Blend
        super(CatalogViewerBlend, self).__init__(*args, **kwargs)