===========
FluorSeg
===========

FlourSeg provides such and such and so and so. You might find
it most useful for tasks involving <x> and also <y>. Typical usage
often looks like this::

    #!/usr/bin/env python

    from fluorseg import liffile
    from fluorseg import roifile

    lif = liffile.LIFFile(path)

    #show the path
    print(lif.path)

    #show the metadata xml object
    print(lif.xml_root)

    #show the number of images in the file
    print(lif.img_count)

    #show the number of layers in each zstack for each image
    print(lif.z_stack_count)

    #show the first image's, 2nd zstack layer
    print(type(lif.combined_channel_images[0][1]))

    #show the type first channel of the first image's 2nd z-stack layer - each data array is a numpy ndarray
    # they are held in nested lists => [image index][z_stack index]
    print(type(lif.channel_one_images[0][1]))

    #plot the second channel of the first image's 1st z-stack layer [image index][z_stack index]
    plt.imshow(lif.channel_two_images[0][0], interpolation='nearest')
    plt.show()

    #get the maximum projection of each images z-stack for each image
    max_projs_channel_one = [liffile.max_proj(z_stacks) for z_stacks in lif.channel_one_images]
    max_projs_channel_two = [liffile.max_proj(z_stacks) for z_stacks in lif.channel_two_images]

    #plot the first max_proj
    plt.imshow(max_projs_channel_one[0], interpolation='nearest')
    plt.show()

    plt.imshow(max_projs_channel_two[0], interpolation='nearest')
    plt.show()

    #get the region of interest info
    roi_info = roifile.ROIFile(roi_zip_path) #roi for series 001 only

    #make the mask for the second region of interest - a polygon
    mask = make_polygon_mask(roi_info.rois[1], 512, 512)

    #make the mask for the 5th region of interest - an ellipse
    oval_mask = make_oval_mask(roi_info.rois[4], 512,512)

    #just get the volume in a region of interest - masking done for you
    series1_mp_c2 = max_projs_channel_two[0]
    get_region_volume(series1_mp_c2, roi_info.rois[4])



(Note the double-colon and 4-space indent formatting above.)

Paragraphs are separated by blank lines. *Italics*, **bold**,
and ``monospace`` look like this.


A Section
=========

Lists look like this:

* First

* Second. Can be multiple lines
  but must be indented properly.

A Sub-Section
-------------

Numbered lists look like you'd expect:

1. hi there

2. must be going

Urls are http://like.this and links can be
written `like this <http://www.example.com/foo/bar>`_.