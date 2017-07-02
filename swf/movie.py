"""
SWF
"""
from __future__ import absolute_import
from .tag import SWFTimelineContainer
from .stream import SWFStream
from .export import SVGExporter
from six.moves import cStringIO
from io import BytesIO

class SWFHeaderException(Exception):
    """ Exception raised in case of an invalid SWFHeader """
    def __init__(self, message):
         super(SWFHeaderException, self).__init__(message)

class SWFHeader(object):
    """ SWF header """
    def __init__(self, stream):
        a = stream.readUI8()
        b = stream.readUI8()
        c = stream.readUI8()
        if not a in [0x43, 0x46, 0x5A] or b != 0x57 or c != 0x53:
            # Invalid signature! ('FWS' or 'CWS' or 'ZFS')
            raise SWFHeaderException("not a SWF file! (invalid signature)")

        self._compressed_zlib = (a == 0x43)
        self._compressed_lzma = (a == 0x5A)
        self._version = stream.readUI8()
        self._file_length = stream.readUI32()
        if not (self._compressed_zlib or self._compressed_lzma):
            self._frame_size = stream.readRECT()
            self._frame_rate = stream.readFIXED8()
            self._frame_count = stream.readUI16()

    @property
    def frame_size(self):
        """ Return frame size as a SWFRectangle """
        return self._frame_size

    @property
    def frame_rate(self):
        """ Return frame rate """
        return self._frame_rate

    @property
    def frame_count(self):
        """ Return number of frames """
        return self._frame_count
                
    @property
    def file_length(self):
        """ Return uncompressed file length """
        return self._file_length
                    
    @property
    def version(self):
        """ Return SWF version """
        return self._version
                
    @property
    def compressed(self):
        """ Whether the SWF is compressed """
        return self._compressed_zlib or self._compressed_lzma

    @property
    def compressed_zlib(self):
        """ Whether the SWF is compressed using ZLIB """
        return self._compressed_zlib

    @property
    def compressed_lzma(self):
        """ Whether the SWF is compressed using LZMA """
        return self._compressed_lzma
        
    def __str__(self):
        return "   [SWFHeader]\n" + \
            "       Version: %d\n" % self.version + \
            "       FileLength: %d\n" % self.file_length + \
            "       FrameSize: %s\n" % self.frame_size.__str__() + \
            "       FrameRate: %d\n" % self.frame_rate + \
            "       FrameCount: %d\n" % self.frame_count

class SWF(SWFTimelineContainer):
    """
    SWF class
    
    The SWF (pronounced 'swiff') file format delivers vector graphics, text, 
    video, and sound over the Internet and is supported by Adobe Flash
    Player software. The SWF file format is designed to be an efficient 
    delivery format, not a format for exchanging graphics between graphics 
    editors.
    
    @param file: a file object with read(), seek(), tell() methods.
    """
    def __init__(self, file=None):
        super(SWF, self).__init__()
        self._data = None if file is None else SWFStream(file)
        self._header = None
        if self._data is not None:
            self.parse(self._data)
    
    @property
    def data(self):
        """
        Return the SWFStream object (READ ONLY)
        """
        return self._data
    
    @property
    def header(self):
        """ Return the SWFHeader """
        return self._header
        
    def export(self, exporter=None, force_stroke=False):
        """
        Export this SWF using the specified exporter. 
        When no exporter is passed in the default exporter used 
        is swf.export.SVGExporter.
        
        Exporters should extend the swf.export.BaseExporter class.
        
        @param exporter : the exporter to use
        @param force_stroke : set to true to force strokes on fills,
                              useful for some edge cases.
        """
        exporter = SVGExporter() if exporter is None else exporter
        if self._data is None:
            raise Exception("This SWF was not loaded! (no data)")
        if len(self.tags) == 0:
            raise Exception("This SWF doesn't contain any tags!")
        return exporter.export(self, force_stroke)
            
    def parse_file(self, filename):
        """ Parses the SWF from a filename """
        self.parse(open(filename, 'rb'))
        
    def parse(self, data):
        """ 
        Parses the SWF.
        
        The @data parameter can be a file object or a SWFStream
        """
        self._data = data = data if isinstance(data, SWFStream) else SWFStream(data)
        self._header = SWFHeader(self._data)
        if self._header.compressed:
            temp = BytesIO()
            if self._header.compressed_zlib:
                import zlib
                data = data.f.read()
                zip = zlib.decompressobj()
                temp.write(zip.decompress(data))
            else:
                import pylzma
                data.readUI32() #consume compressed length
                data = data.f.read()
                temp.write(pylzma.decompress(data))
            temp.seek(0)
            data = SWFStream(temp)
            self._header._frame_size = data.readRECT()
            self._header._frame_rate = data.readFIXED8()
            self._header._frame_count = data.readUI16()
        self.parse_tags(data)
        
    def __str__(self):
        s = "[SWF]\n"
        s += self._header.__str__()
        for tag in self.tags:
            s += tag.__str__() + "\n"
        return s
        
