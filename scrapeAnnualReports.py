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
parser.add_argument('-url', dest="URL", default="http://digitallibrary.amnh.org/handle/2246/6178/recent-submissions", help="Feed url")
parser.add_argument('-fdir', dest="FEED_DIR", default="downloads/annual_reports_feed/", help="Directory to store annual report feed data")
parser.add_argument('-rdir', dest="RECORD_DIR", default="downloads/annual_reports/", help="Directory to store annual report record data")
parser.add_argument('-pdir', dest="PDF_DIR", default="downloads/annual_reports_pdf/", help="Directory to store annual report PDFs")
parser.add_argument('-idir', dest="IMAGE_DIR", default="img/annual_reports/", help="Directory to store Annual report thumbnails")
parser.add_argument('-out', dest="META_DATA_FILE", default="data/annual_reports.csv", help="Output file for metadata")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing data?")
a = parser.parse_args()

FEED_FILENAME = "feed_%s.html"
urlParts = urlparse(a.URL)
BASE_URL = urlParts.scheme + "://" + urlParts.netloc

# Make sure output dirs exist
io.makeDirectories([a.FEED_DIR, a.RECORD_DIR, a.PDF_DIR, a.IMAGE_DIR, a.META_DATA_FILE])

metafields = ["id", "url", "title", "dateIssued", "pdfUrl", "thumbUrl"]
metadata = []

page = 1
url = a.URL
while True:

    filename = FEED_FILENAME % str(page).zfill(3)
    contents = io.downloadFile(url, a.FEED_DIR, filename, overwrite=a.OVERWRITE)
    soup = BeautifulSoup(contents, "html.parser")
    nextLink = soup.find("a", class_="next-page-link")

    entryList = soup.find("ul", class_="ds-artifact-list")
    entries = entryList.find_all("div", class_="artifact-title")
    for i, entry in enumerate(entries):
        entryLink = entry.find("a")
        entryUrl = BASE_URL + entryLink.get("href") + "?show=full"
        entryTitle = entryLink.string.strip()
        entryId = entryLink.get("href").split("/")[-1]
        entryFilename = entryId + ".html"
        entryContents = io.downloadFile(entryUrl, a.RECORD_DIR, entryFilename, overwrite=a.OVERWRITE)

        if len(entryContents) <= 0:
            print("Could not download %s" % entryUrl)
            continue

        esoup = BeautifulSoup(entryContents, "html.parser")

        entryMeta = {}
        entryMeta["id"] = entryId
        entryMeta["url"] = entryUrl
        entryMeta["title"] = entryTitle

        metaDateIssued = esoup.find("meta", {"name": "DCTERMS.issued"})
        if metaDateIssued:
            entryMeta["dateIssued"] = metaDateIssued.get("content")
        else:
            print("Could not find date issued for %s." % entryUrl)

        fileList = esoup.find("div", class_="file-list")
        if fileList:
            pdfLink = fileList.find("a", class_="image-link")
            if pdfLink:
                pdfUrl = BASE_URL + pdfLink.get("href")
                pdfExt = io.getFileextFromUrl(pdfUrl)
                if pdfExt == ".pdf":
                    entryMeta["pdfUrl"] = pdfUrl
                    pdfFilename = entryId + ".pdf"
                    io.downloadBinaryFile(pdfUrl, a.PDF_DIR, pdfFilename, overwrite=a.OVERWRITE)
                else:
                    print("PDF link is not .pdf type: %s in %s" % (pdfUrl, entryUrl))
                imageEl = pdfLink.find("img")
                if imageEl:
                    imageUrl = BASE_URL + imageEl.get("src")
                    entryMeta["thumbUrl"] = imageUrl
                    imageExt = io.getFileextFromUrl(imageUrl)
                    imageFilename = entryId + imageExt
                    io.downloadBinaryFile(imageUrl, a.IMAGE_DIR, imageFilename, overwrite=a.OVERWRITE)
                else:
                    print("Could not find thumbnail image in %s" % entryUrl)
            else:
                print("Could not find PDF link for %s" % entryUrl)
        else:
            print("Could not find file link for %s" % entryUrl)

        metadata.append(entryMeta)

    if nextLink:
        url = BASE_URL + nextLink.get('href')
    else:
        break

    page += 1

io.writeCsv(a.META_DATA_FILE, metadata, metafields)
