PYSWF
=====
A Python library for reading and writing SWF files.
PYSWF is a Python port of Claus Wahlers *great* SWF parser https://github.com/claus/as3swf
Can't thank Claus enough!

INSTALL
-------

    $ pip install pyswf==1.5.4

or:

    $ git clone git@github.com:timknip/pyswf.git
    $ cd pyswf
    $ python setup.py install

or you might need do:

    $ sudo python setup.py install

WINDOWS
-------
Install Pillow, lxml and pylzma from a binary distribution before running setup.
- [Pillow 2.9.0](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pillow)
- [lxml 3.4.0](https://pypi.python.org/pypi/lxml/3.4.0#downloads)
- [pylzma 0.4.6](http://www.lfd.uci.edu/~gohlke/pythonlibs/#pylzma)

Installing the *.whl files:

    $ pip install the-downloaded.whl

USAGE
-----

Basic example:
--------------
```python
from swf.movie import SWF

# create a file object
file = open('path/to/swf', 'rb')

# print out the SWF file structure
print SWF(file)
```


SVG export example:
-------------------
```python
from swf.movie import SWF
from swf.export import SVGExporter

# create a file object
file = open('path/to/swf', 'rb')

# load and parse the SWF
swf = SWF(file)

# create the SVG exporter
svg_exporter = SVGExporter()

# export!
svg = swf.export(svg_exporter)

# save the SVG
open('path/to/svg', 'wb').write(svg.read())
```
