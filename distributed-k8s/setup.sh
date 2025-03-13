#!/bin/bash

echo "Cleaning up workspace"
kubectl delete -f app-manifests/
kubectl delete -f infra-manifests/

echo "Building Docker images..."
services=("user" "product" "payment" "order")
for service in "${services[@]}"; do
    echo "Building $service service..."
    docker build -t ${service}-service:latest ../app/${service}_service
done

kubectl create configmap grafana-dashboards --from-file=k8s_dashboard.json

echo "Applying Kubernetes manifests..."
kubectl apply -f app-manifests/
kubectl apply -f infra-manifests/

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/user-service
kubectl wait --for=condition=available --timeout=300s deployment/product-service
kubectl wait --for=condition=available --timeout=300s deployment/payment-service
kubectl wait --for=condition=available --timeout=300s deployment/order-service



echo "To access grafana, use credentials user:pass admin:admin"
echo "To setup kube-state-metrics, run the following commands"
echo "$ helm repo add prometheus-community https://prometheus-community.github.io/helm-charts"
echo "$ helm repo update"
echo "$ helm install kube-state-metrics prometheus-community/kube-state-metrics -n kube-system"
echo "Setup complete! You can now run your load tests with Locust"
