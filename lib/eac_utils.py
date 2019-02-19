import re
import lib.math_utils as mu

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
