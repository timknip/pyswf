import consts
import tag

def supported_stream(stream):
    return stream[0].soundFormat == consts.AudioCodec.MP3

def supported_tag(tt):
    return tt.soundFormat == consts.AudioCodec.MP3

def write_stream_to_file(stream, output):
    assert len(stream) > 0
    
    header = stream[0]
    print '  Format:', consts.AudioCodec.tostring(header.soundFormat)
    print '  Rate:', consts.AudioSampleRate.tostring(header.soundRate)
    print '  Sample size:', consts.AudioSampleSize.tostring(header.soundSampleSize)
    print '  Channels:', consts.AudioChannels.tostring(header.soundChannels)
    print '  Total samples:', header.samples
    print '  Latency seek:', header.latencySeek
    print '  Blocks:', len(stream) - 1
    
    for block in stream[1:]:
        block.complete_parse_with_header(header)
        
        if header.soundFormat == consts.AudioCodec.MP3:
            output.write(block.mpegFrames)

def write_sound_to_file(st, output):
    assert isinstance(st, tag.TagDefineSound)
    output.write(st.encode_for_file())