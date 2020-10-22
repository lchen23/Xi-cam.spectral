from .stages import SpectralBase, MapStage, AcquireStage, LibraryStage, DecompositionStage, ClusteringStage


class SpectralPlugin(ClusteringStage, DecompositionStage, MapStage, LibraryStage, AcquireStage):
    def __init__(self):
        super(SpectralPlugin, self).__init__()


