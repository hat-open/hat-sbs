`hat.sbs` - Python simple binary serialization library
======================================================

This library provides Python implementation of :ref:`SBS <sbs>` parser and
data serializer.


Python data types
-----------------

Translation between SBS types and Python types is done according to following
translation table:

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

`hat.sbs` provides data type definition as::

    Data: typing.TypeAlias = (None | bool | int | float | str | bytes |
                              typing.List['Data'] |
                              typing.Dict[str, 'Data'] |
                              typing.Tuple[str, 'Data'])


Repository
----------

`hat.sbs.Repository` is used as collection of interconnected SBS schemas.
Instance of `Repository` can be represented as JSON data enabling efficient
storage and reconstruction of SBS repositories.

Once `Repository` instance is initialized, methods `encode` and `decode`
are used for SBS data serialization. `hat.sbs` provides two serializer
implementations:

* `hat.sbs.CSerializer` (default)

  SBS serializer implemented as C extension.

* `hat.sbs.PySerializer`

  Pure Python implementation of SBS serializer.

::

    class Repository:

        def __init__(self,
                     *args: typing.Union['Repository', pathlib.Path, str]): ...

        def encode(self,
                   name: str,
                   value: common.Data, *,
                   serializer: type[Serializer] = DefaultSerializer
                   ) -> util.Bytes: ...

        def decode(self,
                   name: str,
                   data: util.Bytes, *,
                   serializer: type[Serializer] = DefaultSerializer
                   ) -> common.Data: ...

        def to_json(self) -> json.Data: ...

        @staticmethod
        def from_json(data: pathlib.PurePath | common.Data,
                      ) -> 'Repository': ...

Example usage::

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
    encoded_data = repo.encode('Module', 'T', data)
    decoded_data = repo.decode('Module', 'T', encoded_data)
    assert data == decoded_data


API
---

API reference is available as part of generated documentation:

    * `Python hat.sbs module <py_api/hat/sbs.html>`_
