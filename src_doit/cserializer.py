from pathlib import Path

import sys
import sysconfig

from hat.doit.c import (local_platform,
                        Platform,
                        CBuild)


__all__ = ['task_cserializer',
           'task_cserializer_obj',
           'task_cserializer_dep']


build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

platforms = [local_platform]
if local_platform == Platform.LINUX:
    platforms.append(Platform.WINDOWS)

python_versions = [(sys.version_info.major, sys.version_info.minor)]
if local_platform == Platform.LINUX:
    for python_version in [(3, 8), (3, 9), (3, 10)]:
        if python_version not in python_versions:
            python_versions.append(python_version)


def task_cserializer():
    """Build cserializer"""
    for build, cserializer_path in zip(_builds, _cserializer_paths):
        yield from build.get_task_lib(cserializer_path)


def task_cserializer_obj():
    """Build cserializer .o files"""
    for build in _builds:
        yield from build.get_task_objs()


def task_cserializer_dep():
    """Build cserializer .d files"""
    for build in _builds:
        yield from build.get_task_deps()


def _get_cserializer_path(platform, major, minor):
    if platform == Platform.LINUX:
        suffix = f'.cpython-{major}{minor}-x86_64-linux-gnu.so'

    elif platform == Platform.DARWIN:
        suffix = f'.cpython-{major}{minor}-darwin.so'

    elif platform == Platform.WINDOWS:
        suffix = f'.cp{major}{minor}-win_amd64.pyd'

    else:
        raise ValueError('unsupported platform')

    return (src_py_dir / 'hat/sbs/_cserializer').with_suffix(suffix)


def _get_cpp_flags(platform, major, minor):
    if platform == local_platform:
        if python_version == (sys.version_info.major, sys.version_info.minor):
            include_path = sysconfig.get_path('include')
            if include_path:
                yield f'-I{include_path}'

        else:
            yield f'-I/usr/include/python{major}.{minor}'

    elif platform == Platform.WINDOWS:
        yield f'-I/usr/x86_64-w64-mingw32/include/python{major}{minor}'

    else:
        raise ValueError('unsupported platform')

    yield f"-I{deps_dir / 'hat-util/src_c'}"
    yield f'-I{src_c_dir}'
    yield '-DMODULE_NAME="_cserializer"'


def _get_cc_flags(platform, major, minor):
    yield '-fPIC'
    yield '-O2'
    # yield '-O0'
    # yield '-ggdb'


def _get_ld_flags(platform, major, minor):
    if platform == local_platform:
        if platform == 'darwin':
            stdlib_path = (Path(sysconfig.get_path('stdlib')) /
                           f'config-{major}.{minor}-darwin')
            yield f"-L{stdlib_path}"

        elif sys.platform == 'win32':
            data_path = sysconfig.get_path('data')
            yield f"-L{data_path}"

    if platform == Platform.WINDOWS:
        yield f"-lpython{major}{minor}"

    else:
        yield f"-lpython{major}.{minor}"


_src_paths = [src_c_dir / 'hat/sbs.c',
              *(src_c_dir / 'py/_cserializer').rglob('*.c')]

_builds = [CBuild(src_paths=_src_paths,
                  build_dir=(build_dir / 'cserializer' /
                             f'{platform.name.lower()}{major}{minor}'),
                  platform=platform,
                  cpp_flags=list(_get_cpp_flags(platform, major, minor)),
                  cc_flags=list(_get_cc_flags(platform, major, minor)),
                  ld_flags=list(_get_ld_flags(platform, major, minor)),
                  task_dep=['deps'])
           for platform in platforms
           for major, minor in python_versions]

_cserializer_paths = [_get_cserializer_path(platform, major, minor)
                      for platform in platforms
                      for major, minor in python_versions]
