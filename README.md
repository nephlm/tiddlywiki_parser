# tiddlywiki_parser
Parse the tiddler our of a tiddlywiki for backup, git management or anything
else. 

A simple tool to extract the tiddlers from a [Tiddlywiki](https://tiddlywiki.com/) (A personal, non-linear web notebook (aka a wiki in a file)).

TODO: Right now tiddlers are basically just dicts and don't do anything to 
help with data processing.  I'd like to be able to search and extract fields
and tags at the very least.

## Warning 

This is barely more than a hobby project at this point.  I'm turning it into a 
package because I'd like to import it in another project, but if you're using 
a different version of `Tiddlywiki` or use it differently than me, I can't 
suggest, much less promise or guarantee that it will work.

If you have a case where it doesn't work, create an 
[Issue](https://github.com/nephlm/tiddlywiki_parser/issues),
and I'll take a look at it.

## Install

```
pip install tiddlywiki_parser 
```

## Usage

```
import tiddlywiki_parser.readers as readers
import tiddlywiki_parser.writiers as writers
from tiddlywiki_parser.tiddlywiki import TiddlyWiki

raw_content = readers.read('/path/to/tiddlywiki/file')
tiddlywiki = TiddlyWiki(raw_content)
writers.export('/path/to/destination/file.json, tiddlywiki.export_list(), save_json=True)
```

* `readers.read()` can also take a url.
* `TiddlyWiki.tiddlers` is a list of all the Tiddler objects.
* `TiddlyWiki.export_list()` is the same but converted to dicts.
* `TiddlyWiki.parse()` parses the file.  It is run automatically under normal circumstances.
* `TiddlyWiki.remake(delete_list=['title1', 'title2'])`
  * Builds a new tiddlywiki deleting the specified titles, and with any changes 
  made to tiddlers.  Must change raw_text, which is html, not text, which is a 
  clean string. Titles cannot be changed.
* `Tiddler.dict()` returns the dict version of the Tiddler object.
* `writers.export()` will write the tiddlywiki either as individual files or a s a json file. 

## Command Line 

There is a command line packaged with the package.  It will parse a tiddlywiki file and save the tiddlers either as individual files or as a single json file. 

```
usage: tiddlywiki_parser [-h] [--json] source output

positional arguments:
  source      The path to the html file
  output      The path to the output dir (or file).

options:
  -h, --help  show this help message and exit
  --json      Save as a json file instead of as individual tiddlers. output
              must be a dir.
```

`source` can be either a local file or a url.  
`output` is the where the data should be written.  It's either a directory for a writing individual files or a json file if `--json` is specified.

## Packaging

This should now be a proper package, and it uses uv for all the packaging stuff.

