=====
hxann
=====

convert csv into video annotation


quickstart
===========

::
    # clone this repo
    $> git clone https://github.com/nmaekawa/hxann.git
    $>

    # create and activate a virtualenv
    $> virtualenv -p python3 venv
    $> source venv/bin/activate
    $(venv)>

    # install package
    $(venv)> cd hxann
    $(venv) hxann> pip install .
    $(venv) hxann>

    # check help
    $(venv) hxann> hxann --help
    Usage: hxann [OPTIONS]

    Options:
    --csv TEXT            csv file to be converted, default is stdin
    --fmt [annjs|webann]  format to convert to, default is annjs
    --help                Show this message and exit.


notes on csv input
==================

The csv input is expected to have _newlines_ as row delimiters, and _commas_ as
column delimiters. As a rule of thumb, exporting the spreadsheet as csv from
excell (not csv-utf8!) or google sheets would work.

For the headers, these are relevant, case sensitive, spaces-sensitive:
    - "Start Time"
    - "End Time"
    - "Annotation Text"
    - "Tags"

Times should be in the format "hh:mm:ss". Missing start times are considered to
be "00:00:00". Missing end times are considered to be the same as the start time.
Other date formats will make the script fail, for example, "1.47" or "01m47s"
instead of "00:01:47".

Tags should be separated by _commas_ and commas are not allowed in tags.

--eop



