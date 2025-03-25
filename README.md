# tiddlywiki_parser
Parse the tiddler our of a tiddlywiki for backup, git management or anything
else. 

A simple tool to extract the tiddlers from a single file  
[Tiddlywiki](https://tiddlywiki.com/) (A personal, non-linear 
web notebook (aka a wiki in a file)).


## Warning 

This is barely more than a hobby project at this point.  I'm turning 
it into a package because I'd like to import it in another project, 
but if you're using a different version of `Tiddlywiki` 
or use it differently than me, I can't suggest, 
much less promise or guarantee that it will work.

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
  made to tiddlers.   Titles cannot be changed.
* `Tiddler.dict()` returns the dict version of the Tiddler object.
* `writers.export()` will write the tiddlywiki either as individual files or a s a json file. 

## Limitations

tiddlywiki 5.2.0 changed how tiddlers are stored.  v1.x only deals with 
tiddlywiki files that are pre-5.2.0.  Hopefully v2.x can deal 
with pre- and post-5.2.0.  

tiddlywiki does allow storing tiddlers 
in both the old and new form in the same file, this library doesn't 
handle that case (or any sort of modifying pre 5.2.0 wikis). 

Only handles parsing single file tiddlywiki files. 

`remake` is highly experimental and doesn't deal with:

* adding a new tiddler
* renaming tiddlers
* pre-5.2.0 wikis
* probably a bunch of other cases. 

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

`source` can be either a local file or an url.  
`output` is the where the data should be written.  It's either a directory for a writing individual files or a json file if `--json` is specified.

## Packaging

This should now be a proper package, and it uses uv for all the packaging stuff.

