import collections
import struct
import typing

from hat.sbs import common


def encode(refs: typing.Dict[common.Ref, common.Type],
           t: common.Type,
           value: common.Data
           ) -> bytes:
    return bytes(_encode_generic(refs, t, value))


def decode(refs: typing.Dict[common.Ref, common.Type],
           t: common.Type,
           data: memoryview
           ) -> common.Data:
    data, _ = _decode_generic(refs, t, data)
    return data


def _encode_generic(refs, t, value):
    while isinstance(t, common.Ref) and t in refs:
        t = refs[t]

    if isinstance(t, common.NoneType):
        yield from _encode_None(value)

    elif isinstance(t, common.BooleanType):
        yield from _encode_Boolean(value)

    elif isinstance(t, common.IntegerType):
        yield from _encode_Integer(value)

    elif isinstance(t, common.FloatType):
        yield from _encode_Float(value)

    elif isinstance(t, common.StringType):
        yield from _encode_String(value)

    elif isinstance(t, common.BytesType):
        yield from _encode_Bytes(value)

    elif isinstance(t, common.ArrayType):
        yield from _encode_Array(refs, t, value)

    elif isinstance(t, common.RecordType):
        yield from _encode_Record(refs, t, value)

    elif isinstance(t, common.ChoiceType):
        yield from _encode_Choice(refs, t, value)

    else:
        raise ValueError()


def _decode_generic(refs, t, data):
    while isinstance(t, common.Ref) and t in refs:
        t = refs[t]

    if isinstance(t, common.NoneType):
        return _decode_None(data)

    if isinstance(t, common.BooleanType):
        return _decode_Boolean(data)

    if isinstance(t, common.IntegerType):
        return _decode_Integer(data)

    if isinstance(t, common.FloatType):
        return _decode_Float(data)

    if isinstance(t, common.StringType):
        return _decode_String(data)

    if isinstance(t, common.BytesType):
        return _decode_Bytes(data)

    if isinstance(t, common.ArrayType):
        return _decode_Array(refs, t, data)

    if isinstance(t, common.RecordType):
        return _decode_Record(refs, t, data)

    if isinstance(t, common.ChoiceType):
        return _decode_Choice(refs, t, data)

    raise ValueError()


def _encode_None(value):
    yield from b''


def _decode_None(data):
    return None, data


def _encode_Boolean(value):
    yield 1 if value else 0


def _decode_Boolean(data):
    return bool(data[0]), data[1:]


def _encode_Integer(value):
    ret = collections.deque()
    while True:
        temp = value & 0x7F
        if not ret:
            temp |= 0x80
        ret.appendleft(temp)
        value = value >> 7
        if value == 0 and not (temp & 0x40):
            break
        if value == -1 and (temp & 0x40):
            break
    yield from ret


def _decode_Integer(data):
    ret = -1 if data[0] & 0x40 else 0
    while True:
        ret = (ret << 7) | (data[0] & 0x7F)
        if data[0] & 0x80:
            return ret, data[1:]
        data = data[1:]


def _encode_Float(value):
    yield from struct.pack('>d', value)


def _decode_Float(data):
    return struct.unpack('>d', data[:8])[0], data[8:]


def _encode_String(value):
    ret = value.encode('utf-8')
    yield from _encode_Integer(len(ret))
    yield from ret


def _decode_String(data):
    bytes_len, data = _decode_Integer(data)
    return str(data[:bytes_len], encoding='utf-8'), data[bytes_len:]


def _encode_Bytes(value):
    yield from _encode_Integer(len(value))
    yield from value


def _decode_Bytes(data):
    bytes_len, data = _decode_Integer(data)
    return data[:bytes_len], data[bytes_len:]


def _encode_Array(refs, t, value):
    yield from _encode_Integer(len(value))

    for i in value:
        yield from _encode_generic(refs, t.t, i)


def _decode_Array(refs, t, data):
    count, data = _decode_Integer(data)

    ret = collections.deque()
    for _ in range(count):
        i, data = _decode_generic(refs, t.t, data)
        ret.append(i)

    return list(ret), data


def _encode_Record(refs, t, value):
    if not t.entries:
        raise ValueError('empty entries')

    for entry_name, entry_type in t.entries:
        yield from _encode_generic(refs, entry_type, value[entry_name])


def _decode_Record(refs, t, data):
    if not t.entries:
        raise ValueError('empty entries')

    ret = {}
    for entry_name, entry_type in t.entries:
        ret[entry_name], data = _decode_generic(refs, entry_type, data)
    return ret, data


def _encode_Choice(refs, t, value):
    if not t.entries:
        raise ValueError('empty entries')

    for i, (entry_name, entry_type) in enumerate(t.entries):
        if entry_name == value[0]:
            break
    else:
        raise Exception('invalid entry name')

    yield from _encode_Integer(i)
    yield from _encode_generic(refs, entry_type, value[1])


def _decode_Choice(refs, t, data):
    if not t.entries:
        raise ValueError('empty entries')

    i, data = _decode_Integer(data)
    entry_name, entry_type = t.entries[i]
    value, data = _decode_generic(refs, entry_type, data)
    return (entry_name, value), data
