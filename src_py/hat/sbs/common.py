import typing

from hat import util


class Ref(typing.NamedTuple):
    module: str | None
    name: str


class NoneType(typing.NamedTuple):
    pass


class BooleanType(typing.NamedTuple):
    pass


class IntegerType(typing.NamedTuple):
    pass


class FloatType(typing.NamedTuple):
    pass


class StringType(typing.NamedTuple):
    pass


class BytesType(typing.NamedTuple):
    pass


class ArrayType(typing.NamedTuple):
    t: 'Type'


class RecordType(typing.NamedTuple):
    entries: list[typing.Tuple[str, 'Type']]


class ChoiceType(typing.NamedTuple):
    entries: list[typing.Tuple[str, 'Type']]


Type: typing.TypeAlias = (Ref |
                          NoneType |
                          BooleanType |
                          IntegerType |
                          FloatType |
                          StringType |
                          BytesType |
                          ArrayType |
                          RecordType |
                          ChoiceType)

Data: typing.TypeAlias = (None | bool | int | float | str | util.Bytes |
                          typing.List['Data'] |
                          typing.Dict[str, 'Data'] |
                          typing.Tuple[str, 'Data'])
