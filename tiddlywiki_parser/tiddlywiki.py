import copy
import json
from typing import Self

import bs4

from tiddlywiki_parser.tiddler import DivTiddler, Tiddler


class TiddlyWiki(object):
    def __init__(self, content: str):
        """
        Object representing the tiddlywiki as a whole.

        Args:
            content: raw complete text of the tiddlywiki file.
        """
        self._legacy = False  # pre 5.2.0?
        self.content = content
        self.bs4 = None  # Beautiful Soup instance
        self.tiddlers: list = []
        self.parse()

    @classmethod
    def parse_file(cls, path: str) -> Self:
        """
        Parses a file on the local file system.

        Args:
            path: The path

        Returns:
            TiddlyWiki instance made from the content of the file.
        """
        with open(path, "r", encoding="utf8") as fp:
            self = cls(fp.read())
            return self

    def _filter_div(self, div: str) -> None | str:
        """
        Skip over system tiddlers.

        Args:
            div: The div returned by bs4

        Returns:
            The unmodified div if it is a user div, or None if it should be skipped.
        """
        SYSTEM_PREFIX = "$:/"
        try:
            title = div["title"]
            if title.startswith(SYSTEM_PREFIX):
                return None
        except KeyError:
            # print(f"No title - {str(div)[:50]}")
            return None

        try:
            tags = div["tags"]
            if tags.startswith(SYSTEM_PREFIX):
                return None
        except KeyError:
            print(f"No Tags - {str(div)[:100]}")

        return div

    def _get_json_script_stores(self, bs4):
        """Return a list of bs4 objects for each json store in the wiki."""
        return bs4.find_all(
            "script", class_="tiddlywiki-tiddler-store", type="application/json"
        )

    def _read_json_store_content(self, bs4) -> list:
        """
        Read the tiddlywiki store contents and covert to native python object.

        Args:
            bs4: A bs4 object.

        Returns:
            list: list of tuples,
                    item 0 is the bs4 script Tag
                    item 1 is the native python repr of the json content
        """
        store_contents = []
        script_stores = self._get_json_script_stores(bs4)
        for script_tag in script_stores:
            contents = script_tag.decode_contents()
            list_obj = json.loads(contents)
            store_contents.append((script_tag, list_obj))
        return store_contents

    def _get_json_tiddlers(self, bs4, include_system=False) -> list[Tiddler]:
        """
        Return a list of Tiddler objects for the wiki.
        This combination form all stores and doesn't keep track of
        which store they came from.
        """
        tiddlers = []
        for _, tiddler_list in self._read_json_store_content(bs4):
            for tiddler_dict in tiddler_list:
                tiddler = Tiddler(tiddler_dict)
                if include_system or not tiddler.is_system():
                    print(tiddler.title)
                    tiddlers.append(tiddler)
        return tiddlers

    def _get_div_tiddlers(self, bs4, include_system=False) -> list[DivTiddler]:
        store_area = bs4.find("div", id="storeArea")
        tiddlers = []
        divs = store_area.find_all("div")
        for div in divs:
            tiddler = DivTiddler(div)
            if include_system or not tiddler.is_system():
                print(tiddler.title)
                tiddlers.append(tiddler)
        return tiddlers

    def parse(self) -> list[Tiddler]:
        """
        Use bs4 to parse out the div instances that are tiddlers.

        returns:
            List of user Tiddlers.
        """
        self.bs4 = bs4.BeautifulSoup(self.content, "html.parser")
        self.tiddlers = self._get_json_tiddlers(self.bs4)
        if not self.tiddlers:
            # pre 5.2.0 div based tiddler fall back to old method.
            self._legacy = True
            self.tiddlers = self._get_div_tiddlers(self.bs4)
        self.tiddlers = sorted(self.tiddlers, key=lambda t: t.title)
        return self.tiddlers

    def export_list(self) -> list[dict]:
        """
        Export tiddlers in a generic form.
        Will run parse() if self.tiddlers is empty.

        Returns:
            List of tiddlers converted to dicts ready for export.
        """
        if not self.tiddlers:
            self.parse()
        return [tiddler.make_dict() for tiddler in self.tiddlers]

    def remake(self, delete_list: list[str]) -> str:
        """
        Will remake a tiddlywiki html content from the parsed data.

        * Any changes made to the tiddler object will be reflected in the
            new tiddlywiki
        * Any Tiddler (identified by title) in the delete list will be
            removed from the resulting html content.

        NOTE: Does not handle changing the title.  To do this add a new tiddler to
            self.tiddlers and pass the old title in the `delete_list`

        Args:
            delete_list: list of tiddler titles that should be removed from the
                new tiddlywiki.

        Returns:
            A string representing a html file, modified by changes made to self.tiddlers
            and the titles passed in to be deleted.
        """
        if not self.bs4 or not self.tiddlers:
            raise RuntimeError("Can't remake a tiddlywiki until one has been parsed.")

        new_bs4 = copy.deepcopy(self.bs4)

        tiddler_index = {}
        for tiddler in self.tiddlers:
            tiddler_index[tiddler.title] = tiddler

        if self._legacy:
            self.remake_legacy(new_bs4, delete_list)
            return str(new_bs4)
            return new_bs4.prettify(formatter=None)
        else:
            for store, tiddler_list in self._read_json_store_content(new_bs4):
                overwrite_content = []
                for tiddler_dict in tiddler_list:
                    tiddler = Tiddler(tiddler_dict)
                    if tiddler.title in delete_list:
                        print(f'Tiddler "{tiddler.title}" removed.')
                        continue
                    if tiddler.title in tiddler_index:
                        new_dict = tiddler_index[tiddler.title].make_dict()
                        overwrite_content.append(new_dict)
                        print(f'Tiddler "{tiddler.title}" replaced.')
                    else:
                        overwrite_content.append(tiddler.make_dict())
                overwrite_str = json.dumps(overwrite_content)
                store.clear()

                # tiddlywiki (or html) requires "<" be replaced with \u003C in
                # the script tag.  However `json.dump` turns \u003C into \\u003C
                # and I can find no decent way to fix that.
                # This ugly hack puts in a sentinel where the \u003C should be
                # and after json conversion turns it into \u003C.

                # This is ugly as sin, but I've been fighting with it too long and
                # I have a deadline.
                store.append(overwrite_str.replace("ZZZu003cAAA", r"\u003C"))

        # for tiddler in self._get_json_tiddlers(self.bs4, include_system=True):

        # for tiddler_list in self._get_json_content():
        #     for tiddler_dict in tiddler_list:
        #         tiddler

        return str(new_bs4)

    def test(self):
        from pathlib import Path

        # in_path = Path("examples/esoverse.html")
        # content = in_path.read_text(encoding="utf8")
        # soup = bs4.BeautifulSoup(content, "html.parser")
        # path = Path("tests/out.html")
        # path.write_text(str(soup), encoding="utf8")
        # assert False

        for tiddler in self.tiddlers:
            if tiddler.title == "Charactersxxx":
                print("=strings============")
                content = "\n".join(tiddler._div.strings)

                # print("=decode============")
                # content = tiddler._div.decode_contents()

                print(content)

                div = self.bs4.new_tag("div", **tiddler._div.attrs)
                div.append(content)
                print("-out--------------")
                print(str(div))

                orig_tiddler = self.bs4.find("div", attrs={"title": tiddler.title})
                assert orig_tiddler

                new_tiddler = self.bs4.new_tag("div", **tiddler._div.attrs)
                new_tiddler.append(
                    bs4.BeautifulSoup(f"\n<pre>XXX {content}\n</pre>/n", "html.parser")
                )
                # print(orig_tiddler)
                orig_tiddler.replace_with(new_tiddler)
                print(f'Tiddler "{tiddler.title}" replaced.')

        path = Path("tests/out.html")
        path.write_text(str(self.bs4), encoding="utf8")
        # path.write_text(self.bs4.prettify(formatter="html"), encoding="utf8")

    def remake_legacy(self, new_bs4, delete_list):
        tiddler_index = {tiddler.title: tiddler for tiddler in self.tiddlers}

        store_area = new_bs4.find("div", id="storeArea")
        divs = store_area.find_all("div")

        for div in divs:
            div_tiddler = DivTiddler(div)
            if div_tiddler.title == "Characters":
                print(div_tiddler.text)
                div_tiddler.update_div(new_bs4, tiddler_index[div_tiddler.title])
                print(div_tiddler.text)
                # assert False
            if div_tiddler.is_system():
                continue
            if div_tiddler.title in delete_list:
                print(f"legacy tiddler {div_tiddler.title} deleted")
                div.decompose()
            if div_tiddler.title in tiddler_index:
                new_tiddler = tiddler_index[div_tiddler.title]
                # pre = new_bs4.new_tag("pre")
                # pre.clear()
                pre = bs4.BeautifulSoup(f"<pre>{new_tiddler.text}</pre>", "html.parser")
                div.clear()
                div.append(pre)
                # div_tiddler.update_div(new_bs4, tiddler_index[div_tiddler.title])
                # tiddler_index[div_tiddler.title].update_div(new_bs4, div)
                print(f"legacy tiddler {div_tiddler.title} updated")

        #     orig_tiddler = self.bs4.find("div", attrs={"title": tititle})
        #     if not orig_tiddler:
        #         # print(tiddler.dict())
        #         assert orig_tiddler

        #     if title in delete_list:
        #         orig_tiddler.decompose()
        #         print(f'Tiddler "{title}" removed.')
        #     else:
        #         new_tiddler = self.bs4.new_tag("div", **tiddler.attrs)
        #         new_tiddler.append(bs4.BeautifulSoup(tiddler.raw_text, "html.parser"))
        #         # print(orig_tiddler)
        #         orig_tiddler.replace_with(new_tiddler)
        #         print(f'Tiddler "{title}" replaced.')


# =================================

# def old_remake(self, delete_list: list[str]) -> str:
#     """
#     Will remake a tiddlywiki html content from the parsed data.

#     * Any changes made to the tiddler object will be reflected in the
#         new tiddlywiki
#     * Any Tiddler (identified by title) in the delete list will be
#         removed from the resulting html content.

#     NOTE: Does not handle changing the title.  To do this add a new tiddler to
#         self.tiddlers and pass the old title in the `delete_list`

#     Args:
#         delete_list: list of tiddler titles that should be removed from the
#             new tiddlywiki.

#     Returns:
#         A string representing a html file, modified by changes made to self.tiddlers
#         and the titles passed in to be deleted.
#     """
#     if not self.tiddlers:
#         raise RuntimeError("Can't remake a tiddlywiki until one has been parsed.")

#     for tiddler in self.tiddlers:
#         title = tiddler.div["title"]
#         if not title:
#             raise RuntimeError("Tiddler has no title")

#         orig_tiddler = self.bs4.find("div", attrs={"title": title})
#         if not orig_tiddler:
#             # print(tiddler.dict())
#             assert orig_tiddler

#         if title in delete_list:
#             orig_tiddler.decompose()
#             print(f'Tiddler "{title}" removed.')
#         else:
#             new_tiddler = self.bs4.new_tag("div", **tiddler.attrs)
#             new_tiddler.append(bs4.BeautifulSoup(tiddler.raw_text, "html.parser"))
#             # print(orig_tiddler)
#             orig_tiddler.replace_with(new_tiddler)
#             print(f'Tiddler "{title}" replaced.')

#     return str(self.bs4)
