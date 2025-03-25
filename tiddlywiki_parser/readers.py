import sys
from pathlib import Path

import requests


def read_file(path) -> str:
    p = Path(path)
    return p.read_text(encoding='utf8')


def get_content(url) -> str:
    response = requests.get(url, timeout=30)
    if response.status_code == 200:
        return response.content.decode("utf8")
    print(f"couldn't retrieve {url}")
    sys.exit()


def read(source):
    if "://" in source:
        raw_content = get_content(source)
    else:
        raw_content = read_file(source)
    assert isinstance(raw_content, str)
    return raw_content
