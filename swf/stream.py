import struct, math
from data import *
from actions import *
from filters import SWFFilterFactory

class SWFStream(object):
    """
    SWF File stream
    """
    FLOAT16_EXPONENT_BASE = 15
    
    def __init__(self, file):
        """ Initialize with a file object """
        self.f = file
        self._bit_pending = 0
        
    def bin(self, s):
        """ Return a value as a binary string """
        return str(s) if s<=1 else bin(s>>1) + str(s&1)
        
    def calc_max_bits(self, signed, values):
        """ Calculates the maximim needed bits to represent a value """
        b = 0
        vmax = -10000000
        
        for val in values:
            if signed:
                b = b | val if val >= 0 else b | ~val << 1
                vmax = val if vmax < val else vmax
            else:
                b |= val;
        bits = 0
        if b > 0:
            bits = len(self.bin(b)) - 2
            if signed and vmax > 0 and len(self.bin(vmax)) - 2 >= bits:
                bits += 1
        return bits
    
    def close(self):
        """ Closes the stream """
        if self.f:
            self.f.close()
            
    def readbits(self, bits, bit_buffer=0):
        """ Read the specified number of bits from the stream """
        if bits == 0: return bit_buffer
        
        if self._bits_pending > 0:
            self.f.seek(self.f.tell() - 1)
            byte = ord(self.f.read(1)) & (0xff >> (8 - self._bits_pending))
            consumed = min(self._bits_pending, bits)
            self._bits_pending -= consumed
            partial = byte >> self._bits_pending
        else:
            consumed = min(8, bits);
            self._bits_pending = 8 - consumed
            partial = ord(self.f.read(1)) >> self._bits_pending
            
        bits -= consumed;
        bit_buffer = (bit_buffer << consumed) | partial
        return self.readbits(bits, bit_buffer) if bits > 0 else bit_buffer
     
    def readFB(self, bits):
        """ Read a float using the specified number of bits """
        return float(self.readSB(bits)) / 65536.0
          
    def readSB(self, bits):
        """ Read a signed int using the specified number of bits """
        shift = 32 - bits
        return int32(self.readbits(bits) << shift) >> shift
        
    def readUB(self, bits):
        """ Read a unsigned int using the specified number of bits """
        return self.readbits(bits)
            
    def readSI8(self):
        """ Read a signed byte """
        self.reset_bits_pending();
        return struct.unpack('b', self.f.read(1))[0]
            
    def readUI8(self):
        """ Read a unsigned byte """
        self.reset_bits_pending();
        return struct.unpack('B', self.f.read(1))[0]
        
    def readSI16(self):
        """ Read a signed short """
        self.reset_bits_pending();
        return struct.unpack('h', self.f.read(2))[0]

    def readUI16(self):
        """ Read a unsigned short """
        self.reset_bits_pending();
        return struct.unpack('H', self.f.read(2))[0]    

    def readSI32(self):
        """ Read a signed int """
        self.reset_bits_pending();
        return struct.unpack('<i', self.f.read(4))[0]

    def readUI32(self):
        """ Read a unsigned int """
        self.reset_bits_pending();
        return struct.unpack('<I', self.f.read(4))[0]
    
    def readEncodedU32(self):
        """ Read a encoded unsigned int """
        self.reset_bits_pending();
        result = self.readUI8();
        if result & 0x80 != 0:
            result = (result & 0x7f) | (self.readUI8() << 7)
            if result & 0x4000 != 0:
                result = (result & 0x3fff) | (self.readUI8() << 14)
                if result & 0x200000 != 0:
                    result = (result & 0x1fffff) | (self.readUI8() << 21)
                    if result & 0x10000000 != 0:
                        result = (result & 0xfffffff) | (self.readUI8() << 28)
        return result
  
    def readFLOAT(self):
        """ Read a float """
        self.reset_bits_pending();
        return struct.unpack('f', self.f.read(4))[0]
    
    def readFLOAT16(self):
        """ Read a 2 byte float """
        self.reset_bits_pending()
        word = self.readUI16()
        sign = -1 if ((word & 0x8000) != 0) else 1
        exponent = (word >> 10) & 0x1f
        significand = word & 0x3ff
        if exponent == 0:
            if significand == 0:
                return 0.0
            else:
                return sign * math.pow(2, 1 - SWFStream.FLOAT16_EXPONENT_BASE) * (significand / 1024.0)
        if exponent == 31:
            if significand == 0:
                return float('-inf') if sign < 0 else float('inf')
            else:
                return float('nan')
        # normal number
        return sign * math.pow(2, exponent - SWFStream.FLOAT16_EXPONENT_BASE) * (1 + significand / 1024.0)
        
    def readFIXED(self):
        """ Read a 16.16 fixed value """
        self.reset_bits_pending()
        return self.readSI32() / 65536.0

    def readFIXED8(self):
        """ Read a 8.8 fixed value """
        self.reset_bits_pending()
        return self.readSI16() / 256.0

    def readCXFORM(self):
        """ Read a SWFColorTransform """
        return SWFColorTransform(self)
    
    def readCXFORMWITHALPHA(self):
        """ Read a SWFColorTransformWithAlpha """
        return SWFColorTransformWithAlpha(self)
    
    def readGLYPHENTRY(self, glyphBits, advanceBits):
        """ Read a SWFGlyphEntry """
        return SWFGlyphEntry(self, glyphBits, advanceBits)
        
    def readGRADIENT(self, level=1):
        """ Read a SWFGradient """
        return SWFGradient(self, level)
                
    def readFOCALGRADIENT(self, level=1):
        """ Read a SWFFocalGradient """
        return SWFFocalGradient(self, level)
            
    def readGRADIENTRECORD(self, level=1):
        """ Read a SWFColorTransformWithAlpha """
        return SWFGradientRecord(self, level)
    
    def readKERNINGRECORD(self, wideCodes):
        """ Read a SWFKerningRecord """
        return SWFKerningRecord(self, wideCodes)
        
    def readLANGCODE(self):
        """ Read a language code """
        self.reset_bits_pending()
        return self.readUI8()
        
    def readMATRIX(self):
        """ Read a SWFMatrix """
        return SWFMatrix(self)
        
    def readRECT(self):
        """ Read a SWFMatrix """
        r = SWFRectangle()
        r.parse(self)
        return r
    
    def readSHAPE(self, unit_divisor=20):
        """ Read a SWFShape """
        return SWFShape(self, 1, unit_divisor)
        
    def readSHAPEWITHSTYLE(self, level=1, unit_divisor=20):
        """ Read a SWFShapeWithStyle """
        return SWFShapeWithStyle(self, level, unit_divisor)
    
    def readCURVEDEDGERECORD(self, num_bits):
        """ Read a SWFShapeRecordCurvedEdge """
        return SWFShapeRecordCurvedEdge(self, num_bits)
            
    def readSTRAIGHTEDGERECORD(self, num_bits):
        """ Read a SWFShapeRecordStraightEdge """
        return SWFShapeRecordStraightEdge(self, num_bits)
    
    def readSTYLECHANGERECORD(self, states, fill_bits, line_bits, level = 1):
        """ Read a SWFShapeRecordStyleChange """
        return SWFShapeRecordStyleChange(self, states, fill_bits, line_bits, level)
        
    def readFILLSTYLE(self, level=1):
        """ Read a SWFFillStyle """
        return SWFFillStyle(self, level)
    
    def readTEXTRECORD(self, glyphBits, advanceBits, previousRecord=None, level=1):
        """ Read a SWFTextRecord """
        if self.readUI8() == 0:
            return None
        else:
            self.seek(self.tell() - 1)
            return SWFTextRecord(self, glyphBits, advanceBits, previousRecord, level)
            
    def readLINESTYLE(self, level=1):
        """ Read a SWFLineStyle """
        return SWFLineStyle(self, level)
    
    def readLINESTYLE2(self, level=1):
        """ Read a SWFLineStyle2 """
        return SWFLineStyle2(self, level)
    
    def readMORPHFILLSTYLE(self, level=1):
        """ Read a SWFMorphFillStyle """
        return SWFMorphFillStyle(self, level)
    
    def readMORPHLINESTYLE(self, level=1):
        """ Read a SWFMorphLineStyle """
        return SWFMorphLineStyle(self, level)
        
    def readMORPHGRADIENT(self, level=1):
        """ Read a SWFTextRecord """
        return SWFMorphGradient(self, level)
     
    def readMORPHGRADIENTRECORD(self):
        """ Read a SWFTextRecord """
        return SWFMorphGradientRecord(self)
    
    def readACTIONRECORD(self):
        """ Read a SWFActionRecord """
        action = None
        actionCode = self.readUI8()
        if actionCode != 0:
            actionLength = self.readUI16() if actionCode >= 0x80 else 0
            #print "0x%x"%actionCode, actionLength
            action = SWFActionFactory.create(actionCode, actionLength)
            action.parse(self)
        return action
        
    def readCLIPACTIONS(self, version):
        """ Read a SWFClipActions """
        return SWFClipActions(self, version)
    
    def readCLIPACTIONRECORD(self, version):
        """ Read a SWFClipActionRecord """
        pos = self.tell()
        flags = self.readUI32() if version >= 6 else self.readUI16()
        if flags == 0:
            return None
        else:
            self.seek(pos)
            return SWFClipActionRecord(self, version)
            
    def readCLIPEVENTFLAGS(self, version):
        """ Read a SWFClipEventFlags """
        return SWFClipEventFlags(self, version)
        
    def readRGB(self):
        """ Read a RGB color """
        self.reset_bits_pending();
        r = self.readUI8()
        g = self.readUI8()
        b = self.readUI8()
        return (0xff << 24) | (r << 16) | (g << 8) | b
        
    def readRGBA(self):
        """ Read a RGBA color """
        self.reset_bits_pending();
        r = self.readUI8()
        g = self.readUI8()
        b = self.readUI8()
        a = self.readUI8()
        return (a << 24) | (r << 16) | (g << 8) | b
    
    def readSYMBOL(self):
        """ Read a SWFSymbol """
        return SWFSymbol(self)
        
    def readString(self):
        """ Read a string """
        s = self.f.read(1)
        string = ""
        while ord(s) > 0:
            string += s
            s = self.f.read(1)
        return string
    
    def readFILTER(self):
        """ Read a SWFFilter """
        filterId = self.readUI8()
        filter = SWFFilterFactory.create(filterId)
        filter.parse(self)
        return filter
    
    def readZONEDATA(self):
        """ Read a SWFZoneData """
        return SWFZoneData(self)
        
    def readZONERECORD(self):
        """ Read a SWFZoneRecord """
        return SWFZoneRecord(self)
        
    def readraw_tag(self):
        """ Read a SWFRawTag """
        return SWFRawTag(self)
    
    def readtag_header(self):
        """ Read a tag header """
        pos = self.tell()
        tag_type_and_length = self.readUI16()
        tag_length = tag_type_and_length & 0x003f
        if tag_length == 0x3f:
            # The SWF10 spec sez that this is a signed int.
            # Shouldn't it be an unsigned int?
            tag_length = self.readSI32();
        return SWFRecordHeader(tag_type_and_length >> 6, tag_length, self.tell() - pos)
    
    def skip_bytes(self, length):
        """ Skip over the specified number of bytes """
        self.f.seek(self.tell() + length)
              
    def reset_bits_pending(self):
        """ Reset the bit array """
        self._bits_pending = 0
    
    def read(self, count=0):
        """ Read """
        return self.f.read(count) if count > 0 else self.f.read()
        
    def seek(self, pos, whence=0):
        """ Seek """
        self.f.seek(pos, whence)
        
    def tell(self):
        """ Tell """
        return self.f.tell()
        
def int32(x):
    """ Return a signed or unsigned int """
    if x>0xFFFFFFFF:
        raise OverflowError
    if x>0x7FFFFFFF:
        x=int(0x100000000-x)
        if x<2147483648:
            return -x
        else:
            return -2147483648
    return x