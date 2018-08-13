"""Methods for loading and saving mask images."""
import rasterio
from scipy.misc import imread
from skimage.filters import threshold_otsu

from ..extract import extract_features_parallel
from ..features import FeatureSet, NirNDVI
from .conversions import multipolygon2mask
from .shapefile import load_shapefile2multipolygon


def save_mask2file(mask, filename):
    """Save a mask to filename."""
    width, height = mask.shape
    with rasterio.open(
            filename,
            'w',
            driver='GTiff',
            dtype=rasterio.uint8,
            count=1,
            width=width,
            height=height) as dst:
        dst.write(mask, indexes=1)


def load_mask_from_file(filename):
    """Load a binary mask from filename into a numpy array.

    @returns mask The mask image loaded as a numpy array
    """
    mask = imread(filename)

    return mask


def load_mask_from_shapefile(filename, shape, transform):
    """Load a mask from a shapefile."""
    multipolygon, _ = load_shapefile2multipolygon(filename)
    mask = multipolygon2mask(multipolygon, shape, transform)
    return mask


def get_ndxi_mask(generator, feature=NirNDVI):
    """Compute a mask based on an NDXI feature."""
    features = FeatureSet()
    windows = ((generator.x_size, generator.y_size), )
    features.add(feature(windows=windows))

    values = extract_features_parallel(features, generator)
    values.shape = (values.shape[0], values.shape[1])

    return values < threshold_otsu(values)
