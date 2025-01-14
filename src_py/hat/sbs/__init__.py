"""Simple binary serializer

This implementation of SBS encoder/decoder translates between SBS types and
Python types according to following translation table::

    +----------+------------------+
    | SBS type | Python type      |
    +==========+==================+
    | None     | NoneType         |
    +----------+------------------+
    | Boolean  | bool             |
    +----------+------------------+
    | Integer  | int              |
    +----------+------------------+
    | Float    | float            |
    +----------+------------------+
    | String   | str              |
    +----------+------------------+
    | Bytes    | bytes            |
    +----------+------------------+
    | Array    | list[Data]       |
    +----------+------------------+
    | Record   | dict[str, Data]  |
    +----------+------------------+
    | Choice   | tuple[str, Data] |
    +----------+------------------+

Example usage of SBS serializer::

    import hat.sbs

    repo = hat.sbs.Repository('''
        module Module

        Entry(K, V) = Record {
            key: K
            value: V
        }

        T = Array(Optional(Entry(String, Integer)))
    ''')
    data = [
        ('none', None),
        ('value', {
            'key': 'abc',
            'value': 123
        })
    ]
    encoded_data = repo.encode('Module.T', data)
    decoded_data = repo.decode('Module.T', encoded_data)
    assert data == decoded_data

"""

from hat.sbs.common import Ref, Data
from hat.sbs.repository import Repository
from hat.sbs.serializer import (Serializer,
                                CSerializer,
                                PySerializer,
                                DefaultSerializer)


__all__ = ['Ref',
           'Data',
           'Repository',
           'Serializer',
           'CSerializer',
           'PySerializer',
           'DefaultSerializer']
