from fluorseg import filebrowser
from fluorseg import liffile
from fluorseg import roifile
from skimage.color import label2rgb

class Result:

    def __init__(self, lif, type = "regions"):
        self.lif = lif
        self.rois = []
        self.type = type
        self.roi_file_paths = []
        self.volumes_channel_1 = []
        self.volumes_channel_2 = []
        self.max_projects_channel_1 = []
        self.max_projects_channel_2 = []
        self.blob_count_channel_1 = []
        self.blob_count_channel_2 = []
        self.blobs_channel_1 = []
        self.blobs_channel_2 = []


def rescale(img):
    img *= (255.0 / img.max())
    return img


def extract_volumes_for_rois(dirpath):  # single lif file, many lif zips
    """returns volumes for both channels for all regions in all images in a liffile.requires a path
    to a directory containing one lif file and many roi.zip (one for each series). """

    liffiles = filebrowser.GetLifList(dirpath)
    roifiles = roifile.get_sorted_zipfile_list(dirpath)

    lif = liffile.LIFFile(liffiles[0])
    result = Result(lif, type="regions")

    max_projs_channel_one = [liffile.max_proj(z_stacks) for z_stacks in lif.channel_one_images]
    max_projs_channel_two = [liffile.max_proj(z_stacks) for z_stacks in lif.channel_two_images]

    for i in range(lif.img_count):
        roi_info = roifile.ROIFile(roifiles[i][1])
        result.rois.append(roi_info)
        result.roi_file_paths.append(roifiles[i][1])

        mp1 = rescale(max_projs_channel_one[i])
        mp2 = rescale(max_projs_channel_two[i])

        result.max_projects_channel_1.append(mp1)
        result.max_projects_channel_2.append(mp2)

        vols1 = []
        vols2 = []

        for r in roi_info.rois:
            vols1.append(liffile.get_region_volume(mp1, r))
            vols2.append(liffile.get_region_volume(mp2, r))

        result.volumes_channel_1.append(vols1)
        result.volumes_channel_2.append(vols2)

    return result


def extract_small_blob_count(dirpath, quantile = 0.99, min_size = 4):
    """returns images and blob counts for all images in a liffile. Requires a path to a directory containing one lif file.

    quantile = 0.99, the boundary of image intensity at which pixels are retained (ie top one percent of brightest pixels)
    min_size = 4,  the size of the smallest object to keep
    """

    liffiles = filebrowser.GetLifList(dirpath)
    lif = liffile.LIFFile(liffiles[0])
    result = Result(lif, type="endosomes")
    result.max_projects_channel_1 = [ liffile.max_proj(z_stacks) for z_stacks in lif.channel_one_images ]
    result.blobs_channel_1 = [liffile.find_blobs(mp, quantile, min_size) for mp in result.max_projects_channel_1 ]
    result.blob_count_channel_1 = [liffile.count_blobs(bi) for bi in result.blobs_channel_1 ]
    return result

def as_csv(result):

    if result.type == "regions":
        return( region_csv(result) )
    elif result.type == "blobs":
        return( blob_csv(result) )


def region_csv(result):
    csv = [["lif_file", "regions_file", "region_index", "region_name", "channel_1_region_volume", "channel_2_region_volume"]]
    for i in range(result.lif.img_count):
        rois = result.rois[i]
        for j, r in enumerate(rois.rois):
            csv.append([result.lif.path, result.roi_file_paths[i], j + 1, r.name, result.volumes_channel_1[i][j], result.volumes_channel_2[i][j]])
    return csv


def blob_csv(result):
    csv = (["lif_file", "series", "channel_1_endosome_count"])
    for i in range(result.lif.img_count):
        csv.append([result.lif.path, i, result.blob_count_channel_1])
    return csv
