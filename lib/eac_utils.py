import re
import lib.math_utils as mu

def getDateEntryXML(el):
    dateEntry = {}

    dparent = el.parent
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
        dateEntry["datename"] = getNameFromXML(dparent.parent)

    # look for relation
    if dparent.name == "cpfrelation":
        dateEntry["daterelation"] = getRelationFromXML(dparent)

    # look for place
    dateEntry["dateplace"] = getPlaceFromXML(dparent.parent.find("place"))

    return dateEntry

def getNameFromXML(el):
    if not el:
        return ""
    name = []
    parts = el.find_all("part")
    for part in parts:
        name.append(part.string.strip())
    return " ".join(name)

def getPlaceFromXML(el):
    if not el:
        return ""
    entry = el.find("placeentry")
    return entry.string.strip() if entry else ""

def getRelationXML(el):
    if not el:
        return ""
    entry = el.find("relationentry")
    return entry.string.strip() if entry else ""

def getTypes():
    return {
        "amnhc_0": "Museum",
        "amnhp_1": "Person",
        "amnhc_2": "Expedition",
        "amnhc_3": "Department",
        "amnhc_4": "Permanent Exhibition",
        "amnhc_5": "Temporary Exhibition"
    }

def getTypeFromId(id):
    types = getTypes()
    type = ""
    for key in types:
        if id.startswith(key):
            type = types[key]
            break
    return type

def stringsToDateRange(ddate, dfrom, dto, title=None):
    year = stringToYear(ddate)
    yFrom = stringToYear(dfrom)
    yTo = stringToYear(dto)

    if yFrom > 0 and yTo > 0:
        return (yFrom, yTo)

    yFrom = year
    yTo = year

    if title:

        pattern = re.compile("[0-9]{4}\-[0-9]{4}")
        matches = pattern.search(title)
        if matches:
            match = matches.group(0)
            yFrom, yTo = tuple([int(m) for m in match.split("-")])

    return (yFrom, yTo)

def stringToYear(dstring):
    year = -1

    if isinstance(dstring, int):
        return dstring

    dstring = re.sub(r'[^0-9\-]+', '', dstring)

    if "-" in dstring:
        year = int(dstring.split("-")[0])
    elif len(dstring) > 0:
        year = int(dstring)

    return year
