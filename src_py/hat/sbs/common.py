import typing

from hat import util


class Ref(typing.NamedTuple):
    module: typing.Optional[str]
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
    entries: typing.List[typing.Tuple[str, 'Type']]


class ChoiceType(typing.NamedTuple):
    entries: typing.List[typing.Tuple[str, 'Type']]


Type = typing.Union[Ref,
                    NoneType,
                    BooleanType,
                    IntegerType,
                    FloatType,
                    StringType,
                    BytesType,
                    ArrayType,
                    RecordType,
                    ChoiceType]

Data = typing.Union[None, bool, int, float, str, bytes,
                    typing.List['Data'],
                    typing.Dict[str, 'Data'],
                    typing.Tuple[str, 'Data']]

# HACK
util.register_type_alias('Type')
util.register_type_alias('Data')
