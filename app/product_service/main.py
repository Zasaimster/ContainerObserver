from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import random

app = FastAPI()

NUM_PRODUCTS = 1000


class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int


products_db = {}
memory_consumer = []


@app.on_event("startup")
async def startup_event():
    """
    Populates the products_db with initial data when the application starts.
    About 500MB worth of data
    """
    for i in range(NUM_PRODUCTS):
        product = Product(
            id=i,
            name=f"product_{i}",
            price=round(random.uniform(0.5, 250), 2),
            stock=250,
        )

        products_db[product.id] = product
        large_data = {"data": "A" * 1024 * 512}
        memory_consumer.append(large_data)

    print(products_db)
    print(len(products_db))


@app.post("/product")
def create_product(product: Product):
    if product.id in products_db:
        raise HTTPException(status_code=400, detail="Product already exists")

    # consume 0.5MB memory for each created product
    large_data = {"data": "A" * 1024 * 512}
    memory_consumer.append(large_data)

    products_db[product.id] = product
    return {"message": "Product created successfully"}


@app.get("/product/{product_id}")
def get_product(product_id: int):
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]
