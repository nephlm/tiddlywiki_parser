import argparse
import json
import os
import sys

import bs4
import requests

TIDDLY_WIKI_URLS = ["https://tiddlywiki.com/", "http://esoverse.tiddlyspot.com/"]


class TiddlyWiki(object):
    def __init__(self, content):
        self.content = content
        self.bs4 = None
        self.tiddlers = []
        self.parse()

    @classmethod
    def parse_file(cls, path):
        with open(path, "r") as fp:
            self = cls(fp.read())
            return self

    def _filter_div(self, div):
        try:
            title = div["title"]
            if title.startswith("$:/"):
                return None
        except KeyError:
            # print(f"No title - {str(div)[:50]}")
            return None

        try:
            tags = div["tags"]
            if tags.startswith("$:/"):
                return None
        except KeyError:
            print(f"No Tags - {str(div)[:100]}")
            # return None

        return div

    def parse(self):
        self.bs4 = bs4.BeautifulSoup(self.content, "html.parser")
        divs = self.bs4.find_all("div")
        for div in divs:
            if self._filter_div(div):
                tiddler = Tiddler(div)
                self.tiddlers.append(tiddler)
        self.tiddlers = sorted(self.tiddlers, key=lambda t: t.attrs["title"])

    def export_list(self):
        return [tiddler.dict() for tiddler in self.tiddlers]

    # def export(self, path):
    #     export_obj = self.export_list()
    #     with open(path, "w") as fp:
    #         fp.write(
    #             json.dumps(export_obj, sort_keys=True, indent=4, separators=(",", ": "))
    #         )


class Tiddler(object):
    def __init__(self, div):
        self.div = div

        self.attrs = div.attrs
        self.text = div.text

    def dict(self):
        tiddler_dict = self.attrs.copy()
        tiddler_dict["text"] = self.text
        return tiddler_dict


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


def export(path, export_obj, save_json=False):
    if save_json:
        # for tiddler in export_obj:
        #     print(f'{tiddler["title"]}')
        with open(path, "w") as fp:
            fp.write(
                json.dumps(export_obj, sort_keys=True, indent=4, separators=(",", ": "))
            )
    else:
        write_tiddlers(path, export_obj)


def write_tiddlers(path, export_obj):
    for tiddler in export_obj:
        tiddler_path = os.path.join(path, tiddler["title"] + ".tid")
        with open(tiddler_path, "w") as fp:
            for key in tiddler:
                if key == "text":
                    continue
                fp.write(f"{key}:  {tiddler[key]}\n")
            fp.write(f'{tiddler["text"]}')


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="The path to the html file")
    parser.add_argument("output", help="The path to the output dir (of file).")
    parser.add_argument(
        "--json",
        default=False,
        action="store_true",
        help="Save as a json file instead of as individual tiddlers.  output must be a dir.",
    )
    args = parser.parse_args()

    raw_content = read(args.source)
    tiddlywiki = TiddlyWiki(raw_content)
    export(args.output, tiddlywiki.export_list(), save_json=args.json)


if __name__ == "__main__":
    main()
