from read_roi import read_roi_zip

class ROI:
    def __init__(self, r):
        self.name = r["name"]
        self.type = r["type"]
        self.position = r["position"]
        if r["type"] == "polygon":
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