import sys
from pathlib import Path

import requests


def read_file(path):
    p = Path(path)
    return p.read_text()
    with open(path, "r", encoding="utf8") as fp:
        return fp.read()


def get_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    print(f"couldn't retrieve {url}")
    sys.exit()


def read(source):
    if "://" in source:
        raw_content = get_content(source)
        raw_content = raw_content.decode("utf8")
    else:
        raw_content = read_file(source)
    return raw_content
