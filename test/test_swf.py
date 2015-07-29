from swf.movie import SWF

def test_header():

    f = open('./test/data/test.swf', 'rb')

    swf = SWF(f)

    assert swf.header.frame_count == 1
