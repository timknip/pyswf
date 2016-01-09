import argparse
from swf.movie import SWF
from swf.export import SVGExporter, SingleShapeSVGExporterMixin, FrameSVGExporterMixin

parser = argparse.ArgumentParser(description="Convert an SWF file into an SVG")
parser.add_argument("--swf", type=argparse.FileType('rb'),
                    help="Location of SWG file to convert", required=True)
parser.add_argument("--svg", type=argparse.FileType('wb'),
                    help="Location of converted SVG file", required=True)
parser.add_argument("--shape", type=int,
                    help="Only export shape SHAPE (integer)", required=False)
parser.add_argument("--frame", type=int,
                    help="Export frame FRAME (0-based index) instead of frame 0", required=False)

options = parser.parse_args()
argparse.swf_file = options.swf

# load and parse the SWF
swf = SWF(options.swf)

export_opts = {}
export_mixins = []


# process the optional arguments

if options.shape is not None:
    export_mixins.append(SingleShapeSVGExporterMixin)
    export_opts['shape'] = options.shape

if options.frame is not None:
    export_mixins.append(FrameSVGExporterMixin)
    export_opts['frame'] = options.frame

# create the SVG exporter
svg_exporter = SVGExporter()

# NB: Construct the class dynamically, since the chosen options dictate which mixins to use.
svg_exporter.__class__ = type('ThisExporter', tuple(export_mixins + [SVGExporter]), {})

# export!
svg = svg_exporter.export(swf, **export_opts)

# save the SVG
options.svg.write(svg.read())