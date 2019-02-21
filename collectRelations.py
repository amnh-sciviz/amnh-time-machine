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
parser.add_argument('-dir', dest="RECORD_DIR", default="downloads/eac_records/*.xml", help="Directory with EAC records")
parser.add_argument('-rel', dest="RELATIONS_FILE", default="data/eac_relations.csv", help="File to compile relations to")
parser.add_argument('-ent', dest="ENTITIES_FILE", default="data/eac_entities.csv", help="File to compile entities to")
a = parser.parse_args()

ENTITY_FIELDS = ["id", "type", "name", "url"]
RELATIONS_FIELDS = ["id1", "id2", "type", "role", "date"]
BASE_URL = "http://data.library.amnh.org/archives-authorities/id/"

# Make sure output dirs exist
io.makeDirectories([a.RELATIONS_FILE, a.ENTITIES_FILE])
filenames = glob.glob(a.RECORD_DIR)
filenames = sorted(filenames)
fileCount = len(filenames)

entitiesLookup = {}
relations = []

def getDate(cpfRelation):
    dateValue = ""
    date = cpfRelation.find("date")
    if not date:
        date = cpfRelation.find("fromdate")
    if date:
        if date.has_attr("standarddate"):
            dateValue = date.get("standarddate").strip()
        else:
            dateValue = date.string.strip()
    return dateValue

for i, fn in enumerate(filenames):
    id = os.path.basename(fn).split(".")[0]

    # retrieve type
    type = eac.getTypeFromId(id)
    entity = {"id": id, "type": type, "url": BASE_URL + id}

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
        name = eac.getNameFromXML(nameEntry)
    else:
        print("No description in %s. Skipping" % fn)
        continue
    entity["name"] = name
    entitiesLookup[id] = entity

    cpfRelations = cpfDescription.find_all("cpfrelation", {"xlink:href": True})

    for cpfRelation in cpfRelations:
        relation = {}
        id2 = cpfRelation.get("xlink:href")
        relation["id1"] = id
        relation["id2"] = id2
        relation["type"] = cpfRelation.get("cpfrelationtype") if cpfRelation.has_attr("cpfrelationtype") else ""
        relation["role"] = cpfRelation.get("xlink:arcrole") if cpfRelation.has_attr("xlink:arcrole") else ""
        relation["date"] = getDate(cpfRelation)

        if id2 not in entitiesLookup:
            relationEntry = cpfRelation.find("relationentry")
            name = relationEntry.text.strip() if relationEntry else ""
            entitiesLookup[id2] = {
                "id": id2,
                "name": name,
                "type": eac.getTypeFromId(id2),
                "url": BASE_URL + id2
            }

        relations.append(relation)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/fileCount*100,2))
    sys.stdout.flush()

entities = []
for key in entitiesLookup:
    entities.append(entitiesLookup[key])

io.writeCsv(a.ENTITIES_FILE, entities, ENTITY_FIELDS)
io.writeCsv(a.RELATIONS_FILE, relations, RELATIONS_FIELDS)
