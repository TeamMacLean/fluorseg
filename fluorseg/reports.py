import numpy as np
from PIL import Image
from io import BytesIO
import base64
from fluorseg import liffile

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

    buffer = BytesIO()
    final_img = Image.fromarray(img)
    final_img = final_img.resize((200, 200))
    final_img = final_img.quantize(method=2)

    final_img.save(buffer, format="PNG")
    output = buffer.getvalue()

    return "data:image/png;base64," + base64.b64encode(output).decode('utf8')


def rescale(img):
    img *= (255.0 / img.max())
    return img


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
        self.table = self.make_table(result)
        self.footer = self.footer()

    def make_table(self, result):
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

    def footer(self):
        return "</body>"

    def write_html(self):
        return self.preamble + "".join(self.table) + self.footer
