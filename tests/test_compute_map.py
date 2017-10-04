from __future__ import print_function
from __future__ import division
from __future__ import unicode_literals
from __future__ import absolute_import
from builtins import int
from builtins import round
from builtins import filter
from builtins import map
from builtins import open
from builtins import str

from tempfile import NamedTemporaryFile

import os
import pytest
import contextlib

from asreval.compute_map import run_script
from asreval.compute_map import get_arg_parser


@contextlib.contextmanager
def create_cnet_list(cnet_path):
    with NamedTemporaryFile('w') as f:
        for fn in os.listdir(cnet_path):
            if fn.endswith('.lat') or fn.endswith('.lat.gz'):
                f.write(os.path.join(cnet_path, fn) + '\n')
        yield f.name


@pytest.fixture()
def dir_name():
    return os.path.dirname(__file__)


@pytest.fixture()
def cnet_list_file(dir_name):
    with create_cnet_list(os.path.join(dir_name, '3cnets-A')) as fn:
        yield fn


@pytest.fixture()
def gzcnet_list_file(dir_name):
    with create_cnet_list(os.path.join(dir_name, 'gzcnets-A')) as fn:
        yield fn


@pytest.fixture()
def gzcnet_unicode_list_file(dir_name):
    with create_cnet_list(os.path.join(dir_name, 'gzcnets_utf8-A')) as fn:
        yield fn


@pytest.fixture()
def cnet_unicode_list_file(dir_name):
    with create_cnet_list(os.path.join(dir_name, '3cnets_utf8-A')) as fn:
        yield fn


def test_run_script_uncompressed(dir_name, cnet_list_file):
    stm_fn = os.path.join(dir_name, '3test.stm')
    cnet_lst = cnet_list_file
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)


def test_run_script_compressed(dir_name, gzcnet_list_file):
    stm_fn = os.path.join(dir_name, '3test.stm')
    cnet_lst = gzcnet_list_file
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)


def test_uncompressed_unicode(dir_name, cnet_unicode_list_file):
    stm_fn = os.path.join(dir_name, '3test-utf8.stm')
    cnet_lst = cnet_unicode_list_file
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)


def test_compressed_unicode(dir_name, gzcnet_unicode_list_file):
    stm_fn = os.path.join(dir_name, '3test-utf8.stm')
    cnet_lst = gzcnet_unicode_list_file
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)


def test_word_list_unicode(dir_name, gzcnet_unicode_list_file):
    stm_fn = os.path.join(dir_name, '3test-utf8.stm')
    cnet_lst = gzcnet_unicode_list_file
    word_list_fn = os.path.join(dir_name, 'word_list.xml')
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn,
                '--term-list',
                word_list_fn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)
