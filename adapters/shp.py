import os
import tempfile
import shutil

from property_transformation import get_transformed_properties
from utils import get_compressed_file_wrapper

import fiona
from . import fiona_dataset


def read(fp, prop_map, filterer=None, source_filename=None, layer_name=None):
    """Read shapefile.

    :param fp: file-like object
    :param prop_map: dictionary mapping source properties to output properties
    :param source_filename: Filename to read, only applicable if fp is a zip file
    """
    #search for a shapefile in the zip file, unzip if found
    unzip_dir = tempfile.mkdtemp()
    shp_name = source_filename
    zipped_file = get_compressed_file_wrapper(fp.name)

    if shp_name is None:
        for name in zipped_file.infolist():
            base, ext = os.path.splitext(os.path.basename(name.filename))
            if base.startswith("."):
                continue
            if ext == ".shp":
                if shp_name is not None:
                    raise Exception("Found multiple shapefiles in zipfile")
                shp_name = name.filename

        if shp_name is None:
            raise Exception("Found 0 shapefiles in zipfile")

    zipped_file.extractall(unzip_dir)
    zipped_file.close()

    #Open the shapefile
    with fiona.open(os.path.join(unzip_dir, shp_name)) as source:
        collection = fiona_dataset.read_fiona(source, prop_map, filterer)

    shutil.rmtree(unzip_dir)

    return collection
