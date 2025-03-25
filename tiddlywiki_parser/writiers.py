import json
from pathlib import Path


def export(path, export_obj, save_json=False):
    if save_json:
        fp = Path(path)
        # with open(path, "w", encoding='utf8') as fp:
        fp.write_text(
            json.dumps(export_obj, sort_keys=True, indent=4, separators=(",", ": ")),
            encoding="utf8",
        )
    else:
        write_tiddlers(path, export_obj)


def write_tiddlers(path, export_obj):
    for tiddler in export_obj:
        tld_path = Path(path) / f"{tiddler['title']}.tid"
        for key in tiddler:
            if key == "text":
                continue
            tld_path.write_text(f"{key}:  {tiddler[key]}\n", encoding="utf8")
        tld_path.write_text(f"{tiddler['text']}", encoding="utf8")
