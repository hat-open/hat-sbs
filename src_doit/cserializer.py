from pathlib import Path

import sysconfig

from hat.doit import common
from hat.doit.c import (target_ext_suffix,
                        CBuild)


__all__ = ['task_cserializer',
           'task_cserializer_obj',
           'task_cserializer_dep',
           'task_cserializer_cleanup']


build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

cserializer_path = (src_py_dir /
                    'hat/sbs/_cserializer').with_suffix(target_ext_suffix)


def task_cserializer():
    """Build cserializer"""
    yield from _build.get_task_lib(cserializer_path)


def task_cserializer_obj():
    """Build cserializer .o files"""
    yield from _build.get_task_objs()


def task_cserializer_dep():
    """Build cserializer .d files"""
    yield from _build.get_task_deps()


def task_cserializer_cleanup():
    """Cleanup cserializer"""
    return {'actions': [_cleanup]}


def _cleanup():
    for path in cserializer_path.parent.glob('_cserializer.*'):
        if path == cserializer_path:
            continue
        common.rm_rf(path)


def _get_cpp_flags():
    _, major, minor = common.target_py_version.value

    if common.target_platform == common.local_platform:
        if common.target_py_version == common.local_py_version:
            include_path = sysconfig.get_path('include')
            if include_path:
                yield f'-I{include_path}'

        elif common.local_platform == common.Platform.LINUX:
            yield f'-I/usr/include/python{major}.{minor}'

        else:
            raise ValueError('unsupported version')

    elif (common.local_platform, common.target_platform) == (
            common.Platform.LINUX, common.Platform.WINDOWS):
        yield f'-I/usr/x86_64-w64-mingw32/include/python{major}{minor}'

    else:
        raise ValueError('unsupported platform')

    yield f"-I{deps_dir / 'hat-util/src_c'}"
    yield f'-I{src_c_dir}'
    yield '-DMODULE_NAME="_cserializer"'


def _get_cc_flags():
    yield '-fPIC'
    yield '-O2'
    # yield '-O0'
    # yield '-ggdb'


def _get_ld_flags():
    _, major, minor = common.target_py_version.value

    if common.target_platform == common.local_platform:
        if common.local_platform == common.Platform.DARWIN:
            stdlib_path = (Path(sysconfig.get_path('stdlib')) /
                           f'config-{major}.{minor}-darwin')
            yield f"-L{stdlib_path}"

        elif common.local_platform == common.Platform.WINDOWS:
            data_path = sysconfig.get_path('data')
            yield f"-L{data_path}"

    if common.target_platform == common.Platform.WINDOWS:
        yield f"-lpython{major}{minor}"

    elif common.target_platform == common.Platform.DARWIN:
        yield f"-lpython{major}.{minor}"


_build = CBuild(src_paths=[src_c_dir / 'hat/sbs.c',
                           *(src_c_dir / 'py/_cserializer').rglob('*.c')],
                build_dir=(build_dir / 'cserializer' /
                           f'{common.target_platform.name.lower()}_'
                           f'{common.target_py_version.name.lower()}'),
                cpp_flags=list(_get_cpp_flags()),
                cc_flags=list(_get_cc_flags()),
                ld_flags=list(_get_ld_flags()),
                task_dep=['deps',
                          'cserializer_cleanup'])
