import pytest

from hat import sbs


serializers = [sbs.CSerializer,
               sbs.PySerializer]


def test_example():
    repo = sbs.Repository('''
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


@pytest.mark.parametrize("encode_serializer", serializers)
@pytest.mark.parametrize("decode_serializer", serializers)
@pytest.mark.parametrize("schema", ["""
    module Module

    T1 = None
    T2 = Boolean
    T3 = Integer
    T4 = Float
    T5 = String
    T6 = Bytes

    T7 = Array(Integer)
    T8 = Array(Array(Boolean))
    T9 = Record { x: Integer, y: String }
    T10 = Choice { x: Integer, y: String }

    T11 = Optional(Integer)

    T12(x) = x
    T13 = T12(Integer)
    T14 = T12(String)

    T15(x) = Array(x)
    T16(y) = T15(y)
    T17 = T16(Optional(Integer))

    T18 = Array(Float)
    T19 = Array(String)
"""])
@pytest.mark.parametrize("t, v", [
    ('Module.T1', None),
    ('Module.T2', True),
    ('Module.T2', False),
    ('Module.T3', 0),
    ('Module.T3', 1),
    ('Module.T3', -1),
    ('Module.T3', 128),
    ('Module.T3', -128),
    ('Module.T3', 256),
    ('Module.T3', -256),
    ('Module.T3', 123456789123456),
    ('Module.T3', -123456789123456),
    ('Module.T4', 0),
    ('Module.T4', -1),
    ('Module.T4', 1),
    ('Module.T4', 0.5),
    ('Module.T4', -0.5),
    ('Module.T4', 123.456),
    ('Module.T4', -123.456),
    ('Module.T4', 1e25),
    ('Module.T4', -1e25),
    ('Module.T5', ''),
    ('Module.T5', '0'),
    ('Module.T5', 'abcdefg'),
    ('Module.T5', ' \n\'\"\\'),
    ('Module.T6', b''),
    ('Module.T6', b'0'),
    ('Module.T6', b'abcdefg'),
    ('Module.T6', b' \n\'\"\\'),
    ('Module.T7', []),
    ('Module.T7', [1]),
    ('Module.T7', [1, 2, 3, 4, 5]),
    ('Module.T7', list(range(100))),
    ('Module.T8', []),
    ('Module.T8', [[]]),
    ('Module.T8', [[], [], []]),
    ('Module.T8', [[True]]),
    ('Module.T8', [[], [False]]),
    ('Module.T8', [[True], [False], [True, False]]),
    ('Module.T9', {'x': 1, 'y': '1'}),
    ('Module.T10', ('x', 1)),
    ('Module.T10', ('y', '1')),
    ('Module.T11', ('none', None)),
    ('Module.T11', ('value', 1234)),
    ('Module.T13', 1234),
    ('Module.T14', 'abcd'),
    ('Module.T17', [('none', None), ('value', 1234)]),
    ('Module.T18', [0, 1.5, -1, 0.005, 1000.1]),
    ('Module.T19', ['', '', '']),
])
def test_serialization(encode_serializer, decode_serializer, schema, t, v):
    repo = sbs.Repository(schema)

    encoded_v = repo.encode(t, v, serializer=encode_serializer)
    decoded_v = repo.decode(t, encoded_v, serializer=decode_serializer)

    assert decoded_v == v


@pytest.mark.parametrize("serializer", serializers)
def test_loading_schema_file(tmp_path, serializer):
    path = tmp_path / 'schema.sbs'
    with open(path, 'w', encoding='utf-8') as f:
        f.write("module M T = Integer")

    repo = sbs.Repository(path)
    value = 123
    encoded_value = repo.encode('M.T', value, serializer=serializer)
    decoded_value = repo.decode('M.T', encoded_value, serializer=serializer)
    assert value == decoded_value


@pytest.mark.parametrize("serializer", serializers)
def test_parametrized_types(serializer):
    repo = sbs.Repository("""
        module M

        T1(x) = Integer
    """)

    encoded = repo.encode('Integer', 1, serializer=serializer)

    with pytest.raises(Exception):
        repo.encode('M.T1', 1, serializer=serializer)

    with pytest.raises(Exception):
        repo.decode('M.T1', encoded, serializer=serializer)


@pytest.mark.parametrize("serializer", serializers)
def test_multiple_modules(serializer):
    repo = sbs.Repository("""
        module M1

        T = Integer
    """, """
        module M2

        T = M1.T
    """)
    value = 1
    encoded_value = repo.encode('M2.T', value, serializer=serializer)
    decoded_value = repo.decode('M2.T', encoded_value, serializer=serializer)
    assert value == decoded_value


@pytest.mark.parametrize("serializer", serializers)
@pytest.mark.parametrize("schema", ["""
    module Module

    T1 = Choice { a: Integer }
"""])
@pytest.mark.parametrize("t,v", [
    ('Module.T1', ('b', 1))
])
def test_invalid_serialization(serializer, schema, t, v):
    repo = sbs.Repository(schema)
    with pytest.raises(Exception):
        encoded_v = repo.encode(t, v, serializer=serializer)
        decoded_v = repo.decode(t, encoded_v, serializer=serializer)
        if v == decoded_v:
            raise Exception()


@pytest.mark.parametrize("schema", ["""
    module Module

    T1(t) = t
    T = T1(Integer, String)
""", """
    module Module

    T1(t) = t(Integer)
    T = T1(Integer)
""", """
    module Module

    T = None(String)
""", """
    module Module

    T = Array
"""])
def test_invalid_schema(schema):
    with pytest.raises(Exception):
        sbs.Repository(schema)


@pytest.mark.parametrize("serializer", serializers)
def test_repository_initialization_with_repository(serializer):
    repo1 = sbs.Repository("""
        module M

        T = Integer
    """)
    repo2 = sbs.Repository(repo1)

    encoded1 = repo1.encode('M.T', 1, serializer=serializer)
    encoded2 = repo2.encode('M.T', 1, serializer=serializer)
    assert encoded1 == encoded2


def test_invalid_repository_initialization_argument_type():
    with pytest.raises(Exception):
        sbs.Repository(None)


@pytest.mark.parametrize("value", [
    0, 0xFFFF_FFFF, 0x7FFF_FFFF_FFFF_FFFF, 0xFFFF_FFFF_FFFF_FFFF_FFFF
])
@pytest.mark.parametrize("serializer", serializers)
def test_large_integer(value, serializer):
    repo = sbs.Repository()

    if serializer is sbs.CSerializer and value > 0x7FFF_FFFF_FFFF_FFFF:
        with pytest.raises(OverflowError):
            repo.encode('Integer', value, serializer=serializer)

    else:
        encoded_value = repo.encode('Integer', value,
                                    serializer=serializer)
        decoded_value = repo.decode('Integer', encoded_value,
                                    serializer=serializer)
        assert value == decoded_value
