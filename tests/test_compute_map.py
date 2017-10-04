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

import os
import pytest

from asreval.compute_map import run_script
from asreval.compute_map import get_arg_parser


def create_cnet_list(cnet_path, outfile):
    with open(outfile, 'w', encoding='utf-8') as f:
        for fn in os.listdir(cnet_path):
            if fn.endswith('.lat') or fn.endswith('.lat.gz'):
                f.write(os.path.join(cnet_path, fn) + '\n')
    return outfile


@pytest.fixture()
def cnet_list_file():
    dir_name = os.path.dirname(__file__)
    list_name = create_cnet_list(os.path.join(dir_name, '3cnets-A'),
                                 os.path.join(dir_name, '_tmp_cnets.lst'))
    yield list_name
    try:
        os.remove(list_name)
    except:
        pass


@pytest.fixture()
def gzcnet_list_file():
    dir_name = os.path.dirname(__file__)
    list_name = create_cnet_list(os.path.join(dir_name, 'gzcnets-A'),
                                 os.path.join(dir_name, '_tmp_gzcents.lst'))
    yield list_name
    try:
        os.remove(list_name)
    except:
        pass


@pytest.fixture()
def gzcnet_unicode_list_file():
    dir_name = os.path.dirname(__file__)
    list_name = create_cnet_list(os.path.join(dir_name, 'gzcnets_utf8-A'),
                                 os.path.join(dir_name, '_tmp_gzcnets_u.lst'))
    yield list_name
    try:
        os.remove(list_name)
    except:
        pass


@pytest.fixture()
def cnet_unicode_list_file():
    dir_name = os.path.dirname(__file__)
    list_name = create_cnet_list(os.path.join(dir_name, '3cnets_utf8-A'),
                                 os.path.join(dir_name, '_tmp_cnets_u.lst'))
    yield list_name
    try:
        os.remove(list_name)
    except:
        pass


def test_run_script_uncompressed(cnet_list_file):
    dir_name = os.path.dirname(__file__)
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


def test_run_script_compressed(gzcnet_list_file):
    dir_name = os.path.dirname(__file__)
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


def test_uncompressed_unicode(cnet_unicode_list_file):
    dir_name = os.path.dirname(__file__)
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


def test_compressed_unicode(gzcnet_unicode_list_file):
    dir_name = os.path.dirname(__file__)
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


def test_word_list_unicode(gzcnet_unicode_list_file):
    dir_name = os.path.dirname(__file__)
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
