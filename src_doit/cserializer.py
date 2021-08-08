from pathlib import Path

import sysconfig
import sys

from hat.doit import common


__all__ = ['task_cserializer',
           'task_cserializer_obj',
           'task_cserializer_dep']


build_dir = Path('build')
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
        return [f'-I{include_path}']

    elif sys.platform == 'darwin':
        return []

    elif sys.platform == 'win32':
        return [f'-I{include_path}']

    raise Exception('unsupported platform')


def _get_ld_flags():
    if sys.platform == 'linux':
        return []

    elif sys.platform == 'darwin':
        python_version = f'{sys.version_info.major}.{sys.version_info.minor}'
        stdlib_path = (Path(sysconfig.get_path('stdlib')) /
                       f'config-{python_version}-darwin')
        return [f"-L{stdlib_path}",
                f"-lpython{python_version}"]

    elif sys.platform == 'win32':
        data_path = sysconfig.get_path('data')
        python_version = f'{sys.version_info.major}{sys.version_info.minor}'
        return [f"-L{data_path}",
                f"-lpython{python_version}"]

    raise Exception('unsupported platform')


_cpp_flags = _get_cpp_flags()
_cc_flags = ['-fPIC', '-O2']
# _cc_flags = ['-fPIC', '-O0', '-ggdb']
_ld_flags = _get_ld_flags()

_build = common.CBuild(
    src_paths=[src_c_dir / 'hat/sbs.c',
               *(src_c_dir / 'py/_cserializer').rglob('*.c')],
    src_dir=src_c_dir,
    build_dir=build_dir / 'cserializer',
    cpp_flags=[*_cpp_flags,
               '-DMODULE_NAME="_cserializer"',
               f"-I{src_c_dir}"],
    cc_flags=_cc_flags,
    ld_flags=_ld_flags)
