from hat.sbs.common import *  # NOQA

import abc

from hat import util

from hat.sbs.common import Ref, Type, Data


class Serializer(abc.ABC):

    @staticmethod
    @abc.abstractmethod
    def encode(refs: dict[Ref, Type],
               t: Type,
               value: Data
               ) -> util.Bytes:
        """Encode value"""

    @staticmethod
    @abc.abstractmethod
    def decode(refs: dict[Ref, Type],
               t: Type,
               data: util.Bytes
               ) -> Data:
        """Decode data"""
