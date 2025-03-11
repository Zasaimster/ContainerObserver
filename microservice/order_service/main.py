import requests
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Order(BaseModel):
    product_id: int
    quantity: int


orders_db = []


@app.post("/order")
def create_order(order: Order):
    print("getting product-service")
    product = requests.get(f"http://product-service:8002/product/{order.product_id}")
    if product.return_code == 404:
        raise HTTPException(status_code=404, detail="Product not found")

    product = product.json()
    print("PRODUCT", product)

    if product["stock"] < order.quantity:
        raise HTTPException(status_code=400, detail="Not enough stock available")

    orders_db.append(order)
    return {"message": "Order created successfully"}
