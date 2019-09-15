import argparse
import json

import bs4


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
            return None

        try:
            tags = div["tags"]
            if tags.startswith("$:/"):
                return None
        except KeyError:
            return None

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

    def export(self, path):
        export_obj = self.export_list()
        with open(path, "w") as fp:
            fp.write(
                json.dumps(export_obj, sort_keys=True, indent=4, separators=(",", ": "))
            )


class Tiddler(object):
    def __init__(self, div):
        self.div = div

        self.attrs = div.attrs
        self.text = div.text

    def dict(self):
        tiddler_dict = self.attrs.copy()
        tiddler_dict["text"] = self.text
        return tiddler_dict


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    args = parser.parse_args()
    path = args.path
    print(path)

    tiddlywiki = TiddlyWiki.parse_file(path)
    tiddlywiki.export("/tmp/test.json")


if __name__ == "__main__":
    main()
