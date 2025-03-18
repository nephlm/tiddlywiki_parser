from typing import Self

import bs4

from tiddlywiki_parser.tiddler import Tiddler


class TiddlyWiki(object):
    def __init__(self, content: str):
        """
        Object representing the tiddlywiki as a whole.

        Args:
            content: raw complete text of the tiddlywiki file.
        """
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

    def parse(self) -> list[Tiddler]:
        """
        Use bs4 to parse out the div instances that are tiddlers.

        returns:
            List of user Tiddlers.
        """
        self.bs4 = bs4.BeautifulSoup(self.content, "html.parser")
        divs = self.bs4.find_all("div")
        for div in divs:
            if self._filter_div(div):
                print(div["title"])
                tiddler = Tiddler(div)
                self.tiddlers.append(tiddler)
        self.tiddlers = sorted(self.tiddlers, key=lambda t: t.attrs["title"])
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
        return [tiddler.dict() for tiddler in self.tiddlers]

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
        if not self.tiddlers:
            raise RuntimeError("Can't remake a tiddlywiki until one has been parsed.")

        for tiddler in self.tiddlers:
            title = tiddler.div["title"]
            if not title:
                raise RuntimeError("Tiddler has no title")

            orig_tiddler = self.bs4.find("div", attrs={"title": title})
            if not orig_tiddler:
                # print(tiddler.dict())
                assert orig_tiddler

            if title in delete_list:
                orig_tiddler.decompose()
                print(f'Tiddler "{title}" removed.')
            else:
                new_tiddler = self.bs4.new_tag("div", **tiddler.attrs)
                new_tiddler.append(bs4.BeautifulSoup(tiddler.raw_text, "html.parser"))
                # print(orig_tiddler)
                orig_tiddler.replace_with(new_tiddler)
                print(f'Tiddler "{title}" replaced.')

        return str(self.bs4)
