## Deployment Instructions

### Prerequisites
- kubectl configured
- Docker installed
- Build docker images on all nodes manually or have built images pushed to a registry

### Setting up the Kubernetes Environment

1. Run the setup script:
```bash
./k8s/setup.sh
```

2. Monitor auto-scaling:
```bash
kubectl get hpa -w
```

### Running Load Tests with Kubernetes
The project includes a Locust load test file that will create test products and simulate user behavior.

1. Install Locust locally (if not already installed):
```bash
pip install locust
```
Configure your locust file to use the IP addresses exposed by Kubernetes.
Run
```
kubectl get svc
```

If external IP addresses are not exposed:
```
kubectl get configmap/config -n metallb-system -o yaml > metallb-config.yaml
# update metallb-config.yaml with new IP addresses. Reference example-metallb-config.yaml
kubectl apply -f metallb-config.yaml

```

2. Run the load test:
```bash
cd test/distributed && locust
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


# Rebuild and redeploy a specific service
docker build -t <service-name>:latest ./microservice/<service>_service  # e.g., docker build -t order-service:latest ./microservice/order_service
kubectl rollout restart deployment/<service-name>  # e.g., kubectl rollout restart deployment/order-service

# Watch the rollout status
kubectl rollout status deployment/<service-name>
```
