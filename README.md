# Prometheus Opendistro Exporter

Leverage Opendistro for Elasticsearch APIs to fetch some important data & expose them in Prometheus format.

## Usage

You should use Docker to run this script for convenience:

```bash

# Build the Docker container first
make build

# Check the script arguments
make run-local extra_args='-h'

# This will proceed to delete snapshot if any match is found
make run-local
```
