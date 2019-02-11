# -*- coding: utf-8 -*-

import argparse
from bs4 import BeautifulSoup
import glob
import os
from pprint import pprint
import sys

import lib.eac_utils as eac
import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-rdir', dest="RECORD_DIR", default="data/eac_records/*.xml", help="Directory with EAC records")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/eac_records.csv", help="File to compile records to")
parser.add_argument('-overwrite', dest="OVERWRITE", action="store_true", help="Overwrite existing data?")
a = parser.parse_args()

FIELDS = ["id", "type", "name", "date", "fromDate", "toDate", "dateType", "eventDescription"]

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_FILE)
filenames = glob.glob(a.RECORD_DIR)
filenames = sorted(filenames)
fileCount = len(filenames)

# Read existing data
fieldNames = []
recordData = []
if os.path.isfile(a.OUTPUT_FILE):
    fieldNames, recordData = io.readCSV(a.OUTPUT_FILE)
    recordData = sorted(recordData, key=lambda r: r["id"])
for field in FIELDS:
    if field not in fieldNames:
        fieldNames.append(field)

for i, fn in enumerate(filenames):
    append = len(recordData) > 0
    id = os.path.basename(fn).split(".")[0]

    # Check to see if we already processed this file
    found = [r for r in recordData if r["id"]==id]
    if len(found) > 0 and not a.OVERWRITE:
        continue

    # retrieve type
    type = eac.getTypeFromId(id)
    record = {"id": id, "type": type}

    soup = None
    with open(fn) as f:
        soup = BeautifulSoup(f, 'html.parser')
    if not soup:
        print("Could not parse %s" % fn)
        continue

    # retrieve name
    name = []
    cpfDescription = soup.find("cpfdescription")
    if cpfDescription:
        nameEntry = cpfDescription.find("nameentry")
        if nameEntry:
            parts = nameEntry.find_all("part")
            for part in parts:
                name.append(part.string.strip())
    record["name"] = " ".join(name)

    dates = cpfDescription.find_all("date")
    for date in dates:
        dateEntry = {}
        dparent = date.parent
        if dparent.name in ["dateset", "daterange"]:
            continue
        dateEntry["dateType"] = dparent.name

        # parse date value
        dateValue = ""
        if date.has_attr("standarddate"):
            dateValue = date.get("standarddate").strip()
        else:
            dateValue = date.string.strip()

        if len(dateValue) > 0:
            dateEntry["date"] = dateValue

        event = dparent.find("event")
        if event:
            dateEntry["eventDescription"] = event.string.strip()

    dateRanges = cpfDescription.find_all("daterange")

    dateSets = cpfDescription.find_all("dateset")
    
    break

    # progressively save file
    # io.writeCsv(a.OUTPUT_FILE, recordData, fieldNames, append=append, verbose=False)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/fileCount*100,2))
    sys.stdout.flush()
