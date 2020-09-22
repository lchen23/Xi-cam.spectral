from .nxSTXM import ingest_nxSTXM
from .arpes_fits import ingest_NXarpes
from .NXcxi_ptycho import ingest_cxi
import mimetypes
mimetypes.add_type('application/x-fits', '.fits')
mimetypes.add_type('application/x-cxi', '.cxi')




