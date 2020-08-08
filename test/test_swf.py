from __future__ import absolute_import
from swf.movie import SWF
from swf.export import SVGExporter

def test_header():

    f = open('./test/data/test.swf', 'rb')

    swf = SWF(f)

    assert swf.header.frame_count == 1

def test_export():
    f = open('./test/data/test.swf', 'rb')
    swf = SWF(f)

    svg_exporter = SVGExporter()
    svg = svg_exporter.export(swf)

    assert b'<svg xmlns' in svg.read()
