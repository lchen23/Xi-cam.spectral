from setuptools import setup, find_namespace_packages
from codecs import open
from os import path

__version__ = "0.1.0"

here = path.abspath(path.dirname(__file__))

# Get the long description from the README file
with open(path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

# get the dependencies and installs
with open(path.join(here, "requirements.txt"), encoding="utf-8") as f:
    all_reqs = f.read().split("\n")

install_requires = [x.strip() for x in all_reqs if "git+" not in x]
dependency_links = [x.strip().replace("git+", "") for x in all_reqs if x.startswith("git+")]

setup(
    name="xicam.spectral",
    version=__version__,
    description="",
    long_description=long_description,
    url="",
    license="BSD",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
    ],
    keywords="Xi-cam, spectral",
    packages=find_namespace_packages(exclude=["docs", "tests*"]),
    include_package_data=True,
    author="Ron Pandolfi",
    install_requires=install_requires,
    dependency_links=dependency_links,
    author_email="ronpandolfi@lbl.gov",
    entry_points={
        "xicam.plugins.GUIPlugin": ["spectral = xicam.spectral:SpectralPlugin"],
        "xicam.plugins.OperationPlugin": ['pca = xicam.spectral.operations.decomposition:pca',
                                          'nmf = xicam.spectral.operations.decomposition:nmf',
                                          'umap = xicam.spectral.operations.decomposition:umap',
                                          'kmeans = xicam.spectral.operations.clustering:kmeans',
                                          'standard_scaler = xicam.spectral.operations.normalization:standard_scaler',
                                          'normalizer = xicam.spectral.operations.normalization:normalizer'],
        "databroker.ingestors": ["application/x-hdf5 = xicam.spectral.ingestors.nxSTXM:ingest_nxSTXM",
                                 'application/x-fits = xicam.spectral.ingestors.arpes_fits:ingest_NXarpes',
                                 'application/x-cxi = xicam.spectral.ingestors:ingest_cxi'],
        # "databroker.handlers": [
        #     "JPEG = xicam.catalog_viewer.image_handlers:JPEGHandler",
        #     "TIFF = xicam.catalog_viewer.image_handlers:TIFFHandler",
        #     "EDF = xicam.catalog_viewer.image_handlers:EDFHandler",
        # ],
    },
)
