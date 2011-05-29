from utils import ColorUtils

class Filter(object):
    """
    Base Filter class
    """
    def __init__(self, id):
        self._id = id
    
    @property
    def id(self):
        """ Return filter ID """
        return self._id
        
    def parse(self, data):
        '''
        Parses the filter
        '''
        pass
        
class FilterDropShadow(Filter):
    """
    Drop Shadow Filter
    """
    def __init__(self, id):
        super(FilterDropShadow, self).__init__(id)
    
    def parse(self, data):
        self.dropShadowColor = data.readRGBA()
        self.blurX = data.readFIXED()
        self.blurY = data.readFIXED()
        self.angle = data.readFIXED()
        self.distance = data.readFIXED()
        self.strength = data.readFIXED8()
        flags = data.readUI8()
        self.innerShadow = ((flags & 0x80) != 0)
        self.knockout = ((flags & 0x40) != 0)
        self.compositeSource = ((flags & 0x20) != 0)
        self.passes = flags & 0x1f
    
    def __str__(self):
        s = "[DropShadowFilter] " + \
            "DropShadowColor: %s" % ColorUtils.to_rgb_string(self.dropShadowColor) + ", " + \
            "BlurX: %0.2f" % self.blurX + ", " + \
            "BlurY: %0.2f" % self.blurY + ", " + \
            "Angle: %0.2f" % self.angle + ", " + \
            "Distance: %0.2f" % self.distance + ", " + \
            "Strength: %0.2f" % self.strength + ", " + \
            "Passes: %d" % self.passes + ", " + \
            "InnerShadow: %d" % self.innerShadow + ", " + \
            "Knockout: %d" % self.knockout + ", " + \
            "CompositeSource: %d" % self.compositeSource
        return s
        
class FilterBlur(Filter):
    """
    Blur Filter
    """
    def __init__(self, id):
        super(FilterBlur, self).__init__(id)

    def parse(self, data):
        self.blurX = data.readFIXED()
        self.blurY = data.readFIXED()
        self.passes = data.readUI8() >> 3
    
    def __str__(self):
        s = "[FilterBlur] " + \
            "BlurX: %0.2f" % self.blurX + ", " + \
            "BlurY: %0.2f" % self.blurY + ", " + \
            "Passes: %d" % self.passes
        return s
        
class FilterGlow(Filter):
    """
    Glow Filter
    """
    def __init__(self, id):
        super(FilterGlow, self).__init__(id)

    def parse(self, data):
        self.glowColor = data.readRGBA()
        self.blurX = data.readFIXED()
        self.blurY = data.readFIXED()
        self.strength = data.readFIXED8()
        flags = data.readUI8()
        self.innerGlow = ((flags & 0x80) != 0)
        self.knockout = ((flags & 0x40) != 0)
        self.compositeSource = ((flags & 0x20) != 0)
        self.passes = flags & 0x1f
        
    def __str__(self):
        s = "[FilterGlow] " + \
            "glowColor: %s" % ColorUtils.to_rgb_string(self.glowColor) + ", " + \
            "BlurX: %0.2f" % self.blurX + ", " + \
            "BlurY: %0.2f" % self.blurY + ", " + \
            "Strength: %0.2f" % self.strength + ", " + \
            "Passes: %d" % self.passes + ", " + \
            "InnerGlow: %d" % self.innerGlow + ", " + \
            "Knockout: %d" % self.knockout
        return s
            
class FilterBevel(Filter):
    """
    Bevel Filter
    """
    def __init__(self, id):
        super(FilterBevel, self).__init__(id)

    def parse(self, data):
        self.shadowColor = data.readRGBA()
        self.highlightColor = data.readRGBA()
        self.blurX = data.readFIXED()
        self.blurY = data.readFIXED()
        self.angle = data.readFIXED()
        self.distance = data.readFIXED()
        self.strength = data.readFIXED8()
        flags = data.readUI8()
        self.innerShadow = ((flags & 0x80) != 0)
        self.knockout = ((flags & 0x40) != 0)
        self.compositeSource = ((flags & 0x20) != 0)
        self.onTop = ((flags & 0x10) != 0)
        self.passes = flags & 0x0f
        
    def __str__(self):
        s = "[FilterBevel] " + \
            "ShadowColor: %s" % ColorUtils.to_rgb_string(self.shadowColor) + ", " + \
            "HighlightColor: %s" % ColorUtils.to_rgb_string(self.highlightColor) + ", " + \
            "BlurX: %0.2f" % self.blurX + ", " + \
            "BlurY: %0.2f" % self.blurY + ", " + \
            "Angle: %0.2f" % self.angle + ", " + \
            "Passes: %d" % self.passes + ", " + \
            "Knockout: %d" % self.knockout
        return s
          
class FilterGradientGlow(Filter):
    """
    Gradient Glow Filter
    """
    def __init__(self, id):
        self.gradientColors = []
        self.gradientRatios = []
        super(FilterGradientGlow, self).__init__(id)

    def parse(self, data):
        self.gradientColors = []
        self.gradientRatios = []
        self.numColors = data.readUI8()
        for i in range(0, self.numColors):
            self.gradientColors.append(data.readRGBA())
        for i in range(0, self.numColors):
            self.gradientRatios.append(data.readUI8())
        self.blurX = data.readFIXED()
        self.blurY = data.readFIXED()
        self.strength = data.readFIXED8()
        flags = data.readUI8()
        self.innerShadow = ((flags & 0x80) != 0)
        self.knockout = ((flags & 0x40) != 0)
        self.compositeSource = ((flags & 0x20) != 0)
        self.onTop = ((flags & 0x20) != 0)
        self.passes = flags & 0x0f

class FilterConvolution(Filter):
    """
    Convolution Filter
    """
    def __init__(self, id):
        self.matrix = []
        super(FilterConvolution, self).__init__(id)

    def parse(self, data):
        self.matrix = []
        self.matrixX = data.readUI8()
        self.matrixY = data.readUI8()
        self.divisor = data.readFLOAT()
        self.bias = data.readFLOAT()
        length = matrixX * matrixY
        for i in range(0, length):
            self.matrix.append(data.readFLOAT())
        self.defaultColor = data.readRGBA()
        flags = data.readUI8()
        self.clamp = ((flags & 0x02) != 0)
        self.preserveAlpha = ((flags & 0x01) != 0)

class FilterColorMatrix(Filter):
    """
    ColorMatrix Filter
    """
    def __init__(self, id):
        self.colorMatrix = []
        super(FilterColorMatrix, self).__init__(id)

    def parse(self, data):
        self.colorMatrix = []
        for i in range(0, 20):
            self.colorMatrix.append(data.readFLOAT())
        for i in range(4, 20, 5):
            self.colorMatrix[i] /= 256.0
            
    def tostring(self):
        s = "[FilterColorMatrix] " + \
            " ".join(map(str, self.colorMatrix))
        return s
                
class FilterGradientBevel(FilterGradientGlow):
    """
    Gradient Bevel Filter
    """
    def __init__(self, id):
        super(FilterGradientBevel, self).__init__(id)
                                  
class SWFFilterFactory(object):
    """
    Filter factory
    """
    @classmethod
    def create(cls, type):
        """ Return the specified Filter """
        if type == 0: return FilterDropShadow(id)
        elif type == 1: return FilterBlur(id)
        elif type == 2: return FilterGlow(id)
        elif type == 3: return FilterBevel(id)
        elif type == 4: return FilterGradientGlow(id)
        elif type == 5: return FilterConvolution(id)
        elif type == 6: return FilterColorMatrix(id)
        elif type == 7: return FilterGradientBevel(id)
        else:
            raise Exception("Unknown filter type: %d" % type)

