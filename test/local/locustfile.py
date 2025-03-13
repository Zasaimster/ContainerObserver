from locust import HttpUser, task, between
from uuid import uuid1
import random
import os

BASE_URL = os.getenv("BASE_URL", "http://localhost")
USER_URL = f"{BASE_URL}:8001"
PRODUCT_URL = f"{BASE_URL}:8002"
PAYMENT_URL = f"{BASE_URL}:8003"
ORDER_URL = f"{BASE_URL}:8004"

NUM_PRODUCTS = 1000  # NOTE: if you update this value, make sure to change the value in microservice/product_service/main.py as well


class ServiceUser(HttpUser):
    wait_time = between(0.2, 3)  # wait 0.2 - 3 seconds before requests

    @task
    def order_and_pay(self):
        product_id = random.randint(0, NUM_PRODUCTS - 1)
        order = {
            "product_id": product_id,
            # order too many items to trigger the 400 response code ~3% of the time
            # "quantity": 251 if random.random() < 0.03 else random.randint(0, 250),
            "quantity": random.randint(0, 250),
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
