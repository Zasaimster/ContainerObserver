Starting communication between server and client nodes:

Setting up each node
SSH or open Shell for all nodes from Cloudlab GUI
clone this repo on each Node and become root
sudo su
git clone ...

Run microservice applications
For each node except node-0
run hostname -I | awk '{print $1}', this will be HOSTIP
run ufw allow 8001:8004/tcp and ufw reload to allow incoming communication
In ./microservice, run docker-compose up
The microservices are FastAPIs running at:
http://HOSTIP:8001/
http://HOSTIP:8002/
http://HOSTIP:8003/
http://HOSTIP:8004/
(each node will have its own HOSTIP)
What it seems to be always:
node-0 = 128.110.219.101
node-1 = 128.110.219.96
node-2 = 128.110.219.115
node-3 = 128.110.216.231
node-4 = 128.110.216.235

Send communication from node-0
On node-0 cd into ./test
For each client node run the following:
export BASE_URL=$HOSTIP where $HOSTIP is the client node's ip
run locust --users 1000 --spawn-rate 1 --run-time 15m --headless &


