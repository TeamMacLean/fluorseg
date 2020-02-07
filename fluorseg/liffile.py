import xml.etree.ElementTree as ET
import javabridge
import bioformats
javabridge.start_vm(class_path=bioformats.JARS)
import numpy as np
from PIL import Image, ImageDraw
from skimage.filters import sobel
from skimage import morphology
from scipy import ndimage as ndi


def get_xml(path):
    '''gets OMEXML metadata as python ETree object'''
    raw_xml = bioformats.get_omexml_metadata(path)
    root = ET.fromstring(raw_xml)
    return (root)


def count_images(root):
    '''estimate image number in the lif file'''
    image_list = [x for x in root.iter('{http://www.openmicroscopy.org/Schemas/OME/2016-06}Image')]
    return (len(image_list))


def collect_images(path, img_count, z_stacks):
    '''gets images from a lif file into a list of lists of numpy arrays.
       Each numpy array is a z layer, each list of z layers is
    '''
    return [load_img(path, i, z_stacks[i]) for i in range(img_count)]


def load_img(path, series, z_max):
    '''gets all z-stacks in an image'''
    all_z_in_image = [bioformats.load_image(path, series=series, z=z) for z in range(z_max)]
    return (all_z_in_image)


def get_image_xml_meta(root):
    '''gets all Image XML information from ETree root object. Returns list'''
    img_el = root.findall("{http://www.openmicroscopy.org/Schemas/OME/2016-06}Image")
    return img_el


def get_z_plane_count(img_el):
    '''returns the number of planes in the z-stack for an image given the image element'''
    count_string = img_el.findall("{http://www.openmicroscopy.org/Schemas/OME/2016-06}Pixels[@SizeZ]")[0].attrib[
        'SizeZ']
    return int(count_string)


def extract_channel_one(ndarray_list):
    '''returns the first channel data from list of numpyndarrays '''
    return [a[:, :, 0] for a in ndarray_list]


def extract_channel_two(ndarray_list):
    '''returns the second channel data from list of numpyndarrays '''
    return [a[:, :, 1] for a in ndarray_list]


def max_proj(image_list):
    '''returns a single maximum projected image from a list of images'''
    return np.maximum.reduce(image_list)


def make_polygon_mask(roi, width, height, outline = 1, fill = 1):
    polygon = list(zip(roi.x, roi.y))
    img = Image.new('L', (width, height), 0)
    ImageDraw.Draw(img).polygon(polygon, outline=outline, fill=fill)
    return np.array(img)


def make_oval_mask(roi, width, height, outline = 1, fill = 1):
    ellipse = [roi.left, roi.top, roi.left + roi.width, roi.top + roi.height]
    img = Image.new('L', (width, height), 0)
    ImageDraw.Draw(img).ellipse(ellipse, outline=outline, fill=fill)
    return np.array(img)


def mask_with_roi(image, roi, binary = False):
    width, height = image.shape
    mask = None
    if roi.type in ["polygon", "freehand"]:
        mask = make_polygon_mask(roi, width, height)
    elif roi.type == "oval":
        mask = make_oval_mask(roi, width, height)
    if binary:
        return np.ones_like(image) * mask
    return image * mask

def roi_area(image, roi):
    return mask_with_roi(image, roi, binary=True).sum()

def get_region_volume(image, roi):
    masked = mask_with_roi(image, roi)
    return masked.sum()

def get_region_pixel_count(image, roi):
    mask = mask_with_roi(image, roi, binary = True)
    return mask.sum()


def get_region_count(image, roi):
    masked = mask_with_roi(image, roi)
    return count_blobs(masked)


def find_blobs(img, quantile = 0.99, min_size = 4):
    try:
        cutoff = np.quantile(img, quantile)
        mask = img > cutoff
        masked = img * mask
        markers = np.zeros_like(masked)
        markers[masked == 0 ] = 1
        markers[masked > cutoff ] = 2
        elevation_map = sobel(masked)
        segmentation = morphology.watershed(elevation_map, markers)
        segmentation[segmentation == 1] = 0
        labeled_bits, _ = ndi.label(segmentation)
        no_small = morphology.remove_small_objects(labeled_bits, min_size)
        no_small[no_small > 0] = 1
        return no_small
    except RuntimeWarning:
        return np.zeros_like(img)


def count_blobs(img):
    _, count = ndi.label(img)
    return(count)


def make_cell_area_mask(img, low_i, high_i):
    img *= (255.0 / img.max())
    mask = np.logical_and(img > low_i, img < high_i) * 1
    mask = ndi.binary_fill_holes(mask).astype(int)
    return mask




class LIFFile:
    def __init__(self, path):
        self.path = path
        self.xml_root = get_xml(path)
        self.img_count = count_images(self.xml_root)
        self.image_xml_meta = get_image_xml_meta(self.xml_root)
        self.z_stack_count = [get_z_plane_count(el) for el in self.image_xml_meta]
        self.combined_channel_images = collect_images(path, self.img_count, self.z_stack_count)
        self.channel_one_images = [extract_channel_one(a) for a in self.combined_channel_images]
        self.channel_two_images = [extract_channel_two(a) for a in self.combined_channel_images]
