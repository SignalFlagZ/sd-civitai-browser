import argparse

def preload(parser: argparse.ArgumentParser):
    parser.add_argument("--civsfz-api-key", type=str,
                        help="API key of Civita", default=None)