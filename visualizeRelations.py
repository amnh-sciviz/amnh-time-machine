# -*- coding: utf-8 -*-

import argparse
from igraph import *
import numpy as np
import os
import pickle
from PIL import Image, ImageDraw, ImageFont
from pprint import pprint
import sys

import lib.io_utils as io
import lib.math_utils as mu

# input
parser = argparse.ArgumentParser()
parser.add_argument('-rel', dest="RELATIONS_FILE", default="data/eac_relations.csv", help="File to compile relations to")
parser.add_argument('-ent', dest="ENTITIES_FILE", default="data/eac_entities.csv", help="File to compile entities to")
parser.add_argument('-layout', dest="LAYOUT_ALGORITHM", default="fruchterman_reingold", help="Layout algorithm, e.g. fruchterman_reingold, kamada_kawai, drl, large_graph")
parser.add_argument('-width', dest="WIDTH", default=16384, type=int, help="Image width")
parser.add_argument('-height', dest="HEIGHT", default=16384, type=int, help="Image height")
parser.add_argument('-margin', dest="MARGIN", default=100, type=int, help="Margin")
parser.add_argument('-font', dest="FONT", default="data/OverpassMono-Bold.ttf", help="Font file")
parser.add_argument('-fontsize', dest="FONT_SIZE", type=int, default=16, help="Font size")
parser.add_argument('-cache', dest="CACHE_FILE", default="data/eac_graph.p", help="File for caching")
parser.add_argument('-out', dest="OUTPUT_FILE", default="img/eac_relations.png", help="File for output")
a = parser.parse_args()

COLORS = ["#B71C1C", "#0D47A1", "#1B5E20", "#4527A0", "#E65100"]
MAX_LABEL_LENGTH = 100
cWidth = a.WIDTH - a.MARGIN * 2
cHeight = a.HEIGHT - a.MARGIN * 2

# Make sure output dirs exist
io.makeDirectories(a.OUTPUT_FILE)

# Read data
_, entities = io.readCsv(a.ENTITIES_FILE)
_, relations = io.readCsv(a.RELATIONS_FILE)

entities = [e for e in entities if e["type"]!="Museum" and len(e["type"]) > 0]
print("%s entities after filtering type" % len(entities))

relationEntityIds = [r["id1"] for r in relations] + [r["id2"] for r in relations]
relationEntityIds = list(set(relationEntityIds))

entities = [e for e in entities if e["id"] in relationEntityIds]
entityIds = list(set([e["id"] for e in entities]))
print("%s entities after filtering out orphans" % len(entities))
nodeCount = len(entities)
relations = [r for r in relations if r["id1"] in entityIds and r["id2"] in entityIds]

def hexToRGB(hex):
    hex = hex.lstrip("#")
    return tuple(int(hex[i:i+2], 16) for i in (0, 2 ,4))

# Add indices and colors based on type
entityLookup = {}
types = list(set([e["type"] for e in entities]))
for i, e in enumerate(entities):
    entities[i]["index"] = i
    entities[i]["color"] = COLORS[types.index(e["type"])]
    entityLookup[e["id"]] = entities[i]

cachedData = None
if os.path.isfile(a.CACHE_FILE):
    with open(a.CACHE_FILE, "rb") as f:
        cachedData = pickle.load(f)
        print("Loaded cache file %s" % a.CACHE_FILE)

if cachedData is None:
    print("Building graph from scratch...")

    edges = []
    for r in relations:
        i1 = entityLookup[r["id1"]]["index"]
        i2 = entityLookup[r["id2"]]["index"]
        edges.append((i1, i2))

    g = Graph()
    g.add_vertices(nodeCount)
    g.add_edges(edges)
    layout = g.layout(a.LAYOUT_ALGORITHM)

    # get bounds and convert to pixels
    xs = [p[0] for p in layout]
    ys = [p[1] for p in layout]
    xBound = (min(xs), max(xs))
    yBound = (min(ys), max(ys))

    cachedData = np.zeros((len(layout), 3))
    for i, p in enumerate(layout):
        nx = mu.norm(p[0], xBound)
        ny = mu.norm(p[1], yBound)
        cachedData[i] = [i, nx, ny]

    pickle.dump(cachedData, open(a.CACHE_FILE, 'wb'))
    print("Saved cached data %s" % a.CACHE_FILE)

font = ImageFont.truetype(a.FONT, a.FONT_SIZE)
im = Image.new('RGB', (a.WIDTH, a.HEIGHT), (255,255,255))
draw = ImageDraw.Draw(im)

print("Drawing image...")
for entry in cachedData:
    i, nx, ny = tuple(entry)
    i = int(i)
    x = int(round(nx * cWidth + a.MARGIN))
    y = int(round(ny * cHeight + a.MARGIN))

    label = entities[i]["name"]
    if len(label) > MAX_LABEL_LENGTH:
        label = label[:(MAX_LABEL_LENGTH-3)] + "..."
    color = entities[i]["color"]

    # calculate text size
    tw, th = draw.textsize(label, font=font)

    # center the text
    x -= tw * 0.5
    y -= th * 0.5
    x = int(round(x))
    y = int(round(y))

    draw.text((x, y), label, font=font, fill=color)

    sys.stdout.write('\r')
    sys.stdout.write("%s%%" % round(1.0*(i+1)/nodeCount*100,2))
    sys.stdout.flush()

print("Saving image...")
im.save(a.OUTPUT_FILE)
print("Created %s" % a.OUTPUT_FILE)
