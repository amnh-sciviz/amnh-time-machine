# -*- coding: utf-8 -*-

import argparse
import glob
import os
import pdf2image
from pprint import pprint
import sys

import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-dir', dest="PDF_DIR", default="downloads/annual_reports_pdf/*.pdf", help="Directory with PDF files")
parser.add_argument('-width', dest="WIDTH", default=800, type=int, help="Output image width")
parser.add_argument('-out', dest="OUTPUT_DIR", default="img/annual_reports/%s.jpg", help="Director to export files to")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing images?")
a = parser.parse_args()

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_DIR)
filenames = glob.glob(a.PDF_DIR)
fileCount = len(filenames)

rows = []
for i, fn in enumerate(filenames):
    id = os.path.basename(fn).split(".")[0]

    imageFilename = a.OUTPUT_DIR % id

    if os.path.isfile(imageFilename) and not a.OVERWRITE:
        print("%s already exists" % imageFilename)
        continue

    images = pdf2image.convert_from_path(fn, dpi=150, first_page=1, last_page=1)
    if len(images) > 0:
        image = images[0]
        w, h = image.size
        outWidth = a.WIDTH
        outHeight = int(round(1.0 * outWidth / (1.0 * w / h)))
        image = image.resize((w, h))
        image.save(imageFilename)
        print("Created %s" % imageFilename)
    else:
        print("Could not read %s" % fn)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/fileCount*100,2))
    sys.stdout.flush()
