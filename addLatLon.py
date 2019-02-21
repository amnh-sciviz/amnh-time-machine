# -*- coding: utf-8 -*-

import argparse
from difflib import SequenceMatcher
import os
from pprint import pprint
import sys

import lib.eac_utils as eac
import lib.io_utils as io

# input
parser = argparse.ArgumentParser()
parser.add_argument('-in', dest="INPUT_FILE", default="data/eac_dates.csv", help="File with EAC data (from collectDates.py)")
parser.add_argument('-countries', dest="COUNTRIES_FILE", default="data/countries.csv", help="File with countries data")
parser.add_argument('-states', dest="STATES_FILE", default="data/states.csv", help="File with states data")
parser.add_argument('-keys', dest="KEYS", default="name,dateplace,dateevent", help="List of keys to check in order of priority (first is highest priority)")
parser.add_argument('-out', dest="OUTPUT_FILE", default="data/eac_expeditions.csv", help="File for output")
a = parser.parse_args()

MIN_MATCH_LEN = 4
placeKeys = a.KEYS.strip().split(",")
keysToAdd = ["lon", "lat", "match"]

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_FILE)

_, countries = io.readCsv(a.COUNTRIES_FILE)
_, states = io.readCsv(a.STATES_FILE)

# https://stackoverflow.com/questions/18715688/find-common-substring-between-two-strings
def findLongestCommonSubstring(string1, string2):
    match = SequenceMatcher(None, string1, string2).find_longest_match(0, len(string1), 0, len(string2))
    if match:
        return string1[match.a: match.a + match.size]
    else:
        return None

def listIntersection(a, b):
    return list(set(a).intersection(set(b)))

def isValidMatch(candidate, match):
    if match is None:
        return False

    candidate = candidate.lower()
    match = match.lower()

    valid = True
    stopWords = ["and", "the", "to", "of", "united", "american", "island", "islands", "north", "south", "southern", "northern", "east", "west", "eastern", "western", "central", "columbia", "african"]
    aList = [word.strip('[]()') for word in candidate.split()]
    bList = [word.strip('[]()') for word in match.split()]
    intersections = listIntersection(aList, bList)
    intersections = [word for word in intersections if word not in stopWords and len(word) > 3]
    if len(intersections) <= 0:
        valid = False

    return valid

def findPlace(value, pool):
    value = value.lower()
    matches = []
    for i, candidate in enumerate(pool):
        match = findLongestCommonSubstring(value, candidate["name"].lower())
        if isValidMatch(value, candidate["name"]):
            matches.append((i,match))
    matches = [m for m in matches if len(m[1]) >= MIN_MATCH_LEN]
    if len(matches) > 0:
        matches = sorted(matches, key=lambda m:-len(m[1]))
        place = pool[matches[0][0]]
        print("%s = %s" % (value, place["name"]))
        return (place["longitude"], place["latitude"], place["name"])
    else:
        return (None, None, None)

# retrieve expeditions
expeditions = []
fieldNames, eacData = io.readCsv(a.INPUT_FILE)
for key in keysToAdd:
    if key not in fieldNames:
        fieldNames.append(key)
# eacData = [e for e in eacData if e["type"]=="Expedition"]
entryCount = len(eacData)

for i, entry in enumerate(eacData):
    if entry["type"]=="Expedition":
        for key in placeKeys:
            lon, lat, match = findPlace(entry[key], countries+states)
            if match:
                eacData[i].update({
                    "lon": lon,
                    "lat": lat,
                    "match": match
                })
                break

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/entryCount*100,2))
    sys.stdout.flush()

io.writeCsv(a.OUTPUT_FILE, eacData, fieldNames)
