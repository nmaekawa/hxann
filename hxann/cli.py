# -*- coding: utf-8 -*-

"""Console script for hxann."""
import contextlib
import sys
import click

from .hxann import convert

@click.command()
@click.option('--csv',
              default='-',
              help='csv file to be converted, default is stdin',
             )
@click.option( '--fmt',
              type=click.Choice(['annjs', 'webann'], case_sensitive=False),
              default='annjs',
              help='format to convert to, default is annjs',
             )
def cli(csv, fmt):

    with _smart_open(csv) as handle:
        #content = handle.read()
        result = convert(handle)

    #result = convert(content)
    print(result)



# from http://stackoverflow.com/a/29824059
@contextlib.contextmanager
def _smart_open(filename, mode='Ur'):
    if filename == '-':
        if mode is None or mode == '' or 'r' in mode:
            fh = sys.stdin
        else:
            fh = sys.stdout
    else:
        fh = open(filename, mode)

    try:
        yield fh
    finally:
        if filename is not '-':
            fh.close()


if __name__ == "__main__":
    sys.exit(cli())  # pragma: no cover
