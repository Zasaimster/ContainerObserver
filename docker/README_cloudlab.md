# Setting Up and Running Server-Client Communication on CloudLab

This document outlines the steps to set up and run server(node0)-client(node1-4) communication on a distributed microservices architecture deployed on CloudLab.

## 1. Initial Node Setup

### 1.1 Accessing Nodes

1.  **CloudLab GUI:** Use the CloudLab GUI to access the shell or SSH into each allocated node.

### 1.2 Repository Cloning and Root Access

1.  **Become Root:** On each node, execute `sudo su` to gain root privileges.
2.  **Clone Repository:** Clone the repository containing the microservices and Locust test scripts:

    ```bash
    git clone https://github.com/Zasaimster/ContainerObserver.git
    ```

## 2. Deploying Microservices

### 2.1 Identifying Node IP Addresses

1.  **Find Host IP:** On each node *except node-0*, determine the node's IP address using:

    ```bash
    hostname -I | awk '{print $1}'
    ```

    This IP address will be referred to as `HOSTIP`.
    In this setup, the node IP addresses are consistently:

    * node-0: `128.110.219.101`
    * node-1: `128.110.219.96`
    * node-2: `128.110.219.115`
    * node-3: `128.110.216.231`
    * node-4: `128.110.216.235`
    

### 2.2 Allowing Network Traffic

1.  **Open Firewall Ports:** Allow incoming TCP traffic on ports 8001 to 8004 using `ufw`:

    ```bash
    ufw allow 8001:8004/tcp
    ufw reload
    ```

### 2.3 Running Microservices with Docker Compose

1.  **Navigate to Microservices Directory:** On each node *except node-0*, navigate to the `microservice` directory within the cloned repository.

2.  **Start Services:** Start the microservices using Docker Compose:

    ```bash
    docker-compose up -d
    ```

    This will deploy the FastAPI microservices.

### 2.4 Microservice Endpoints

The microservices will be accessible at the following endpoints, where `HOSTIP` is the IP address of each node:

* `http://HOSTIP:8001/`
* `http://HOSTIP:8002/`
* `http://HOSTIP:8003/`
* `http://HOSTIP:8004/`


## 3. Running Load Tests from node-0

### 3.1 Navigating to Test Directory

1.  **Access Test Directory:** On node-0, navigate to the `test` directory within the cloned repository:

    ```bash
    cd test
    ```

### 3.2 Executing Locust Tests

1. **TMUX** Open several tmux sessions, 1 per client node.

2.  **Environment Variable Setup:** For each client node and corresponding TMUX session, set the `BASE_URL` environment variable to the node's corresponding `HOSTIP`:

    ```bash
    export BASE_URL=http://<CLIENT_NODE_HOSTIP>
    ```

    Replace `<CLIENT_NODE_HOSTIP>` with the correct IP address for each node (e.g. `128.110.219.96`).

3.  **Run Locust:** Execute the Locust load test using the following command:

    ```bash
    locust -H $BASE_URL --users 1000 --spawn-rate 1 --run-time 15m --headless
    ```

    This command performs a headless load test targeting the specified `BASE_URL`, simulating 1000 users with a spawn rate of 1 user per second, and running for 15 minutes.
