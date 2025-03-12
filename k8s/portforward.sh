#!/bin/bash
# Port-forward the nginx ingress controller (ensure this service name and namespace are correct)
kubectl port-forward -n ingress-nginx service/ingress-nginx-controller 80:80 &

# Port-forward individual services
kubectl port-forward service/order-service 8004:8004 &
kubectl port-forward service/payment-service 8003:8003 &
kubectl port-forward service/product-service 8002:8002 &
kubectl port-forward service/user-service 8001:8001 &
# Port-forward Prometheus service: accessible at http://localhost:9090
kubectl port-forward service/prometheus 9090:9090 &
# Port-forward Grafana service: accessible at http://localhost:3000
kubectl port-forward service/grafana 3000:3000 &
# Port-forward cAdvisor service: accessible at http://localhost:8080
kubectl port-forward service/cadvisor 8080:8080 &
# kubectl port-forward service/kube-state-metrics 8081:8081 & 

# Wait for all background jobs to finish
wait