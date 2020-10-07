#!/usr/bin/env python3

"""Prometheus Opendistro exporter

Usage:
  prometheus-opendistro-exporter [-v | --verbose] [--port=<port>] [--interval=<seconds>] --endpoint=<opendistro> 
  prometheus-opendistro-exporter (-h | --help)

Options:
  --endpoint=<opendistro>       HTTP endpoint of the Opendistro Elasticsearch cluster to monitor.
  --interval=<seconds>          Time interval in seconds between Opendistro checks [default: 60]
  --port=<port>                 Listening port of the exporter. [default: 9210]
  -v, --verbose                 Set log level to DEBUG (much more logs).
  -h, --help                    Show this screen.
"""

import json
from pythonjsonlogger import jsonlogger
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

logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter("%(message)%(levelname)%(name)%(asctime)")
logHandler.setFormatter(formatter)
logging.root.addHandler(logHandler)

LOG = logging.getLogger(__name__)
LOG.setLevel(logging.INFO)


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

EXCLUDED = (".opendistro", ".kibana", ".apm")

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
            labelnames=[
                "index",
                "policy_id",
                "state",
                "rolled_over",
                "action_name",
                "action_failed",
                "retry_failed",
                "retry_consumed",
            ],
        )

    def fetch_metrics(self):
        """fetch_metrics Fetch all metrics related to index State Management."""

        self.explain_all_indices()

    def explain_all_indices(self):

        explain_request = HTTP.get(f"{self.endpoint}/_opendistro/_ism/explain/*")

        for name, details in explain_request.json().items():
            if name.startswith(EXCLUDED):
                LOG.debug(
                    "Rejected index '%s' (reason: name part of the exclusion list)",
                    name,
                )
            else:
                try:
                    self.explain_gauge.labels(
                        index=name,
                        policy_id=details["policy_id"],
                        state=details["state"]["name"],
                        rolled_over=details["rolled_over"],
                        action_name=details["action"]["name"],
                        action_failed=details["action"]["failed"],
                        retry_failed=details["retry_info"]["failed"],
                        retry_consumed=details["retry_info"]["consumed_retries"],
                    ).set(1.0)
                except KeyError as e:
                    LOG.info(
                        "Rejected index '%s' (Reason: missing %s from ISM explain call)",
                        name,
                        e,
                    )


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

    LOG.info("Prometheus Opendistro Exporter")
    LOG.info("Index exclusion list: %s", EXCLUDED)
    LOG.info("Opendistro endpoint: %s", endpoint)
    LOG.info("Interval between Opendistro calls: %s", interval)
    LOG.info("Initialization done")

    ism = IndexStateManagement(endpoint)

    start_http_server(listening_port)
    LOG.info("Listening for Prometheus requests on port %i", listening_port)

    while True:

        ism.fetch_metrics()

        time.sleep(interval)


if __name__ == "__main__":
    main()
