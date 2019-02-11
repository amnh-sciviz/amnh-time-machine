

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
