import os

from asreval.compute_map import run_script
from asreval.compute_map import get_arg_parser


def test_run_script_uncompressed():
    dir_name = os.path.dirname(__file__)
    stm_fn = os.path.join(dir_name, '3test.stm')
    cnet_lst = os.path.join(dir_name, '3cnet.list')
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)


def test_run_script_compressed():
    dir_name = os.path.dirname(__file__)
    stm_fn = os.path.join(dir_name, '3test.stm')
    cnet_lst = os.path.join(dir_name, 'gzcnet.list')
    use_chn = 'directory'
    cmd_args = ['--stm',
                stm_fn,
                '--cnet-list',
                cnet_lst,
                '--use-channel',
                use_chn]

    args = get_arg_parser().parse_args(cmd_args)
    run_script(args)
