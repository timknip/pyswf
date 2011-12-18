
class Enum(object):
    @classmethod
    def tostring(cls, type):
        return cls._mapping.get(type, 'unknown')

class BitmapFormat(Enum):
    BIT_8 = 3
    BIT_15 = 4
    BIT_24 = 5
    
    _mapping = {
        BIT_8: 'BIT_8',
        BIT_15: 'BIT_15',
        BIT_24: 'BIT_24',
    }

class BitmapType(Enum):
    JPEG = 1  
    GIF89A = 2
    PNG = 3
    
    _mapping = {
        JPEG: 'JPEG',
        GIF89A: 'GIF89A',
        PNG: 'PNG',
    }
    
    FileExtensions = {
        JPEG: '.jpeg',
        GIF89A: '.gif',
        PNG: '.png'
    }

class GradientSpreadMode(Enum):
    PAD = 0 
    REFLECT = 1
    REPEAT = 2
    
    _mapping = {
        PAD: 'pad',
        REFLECT: 'reflect',
        REPEAT: 'repeat',
    }

class GradientType(Enum):
    LINEAR = 1
    RADIAL = 2
    
    _mapping = {
        LINEAR: 'LINEAR',
        RADIAL: 'RADIAL',
    }
                
class LineScaleMode(Enum):
    NONE = 0
    HORIZONTAL = 1 
    NORMAL = 2
    VERTICAL = 3
    
    _mapping = {
        NONE: 'none',
        HORIZONTAL: 'horizontal',
        NORMAL: 'normal',
        VERTICAL: 'vertical',
    }
                        
class SpreadMethod(Enum):
    PAD = 0 
    REFLECT = 1
    REPEAT = 2
    
    _mapping = {
        PAD: 'pad',
        REFLECT: 'reflect',
        REPEAT: 'repeat',
    }
                
class InterpolationMethod(Enum):
    RGB = 0
    LINEAR_RGB = 1
    
    _mapping = {
        RGB: 'RGB',
        LINEAR_RGB: 'LINEAR_RGB',
    }
                        
class LineJointStyle(Enum):
    ROUND = 0
    BEVEL = 1
    MITER = 2
    
    _mapping = {
        ROUND: 'ROUND',
        BEVEL: 'BEVEL',
        MITER: 'MITER',
    }
        
class LineCapsStyle(Enum):
    ROUND = 0
    NO = 1
    SQUARE = 2
    
    _mapping = {
        ROUND: 'ROUND',
        NO: 'NO',
        SQUARE: 'SQUARE',
    }
        
class TextAlign(Enum):
    LEFT = 0
    RIGHT = 1
    CENTER = 2
    JUSTIFY = 3
    
    _mapping = {
        LEFT: 'left',
        RIGHT: 'right',
        CENTER: 'center',
        JUSTIFY: 'justify',
    }
        
class BlendMode(Enum):
    Normal = 0
    Normal_1 = 1
    Layer = 2
    Multiply = 3
    Screen = 4
    Lighten = 5
    Darken = 6
    Difference = 7
    Add = 8
    Subtract = 9
    Invert = 10
    Alpha = 11
    Erase = 12
    Overlay = 13
    Hardlight = 14
    
    _mapping = {
        Normal: "Normal",
        Normal_1: "Normal",
        Layer: "Layer",
        Multiply: "Multiply",
        Screen: "Screen",
        Lighten: "Lighten",
        Darken: "Darken",
        Difference: "Difference",
        Add: "Add",
        Subtract: "Subtract",
        Invert: "Invert",
        Alpha: "Alpha",
        Erase: "Erase",
        Overlay: "Overlay",
        Hardlight: "Hardlight",
    }

class AudioSampleRate(Enum):
    Hz5k512 = 0
    Hz11k025 = 1
    Hz22k05 = 2
    Hz44k1 = 3
    
    _mapping = {
        Hz5k512: '5.512kHz',
        Hz11k025: '11.025kHz',
        Hz22k05: '22.05kHz',
        Hz44k1: '44.1kHz',
    }
    
    Rates = {
        Hz5k512: 5512,
        Hz11k025: 11025,
        Hz22k05: 22050,
        Hz44k1: 44100,
    }

class AudioChannels(Enum):
    Mono = 0
    Stereo = 1
    
    _mapping = {
        Mono: 'Mono',
        Stereo: 'Stereo',
    }
    
    Channels = {
        Mono: 1,
        Stereo: 2
    }

class AudioSampleSize(Enum):
    b8 = 0
    b16 = 1
    
    _mapping = {
        b8: '8-bit',
        b16: '16-bit',
    }
    
    Bits = {
        b8: 8,
        b16: 16
    }

class AudioCodec(Enum):
    UncompressedNativeEndian = 0
    ADPCM = 1
    MP3 = 2
    UncompressedLittleEndian = 3
    Nellymoser16kHz = 4
    Nellymoser8kHz = 5
    Nellymoser = 6
    Speex = 11
    
    _mapping = {
        UncompressedNativeEndian: 'UncompressedNativeEndian',
        ADPCM: 'ADPCM',
        MP3: 'MP3',
        UncompressedLittleEndian: 'UncompressedLittleEndian',
        Nellymoser16kHz: 'Nellymoser16kHz',
        Nellymoser8kHz: 'Nellymoser8kHz',
        Nellymoser: 'Nellymoser',
        Speex: 'Speex',
    }
    
    MinimumVersions = {
        UncompressedNativeEndian: 1,
        ADPCM: 1,
        MP3: 4,
        UncompressedLittleEndian: 4,
        Nellymoser16kHz: 10,
        Nellymoser8kHz: 10,
        Nellymoser: 6,
        Speex: 10,
    }
    
    FileExtensions = {
        MP3: '.mp3',
        
        # arbitrary container
        UncompressedNativeEndian: '.wav',   
        UncompressedLittleEndian: '.wav',
        ADPCM: '.wav',
        
        # fictitious
        Nellymoser16kHz: '.nel',
        Nellymoser8kHz: '.nel',
        Nellymoser: '.nel',
        Speex: '.spx',
    }

class ProductEdition(Enum):
    DeveloperEdition = 0
    FullCommercialEdition = 1
    NonCommercialEdition = 2
    EducationalEdition = 3
    NotForResaleEdition = 4
    TrialEdition = 5
    NoEdition = 6
    
    _mapping = {
        DeveloperEdition: 'Developer edition',
        FullCommercialEdition: 'Full commercial',
        NonCommercialEdition: 'Non-commercial',
        EducationalEdition: 'Educational',
        NotForResaleEdition: 'Not for resale',
        TrialEdition: 'Trial',
        NoEdition: 'None',
    }

class ProductKind(Enum):
    Unknown = 0
    FlexForJ2EE = 1
    FlexForDotNET = 2
    AdobeFlex = 3
    
    _mapping = {
        Unknown: 'Unknown',
        FlexForJ2EE: 'Flex for J2EE',
        FlexForDotNET: 'Flex for .NET',
        AdobeFlex: 'Adobe Flex',
    }

class VideoCodec(Enum):
    SorensonH263 = 2
    ScreenVideo = 3
    VP6 = 4
    VP6Alpha = 5
    
    _mapping = {
        SorensonH263: 'Sorenson H.263',
        ScreenVideo: 'Screen video',
        VP6: 'VP6',
        VP6Alpha: 'VP6 with alpha',
    }
    
    MinimumVersions = {
        SorensonH263: 6,
        ScreenVideo: 7,
        VP6: 8,
        VP6Alpha: 8,
    }

class MPEGVersion(Enum):
    MPEG2_5 = 0
    RFU = 1
    MPEG2 = 2
    MPEG1 = 3
    
    _mapping = {
        MPEG2_5: 'MPEG2.5',
        RFU: 'Reserved',
        MPEG2: 'MPEG2',
        MPEG1: 'MPEG1',
    }

class MPEGLayer(Enum):
    RFU = 0
    Layer3 = 1
    Layer2 = 2
    Layer1 = 3
    
    _mapping = {
        RFU: 'Reserved',
        Layer3: 'Layer 3',
        Layer2: 'Layer 2',
        Layer1: 'Layer 1',
    }

def MPEGBitrate(version, value):
    """
    Returns bitrate in thousands of bits per second.
    """
    if version == MPEGVersion.MPEG1:
        bitrates = [ 0, 32, 40, 48, 56, 64, 80, 96, 112, 128, 160, 192, 224, 256, 320, None ]
    else:
        bitrates = [ 0, 8, 16, 24,32, 40, 48, 56, 64, 80, 96, 112, 128, 144, 160, None ]
    assert len(bitrates) == 16
    return bitrates[value]

def MPEGSampleRate(version, value):
    """
    Returns sample rate in samples per second.
    """
    if version == MPEGVersion.MPEG1:
        return [ 44100, 22050, 11025 ][value]
    elif version == MPEGVersion.MPEG2:
        return [ 48000, 24000, 12000 ][value]
    elif version == MPEGVersion.MPEG2_5:
        return [ 32000, 16000, 8000 ][value]
