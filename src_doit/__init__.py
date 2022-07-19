from pathlib import Path
import sys

from hat.doit import common
from hat.doit.c import get_task_clang_format
from hat.doit.docs import (build_sphinx,
                           build_pdoc)
from hat.doit.py import (build_wheel,
                         run_pytest,
                         run_flake8,
                         get_py_versions)

from .cserializer import py_limited_api
from .cserializer import *  # NOQA
from . import cserializer


__all__ = ['task_clean_all',
           'task_build',
           'task_check',
           'task_test',
           'task_docs',
           'task_deps',
           'task_format',
           *cserializer.__all__]


build_dir = Path('build')
src_py_dir = Path('src_py')
pytest_dir = Path('test_pytest')
docs_dir = Path('docs')

build_py_dir = build_dir / 'py'
build_docs_dir = build_dir / 'docs'


def task_clean_all():
    """Clean all"""
    return {'actions': [(common.rm_rf, [
        build_dir,
        *(src_py_dir / 'hat/sbs').glob('_cserializer.*')])]}


def task_build():
    """Build"""

    def build():
        build_wheel(
            src_dir=src_py_dir,
            dst_dir=build_py_dir,
            name='hat-sbs',
            description='Hat simple binary serializer',
            url='https://github.com/hat-open/hat-sbs',
            license=common.License.APACHE2,
            py_versions=get_py_versions(py_limited_api),
            py_limited_api=py_limited_api,
            platform=common.target_platform,
            has_ext_modules=True)

    return {'actions': [build],
            'task_dep': ['cserializer']}


def task_check():
    """Check with flake8"""
    return {'actions': [(run_flake8, [src_py_dir]),
                        (run_flake8, [pytest_dir])]}


def task_test():
    """Test"""
    return {'actions': [lambda args: run_pytest(pytest_dir, *(args or []))],
            'pos_arg': 'args',
            'task_dep': ['cserializer']}


def task_docs():
    """Docs"""

    def build():
        build_sphinx(src_dir=docs_dir,
                     dst_dir=build_docs_dir,
                     project='hat-sbs')
        build_pdoc(module='hat.sbs',
                   dst_dir=build_docs_dir / 'py_api')

    return {'actions': [build],
            'task_dep': ['cserializer']}


def task_deps():
    """Dependencies"""
    return {'actions': [f'{sys.executable} -m peru sync']}


def task_format():
    """Format"""
    yield from get_task_clang_format([*Path('src_c').rglob('*.c'),
                                      *Path('src_c').rglob('*.h')])
