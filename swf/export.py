"""
This module defines exporters for the SWF fileformat.
"""
from consts import *
from geom import *
from utils import *
from data import *
from tag import *
from filters import *
from lxml import objectify
from lxml import etree
import base64
import Image
from StringIO import StringIO
import math
import re
import copy
 
SVG_VERSION = "1.1"
SVG_NS      = "http://www.w3.org/2000/svg"
XLINK_NS    = "http://www.w3.org/1999/xlink"
XLINK_HREF  = "{%s}href" % XLINK_NS
NS = {"svg" : SVG_NS, "xlink" : XLINK_NS}

MINIMUM_STROKE_WIDTH = 1.0

CAPS_STYLE = {
    0 : 'round',
    1 : 'butt',
    2 : 'square'
}

JOIN_STYLE = {
    0 : 'round',
    1 : 'bevel',
    2 : 'miter'
}
                
class DefaultShapeExporter(object):
    """
    The default (abstract) Shape exporter class. 
    All shape exporters should extend this class.
    
    
    """
    def __init__(self, swf=None, debug=False, force_stroke=False):
        self.swf = None
        self.debug = debug
        self.force_stroke = force_stroke
        
    def begin_bitmap_fill(self, bitmap_id, matrix=None, repeat=False, smooth=False):
        pass
    def begin_fill(self, color, alpha=1.0):
        pass
    def begin_gradient_fill(self, type, colors, alphas, ratios, 
                            matrix=None, 
                            spreadMethod=SpreadMethod.PAD, 
                            interpolationMethod=InterpolationMethod.RGB,
                            focalPointRatio=0.0):
        pass
    def line_style(self,
                    thickness=float('nan'), color=0, alpha=1.0, 
                    pixelHinting=False, 
                    scaleMode=LineScaleMode.NORMAL, 
                    startCaps=None, endCaps=None, 
                    joints=None, miterLimit=3.0):
        pass
    def line_gradient_style(self,
                    thickness=float('nan'), color=0, alpha=1.0, 
                    pixelHinting=False,
                    scaleMode=LineScaleMode.NORMAL,
                    startCaps=None, endCaps=None,
                    joints=None, miterLimit=3.0,
                    type = 1, colors = [], alphas = [], ratios = [],
                    matrix=None,
                    spreadMethod=SpreadMethod.PAD,
                    interpolationMethod=InterpolationMethod.RGB,
                    focalPointRatio=0.0):
        pass
    def line_bitmap_style(self,
                    thickness=float('nan'),
                    pixelHinting=False, 
                    scaleMode=LineScaleMode.NORMAL, 
                    startCaps=None, endCaps=None, 
                    joints=None, miterLimit = 3.0,
                    bitmap_id=None, matrix=None, repeat=False, smooth=False):
        pass   
    def end_fill(self):
        pass
            
    def begin_fills(self):
        pass
    def end_fills(self):
        pass
    def begin_lines(self):
        pass
    def end_lines(self):
        pass
            
    def begin_shape(self):
        pass
    def end_shape(self):
        pass
        
    def move_to(self, x, y):
        #print "move_to", x, y
        pass
    def line_to(self, x, y):
        #print "line_to", x, y
        pass
    def curve_to(self, cx, cy, ax, ay):
        #print "curve_to", cx, cy, ax, ay
        pass

class DefaultSVGShapeExporter(DefaultShapeExporter):
    def __init__(self, defs=None):
        self.defs = defs
        self.current_draw_command = ""
        self.path_data = ""
        self._e = objectify.ElementMaker(annotate=False,
                        namespace=SVG_NS, nsmap={None : SVG_NS, "xlink" : XLINK_NS})
        super(DefaultSVGShapeExporter, self).__init__()
    
    def move_to(self, x, y):
        self.current_draw_command = ""
        self.path_data += "M" + \
            str(NumberUtils.round_pixels_20(x)) + " " + \
            str(NumberUtils.round_pixels_20(y)) + " "
        
    def line_to(self, x, y):
        if self.current_draw_command != "L":
            self.current_draw_command = "L"
            self.path_data += "L"
        self.path_data += "" + \
            str(NumberUtils.round_pixels_20(x)) + " " + \
            str(NumberUtils.round_pixels_20(y)) + " "
        
    def curve_to(self, cx, cy, ax, ay):
        if self.current_draw_command != "Q":
            self.current_draw_command = "Q"
            self.path_data += "Q"
        self.path_data += "" + \
            str(NumberUtils.round_pixels_20(cx)) + " " + \
            str(NumberUtils.round_pixels_20(cy)) + " " + \
            str(NumberUtils.round_pixels_20(ax)) + " " + \
            str(NumberUtils.round_pixels_20(ay)) + " "
        
    def begin_bitmap_fill(self, bitmap_id, matrix=None, repeat=False, smooth=False):
        self.finalize_path()
        
    def begin_fill(self, color, alpha=1.0):
        self.finalize_path()
    
    def end_fill(self):
        pass
        #self.finalize_path()
    
    def begin_fills(self):
        pass
    def end_fills(self):
        self.finalize_path()
            
    def begin_gradient_fill(self, type, colors, alphas, ratios, 
                            matrix=None, 
                            spreadMethod=SpreadMethod.PAD, 
                            interpolationMethod=InterpolationMethod.RGB,
                            focalPointRatio=0.0):
        self.finalize_path()
        
    def line_style(self,
                    thickness=float('nan'), color=0, alpha=1.0, 
                    pixelHinting=False, 
                    scaleMode=LineScaleMode.NORMAL, 
                    startCaps=None, endCaps=None, 
                    joints=None, miterLimit=3.0):
        self.finalize_path()
                       
    def end_lines(self):
        self.finalize_path()
    
    def end_shape(self):
        self.finalize_path()
            
    def finalize_path(self):
        self.current_draw_command = ""
        self.path_data = ""
        
class SVGShapeExporter(DefaultSVGShapeExporter):
    def __init__(self):
        self.path = None
        self.num_patterns = 0
        self.num_gradients = 0
        self._gradients = {}
        self._gradient_ids = {}
        self.paths = {}
        self.fills_ended = False
        super(SVGShapeExporter, self).__init__()
        
    def begin_shape(self):
        self.g = self._e.g()
         
    def begin_fill(self, color, alpha=1.0):
        self.finalize_path()
        self.path.set("fill", ColorUtils.to_rgb_string(color))
        if alpha < 1.0:
            self.path.set("fill-opacity", str(alpha))
        elif self.force_stroke:
            self.path.set("stroke", ColorUtils.to_rgb_string(color))
            self.path.set("stroke-width", "1")
        else:
            self.path.set("stroke", "none")
            
    def begin_gradient_fill(self, type, colors, alphas, ratios, 
                            matrix=None, 
                            spreadMethod=SpreadMethod.PAD, 
                            interpolationMethod=InterpolationMethod.RGB,
                            focalPointRatio=0.0):
        self.finalize_path()
        gradient_id = self.export_gradient(type, colors, alphas, ratios, matrix, spreadMethod, interpolationMethod, focalPointRatio)
        self.path.set("stroke", "none")    
        self.path.set("fill", "url(#%s)" % gradient_id)
        
    def export_gradient(self, type, colors, alphas, ratios, 
                        matrix=None, 
                        spreadMethod=SpreadMethod.PAD,
                        interpolationMethod=InterpolationMethod.RGB,
                        focalPointRatio=0.0):
        self.num_gradients += 1
        gradient_id = "gradient%d" % self.num_gradients
        gradient = self._e.linearGradient() if type == GradientType.LINEAR \
            else self._e.radialGradient()
        gradient.set("gradientUnits", "userSpaceOnUse")
        
        if type == GradientType.LINEAR:
            gradient.set("x1", "-819.2")
            gradient.set("x2", "819.2")
        else:
            gradient.set("r", "819.2")
            gradient.set("cx", "0")
            gradient.set("cy", "0")
            if focalPointRatio < 0.0 or focalPointRatio > 0.0:
                gradient.set("fx", str(819.2 * focalPointRatio))
                gradient.set("fy", "0")
        
        if spreadMethod == SpreadMethod.PAD:
            gradient.set("spreadMethod", "pad")
        elif spreadMethod == SpreadMethod.REFLECT:
            gradient.set("spreadMethod", "reflect")
        elif spreadMethod == SpreadMethod.REPEAT:
            gradient.set("spreadMethod", "repeat")
        
        if interpolationMethod == InterpolationMethod.LINEAR_RGB:
            gradient.set("color-interpolation", "linearRGB")
            
        if matrix is not None:
            sm = _swf_matrix_to_svg_matrix(matrix)
            gradient.set("gradientTransform", sm);
        
        for i in range(0, len(colors)):
            entry = self._e.stop()
            offset = ratios[i] / 255.0
            entry.set("offset", str(offset))
            if colors[i] != 0.0:
                entry.set("stop-color", ColorUtils.to_rgb_string(colors[i]))
            if alphas[i] != 1.0:
                entry.set("stop-opacity", str(alphas[i]))
            gradient.append(entry)
        
        # prevent same gradient in <defs />
        key = etree.tostring(gradient)
        if key in self._gradients:
            gradient_id = self._gradient_ids[key]
        else:
            self._gradients[key] = copy.copy(gradient)
            self._gradient_ids[key] = gradient_id
            gradient.set("id", gradient_id)
            self.defs.append(gradient)
            
        return gradient_id
        
    def export_pattern(self, bitmap_id, matrix, repeat=False, smooth=False):
        self.num_patterns += 1
        bitmap_id = "c%d" % bitmap_id
        e = self.defs.xpath("./svg:image[@id='%s']" % bitmap_id, namespaces=NS)
        if len(e) < 1:
            raise Exception("SVGShapeExporter::begin_bitmap_fill Could not find bitmap!")
        image = e[0]
        pattern_id = "pat%d" % (self.num_patterns)
        pattern = self._e.pattern()
        pattern.set("id", pattern_id)
        pattern.set("width", image.get("width"))
        pattern.set("height", image.get("height"))
        pattern.set("patternUnits", "userSpaceOnUse")
        #pattern.set("patternContentUnits", "objectBoundingBox")
        if matrix is not None:
            pattern.set("patternTransform", _swf_matrix_to_svg_matrix(matrix, True, True, True))
            pass
        use = self._e.use()
        use.set(XLINK_HREF, "#%s" % bitmap_id)
        pattern.append(use)
        self.defs.append(pattern)
        
        return pattern_id
        
    def begin_bitmap_fill(self, bitmap_id, matrix=None, repeat=False, smooth=False):
        self.finalize_path()
        pattern_id = self.export_pattern(bitmap_id, matrix, repeat, smooth)
        self.path.set("stroke", "none")    
        self.path.set("fill", "url(#%s)" % pattern_id)
         
    def line_style(self,
                    thickness=float('nan'), color=0, alpha=1.0, 
                    pixelHinting=False, 
                    scaleMode=LineScaleMode.NORMAL, 
                    startCaps=None, endCaps=None, 
                    joints=None, miterLimit=3.0):
        self.finalize_path()
        self.path.set("fill", "none")
        self.path.set("stroke", ColorUtils.to_rgb_string(color))
        thickness = 1 if math.isnan(thickness) else thickness
        thickness = MINIMUM_STROKE_WIDTH if thickness < MINIMUM_STROKE_WIDTH else thickness
        self.path.set("stroke-width", str(thickness))
        if alpha < 1.0:
            self.path.set("stroke-opacity", str(alpha))

    def line_gradient_style(self,
                    thickness=float('nan'),
                    pixelHinting = False, 
                    scaleMode=LineScaleMode.NORMAL, 
                    startCaps=0, endCaps=0, 
                    joints=0, miterLimit=3.0,
                    type = 1,
                    colors = [],
                    alphas = [],
                    ratios = [], 
                    matrix=None,
                    spreadMethod=SpreadMethod.PAD,
                    interpolationMethod=InterpolationMethod.RGB,
                    focalPointRatio=0.0):
        self.finalize_path()
        gradient_id = self.export_gradient(type, colors, alphas, ratios, matrix, spreadMethod, interpolationMethod, focalPointRatio)
        self.path.set("fill", "none")
        self.path.set("stroke-linejoin", JOIN_STYLE[joints])
        self.path.set("stroke-linecap", CAPS_STYLE[startCaps])
        self.path.set("stroke", "url(#%s)" % gradient_id)
        thickness = 1 if math.isnan(thickness) else thickness
        thickness = MINIMUM_STROKE_WIDTH if thickness < MINIMUM_STROKE_WIDTH else thickness
        self.path.set("stroke-width", str(thickness))
    
    def line_bitmap_style(self,
                    thickness=float('nan'),
                    pixelHinting=False, 
                    scaleMode=LineScaleMode.NORMAL, 
                    startCaps=None, endCaps=None, 
                    joints=None, miterLimit = 3.0,
                    bitmap_id=None, matrix=None, repeat=False, smooth=False):
        self.finalize_path()
        pattern_id = self.export_pattern(bitmap_id, matrix, repeat, smooth)
        self.path.set("fill", "none")
        self.path.set("stroke", "url(#%s)" % pattern_id)
        self.path.set("stroke-linejoin", JOIN_STYLE[joints])
        self.path.set("stroke-linecap", CAPS_STYLE[startCaps])
        thickness = 1 if math.isnan(thickness) else thickness
        thickness = MINIMUM_STROKE_WIDTH if thickness < MINIMUM_STROKE_WIDTH else thickness
        self.path.set("stroke-width", str(thickness))
        
    def begin_fills(self):
        self.fills_ended = False
    def end_fills(self):
        self.finalize_path()
        self.fills_ended = True
                                                         
    def finalize_path(self):
        if self.path is not None and len(self.path_data) > 0:
            self.path_data = self.path_data.rstrip()
            self.path.set("d", self.path_data)
            self.g.append(self.path)
        self.path = self._e.path()
        super(SVGShapeExporter, self).finalize_path()


class BaseExporter(object):
    def __init__(self, swf=None, shape_exporter=None, force_stroke=False):
        self.shape_exporter = SVGShapeExporter() if shape_exporter is None else shape_exporter
        self.clip_depth = 0
        self.mask_id = None
        self.jpegTables = None
        self.force_stroke = force_stroke
        if swf is not None:
            self.export(swf)
            
    def export(self, swf, force_stroke=False):
        self.force_stroke = force_stroke
        self.export_define_shapes(swf.tags)
        self.export_display_list(self.get_display_tags(swf.tags))
        
    def export_define_bits(self, tag):
        png_buffer = StringIO()
        image = None
        if isinstance(tag, TagDefineBitsJPEG3):
            
            tag.bitmapData.seek(0)
            tag.bitmapAlphaData.seek(0, 2)
            num_alpha = tag.bitmapAlphaData.tell()
            tag.bitmapAlphaData.seek(0)
            image = Image.open(tag.bitmapData)
            if num_alpha > 0:
                image_width = image.size[0]
                image_height = image.size[1]
                image_data = image.getdata()
                image_data_len = len(image_data)
                if num_alpha == image_data_len:
                    buff = ""
                    for i in range(0, num_alpha):
                        alpha = ord(tag.bitmapAlphaData.read(1))
                        rgb = list(image_data[i])
                        buff += struct.pack("BBBB", rgb[0], rgb[1], rgb[2], alpha)
                    image = Image.fromstring("RGBA", (image_width, image_height), buff)
        elif isinstance(tag, TagDefineBitsJPEG2):
            tag.bitmapData.seek(0)
            image = Image.open(tag.bitmapData)
        else:
            tag.bitmapData.seek(0)
            if self.jpegTables is not None:
                buff = StringIO()
                self.jpegTables.seek(0)
                buff.write(self.jpegTables.read())
                buff.write(tag.bitmapData.read())
                buff.seek(0)
                image = Image.open(buff)
            else:
                image = Image.open(tag.bitmapData)
            
        self.export_image(tag, image)
    
    def export_define_bits_lossless(self, tag):
        image = Image.open(tag.bitmapData)
        self.export_image(tag, image)
        
    def export_define_sprite(self, tag, parent=None):
        display_tags = self.get_display_tags(tag.tags)
        self.export_display_list(display_tags, parent)
            
    def export_define_shape(self, tag):
        self.shape_exporter.debug = isinstance(tag, TagDefineShape4)
        tag.shapes.export(self.shape_exporter)
        
    def export_define_shapes(self, tags):
        for tag in tags:
            if isinstance(tag, SWFTimelineContainer):
                self.export_define_sprite(tag)
                self.export_define_shapes(tag.tags)
            elif isinstance(tag, TagDefineShape):
                self.export_define_shape(tag)
            elif isinstance(tag, TagJPEGTables):
                if tag.length > 0:
                    self.jpegTables = tag.jpegTables
            elif isinstance(tag, TagDefineBits):
                self.export_define_bits(tag)
            elif isinstance(tag, TagDefineBitsLossless):
                self.export_define_bits_lossless(tag)
                  
    def export_display_list(self, tags, parent=None):
        self.clip_depth = 0
        for tag in tags:
            self.export_display_list_item(tag, parent)
    
    def export_display_list_item(self, tag, parent=None):
        pass
    
    def export_image(self, tag, image=None):
        pass
        
    def get_display_tags(self, tags, z_sorted=True):
        dp_tuples = []
        for tag in tags:
            if isinstance(tag, TagPlaceObject):
                dp_tuples.append((tag, tag.depth))
            elif isinstance(tag, TagShowFrame):
                break
        if z_sorted:
            dp_tuples = sorted(dp_tuples, key=lambda tag_info: tag_info[1])
        display_tags = []
        for item in dp_tuples:
            display_tags.append(item[0])
        return display_tags
    
    def serialize(self):
        return None
        
class SVGExporter(BaseExporter):
    def __init__(self, swf=None, margin=0):
        self._e = objectify.ElementMaker(annotate=False,
                        namespace=SVG_NS, nsmap={None : SVG_NS, "xlink" : XLINK_NS})
        self._margin = margin
        super(SVGExporter, self).__init__(swf)
        
    def export(self, swf, force_stroke=False):
        """ Exports the specified SWF to SVG.
        
        @param swf  The SWF.
        @param force_stroke Whether to force strokes on non-stroked fills.
        """
        self.svg = self._e.svg(version=SVG_VERSION)
        self.force_stroke = force_stroke
        self.defs = self._e.defs()
        self.root = self._e.g()
        self.svg.append(self.defs)
        self.svg.append(self.root)
        self.shape_exporter.defs = self.defs
        self._num_filters = 0
        
        # GO!
        super(SVGExporter, self).export(swf, force_stroke)
        
        # Setup svg @width, @height and @viewBox
        # and add the optional margin
        self.bounds = SVGBounds(self.svg)
        self.svg.set("width", "%dpx" % round(self.bounds.width))
        self.svg.set("height", "%dpx" % round(self.bounds.height))
        if self._margin > 0:
            self.bounds.grow(self._margin)
        vb = [self.bounds.minx, self.bounds.miny, 
              self.bounds.width, self.bounds.height]
        self.svg.set("viewBox", "%s" % " ".join(map(str,vb)))
        
        # Return the SVG as StringIO
        return self._serialize()
    
    def _serialize(self):
        return StringIO(etree.tostring(self.svg,
                encoding="UTF-8", xml_declaration=True))
                
    def export_define_sprite(self, tag, parent=None):
        id = "c%d"%tag.characterId
        g = self._e.g(id=id)
        self.defs.append(g)
        self.clip_depth = 0
        super(SVGExporter, self).export_define_sprite(tag, g)
            
    def export_define_shape(self, tag):
        self.shape_exporter.force_stroke = self.force_stroke
        super(SVGExporter, self).export_define_shape(tag)
        shape = self.shape_exporter.g
        shape.set("id", "c%d" % tag.characterId)
        self.defs.append(shape)
    
    def export_display_list_item(self, tag, parent=None):
        g = self._e.g()
        use = self._e.use()

        if tag.hasMatrix:
            use.set("transform", _swf_matrix_to_svg_matrix(tag.matrix))
        if tag.hasClipDepth:
            self.mask_id = "mask%d" % tag.characterId
            self.clip_depth = tag.clipDepth
            g = self._e.mask(id=self.mask_id)
            # make sure the mask is completely filled white
            paths = self.defs.xpath("./svg:g[@id='c%d']/svg:path" % tag.characterId, namespaces=NS)
            for path in paths:
                path.set("fill", "#ffffff")
        elif tag.depth <= self.clip_depth:
            g.set("mask", "url(#%s)" % self.mask_id)

        filters = []
        filter_cxform = None
        self._num_filters += 1
        filter_id = "filter%d" % self._num_filters
        svg_filter = self._e.filter(id=filter_id)

        if tag.hasColorTransform:
            filter_cxform = self.export_color_transform(tag.colorTransform, svg_filter)
            filters.append(filter_cxform) 
        if tag.hasFilterList and len(tag.filters) > 0:
            cxform = "color-xform" if tag.hasColorTransform else None
            f = self.export_filters(tag, svg_filter, cxform)
            if len(f) > 0:
                filters.extend(f)
        if tag.hasColorTransform or (tag.hasFilterList and len(filters) > 0):
            self.defs.append(svg_filter)
            use.set("filter", "url(#%s)" % filter_id)
            
        use.set(XLINK_HREF, "#c%s" % tag.characterId)
        g.append(use)
        if parent is not None:
            parent.append(g)
        else:
            self.root.append(g)
        return use
        
    def export_color_transform(self, cxform, svg_filter, result='color-xform'):
        fe_cxform = self._e.feColorMatrix()
        fe_cxform.set("in", "SourceGraphic")
        fe_cxform.set("type", "matrix")
        fe_cxform.set("values", " ".join(map(str, cxform.matrix)))
        fe_cxform.set("result", "cxform")
        
        fe_composite = self._e.feComposite(operator="in")
        fe_composite.set("in2", "SourceGraphic")
        fe_composite.set("result", result)
        
        svg_filter.append(fe_cxform)
        svg_filter.append(fe_composite)
        return result
    
    def export_filters(self, tag, svg_filter, cxform=None):
        num_filters = len(tag.filters)
        elements = []
        attr_in = None
        for i in range(0, num_filters):
            swf_filter = tag.filters[i]
            #print swf_filter
            if isinstance(swf_filter, FilterDropShadow):
                elements.append(self.export_filter_dropshadow(swf_filter, svg_filter, cxform))
                #print swf_filter.strength
                pass
            elif isinstance(swf_filter, FilterBlur):
                pass
            elif isinstance(swf_filter, FilterGlow):
                #attr_in = SVGFilterFactory.export_glow_filter(self._e, svg_filter, attr_in=attr_in)
                #elements.append(attr_in)
                pass
            elif isinstance(swf_filter, FilterBevel):
                pass
            elif isinstance(swf_filter, FilterGradientGlow):
                pass
            elif isinstance(swf_filter, FilterConvolution):
                pass
            elif isinstance(swf_filter, FilterColorMatrix):
                attr_in = SVGFilterFactory.export_color_matrix_filter(self._e, svg_filter, swf_filter.colorMatrix, svg_filter, attr_in=attr_in)
                elements.append(attr_in)
                pass
            elif isinstance(swf_filter, FilterGradientBevel):
                pass
            else:
                raise Exception("unknown filter: ", swf_filter)
        return elements
    
#   <filter id="test-filter" x="-50%" y="-50%" width="200%" height="200%">
#		<feGaussianBlur in="SourceAlpha" stdDeviation="6" result="blur"/>
#		<feOffset dy="0" dx="0"/>
#		<feComposite in2="SourceAlpha" operator="arithmetic"
#			k2="-1" k3="1" result="shadowDiff"/>
#		<feFlood flood-color="black" flood-opacity="1"/>
#		<feComposite in2="shadowDiff" operator="in"/>	
#	</filter>;
        			
    def export_filter_dropshadow(self, swf_filter, svg_filter, blend_in=None, result="offsetBlur"):
        gauss = self._e.feGaussianBlur()
        gauss.set("in", "SourceAlpha")
        gauss.set("stdDeviation", "6")
        gauss.set("result", "blur")
        if swf_filter.knockout:
            composite0 = self._e.feComposite(
                in2="SourceAlpha", operator="arithmetic",
                k2="-1", k3="1", result="shadowDiff")
            flood = self._e.feFlood()
            flood.set("flood-color", "black")
            flood.set("flood-opacity", "1")
            composite1 = self._e.feComposite(
                in2="shadowDiff", operator="in", result=result)
            svg_filter.append(gauss)
            svg_filter.append(composite0)
            svg_filter.append(flood)
            svg_filter.append(composite1)
        else:
            SVGFilterFactory.create_drop_shadow_filter(self._e, svg_filter, 
                None, 
                swf_filter.blurX/20.0, 
                swf_filter.blurY/20.0,
                blend_in,
                result)
        #print etree.tostring(svg_filter, pretty_print=True)
        return result
        
    def export_image(self, tag, image=None):
        if image is not None:
            buff = StringIO()
            image.save(buff, "PNG")
            buff.seek(0)
            data_url = _encode_png(buff.read())
            img = self._e.image()
            img.set("id", "c%s" % tag.characterId)
            img.set("x", "0")
            img.set("y", "0 ")
            img.set("width", "%s" % str(image.size[0]))
            img.set("height", "%s" % str(image.size[1]))
            img.set(XLINK_HREF, "%s" % data_url)
            self.defs.append(img)

class SVGFilterFactory(object):
    # http://commons.oreilly.com/wiki/index.php/SVG_Essentials/Filters
    # http://dev.opera.com/articles/view/svg-evolution-3-applying-polish/

    @classmethod
    def create_drop_shadow_filter(cls, e, filter, attr_in=None, blurX=0, blurY=0, blend_in=None, result=None):
        gaussianBlur = SVGFilterFactory.create_gaussian_blur(e, attr_deviaton="1", result="blur-out")
        offset = SVGFilterFactory.create_offset(e, "blur-out", blurX, blurY, "the-shadow")
        blend = SVGFilterFactory.create_blend(e, blend_in, attr_in2="the-shadow", result=result)
        filter.append(gaussianBlur)
        filter.append(offset)
        filter.append(blend)
        return result
        
    @classmethod
    def export_color_matrix_filter(cls, e, filter, matrix, svg_filter, attr_in=None, result='color-matrix'):
        attr_in = "SourceGraphic" if attr_in is None else attr_in
        fe_cxform = e.feColorMatrix()
        fe_cxform.set("in", attr_in)
        fe_cxform.set("type", "matrix")
        fe_cxform.set("values", " ".join(map(str, matrix)))
        fe_cxform.set("result", result)
        filter.append(fe_cxform)
        #print etree.tostring(filter, pretty_print=True)
        return result
    
    @classmethod
    def export_glow_filter(cls, e, filter, attr_in=None, result="glow-out"):
        attr_in = "SourceGraphic" if attr_in is None else attr_in
        gaussianBlur = SVGFilterFactory.create_gaussian_blur(e, attr_in=attr_in, attr_deviaton="1", result=result)
        filter.append(gaussianBlur)
        return result
        
    @classmethod
    def create_blend(cls, e, attr_in=None, attr_in2="BackgroundImage", mode="normal", result=None):
        blend = e.feBlend()
        attr_in = "SourceGraphic" if attr_in is None else attr_in
        blend.set("in", attr_in)
        blend.set("in2", attr_in2)
        blend.set("mode", mode)
        if result is not None:
            blend.set("result", result)
        return blend
        
    @classmethod
    def create_gaussian_blur(cls, e, attr_in="SourceAlpha", attr_deviaton="3", result=None):
        gaussianBlur = e.feGaussianBlur()
        gaussianBlur.set("in", attr_in)
        gaussianBlur.set("stdDeviation", attr_deviaton)
        if result is not None:
            gaussianBlur.set("result", result)
        return gaussianBlur
        
    @classmethod
    def create_offset(cls, e, attr_in=None, dx=0, dy=0, result=None):
        offset = e.feOffset()
        if attr_in is not None:
            offset.set("in", attr_in)
        offset.set("dx", "%d" % round(dx))
        offset.set("dy", "%d" % round(dy))
        if result is not None:
            offset.set("result", result)
        return offset
        
class SVGBounds(object):
    def __init__(self, svg=None):
        self.minx = 1000000.0
        self.miny = 1000000.0
        self.maxx = -self.minx
        self.maxy = -self.miny
        self._stack = []
        self._matrix = self._calc_combined_matrix()
        if svg is not None:
            self._svg = svg;
            self._parse(svg)

    def add_point(self, x, y):
        self.minx = x if x < self.minx else self.minx
        self.miny = y if y < self.miny else self.miny
        self.maxx = x if x > self.maxx else self.maxx
        self.maxy = y if y > self.maxy else self.maxy

    def set(self, minx, miny, maxx, maxy):
        self.minx = minx
        self.miny = miny
        self.maxx = maxx
        self.maxy = maxy

    def grow(self, margin):
        self.minx -= margin
        self.miny -= margin
        self.maxx += margin
        self.maxy += margin

    @property
    def height(self):
        return self.maxy - self.miny

    def merge(self, other):
        self.minx = other.minx if other.minx < self.minx else self.minx
        self.miny = other.miny if other.miny < self.miny else self.miny
        self.maxx = other.maxx if other.maxx > self.maxx else self.maxx
        self.maxy = other.maxy if other.maxy > self.maxy else self.maxy

    def shrink(self, margin):
        self.minx += margin
        self.miny += margin
        self.maxx -= margin
        self.maxy -= margin

    @property
    def width(self):
        return self.maxx - self.minx

    def _parse(self, element):

        if element.get("transform") and element.get("transform").find("matrix") < 0:
            pass

        if element.get("transform") and element.get("transform").find("matrix") >= 0:
            self._push_transform(element.get("transform"))

        if element.tag == "{%s}path" % SVG_NS:
            self._handle_path_data(str(element.get("d")))
        elif element.tag == "{%s}use" % SVG_NS:
            href = element.get(XLINK_HREF)
            href = href.replace("#", "")
            els = self._svg.xpath("./svg:defs//svg:g[@id='%s']" % href,
                    namespaces=NS)
            if len(els) > 0:
                self._parse(els[0])

        for child in element.getchildren():
            if child.tag == "{%s}defs" % SVG_NS: continue
            self._parse(child)

        if element.get("transform") and element.get("transform").find("matrix") >= 0:
            self._pop_transform()

    def _build_matrix(self, transform):
        if transform.find("matrix") >= 0:
            raw = str(transform).replace("matrix(", "").replace(")", "")
            f = map(float, re.split("\s+|,", raw))
            return Matrix2(f[0], f[1], f[2], f[3], f[4], f[5])

    def _calc_combined_matrix(self):
        m = Matrix2()
        for mat in self._stack:
            m.append_matrix(mat)
        return m

    def _handle_path_data(self, d):
        parts = re.split("[\s]+", d)
        for i in range(0, len(parts), 2):
            try:
                p0 = parts[i]
                p1 = parts[i+1]
                p0 = p0.replace("M", "").replace("L", "").replace("Q", "")
                p1 = p1.replace("M", "").replace("L", "").replace("Q", "")

                v = [float(p0), float(p1)]
                w = self._matrix.multiply_point(v)
                self.minx = w[0] if w[0] < self.minx else self.minx
                self.miny = w[1] if w[1] < self.miny else self.miny
                self.maxx = w[0] if w[0] > self.maxx else self.maxx
                self.maxy = w[1] if w[1] > self.maxy else self.maxy
            except:
                continue

    def _pop_transform(self):
        m = self._stack.pop()
        self._matrix = self._calc_combined_matrix()
        return m

    def _push_transform(self, transform):
        self._stack.append(self._build_matrix(transform))
        self._matrix = self._calc_combined_matrix()

def _encode_jpeg(data):
    return "data:image/jpeg;base64," + base64.encodestring(data)[:-1]
                                        
def _encode_png(data):
    return "data:image/png;base64," + base64.encodestring(data)[:-1]

def _swf_matrix_to_matrix(swf_matrix=None, need_scale=False, need_translate=True, need_rotation=False, unit_div=20.0):
    
    if swf_matrix is None:
        values = [1,0,0,0,0,1,0,0,0,0,1,0,0,0,0,1]
    else:
        values = swf_matrix.to_array()
        if need_rotation:
            values[1] /= unit_div
            values[2] /= unit_div
        if need_scale:
            values[0] /= unit_div
            values[3] /= unit_div
        if need_translate:
            values[4] /= unit_div
            values[5] /= unit_div
        
    return values
    
def _swf_matrix_to_svg_matrix(swf_matrix=None, need_scale=False, need_translate=True, need_rotation=False, unit_div=20.0):
    values = _swf_matrix_to_matrix(swf_matrix, need_scale, need_translate, need_rotation, unit_div)
    str_values = ",".join(map(str, values))
    return "matrix(%s)" % str_values

