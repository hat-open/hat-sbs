from pathlib import Path

from hat.doit import common
from hat.doit.c import (get_target_ext_suffix,
                        get_py_cpp_flags,
                        get_py_ld_flags,
                        CBuild)


__all__ = ['task_cserializer',
           'task_cserializer_obj',
           'task_cserializer_dep',
           'task_cserializer_cleanup']


# py_limited_api = common.PyVersion.CP310
# py_limited_api = next(iter(common.PyVersion))
py_limited_api = None


build_dir = Path('build')
deps_dir = Path('deps')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')


target_ext_suffix = get_target_ext_suffix(py_limited_api)
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
    yield from get_py_cpp_flags(py_limited_api)
    yield f"-I{deps_dir / 'hat-util/src_c'}"
    yield f'-I{src_c_dir}'
    yield '-DMODULE_NAME="_cserializer"'


def _get_cc_flags():
    yield '-fPIC'
    yield '-O2'
    # yield '-O0'
    # yield '-ggdb'


def _get_ld_flags():
    yield from get_py_ld_flags(py_limited_api)


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
