import json
import os


def export(path, export_obj, save_json=False):
    if save_json:
        with open(path, "w", encoding='utf8') as fp:
            fp.write(
                json.dumps(export_obj, sort_keys=True, indent=4, separators=(",", ": "))
            )
    else:
        write_tiddlers(path, export_obj)


def write_tiddlers(path, export_obj):
    for tiddler in export_obj:
        tiddler_path = os.path.join(path, tiddler["title"] + ".tid")
        with open(tiddler_path, "w", encoding='utf8') as fp:
            for key in tiddler:
                if key == "text":
                    continue
                fp.write(f"{key}:  {tiddler[key]}\n")
            fp.write(f"{tiddler['text']}")
