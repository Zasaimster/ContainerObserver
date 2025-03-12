from locust import HttpUser, task, between, events
from uuid import uuid1
import random
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost")
USER_URL = f"{BASE_URL}:8001"
PRODUCT_URL = f"{BASE_URL}:8002"
PAYMENT_URL = f"{BASE_URL}:8003"
ORDER_URL = f"{BASE_URL}:8004"

NUM_PRODUCTS = 1000  # NOTE: if you update this value, make sure to change the value in microservice/product_service/main.py as well


# # Startup: make products, few thousand total
# @events.test_start.add_listener
# def on_test_start(environment, **kwargs):
#     print(environment.host)
#     for i in range(NUM_PRODUCTS):
#         product = {
#             "id": i,
#             "name": f"product_{i}",
#             "price": round(random.uniform(0.5, 250), 2),
#             "stock": 250,
#         }
#         res = requests.post(f"{PRODUCT_URL}/product", json=product)

#         if res.status_code == 200:
#             print(f"Successfully created product {i}: {product['name']}")
#         else:
#             print(f"Failed to create product {i}. Status code: {res.status_code}")
#             print(f"Response: {res.text}")


# @events.init.add_listener
# def on_locust_init(environment, **kwargs):
#     if isinstance(environment.runner, MasterRunner):
#         print("I'm on master node")
#     else:
#         print("I'm on a worker or standalone node")


class ServiceUser(HttpUser):
    wait_time = between(0.2, 3)  # wait 0.2 - 3 seconds before requests

    @task
    def order_and_pay(self):
        product_id = random.randint(0, NUM_PRODUCTS - 1)
        order = {
            "product_id": product_id,
            # order too many items to trigger the 400 response code ~3% of the time
            "quantity": 251 if random.random() < 0.03 else random.randint(0, 250),
        }
        res = self.client.post(f"{ORDER_URL}/order", json=order)

        # Pay if successful
        if res.status_code == 200:
            res = self.client.post(f"{PAYMENT_URL}/pay/?amount=10.0")

    def on_start(self):
        uid = uuid1()

        self.client.post(
            f"{USER_URL}/signup",
            json={
                "username": f"{uid}_user",
                "email": f"{uid}_email",
                "password": f"{uid}_pass",
            },
        )

        self.client.post(
            f"{USER_URL}/login",
            json={
                "username": f"{uid}_user",
                "email": f"{uid}_email",
                "password": f"{uid}_pass",
            },
        )
