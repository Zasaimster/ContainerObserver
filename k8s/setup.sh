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

echo "Applying Kubernetes manifests..."
kubectl apply -f k8s/manifests/

echo "Waiting for deployments to be ready..."
kubectl wait --for=condition=available --timeout=300s deployment/user-service
kubectl wait --for=condition=available --timeout=300s deployment/product-service
kubectl wait --for=condition=available --timeout=300s deployment/payment-service
kubectl wait --for=condition=available --timeout=300s deployment/order-service

echo "Setting up port forwarding..."
echo "Use these commands in separate terminals to enable local access:"
echo "kubectl port-forward svc/user-service 8001:8001"
echo "kubectl port-forward svc/product-service 8002:8002"
echo "kubectl port-forward svc/payment-service 8003:8003"
echo "kubectl port-forward svc/order-service 8004:8004"

echo "To monitor HPA scaling:"
echo "kubectl get hpa -w"

echo "Setup complete! You can now run your load tests with Locust"
