__author__ = 'dkudrow'


from client import Client
from util import Util
from argparse import ArgumentParser
import logging


def main():
    """

    :return:
    """
    logging.basicConfig()
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default='2181')
    args = parser.parse_args()
    Client(args.port).run()


def util():
    """

    :return:
    """
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default='2181')
    subparsers = parser.add_subparsers(dest='subcommand')

    start_service = subparsers.add_parser('start_service')
    start_service.add_argument('service', default='')

    start_service = subparsers.add_parser('start_host')
    start_service.add_argument('host', default='')

    start_service = subparsers.add_parser('start_service_on_host')
    start_service.add_argument('service', default='')
    start_service.add_argument('host', default='')

    start_service = subparsers.add_parser('stop_service')
    start_service.add_argument('service_id', default='')

    start_service = subparsers.add_parser('stop_host')
    start_service.add_argument('host', default='')

    start_service = subparsers.add_parser('set_arg')
    start_service.add_argument('arg', default='')
    start_service.add_argument('value', default='')

    start_service = subparsers.add_parser('load_spec')
    start_service.add_argument('filename', default='')

    dump = subparsers.add_parser('dump')

    kwargs = vars(parser.parse_args())
    subcommand = kwargs.pop('subcommand')
    port = kwargs.pop('port')

    getattr(Util(port), subcommand)(**kwargs)
