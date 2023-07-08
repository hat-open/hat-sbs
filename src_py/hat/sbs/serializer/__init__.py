import typing

from hat.sbs.serializer.common import Serializer
from hat.sbs.serializer.cserializer import CSerializer
from hat.sbs.serializer.pyserializer import PySerializer


__all__ = ['Serializer', 'CSerializer', 'PySerializer', 'DefaultSerializer']


try:
    import hat.sbs.serializer._cserializer  # NOQA
    DefaultSerializer: typing.TypeAlias = CSerializer

except ImportError:
    DefaultSerializer: typing.TypeAlias = PySerializer
