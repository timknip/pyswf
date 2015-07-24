import consts
import tag
import wave
import stream

supportedCodecs = (
    consts.AudioCodec.MP3,
    consts.AudioCodec.UncompressedNativeEndian,
    consts.AudioCodec.UncompressedLittleEndian,
)

uncompressed = (
    consts.AudioCodec.UncompressedNativeEndian,
    consts.AudioCodec.UncompressedLittleEndian,
)

REASON_OK = None
REASON_EMPTY = 'stream is empty'

def get_header(stream_or_tag):
    if isinstance(stream_or_tag, list):
        assert len(stream_or_tag) > 0, 'empty stream'
        return stream_or_tag[0]
    else:
        assert isinstance(stream_or_tag, tag.TagDefineSound), 'sound is not a stream or DefineSound tag'
        return stream_or_tag

def reason_unsupported(stream_or_tag):
    header = get_header(stream_or_tag)
    is_stream = isinstance(stream_or_tag, list)
    
    if header.soundFormat not in supportedCodecs:
        return 'codec %s (%d) not supported' % (consts.AudioCodec.tostring(header.soundFormat),
                                                header.soundFormat)
    
    if is_stream and len(stream_or_tag) == 1:
        return REASON_EMPTY
    
    return REASON_OK
        
def supported(stream_or_tag):
    return reason_unsupported(stream_or_tag) is None
    
def junk(stream_or_tag):
    return reason_unsupported(stream_or_tag) == REASON_EMPTY

def get_wave_for_header(header, output):
    w = wave.open(output, 'w')
    w.setframerate(consts.AudioSampleRate.Rates[header.soundRate])
    w.setnchannels(consts.AudioChannels.Channels[header.soundChannels])
    w.setsampwidth(consts.AudioSampleSize.Bits[header.soundSampleSize] / 8)
    return w
    
def write_stream_to_file(stream, output):
    header = get_header(stream)
    
    w = None
    if header.soundFormat in uncompressed:
        w = get_wave_for_header(header, output)
    
    for block in stream[1:]:
        block.complete_parse_with_header(header)
        
        if header.soundFormat == consts.AudioCodec.MP3:
            output.write(block.mpegFrames)
        else:
            w.writeframes(block.data.read())
    
    if w:
        w.close()

def write_sound_to_file(st, output):
    assert isinstance(st, tag.TagDefineSound)
    if st.soundFormat == consts.AudioCodec.MP3:
        swfs = stream.SWFStream(st.soundData)
        seekSamples = swfs.readSI16()
        output.write(swfs.read())
    elif st.soundFormat in uncompressed:
        w = get_wave_for_header(st, output)
        w.writeframes(st.soundData.read())
        w.close()