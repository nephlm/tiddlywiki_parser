import argparse

import tiddlywiki_parser.readers as readers
import tiddlywiki_parser.writiers as writers
from tiddlywiki_parser.tiddlywiki import TiddlyWiki


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("source", help="The path to the html file")
    parser.add_argument("output", help="The path to the output dir (or file).")
    parser.add_argument(
        "--json",
        default=False,
        action="store_true",
        help="Save as a json file instead of as individual tiddlers.  output must be a file.",
    )
    args = parser.parse_args()

    raw_content = readers.read(args.source)
    tiddlywiki = TiddlyWiki(raw_content)
    writers.export(args.output, tiddlywiki.export_list(), save_json=args.json)


def test():
    print("test being called")
    # currently being used to test remake command, but may change without notice.
    content = readers.read("https://nephlm.github.io/tw/gods-reborn.html")
    wiki = TiddlyWiki(content)
    new_wiki = wiki.remake(["Toe Market"])
    with open("tests/out.html", "w", encoding="utf8") as f:
        f.write(new_wiki)
    print("test finished")


if __name__ == "__main__":
    main()
