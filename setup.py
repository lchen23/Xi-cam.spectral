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
        "databroker.ingestors": ["application/x-hdf5 = xicam.spectral.ingestors:ingest_nxSTXM"],
        "xicam.plugins.OperationPlugin": ["wiener_filter = pystxmtools.corrections.filter:WienerFilterOperation",
                                          "median_filter = pystxmtools.corrections.filter:MedianFilterOperation",
                                          "nl_means_filter = pystxmtools.corrections.filter:nlMeansFilter",
                                          "despike = pystxmtools.corrections.filter:Despike",
                                          "denoise = pystxmtools.corrections.filter:Denoise",
                                          "calc_optical_density = pystxmtools.corrections.optical_density:CalcOpticalDensity",
                                          "get_I0_mask = pystxmtools.corrections.optical_density:CalcI0Mask",
                                          "register_stack = pystxmtools.corrections.register:RegisterOperation",
                                          "lin_fit_spectra = pystxmtools.corrections.fitting:LinFitSpectra",
                                          "lstsq_fit = pystxmtools.corrections.fitting:LeastSquaresFit",
                                          "nn_lstsq = pystxmtools.corrections.fitting:NNLeastSquaresFit"]
        # "databroker.handlers": [
        #     "JPEG = xicam.catalog_viewer.image_handlers:JPEGHandler",
        #     "TIFF = xicam.catalog_viewer.image_handlers:TIFFHandler",
        #     "EDF = xicam.catalog_viewer.image_handlers:EDFHandler",
        # ],
    },
)
