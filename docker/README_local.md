## Installation
- Install Docker

## Running Microservices
- In `../app`, run `docker compose up`
- The microservices are FastAPIs running at:
  - `http://0.0.0.0:8001/`
  - `http://0.0.0.0:8002/`
  - `http://0.0.0.0:8003/`
  - `http://0.0.0.0:8004/`
- You can view the endpoint documentation at `http://0.0.0.0:800X/docs`,
- cAdvisor does not rely on knowing the location of these APIs, and it is automatically setup to scrape all Docker containers. So, you can use any microservice setup you would like

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
- In `../test` run:
  - `pip install locust`
  - `locust -H localhost --users 100 --spawn-rate 1 --run-time 15m --headless `
    - This will simulate 100 users (generating a new one every second).
    - View API stats on the CLI and container metrics on Grafana