from read_roi import read_roi_zip
import re
from fluorseg import filebrowser
import sys

class ROI:
    def __init__(self, r):
        self.name = r["name"]
        self.type = r["type"]
        self.position = r["position"]
        if r["type"] in ["polygon", "freehand"]:
            self.x = r["x"]
            self.y = r["y"]
            self.n = r["n"]
        elif r["type"] == "oval":
            self.left = r["left"]
            self.top = r["top"]
            self.width = r["width"]
            self.height = r["height"]


class ROIFile:
    def __init__(self, path):
        self.path = path
        self.raw_rois = read_roi_zip(path)
        self.region_names = [name for name, data in self.raw_rois.items()]
        self.rois = []

        for r in self.region_names:
            self.rois.append(ROI(self.raw_rois[r]))


def get_sorted_zipfile_list(dirpath):
    '''makes a sorted list of all roi.zips. Requires zips to be named with suffix SeriesXXX.zip'''
    zips = filebrowser.GetROIZIPList(dirpath)
    if zips:
        series_ids = [int(re.search(".*Series(\d+)\.zip", i).group(1)) for i in zips]
        return sorted(list(zip(series_ids, zips)))
    else:
        return []
