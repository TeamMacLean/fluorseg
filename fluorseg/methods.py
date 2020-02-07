from fluorseg import filebrowser
from fluorseg import liffile
from fluorseg import roifile
import numpy as np
from skimage.color import label2rgb

class Result:

    def __init__(self, lif, type="regions"):
        self.lif = lif
        self.rois = []
        self.type = type
        self.roi_file_paths = []
        self.volumes_channel_1 = []
        self.volumes_channel_2 = []
        self.unscaled_volumes_channel_1 = []
        self.unscaled_volumes_channel_2 = []
        self.max_projects_channel_1 = []
        self.max_projects_channel_2 = []
        self.blob_count_channel_1 = []
        self.blob_count_channel_2 = []
        self.blobs_channel_1 = []
        self.blobs_channel_2 = []
        self.cell_area_masks_channel_1 = []
        self.cell_areas_channel_1 = []
        self.qs = []
        self.roi_areas = []


def rescale(img):
    img = img * (255.0 / img.max())
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

        unscaled_mp1 = max_projs_channel_one[i]
        unscaled_mp2 = max_projs_channel_two[i]
#        print("unscaled")
#        print(unscaled_mp1.sum())
        scaled_mp1 = rescale(unscaled_mp1)
        scaled_mp2 = rescale(unscaled_mp2)
#        print("scaled")
#        print(scaled_mp1.sum())
        result.max_projects_channel_1.append(scaled_mp1)
        result.max_projects_channel_2.append(scaled_mp2)

        unscaled_vols1 = []
        unscaled_vols2 = []

        vols1 = []
        vols2 = []

        areas = []


        for r in roi_info.rois:
            unscaled_vols1.append(liffile.get_region_volume(unscaled_mp1, r))
            unscaled_vols2.append(liffile.get_region_volume(unscaled_mp2, r))

            vols1.append(liffile.get_region_volume(scaled_mp1, r))
            vols2.append(liffile.get_region_volume(scaled_mp2, r))

            areas.append(liffile.roi_area(unscaled_mp1,r))
#        print(vols1)
        result.volumes_channel_1.append(vols1)
        result.volumes_channel_2.append(vols2)
#        print(result.volumes_channel_2)
        result.unscaled_volumes_channel_1.append(unscaled_vols1)
        result.unscaled_volumes_channel_2.append(unscaled_vols2)

        result.roi_areas.append(areas)



    return result


def extract_small_blob_count(dirpath, quantile = 0.99,
                             min_size = 4, guess_cell_area = False,
                             guess_cell_area_min_i=30
                             ):
    """returns images and blob counts for all images in a liffile. Requires a path to a directory containing one lif file.

    quantile = 0.99, the boundary of image intensity at which pixels are retained (ie top one percent of brightest pixels)
    min_size = 4,  the size of the smallest object to keep
    """

    liffiles = filebrowser.GetLifList(dirpath)

    roifiles = roifile.get_sorted_zipfile_list(dirpath)

    lif = liffile.LIFFile(liffiles[0])
    result = Result(lif, type="blobs")

    result.max_projects_channel_1 = [ liffile.max_proj(z_stacks) for z_stacks in lif.channel_one_images ]
    result.blobs_channel_1 = [liffile.find_blobs(mp, quantile, min_size) for mp in result.max_projects_channel_1 ]

    if roifiles:
        for i in range(lif.img_count):
            roi_info = roifile.ROIFile(roifiles[i][1])
            result.rois.append(roi_info)
            result.roi_file_paths.append(roifiles[i][1])

            blobs = []

            for j,r in enumerate(roi_info.rois):
                blobs.append(liffile.get_region_count(result.blobs_channel_1[i], r))

            result.blob_count_channel_1.append(blobs)
    else:
        result.blob_count_channel_1 = [liffile.count_blobs(img) for img in result.blobs_channel_1]

        if guess_cell_area:
            result.cell_area_masks_channel_1 = [liffile.make_cell_area_mask(img, guess_cell_area_min_i, 255) for img in result.max_projects_channel_1]
            result.cell_areas_channel_1 = [np.sum(mask) for mask in result.cell_area_masks_channel_1 ]

    return result

def as_csv(result):

    if result.type == "regions":
        return( region_csv(result) )
    elif result.type == "blobs":
        return( blob_csv(result) )


def region_csv(result):
    csv = [["lif_file", "regions_file", "region_index", "region_name", "channel_1_region_volume", "channel_2_region_volume", "channel_1_unscaled_region_volume", "channel_2_unscaled_region_volume", "region_area"]]
    for i in range(result.lif.img_count):
        rois = result.rois[i]
        for j, r in enumerate(rois.rois):
            csv.append([result.lif.path, result.roi_file_paths[i], j + 1, r.name, result.volumes_channel_1[i][j], result.volumes_channel_2[i][j], result.unscaled_volumes_channel_1[i][j], result.unscaled_volumes_channel_2[i][j], result.roi_areas[i][j] ] )
    return csv


def blob_csv(result):
    if result.rois:
        csv = [["lif_file", "region_file", "series", "region_index", "region_name", "region_endosome_count"]]
        for i in range(result.lif.img_count):
            rois = result.rois[i]
            for j, r in enumerate(rois.rois):
                csv.append([result.lif.path, result.roi_file_paths[i], i + 1, j + 1, r.name, result.blob_count_channel_1[i][j]])
        return csv
    else:
        csv = [["lif_file",  "series", "channel_1_endosome_count", "cell_area"]]
        for i in range(result.lif.img_count):
            csv.append([result.lif.path, i + 1, result.blob_count_channel_1[i], result.cell_areas_channel_1[i] ])
        return csv

