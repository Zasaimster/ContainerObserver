import argparse
import logging
import os
import sys
import time

import pandas as pd
from prometheus_api_client import PrometheusConnect
from prometheus_api_client.exceptions import PrometheusApiClientException

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


class MetricCollector:
    def __init__(
        self,
        prometheus_url: str = "http://localhost:9090",
        poll_interval: int = 60,
        data_dir: str = "./data",
        debug: bool = False,
    ):
        """Initialize the collector with Prometheus connection"""
        if debug:
            logging.getLogger().setLevel(logging.DEBUG)

        logger.info(f"Initializing collector with Prometheus URL: {prometheus_url}")
        try:
            self.prom = PrometheusConnect(url=prometheus_url, disable_ssl=True)
            # Test connection
            self.prom.check_prometheus_connection()
            logger.info("Successfully connected to Prometheus")
        except Exception as e:
            logger.error(f"Failed to connect to Prometheus: {e}")
            logger.error("Make sure Prometheus is running and accessible")
            logger.error(
                "You may need to run: kubectl port-forward svc/prometheus-k8s 9090:9090 -n monitoring"
            )
            sys.exit(1)

        self.poll_interval = poll_interval
        self.output_dir = data_dir
        self.ensure_directories()

    def ensure_directories(self):
        """Create necessary directories for data storage"""
        subdirs = ["NodeMetrics", "MSMetrics"]
        for dir in subdirs:
            os.makedirs(os.path.join(self.output_dir, dir), exist_ok=True)

    def get_node_metrics(self) -> pd.DataFrame:
        """Collect node-level metrics using kube-prometheus queries"""
        timestamp = int(time.time() * 1000)  # milliseconds timestamp

        try:
            # Query CPU utilization by node (1 minus idle time)
            cpu_query = """
            1 - (
                sum by (instance) (rate(node_cpu_seconds_total{mode=~"idle|iowait|steal",job="node-exporter"}[5m]))
                /
                sum by (instance) (rate(node_cpu_seconds_total{job="node-exporter"}[5m]))
            )
            """
            cpu_result = self.prom.custom_query(cpu_query)
            logger.debug(f"CPU query result: {cpu_result}")

            # Query memory utilization by node
            mem_query = """
            1 - node_memory_MemAvailable_bytes{job="node-exporter"} 
            / node_memory_MemTotal_bytes{job="node-exporter"}
            """
            mem_result = self.prom.custom_query(mem_query)
            logger.debug(f"Memory query result: {mem_result}")

            # Process results
            metrics = []
            seen_nodes = set()

            # First collect CPU metrics
            for cpu in cpu_result:
                instance = cpu["metric"].get("instance", "unknown").split(":")[0]
                node_name = f"NODE_{instance.replace('-', '_').replace('.', '_')}"
                seen_nodes.add(node_name)

                metrics.append(
                    {
                        "timestamp": timestamp,
                        "nodeid": node_name,
                        "cpu_utilization": float(cpu["value"][1]),
                        "memory_utilization": 0.0,  # Will be updated with memory data
                    }
                )

            # Update memory metrics for each node
            for mem in mem_result:
                instance = mem["metric"].get("instance", "unknown").split(":")[0]
                node_name = f"NODE_{instance.replace('-', '_').replace('.', '_')}"

                # Find matching node in metrics
                for metric in metrics:
                    if metric["nodeid"] == node_name:
                        metric["memory_utilization"] = float(mem["value"][1])
                        break

                # If node wasn't seen in CPU metrics, add it
                if node_name not in seen_nodes:
                    metrics.append(
                        {
                            "timestamp": timestamp,
                            "nodeid": node_name,
                            "cpu_utilization": 0.0,
                            "memory_utilization": float(mem["value"][1]),
                        }
                    )
                    seen_nodes.add(node_name)

            if not metrics:
                logger.warning("No node metrics found")
                return pd.DataFrame()

            logger.debug(f"Collected metrics for {len(metrics)} nodes")
            return pd.DataFrame(metrics)

        except Exception as e:
            logger.error(f"Error collecting node metrics: {e}")
            if self.debug:
                logger.exception("Detailed error:")
            return pd.DataFrame()

        return pd.DataFrame(metrics)

    def get_service_metrics(self) -> pd.DataFrame:
        """Collect microservice-level metrics using kube-prometheus queries"""
        timestamp = int(time.time() * 1000)

        try:
            # Query container CPU usage (cores)
            cpu_query = """
            sum(
              rate(container_cpu_usage_seconds_total{container!="",pod!=""}[5m])
            ) by (pod,namespace,node)
            """
            cpu_result = self.prom.custom_query(cpu_query)
            logger.debug(f"Container CPU query result: {cpu_result}")

            # Query container memory usage (bytes)
            mem_query = """
            sum(
              container_memory_working_set_bytes{container!="",pod!=""}
            ) by (pod,namespace,node) 
            /
            sum(
              kube_pod_container_resource_limits{resource="memory"}
            ) by (pod,namespace,node)
            """
            mem_result = self.prom.custom_query(mem_query)
            logger.debug(f"Container Memory query result: {mem_result}")

            # Process results
            metrics = []
            seen_pods = set()

            # First collect CPU metrics
            for cpu in cpu_result:
                pod = cpu["metric"].get("pod", "unknown")
                namespace = cpu["metric"].get("namespace", "unknown")
                node = cpu["metric"].get("node", "unknown").split(":")[0]
                pod_key = f"{namespace}/{pod}"
                seen_pods.add(pod_key)

                metrics.append(
                    {
                        "timestamp": timestamp,
                        "msname": f"MS_{namespace}",
                        "msinstanceid": f"MS_{namespace}_POD_{pod}",
                        "nodeid": f"NODE_{node.replace('-', '_').replace('.', '_')}",
                        "cpu_utilization": float(cpu["value"][1]),
                        "memory_utilization": 0.0,  # Will be updated with memory data
                    }
                )

            # Update memory metrics for each pod
            for mem in mem_result:
                pod = mem["metric"].get("pod", "unknown")
                namespace = mem["metric"].get("namespace", "unknown")
                node = mem["metric"].get("node", "unknown").split(":")[0]
                pod_key = f"{namespace}/{pod}"

                # Find matching pod in metrics
                found = False
                for metric in metrics:
                    if (
                        metric["msname"] == f"MS_{namespace}"
                        and metric["msinstanceid"] == f"MS_{namespace}_POD_{pod}"
                    ):
                        metric["memory_utilization"] = float(mem["value"][1])
                        found = True
                        break

                # If pod wasn't seen in CPU metrics, add it
                if not found and pod_key not in seen_pods:
                    metrics.append(
                        {
                            "timestamp": timestamp,
                            "msname": f"MS_{namespace}",
                            "msinstanceid": f"MS_{namespace}_POD_{pod}",
                            "nodeid": f"NODE_{node.replace('-', '_').replace('.', '_')}",
                            "cpu_utilization": 0.0,
                            "memory_utilization": float(mem["value"][1]),
                        }
                    )
                    seen_pods.add(pod_key)

            if not metrics:
                logger.warning("No service metrics found")
                return pd.DataFrame()

            logger.debug(f"Collected metrics for {len(metrics)} pods")
            return pd.DataFrame(metrics)

        except Exception as e:
            logger.error(f"Error collecting service metrics: {e}")
            if self.debug:
                logger.exception("Detailed error:")
            return pd.DataFrame()

        return pd.DataFrame(metrics)

    def write_metrics(self):
        """Write metrics to CSV files"""
        try:
            # Collect and write node metrics
            node_df = self.get_node_metrics()
            if not node_df.empty:
                node_file = os.path.join(
                    self.output_dir, "NodeMetrics", "NodeMetricsUpdate_0.csv"
                )
                # Append to existing file, write header only if file doesn't exist
                node_df.to_csv(
                    node_file,
                    mode="a",
                    index=False,
                    header=not os.path.exists(node_file),
                )
                logger.debug(f"Wrote {len(node_df)} node metrics to {node_file}")

            # Collect and write service metrics
            service_df = self.get_service_metrics()
            if not service_df.empty:
                service_file = os.path.join(
                    self.output_dir, "MSMetrics", "MSMetricsUpdate_0.csv"
                )
                # Append to existing file, write header only if file doesn't exist
                service_df.to_csv(
                    service_file,
                    mode="a",
                    index=False,
                    header=not os.path.exists(service_file),
                )
                logger.debug(
                    f"Wrote {len(service_df)} service metrics to {service_file}"
                )

        except Exception as e:
            logger.error(f"Error writing metrics: {e}")
            if self.debug:
                logger.exception("Detailed error:")


def parse_args():
    parser = argparse.ArgumentParser(
        description="Container Observer - Metrics collector for Kubernetes"
    )
    parser.add_argument(
        "--prometheus-url",
        default="http://localhost:9090",
        help="Prometheus server URL (default: http://localhost:9090)",
    )
    parser.add_argument(
        "--interval",
        type=int,
        default=60,
        help="Polling interval in seconds (default: 60)",
    )
    parser.add_argument(
        "--data-dir",
        default="./data",
        help="Directory to store CSV files (default: ./data)",
    )
    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug logging",
    )
    parser.add_argument(
        "--single-run",
        action="store_true",
        help="Run once and exit (useful for testing)",
    )
    return parser.parse_args()


def main():
    args = parse_args()

    collector = MetricCollector(
        prometheus_url=args.prometheus_url,
        poll_interval=args.interval,
        data_dir=args.data_dir,
        debug=args.debug,
    )

    logger.info("Starting Container Observer...")
    logger.info("Monitoring following metrics:")
    logger.info("- Node CPU/Memory Usage")
    logger.info("- Service CPU/Memory Usage")
    logger.info(f"Writing data to: {args.data_dir}")

    if args.single_run:
        logger.info("Running in single-run mode")
        try:
            collector.write_metrics()
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            if args.debug:
                logger.exception("Detailed error:")
            sys.exit(1)
        logger.info("Single run completed successfully")
        return

    while True:
        try:
            collector.write_metrics()
            logger.debug(f"Sleeping for {args.interval} seconds")
            time.sleep(args.interval)
        except KeyboardInterrupt:
            logger.info("Received interrupt signal, shutting down...")
            break
        except Exception as e:
            logger.error(f"Error collecting metrics: {e}")
            if args.debug:
                logger.exception("Detailed error:")
            logger.info("Waiting 10 seconds before retry...")
            time.sleep(10)


if __name__ == "__main__":
    main()
