"""
BlacKnight
"""

__author__ = 'dkudrow'


import logging
from argparse import ArgumentParser
from client import BlacKnightClient
from eucalyptus import Eucalyptus
from util import Util


def main():
    """
    Start the BlacKnight daemon.
    """
    logging.basicConfig()
    logging.getLogger('blacknight').setLevel(logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default='2181')
    args = parser.parse_args()
    BlacKnightClient(args.port).run()


def util():
    """
    Run the BlacKnight utility.
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

    subparsers.add_parser('dump')

    kwargs = vars(parser.parse_args())
    subcommand = kwargs.pop('subcommand')
    port = kwargs.pop('port')

    getattr(Util(port), subcommand)(**kwargs)


def euca():
    """
    Start the Eucalytpus adapter daemon.
    """
    logging.basicConfig()
    logging.getLogger('blacknight').setLevel(logging.DEBUG)
    parser = ArgumentParser()
    parser.add_argument('-p', '--port', default='2181')
    parser.add_argument('-f', '--eucarc', default='')
    parser.add_argument('-i', '--interval', default='')
    args = parser.parse_args()
    Eucalyptus(args.port, eucarc=args.eucarc, interval=args.interval).run()
