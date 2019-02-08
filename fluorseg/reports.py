import numpy as np
from PIL import Image
from io import BytesIO
import base64
from fluorseg import liffile
from skimage.color import label2rgb
from skimage.measure import label
import math

def make_overlay_base64(img, roi):
    width, height = img.shape
    mask = None
    if roi.type in ["polygon", "freehand"]:
        mask = liffile.make_polygon_mask(roi, width, height, outline=255, fill=255)
    elif roi.type == "oval":
        mask = liffile.make_oval_mask(roi, width, height, outline=255, fill=255)
    img = np.uint8(img)
    img = Image.fromarray(img).convert("RGBA")

    mask = np.uint8(mask)
    overlay = Image.fromarray(mask).convert("RGBA")
    final_img = Image.blend(img, overlay, alpha=.3)
    return make_base64(final_img)


def make_base64(img):
    img = np.uint8(img)
    h, w  = img.shape[0:2]
    buffer = BytesIO()
    final_img = Image.fromarray(img)
    final_img = final_img.resize( (math.floor(w / 2.0), math.floor(h / 2.0) ))
    final_img = final_img.quantize(method=2)

    final_img.save(buffer, format="PNG")
    output = buffer.getvalue()

    return "data:image/png;base64," + base64.b64encode(output).decode('utf8')


def rescale(img):
    new_img = img * (255 / img.max())
    return new_img


class HtmlReport:

    def __init__(self, result):
        self.preamble = '''<!DOCTYPE html>
        <head>
            <title>Image Mask Preview</title>
            <style>
            img {
            padding:10px;
            }
            </style>
        </head>
        <body>
        <h2> Report for image ''' + result.lif.path + '''</h2>
        '''
        if result.type == "regions":
            self.table = self.make_roi_table(result)
        elif result.type == "blobs":
            self.table = self.make_blob_table(result)
        self.footer = self.footer()

    def make_roi_table(self, result):
        rows = []
        for i in range(result.lif.img_count):
            title = "<h3>{0}</h3>".format(result.roi_file_paths[i])
            # base_64_imgs1 = []
            base_64_imgs_c2 = []
            for j, r in enumerate(result.rois[i].rois):
                # base_64_imgs1.append( make_overlay_base64(rescale(result.max_projects_channel_1[i]), r) )
                base_64_imgs_c2.append(make_overlay_base64(rescale(result.max_projects_channel_2[i]), r))

                # make channel

            img_row = "<div>" + title + "<img src='" + "' /><img src='".join(base_64_imgs_c2) + "'/></div>\n"
            rows.append(img_row)

        return rows


    def make_blob_table(self,result):
        if result.rois:
            rows = []
            for i in range(result.lif.img_count):
                title = "<h3>{0}</h3>".format(result.roi_file_paths[i])
                base_64_imgs = []
                base_64_imgs.append(
                    make_base64(rescale(
                        label2rgb(label(result.blobs_channel_1[i]),
                                                                  image=result.max_projects_channel_1[i]
                                          )
                                )
                                )
                )

                for j, r in enumerate(result.rois[i].rois):
                    base_64_imgs.append( make_overlay_base64(rescale(result.max_projects_channel_1[i]), r) )

                    # make channel

                img_row = "<div>" + title + "<img src='" + "' /><img src='".join(base_64_imgs) + "'/></div>\n"
                rows.append(img_row)

            return rows

        else:
            rows = []
            for i in range(result.lif.img_count):
                title = "<h3>Series {0}</h3>".format(i + 1)
                img_row = title + "<img src='" + \
                          make_base64(rescale(label2rgb(label(result.blobs_channel_1[i]), image=result.max_projects_channel_1[i].astype('uint8')))) + \
                          "' />" + \
                        "<img src='" + make_base64(rescale(result.max_projects_channel_1[i])) + "' />"
                if result.cell_area_masks_channel_1:
                    b64_img = result.cell_area_masks_channel_1[i] * 255
                    img_row += "<img src='" + make_base64(b64_img)  + "' />"
                rows.append(img_row)
            return rows



    def footer(self):
        return "</body>"

    def write_html(self):
        return self.preamble + "".join(self.table) + self.footer
