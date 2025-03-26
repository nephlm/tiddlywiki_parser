import argparse
import datetime
from hmac import new
from pathlib import Path

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
    # content = readers.read("examples/esoverse.html")
    content = readers.read("https://nephlm.github.io/tw/gods-reborn.html")
    if isinstance(content, bytes):
        content.encode("utf8")

    assert isinstance(content, str)

    wiki = TiddlyWiki(content)
    print("\n".join([x.title for x in wiki.system_tiddlers if "GitHub" in x.title]))
    # wiki.test()
    # delete_list = []
    # for tiddler in wiki.tiddlers:
    #     if tiddler.title == "Welcome":
    #         tiddler["version"] = "Player's"
    #     elif tiddler.title == "generation_timestamp":
    #         now = datetime.datetime.now()
    #         tiddler["timestamp"] = now.isoformat()
    #     elif tiddler.title == "xxtest public":
    #         tiddler.text = "public test \n\n<hr>\n\n public again<hr>"
    #     if tiddler.has_tag("private"):
    #         delete_list.append(tiddler.title)
    # new_wiki = wiki.remake(delete_list)
    # print(wiki.export_list())
    # fp = Path("tests/out.html")
    # fp.write_text(new_wiki, "utf8")
    # print(f"wrote {str(fp)}")

    print("test finished")


if __name__ == "__main__":
    main()
