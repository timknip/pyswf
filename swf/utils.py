from consts import BitmapType
import math

class NumberUtils(object):
    @classmethod
    def round_pixels_20(cls, pixels):
        return round(pixels * 100) / 100
    @classmethod
    def round_pixels_400(cls, pixels):
        return round(pixels * 10000) / 10000
 
class ColorUtils(object):
    @classmethod
    def alpha(cls, color):
        return int(color >> 24) / 255.0
    
    @classmethod
    def rgb(cls, color):
        return (color & 0xffffff)
    
    @classmethod
    def to_rgb_string(cls, color):
        c = "%x" % color
        while len(c) < 6: c = "0" + c
        return "#"+c
        
class ImageUtils(object):
    @classmethod
    def get_image_size(cls, data):
        pass
        
    @classmethod
    def get_image_type(cls, data):
        pos = data.tell()
        image_type = 0
        data.seek(0, 2) # moves file pointer to final position
        if data.tell() > 8:
            data.seek(0)
            b0 = ord(data.read(1))
            b1 = ord(data.read(1))
            b2 = ord(data.read(1))
            b3 = ord(data.read(1))
            b4 = ord(data.read(1))
            b5 = ord(data.read(1))
            b6 = ord(data.read(1))
            b7 = ord(data.read(1))
            if b0 == 0xff and (b1 == 0xd8 or 1 == 0xd9):
                image_type = BitmapType.JPEG
            elif b0 == 0x89 and b1 == 0x50 and b2 == 0x4e and b3 == 0x47 and \
                b4 == 0x0d and b5 == 0x0a and b6 == 0x1a and b7 == 0x0a:
                image_type = BitmapType.PNG
            elif b0 == 0x47 and b1 == 0x49 and b2 == 0x46 and b3 == 0x38 and b4 == 0x39 and b5 == 0x61:
                image_type = BitmapType.GIF89A
        data.seek(pos)
        return image_type