#!/usr/bin/env python3

"""Prometheus Opendistro exporter

Usage:
  prometheus-opendistro-exporter [-v | --verbose]
  prometheus-opendistro-exporter (-h | --help)

Options:
  -v, --verbose             Set log level to DEBUG (much more logs)
  -h, --help                Show this screen.
"""

import kubernetes
import logging
from datetime import datetime
from docopt import docopt

"""
Setup logging & global variables
"""

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(name)s.%(funcName)s +%(lineno)s: %(levelname)-8s [%(process)d] %(message)s",
)

LOG = logging.getLogger(__name__)

"""
Functions
"""


def main():
    """
    CLI entry point
    """

    arguments = docopt(__doc__)

    if arguments["--verbose"]:
        LOG.setLevel(logging.DEBUG)

    LOG.critical("SORTIE !!")


if __name__ == "__main__":
    main()
