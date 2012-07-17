import argparse
from swf.movie import SWF
from swf.export import SVGExporter

parser = argparse.ArgumentParser(description="Convert an SWF file into an SVG")
parser.add_argument("--swf", type=argparse.FileType('rb'),
                    help="Location of SWG file to convert", required=True)
parser.add_argument("--svg", type=argparse.FileType('wb'),
                    help="Location of converted SVG file", required=True)

options = parser.parse_args()
argparse.swf_file = options.swf

# load and parse the SWF
swf = SWF(options.swf)

# create the SVG exporter
svg_exporter = SVGExporter()

# export!
svg = swf.export(svg_exporter)

# save the SVG
options.svg.write(svg.read())