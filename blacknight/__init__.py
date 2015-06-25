__author__ = 'dkudrow'


from client import Client
from argparse import ArgumentParser


def main():
    parser = ArgumentParser()
    parser.add_argument('-p', default='2181')
    args = parser.parse_args()
    print 'Starting client on port {}'.format(args.p)
    Client(args.p).run()
