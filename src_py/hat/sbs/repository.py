import pathlib
import typing

from hat import json
from hat import util

from hat.sbs import common
from hat.sbs import evaluator
from hat.sbs import parser
from hat.sbs.serializer import Serializer, DefaultSerializer


class Repository:
    """SBS schema repository.

    Supported initialization arguments:
        * string containing sbs schema
        * file path to .sbs file
        * path to direcory recursivly searched for .sbs files
        * other repository

    """

    def __init__(self,
                 *args: typing.Union['Repository', pathlib.Path, str]):
        self._modules = list(_parse_args(args))
        self._refs = evaluator.evaluate_modules(self._modules)

    def encode(self,
               name: str,
               value: common.Data, *,
               serializer: typing.Type[Serializer] = DefaultSerializer
               ) -> util.Bytes:
        """Encode value."""
        ref = _parse_name(name)
        return serializer.encode(self._refs, ref, value)

    def decode(self,
               name: str,
               data: util.Bytes, *,
               serializer: typing.Type[Serializer] = DefaultSerializer
               ) -> common.Data:
        """Decode data."""
        ref = _parse_name(name)
        return serializer.decode(self._refs, ref, data)

    def to_json(self) -> json.Data:
        """Export repository content as json serializable data.

        Entire repository content is exported as json serializable data.
        New repository can be created from the exported content by using
        :meth:`Repository.from_json`.

        """
        return [parser.module_to_json(module) for module in self._modules]

    @staticmethod
    def from_json(data: pathlib.PurePath | json.Data) -> 'Repository':
        """Create new repository from content exported as json serializable
        data.

        Creates a new repository from content of another repository that was
        exported by using :meth:`Repository.to_json`.

        """
        if isinstance(data, pathlib.PurePath):
            data = json.decode_file(data)

        repo = Repository()
        repo._modules = [parser.module_from_json(i) for i in data]
        repo._refs = evaluator.evaluate_modules(repo._modules)
        return repo


def _parse_args(args):
    for arg in args:
        if isinstance(arg, pathlib.PurePath):
            paths = ([arg] if arg.suffix == '.sbs'
                     else arg.rglob('*.sbs'))
            for path in paths:
                yield parser.parse(path.read_text('utf-8'))

        elif isinstance(arg, Repository):
            yield from arg._modules

        elif isinstance(arg, str):
            yield parser.parse(arg)

        else:
            raise ValueError('unsupported arg')


def _parse_name(name):
    segments = name.split('.', 1)
    module = segments[0] if len(segments) > 1 else None
    return common.Ref(module, segments[-1])
