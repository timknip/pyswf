PYSWF
=====
A Python library for reading and writing SWF files.
PYSWF is a Python port of Claus Wahlers *great* SWF parser https://github.com/claus/as3swf
Can't thank Claus enough!

INSTALL
=======

    python setup.py install

or you might need do:

    $sudo python setup.py install

DEPENDENCIES
============
- lxml
- StringIO
- Image (PIL)

You can use easy_install or pip to install these.
NOTE: this code is only tested with python 2.6

USAGE
=====

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