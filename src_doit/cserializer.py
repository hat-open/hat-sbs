from pathlib import Path

import sys
import sysconfig

from hat.doit.c import CBuild


__all__ = ['task_cserializer',
           'task_cserializer_obj',
           'task_cserializer_dep']


build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

cserializer_path = (src_py_dir / 'hat/sbs/_cserializer').with_suffix(
    '.pyd' if sys.platform == 'win32' else '.so')


def task_cserializer():
    """Build cserializer"""
    return _build.get_task_lib(cserializer_path)


def task_cserializer_obj():
    """Build cserializer .o files"""
    yield from _build.get_task_objs()


def task_cserializer_dep():
    """Build cserializer .d files"""
    yield from _build.get_task_deps()


def _get_cpp_flags():
    include_path = sysconfig.get_path('include')

    if sys.platform == 'linux':
        yield f'-I{include_path}'

    elif sys.platform == 'darwin':
        pass

    elif sys.platform == 'win32':
        yield f'-I{include_path}'

    else:
        raise Exception('unsupported platform')

    yield f"-I{deps_dir / 'hat-util/src_c'}"
    yield f'-I{src_c_dir}'
    yield '-DMODULE_NAME="_cserializer"'


def _get_ld_flags():
    if sys.platform == 'linux':
        pass

    elif sys.platform == 'darwin':
        python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
        stdlib_path = (Path(sysconfig.get_path('stdlib')) /
                       f'config-{python_version}-darwin')
        yield f"-L{stdlib_path}"
        yield f"-lpython{python_version}"

    elif sys.platform == 'win32':
        data_path = sysconfig.get_path('data')
        python_version = f'{sys.version_info.major}{sys.version_info.minor}'
        yield f"-L{data_path}"
        yield f"-lpython{python_version}"

    else:
        raise Exception('unsupported platform')


_cpp_flags = list(_get_cpp_flags())
_cc_flags = ['-fPIC', '-O2']
# _cc_flags = ['-fPIC', '-O0', '-ggdb']
_ld_flags = list(_get_ld_flags())

_build = CBuild(
    src_paths=[src_c_dir / 'hat/sbs.c',
               *(src_c_dir / 'py/_cserializer').rglob('*.c')],
    build_dir=build_dir / 'cserializer',
    cpp_flags=_cpp_flags,
    cc_flags=_cc_flags,
    ld_flags=_ld_flags,
    task_dep=['deps'])
