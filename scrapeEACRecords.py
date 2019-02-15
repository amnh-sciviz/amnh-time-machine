# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
import os
from pprint import pprint
import sys

import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-url', dest="URL", default="http://data.library.amnh.org/archives-authorities/feed/?q=*:*", help="Feed url")
parser.add_argument('-fdir', dest="FEED_DIR", default="downloads/eac_feed/", help="Directory to store EAC feed data")
parser.add_argument('-rdir', dest="RECORD_DIR", default="downloads/eac_records/", help="Directory to store EAC record data")
parser.add_argument('-rformat', dest="RECORD_FILEFORMAT", default=".xml", help="Record file format (.jsonld, .xml, , .rdf, .kml)")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing data?")
a = parser.parse_args()

FEED_FILENAME = "feed_%s.xml"

# Make sure output dirs exist
io.makeDirectories([a.FEED_DIR, a.RECORD_DIR])

page = 1
url = a.URL
while True:

    filename = FEED_FILENAME % str(page).zfill(3)
    contents = io.downloadFile(url, a.FEED_DIR, filename, overwrite=a.OVERWRITE)
    soup = BeautifulSoup(contents, "html.parser")
    nextLink = soup.find("link", rel="next")

    entries = soup.find_all("entry")
    for i, entry in enumerate(entries):
        entryUrl = entry.find("link").get("href") + a.RECORD_FILEFORMAT
        entryId = entry.find("id").string
        entryFilename = entryId + ".json" if a.RECORD_FILEFORMAT == ".jsonld" else entryId + a.RECORD_FILEFORMAT
        io.downloadFile(entryUrl, a.RECORD_DIR, entryFilename, overwrite=a.OVERWRITE)

    if nextLink:
        url = nextLink.get('href')
    else:
        break

    page += 1
