import re
from typing import Any

SYSTEM_PREFIX = "$:/"


class Tiddler:
    def __init__(self, tiddler_dict: dict) -> None:
        self._dict = tiddler_dict
        self.title = self.decode_lt(tiddler_dict.get("title", ""))
        self.tags = self.parse_tags(tiddler_dict.get("tags", ""))
        # This is the text as it would be seen in the editor.
        self.text = self.decode_lt(tiddler_dict.get("text", ""))

    @staticmethod
    def encode_lt(st):
        """strings have to have < encoded as \u003c

        # tiddlywiki (or html) requires "<" be replaced with \u003c in
        # the script tag.  However `json.dump` turns \u003c into \\u003C
        # and I can find no decent way to fix that.
        # This ugly hack puts in a sentinel where the \u003c should be
        # and after json conversion turns it into \u003c.

        # This is ugly as sin, but I've been fighting with it too long and
        # I have a deadline.
        """

        return st.replace("<", "ZZZu003cAAA")

    @staticmethod
    def decode_lt(st):
        """strings have to have < encoded as \u003c"""
        # beautiful soup seems to be doing this automatically for us
        return st
        # return st.replace("\\u003C", "<")

    def parse_tags(self, tags_str: str) -> list[str]:
        # Extract contents inside [[ ]]
        matches = re.findall(r"\[\[(.*?)\]\]", tags_str)
        # Remove the multiword tags
        cleaned_text = re.sub(r"\[\[.*?\]\]", "", tags_str).strip()
        # Add them back at the front (convert to list as well)
        tags = matches + cleaned_text.split()
        return [self.decode_lt(st) for st in tags]

    def make_tags(self, tags: list[str]) -> str:
        """The inverse of the parse_tags method."""
        encoded_tags = [
            f"[[{self.encode_lt(tag)}]]" if " " in tag else self.encode_lt(tag)
            for tag in tags
        ]
        return " ".join(encoded_tags)

    def is_system(self):
        return self.title.startswith(SYSTEM_PREFIX)

    def has_tag(self, tag):
        return tag in self.tags

    def make_dict(self):
        new_dict = self._dict.copy()
        new_dict["title"] = self.encode_lt(self.title)
        new_dict["tags"] = self.make_tags(self.tags)
        new_dict["text"] = self.encode_lt(self.text)
        return new_dict


class DivTiddler(Tiddler):
    """
    Pre 5.2.0 div based tiddler

    TODO: subclass Tiddler
    * add make_div function
    * construct a dict from div and call Tiddler.__init__() with it.
    * deal with wrapping in <pre>/unwrapping <pre>
    * turn encode_lt into a nop
    """

    def __init__(self, div: dict[str, Any]) -> None:
        """
        Object representing an individual tiddler.

        Args:
            div: The BS4 div that the tiddler will be built from.
        """
        self._div = div
        print(type(self._div))
        div_dict = div.attrs
        div_dict["text"] = self.unwrap(div)

        super().__init__(div_dict)

    def unwrap(self, div):
        pre = div.find("pre")
        return pre.decode_contents()

    def make_dict(self):
        raise NotImplementedError(
            "calling make_dict on a DivTiddler is probably wrong."
        )

    def update_div(self, bs4, new_tiddler):
        div = self._div
        div.attrs["tags"] = self.make_tags(new_tiddler.tags)
        div.clear()
        pre = bs4.new_tag("pre")
        pre.append(new_tiddler.text)
        div.clear()
        div.append("\n")
        div.append(pre)
        div.append("\n")
        if div.has_attr("text"):
            del div.attrs["text"]
