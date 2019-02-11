import json
import os
import requests
from urllib.parse import urlparse

def downloadFile(url, dir, filename=None, save=True, overwrite=False):
    if filename is None:
        urlObj = urlparse.urlparse(url)
        filename = os.path.basename(urlObj.path)
    if len(filename) <= 0:
        filename = "file.dat"

    filename = dir + filename
    contents = ""
    isJSON = filename.endswith(".json")

    if os.path.isfile(filename) and not overwrite:
        print("%s already exists." % filename)
        with open(filename, "r") as f:
            if isJSON:
                contents = json.load(f)
            else:
                contents = f.read()
        return contents

    r = requests.get(url)
    contents = r.json() if isJSON else r.text
    print("Downloading %s to %s" % (url, filename))

    if save:
        with open(filename, "w") as f:
            if isJSON:
                json.dump(contents, f)
            else:
                f.write(contents)

    return contents

def makeDirectories(filenames):
    if not isinstance(filenames, list):
        filenames = [filenames]
    for filename in filenames:
        dirname = os.path.dirname(filename)
        if not os.path.exists(dirname):
            os.makedirs(dirname)
