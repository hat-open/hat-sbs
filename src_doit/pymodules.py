from pathlib import Path

from hat.doit import common
from hat.doit.c import (get_py_ext_suffix,
                        get_py_c_flags,
                        get_py_ld_flags,
                        get_py_ld_libs,
                        CBuild)


__all__ = ['task_pymodules',
           'task_pymodules_serializer',
           'task_pymodules_serializer_obj',
           'task_pymodules_serializer_dep',
           'task_pymodules_serializer_cleanup']


py_limited_api = next(iter(common.PyVersion))
py_ext_suffix = get_py_ext_suffix(py_limited_api=py_limited_api)

build_dir = Path('build')
peru_dir = Path('peru')
src_c_dir = Path('src_c')
src_py_dir = Path('src_py')

pymodules_build_dir = build_dir / 'pymodules'

serializer_path = (src_py_dir /
                   'hat/sbs/serializer/_cserializer').with_suffix(py_ext_suffix)  # NOQA
serializer_src_paths = [src_c_dir / 'hat/sbs.c',
                        src_c_dir / 'py/serializer/_cserializer.c']
serializer_build_dir = (pymodules_build_dir / 'serializer' /
                        f'{common.target_platform.name.lower()}')
serializer_c_flags = [*get_py_c_flags(py_limited_api=py_limited_api),
                      '-fPIC',
                      '-O2',
                      f"-I{peru_dir / 'hat-util/src_c'}",
                      f"-I{src_c_dir}"]
serializer_ld_flags = [*get_py_ld_flags(py_limited_api=py_limited_api)]
serializer_ld_libs = [*get_py_ld_libs(py_limited_api=py_limited_api)]

serializer_build = CBuild(src_paths=serializer_src_paths,
                          build_dir=serializer_build_dir,
                          c_flags=serializer_c_flags,
                          ld_flags=serializer_ld_flags,
                          ld_libs=serializer_ld_libs,
                          task_dep=['pymodules_serializer_cleanup',
                                    'peru'])


def task_pymodules():
    """Build pymodules"""
    return {'actions': None,
            'task_dep': ['pymodules_serializer']}


def task_pymodules_serializer():
    """Build pymodules serializer"""
    yield from serializer_build.get_task_lib(serializer_path)


def task_pymodules_serializer_obj():
    """Build pymodules serializer .o files"""
    yield from serializer_build.get_task_objs()


def task_pymodules_serializer_dep():
    """Build pymodules serializer .d files"""
    yield from serializer_build.get_task_deps()


def task_pymodules_serializer_cleanup():
    """Cleanup pymodules serializer"""

    def cleanup():
        for path in serializer_path.parent.glob('_cserializer.*'):
            if path == serializer_path:
                continue
            common.rm_rf(path)

    return {'actions': [cleanup]}
