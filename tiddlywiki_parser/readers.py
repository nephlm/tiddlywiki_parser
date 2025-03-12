import sys

import requests


def read_file(path):
    with open(path, "r") as fp:
        return fp.read()


def get_content(url):
    response = requests.get(url)
    if response.status_code == 200:
        return response.content
    print(f"couldn't retreive {url}")
    sys.exit()


def read(source):
    if "://" in source:
        raw_content = get_content(source)
    else:
        raw_content = read_file(source)
    return raw_content
