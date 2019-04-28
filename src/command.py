from os.path import expanduser

import click

from src.logclouseau import Logclouseau


@click.command()
@click.option('--config', default='~/.logclouseau/logclouseau.toml',
              help='Config file path (defaults to '
                   '~/.logclouseau/logclouseau.toml)'
              )
@click.option('--log', default='debug',
              help='Logging level (defaults to debug)')
def main(config, log):
    Logclouseau(expanduser(config), log).investigate()


if __name__ == '__main__':
    main()
