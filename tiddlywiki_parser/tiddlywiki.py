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
