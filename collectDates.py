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
parser.add_argument('-rdir', dest="RECORD_DIR", default="downloads/eac_records/*.xml", help="Directory with EAC records")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/eac_dates.csv", help="File to compile records to")
a = parser.parse_args()

DATE_FIELDS = ["date", "fromdate", "todate", "datetype", "dateevent", "datename", "daterelation", "dateplace"]
FIELDS = ["id", "type", "name"] + DATE_FIELDS

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_FILE)
filenames = glob.glob(a.RECORD_DIR)
filenames = sorted(filenames)
fileCount = len(filenames)

# Read existing data
fieldNames = FIELDS[:]
recordData = []

def cleanDateEntry(entry):
    for field in DATE_FIELDS:
        if field not in entry:
            entry[field] = ""

    hasDate = len(entry["date"]) > 0
    hasFromDate = len(entry["fromdate"]) > 0
    hasToDate = len(entry["todate"]) > 0

    if hasFromDate and not hasToDate:
        entry["date"] = entry["fromdate"]
        entry["fromdate"] = ""

    elif hasToDate and not hasFromDate:
        entry["date"] = entry["todate"]
        entry["todate"] = ""

    elif hasFromDate and hasToDate and entry["todate"] == entry["fromdate"]:
        entry["date"] = entry["fromdate"]
        entry["fromdate"] = ""
        entry["todate"] = ""

    return entry

def getName(el):
    if not el:
        return ""
    name = []
    parts = el.find_all("part")
    for part in parts:
        name.append(part.string.strip())
    return " ".join(name)

def getPlace(el):
    if not el:
        return ""
    entry = el.find("placeentry")
    return entry.string.strip() if entry else ""

def getRelation(el):
    if not el:
        return ""
    entry = el.find("relationentry")
    return entry.string.strip() if entry else ""

def getDateEntry(el):
    dateEntry = {}

    dparent = date.parent
    if dparent.name in ["dateset", "daterange"]:
        dparent = dparent.parent
    dateEntry["datetype"] = dparent.name

    # parse date value
    dateValue = ""
    if date.has_attr("standarddate"):
        dateValue = date.get("standarddate").strip()
    else:
        dateValue = date.string.strip()
    dateEntry[el.name] = dateValue

    # look for event
    event = dparent.find("event")
    description = ""
    if event:
        description = event.string.strip()
    dateEntry["dateevent"] = description

    # look for names
    if dparent.parent.name == "nameentry":
        dateEntry["datename"] = getName(dparent.parent)

    # look for relation
    if dparent.name == "cpfrelation":
        dateEntry["daterelation"] = getRelation(dparent)

    # look for place
    dateEntry["dateplace"] = getPlace(dparent.parent.find("place"))

    return dateEntry

rows = []
for i, fn in enumerate(filenames):
    id = os.path.basename(fn).split(".")[0]

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
    name = ""
    cpfDescription = soup.find("cpfdescription")
    if cpfDescription:
        nameEntry = cpfDescription.find("nameentry")
        name = getName(nameEntry)
    else:
        print("No description in %s. Skipping" % fn)
        continue
    record["name"] = name

    dateEntries = []
    dates = cpfDescription.find_all("date")
    for date in dates:
        dparent = date.parent
        if dparent.name in ["dateset", "daterange"]:
            continue
        dateEntries.append(getDateEntry(date))

    dateRanges = cpfDescription.find_all("daterange")
    for drange in dateRanges:
        fromDate = drange.find("fromdate")
        toDate = drange.find("todate")
        dateEntry = {}
        if fromDate:
            dateEntry.update(getDateEntry(fromDate))
        if toDate:
            dateEntry.update(getDateEntry(toDate))
        if fromDate or toDate:
            dateEntries.append(dateEntry)

    dateSets = cpfDescription.find_all("dateset")
    for dset in dateSets:
        setEntries = []
        for date in dset.find_all("date"):
            dateEntry = getDateEntry(date)
            setEntries.append(dateEntry)

        dateEntry = None
        # convert set to range for now
        if len(setEntries) > 1:
            setEntries = sorted(setEntries, key=lambda entry: entry["date"])
            dateEntry = setEntries[0]
            dateEntry["fromdate"] = dateEntry["date"]
            dateEntry.update(setEntries[-1])
            dateEntry["todate"] = dateEntry["date"]
            dateEntry["date"] = ""
        elif len(setEntries) > 0:
            dateEntry = setEntries[0]

        if dateEntry:
            dateEntries.append(dateEntry)

    # clean entries
    for j, entry in enumerate(dateEntries):
        dateEntries[j] = cleanDateEntry(entry)

    # remove duplicates
    dateEntries = list({(e["date"], e["fromdate"], e["todate"], e["datetype"], e["dateevent"], e["datename"], e["daterelation"], e["dateplace"]):e for e in dateEntries}.values())

    entryRows = []
    for dentry in dateEntries:
        row = {}
        row.update(record)
        row.update(dentry)
        entryRows.append(row)

    rows += entryRows

    # progressively save file
    # append = i > 0
    # io.writeCsv(a.OUTPUT_FILE, entryRows, fieldNames, append=append, verbose=False)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/fileCount*100,2))
    sys.stdout.flush()

io.writeCsv(a.OUTPUT_FILE, rows, fieldNames)
