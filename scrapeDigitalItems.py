# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
import os
from pprint import pprint
import sys
from urllib.parse import urlparse

import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-url', dest="URL", default="http://lbry-web-007.amnh.org/digital/items/browse?collection=18", help="Feed url")
parser.add_argument('-uid', dest="UNIQUE_ID", default="historic", help="Unique ID for creating unique files/folders")
parser.add_argument('-fdir', dest="FEED_DIR", default="downloads/%s_digital_items_feed/", help="Directory to store item feed data")
parser.add_argument('-rdir', dest="RECORD_DIR", default="downloads/%s_digital_items/", help="Directory to store item entry data")
parser.add_argument('-idir', dest="IMAGE_DIR", default="downloads/%s_digital_items_images/", help="Directory to store images")
parser.add_argument('-tdir', dest="THUMB_DIR", default="downloads/%s_thumbnails/", help="Directory to store thumbnails")
parser.add_argument('-out', dest="META_DATA_FILE", default="data/%s_images.csv", help="Output file for metadata")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing data?")
a = parser.parse_args()

FEED_FILENAME = "feed_%s.html"
urlParts = urlparse(a.URL)
BASE_URL = urlParts.scheme + "://" + urlParts.netloc

FEED_DIR = a.FEED_DIR % a.UNIQUE_ID
RECORD_DIR = a.RECORD_DIR % a.UNIQUE_ID
THUMB_DIR = a.THUMB_DIR % a.UNIQUE_ID
IMAGE_DIR = a.IMAGE_DIR % a.UNIQUE_ID
META_DATA_FILE = a.META_DATA_FILE % a.UNIQUE_ID

# Make sure output dirs exist
io.makeDirectories([FEED_DIR, RECORD_DIR, IMAGE_DIR, THUMB_DIR, META_DATA_FILE])

metafields = ["id", "url", "title", "date", "imageUrl", "thumbUrl"]
metadata = []

page = 1
url = a.URL
while True:

    filename = FEED_FILENAME % str(page).zfill(3)
    contents = io.downloadFile(url, FEED_DIR, filename, overwrite=a.OVERWRITE)
    soup = BeautifulSoup(contents, "html.parser")
    nextLink = soup.find("a", rel="next")
    entries = soup.find_all("div", class_="item hentry")
    for i, entry in enumerate(entries):
        entryLinks = entry.find_all("a", class_="permalink")
        entryUrl = BASE_URL + entryLinks[0].get("href")
        entryId = entryLinks[0].text.strip()
        entryTitle = entryLinks[1].text.strip()
        entryThumb = entry.find("img")
        entryThumbUrl = entryThumb.get("src")
        entryFilename = entryId + ".html"
        entryContents = io.downloadFile(entryUrl, RECORD_DIR, entryFilename, overwrite=a.OVERWRITE)

        if len(entryContents) <= 0:
            print("Could not download %s" % entryUrl)
            continue

        esoup = BeautifulSoup(entryContents, "html.parser")

        # Retrieve date
        dateContainer = esoup.find("div", id="dublin-core-date")
        entryDate = dateContainer.find("p").text if dateContainer else ""

        # Retrieve image url
        imageContainer = esoup.find("div", class_="fullsize image-jpeg")
        imageLink = imageContainer.find("a", class_="fancyitem") if imageContainer else None
        entryImageUrl = imageLink.get("href") if imageLink else ""

        entryMeta = {}
        entryMeta["id"] = entryId
        entryMeta["url"] = entryUrl
        entryMeta["title"] = entryTitle
        entryMeta["date"] = entryDate
        entryMeta["imageUrl"] = entryImageUrl
        entryMeta["thumbUrl"] = entryThumbUrl

        # Download thumbnail
        thumbExt = io.getFileextFromUrl(entryThumbUrl)
        thumbFilename = entryId + thumbExt
        io.downloadBinaryFile(entryThumbUrl, THUMB_DIR, thumbFilename, overwrite=a.OVERWRITE)

        metadata.append(entryMeta)

    if nextLink:
        url = BASE_URL + nextLink.get('href')
    else:
        break

    page += 1

io.writeCsv(META_DATA_FILE, metadata, metafields)
