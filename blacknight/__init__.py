__author__ = 'dkudrow'


from client import Client
from util import ZKUtil
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('-p', default='2181')
    args = parser.parse_args()
    Client(args.p).run()


def util():
    parser = ArgumentParser()
    parser.add_argument('-p', default='2181')
    parser.add_argument('-f', default='')
    parser.add_argument('-s', default='')
    parser.add_argument('-i', default='')
    parser.add_argument('-h', default='')
    parser.add_argument('-a', default='')
    parser.add_argument('-v', default='')
    parser.add_argument('cmd', default='')
    subparsers = parser.add_subparsers()

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

    args = parser.parse_args()

    print args
