# Container Observer

A metrics collector that exports Kubernetes monitoring data in a format compatible with the Alibaba 2022 microservices trace dataset structure.

## Overview

Container Observer connects to kube-prometheus and exports resource utilization metrics as CSV files:

1. **Node Metrics** (`NodeMetricsUpdate_0.csv`): Node-level resource utilization
   ```
   timestamp,nodeid,cpu_utilization,memory_utilization
   ```

2. **Microservice Metrics** (`MSMetricsUpdate_0.csv`): Container-level resource utilization
   ```
   timestamp,msname,msinstanceid,nodeid,cpu_utilization,memory_utilization
   ```

## Prerequisites

- Python 3.8 or higher
- Kubernetes cluster with kube-prometheus stack installed
- kubectl configured with cluster access

## Quick Start

1. Install dependencies:
   ```bash
   pip install -e .
   ```

2. Port-forward Prometheus:
   ```bash
   kubectl port-forward svc/prometheus-k8s 9090:9090 -n monitoring
   ```

3. Run the observer:
   ```bash
   python main.py
   ```

## Usage

```bash
python main.py [options]

options:
  -h, --help            Show this help message and exit
  --prometheus-url URL  Prometheus server URL (default: http://localhost:9090)
  --interval SECONDS    Polling interval in seconds (default: 60)
  --data-dir PATH      Directory to store CSV files (default: ./data)
  --debug              Enable debug logging
  --single-run         Run once and exit (useful for testing)
```

## Development

### Running in Debug Mode

```bash
python main.py --debug --single-run
```

This will:
- Enable detailed debug logging
- Run one collection cycle and exit
- Show full error traces if anything fails

### Data Collection

The observer continuously collects metrics and appends them to CSV files:

1. Data files grow over time as new metrics are collected
2. Headers are written only once when files are created
3. Timestamps allow tracking metrics over time
