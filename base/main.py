#!/usr/bin/env python3

"""Prometheus Opendistro exporter

Usage:
  prometheus-opendistro-exporter [-v | --verbose] [--port=<port>] --interval=<seconds> --endpoint=<opendistro> 
  prometheus-opendistro-exporter (-h | --help)

Options:
  --endpoint=<opendistro>       HTTP endpoint of the Opendistro Elasticsearch cluster to monitor.
  --interval=<seconds>          Time interval in seconds between Opendistro checks [default: 60]
  --port=<port>                 Listening port of the exporter. [default: 9210]
  -v, --verbose                 Set log level to DEBUG (much more logs).
  -h, --help                    Show this screen.
"""

import json
import logging
import requests
import time
from prometheus_client import start_http_server, Gauge
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
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
Requests HTTP helpers
"""
ADAPTER = HTTPAdapter(
    max_retries=Retry(
        total=3,
        status_forcelist=[429, 500, 502, 503, 504],
        method_whitelist=["HEAD", "GET", "OPTIONS"],
    )
)
HTTP = requests.Session()
HTTP.mount("https://", ADAPTER)
HTTP.mount("http://", ADAPTER)

"""
Classes
"""


class IndexStateManagement:
    """Handle metrics related to opendistro Index State Management"""

    def __init__(self, endpoint: str):
        """__init__

        Args:
            endpoint (str): Opendistro Elasticsearch endpoint
        """
        self.endpoint = endpoint
        self.explain_gauge = Gauge(
            name="opendistro_ism_explain",
            documentation="Details got from Opendistro ISM explain API",
            labelnames=["index", "state"],
        )

    def fetch_metrics(self):
        """fetch_metrics Fetch all metrics related to index State Management."""

        self.explain_all_indices()

    def explain_all_indices(self):

        explain_request = HTTP.get(f"{self.endpoint}/_opendistro/_ism/explain/*")

        excluded = (".opendistro", ".kibana", ".apm")

        for name, details in explain_request.json().items():
            if not name.startswith(excluded):
                self.explain_gauge.labels(name, details["state"]["name"]).set(1.0)


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

    # Fetch CLI arguments
    interval = int(arguments["--interval"])
    endpoint = arguments["--endpoint"]
    listening_port = int(arguments["--port"])

    ism = IndexStateManagement(endpoint)

    start_http_server(listening_port)

    while True:

        ism.fetch_metrics()

        LOG.debug("See you in %s seconds", interval)
        time.sleep(interval)


if __name__ == "__main__":
    main()
