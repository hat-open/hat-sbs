from hat.sbs.serializer import common

try:
    from hat.sbs.serializer import _cserializer

except ImportError:
    _cserializer = None


class CSerializer(common.Serializer):
    """Serializer implementation in C"""

    def encode(refs, t, value):
        if not _cserializer:
            raise Exception('implementation not available')

        return _cserializer.encode(refs, t, value)

    def decode(refs, t, data):
        if not _cserializer:
            raise Exception('implementation not available')

        return _cserializer.decode(refs, t, memoryview(data))
