import re
from typing import Any

SYSTEM_PREFIX = "$:/"


class Tiddler:
    def __init__(self, tiddler_dict: dict) -> None:
        self._orig_dict = tiddler_dict
        self._dict = tiddler_dict.copy()
        self.tags: list[str] = self.parse_tags(tiddler_dict.get("tags", ""))

    def __getitem__(self, item):
        return self._dict[item]

    def __setitem__(self, item, val):
        self._dict[item] = val

    @property
    def original_dict(self):
        return self._orig_dict.copy()

    @property
    def title(self) -> str:
        return self._dict["title"]

    @title.setter
    def title(self, val):
        self._dict["title"] = val

    @property
    def text(self) -> str:
        return self._dict["text"]

    @text.setter
    def text(self, val):
        self._dict["text"] = val

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

    def parse_tags(self, tags_str: str) -> list[str]:
        # Extract contents inside [[ ]]
        matches = re.findall(r"\[\[(.*?)\]\]", tags_str)
        # Remove the multiword tags
        cleaned_text = re.sub(r"\[\[.*?\]\]", "", tags_str).strip()
        # Add them back at the front (convert to list as well)
        tags = matches + cleaned_text.split()
        return tags

    def make_tags(self, tags: list[str], set_sentinel=False) -> str:
        """The inverse of the parse_tags method."""
        if set_sentinel:
            encoded_tags = [
                f"[[{self.encode_lt(tag)}]]" if " " in tag else self.encode_lt(tag)
                for tag in tags
            ]
        else:
            encoded_tags = [f"[[{tag}]]" if " " in tag else tag for tag in tags]
        return " ".join(encoded_tags)

    def is_system(self):
        return self.title.startswith(SYSTEM_PREFIX)

    def has_tag(self, tag):
        return tag in self.tags

    def make_dict(self, set_sentinel: bool = False) -> dict[str, str]:
        """
        Returns a dictionary containing all the tiddler fields.  Probably contains
        'title', 'tags', 'created', 'modified' and 'text', but may contain more.

        Args:
            set_sentinel: Whether to encode the output using encode_lt which will put
            a sentinel value in the place of '<' to be replaced after json encoding or
            or return the direct string if set to False. Defaults to False.

        Returns:
            Dictionary representation of the tiddler.
        """
        new_dict = self._dict.copy()
        new_dict["tags"] = self.make_tags(self.tags, set_sentinel)
        if set_sentinel:
            for key in new_dict:
                if key == "tags":
                    continue
                else:
                    new_dict[key] = self.encode_lt(self._dict[key])
        return new_dict


class DivTiddler(Tiddler):
    """
    Pre 5.2.0 div based tiddler

    """

    def __init__(self, div: dict[str, Any]) -> None:
        """
        Object representing an individual tiddler.

        Args:
            div: The BS4 div that the tiddler will be built from.
        """
        self._div = div
        div_dict = div.attrs
        div_dict["text"] = self.unwrap(div)

        super().__init__(div_dict)

    def unwrap(self, div):
        """pre 5.2.0 the tiddler content is wrapped in pre."""
        pre = div.find("pre")
        return "\n".join(pre.strings)
