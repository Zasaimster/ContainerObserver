from fastapi import FastAPI, HTTPException
from pydantic import BaseModel

app = FastAPI()


class Product(BaseModel):
    id: int
    name: str
    price: float
    stock: int


products_db = {}
memory_consumer = []


@app.post("/product")
def create_product(product: Product):
    # consume 0.5MB memory for each created product
    large_data = {"data": "A" * 1024 * 1024}
    memory_consumer.append(large_data)

    if product.id in products_db:
        raise HTTPException(status_code=400, detail="Product already exists")
    products_db[product.id] = product
    return {"message": "Product created successfully"}


@app.get("/product/{product_id}")
def get_product(product_id: int):
    print(f"Products_db: {products_db}")
    if product_id not in products_db:
        raise HTTPException(status_code=404, detail="Product not found")
    return products_db[product_id]
