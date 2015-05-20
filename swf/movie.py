"""
SWF
"""
from tag import SWFTimelineContainer
from stream import SWFStream
from export import SVGExporter
import StringIO

class SWFHeaderException(Exception):
    """Exception raised in case of an invalid SWFHeader."""


class SWFCompressionException(Exception):
    """Exception raised when a compressed file cannot be decompressed."""

class SWFHeader(object):
    """ SWF header """
    def __init__(self, stream):
        a = stream.readUI8()
        b = stream.readUI8()
        c = stream.readUI8()
        if a not in [ord('F'), ord('C'), ord('Z')] or \
           b != ord('W') or \
           c != ord('S'):
            # Invalid signature! ('FWS', 'CWS', 'ZWS')
            raise SWFHeaderException("not a SWF file! (invalid signature)")

        self._zlib_compressed = (a == ord('C'))
        self._lzma_compressed = (a == ord('Z'))

        self._version = stream.readUI8()
        self._file_length = stream.readUI32()
        self._frame_size = self._frame_rate = self._frame_count = None

    def set_frame_prop(self, stream):
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
    def zlib_compressed(self):
        """ Whether the SWF is compressed using ZLIB """
        return self._zlib_compressed

    @property
    def lzma_compressed(self):
        """ Whether the SWF is compressed using LZMA"""
        return self._lzma_compressed

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
        self._data = data if isinstance(data, SWFStream) else SWFStream(data)
        self._header = SWFHeader(self._data)
        if self._header.zlib_compressed or self._header.lzma_compressed:
            self._data = self._decompress()
        self._header.set_frame_prop(self._data)
        self.parse_tags(self._data)

    def _decompress(self):
        decomp_data = None
        data = self._data.f.read()
        if self._header.zlib_compressed:
            import zlib
            zip_decompressor = zlib.decompressobj()
            decomp_data = zip_decompressor.decompress(data)
        elif self._header.lzma_compressed:
            from backports import lzma
            # We need to do some massaging to ensure that the SWF data conforms
            # to the lzma_alone format used in liblzma. In particular, liblzma
            # expects:
            # - lzma properties (5 bytes)
            # - uncompressed size (64-bit little endian integer); the special
            #   value 0xFFFF_FFFF_FFFF_FFFF indicates that Uncompressed Size is
            #   unknown
            # - compressed data, without trailing garbage
            # Details taken from http://svn.python.org/projects/external/xz-5.0.3/doc/lzma-file-format.txt
            lzma_prop_offset = 4
            lzma_prop_len = 5
            comp_data_offset = lzma_prop_offset + lzma_prop_len
            max_trailing_garbage = 256
            for i in range(max_trailing_garbage):
                try:
                    decomp_data = lzma.decompress(
                        data[lzma_prop_offset:lzma_prop_offset + lzma_prop_len] +
                        "\xff" * 8 +
                        data[comp_data_offset:len(data) - i])
                    break
                except lzma.LZMAError:
                    pass

        # Was the decompressing successful?
        if not decomp_data:
            raise SWFCompressionException

        return SWFStream(StringIO.StringIO(decomp_data))

    def __str__(self):
        s = "[SWF]\n"
        s += self._header.__str__()
        for tag in self.tags:
            s += tag.__str__() + "\n"
        return s

