
class BitmapFormat(object):
    BIT_8 = 3
    BIT_15 = 4
    BIT_24 = 5

    @classmethod
    def tostring(cls, type):
        if type == BitmapFormat.BIT_8: return "BIT_8"
        elif type == BitmapFormat.BIT_15: return "BIT_15"
        elif type == BitmapFormat.BIT_24: return "BIT_24"
        else: return "unknown"

class BitmapType(object):
    JPEG = 1  
    GIF89A = 2
    PNG = 3
    
    @classmethod
    def tostring(cls, type):
        if type == BitmapType.JPEG: return "JPEG"
        elif type == BitmapType.GIF89A: return "GIF89A"
        elif type == BitmapType.PNG: return "PNG"
        else: return "unknown"

class GradientSpreadMode(object):
    PAD = 0 
    REFLECT = 1
    REPEAT = 2

    @classmethod
    def tostring(cls, type):
        if type == GradientSpreadMode.PAD: return "pad"
        elif type == GradientSpreadMode.REFLECT: return "reflect"
        elif type == GradientSpreadMode.REPEAT: return "repeat"
        else: return "unknown"

class GradientType(object):
    LINEAR = 1
    RADIAL = 2

    @classmethod
    def tostring(cls, type):
        if type == GradientType.LINEAR: return "LINEAR"
        elif type == GradientType.RADIAL: return "RADIAL"
        else: return "unknown"
                
class LineScaleMode(object):
    NONE = 0
    HORIZONTAL = 1 
    NORMAL = 2
    VERTICAL = 3
    @classmethod
    def tostring(cls, type):
        if type == LineScaleMode.HORIZONTAL: return "horizontal"
        elif type == LineScaleMode.NORMAL: return "normal"
        elif type == LineScaleMode.VERTICAL: return "vertical"
        elif type == LineScaleMode.NONE: return "none"
        else: return "unknown"
                        
class SpreadMethod(object):
    PAD = 0 
    REFLECT = 1
    REPEAT = 2

    @classmethod
    def tostring(cls, type):
        if type == SpreadMethod.PAD: return "pad"
        elif type == SpreadMethod.REFLECT: return "reflect"
        elif type == SpreadMethod.REPEAT: return "repeat"
        else: return "unknown"
                
class InterpolationMethod(object):
    RGB = 0
    LINEAR_RGB = 1
    @classmethod
    def tostring(cls, type):
        if type == InterpolationMethod.LINEAR_RGB: return "LINEAR_RGB"
        elif type == InterpolationMethod.RGB: return "RGB"
        else: return "unknown"
                        
class LineJointStyle(object):
    ROUND = 0
    BEVEL = 1
    MITER = 2
    
    @classmethod
    def tostring(cls, type):
        if type == LineJointStyle.ROUND: return "ROUND"
        elif type == LineJointStyle.BEVEL: return "BEVEL"
        elif type == LineJointStyle.MITER: return "MITER"
        else: return "unknown"
        
class LineCapsStyle(object):
    ROUND = 0
    NO = 1
    SQUARE = 2
    
    @classmethod    
    def tostring(cls, type):
        if type == LineCapsStyle.ROUND: return "ROUND"
        elif type == LineCapsStyle.NO: return "NO"
        elif type == LineCapsStyle.SQUARE: return "SQUARE"
        else: return "unknown"
        
    