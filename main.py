#!/usr/bin/env python
"""
  " Main entry point.
  """

import argparse
from src import logger


def main():
    log = logger.setup_logger()
    log.debug('MLP Wiki Scraper! /)')


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('-v', '--verbose', action="store_true",
                        help='increase output verbosity')
    args = parser.parse_args()

    if args.verbose:
        main()
