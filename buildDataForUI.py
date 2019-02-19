# -*- coding: utf-8 -*-

import argparse
import glob
import json
import os
from pprint import pprint
import sys

import lib.eac_utils as eac
import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-fdir', dest="FLOOR_PLANS_DIR", default="data/floor_plans/%s/*.png", help="Directory with floor plans")
parser.add_argument('-rdir', dest="REPORTS_DIR", default="img/annual_reports/%s.jpg", help="Directory with reports")
parser.add_argument('-ldir', dest="LOGOS_DIR", default="img/logos/*.png", help="Directory with logos")
parser.add_argument('-reports', dest="REPORTS_FILE", default="data/annual_reports.csv", help="File with annual report data (from scrapeAnnualReports.py)")
parser.add_argument('-dates', dest="EAC_DATES_FILE", default="data/eac_dates.csv", help="File with EAC dates data (from collectDates.py)")
parser.add_argument('-items', dest="ITEMS_FILE", default="data/historic_images.csv", help="File with digital items data (from scrapeDigitalItems.py)")
parser.add_argument('-start', dest="START_YEAR", default=1869, type=int, help="Start year")
parser.add_argument('-end', dest="END_YEAR", default=2019, type=int, help="End year")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/ui.json", help="File for output")
a = parser.parse_args()

FLOORS = 4

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_FILE)

def addRanges(items, startYear, endYear):
    itemCount = len(items)
    sortedItems = sorted(items, key=lambda k:k["year"])
    for i, item in enumerate(sortedItems):
        fromYear = item["year"]
        toYear = endYear
        j = i+1
        while j < itemCount:
            nextItem = sortedItems[j]
            if nextItem["year"] > fromYear:
                toYear = nextItem["year"]-1
                break
            j += 1
        sortedItems[i].update({
            "yearFrom": fromYear,
            "yearTo": toYear
        })
    return sortedItems

# Retrieve floor plans
floorPlans = []
for i in range(FLOORS):
    floor = i + 1
    floorDir = a.FLOOR_PLANS_DIR % floor
    floorPlanFiles = glob.glob(floorDir)
    for fn in floorPlanFiles:
        year = int(io.getFileBasename(fn))
        floorPlans.append({
            "image": fn,
            "floor": floor,
            "year": year
        })
floorPlans = addRanges(floorPlans, a.START_YEAR, a.END_YEAR)

# Retrieve logos
logos = []
logoFiles = glob.glob(a.LOGOS_DIR)
for fn in logoFiles:
    year = int(io.getFileBasename(fn))
    logos.append({
        "image": fn,
        "year": year
    })
logos = addRanges(logos, a.START_YEAR, a.END_YEAR)

# Retrieve reports
reports = []
_, reportData = io.readCsv(a.REPORTS_FILE)
for r in reportData:
    year = eac.stringToYear(r["dateIssued"])
    if year > 0:
        reports.append({
            "title": r["title"],
            "url": r["url"],
            "image": a.REPORTS_DIR % r["id"],
            "year": year
        })
    else:
        print("No year found for annual report %s" % r["id"])
reports = addRanges(reports, a.START_YEAR, a.END_YEAR)

# retrieve items
items = []
_, itemData = io.readCsv(a.ITEMS_FILE)
for item in itemData:
    year = eac.stringToYear(item["date"])
    if year > 0:
        items.append({
            "title": item["title"],
            "url": item["url"],
            "image": item["thumbUrl"],
            "year": year
        })
    else:
        print("No year found for item %s" % item["id"])

# retrieve expeditions
expeditions = []
_, eacData = io.readCsv(a.EAC_DATES_FILE)
eacData = [e for e in eacData if e["type"]=="Expedition"]
for e in eacData:
    entry = {
        "title": e["name"],
        "event": e["dateevent"],
        "place": e["dateplace"]
    }
    yearFrom, yearTo = eac.stringsToDateRange(e["date"], e["fromdate"], e["todate"], e["name"])
    if yearFrom > 0 and yearTo > 0:
        if yearFrom == yearTo:
            entry["year"] = yearFrom
        else:
            entry["yearFrom"] = yearFrom
            entry["yearTo"] = yearTo
        expeditions.append(entry)

data = {
    "logos": logos,
    "floorPlans": floorPlans,
    "reports": reports,
    "items": items,
    "expeditions": expeditions
}
dataKeys = list(data.keys())

# Create a table of years with indices
years = [[[] for k in range(len(dataKeys))] for y in range(a.END_YEAR-a.START_YEAR+1)]
for dataKey in data:
    items = data[dataKey]
    dataIndex = dataKeys.index(dataKey)
    for itemIndex, item in enumerate(items):
        if "yearFrom" in item and "yearTo" in item:
            year = item["yearFrom"]
            while year <= item["yearTo"]:
                yearIndex = year - a.START_YEAR
                if 0 <= yearIndex <= (a.END_YEAR-a.START_YEAR):
                    years[yearIndex][dataIndex].append(itemIndex)
                year += 1
        else:
            yearIndex = item["year"] - a.START_YEAR
            if 0 <= yearIndex <= (a.END_YEAR-a.START_YEAR):
                years[yearIndex][dataIndex].append(itemIndex)

outData = {
    "yearStart": a.START_YEAR,
    "yearEnd": a.END_YEAR,
    "years": years,
    "dataKeys": dataKeys
}
outData.update(data)

with open(a.OUTPUT_FILE, 'w') as f:
    json.dump(outData, f)
    print("Created %s" % a.OUTPUT_FILE)
