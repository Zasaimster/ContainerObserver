## Installation
- Install Docker

## Running Microservices
- In `./microservice`, run `docker compose up`
- The microservices are FastAPIs running at:
  - `http://0.0.0.0:8001/`
  - `http://0.0.0.0:8002/`
  - `http://0.0.0.0:8003/`
  - `http://0.0.0.0:8004/`
- You can view the endpoint documentation at `http://0.0.0.0:800X/docs`,

## Running Metric Observer
- In `./metric_observer`, run `docker compose up`
- This starts cAdvisor, Prometheus, and Grafana
- Local endpoints:
  - cAdvisor: `http://0.0.0.0:8080/`
    - Make sure you can access `http://0.0.0.0:8080/docker` and see the names of your microservice containers under the "Subcontainer" heading
  - Prometheus: `http://0.0.0.0:8080/`
  - Grafana: `http://0.0.0.0:9100/`
    - View the dashboard at: `http://0.0.0.0:9100/d/aeeepbndvsow0e/docker-monitoring`

## Running Load Tests (WIP)
- In `./test` run:
  - `pip install locust`
  - `locust -H localhost --users 100 --spawn-rate 1 --run-time 15m --headless `
    - This will simulate 100 users (generating a new one every second).
    - View API stats on the CLI and container metrics on Grafana

## Kubernetes Deployment Instructions

### Prerequisites
- Minikube installed (`brew install minikube` on macOS)
- kubectl configured
- Docker installed

### Setting up the Kubernetes Environment

1. Run the setup script:
```bash
./k8s/setup.sh
```

2. Open separate terminal windows and run the following commands for port forwarding:
```bash
kubectl port-forward svc/user-service 8001:8001
kubectl port-forward svc/product-service 8002:8002
kubectl port-forward svc/payment-service 8003:8003
kubectl port-forward svc/order-service 8004:8004
```

3. Monitor auto-scaling:
```bash
kubectl get hpa -w
```

### Running Load Tests with Kubernetes
The project includes a Locust load test file that will create test products and simulate user behavior.

1. Install Locust (if not already installed):
```bash
pip install locust
```

2. Run the load test:
```bash
cd test && locust
```

3. Open Locust web interface:
- Visit http://localhost:8089
- Start a new test with desired number of users

### Observing Auto-scaling
- The services are configured to auto-scale based on CPU utilization
- Initial setup: 2 replicas per service
- Will scale up to 10 replicas when CPU utilization exceeds 50%
- Monitor scaling in real-time: `kubectl get hpa -w`

### Viewing Service Logs
To view logs from a service:

```bash
# View logs from all pods of a service
kubectl logs -l app=order-service

# View logs from a specific pod
kubectl get pods  # List all pods
kubectl logs <pod-name>  # e.g., kubectl logs order-service-7d8f9b7b5-2x2jz

# Follow logs in real-time
kubectl logs -f -l app=order-service
```

### Restarting Services

#### Docker Compose
To restart services after code changes:
```bash
# Rebuild and restart all services
docker compose down
docker compose up --build

# Rebuild and restart a specific service
docker compose up -d --build <service-name>  # e.g., docker compose up -d --build order-service
```

#### Kubernetes
To restart services after code changes:
```bash
# Rebuild and redeploy all services
kubectl delete -f k8s/manifests/
./k8s/setup.sh

# Point to Minikube's Docker daemon first
eval $(minikube -p minikube docker-env)

# Rebuild and redeploy a specific service
docker build -t <service-name>:latest ./microservice/<service>_service  # e.g., docker build -t order-service:latest ./microservice/order_service
kubectl rollout restart deployment/<service-name>  # e.g., kubectl rollout restart deployment/order-service

# Watch the rollout status
kubectl rollout status deployment/<service-name>
```

### Cleanup
To stop the Kubernetes cluster:
```bash
minikube stop
```

To delete the cluster:
```bash
minikube delete
