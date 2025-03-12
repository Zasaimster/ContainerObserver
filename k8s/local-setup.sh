#!/bin/bash

echo "Starting Minikube..."
minikube start --memory=4096 --cpus=4

echo "Enabling metrics server..."
minikube addons enable metrics-server

echo "Building Docker images..."
eval $(minikube -p minikube docker-env)

# Build all services
services=("user" "product" "payment" "order")
for service in "${services[@]}"; do
    echo "Building $service service..."
    docker build -t ${service}-service:latest ./microservice/${service}_service
done

# kubectl create configmap grafana-dashboards --from-file=metric_observer/grafana/dashboards/docker_monitoring.json
kubectl create configmap grafana-dashboards --from-file=metric_observer/grafana/dashboards/docker_monitoring_k8s.json

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/manifests/

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/user-service
kubectl wait --for=condition=available --timeout=300s deployment/product-service
kubectl wait --for=condition=available --timeout=300s deployment/payment-service
kubectl wait --for=condition=available --timeout=300s deployment/order-service

echo "To monitor HPA scaling:"
echo "kubectl get hpa -w"

# echo "Setting up port forwarding..."
# sudo ./k8s/portforward.sh
echo "Use the following command to setup local access:"
echo "sudo ./k8s/portforward.sh"


echo "To access grafana, use user:pass admin:admin"
echo "Setup complete! You can now run your load tests with Locust"

# helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
# helm repo update
# helm install kube-state-metrics prometheus-community/kube-state-metrics -n kube-system
