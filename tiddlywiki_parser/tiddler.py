from typing import Any


class Tiddler(object):
    def __init__(self, div: dict[str, Any]) -> None:
        """
        Object representing an individual tiddler.

        Args:
            div: The BS4 div that the tiddler will be built from.
        """
        self.div = div

        self.attrs = div.attrs
        self.text = div.text
        self.raw_text = div.decode_contents() 

    def dict(self) -> dict:
        tiddler_dict = self.attrs.copy()
        tiddler_dict["text"] = self.text
        return tiddler_dict
